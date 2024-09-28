from py_spring import EntityProvider
from py_spring_admin.controller.auth_controller import AdminAuthController
from py_spring_admin.controller.admin_main_controller import AdminMainController
from py_spring_admin.controller.middleware.auth_middleware import AuthMiddleware
from py_spring_admin.controller.middleware.exception_middleware import ExceptionMiddleware
from py_spring_admin.py_spring_admin import AdminUserProperties, PySpringAdmin
from py_spring_admin.repository.models import User
from py_spring_admin.repository.user_repository import UserRepository
from py_spring_admin.repository.user_service import UserService
from py_spring_admin.service.auth_service import AdminSecurityProperties, AuthService, SecurityBeanCollection

def provide_py_spring_admin() -> EntityProvider:
    provider = EntityProvider(
        component_classes=[
            PySpringAdmin,
            UserRepository,
            UserService,
            AuthService,
            ExceptionMiddleware,
            AuthMiddleware
        ],
        properties_classes=[
            AdminUserProperties,
            AdminSecurityProperties
        ],
        model_classes=[
            User
        ],
        bean_collection_classes= [
            SecurityBeanCollection
        ],
        rest_controller_classes= [
            AdminMainController,
            AdminAuthController
        ]
        
    )
    return provider