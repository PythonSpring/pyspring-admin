from typing import ClassVar

from fastapi.staticfiles import StaticFiles
from loguru import logger
from py_spring import RestController

from py_spring_admin.core.controller import build_utils


class AdminSiteStaticFileController(RestController):
    """
    AdminSiteStaticFileController is a FastAPI controller responsible for serving static files for the admin site.

    Attributes:
        DIST_DIR (str):
            The directory path where the static files, such as HTML, CSS, and JavaScript, are located.

    Methods:
        register_routes() -> None:
            Registers the necessary routes to serve static files using FastAPI's StaticFiles middleware.
            This allows users to access the admin site through predefined URLs.

    Access:
        Admin can access the admin site at:
            http://0.0.0.0:8080/spring-admin/public/site

    Frontend Configuration:
        When building the frontend application, the base URL should be adjusted to ensure proper routing:

        - Angular:
            Set the `base-href` for Angular builds as follows:
                ng build --base-href /spring-admin/public/site/

        - Vue:
            Update the `vue.config.js` file in the root of the Vue project:
                module.exports = {
                    publicPath: '/spring-admin/public/site/'
                };

    By setting the correct base URL, all frontend assets and routes will be properly served by the FastAPI application.
    """

    DIST_DIR: ClassVar[str] = "py_spring_admin/core/controller/static/_dist"

    def register_routes(self) -> None:
        static_file_dir = build_utils.resource_path(self.DIST_DIR)
        logger.success(f"[STATIC FILES] Static files served from {static_file_dir}")
        self.app.mount(
            "/spring-admin/public/site",
            StaticFiles(directory=static_file_dir, html=True),
            name="spring_admin",
        )
