from enum import Enum


class HTTPMethods(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH",
    HEAD = "HEAD",
    OPTIONS = "OPTIONS"

