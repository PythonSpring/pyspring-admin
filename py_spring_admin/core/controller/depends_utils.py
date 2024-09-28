import functools
from typing import Any, Callable

from fastapi import Request
from loguru import logger

from py_spring_admin.core.repository.commons import UserRole
from py_spring_admin.core.service.auth_service import InvalidAdminUserError, JWTUser


def get_current_user(request: Request) -> JWTUser:
    """
    Retrieve the current user from the request.

    Args:
        request (Request): The request object containing the user state.

    Returns:
        JWTUser: The current user extracted from the request state.
    """
    user: JWTUser = request.state.user
    return user


def admin_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to ensure that the user has admin privileges.
    This decorator checks if the user provided in the keyword arguments has an admin role.
    If the user is not found or does not have admin privileges, it raises an InvalidAdminUserError.
    # Usage:
        @admin_required
        def some_admin_function(user: Annotated[JWTUser, Depends(get_current_user)], ...):
            ...
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = kwargs.get("user", None)
        if user is None:
            raise InvalidAdminUserError("[INVALID USER] User is not found")
        if user["role"] != UserRole.Admin.value:
            raise InvalidAdminUserError("[INVALID USER] User is not admin")

        logger.info(f"[ADMIN USER GRANTED] User: {user} is admin, access granted")
        return func(*args, **kwargs)

    return wrapper
