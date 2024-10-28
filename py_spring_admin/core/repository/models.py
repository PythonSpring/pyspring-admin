from typing import Annotated, Optional

from py_spring_model import PySpringModel
from pydantic import EmailStr
from sqlmodel import Field
from typing_extensions import ReadOnly

from py_spring_admin.core.repository.commons import UserRead, UserRole


class User(PySpringModel, table=True):
    __tablename__: str = "app_user"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str
    email: EmailStr = Field(unique=True)
    password: Annotated[str, ReadOnly] = Field(exclude=True)
    role: str = Field(default=UserRole.Guest)
    is_verified: bool = Field(default=False)

    def as_read(self) -> UserRead:
        return UserRead(id=self.id, role=self.role, user_name=self.user_name, is_verified=self.is_verified)
