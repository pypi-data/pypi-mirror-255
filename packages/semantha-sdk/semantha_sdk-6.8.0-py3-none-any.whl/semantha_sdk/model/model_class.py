
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import List
from typing import Optional


@dataclass
class ModelClass:
    """ author semantha, this is a generated class do not change manually! """
    name: Optional[str] = None
    label: Optional[str] = None
    sub_model_classes: Optional[List["ModelClass"]] = None

ModelClassSchema = class_schema(ModelClass, base_schema=RestSchema)
