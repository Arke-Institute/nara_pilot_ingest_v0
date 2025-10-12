"""
NARA Hash Utilities

Functions for computing content hashes from S3 URLs without storing files locally.
Downloads files in streaming mode, computes SHA256 hash, and discards bytes.
"""

import hashlib
import requests
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class HashComputationError(Exception):
    """Raised when hash computation fails"""
    pass


def download_and_hash_s3(
    s3_url: str,
    chunk_size: int = 8192,
    timeout: int = 300
) -> Tuple[str, int]:
    """
    Download file from S3 and compute SHA256 hash without storing locally.

    Uses streaming download to minimize memory usage. Computes hash on-the-fly
    and discards bytes immediately after processing.

    Args:
        s3_url: S3 URL to download from
        chunk_size: Size of chunks to read (default 8KB)
        timeout: Request timeout in seconds (default 5 minutes)

    Returns:
        Tuple of (sha256_hex, file_size_bytes)

    Raises:
        HashComputationError: If download or hash computation fails

    Examples:
        >>> hash_hex, size = download_and_hash_s3("https://s3.amazonaws.com/...")
        >>> print(f"SHA256: {hash_hex}, Size: {size} bytes")
        SHA256: a3f58b4c..., Size: 401408 bytes
    """
    try:
        logger.debug(f"Downloading and hashing: {s3_url}")

        # Stream download without loading entire file into memory
        response = requests.get(s3_url, stream=True, timeout=timeout)
        response.raise_for_status()

        # Initialize hash
        hasher = hashlib.sha256()
        total_bytes = 0

        # Process file in chunks
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:  # Filter out keep-alive chunks
                hasher.update(chunk)
                total_bytes += len(chunk)

        digest_hex = hasher.hexdigest()

        logger.debug(f"Hash computed: {digest_hex[:16]}... ({total_bytes} bytes)")

        return digest_hex, total_bytes

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download {s3_url}: {e}")
        raise HashComputationError(f"Download failed: {e}") from e

    except Exception as e:
        logger.error(f"Unexpected error hashing {s3_url}: {e}")
        raise HashComputationError(f"Hash computation failed: {e}") from e


def verify_hash(
    s3_url: str,
    expected_hex: str,
    chunk_size: int = 8192
) -> bool:
    """
    Verify that a file at S3 URL matches the expected SHA256 hash.

    Args:
        s3_url: S3 URL to verify
        expected_hex: Expected SHA256 hash (hex string)
        chunk_size: Chunk size for streaming download

    Returns:
        True if hash matches, False otherwise

    Examples:
        >>> verify_hash("https://s3.amazonaws.com/...", "a3f58b4c...")
        True
    """
    try:
        actual_hex, _ = download_and_hash_s3(s3_url, chunk_size=chunk_size)
        return actual_hex.lower() == expected_hex.lower()

    except HashComputationError:
        return False


def create_content_hash_object(digest_hex: str, algorithm: str = "sha256") -> dict:
    """
    Create a content_hash object for inclusion in catalog records.

    Args:
        digest_hex: Hash digest as hex string
        algorithm: Hash algorithm name (default: "sha256")

    Returns:
        Dictionary with algorithm and digest_hex fields

    Examples:
        >>> create_content_hash_object("a3f58b4c...")
        {'algorithm': 'sha256', 'digest_hex': 'a3f58b4c...'}
    """
    return {
        "algorithm": algorithm,
        "digest_hex": digest_hex
    }


def batch_hash_urls(
    urls: list[str],
    chunk_size: int = 8192,
    on_progress: Optional[callable] = None
) -> dict[str, Tuple[str, int]]:
    """
    Compute hashes for multiple URLs.

    Args:
        urls: List of S3 URLs to hash
        chunk_size: Chunk size for downloads
        on_progress: Optional callback(url, index, total, hash_hex, size)

    Returns:
        Dictionary mapping URL -> (hash_hex, file_size)

    Examples:
        >>> urls = ["https://s3.../page1.jpg", "https://s3.../page2.jpg"]
        >>> results = batch_hash_urls(urls)
        >>> results["https://s3.../page1.jpg"]
        ('a3f58b4c...', 401408)
    """
    results = {}
    total = len(urls)

    for i, url in enumerate(urls):
        try:
            hash_hex, size = download_and_hash_s3(url, chunk_size=chunk_size)
            results[url] = (hash_hex, size)

            if on_progress:
                on_progress(url, i + 1, total, hash_hex, size)

        except HashComputationError as e:
            logger.warning(f"Skipping {url}: {e}")
            results[url] = (None, None)

    return results


def estimate_download_size(urls: list[str], sample_size: int = 10) -> dict:
    """
    Estimate total download size by sampling URLs.

    Args:
        urls: List of S3 URLs
        sample_size: Number of URLs to sample (default: 10)

    Returns:
        Dictionary with: sample_count, avg_size, estimated_total, urls_count

    Examples:
        >>> estimate = estimate_download_size(urls, sample_size=5)
        >>> print(f"Estimated total: {estimate['estimated_total']/1e6:.1f} MB")
        Estimated total: 234.5 MB
    """
    import random

    sample = random.sample(urls, min(sample_size, len(urls)))
    total_sampled = 0
    successful = 0

    for url in sample:
        try:
            _, size = download_and_hash_s3(url)
            total_sampled += size
            successful += 1
        except HashComputationError:
            logger.warning(f"Failed to sample {url}")

    if successful == 0:
        return {
            "sample_count": 0,
            "avg_size": 0,
            "estimated_total": 0,
            "urls_count": len(urls)
        }

    avg_size = total_sampled / successful
    estimated_total = avg_size * len(urls)

    return {
        "sample_count": successful,
        "avg_size": int(avg_size),
        "estimated_total": int(estimated_total),
        "urls_count": len(urls)
    }
