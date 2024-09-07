from typing import Optional
from modules.py_spring_modules.py_spring_admin.repository.models import User
from py_spring.persistence.repositories.crud_repository import CrudRepository


class UserRepository(CrudRepository[int, User]):
    def find_user_by_user_name(self, user_name: str) -> Optional[User]:
        _, user = self._find_by_query({"user_name": user_name})
        return user
    
    def find_user_by_email(self, email: str) -> Optional[User]:
        _, user = self._find_by_query({"email": email})
        return user