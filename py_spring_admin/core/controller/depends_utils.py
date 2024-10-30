import functools
from typing import Any, Callable, Optional, Type, cast

import cachetools
from fastapi import Request

from py_spring_admin.core.repository.commons import StrEnum
from py_spring_admin.core.service.auth_service import JWTUser
from py_spring_admin.core.service.errors import PermissionDeniedError, UserEmailNotVerified


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


@cachetools.cached(cache={})
def __find_type_in_params(
    func: Callable[..., Any], target_type: Type[Any]
) -> Optional[str]:
    """
    Finds the name of the parameter in the given function that matches the specified type.

    Args:
        func (Callable[..., Any]): The function to inspect.
        target_type (Type[Any]): The type to search for in the function parameters.

    Returns:
        Optional[str]: The name of the parameter that matches the target type, or `None` if no match is found.
    """
    for attr, param_type in func.__annotations__.items():
        if issubclass(param_type, target_type):
            return attr
    return None


def require_in_roles(roles: list[StrEnum]) -> Callable[..., Any]:
    """
    Decorator that requires the current user to have one or more of the specified roles.

    This decorator checks if the user provided in the keyword arguments has one of the required roles.
    If the user is not found or does not have any of the required roles, it raises a PermissionDeniedError.

    Usage:
        from fastapi import Request

        @require_in_roles([UserRole.Admin, UserRole.Manager])
        def some_admin_or_manager_function(request: Request], ...):
            ...
    """

    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def inner_wrapper(*args, **kwargs):
            param_name = __find_type_in_params(func, Request)
            if param_name is None:
                raise ValueError("Request parameter not found in function annotations")
            request: Request = cast(Request, kwargs.get(param_name))
            user: JWTUser = request.state.user
            
            if not user["is_verified"]:
                raise UserEmailNotVerified()

            for role in roles:
                if user["role"] == role:
                    return func(*args, **kwargs)
            raise PermissionDeniedError(f"User does not have the required role: {role}")

        return inner_wrapper

    return wrapper


def require_role(role: StrEnum) -> Callable[..., Any]:
    """
    Decorator that requires the current user to have the specified role.

    This decorator checks if the user provided in the keyword arguments has the required role.
    If the user is not found or does not have the required role, it raises a PermissionDeniedError.

    Usage:
        from fastapi import Request

        @require_role(UserRole.Admin)
        def some_admin_function(request: Request], ...):
            ...
    """
    return require_in_roles([role])
