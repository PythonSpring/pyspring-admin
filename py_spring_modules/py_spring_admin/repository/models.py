
from typing import Optional

from py_spring_modules.py_spring_admin.repository.commons import UserRole
from pydantic import EmailStr
from sqlmodel import Field
from py_spring.persistence.core.py_spring_model import PySpringModel




class User(PySpringModel, table= True):
    __tablename__: str = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str
    email: EmailStr = Field(unique=True)
    password: str = Field(exclude=True)
    role: UserRole = Field(default= UserRole.Guest)
