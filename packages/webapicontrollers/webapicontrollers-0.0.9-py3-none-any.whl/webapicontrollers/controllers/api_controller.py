from enum import Enum
from typing import List
from fastapi.responses import JSONResponse
from ..di import DIContainer
from ..routing import Registry
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.routing import APIRoute, BaseRoute
from fastapi.middleware.cors import CORSMiddleware
import logging


class APIController:
    routes = []

    def __init__(self,
                 app: FastAPI,
                 cors_origins: List[str]=None,
                 generate_options_endpoints: bool=True,
                 generate_head_endpoints: bool=True,
                 debug_mode: bool=False
                 ) -> None:
        self.__app = app        
        self.__generate_options_endpoints = generate_options_endpoints
        self.__generate_head_endpoints = generate_head_endpoints   
        self.__debug_mode = debug_mode     
        if cors_origins is not None:
            self.__add_cors(cors_origins)

        self.__register_routes()

    def __register_routes(self) -> None:
        container = DIContainer(Registry())
        registry = container.get(Registry)
        self.__routes = registry.get_routes()

        for func, path, method in self.__routes:
            if hasattr(self,'_route_prefix'):
                path = self._route_prefix + path
                
            if hasattr(self, func.__name__) and callable(getattr(self, func.__name__)):
                bound_method = getattr(self, func.__name__)            
                self.__add_route(bound_method, method, path)

        if self.__generate_options_endpoints:
            self.__add_options_endpoints()

        self.__add_exception_handlers()

    def __add_route(self, bound_method: callable, method: Enum, path: str) -> None:
        self.__app.add_api_route(
            path=path,
            endpoint=bound_method,
            methods=[method.value]
        )
        if method.value == 'GET' and self.__generate_head_endpoints:
            self.__add_head(path)

    def __add_head(self, path: str) -> None:
        self.__app.add_api_route(
            path=path,
            endpoint=self.__head_handler,
            methods=['HEAD']
        )

    def __add_cors(self, cors_origins: List[str]) -> None:
        # noinspection PyTypeChecker
        self.__app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def __add_options_endpoints(self) -> None:
        current_routes = self.__app.routes.copy()
        for route in current_routes:
            if isinstance(route, APIRoute):
                self.__add_options_route(route, current_routes)

    def __add_options_route(self, route: APIRoute, current_routes: List[BaseRoute]) -> None:
        methods = self.__get_methods_for_route(route, current_routes)
        # noinspection PyTypeChecker
        self.__app.add_api_route(
            path=route.path,
            endpoint=lambda: {"allowed_methods": methods},
            methods=["OPTIONS"],
        )

    def __add_exception_handlers(self) -> None:
        self.__app.add_exception_handler(400, self.bad_request)
        self.__app.add_exception_handler(401, self.not_authorized)
        self.__app.add_exception_handler(403, self.forbidden)
        self.__app.add_exception_handler(404, self.not_found)
        self.__app.add_exception_handler(405, self.method_not_allowed)
        self.__app.add_exception_handler(500, self.internal_server_error)

    def bad_request(self, request: Request, exc: HTTPException) -> JSONResponse:
        return self.__handle_exception(
            request, 
            exc, 
            400, 
            f"Bad Request for method {request.method} "
            f"and path {request.url.path}"
        )

    def not_authorized(self, request: Request, exc: HTTPException) -> JSONResponse:
        return self.__handle_exception(
            request, 
            exc, 
            401, 
            f"Not authorized for method {request.method} "
            f"and path {request.url.path}"
        )

    def forbidden(self, request: Request, exc: HTTPException) -> JSONResponse:
        return self.__handle_exception(
            request, 
            exc, 
            403, 
            f"Forbidden for method {request.method} "
            f"and path {request.url.path}"
        )

    def not_found(self, request: Request, exc: HTTPException) -> JSONResponse:
        return self.__handle_exception(
            request, 
            exc, 
            404, 
            f"Path {request.url.path} not found"
        )

    def method_not_allowed(self, request: Request, exc: HTTPException) -> JSONResponse:        
        return self.__handle_exception(
            request, 
            exc, 
            405, 
            f"Method {request.method} not allowed for path {request.url.path}"
        )

    def internal_server_error(self, request: Request, exc: HTTPException) -> JSONResponse:          
        return self.__handle_exception(
            request,
            exc,
            500, 
            f"Internal server error for method {request.method} "
            f"and path {request.url.path}"
        )


    def __handle_exception(self, request: Request, exc: HTTPException, status_code: int, error_message: str) -> JSONResponse:
        self.__log_exception(error_message, exc)
        content = {"detail": error_message}
        if self.__debug_mode and hasattr(exc, "detail"):
            content["exception"] = exc.detail
        return JSONResponse(status_code=status_code, content=content)

    def __log_exception(self, error_message: str, exc: HTTPException) -> None:
        if hasattr(exc, "detail"):
                error_message += f"; Exception: {exc.detail}"
        if logging.getLogger().hasHandlers():
            logger = logging.getLogger(__name__)            
            logger.error(error_message)
        else:
            print(error_message)
    
    @staticmethod
    def __get_methods_for_route(route: APIRoute, current_routes: List[BaseRoute]) -> List[str]:
        methods = set()
        for r in current_routes:
            if isinstance(r, APIRoute) and r.path == route.path:
                methods.update(r.methods)
        return list(methods)

    @staticmethod
    async def __head_handler() -> Response:
        return Response()
    
    
