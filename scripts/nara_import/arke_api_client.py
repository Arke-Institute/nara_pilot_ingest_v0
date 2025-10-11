"""
Arke IPFS API Client

Python client for interacting with the Arke IPFS API.
Wraps API endpoints defined in API_SPEC.md for entity and file management.
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ArkeAPIError(Exception):
    """Base exception for Arke API errors"""
    pass


class ArkeConflictError(ArkeAPIError):
    """Raised when API returns 409 Conflict (e.g., PI already exists, CAS failure)"""
    pass


class ArkeNotFoundError(ArkeAPIError):
    """Raised when API returns 404 Not Found"""
    pass


class ArkeValidationError(ArkeAPIError):
    """Raised when API returns 400 Bad Request"""
    pass


class ArkeClient:
    """
    Client for Arke IPFS API.

    Provides methods for:
    - Uploading files to IPFS
    - Creating and managing entities
    - Appending entity versions
    - Querying entities

    Examples:
        >>> client = ArkeClient("http://localhost:8787")
        >>> cid = client.upload_json({"key": "value"})
        >>> entity = client.create_entity(
        ...     pi="01J8ME3H6FZ3KQ5W1P2XY8K7E5",
        ...     components={"metadata": cid},
        ...     note="Initial version"
        ... )
    """

    def __init__(self, base_url: str, timeout: int = 300):
        """
        Initialize Arke API client.

        Args:
            base_url: Base URL of Arke API (e.g., "http://localhost:8787")
            timeout: Request timeout in seconds (default: 5 minutes)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json_data: Optional JSON body
            params: Optional query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            ArkeAPIError: On HTTP or API errors
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.debug(f"{method} {url}")
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                timeout=self.timeout
            )

            # Handle error responses
            if response.status_code == 400:
                error_data = response.json()
                logger.error(f"Validation error. Request: {json_data}")
                logger.error(f"Response: {error_data}")
                raise ArkeValidationError(f"Validation error: {error_data.get('message', 'Unknown error')} | Details: {error_data.get('details', 'No details')}")

            elif response.status_code == 404:
                error_data = response.json()
                raise ArkeNotFoundError(f"Not found: {error_data.get('message', 'Unknown error')}")

            elif response.status_code == 409:
                error_data = response.json()
                raise ArkeConflictError(f"Conflict: {error_data.get('message', 'Unknown error')}")

            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise ArkeAPIError(f"API error {response.status_code}: {error_data.get('message', 'Unknown error')}")
                except json.JSONDecodeError:
                    raise ArkeAPIError(f"API error {response.status_code}: {response.text}")

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise ArkeAPIError(f"Request failed: {e}") from e

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.

        Returns:
            Dictionary with service, version, status

        Examples:
            >>> client.health_check()
            {'service': 'arke-ipfs-api', 'version': '0.1.0', 'status': 'ok'}
        """
        return self._request("GET", "/")

    def upload_bytes(self, data: bytes, name: str = "file") -> Tuple[str, int]:
        """
        Upload raw bytes to IPFS.

        Args:
            data: Bytes to upload
            name: File name for multipart form

        Returns:
            Tuple of (CID, size)

        Examples:
            >>> cid, size = client.upload_bytes(b"Hello, IPFS!")
            >>> print(f"Uploaded: {cid} ({size} bytes)")
        """
        files = {"file": (name, data)}
        response = self.session.post(
            f"{self.base_url}/upload",
            files=files,
            timeout=self.timeout
        )
        response.raise_for_status()
        result = response.json()[0]  # API returns array
        return result["cid"], result["size"]

    def upload_json(self, data: Dict[str, Any]) -> str:
        """
        Upload JSON data to IPFS.

        Args:
            data: Dictionary to serialize and upload

        Returns:
            CID of uploaded JSON

        Examples:
            >>> cid = client.upload_json({"key": "value"})
        """
        json_bytes = json.dumps(data, sort_keys=True).encode("utf-8")
        cid, _ = self.upload_bytes(json_bytes, name="data.json")
        return cid

    def download_file(self, cid: str) -> bytes:
        """
        Download file content by CID.

        Args:
            cid: IPFS CID to download

        Returns:
            File bytes

        Examples:
            >>> data = client.download_file("bafybeiabc123...")
        """
        response = self.session.get(
            f"{self.base_url}/cat/{cid}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.content

    def create_entity(
        self,
        components: Dict[str, str],
        pi: Optional[str] = None,
        children_pi: Optional[List[str]] = None,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new entity with v1 manifest.

        Args:
            components: Dictionary mapping component names to CIDs
            pi: Optional Persistent Identifier (ULID format). If not provided, API will auto-generate.
            children_pi: Optional list of child entity PIs
            note: Optional version note

        Returns:
            Dictionary with: pi, ver, manifest_cid, tip

        Raises:
            ArkeConflictError: If PI already exists (when PI provided)

        Examples:
            >>> # Auto-generate PI
            >>> entity = client.create_entity(
            ...     components={"metadata": "bafybeiabc123..."},
            ...     note="Initial import from NARA"
            ... )
            >>> print(entity["pi"])  # API-generated ULID

            >>> # Or provide specific PI
            >>> entity = client.create_entity(
            ...     pi="01J8ME3H6FZ3KQ5W1P2XY8K7E5",
            ...     components={"metadata": "bafybeiabc123..."}
            ... )
        """
        payload = {
            "components": components
        }

        if pi:
            payload["pi"] = pi

        if children_pi:
            payload["children_pi"] = children_pi

        if note:
            payload["note"] = note

        return self._request("POST", "/entities", json_data=payload)

    def get_entity(self, pi: str) -> Dict[str, Any]:
        """
        Get latest manifest for entity.

        Args:
            pi: Entity PI

        Returns:
            Entity manifest dictionary

        Raises:
            ArkeNotFoundError: If entity not found

        Examples:
            >>> entity = client.get_entity("NARA-WJC-NSCSW-FILE-23902919-01JAB...")
            >>> print(entity["title"])
        """
        return self._request("GET", f"/entities/{pi}")

    def entity_exists(self, pi: str) -> bool:
        """
        Check if entity exists.

        Args:
            pi: Entity PI

        Returns:
            True if exists, False otherwise

        Examples:
            >>> if client.entity_exists("NARA-WJC-NSCSW-FILE-23902919-01JAB..."):
            ...     print("Entity exists")
        """
        try:
            self.get_entity(pi)
            return True
        except ArkeNotFoundError:
            return False

    def append_version(
        self,
        pi: str,
        expect_tip: str,
        components: Optional[Dict[str, str]] = None,
        children_pi_add: Optional[List[str]] = None,
        children_pi_remove: Optional[List[str]] = None,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Append new version to entity (CAS-protected).

        Args:
            pi: Entity PI
            expect_tip: Expected current tip CID (for CAS)
            components: Optional component updates (partial OK)
            children_pi_add: Optional children to add
            children_pi_remove: Optional children to remove
            note: Optional version note

        Returns:
            Dictionary with: pi, ver, manifest_cid, tip

        Raises:
            ArkeConflictError: If CAS check fails (tip changed)
            ArkeNotFoundError: If entity not found

        Examples:
            >>> result = client.append_version(
            ...     pi="NARA-WJC-NSCSW-FILE-23902919-01JAB...",
            ...     expect_tip="bafybeiabc789...",
            ...     children_pi_add=["NARA-WJC-NSCSW-OBJ-55251313-01JAB..."],
            ...     note="Added first page"
            ... )
        """
        payload = {
            "expect_tip": expect_tip
        }

        if components:
            payload["components"] = components

        if children_pi_add:
            payload["children_pi_add"] = children_pi_add

        if children_pi_remove:
            payload["children_pi_remove"] = children_pi_remove

        if note:
            payload["note"] = note

        return self._request("POST", f"/entities/{pi}/versions", json_data=payload)

    def list_entities(
        self,
        offset: int = 0,
        limit: int = 100,
        include_metadata: bool = False
    ) -> Dict[str, Any]:
        """
        List all entities with pagination.

        Args:
            offset: Starting position (default: 0)
            limit: Max results per page (1-1000, default: 100)
            include_metadata: Include full entity details (default: False)

        Returns:
            Dictionary with: entities, total, offset, limit, has_more

        Examples:
            >>> result = client.list_entities(limit=10)
            >>> for entity in result["entities"]:
            ...     print(f"{entity['pi']}: {entity['tip']}")
        """
        params = {
            "offset": offset,
            "limit": limit,
            "include_metadata": str(include_metadata).lower()
        }
        return self._request("GET", "/entities", params=params)

    def resolve_pi(self, pi: str) -> Dict[str, str]:
        """
        Fast lookup: PI → tip CID (no manifest fetch).

        Args:
            pi: Entity PI

        Returns:
            Dictionary with: pi, tip

        Raises:
            ArkeNotFoundError: If entity not found

        Examples:
            >>> result = client.resolve_pi("NARA-WJC-NSCSW-FILE-23902919-01JAB...")
            >>> print(f"Current tip: {result['tip']}")
        """
        return self._request("GET", f"/resolve/{pi}")

    def close(self):
        """Close HTTP session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
