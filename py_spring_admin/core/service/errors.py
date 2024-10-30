

from enum import Enum
from typing import Literal

class StatusCode(str, Enum):
    UserAlreadyRegisteredAndVerified = "UserAlreadyRegisteredAndVerified"
    UserAlreadyRegisteredAndUnverified = "UserAlreadyRegisteredAndUnverified"

    UserNotFound = "UserNotFound"
    UserEmailNotVerified = "UserEmailNotVerified"
    PermissionDenied = "PermissionDenied"

    PasswordDoesNotMatch = "PasswordDoesNotMatch"
    InvalidOtp = "InvalidOtp"

    EmailDomainNowAllowed = "InvalidOtp"
    




class HandledServerError(Exception):
    def __init__(self, status_code: str, message: str):
        self.status_code = status_code
        self.message = message

class PermissionDeniedError(HandledServerError):
    def __init__(self, message: str):
        super().__init__(status_code=StatusCode.PermissionDenied, message=message)
    

class UserAlreadyRegistered(HandledServerError):
    def __init__(self, status: Literal[StatusCode.UserAlreadyRegisteredAndUnverified, StatusCode.UserAlreadyRegisteredAndVerified]):
        super().__init__(status_code=status, message="User already exists")


class UserNotFound(HandledServerError):
    def __init__(self):
        super().__init__(status_code=StatusCode.UserNotFound, message="User not found")


class PasswordDoesNotMatch(HandledServerError):
    def __init__(self):
        super().__init__(status_code=StatusCode.PasswordDoesNotMatch, message="Password does not match")


class InvalidOtpError(HandledServerError):
    def __init__(self):
        super().__init__(status_code=StatusCode.InvalidOtp, message= "Invalid OTP")

class UserEmailNotVerified(HandledServerError):
    def __init__(self):
        super().__init__(status_code=StatusCode.UserEmailNotVerified, message="User email not verified")


class EmailDomainNowAllowed(HandledServerError):
    def __init__(self):
        super().__init__(status_code=StatusCode.EmailDomainNowAllowed, message="Email domain not allowed")