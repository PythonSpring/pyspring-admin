import datetime
from typing import Callable
from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from py_spring_modules.py_spring_admin.controller.middleware.middleware_base import MiddlewareBase


class ExceptionMiddleware(MiddlewareBase):
    async def __call__(self, request: Request, call_next: Callable):
        utc_time = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        try:
            return await call_next(request)
        except Exception as base_exception:
            logger.error(base_exception)
            return JSONResponse(
                content= {"message": str(base_exception), "status": status.HTTP_403_FORBIDDEN},
                status_code=status.HTTP_403_FORBIDDEN,
            )