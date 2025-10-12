"""
NARA Collection Schema Definitions for Arke IPFS Import

Defines the JSON schemas for Collection, Series, FileUnit, and DigitalObject entities.
Each entity type has a corresponding catalog record schema that gets uploaded to IPFS.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class SchemaVersion:
    """Schema version constants"""
    INSTITUTION = "nara-institution@v1"
    COLLECTION = "nara-collection@v1"
    SERIES = "nara-series@v1"
    FILEUNIT = "nara-fileunit@v1"
    DIGITALOBJECT = "nara-digitalobject@v1"


def create_institution_catalog_record(
    name: str,
    description: Optional[str] = None,
    url: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create catalog record for an Institution entity.

    Args:
        name: Institution name (e.g., "National Archives")
        description: Optional institution description
        url: Optional institution website URL
        location: Optional physical location

    Returns:
        Catalog record dictionary ready for JSON serialization
    """
    record = {
        "schema": SchemaVersion.INSTITUTION,
        "name": name,
        "import_timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if description:
        record["description"] = description

    if url:
        record["url"] = url

    if location:
        record["location"] = location

    return record


def create_collection_catalog_record(
    nara_naid: int,
    collection_identifier: str,
    title: str,
    date_range: Dict[str, str],
    stats: Optional[Dict[str, int]] = None,
    full_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create catalog record for a Collection entity.

    Args:
        nara_naid: NARA National Archives Identifier
        collection_identifier: Collection ID (e.g., "WJC-NSCSW")
        title: Collection title
        date_range: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
        stats: Optional statistics (total_series, total_file_units, etc.)
        full_metadata: Optional complete NARA metadata for preservation

    Returns:
        Catalog record dictionary ready for JSON serialization
    """
    record = {
        "schema": SchemaVersion.COLLECTION,
        "nara_naId": nara_naid,
        "collection_identifier": collection_identifier,
        "title": title,
        "date_range": date_range,
        "import_timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if stats:
        record["stats"] = stats

    if full_metadata:
        record["nara_full_metadata"] = full_metadata

    return record


def create_series_catalog_record(
    nara_naid: int,
    parent_naid: int,
    title: str,
    date_range: Dict[str, str],
    creators: Optional[List[Dict[str, Any]]] = None,
    full_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create catalog record for a Series entity.

    Args:
        nara_naid: NARA naId for this series
        parent_naid: Parent collection naId
        title: Series title
        date_range: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
        creators: Optional list of creator records
        full_metadata: Optional complete NARA metadata

    Returns:
        Catalog record dictionary
    """
    record = {
        "schema": SchemaVersion.SERIES,
        "nara_naId": nara_naid,
        "parent_naId": parent_naid,
        "title": title,
        "date_range": date_range,
        "import_timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if creators:
        record["creators"] = creators

    if full_metadata:
        record["nara_full_metadata"] = full_metadata

    return record


def create_fileunit_catalog_record(
    nara_naid: int,
    parent_naid: int,
    collection_naid: int,
    title: str,
    record_types: List[str],
    digital_object_count: int,
    access_restriction: Optional[Dict[str, Any]] = None,
    foia_tracking: Optional[str] = None,
    physical_location: Optional[Dict[str, Any]] = None,
    other_titles: Optional[List[str]] = None,
    full_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create catalog record for a FileUnit entity (document/folder).

    Args:
        nara_naid: NARA naId for this file unit
        parent_naid: Parent series naId
        collection_naid: Root collection naId
        title: File unit title
        record_types: List of record types (e.g., ["Textual Records"])
        digital_object_count: Number of digital objects (pages)
        access_restriction: Optional access restriction info
        foia_tracking: Optional FOIA tracking number
        physical_location: Optional physical location info
        other_titles: Optional alternate titles
        full_metadata: Optional complete NARA metadata

    Returns:
        Catalog record dictionary
    """
    record = {
        "schema": SchemaVersion.FILEUNIT,
        "nara_naId": nara_naid,
        "parent_naId": parent_naid,
        "collection_naId": collection_naid,
        "title": title,
        "level": "fileUnit",
        "record_types": record_types,
        "digital_object_count": digital_object_count,
        "import_timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if access_restriction:
        record["access_restriction"] = access_restriction

    if foia_tracking:
        record["foia_tracking"] = foia_tracking

    if physical_location:
        record["physical_location"] = physical_location

    if other_titles:
        record["other_titles"] = other_titles

    if full_metadata:
        record["nara_full_metadata"] = full_metadata

    return record


def create_digitalobject_catalog_record(
    nara_object_id: str,
    parent_naid: int,
    filename: str,
    object_type: str,
    s3_url: str,
    content_hash: Dict[str, str],
    file_size: int,
    page_number: Optional[int] = None,
    extracted_text: Optional[str] = None,
    full_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create catalog record for a DigitalObject entity (individual page/file).

    IMPORTANT: This does NOT store the actual image/PDF bytes in IPFS.
    Instead, it stores:
    - S3 URL for retrieval
    - SHA256 hash for content verification
    - Metadata for cataloging

    Args:
        nara_object_id: NARA objectId
        parent_naid: Parent file unit naId
        filename: Original filename
        object_type: Type (e.g., "Image (JPG)", "Portable Document File (PDF)")
        s3_url: S3 URL where actual content is stored
        content_hash: {"algorithm": "sha256", "digest_hex": "..."}
        file_size: File size in bytes
        page_number: Optional page number within document
        extracted_text: Optional OCR text if available from NARA
        full_metadata: Optional complete NARA digital object metadata

    Returns:
        Catalog record dictionary
    """
    record = {
        "schema": SchemaVersion.DIGITALOBJECT,
        "nara_objectId": nara_object_id,
        "parent_naId": parent_naid,
        "filename": filename,
        "object_type": object_type,
        "file_size": file_size,
        "s3_url": s3_url,
        "content_hash": content_hash,
        "import_timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if page_number is not None:
        record["page_number"] = page_number

    if extracted_text:
        record["extracted_text"] = extracted_text

    if full_metadata:
        record["nara_full_metadata"] = full_metadata

    return record


def validate_catalog_record(record: Dict[str, Any]) -> bool:
    """
    Validate that a catalog record has required fields.

    Args:
        record: Catalog record to validate

    Returns:
        True if valid, raises ValueError if invalid
    """
    schema = record.get("schema")

    if not schema:
        raise ValueError("Catalog record missing 'schema' field")

    required_fields = {
        SchemaVersion.INSTITUTION: ["name"],
        SchemaVersion.COLLECTION: ["nara_naId", "collection_identifier", "title"],
        SchemaVersion.SERIES: ["nara_naId", "parent_naId", "title"],
        SchemaVersion.FILEUNIT: ["nara_naId", "parent_naId", "collection_naId", "title"],
        SchemaVersion.DIGITALOBJECT: ["nara_objectId", "parent_naId", "s3_url", "content_hash"],
    }

    if schema not in required_fields:
        raise ValueError(f"Unknown schema version: {schema}")

    missing = [f for f in required_fields[schema] if f not in record]
    if missing:
        raise ValueError(f"Catalog record missing required fields: {missing}")

    return True


def catalog_record_to_json(record: Dict[str, Any], pretty: bool = False) -> str:
    """
    Convert catalog record to JSON string.

    Args:
        record: Catalog record dictionary
        pretty: If True, use indentation for readability

    Returns:
        JSON string
    """
    validate_catalog_record(record)

    if pretty:
        return json.dumps(record, indent=2, sort_keys=True)
    else:
        return json.dumps(record, sort_keys=True)
