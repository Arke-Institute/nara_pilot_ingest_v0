"""
NARA PI (Persistent Identifier) Naming Utilities

Generates hierarchical, human-readable PI names for NARA entities using ULID.
Format: NARA-<COLLECTION_ID>-<TYPE>-<NARA_ID>-{ulid}

Examples:
- Collection:     NARA-WJC-NSCSW-COL-7388842-01JABBCCDDEEFFGGHHKKMMNNPP
- Series:         NARA-WJC-NSCSW-SER-7585787-01JABBCCDDEEFFGGHHKKMMNNPP
- FileUnit:       NARA-WJC-NSCSW-FILE-23902919-01JABBCCDDEEFFGGHHKKMMNNPP
- DigitalObject:  NARA-WJC-NSCSW-OBJ-55251313-01JABBCCDDEEFFGGHHKKMMNNPP
"""

from ulid import ULID
from typing import Literal

EntityType = Literal["COL", "SER", "FILE", "OBJ"]


def generate_pi(
    collection_id: str,
    entity_type: EntityType,
    nara_id: str | int,
    ulid_value: ULID | None = None
) -> str:
    """
    Generate a PI for a NARA entity (returns ULID only - API requirement).

    Args:
        collection_id: Collection identifier (e.g., "WJC-NSCSW")
        entity_type: Type of entity ("COL", "SER", "FILE", "OBJ")
        nara_id: NARA identifier (naId or objectId)
        ulid_value: Optional ULID (generates new one if not provided)

    Returns:
        ULID string (26 characters)

    Examples:
        >>> generate_pi("WJC-NSCSW", "COL", 7388842)
        '01JABBCCDDEEFFGGHHKKMMNNPP'

        >>> generate_pi("WJC-NSCSW", "FILE", 23902919)
        '01JABBCCDDEEFFGGHHKKMMNNPP'
    """
    if ulid_value is None:
        ulid_value = ULID()

    return str(ulid_value)


def generate_semantic_id(
    collection_id: str,
    entity_type: EntityType,
    nara_id: str | int,
) -> str:
    """
    Generate a semantic identifier for tracking and logging.

    This is NOT the PI used with the API, but a human-readable identifier
    for internal tracking.

    Args:
        collection_id: Collection identifier (e.g., "WJC-NSCSW")
        entity_type: Type of entity ("COL", "SER", "FILE", "OBJ")
        nara_id: NARA identifier (naId or objectId)

    Returns:
        Semantic ID in format: NARA-<COLLECTION_ID>-<TYPE>-<NARA_ID>

    Examples:
        >>> generate_semantic_id("WJC-NSCSW", "COL", 7388842)
        'NARA-WJC-NSCSW-COL-7388842'

        >>> generate_semantic_id("WJC-NSCSW", "FILE", 23902919)
        'NARA-WJC-NSCSW-FILE-23902919'
    """
    return f"NARA-{collection_id}-{entity_type}-{nara_id}"


def parse_pi(pi: str) -> dict[str, str]:
    """
    Parse a NARA PI into its components.

    Args:
        pi: PI string to parse

    Returns:
        Dictionary with: prefix, collection_id, entity_type, nara_id, ulid

    Raises:
        ValueError: If PI format is invalid

    Examples:
        >>> parse_pi("NARA-WJC-NSCSW-FILE-23902919-01JABBCCDDEEFFGGHHKKMMNNPP")
        {
            'prefix': 'NARA',
            'collection_id': 'WJC-NSCSW',
            'entity_type': 'FILE',
            'nara_id': '23902919',
            'ulid': '01JABBCCDDEEFFGGHHKKMMNNPP'
        }
    """
    parts = pi.split("-")

    if len(parts) < 6:
        raise ValueError(f"Invalid PI format: {pi}")

    # Handle collection IDs with hyphens (e.g., WJC-NSCSW)
    # Format: NARA-<part1>-<part2>-<type>-<nara_id>-<ulid>
    prefix = parts[0]
    if prefix != "NARA":
        raise ValueError(f"PI must start with 'NARA', got: {prefix}")

    # For WJC-NSCSW: parts = ["NARA", "WJC", "NSCSW", "FILE", "23902919", "01JAB..."]
    # entity_type is at parts[-3], nara_id at parts[-2], ulid at parts[-1]
    entity_type = parts[-3]
    nara_id = parts[-2]
    ulid = parts[-1]
    collection_id = "-".join(parts[1:-3])

    valid_types = {"COL", "SER", "FILE", "OBJ"}
    if entity_type not in valid_types:
        raise ValueError(f"Invalid entity type: {entity_type}, must be one of {valid_types}")

    return {
        "prefix": prefix,
        "collection_id": collection_id,
        "entity_type": entity_type,
        "nara_id": nara_id,
        "ulid": ulid,
    }


def extract_nara_id(pi: str) -> str:
    """
    Extract just the NARA ID from a PI.

    Args:
        pi: PI string

    Returns:
        NARA ID string

    Examples:
        >>> extract_nara_id("NARA-WJC-NSCSW-FILE-23902919-01JABBCCDDEEFFGGHHKKMMNNPP")
        '23902919'
    """
    return parse_pi(pi)["nara_id"]


def extract_entity_type(pi: str) -> str:
    """
    Extract entity type from a PI.

    Args:
        pi: PI string

    Returns:
        Entity type ("COL", "SER", "FILE", "OBJ")

    Examples:
        >>> extract_entity_type("NARA-WJC-NSCSW-FILE-23902919-01JAB...")
        'FILE'
    """
    return parse_pi(pi)["entity_type"]


def is_valid_pi(pi: str) -> bool:
    """
    Check if a string is a valid NARA PI.

    Args:
        pi: String to validate

    Returns:
        True if valid PI, False otherwise

    Examples:
        >>> is_valid_pi("NARA-WJC-NSCSW-FILE-23902919-01JABBCCDDEEFFGGHHKKMMNNPP")
        True

        >>> is_valid_pi("invalid-pi")
        False
    """
    try:
        parse_pi(pi)
        return True
    except (ValueError, IndexError):
        return False
