import datetime
from typing import Callable, ClassVar, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from modules.pyspring_modules.py_spring_admin.repository.user_service import RegisterUser, UserService
from modules.pyspring_modules.py_spring_admin.service.auth_service import AuthService
from py_spring.core.entities.controllers.rest_controller import RestController

class CredentialContext(BaseModel):
    password: str


class EmailCredential(CredentialContext):
    email: str


class UserNameCredential(CredentialContext):
    user_name: str


CredentialType = Optional[ EmailCredential | UserNameCredential]


class ExceptionMiddleware:
    async def __call__(self, request: Request, call_next: Callable):
        utc_time = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        try:
            return await call_next(request)
        except Exception as base_exception:
            logger.exception(base_exception)
            return JSONResponse(
                content={"detail": str(base_exception), "timestamp": utc_time},
                status_code=500,
            )

class AdminAuthController(RestController):
    auth_service: AuthService
    user_service: UserService
    COOKIE_NAME: ClassVar[str] = "jwt"


    class Config:
        prefix: str = "/spring-admin/public"

    def register_routes(self) -> None:
        @self.router.post("/login")
        def user_login(
            request: Request, credential: CredentialType = None
        ) -> JSONResponse:
            base_response = JSONResponse("login success")

            if self.__validate_jwt_for_existing_users(request):
                return JSONResponse("already login")
            token = self._handle_token_from_credential(credential)
            base_response.set_cookie(key=self.COOKIE_NAME, value=token, httponly=True)
            return base_response
        
        @self.router.get("/logout")
        def user_logout(request: Request) -> JSONResponse:
            base_response = JSONResponse("logout success")
            base_response.delete_cookie(key=self.COOKIE_NAME)
            return base_response
        
        @self.router.post("/register")
        def user_register(new_user: RegisterUser) -> JSONResponse:
            self.user_service.register_user(new_user)
            return JSONResponse("register success", status_code= status.HTTP_202_ACCEPTED)
        
    def _handle_token_from_credential(self, credential: CredentialType) -> str:
        if credential is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credential provided, getting None for credential validation",
            )

        if isinstance(credential, EmailCredential):
            token = self.auth_service.user_login_by_email(
                credential.email, credential.password
            )
        elif isinstance(credential, UserNameCredential):
            token = self.auth_service.user_login_by_user_name(
                credential.user_name, credential.password
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credential type",
            )
        return token
    
    def __validate_jwt_for_existing_users(self, request: Request) -> bool:
        optional_jwt = request.cookies.get(self.COOKIE_NAME)
        if optional_jwt is None:
            return False
        optional_user = self.auth_service.get_jwt_user_from_jwt(optional_jwt)
        logger.info(f"[JWT USER FOUND] User: {optional_user}")
        return optional_user is not None
        
    def register_middlewares(self) -> None:
        self.app.middleware("http")(ExceptionMiddleware())

        