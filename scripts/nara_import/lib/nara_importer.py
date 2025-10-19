"""
NARA Collection Importer

Main importer class for ingesting NARA collections into Arke IPFS database.
Handles hierarchical entity creation: Collection → Series → FileUnit → DigitalObject.
"""

import json
import logging
from typing import Dict, Any, List, Optional

from .arke_api_client import ArkeClient, ArkeConflictError, ArkeNotFoundError
from .nara_schema import (
    create_institution_catalog_record,
    create_collection_catalog_record,
    create_series_catalog_record,
    create_fileunit_catalog_record,
    create_digitalobject_catalog_record,
    catalog_record_to_json,
)
from .nara_hash_utils import download_and_hash_s3, create_content_hash_object, HashComputationError

logger = logging.getLogger(__name__)


class NARAImporter:
    """
    Importer for NARA collections into Arke IPFS database.

    Simplified approach:
    - Let API auto-generate all PIs
    - Track NARA ID → API-generated PI mapping
    - Focus on hierarchy and parent-child relationships
    - Minimal metadata transformation

    Examples:
        >>> importer = NARAImporter(
        ...     api_client=ArkeClient("http://localhost:8787"),
        ...     collection_id="WJC-NSCSW"
        ... )
        >>> importer.import_collection(collection_naid=7388842, ...)
    """

    def __init__(
        self,
        api_client: ArkeClient,
        collection_id: str,
        dry_run: bool = False,
        initial_mappings: Optional[Dict[str, str]] = None,
        institution_pi: Optional[str] = None
    ):
        """
        Initialize NARA importer.

        Args:
            api_client: Arke API client instance
            collection_id: Collection identifier (e.g., "WJC-NSCSW")
            dry_run: If True, log actions but don't create entities
            initial_mappings: Pre-existing NARA ID → PI mappings (for resume)
            institution_pi: Pre-existing institution PI (for resume)
        """
        self.api = api_client
        self.collection_id = collection_id
        self.dry_run = dry_run

        # Single tracking dict: NARA ID → API-generated PI
        self.nara_to_pi: Dict[str, str] = initial_mappings or {}

        # Track institution PI separately
        self.institution_pi: Optional[str] = institution_pi

        # Statistics
        self.stats = {
            "institutions_created": 0,
            "collections_created": 0,
            "series_created": 0,
            "fileunits_created": 0,
            "digitalobjects_created": 0,
            "bytes_hashed": 0,
            "errors": 0,
        }

        # Log if resuming with existing mappings
        if initial_mappings:
            logger.info(f"Loaded {len(initial_mappings)} existing NARA ID → PI mappings")
        if institution_pi:
            logger.info(f"Using existing institution PI: {institution_pi}")

    def import_institution(
        self,
        name: str,
        description: Optional[str] = None,
        url: Optional[str] = None,
        location: Optional[str] = None
    ) -> str:
        """
        Import or retrieve institution entity.

        Args:
            name: Institution name (e.g., "National Archives")
            description: Optional institution description
            url: Optional institution website URL
            location: Optional physical location

        Returns:
            API-generated PI
        """
        # Check if already imported
        if self.institution_pi:
            logger.info(f"Institution already imported: {self.institution_pi}")
            return self.institution_pi

        # Create catalog record
        catalog_record = create_institution_catalog_record(
            name=name,
            description=description,
            url=url,
            location=location
        )

        if self.dry_run:
            logger.info(f"[DRY RUN] Would create institution: {name}")
            self.institution_pi = "dry-run-pi"
            return "dry-run-pi"

        # Upload catalog to IPFS
        catalog_cid = self.api.upload_json(catalog_record)
        logger.debug(f"Uploaded institution catalog: {catalog_cid}")

        # Get Arke genesis block PI
        try:
            arke_block = self.api.get_arke_block()
            arke_pi = arke_block["pi"]
        except Exception as e:
            logger.warning(f"Could not get Arke genesis block: {e}")
            arke_pi = None

        # Create entity with parent_pi to Arke genesis block
        result = self.api.create_entity(
            components={"catalog_record": catalog_cid},
            parent_pi=arke_pi,  # Link to Arke genesis block
            note=f"Institution: {name}"
        )

        pi = result["pi"]
        logger.info(f"Created institution {pi} ({name}) v{result['ver']}")

        # Track PI
        self.institution_pi = pi
        self.stats["institutions_created"] += 1

        if arke_pi:
            logger.info(f"Institution {pi} linked to Arke genesis block ({arke_pi})")

        return pi

    def import_collection(
        self,
        collection_naid: int,
        title: str,
        date_range: Dict[str, str],
        full_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Import or retrieve collection entity.

        Args:
            collection_naid: NARA naId for collection
            title: Collection title
            date_range: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
            full_metadata: Optional complete NARA metadata

        Returns:
            API-generated PI
        """
        # Check if already imported
        nara_id = str(collection_naid)
        if nara_id in self.nara_to_pi:
            logger.info(f"Collection {collection_naid} already imported: {self.nara_to_pi[nara_id]}")
            return self.nara_to_pi[nara_id]

        # Create catalog record
        catalog_record = create_collection_catalog_record(
            nara_naid=collection_naid,
            collection_identifier=self.collection_id,
            title=title,
            date_range=date_range,
            full_metadata=full_metadata
        )

        if self.dry_run:
            logger.info(f"[DRY RUN] Would create collection naId:{collection_naid}")
            self.nara_to_pi[nara_id] = "dry-run-pi"
            return "dry-run-pi"

        # Upload catalog to IPFS
        catalog_cid = self.api.upload_json(catalog_record)
        logger.debug(f"Uploaded collection catalog: {catalog_cid}")

        # Create entity with parent_pi (API generates PI and creates bidirectional link)
        result = self.api.create_entity(
            components={"catalog_record": catalog_cid},
            parent_pi=self.institution_pi,  # Automatic bidirectional link
            note=f"Collection: {title} (naId:{collection_naid})"
        )

        pi = result["pi"]
        logger.info(f"Created collection {pi} (naId:{collection_naid}) v{result['ver']}")

        # Track mapping
        self.nara_to_pi[nara_id] = pi
        self.stats["collections_created"] += 1

        return pi

    def import_series(
        self,
        series_naid: int,
        parent_naid: int,
        title: str,
        date_range: Dict[str, str],
        creators: Optional[List[Dict[str, Any]]] = None,
        full_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Import or retrieve series entity.

        Args:
            series_naid: NARA naId for series
            parent_naid: Parent collection naId
            title: Series title
            date_range: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
            creators: Optional creator records
            full_metadata: Optional complete NARA metadata

        Returns:
            API-generated PI
        """
        # Check if already imported
        nara_id = str(series_naid)
        if nara_id in self.nara_to_pi:
            logger.debug(f"Series {series_naid} already imported: {self.nara_to_pi[nara_id]}")
            return self.nara_to_pi[nara_id]

        # Create catalog record
        catalog_record = create_series_catalog_record(
            nara_naid=series_naid,
            parent_naid=parent_naid,
            title=title,
            date_range=date_range,
            creators=creators,
            full_metadata=full_metadata
        )

        if self.dry_run:
            logger.info(f"[DRY RUN] Would create series naId:{series_naid}")
            self.nara_to_pi[nara_id] = "dry-run-pi"
            return "dry-run-pi"

        # Upload catalog
        catalog_cid = self.api.upload_json(catalog_record)
        logger.debug(f"Uploaded series catalog: {catalog_cid}")

        # Get parent PI
        parent_pi = self.nara_to_pi.get(str(parent_naid))

        # Create entity with parent_pi (automatic bidirectional link)
        result = self.api.create_entity(
            components={"catalog_record": catalog_cid},
            parent_pi=parent_pi,  # Automatic bidirectional link
            note=f"Series: {title} (naId:{series_naid})"
        )

        pi = result["pi"]
        logger.info(f"Created series {pi} (naId:{series_naid}) v{result['ver']}")

        # Track mapping
        self.nara_to_pi[nara_id] = pi
        self.stats["series_created"] += 1

        return pi

    def import_fileunit(
        self,
        fileunit_naid: int,
        parent_series_naid: int,
        collection_naid: int,
        title: str,
        record_types: List[str],
        digital_objects: List[Dict[str, Any]],
        access_restriction: Optional[Dict[str, Any]] = None,
        foia_tracking: Optional[str] = None,
        physical_location: Optional[Dict[str, Any]] = None,
        other_titles: Optional[List[str]] = None,
        full_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Import file unit entity with digital objects.

        Args:
            fileunit_naid: NARA naId for file unit
            parent_series_naid: Parent series naId
            collection_naid: Root collection naId
            title: File unit title
            record_types: Record types (e.g., ["Textual Records"])
            digital_objects: List of digital object records from NARA
            access_restriction: Optional access restriction info
            foia_tracking: Optional FOIA tracking number
            physical_location: Optional physical location
            other_titles: Optional alternate titles
            full_metadata: Optional complete NARA record

        Returns:
            API-generated PI
        """
        # Check if already imported
        nara_id = str(fileunit_naid)
        if nara_id in self.nara_to_pi:
            logger.debug(f"FileUnit {fileunit_naid} already imported: {self.nara_to_pi[nara_id]}")
            return self.nara_to_pi[nara_id]

        # Create catalog record
        catalog_record = create_fileunit_catalog_record(
            nara_naid=fileunit_naid,
            parent_naid=parent_series_naid,
            collection_naid=collection_naid,
            title=title,
            record_types=record_types,
            digital_object_count=len(digital_objects),
            access_restriction=access_restriction,
            foia_tracking=foia_tracking,
            physical_location=physical_location,
            other_titles=other_titles,
            full_metadata=full_metadata
        )

        if self.dry_run:
            logger.info(f"[DRY RUN] Would create fileunit naId:{fileunit_naid} ({len(digital_objects)} objects)")
            self.nara_to_pi[nara_id] = "dry-run-pi"
            return "dry-run-pi"

        # Upload catalog
        catalog_cid = self.api.upload_json(catalog_record)
        logger.debug(f"Uploaded fileunit catalog: {catalog_cid}")

        # Get parent PI
        parent_pi = self.nara_to_pi.get(str(parent_series_naid))

        # Create entity with parent_pi (automatic bidirectional link)
        result = self.api.create_entity(
            components={"catalog_record": catalog_cid},
            parent_pi=parent_pi,  # Automatic bidirectional link
            note=f"FileUnit: {title} (naId:{fileunit_naid}, {len(digital_objects)} pages)"
        )

        pi = result["pi"]
        logger.info(f"Created fileunit {pi} (naId:{fileunit_naid}) v{result['ver']} - {len(digital_objects)} objects")

        # Track mapping
        self.nara_to_pi[nara_id] = pi
        self.stats["fileunits_created"] += 1

        # Import digital objects (they will auto-link to this fileunit as parent)
        for i, obj in enumerate(digital_objects, start=1):
            try:
                obj_pi = self.import_digitalobject(
                    object_id=obj["objectId"],
                    parent_naid=fileunit_naid,
                    filename=obj["objectFilename"],
                    object_type=obj["objectType"],
                    s3_url=obj["objectUrl"],
                    file_size=obj.get("objectFileSize"),
                    page_number=i,
                    extracted_text=obj.get("extractedText"),
                    full_metadata=obj
                )

            except Exception as e:
                logger.error(f"Failed to import digital object {obj.get('objectId')}: {e}")
                self.stats["errors"] += 1

        return pi

    def import_digitalobject(
        self,
        object_id: str,
        parent_naid: int,
        filename: str,
        object_type: str,
        s3_url: str,
        file_size: Optional[int] = None,
        page_number: Optional[int] = None,
        extracted_text: Optional[str] = None,
        full_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Import digital object entity (downloads and hashes, doesn't store image).

        Args:
            object_id: NARA objectId
            parent_naid: Parent file unit naId
            filename: Original filename
            object_type: Object type (e.g., "Image (JPG)")
            s3_url: S3 URL where content is stored
            file_size: Optional file size
            page_number: Optional page number
            extracted_text: Optional OCR text
            full_metadata: Optional complete NARA object metadata

        Returns:
            API-generated PI
        """
        # Check if already imported
        if object_id in self.nara_to_pi:
            logger.debug(f"DigitalObject {object_id} already imported: {self.nara_to_pi[object_id]}")
            return self.nara_to_pi[object_id]

        if self.dry_run:
            logger.info(f"[DRY RUN] Would create digital object objectId:{object_id}")
            self.nara_to_pi[object_id] = "dry-run-pi"
            return "dry-run-pi"

        # Download and hash (without storing locally)
        logger.debug(f"Hashing: {filename}")
        try:
            hash_hex, actual_size = download_and_hash_s3(s3_url)
            content_hash = create_content_hash_object(hash_hex)
            self.stats["bytes_hashed"] += actual_size

        except HashComputationError as e:
            logger.error(f"Failed to hash {filename}: {e}")
            self.stats["errors"] += 1
            raise

        # Create catalog record
        catalog_record = create_digitalobject_catalog_record(
            nara_object_id=object_id,
            parent_naid=parent_naid,
            filename=filename,
            object_type=object_type,
            s3_url=s3_url,
            content_hash=content_hash,
            file_size=file_size or actual_size,
            page_number=page_number,
            extracted_text=extracted_text,
            full_metadata=full_metadata
        )

        # Upload catalog
        catalog_cid = self.api.upload_json(catalog_record)
        logger.debug(f"Uploaded digital object catalog: {catalog_cid}")

        # Get parent PI
        parent_pi = self.nara_to_pi.get(str(parent_naid))

        # Create entity with parent_pi (automatic bidirectional link)
        result = self.api.create_entity(
            components={"digital_object_metadata": catalog_cid},
            parent_pi=parent_pi,  # Automatic bidirectional link
            note=f"Page {page_number}: {filename} (objectId:{object_id})"
        )

        pi = result["pi"]
        logger.info(f"Created digital object {pi} (objectId:{object_id}) v{result['ver']} - {filename}")

        # Track mapping
        self.nara_to_pi[object_id] = pi
        self.stats["digitalobjects_created"] += 1

        return pi

    def print_stats(self):
        """Print import statistics"""
        print("\n=== Import Statistics ===")
        print(f"Institutions created: {self.stats['institutions_created']}")
        print(f"Collections created:  {self.stats['collections_created']}")
        print(f"Series created:       {self.stats['series_created']}")
        print(f"FileUnits created:    {self.stats['fileunits_created']}")
        print(f"DigitalObjects:       {self.stats['digitalobjects_created']}")
        print(f"Bytes hashed:         {self.stats['bytes_hashed']:,}")
        print(f"Errors:               {self.stats['errors']}")
        print("========================\n")
