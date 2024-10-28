from typing import Optional

from loguru import logger
from passlib.context import CryptContext
from py_spring_core import Component
from py_spring_model import PySpringModel
from pydantic import BaseModel

from py_spring_core.core.entities.component import Component
from pydantic import BaseModel
from passlib.context import CryptContext
from py_spring_admin.core.repository.commons import UserRead
from py_spring_admin.core.repository.models import User, UserRole
from py_spring_admin.core.repository.user_repository import UserRepository
from py_spring_model import PySpringModel

class RegisterUser(BaseModel):
    user_name: str
    password: str
    email: str
    role: UserRole = UserRole.Guest


class UserService(Component):
    user_repo: UserRepository
    password_context: CryptContext

    def find_user_by_user_name(self, user_name: str) -> Optional[User]:
        return self.user_repo.find_user_by_user_name(user_name)

    def find_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.find_user_by_email(email)

    def find_user_by_id(self, user_id: int) -> Optional[User]:
        return self.user_repo.find_by_id(user_id)

    def get_hashed_password(self, raw_password: str) -> str:
        return self.password_context.hash(raw_password)

    def update_user_password(self, user_email: str, new_password: str) -> UserRead:
        with PySpringModel.create_managed_session() as session:
            _, optional_user = self.user_repo._find_by_query(
                {"email": user_email}, session
            )
            if optional_user is None:
                raise ValueError("User not found")
            optional_user.password = self.get_hashed_password(new_password)
            logger.info(f"User password updated: {optional_user}")
            user_read = optional_user.as_read()

        return user_read
    
    def update_user_email_verified(self, user_email: str) -> UserRead:
        with PySpringModel.create_managed_session() as session:
            _, optional_user = self.user_repo._find_by_query(
                {"email": user_email}, session
            )
            if optional_user is None:
                raise ValueError("User not found")
            optional_user.is_verified = True
            logger.info(f"User email verified: {optional_user}")
            user_read = optional_user.as_read()

        return user_read
        ...

    def register_user(self, new_user: RegisterUser) -> User:
        hashed_password = self.get_hashed_password(new_user.password)
        user = User(
            user_name=new_user.user_name,
            password=hashed_password,
            email=new_user.email,
            role=new_user.role,
        )
        return self.user_repo.save(user)
