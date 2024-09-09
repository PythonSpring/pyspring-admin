import functools
from typing import Any, Callable
from fastapi import Request
from loguru import logger
from py_spring_modules.py_spring_admin.repository.commons import UserRole
from py_spring_modules.py_spring_admin.service.auth_service import InvalidAdminUserError, JWTUser


def get_current_user(request: Request) -> JWTUser:
    user: JWTUser = request.state.user
    return user

def admin_required(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = kwargs.get("user", None)
        if user is None:
            raise InvalidAdminUserError("[INVALID USER] User is not found")
        if user["role"] != UserRole.Admin.value:
            raise InvalidAdminUserError("[INVALID USER] User is not admin")
        
        logger.info(f"[ADMIN USER GRANTED] User {user['id']} is admin, access granted")
        return func(*args, **kwargs)

    return wrapper