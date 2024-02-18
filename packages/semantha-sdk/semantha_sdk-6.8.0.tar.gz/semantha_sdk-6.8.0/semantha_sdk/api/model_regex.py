from semantha_sdk.model.regex import Regex
from semantha_sdk.model.regex import RegexSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ModelRegexEndpoint(RestEndpoint):
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
    ) -> Regex:
        """
        Get a regex by id
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(RegexSchema)

    
    
    def delete(
        self,
    ) -> None:
        """
        Delet a regex by id
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: Regex
    ) -> Regex:
        """
        Update a regex by id
        """
        return self._session.put(
            url=self._endpoint,
            json=RegexSchema().dump(body)
        ).execute().to(RegexSchema)
