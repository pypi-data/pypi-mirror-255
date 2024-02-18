from ..di import DIContainer
from ..enums import HTTPMethods
from typing import Callable
from ..routing import Registry


class Route:
    def __init__(self, path: str, method: HTTPMethods):
        self.path = path
        self.method = method
        self.__container = DIContainer(Registry())
        self.__registry = self.__container.get(Registry)

    def __call__(self, func: Callable) -> Callable:
        self.__registry.add_route(func, self.path, self.method)

        return func
