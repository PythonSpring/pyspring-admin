
import datetime
from typing import Callable, ClassVar
from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from py_spring_modules.py_spring_admin.controller.middleware.middleware_base import MiddlewareBase
from py_spring_modules.py_spring_admin.repository.user_service import UserService
from py_spring_modules.py_spring_admin.service.auth_service import AuthService


class AuthMiddleware(MiddlewareBase):
    auth_service: AuthService
    protected_routes: ClassVar[list[str]] = [
        "/spring-admin/private"
    ]
    COOKIE_NAME: ClassVar[str] = "jwt"
    async def __call__(self, request: Request, call_next: Callable):
        utc_time = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        optional_jwt = request.cookies.get(self.COOKIE_NAME)
        for url in self.protected_routes:
            if url not in str(request.url):
                logger.info(f"[AUTH MIDDLEWARE ROUTE EXCLUDED] Bypass URL: {url}")
                return await call_next(request)

        if optional_jwt is None:
            return JSONResponse(
                content={"detail": "Please login first", "timestamp": utc_time},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        jwt_user = self.auth_service.get_jwt_user_from_jwt(optional_jwt)
        if jwt_user is None:
            return JSONResponse(
                content={"detail": "Please login first", "timestamp": utc_time},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        request.state.user = jwt_user
        return await call_next(request)