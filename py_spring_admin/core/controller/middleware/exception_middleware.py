import datetime
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from py_spring_admin.core.controller.middleware.middleware_base import MiddlewareBase
from py_spring_admin.core.service.errors import HandledServerError


class ExceptionMiddleware(MiddlewareBase):
    """
    Middleware for handling exceptions in the application.
    """

    async def __call__(self, request: Request, call_next: Callable):
        utc_time = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        try:
            return await call_next(request)
        
        except HandledServerError as handled_error:
            logger.error(f"Handled Error: {handled_error.message}, code: {handled_error.status_code}")
            return JSONResponse(
                content={
                    "timestamp": utc_time,
                    "message": handled_error.message,
                    "status": handled_error.status_code,
                },
                status_code= status.HTTP_403_FORBIDDEN,
            )
        except Exception as base_exception:
            logger.exception(base_exception)
            return JSONResponse(
                content={
                    "timestamp": utc_time,
                    "message": str(base_exception),
                    "status": status.HTTP_403_FORBIDDEN,
                },
                status_code=status.HTTP_403_FORBIDDEN,
            )
