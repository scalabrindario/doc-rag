"""
File hashing utilities.
"""
import hashlib
from pathlib import Path

from config.logging_config import get_logger

logger = get_logger(__name__)


def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Calculate hash of a file for deduplication.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)

    Returns:
        str: Hash of the file

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If algorithm is not supported
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        hash_func = getattr(hashlib, algorithm)()
    except AttributeError:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            hash_func.update(byte_block)

    file_hash = hash_func.hexdigest()
    logger.info(f"🔑 File hash calculated: {file_hash[:16]}... ({algorithm})")
    return file_hash
