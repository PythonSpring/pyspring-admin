
from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field
from py_spring.persistence.core.py_spring_model import PySpringModel


class UserRole(str, Enum):
    Admin = "admin"
    Guest = "guest"

class User(PySpringModel, table= True):
    __tablename__: str = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str
    email: EmailStr = Field(unique=True)
    password: str = Field(exclude=True)
    role: UserRole = Field(default= UserRole.Guest)
