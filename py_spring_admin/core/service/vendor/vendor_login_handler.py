

from abc import ABC
from typing import Generic, TypeVar

from py_spring_admin.core.repository.commons import UserRead

T = TypeVar("T")

class VendorLoginHandler(ABC, Generic[T]):
    def login(self, user_context: T) -> UserRead:
        ...