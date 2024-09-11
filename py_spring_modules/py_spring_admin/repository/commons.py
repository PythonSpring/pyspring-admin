from enum import Enum

from pydantic import BaseModel


class UserRole(str, Enum):
    Admin = "admin"
    Guest = "guest"


class UserRead(BaseModel):
    role: UserRole
    user_name: str
