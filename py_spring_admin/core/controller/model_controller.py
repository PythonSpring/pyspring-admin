from typing import Annotated, Any

from fastapi import Depends
from py_spring_admin.core.controller.depends_utils import (
    admin_required,
    get_current_user,
)
from py_spring_admin.core.repository.user_service import UserService
from py_spring_admin.core.service.auth_service import JWTUser
from py_spring_admin.core.service.model_service import (
    InputField,
    ModelService,
    TableView,
    TransactionResponse,
)

from py_spring.core.entities.controllers.rest_controller import RestController


class ModelController(RestController):
    """
    ModelController is a RESTful controller that handles various operations related to models and tables in the application.
    """

    model_service: ModelService
    user_service: UserService

    class Config:
        prefix: str = "/spring-admin/private"

    def register_routes(self) -> None:
        @self.router.get("/tables")
        def get_all_tables() -> list[str]:
            return self.model_service.find_all_tables()

        @self.router.get("/models/{table_name}")
        def get_all_models_in_table(table_name: str) -> TableView:
            return self.model_service.find_all_models_in_table(table_name)

        @self.router.get("/models/enum_choices/{table_name}/{column_name}")
        def get_enum_choices_for_column(table_name: str, column_name: str) -> list[str]:
            return self.model_service.get_table_column_enum_choices(
                table_name, column_name
            )

        @self.router.post("/models/{table_name}")
        @admin_required
        def add_model_into_table(
            user: Annotated[JWTUser, Depends(get_current_user)],
            table_name: str,
            fields: list[InputField],
        ) -> TransactionResponse:
            return self.model_service.add_model_into_table_by_input_fields(
                table_name, fields
            )

        @self.router.delete("/models/{table_name}")
        @admin_required
        def delete_model_from_table(
            user: Annotated[JWTUser, Depends(get_current_user)],
            table_name: str,
            primary_key_ids_query: dict[str, Any],
        ) -> TransactionResponse:
            return self.model_service.delete_model_from_table(
                table_name, primary_key_ids_query
            )

        @self.router.put("/models/{table_name}")
        @admin_required
        def update_model_in_table(
            user: Annotated[JWTUser, Depends(get_current_user)],
            table_name: str,
            primary_key_ids_query: dict[str, Any],
            updated_model_json_dict: dict[str, Any],
        ) -> TransactionResponse:
            return self.model_service.update_model_in_table(
                table_name, primary_key_ids_query, updated_model_json_dict
            )
