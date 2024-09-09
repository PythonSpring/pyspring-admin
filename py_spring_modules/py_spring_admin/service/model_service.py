import json
from typing import Any, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import select
from py_spring.core.entities.component import Component
from py_spring.persistence.core.py_spring_model import PySpringModel


ID = TypeVar("ID", int, UUID)

class TransactionResponse(BaseModel):
    is_success: bool
    message: str
    affected_rows: int

class ModelService(Component):
    def __init__(self) -> None:
        self.models: dict[str, Type[PySpringModel]] = {}

    def post_construct(self) -> None:
        self.models = PySpringModel.get_model_lookup()


    def find_all_models_in_table(self, table_name: str) -> list[dict[str, Any]]:
        model_cls = self.models[table_name]
        with PySpringModel.create_managed_session() as session:
            statement = select(model_cls)
            result = session.exec(statement).fetchall()
            return [json.loads(_model.model_dump_json()) for _model in result]


    def add_model_into_table(self, table_name: str, model_json_dict: dict[str, Any]) -> TransactionResponse:
        model_cls =self.models[table_name]
        model_instance = model_cls.model_validate(model_json_dict)
        try:
            with PySpringModel.create_managed_session() as session:
                session.add(model_instance)
        except Exception as error:
            return TransactionResponse(is_success=False, message=str(error), affected_rows=0)
    
        return TransactionResponse(is_success=True, message="Model added successfully", affected_rows=1)

    
    def delete_model_from_table(self, table_name: str, primary_key_ids_query: dict[str, ID]) -> TransactionResponse:
        model_cls = self.models[table_name]
        with PySpringModel.create_managed_session() as session:
            statement = select(model_cls).filter_by(**primary_key_ids_query)
            optional_model = session.exec(statement).one_or_none()
            if optional_model is None:
                return TransactionResponse(is_success=False, message="Model not found", affected_rows=0)
            session.delete(optional_model)

        return TransactionResponse(is_success=True, message="Model deleted successfully", affected_rows=1)
    
    def update_model_in_table(self, table_name: str, primary_key_ids_query: dict[str, ID], updated_model_json_dict: dict[str, Any], is_upsert: bool = False) -> TransactionResponse:
        model_cls = self.models[table_name]
        try:
            with PySpringModel.create_managed_session() as session:
                statement = select(model_cls).filter_by(**primary_key_ids_query)  # type: ignore
                optional_model_instance = session.exec(statement).one_or_none()
                if optional_model_instance is None:
                    # If the entity does not exist, insert it
                    if not is_upsert:
                        return TransactionResponse(is_success=False, message="Model not found", affected_rows=0)
                    session.add(optional_model_instance)
                else:
                    # If the entity exists, update its attributes
                    for key, value in updated_model_json_dict.items():
                        setattr(optional_model_instance, key, value)
                    session.add(optional_model_instance)            
                return TransactionResponse(is_success=True, message="Model updated successfully", affected_rows=1)
        except Exception as error:
            return TransactionResponse(is_success=False, message=str(error), affected_rows=0)