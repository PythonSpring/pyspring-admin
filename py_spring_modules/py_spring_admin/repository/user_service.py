from typing import Optional

from pydantic import BaseModel

from modules.py_spring_modules.py_spring_admin.repository.models import User, UserRole
from modules.py_spring_modules.py_spring_admin.repository.user_repository import (
    UserRepository,
)
from py_spring.core.entities.component import Component


class RegisterUser(BaseModel):
    user_name: str
    password: str
    email: str
    role: UserRole = UserRole.Guest


class UserService(Component):
    user_repo: UserRepository

    def find_user_by_user_name(self, user_name: str) -> Optional[User]:
        return self.user_repo.find_user_by_user_name(user_name)

    def find_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.find_user_by_email(email)

    def find_user_by_id(self, user_id: int) -> Optional[User]:
        return self.user_repo.find_by_id(user_id)

    def register_user(self, new_user: RegisterUser):
        user = User(
            user_name=new_user.user_name,
            password=new_user.password,
            email=new_user.email,
            role=new_user.role,
        )
        return self.user_repo.save(user)
