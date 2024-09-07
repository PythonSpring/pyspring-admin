from py_spring.core.entities.component import Component
from py_spring.persistence.core.py_spring_model import PySpringModel


class ModelService(Component):
    ...

    def post_construct(self) -> None:
        tables = PySpringModel.get_model_lookup()
        breakpoint()