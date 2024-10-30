from fastapi import Request
from fastapi.responses import JSONResponse

from py_spring_admin.core.controller.auth_controller import AdminAuthController
from py_spring_admin.core.service.vendor.google_auth_service import GoogleAuthService, GoogleUserContext

class GoogleAuthController(AdminAuthController):
    google_auth_service: GoogleAuthService
    class Config:
        prefix: str = "/google/public"
    def register_routes(self) -> None:
        @self.router.post("/login")
        def user_login(
            request: Request, user_context: GoogleUserContext
        ) -> JSONResponse:
            base_response = JSONResponse(content="Login success")
            if self._validate_jwt_for_existing_users(request):
                return base_response
            token = self.google_auth_service.login(user_context)
            base_response.set_cookie(key=self.COOKIE_NAME, value=token)
            return base_response
            

