from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from py_spring_core import RestController

from py_spring_admin.core.controller.middleware.auth_middleware import AuthMiddleware
from py_spring_admin.core.controller.middleware.exception_middleware import (
    ExceptionMiddleware,
)


class AdminMainController(RestController):
    exception_middleware: ExceptionMiddleware
    auth_middleware: AuthMiddleware

    def enable_cors(self) -> None:
        logger.success("[ENABLE CORS] Enable CORS for FastAPI App")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def register_middlewares(self) -> None:
        self.app.middleware("http")(self.auth_middleware)
        self.app.middleware("http")(self.exception_middleware)

        # cors should be  enabled after middleware registration
        self.enable_cors()
