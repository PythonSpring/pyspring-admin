import datetime
from typing import Callable, ClassVar

from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from py_spring_core import Properties
from py_spring_admin.core.controller.commons import HTTPMethod
from py_spring_admin.core.controller.middleware.middleware_base import MiddlewareBase
from py_spring_admin.core.service.auth_service import AuthService


class AuthMiddlewareProperties(Properties):
    __key__ = "auth_middleware"
    excluded_routes: list[str]

class AuthMiddleware(MiddlewareBase):
    auth_service: AuthService
    auth_middleware_properties: AuthMiddlewareProperties
    
    COOKIE_NAME: ClassVar[str] = "jwt"

    def __init__(self) -> None:
        self.excluded_routes: list[str] = [
            "/spring-admin/public",
            "/docs",
            "/favicon.ico",
            "/openapi.json",
        ]
    def post_construct(self) -> None:
        additional_excluded_routes = self.auth_middleware_properties.excluded_routes
        logger.info(f"[AUTH MIDDLEWARE] Extending excluded routes: {additional_excluded_routes}")
        self.excluded_routes.extend(additional_excluded_routes)

    async def __call__(self, request: Request, call_next: Callable):
        utc_time = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        if request.method == HTTPMethod.OPTIONS:
            return await call_next(request)
        optional_jwt = request.cookies.get(self.COOKIE_NAME)
        for url in self.excluded_routes:
            if url in str(request.url):
                logger.info(f"[AUTH MIDDLEWARE ROUTE EXCLUDED] Bypass URL: {url}")
                return await call_next(request)

        if optional_jwt is None:
            return JSONResponse(
                content={"detail": "Please login first", "timestamp": utc_time},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        user_read = self.auth_service.get_user_from_jwt(optional_jwt)
        if user_read is None:
            return JSONResponse(
                content={"detail": "Please login first", "timestamp": utc_time},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        request.state.user = user_read.model_dump()
        return await call_next(request)
