from enum import Enum
from typing import Optional

from pydantic import BaseModel


class StrEnum(str, Enum):
    ...

class UserRole(StrEnum):
    Admin = "admin"
    Guest = "guest"


class UserRead(BaseModel):
    id: Optional[int]
    role: str
    user_name: str
