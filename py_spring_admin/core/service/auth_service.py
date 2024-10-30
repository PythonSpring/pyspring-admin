import logging
from email.message import EmailMessage
from typing import Any, Optional, Type, TypeVar
from uuid import uuid4
import cryptography
from cryptography.fernet import Fernet

import cryptography.fernet
import jwt
from loguru import logger
from passlib.context import CryptContext
from py_spring_core import BeanCollection, Component, Properties
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import TypedDict

from py_spring_admin.core.service.errors import PasswordDoesNotMatch, UserNotFound
import py_spring_admin.core.service.template as template
from py_spring_admin.core.repository.commons import UserRead
from py_spring_admin.core.repository.models import User
from py_spring_admin.core.repository.user_service import UserService
from py_spring_admin.core.service.otp_service import InvalidOtpError, OtpPurpose, OtpService
from py_spring_admin.core.service.smtp_service import EmailContentType, SmtpService
from py_spring_admin.core.service.commons import JsonWebTokenEncrypted, Token, IsSendEmailSuccess, JsonWebToken


T = TypeVar("T", bound=BaseModel)


class JWTUser(TypedDict):
    id: int
    role: str
    user_name: str
    is_verified: bool


class AdminSecurityProperties(Properties):
    __key__ = "admin_security"
    secret: str = Field(default_factory=lambda: str(uuid4()))




class SecurityBeanCollection(BeanCollection):
    admin_security_properties: AdminSecurityProperties

    @classmethod
    def create_bcrypt_password_context(cls) -> CryptContext:
        return CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @classmethod
    def create_fernet(cls) -> Fernet:
        return Fernet(Fernet.generate_key())


class AuthService(Component):
    """
    AuthService is responsible for handling authentication-related operations such as hashing passwords,
    verifying user credentials, issuing JSON Web Tokens (JWT), and validating JWTs.
    Attributes:
        admin_security_properties (AdminSecurityProperties): Configuration properties for admin security.
        uesr_service (UserService): Service for user-related operations.
        password_context (CryptContext): Context for password hashing and verification.
    Methods:
        post_construct() -> None:
            Initializes the service by setting the logging level for passlib.
        get_hashed_password(raw_password: str) -> str:
            Returns the hashed version of the provided raw password.
        __is_correct_password(raw_password: str, hashed_password: str) -> bool:
            Checks if the provided raw password matches the hashed password.
        __login_user(optional_user: Optional[User], password: str) -> JsonWebToken:
            Authenticates the user and issues a JWT if credentials are correct.
        user_login_by_user_name(user_name: str, password: str) -> JsonWebToken:
            Authenticates a user by their username and password, then issues a JWT.
        user_login_by_email(email: str, password: str) -> JsonWebToken:
            Authenticates a user by their email and password, then issues a JWT.
        get_user_from_jwt(token: str) -> Optional[UserRead]:
            Validates a JWT and returns the corresponding user information if valid.
        __issue_token(payload: dict[str, Any]) -> JsonWebToken:
            Issues a JWT with the provided payload.
    """

    admin_security_properties: AdminSecurityProperties
    uesr_service: UserService
    smtp_service: SmtpService
    password_context: CryptContext
    fernet: Fernet
    otp_service: OtpService

    def post_construct(self) -> None:
        logging.getLogger("passlib").setLevel(logging.ERROR)  # Hide passlib logs

    def get_hashed_password(self, raw_password: str) -> str:
        return self.password_context.hash(raw_password)

    def __is_correct_password(self, raw_password: str, hashed_password: str) -> bool:
        return self.password_context.verify(raw_password, hashed_password)

    def __login_user(
        self, optional_user: Optional[User], password: str
    ) -> JsonWebToken:
        if optional_user is None:
            raise UserNotFound()

        if not self.__is_correct_password(password, optional_user.password):
            raise PasswordDoesNotMatch()

        return self.issue_token(optional_user.model_dump(), is_encrypted= False)
    
    def user_login_by_user_name_without_password(self, user: User) -> JsonWebToken:
        """
        Authenticates a user by their username without requiring a password, and issues a JSON Web Token (JWT) for the authenticated user.
        
        This method is intended for use with OAuth login flows, where the user's identity is already verified by an external authentication provider.
        
        Args:
            user_name (str): The username of the user to authenticate.
        
        Returns:
            JsonWebToken: A JSON Web Token representing the authenticated user.
        
        Raises:
            UserNotFound: If the user with the provided username does not exist.
        """
        
        return self.issue_token(user.model_dump(), is_encrypted= False)


    def user_login_by_user_name(self, user_name: str, password: str) -> JsonWebToken:
        optional_user = self.uesr_service.find_user_by_user_name(user_name)
        return self.__login_user(optional_user, password)

    def user_login_by_email(self, email: str, password: str) -> JsonWebToken:
        optional_user = self.uesr_service.find_user_by_email(email)
        return self.__login_user(optional_user, password)
    
    def _get_user_by_email(self, email: str) -> User:
        optional_user = self.uesr_service.find_user_by_email(email)
        if optional_user is None:
            raise UserNotFound()
        return optional_user

    def send_reset_user_password_email(self, email: str) -> IsSendEmailSuccess:
        user = self._get_user_by_email(email)
        otp = self.otp_service.get_otp(OtpPurpose.PasswordReset,user.email)
        reset_password_email = self._create_reset_email_mesage(
            otp.code,
            self.smtp_service.get_company_name(),
            user.user_name,
            user.email,
        )
        return self.smtp_service.async_send_email(reset_password_email)
    
    def send_user_verification_email(self, email: str) -> IsSendEmailSuccess:
        user = self._get_user_by_email(email)
        otp = self.otp_service.get_otp(OtpPurpose.UserRegistration, user.email)
        verification_email = self._create_user_verification_email_message(
            otp.code,
            self.smtp_service.get_company_name(),
            user.user_name,
            user.email,
        )
        return self.smtp_service.async_send_email(verification_email)
        

    def validate_otp(
        self, purpose: OtpPurpose, email: str, code: str
    ) -> Optional[InvalidOtpError]:
        return self.otp_service.validate_otp(email, purpose, code)

    def update_user_password(
        self, user_email: str, new_password: str, password_for_confirmation: str
    ) -> None:
        if new_password != password_for_confirmation:
            raise PasswordDoesNotMatch()
        logger.info(f"[PASSWORD UPDATE] Updating password for user: {user_email}")
        self.uesr_service.update_user_password(user_email, new_password)
        logger.info(f"[DELETE OTP] Deleting OTP for user: {user_email}")
        self.otp_service.delete_otp(user_email)

    def _create_reset_email_mesage(
        self, one_time_password: str, company_name: str, user_name: str, user_email: str
    ) -> EmailMessage:
        email_template = template.create_reset_password_email_template(
            company_name=company_name,
            user_name=user_name,
            one_time_password=one_time_password,
        )
        reset_password_email = self.smtp_service.create_email_message(
            receiver_email=user_email,
            subject="Reset Password",
            content=email_template,
            content_type=EmailContentType.HTML,
        )
        return reset_password_email
    
    def _create_user_verification_email_message(
        self, one_time_password: str, company_name: str, user_name: str, user_email: str
    ) -> EmailMessage:
        email_template = template.create_user_verification_email_template(
            company_name=company_name,
            user_name=user_name,
            one_time_password=one_time_password,
        )
        reset_password_email = self.smtp_service.create_email_message(
            receiver_email=user_email,
            subject="User Verification",
            content=email_template,
            content_type=EmailContentType.HTML,
        )
        return reset_password_email



    def get_user_from_jwt(self, token: str) -> Optional[UserRead]:
        """
        Validates a JSON Web Token (JWT) by decoding it using the configured secret key and algorithm.

        Args:
            token (str): The JWT token to validate.
        """
        try:
            jwt_user: JWTUser = jwt.decode(
                token, self.admin_security_properties.secret, algorithms=["HS256"]
            )
            user_id = jwt_user["id"]
            optional_user = self.uesr_service.find_user_by_id(user_id)
            if optional_user is None:
                return

        except jwt.exceptions.InvalidTokenError as invalid_token_error:
            logger.error(invalid_token_error)
            return

        return optional_user.as_read() 

    def issue_token(self, payload: dict[str, Any], is_encrypted: bool) -> Token:
        _jwt = jwt.encode(
            payload, self.admin_security_properties.secret, algorithm="HS256"
        )
        if is_encrypted:
            return self.fernet.encrypt(_jwt.encode()).decode()
        return _jwt

    def decode_token_returning_model(self, token: str, model: Type[T]) -> Optional[T]:
        try:
            _jwt = self.fernet.decrypt(token.encode())
        except cryptography.fernet.InvalidToken:
            logger.error("Key mismatch for decryption...")
            return
        payload = jwt.decode(
            _jwt, self.admin_security_properties.secret, algorithms=["HS256"]
        )
        try:
            return model.model_validate(payload)
        except ValidationError as validation_error:
            logger.error(validation_error)
            return
