from typing import ClassVar
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from py_spring import RestController

class AdminSiteStaticFileController(RestController):
    """
    AdminSiteStaticFileController is a RestController responsible for serving static files for the admin site.
    Attributes:
        DIST_DIR (str): The directory path where the static files are located.
    Methods:
        register_routes() -> None:
            Registers the routes for serving static files using the FastAPI StaticFiles middleware.

    Admin can access the site via:
    http://0.0.0.0:8080/spring-admin/public/site
    """
    
    DIST_DIR: ClassVar[str] = "py_spring_admin/core/controller/static/dist"
    def register_routes(self) -> None:
        self.app.mount("/spring-admin/public/site", StaticFiles(directory=self.DIST_DIR, html=True), name="spring_admin")