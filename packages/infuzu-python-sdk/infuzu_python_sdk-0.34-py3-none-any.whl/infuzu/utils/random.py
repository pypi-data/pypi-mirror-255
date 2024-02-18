"""
utils/random.py
This module contains utility functions related to random data generation, such as UUIDs.
"""

import uuid


def create_uuid_without_dash() -> str:
    """
    Generate a UUID (Universally Unique Identifier) and return it as a string without dashes.

    Returns:
        str: A 32-character string representation of the UUID without dashes.

    Example:
        >>> create_uuid_without_dash()
        'f47ac10b58cc4372a5670e02b2c3d479'
    """
    return str(uuid.uuid4()).replace('-', '')
