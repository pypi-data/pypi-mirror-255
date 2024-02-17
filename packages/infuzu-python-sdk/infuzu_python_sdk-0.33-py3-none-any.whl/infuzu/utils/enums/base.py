"""
utils/enums/base.py
This module contains the base implementation of a serializable enumeration class.
"""

from enum import Enum


class SerializableEnum(Enum):
    """
    A custom Enum class that supports direct serialization and deserialization.
    This class allows for converting between the name and value of enum members.
    """

    def __str__(self) -> str:
        """
        Override the default string representation of the enum member to return its name.

        Returns:
            str: The name of the enum member.
        """
        return self.name

    @classmethod
    def from_name(cls, name: str) -> 'SerializableEnum':
        """
        Retrieve an enum member by its name.

        Args:
            name (str): The name of the enum member.

        Returns:
            SerializableEnum: The corresponding enum member.

        Example:
            >>> MyEnum = SerializableEnum('MyEnum', {'ONE': 1, 'TWO': 2})
            >>> MyEnum.from_name('ONE')
            <MyEnum.ONE: 1>
        """
        return cls[name]

    @classmethod
    def from_value(cls, value) -> 'SerializableEnum':
        """
        Retrieve an enum member by its value.

        Args:
            value: The value of the enum member. Can be of any type.

        Returns:
            SerializableEnum: The corresponding enum member.

        Example:
            >>> MyEnum = SerializableEnum('MyEnum', {'ONE': 1, 'TWO': 2})
            >>> MyEnum.from_value(2)
            <MyEnum.TWO: 2>
        """
        return cls(value)
