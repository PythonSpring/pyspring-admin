import json
from enum import Enum
from typing import Annotated, Any, Type, TypeVar, Union, get_args, get_origin
from uuid import UUID

import cachetools
from py_spring.core.entities.component import Component
from py_spring_model import PySpringModel
from pydantic import BaseModel, Field, computed_field, field_validator
from sqlmodel import select
from typing_extensions import ReadOnly

ID = TypeVar("ID", int, UUID)


def to_camel_case(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(word.title() for word in components[1:])


def to_snake_case(camel_str: str) -> str:
    return "".join(
        [f"_{char.lower()}" if char.isupper() else char for char in camel_str]
    ).lstrip("_")


class InputField(BaseModel):
    key: str
    value: Any

    @field_validator("key", mode="before")
    def validate_key(cls, value: str) -> str:
        return to_snake_case(value)


class _TableColumn(BaseModel):
    private_field: str = Field(exclude=True)
    sql_type: str
    builtin_type: str
    is_primary_key: bool
    is_readonly: bool

    @computed_field
    @property
    def is_enum(self) -> bool:
        return self.builtin_type == Enum.__name__

    @computed_field
    @property
    def field(self) -> str:
        return to_camel_case(self.private_field)

    @computed_field
    @property
    def header(self) -> str:
        return self.field.replace("_", " ").upper()


class TableView(BaseModel):
    table_name: str
    columns: list[_TableColumn]
    rows: list[dict[str, Any]]


class TransactionResponse(BaseModel):
    is_success: bool
    message: str
    affected_rows: int


class ModelService(Component):
    def __init__(self) -> None:
        self.models: dict[str, Type[PySpringModel]] = {}

    def post_construct(self) -> None:
        self.models = PySpringModel.get_model_lookup()
        self.table_definitions = PySpringModel.metadata.tables

    @cachetools.cached(cache={})
    def get_primary_key_columns(self, table_name: str) -> list[str]:
        column_names: list[str] = []
        for column in self.table_definitions[table_name].columns:
            if column.primary_key:
                column_names.append(column.name)
        return column_names

    @cachetools.cached(cache={})
    def get_table_column_enum_choices(self, table_name: str, column: str) -> list[str]:
        model_cls = self.models[table_name]
        column_type: Type[Enum] = model_cls.__annotations__[column]
        return [enum_type.value for enum_type in column_type]

    def find_all_tables(self) -> list[str]:
        return [table_name for table_name in self.table_definitions]

    def find_columns_by_table(self, table_name: str) -> list[_TableColumn]:
        columns: list[_TableColumn] = []
        model_cls = self.models[table_name]
        for column in PySpringModel.metadata.tables[table_name].columns:
            is_readonly: bool = False
            builtin_type: Type[object] = model_cls.__annotations__[column.name]
            is_enum = builtin_type.__class__ == Enum.__class__
            origin_type = get_origin(builtin_type)
            is_optional = origin_type is Union
            is_annotatted = origin_type is Annotated
            if is_annotatted:
                real_type, metadata = get_args(builtin_type)
                is_readonly = metadata is ReadOnly
                builtin_type = real_type

            if is_enum:
                builtin_type = Enum
            if is_optional:
                builtin_type = get_args(builtin_type)[0]
            table_column = _TableColumn(
                private_field=column.name,
                sql_type=str(column.type),
                builtin_type=builtin_type.__name__,
                is_primary_key=column.primary_key,
                is_readonly=is_readonly or column.primary_key,
            )
            columns.append(table_column)

        return columns

    def find_all_models_in_table(self, table_name: str) -> TableView:
        model_cls = self.models[table_name]
        with PySpringModel.create_managed_session() as session:
            statement = select(model_cls)
            result = session.exec(statement).fetchall()
            rows = [json.loads(_model.model_dump_json()) for _model in result]
        table_columns = self.find_columns_by_table(table_name)
        return TableView(table_name=table_name, columns=table_columns, rows=rows)

    def add_model_into_table_by_input_fields(
        self, table_name: str, input_fields: list[InputField]
    ) -> TransactionResponse:
        model_cls = self.models[table_name]
        primary_key_columns = self.get_primary_key_columns(table_name)
        model_dict = {}
        for field in input_fields:
            if field.key in primary_key_columns:
                continue

            model_dict[field.key] = field.value
        return self._add_model_into_table(table_name, model_dict)

    def _add_model_into_table(
        self, table_name: str, model_json_dict: dict[str, Any]
    ) -> TransactionResponse:
        model_cls = self.models[table_name]
        try:
            model_instance = model_cls.model_validate(model_json_dict)
            with PySpringModel.create_managed_session() as session:
                session.add(model_instance)
        except Exception as error:
            return TransactionResponse(
                is_success=False, message=str(error), affected_rows=0
            )

        return TransactionResponse(
            is_success=True, message="Model added successfully", affected_rows=1
        )

    def delete_model_from_table(
        self, table_name: str, primary_key_ids_query: dict[str, ID]
    ) -> TransactionResponse:
        model_cls = self.models[table_name]
        with PySpringModel.create_managed_session() as session:
            statement = select(model_cls).filter_by(**primary_key_ids_query)
            optional_model = session.exec(statement).one_or_none()
            if optional_model is None:
                return TransactionResponse(
                    is_success=False, message="Model not found", affected_rows=0
                )
            session.delete(optional_model)

        return TransactionResponse(
            is_success=True, message="Model deleted successfully", affected_rows=1
        )

    def update_model_in_table(
        self,
        table_name: str,
        primary_key_ids_query: dict[str, ID],
        updated_model_json_dict: dict[str, Any],
        is_upsert: bool = False,
    ) -> TransactionResponse:
        model_cls = self.models[table_name]
        try:
            with PySpringModel.create_managed_session() as session:
                statement = select(model_cls).filter_by(**primary_key_ids_query)  # type: ignore
                optional_model_instance = session.exec(statement).one_or_none()
                if optional_model_instance is None:
                    # If the entity does not exist, insert it
                    if not is_upsert:
                        return TransactionResponse(
                            is_success=False, message="Model not found", affected_rows=0
                        )
                    session.add(optional_model_instance)
                else:
                    # If the entity exists, update its attributes
                    for key, value in updated_model_json_dict.items():
                        setattr(optional_model_instance, key, value)
                    session.add(optional_model_instance)
                return TransactionResponse(
                    is_success=True,
                    message="Model updated successfully",
                    affected_rows=1,
                )
        except Exception as error:
            return TransactionResponse(
                is_success=False, message=str(error), affected_rows=0
            )
