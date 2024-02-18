from semantha_sdk.model.summarization import Summarization
from semantha_sdk.model.summarization import SummarizationSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class SummarizationsEndpoint(RestEndpoint):
    """ author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/summarizations"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        texts: List[str] = None,
        topic: str = None,
        language: str = None,
    ) -> Summarization:
        """
        Generates a summary for given number of texts. If topic is supplied summarization is generated for this topic
        Args:
        texts (List[str]): 
    topic (str): 
    language (str): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "texts": texts,
                "topic": topic,
                "language": language,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(SummarizationSchema)

    
    
    