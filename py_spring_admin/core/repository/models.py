import datetime
from decimal import Decimal
from typing import Annotated, Optional
from typing_extensions import ReadOnly

from py_spring_admin.core.repository.commons import UserRead, UserRole
from pydantic import EmailStr
from sqlmodel import Field

from py_spring.persistence.core.py_spring_model import PySpringModel


class User(PySpringModel, table=True):
    __tablename__: str = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str
    email: EmailStr = Field(unique=True)
    password: Annotated[str, ReadOnly] = Field(exclude=True)
    role: UserRole = Field(default=UserRole.Guest)

    def as_read(self) -> UserRead:
        return UserRead(role=self.role, user_name=self.user_name)
