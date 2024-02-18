"""
utils/encryption.py
This module contains utility functions related to encryption and hashing operations.
"""

import hashlib
from PythonAdvancedTyping import check_type


def compute_sha256(text: str) -> str:
    """
    Compute the SHA-256 hash of a given text.

    Args:
        text (str): The input string to be hashed.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash.

    Raises:
        TypeError: If the provided `text` argument is not of type string.

    Example:
        >>> compute_sha256("Hello, World!")
        '315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3'
    """

    check_type(text, "text", str)
    encoded_text: bytes = text.encode()
    sha256 = hashlib.sha256(encoded_text)
    return sha256.hexdigest()
