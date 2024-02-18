from _typeshed import Incomplete
from pydantic import BaseModel as PydanticBaseModel

class BaseModel(PydanticBaseModel):
    class Config:
        extra: Incomplete
        allow_population_by_field_name: bool
