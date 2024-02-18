
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.custom_field import CustomField
from typing import List
from typing import Optional


@dataclass
class DocumentClassBulk:
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    sub_classes: Optional[List["DocumentClassBulk"]] = None
    tags: Optional[List[str]] = None
    color: Optional[str] = None
    comment: Optional[str] = None
    created: Optional[int] = None
    updated: Optional[int] = None
    metata: Optional[str] = None
    custom_fields: Optional[List[CustomField]] = None

DocumentClassBulkSchema = class_schema(DocumentClassBulk, base_schema=RestSchema)
