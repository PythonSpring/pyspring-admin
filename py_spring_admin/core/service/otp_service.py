import datetime
import random
from typing import Optional

from py_spring_core import Component
from pydantic import BaseModel


class OneTimePassword(BaseModel):
    code: str
    expired_at: datetime.datetime


class InvalidOtpError(Exception): ...


class OtpService(Component):
    """
    Generates and manages one-time passwords (OTPs) for user authentication.

    The `OtpService` class is responsible for generating and caching OTPs for users. It provides a `generate_otp` method to generate a new OTP for a given user ID and store it in an internal cache.
    """

    def __init__(self) -> None:
        self.one_time_password_cache: dict[str, OneTimePassword] = {}

    def get_otp(self, _id: str) -> OneTimePassword:
        code = self._generate_otp()
        password = OneTimePassword(
            code=code,
            expired_at=datetime.datetime.now() + datetime.timedelta(minutes=3),
        )
        self.one_time_password_cache[_id] = password
        return password

    def validate_otp(self, _id: str, code: str) -> Optional[InvalidOtpError]:
        optional_password = self.one_time_password_cache.get(_id)
        if optional_password is None:
            return InvalidOtpError("OTP not found")
        is_expired = optional_password.expired_at < datetime.datetime.now()
        if is_expired:
            return InvalidOtpError("OTP is expired")
        if optional_password.code != code:
            return InvalidOtpError("OTP is incorrect")

    def delete_otp(self, _id: str) -> None:
        if _id in self.one_time_password_cache:
            self.one_time_password_cache.pop(_id)

    def _generate_otp(self) -> str:
        choices = list(range(0, 10))
        return "".join(str(random.choice(choices)) for _ in range(6))
