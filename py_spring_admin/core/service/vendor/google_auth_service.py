

from py_spring_core import Component
from typing import Optional
from pydantic import BaseModel, EmailStr, HttpUrl, computed_field
from py_spring_admin.core.repository.commons import UserRead, UserRole
from py_spring_admin.core.repository.models import User
from py_spring_admin.core.repository.user_service import RegisterUser, UserService
from py_spring_admin.core.service.auth_service import AuthService
from py_spring_admin.core.service.vendor.vendor_login_handler import VendorLoginHandler
from py_spring_admin.core.service.commons import JsonWebToken

class GoogleUserContext(BaseModel):
    """
    Represents the user context information returned from a Google authentication flow.
    
    This model contains the various claims and fields that are typically included in a Google ID token.
    
    Attributes:
        sub (str): The subject identifier, a unique identifier for the user.
        email (EmailStr): The email address of the user.
        email_verified (bool): Whether the email address has been verified.
        name (Optional[str]): The full name of the user.
        given_name (str): The given name (first name) of the user.
        family_name (str): The family name (last name) of the user.
        picture (Optional[HttpUrl]): The URL of the user's profile picture.
        iat (int): The time the ID token was issued, represented as the number of seconds since the Unix epoch.
        exp (int): The time the ID token expires, represented as the number of seconds since the Unix epoch.
        iss (str): The issuer identifier, typically the URL of the Google OAuth 2.0 Authorization Server.
        aud (str): The audience, which identifies the recipient the ID token is intended for.
        nonce (Optional[str]): A string value used to associate a client session with an ID token, and to mitigate replay attacks.
    
        full_name (str): The full name of the user, computed from the given_name and family_name fields.
    """
    sub: str
    email: EmailStr
    email_verified: bool
    name: Optional[str]
    given_name: str
    family_name: str
    picture: Optional[HttpUrl]
    iat: int
    exp: int
    iss: str
    aud: str
    nonce: Optional[str]

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.given_name} {self.family_name}"

class GoogleAuthService(Component, VendorLoginHandler[GoogleUserContext]):
    uesr_service: UserService
    auth_service: AuthService

    def _register_new_user(self, user_context: GoogleUserContext) -> User:
        new_user = self.uesr_service.register_user(
            RegisterUser(
                user_name=user_context.full_name,
                password="",
                email=user_context.email,
                role=UserRole.Guest,
                is_verified=user_context.email_verified
            )
        )
        return new_user



    def login(self, user_context: GoogleUserContext) -> JsonWebToken:
        optional_user = self.uesr_service.find_user_by_email(user_context.email)
        
        if optional_user is None:
            user = self._register_new_user(user_context)
            return self.auth_service.user_login_by_user_name_without_password(user)
        

        return self.auth_service.user_login_by_user_name_without_password(optional_user)