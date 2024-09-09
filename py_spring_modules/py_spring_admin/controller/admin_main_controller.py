

from py_spring_modules.py_spring_admin.controller.middleware.auth_middleware import AuthMiddleware
from py_spring_modules.py_spring_admin.controller.middleware.exception_middleware import ExceptionMiddleware
from py_spring.core.entities.controllers.rest_controller import RestController


class AdminMainController(RestController):
    exception_middleware: ExceptionMiddleware
    auth_middleware: AuthMiddleware

    def register_middlewares(self) -> None:
        self.app.middleware("http")(self.exception_middleware)
        self.app.middleware("http")(self.auth_middleware)