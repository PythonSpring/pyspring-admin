from enum import Enum


class UserRole(str, Enum):
    Admin = "admin"
    Guest = "guest"