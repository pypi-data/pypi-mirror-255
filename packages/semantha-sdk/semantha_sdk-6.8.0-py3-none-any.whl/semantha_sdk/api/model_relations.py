from semantha_sdk.api.model_relation import ModelRelationEndpoint
from semantha_sdk.model.relation import Relation
from semantha_sdk.model.relation import RelationSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelRelationsEndpoint(RestEndpoint):
    """ author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/relations"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
    def __call__(
            self,
            id: str,
    ) -> ModelRelationEndpoint:
        return ModelRelationEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[Relation]:
        """
        Get all relations
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(RelationSchema)

    def post(
        self,
        body: Relation = None,
    ) -> Relation:
        """
        Create a relation
        Args:
        body (Relation): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=RelationSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(RelationSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all relations
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    