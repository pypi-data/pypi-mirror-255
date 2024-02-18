from .route import Route
from ..enums import HTTPMethods


class Post(Route):
    def __init__(self, path: str):
        super().__init__(path, HTTPMethods.POST)
