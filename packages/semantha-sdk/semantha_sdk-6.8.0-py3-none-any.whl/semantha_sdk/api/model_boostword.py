from semantha_sdk.model.boost_word import BoostWord
from semantha_sdk.model.boost_word import BoostWordSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ModelBoostwordEndpoint(RestEndpoint):
    """ author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._id}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        id: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._id = id

    def get(
        self,
    ) -> BoostWord:
        """
        Get a boostword by id
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(BoostWordSchema)

    
    
    def delete(
        self,
    ) -> None:
        """
        Delete a boostword by id
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: BoostWord
    ) -> BoostWord:
        """
        Update a boostword by id
        """
        return self._session.put(
            url=self._endpoint,
            json=BoostWordSchema().dump(body)
        ).execute().to(BoostWordSchema)
