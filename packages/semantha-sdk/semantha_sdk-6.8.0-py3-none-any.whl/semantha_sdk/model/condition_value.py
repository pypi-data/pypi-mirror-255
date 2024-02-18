
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from typing import List
from typing import Optional


@dataclass
class ConditionValue:
    """ author semantha, this is a generated class do not change manually! """
    function: Optional[str] = None
    arguments: Optional[List["Argument"]] = None

from semantha_sdk.model.argument import Argument
ConditionValueSchema = class_schema(ConditionValue, base_schema=RestSchema)
