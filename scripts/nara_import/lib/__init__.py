"""
NARA Collection Importer Library

Core modules for importing National Archives collections into Arke IPFS database.
"""

from .arke_api_client import ArkeClient, ArkeAPIError, ArkeConflictError, ArkeNotFoundError, ArkeValidationError
from .nara_importer import NARAImporter
from .nara_schema import (
    create_institution_catalog_record,
    create_collection_catalog_record,
    create_series_catalog_record,
    create_fileunit_catalog_record,
    create_digitalobject_catalog_record,
)
from .nara_hash_utils import download_and_hash_s3, create_content_hash_object, HashComputationError
from .nara_pi import generate_pi, generate_semantic_id, parse_pi, is_valid_pi

__all__ = [
    # API Client
    'ArkeClient',
    'ArkeAPIError',
    'ArkeConflictError',
    'ArkeNotFoundError',
    'ArkeValidationError',
    # Importer
    'NARAImporter',
    # Schema
    'create_institution_catalog_record',
    'create_collection_catalog_record',
    'create_series_catalog_record',
    'create_fileunit_catalog_record',
    'create_digitalobject_catalog_record',
    # Hash Utils
    'download_and_hash_s3',
    'create_content_hash_object',
    'HashComputationError',
    # PI Utils
    'generate_pi',
    'generate_semantic_id',
    'parse_pi',
    'is_valid_pi',
]
