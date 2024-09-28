from loguru import logger
from py_spring.core.entities.component import Component
from py_spring.core.entities.properties.properties import Properties

from py_spring_admin.core.repository.models import User, UserRole
from py_spring_admin.core.repository.user_repository import UserRepository
from py_spring_admin.core.service.auth_service import AuthService


class AdminUserProperties(Properties):
    __key__ = "admin_user"
    user_name: str
    password: str
    email: str


class PySpringAdmin(Component):
    __key__ = "py_spring_admin"
    admin_user_properties: AdminUserProperties
    user_repo: UserRepository
    auth_service: AuthService

    def post_construct(self) -> None:
        admin_user = User(
            user_name=self.admin_user_properties.user_name,
            password=self.auth_service.get_hashed_password(
                self.admin_user_properties.password
            ),
            email=self.admin_user_properties.email,
            role=UserRole.Admin,
        )
        is_admin_exists = (
            self.user_repo.find_user_by_user_name(admin_user.user_name) is not None
        )
        if is_admin_exists:
            logger.warning("[ADMIN USER EXISTS] Admin user already exists")
            return
        self.user_repo.save(admin_user)
