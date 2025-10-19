#!/usr/bin/env python3
"""
Limited Import Script for WJC-NSCSW Collection

Downloads and imports a limited number of file units from NARA S3 bucket.
Useful for testing and validation before running full import.

Default limit: 150 file units
Rate limiting: 1 minute delay between each file unit
Estimated processing time: ~2.5 hours for 150 records (with 60s delays)
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from lib import ArkeClient, NARAImporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'import_limited_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def download_jsonl_file(file_number: int) -> List[Dict]:
    """
    Download a single JSONL file from S3.

    Args:
        file_number: File number (1-72)

    Returns:
        List of NARA record dictionaries
    """
    s3_path = f"s3://nara-national-archives-catalog/descriptions/collections/coll_WJC-NSCSW/coll_WJC-NSCSW-{file_number}.jsonl"

    logger.info(f"Downloading {s3_path}...")

    cmd = ["aws", "s3", "cp", s3_path, "-", "--no-sign-request"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        records = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                data = json.loads(line)
                records.append(data["record"])

        logger.info(f"Downloaded {len(records)} records from file {file_number}")
        return records

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download file {file_number}: {e}")
        return []


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


def import_record(importer: NARAImporter, record: Dict, record_num: int, total_records: int) -> str:
    """
    Import a single NARA record.

    Args:
        importer: NARAImporter instance
        record: NARA record dictionary
        record_num: Current record number
        total_records: Total number of records to import

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
        date_range=collection["date_range"]
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

    # Log progress
    digital_obj_count = len(record.get("digitalObjects", []))
    logger.info(f"[{record_num}/{total_records}] Importing: {record.get('title')} (naId:{record.get('naId')}, {digital_obj_count} objects)")

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


def save_checkpoint(checkpoint_file: str, file_number: int, record_index: int, importer: NARAImporter):
    """
    Save checkpoint to resume later.

    Includes NARA ID → PI mappings to avoid duplicates on resume.
    """
    with open(checkpoint_file, 'w') as f:
        json.dump({
            "file_number": file_number,
            "record_index": record_index,
            "timestamp": datetime.now().isoformat(),
            "nara_to_pi": importer.nara_to_pi,
            "institution_pi": importer.institution_pi
        }, f, indent=2)


def load_checkpoint(checkpoint_file: str) -> Dict:
    """
    Load checkpoint if exists.

    Returns checkpoint dict with file position and NARA mappings.
    """
    if Path(checkpoint_file).exists():
        with open(checkpoint_file) as f:
            checkpoint = json.load(f)
            # Ensure backwards compatibility with old checkpoints
            if "nara_to_pi" not in checkpoint:
                checkpoint["nara_to_pi"] = {}
            if "institution_pi" not in checkpoint:
                checkpoint["institution_pi"] = None
            return checkpoint
    return {
        "file_number": 1,
        "record_index": 0,
        "nara_to_pi": {},
        "institution_pi": None
    }


def main():
    """Main limited import function"""
    # Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.arke.institute")
    COLLECTION_ID = "WJC-NSCSW"
    TOTAL_JSONL_FILES = 72
    MAX_FILE_UNITS = 300  # Limit the number of file units to import
    CHECKPOINT_FILE = "import_limited_checkpoint.json"

    logger.info("=" * 80)
    logger.info("=== NARA WJC-NSCSW Limited Import ===")
    logger.info(f"API: {API_BASE_URL}")
    logger.info(f"Collection: {COLLECTION_ID}")
    logger.info(f"Max File Units: {MAX_FILE_UNITS}")
    logger.info(f"JSONL Files: {TOTAL_JSONL_FILES}")
    logger.info(f"Checkpoint: {CHECKPOINT_FILE}")
    logger.info("=" * 80)

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

    # Load checkpoint (before initializing importer)
    checkpoint = load_checkpoint(CHECKPOINT_FILE)
    start_file = checkpoint["file_number"]
    start_record_index = checkpoint["record_index"]
    nara_to_pi = checkpoint["nara_to_pi"]
    institution_pi = checkpoint["institution_pi"]

    # Initialize importer with restored mappings
    logger.info("\n2. Initializing importer...")
    importer = NARAImporter(
        api_client=client,
        collection_id=COLLECTION_ID,
        dry_run=False,
        initial_mappings=nara_to_pi,
        institution_pi=institution_pi
    )

    # Import institution (will skip if already exists in mappings)
    logger.info("\n3. Creating/retrieving institution...")
    importer.import_institution(
        name="National Archives",
        description="National Archives and Records Administration",
        url="https://www.archives.gov/"
    )

    if start_file > 1 or start_record_index > 0:
        logger.info(f"\n4. Resuming from checkpoint: file {start_file}, record index {start_record_index}")
        logger.info(f"   Loaded {len(nara_to_pi)} existing NARA ID → PI mappings")
    else:
        logger.info(f"\n4. Starting fresh import (limit: {MAX_FILE_UNITS} file units)...")

    # Process JSONL files until we hit the limit
    total_records_processed = 0
    start_time = time.time()

    try:
        for file_num in range(start_file, TOTAL_JSONL_FILES + 1):
            # Check if we've hit the limit
            if total_records_processed >= MAX_FILE_UNITS:
                logger.info(f"\n✓ Reached limit of {MAX_FILE_UNITS} file units")
                break

            logger.info(f"\n{'=' * 80}")
            logger.info(f"Processing file {file_num}/{TOTAL_JSONL_FILES}: coll_WJC-NSCSW-{file_num}.jsonl")
            logger.info(f"Progress: {total_records_processed}/{MAX_FILE_UNITS} file units")
            logger.info(f"{'=' * 80}")

            # Download file
            records = download_jsonl_file(file_num)

            if not records:
                logger.warning(f"No records in file {file_num}, skipping...")
                continue

            # Determine starting index for this file
            start_idx = start_record_index if file_num == start_file else 0

            # Process each record
            for i, record in enumerate(records):
                # Check limit before processing
                if total_records_processed >= MAX_FILE_UNITS:
                    logger.info(f"✓ Reached limit of {MAX_FILE_UNITS} file units during file {file_num}")
                    break

                if i < start_idx:
                    continue

                try:
                    pi = import_record(importer, record, total_records_processed + 1, MAX_FILE_UNITS)
                    total_records_processed += 1

                    # Wait 1 minute between imports to avoid overwhelming the API
                    logger.info(f"Waiting 60 seconds before next import...")
                    time.sleep(60)

                    # Save checkpoint every 10 records
                    if total_records_processed % 10 == 0:
                        save_checkpoint(CHECKPOINT_FILE, file_num, i + 1, importer)
                        elapsed = time.time() - start_time
                        rate = total_records_processed / elapsed if elapsed > 0 else 0
                        logger.info(f"✓ Checkpoint: {total_records_processed}/{MAX_FILE_UNITS} file units, {rate:.2f} records/sec")

                except Exception as e:
                    logger.error(f"✗ Failed to import record {record.get('naId')}: {e}")
                    import traceback
                    traceback.print_exc()
                    # Continue with next record

            # Break if we hit the limit
            if total_records_processed >= MAX_FILE_UNITS:
                break

            # Reset record index for next file
            start_record_index = 0

            # File completed, save checkpoint
            save_checkpoint(CHECKPOINT_FILE, file_num + 1, 0, importer)
            logger.info(f"Completed file {file_num}/{TOTAL_JSONL_FILES}")

    except KeyboardInterrupt:
        logger.warning("\n\nImport interrupted by user!")
        logger.info("Progress has been saved. Run script again to resume.")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Print final statistics
    elapsed_time = time.time() - start_time
    logger.info("\n" + "=" * 80)
    logger.info("=== Import Complete ===")
    logger.info(f"Total time: {elapsed_time/60:.1f} minutes ({elapsed_time:.1f} seconds)")
    logger.info(f"File units processed: {total_records_processed}/{MAX_FILE_UNITS}")
    logger.info(f"Average rate: {total_records_processed/elapsed_time:.2f} records/sec")
    logger.info("=" * 80)

    importer.print_stats()

    # Clean up checkpoint
    if Path(CHECKPOINT_FILE).exists():
        Path(CHECKPOINT_FILE).unlink()
        logger.info("Checkpoint file removed (import complete)")


if __name__ == "__main__":
    main()
