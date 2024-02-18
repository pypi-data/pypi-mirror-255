
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.rest.rest_client import RestSchema

from semantha_sdk.model.semi_super_vised_document import SemiSuperVisedDocument
from typing import List
from typing import Optional


@dataclass
class SmartClusterSemiSupervisedRequest:
    """ author semantha, this is a generated class do not change manually! """
    clustering_name: Optional[str] = None
    min_cluster_size: Optional[str] = None
    clustering_structure: Optional[str] = None
    topic_over_time_range: Optional[str] = None
    reduce_outliers: Optional[bool] = None
    umap_nr_of_neighbors: Optional[int] = None
    documents: Optional[List[SemiSuperVisedDocument]] = None

SmartClusterSemiSupervisedRequestSchema = class_schema(SmartClusterSemiSupervisedRequest, base_schema=RestSchema)
