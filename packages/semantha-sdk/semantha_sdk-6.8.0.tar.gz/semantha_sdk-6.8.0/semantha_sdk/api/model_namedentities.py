from semantha_sdk.api.model_namedentity import ModelNamedentityEndpoint
from semantha_sdk.model.named_entity import NamedEntity
from semantha_sdk.model.named_entity import NamedEntitySchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class ModelNamedentitiesEndpoint(RestEndpoint):
    """ author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/namedentities"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
    def __call__(
            self,
            id: str,
    ) -> ModelNamedentityEndpoint:
        return ModelNamedentityEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[NamedEntity]:
        """
        Get custom entities
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(NamedEntitySchema)

    def post(
        self,
        body: NamedEntity = None,
    ) -> NamedEntity:
        """
        Create a custom entity
        Args:
        body (NamedEntity): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=NamedEntitySchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(NamedEntitySchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all custom entities
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    