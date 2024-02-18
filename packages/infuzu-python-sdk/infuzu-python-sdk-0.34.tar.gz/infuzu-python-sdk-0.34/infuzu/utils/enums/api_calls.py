"""
utils/enums/api_calls.py
This module contains the HttpMethod enumeration which represents the various HTTP methods
used in making API calls.
"""

from .base import SerializableEnum


class HttpMethod(SerializableEnum):
    """
    Enumeration representing the different HTTP methods commonly used in RESTful API calls.

    Inherits:
        SerializableEnum: The custom Enum class which allows for serialization.

    Members:
        GET: Represents the HTTP GET method.
        POST: Represents the HTTP POST method.
        PUT: Represents the HTTP PUT method.
        DELETE: Represents the HTTP DELETE method.
        HEAD: Represents the HTTP HEAD method.
        OPTIONS: Represents the HTTP OPTIONS method.
        PATCH: Represents the HTTP PATCH method.
        CONNECT: Represents the HTTP CONNECT method.
        TRACE: Represents the HTTP TRACE method.

    Example:
        >>> HttpMethod.GET
        <HttpMethod.GET: 'GET'>
    """

    GET: 'HttpMethod' = "GET"
    POST: 'HttpMethod' = "POST"
    PUT: 'HttpMethod' = "PUT"
    DELETE: 'HttpMethod' = "DELETE"
    HEAD: 'HttpMethod' = "HEAD"
    OPTIONS: 'HttpMethod' = "OPTIONS"
    PATCH: 'HttpMethod' = "PATCH"
    CONNECT: 'HttpMethod' = "CONNECT"
    TRACE: 'HttpMethod' = "TRACE"
