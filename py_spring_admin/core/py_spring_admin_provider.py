from py_spring_core import EntityProvider

from py_spring_admin.core.controller.admin_main_controller import AdminMainController
from py_spring_admin.core.controller.admin_site_static_file_controller import (
    AdminSiteStaticFileController,
)
from py_spring_admin.core.controller.auth_controller import AdminAuthController
from py_spring_admin.core.controller.middleware.auth_middleware import (
    AuthMiddleware,
    AuthMiddlewareProperties,
)
from py_spring_admin.core.controller.middleware.exception_middleware import (
    ExceptionMiddleware,
)
from py_spring_admin.core.controller.model_controller import ModelController
from py_spring_admin.core.controller.vendor.google_auth_controller import GoogleAuthController
from py_spring_admin.core.py_spring_admin import AdminUserProperties, PySpringAdmin
from py_spring_admin.core.repository.models import User
from py_spring_admin.core.repository.user_repository import UserRepository
from py_spring_admin.core.repository.user_service import UserService
from py_spring_admin.core.service.auth_service import (
    AdminSecurityProperties,
    AuthService,
    SecurityBeanCollection,
)
from py_spring_admin.core.service.model_service import ModelService
from py_spring_admin.core.service.otp_service import OtpService
from py_spring_admin.core.service.smtp_service import SmtpProperties, SmtpService
from py_spring_admin.core.service.vendor.google_auth_service import GoogleAuthService


def provide_py_spring_admin() -> EntityProvider:
    """
    Provides an EntityProvider instance that configures and returns a PySpringAdmin application.

    The EntityProvider instance is responsible for registering all the necessary components, properties, models, bean collections, and REST controllers required for the PySpringAdmin application.

    Returns:
        EntityProvider: The configured EntityProvider instance for the PySpringAdmin application.
    """
    provider = EntityProvider(
        component_classes=[
            PySpringAdmin,
            UserRepository,
            UserService,
            AuthService,
            GoogleAuthService,
            ExceptionMiddleware,
            AuthMiddleware,
            ModelService,
            SmtpService,
            OtpService,
        ],
        properties_classes=[
            AdminUserProperties,
            AdminSecurityProperties,
            AuthMiddlewareProperties,
            SmtpProperties,
        ],
        bean_collection_classes=[SecurityBeanCollection],
        rest_controller_classes=[
            AdminMainController,
            AdminAuthController,
            ModelController,
            GoogleAuthController
        ],
        extneral_dependencies=[User],
    )
    return provider
