
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.field import Field
from typing import List
from typing import Optional


@dataclass
class Argument:
    """ author semantha, this is a generated class do not change manually! """
    value: Optional[str] = None
    fields: Optional[List[Field]] = None
    condition: Optional["ConditionValue"] = None

from semantha_sdk.model.condition_value import ConditionValue
ArgumentSchema = class_schema(Argument, base_schema=RestSchema)
