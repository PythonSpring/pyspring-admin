from typing import Optional

from py_spring_model import CrudRepository

from py_spring_admin.core.repository.models import User


class UserRepository(CrudRepository[int, User]):
    def find_user_by_user_name(self, user_name: str) -> Optional[User]:
        _, user = self._find_by_query({"user_name": user_name})
        return user

    def find_user_by_email(self, email: str) -> Optional[User]:
        _, user = self._find_by_query({"email": email})
        return user
