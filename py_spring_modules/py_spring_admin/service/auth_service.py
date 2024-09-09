import logging
from typing import Any, Optional
from passlib.context import CryptContext
from uuid import uuid4
from loguru import logger
from pydantic import Field
from typing_extensions import TypedDict
import jwt

from modules.py_spring_modules.py_spring_admin.repository.models import User
from modules.py_spring_modules.py_spring_admin.repository.user_service import UserService
from py_spring.core.entities.bean_collection import BeanCollection
from py_spring.core.entities.component import Component
from py_spring.core.entities.properties.properties import Properties

JsonWebToken = str
class JWTUser(TypedDict):
    id: int

class AdminSecurityProperties(Properties):
    __key__ = "admin_security"
    secret: str = Field(default_factory= lambda: str(uuid4()))



class InvalidAdminUserError(Exception): ...
class UserNotFoundError(Exception): ...

class SecurityBeanCollection(BeanCollection):
    admin_security_properties: AdminSecurityProperties

    @classmethod
    def create_bcrypt_password_context(cls) -> CryptContext:
        return CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService(Component):
    admin_security_properties: AdminSecurityProperties
    uesr_service: UserService
    password_context: CryptContext

    def post_construct(self) -> None:
        logging.getLogger('passlib').setLevel(logging.ERROR) # Hide passlib logs

    def get_hashed_password(self, raw_password: str) -> str:
        return self.password_context.hash(raw_password)
    
    def __is_correct_password(self, raw_password: str, hashed_password: str) -> bool:
        return self.password_context.verify(raw_password, hashed_password)

    

    def __login_user(self, optional_user: Optional[User], password: str) -> JsonWebToken:
        if optional_user is None:
            raise UserNotFoundError("[USER NOT FOUND] User not found")

        if not self.__is_correct_password(password, optional_user.password):
            raise InvalidAdminUserError("[INVALID USER PASSWORD] Password is incorrect")

        return self.__issue_token(optional_user.model_dump())
    

    def user_login_by_user_name(self, user_name: str, password: str) -> JsonWebToken:
        optional_user = self.uesr_service.find_user_by_user_name(user_name)
        return self.__login_user(optional_user, password)
    
    def user_login_by_email(self, email: str, password: str) -> JsonWebToken:
        optional_user = self.uesr_service.find_user_by_email(email)
        return self.__login_user(optional_user, password)
    
    def get_jwt_user_from_jwt(self, token: str) -> Optional[JWTUser]:
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

        return jwt_user

    def __issue_token(self, payload: dict[str, Any]) -> JsonWebToken:
        return jwt.encode(payload, self.admin_security_properties.secret, algorithm="HS256")

    
