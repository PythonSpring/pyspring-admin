from typing import Any, ClassVar, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from py_spring_core import RestController
from pydantic import BaseModel

from py_spring_admin.core.repository.commons import UserRead
from py_spring_admin.core.repository.user_service import RegisterUser, UserService
from py_spring_admin.core.service.auth_service import AuthService
from py_spring_admin.core.service.errors import UserNotFound
from py_spring_admin.core.service.otp_service import OtpPurpose


class CredentialContext(BaseModel):
    password: str


class EmailCredential(CredentialContext):
    email: str


class UserNameCredential(CredentialContext):
    user_name: str


class TokenIssueSchema(BaseModel):
    purpose: OtpPurpose
    email: str




class TokenSchema(BaseModel):
    token: str

class OtpVerificationSchema(BaseModel):
    code: str


class ResetPasswordSchema(BaseModel):
    new_password: str
    password_for_confirmation: str


CredentialType = Optional[EmailCredential | UserNameCredential]


class LoginResponse(BaseModel):
    message: Optional[UserRead] = None
    status: int = status.HTTP_200_OK


class AdminAuthController(RestController):
    auth_service: AuthService
    user_service: UserService
    COOKIE_NAME: ClassVar[str] = "jwt"

    class Config:
        prefix: str = "/spring-admin/public"

    def _create_json_response(
        self, content: str | dict[str, Any], status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        return JSONResponse(content={"message": content, "status": status_code})

    def register_routes(self) -> None:
        @self.router.post("/login")
        def user_login(
            request: Request, credential: CredentialType = None
        ) -> JSONResponse:
            base_response = JSONResponse(content="Login success")
            if self._validate_jwt_for_existing_users(request):
                return base_response
            token = self._handle_token_from_credential(credential)
            base_response.set_cookie(key=self.COOKIE_NAME, value=token)
            return base_response

        @self.router.get("/logout")
        def user_logout(request: Request) -> JSONResponse:
            base_response = self._create_json_response("Logout success")
            base_response.delete_cookie(key=self.COOKIE_NAME)
            return base_response

        @self.router.post("/register")
        def user_register(new_user: RegisterUser) -> JSONResponse:
            self.user_service.register_user(new_user)
            return self._create_json_response(
                "Register success", status_code=status.HTTP_202_ACCEPTED
            )

        @self.router.get("/user")
        def get_current_user(request: Request) -> LoginResponse:
            optional_user_read = self._get_user_from_cookies(request)

            if optional_user_read is None:
                return LoginResponse(
                    message=None, status=status.HTTP_401_UNAUTHORIZED
                )
            return LoginResponse(
                message=optional_user_read, status=status.HTTP_200_OK
            )
        
        @self.router.post("/token")
        def get_token(schema: TokenIssueSchema) -> JSONResponse:
            optional_user = self.user_service.find_user_by_email(schema.email)
            if optional_user is None:
                raise UserNotFound()
            token = self.auth_service.issue_token({"purpose": schema.purpose, "email": schema.email}, is_encrypted= True)
            return self._create_json_response(
                token, status_code=status.HTTP_202_ACCEPTED
            )

        @self.router.post("/resend_email")
        def send_verification_email(token_schema: TokenSchema) -> JSONResponse:
            schema = self.auth_service.decode_token_returning_model(token_schema.token, TokenIssueSchema)
            if schema is None:
                return self._create_json_response(
                    "Invalid token", status_code=status.HTTP_401_UNAUTHORIZED
                )
            
            match schema.purpose:
                case OtpPurpose.PasswordReset:
                    self.auth_service.send_reset_user_password_email(schema.email)
                    return self._create_json_response(
                        "Reset password email sent", status_code=status.HTTP_202_ACCEPTED
                    )
                case OtpPurpose.UserRegistration:
                    self.auth_service.send_user_verification_email(schema.email)
                    return self._create_json_response(
                        "Verification email sent", status_code=status.HTTP_202_ACCEPTED
                    )
        
        @self.router.post("/verify_user_email")
        def verify_email(token_schema: TokenSchema, otp_verification_schema: OtpVerificationSchema) -> JSONResponse:
            token_issue_schema = self.auth_service.decode_token_returning_model(token_schema.token, TokenIssueSchema)
            if token_issue_schema is None:
                return self._create_json_response(
                    "Invalid token", status_code=status.HTTP_401_UNAUTHORIZED
                )
            if token_issue_schema.purpose != OtpPurpose.UserRegistration:
                return self._create_json_response(
                    "Invalid token for wrong purpose", status_code=status.HTTP_401_UNAUTHORIZED
                )
            optional_error = self.auth_service.validate_otp(
                OtpPurpose.UserRegistration, token_issue_schema.email, otp_verification_schema.code
            )
            if optional_error is not None:
                return self._create_json_response(
                    str(optional_error), status_code=status.HTTP_403_FORBIDDEN
                )
            
            self.user_service.update_user_email_verified(token_issue_schema.email)
            return self._create_json_response("Email verified successfully")


        @self.router.post("/reset_password")
        def reset_password(
            token_schema: TokenSchema, 
            token_verification_schema: OtpVerificationSchema,
            password_reset_schema: ResetPasswordSchema
        ) -> JSONResponse:
            token_issue_schema = self.auth_service.decode_token_returning_model(token_schema.token, TokenIssueSchema)
            if token_issue_schema is None:
                return self._create_json_response(
                    "Invalid token", status_code=status.HTTP_401_UNAUTHORIZED
                )
            if token_issue_schema.purpose != OtpPurpose.PasswordReset:
                return self._create_json_response(
                    "Invalid token for wrong purpose", status_code=status.HTTP_401_UNAUTHORIZED
                )
            
            optional_error = self.auth_service.validate_otp(
                OtpPurpose.PasswordReset, token_issue_schema.email, token_verification_schema.code
            )
            if optional_error is not None:
                return self._create_json_response(
                    str(optional_error), status_code=status.HTTP_403_FORBIDDEN
                )
            self.auth_service.update_user_password(
                token_issue_schema.email, password_reset_schema.new_password, password_reset_schema.password_for_confirmation
            )

            response = self._create_json_response(
                "Reset password success, please re-login"
            )
            response.delete_cookie(key=self.COOKIE_NAME)
            return response

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

    def _validate_jwt_for_existing_users(self, request: Request) -> bool:
        return self._get_user_from_cookies(request) is not None

    def _get_user_from_cookies(self, request: Request) -> Optional[UserRead]:
        optional_jwt = request.cookies.get(self.COOKIE_NAME)
        if optional_jwt is None:
            return
        user_read = self.auth_service.get_user_from_jwt(optional_jwt)
        logger.info(f"[JWT USER FOUND] User: {user_read}")
        return user_read
