import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class StrEnum(str, Enum): ...


class UserRole(StrEnum):
    Admin = "admin"
    Guest = "guest"


class UserRead(BaseModel):
    id: Optional[int]
    role: str
    user_name: str


class ResetPasswordSchema(BaseModel):
    id: int
    expired_at: datetime.datetime = Field(serialization_alias="exp")
