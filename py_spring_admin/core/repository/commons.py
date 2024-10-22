from enum import Enum
from typing import Optional

from pydantic import BaseModel


class UserRole(str, Enum):
    Admin = "admin"
    Guest = "guest"


class UserRead(BaseModel):
    id: Optional[int]
    role: UserRole
    user_name: str
