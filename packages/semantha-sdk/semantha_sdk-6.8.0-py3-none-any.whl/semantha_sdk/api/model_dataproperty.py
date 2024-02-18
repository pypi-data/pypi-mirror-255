from semantha_sdk.model.data_property import DataProperty
from semantha_sdk.model.data_property import DataPropertySchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class ModelDatapropertyEndpoint(RestEndpoint):
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
    ) -> DataProperty:
        """
        Get a data property by id
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params, headers=RestClient.to_header(MediaType.JSON)).execute().to(DataPropertySchema)

    
    
    def delete(
        self,
    ) -> None:
        """
        Delete a data property by id
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: DataProperty
    ) -> DataProperty:
        """
        Update a data property by id
        """
        return self._session.put(
            url=self._endpoint,
            json=DataPropertySchema().dump(body)
        ).execute().to(DataPropertySchema)
