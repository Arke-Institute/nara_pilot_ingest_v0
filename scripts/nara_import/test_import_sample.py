#!/usr/bin/env python3
"""
Test Import Script for WJC-NSCSW Collection

Downloads a small sample of records from NARA S3 and imports into Arke IPFS.
Tests the complete import pipeline with 3 records.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List

from lib import ArkeClient, NARAImporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_sample_metadata(output_file: str, num_records: int = 3) -> List[Dict]:
    """
    Download sample records from NARA S3.

    Args:
        output_file: Path to save sample metadata
        num_records: Number of records to download

    Returns:
        List of NARA record dictionaries
    """
    logger.info(f"Downloading {num_records} sample records from NARA S3...")

    # Download first JSONL file from S3
    cmd = [
        "aws", "s3", "cp",
        "s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/coll_WJC-NSCSW-10.jsonl",
        "-",
        "--no-sign-request"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Parse JSONL and take first N records
    records = []
    for i, line in enumerate(result.stdout.strip().split("\n")):
        if i >= num_records:
            break
        if line.strip():
            data = json.loads(line)
            records.append(data["record"])

    # Save to file
    with open(output_file, "w") as f:
        json.dump(records, f, indent=2)

    logger.info(f"Saved {len(records)} records to {output_file}")
    return records


def extract_hierarchy_info(record: Dict) -> Dict[str, Any]:
    """
    Extract collection and series info from record ancestors.

    Args:
        record: NARA record dictionary

    Returns:
        Dictionary with collection_info and series_info
    """
    ancestors = record.get("ancestors", [])

    collection_info = None
    series_info = None

    for ancestor in ancestors:
        if ancestor.get("levelOfDescription") == "collection":
            collection_info = {
                "naId": ancestor["naId"],
                "title": ancestor["title"],
                "collection_identifier": ancestor.get("collectionIdentifier"),
                "date_range": {
                    "start": ancestor.get("inclusiveStartDate", {}).get("logicalDate", ""),
                    "end": ancestor.get("inclusiveEndDate", {}).get("logicalDate", "")
                }
            }

        elif ancestor.get("levelOfDescription") == "series":
            series_info = {
                "naId": ancestor["naId"],
                "title": ancestor["title"],
                "creators": ancestor.get("creators", []),
                "date_range": {
                    "start": ancestor.get("inclusiveStartDate", {}).get("logicalDate", ""),
                    "end": ancestor.get("inclusiveEndDate", {}).get("logicalDate", "")
                }
            }

    return {
        "collection": collection_info,
        "series": series_info
    }


def import_record(importer: NARAImporter, record: Dict) -> str:
    """
    Import a single NARA record.

    Args:
        importer: NARAImporter instance
        record: NARA record dictionary

    Returns:
        FileUnit PI
    """
    # Extract hierarchy
    hierarchy = extract_hierarchy_info(record)

    if not hierarchy["collection"]:
        raise ValueError(f"Record {record.get('naId')} missing collection ancestor")

    if not hierarchy["series"]:
        raise ValueError(f"Record {record.get('naId')} missing series ancestor")

    # Import collection (if not already done)
    collection = hierarchy["collection"]
    importer.import_collection(
        collection_naid=collection["naId"],
        title=collection["title"],
        date_range=collection["date_range"],
        full_metadata=None  # Could include full collection metadata if available
    )

    # Import series
    series = hierarchy["series"]
    importer.import_series(
        series_naid=series["naId"],
        parent_naid=collection["naId"],
        title=series["title"],
        date_range=series["date_range"],
        creators=series["creators"]
    )

    # Extract FOIA tracking number
    foia_tracking = None
    for vcn in record.get("variantControlNumbers", []):
        if vcn.get("type") == "FOIA Tracking Number":
            foia_tracking = vcn.get("number")
            break

    # Import file unit with digital objects
    fileunit_pi = importer.import_fileunit(
        fileunit_naid=record["naId"],
        parent_series_naid=series["naId"],
        collection_naid=collection["naId"],
        title=record.get("title", "Untitled"),
        record_types=record.get("generalRecordsTypes", []),
        digital_objects=record.get("digitalObjects", []),
        access_restriction=record.get("accessRestriction"),
        foia_tracking=foia_tracking,
        physical_location=record.get("physicalOccurrences", [{}])[0] if record.get("physicalOccurrences") else None,
        other_titles=record.get("otherTitles"),
        full_metadata=record
    )

    return fileunit_pi


def main():
    """Main test import function"""
    # Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.arke.institute")
    COLLECTION_ID = "WJC-NSCSW"
    NUM_RECORDS = 3
    SAMPLE_FILE = "sample_records.json"
    DRY_RUN = False  # Set to True to test without creating entities

    logger.info("=== NARA Import Test ===")
    logger.info(f"API: {API_BASE_URL}")
    logger.info(f"Collection: {COLLECTION_ID}")
    logger.info(f"Records: {NUM_RECORDS}")
    logger.info(f"Dry run: {DRY_RUN}")
    logger.info("=" * 40)

    # Check API health
    logger.info("\n1. Checking API health...")
    try:
        client = ArkeClient(API_BASE_URL)
        health = client.health_check()
        logger.info(f"API Status: {health}")
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        logger.error("Make sure the Arke API is running at http://localhost:8787")
        sys.exit(1)

    # Download sample records
    logger.info(f"\n2. Downloading {NUM_RECORDS} sample records...")
    try:
        if Path(SAMPLE_FILE).exists():
            logger.info(f"Loading existing sample from {SAMPLE_FILE}")
            with open(SAMPLE_FILE) as f:
                records = json.load(f)
        else:
            records = download_sample_metadata(SAMPLE_FILE, NUM_RECORDS)
    except Exception as e:
        logger.error(f"Failed to download sample: {e}")
        sys.exit(1)

    # Print sample info
    logger.info(f"\nSample records:")
    for i, record in enumerate(records, 1):
        digital_obj_count = len(record.get("digitalObjects", []))
        logger.info(f"  {i}. {record.get('title')} (naId: {record.get('naId')}, {digital_obj_count} objects)")

    # Initialize importer
    logger.info(f"\n3. Initializing importer...")
    importer = NARAImporter(
        api_client=client,
        collection_id=COLLECTION_ID,
        dry_run=DRY_RUN
    )

    # Import institution
    logger.info(f"\n4. Creating/retrieving institution...")
    importer.import_institution(
        name="National Archives",
        description="National Archives and Records Administration",
        url="https://www.archives.gov/"
    )

    # Import records
    logger.info(f"\n5. Importing {len(records)} records...")
    imported_pis = []

    for i, record in enumerate(records, 1):
        logger.info(f"\n--- Record {i}/{len(records)}: {record.get('title')} ---")

        try:
            pi = import_record(importer, record)
            imported_pis.append(pi)
            logger.info(f"✓ Imported: {pi}")

        except Exception as e:
            logger.error(f"✗ Failed to import record {record.get('naId')}: {e}")
            import traceback
            traceback.print_exc()

    # Print statistics
    logger.info("\n6. Import complete!")
    importer.print_stats()

    # List imported entities
    if imported_pis and not DRY_RUN:
        logger.info("\n7. Verifying imported entities...")
        for pi in imported_pis:
            try:
                entity = client.get_entity(pi)
                logger.info(f"  ✓ {pi}: v{entity['ver']}, {len(entity.get('children_pi', []))} children")
            except Exception as e:
                logger.error(f"  ✗ {pi}: {e}")

    logger.info("\n=== Test Complete ===")


if __name__ == "__main__":
    main()
