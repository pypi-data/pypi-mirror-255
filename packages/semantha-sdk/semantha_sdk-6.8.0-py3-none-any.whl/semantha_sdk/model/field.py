
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema



@dataclass
class Field:
    """ author semantha, this is a generated class do not change manually! """
    id: str
    type: str

FieldSchema = class_schema(Field, base_schema=RestSchema)
