from io import IOBase
from semantha_sdk.model.document import Document
from semantha_sdk.model.document import DocumentSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class DocumentsEndpoint(RestEndpoint):
    """ author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/documents"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        file: IOBase = None,
        text: str = None,
        type: str = None,
        documenttype: str = None,
        withareas: bool = None,
        withcontextparagraphs: bool = None,
        mode: str = None,
        withparagraphtype: bool = None,
    ) -> List[Document]:
        """
        Creates a list of document models from an input document (pdf, docx, txt, zip, xlsx)
            This service can be used with different accept headers which return the document model as json, pdf or docx. You can send a docx and return it as pdf which is based on the document model.
        Args:
        file (IOBase): Input document (left document).
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    type (str): Choose the structure of a document for similarity or extraction. The type depends on the Use Case you're in.
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    withareas (bool): Gives back the coordinates of referenced area.
    withcontextparagraphs (bool): 
    mode (str): When using the references endpoint: Use mode to determine the type of search semantha should perform. 
            fingerprint: semantic search based on sentences; 
            keyword: keyword: search based on sentences; 
            document: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. Higher scores indicate higher similarity. Please note that the similarity score has no upper limit and is not normalized; 
            document_fingerprint: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. The results are then reranked based on a semantic search. This reranking results in normalized scores and as such represents an enhancement of the mode document; 
            fingerprint_keyword (formerly auto): semantic search, if no results are found a keyword search is performed
            Creating document model: It also defines what structure should be considered for what operator (similarity or extraction).
    withparagraphtype (bool): The type of the paragraph, for example heading, text
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "text": text,
                "type": type,
                "documenttype": documenttype,
                "withareas": withareas,
                "withcontextparagraphs": withcontextparagraphs,
                "mode": mode,
                "withparagraphtype": withparagraphtype,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(DocumentSchema)
    def post_as_xlsx(
        self,
        file: IOBase = None,
        text: str = None,
        type: str = None,
        documenttype: str = None,
        withareas: bool = None,
        withcontextparagraphs: bool = None,
        mode: str = None,
        withparagraphtype: bool = None,
    ) -> IOBase:
        """
        Creates a list of document models from an input document (pdf, docx, txt, zip, xlsx)
            This service can be used with different accept headers which return the document model as json, pdf or docx. You can send a docx and return it as pdf which is based on the document model.
        Args:
        file (IOBase): Input document (left document).
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    type (str): Choose the structure of a document for similarity or extraction. The type depends on the Use Case you're in.
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    withareas (bool): Gives back the coordinates of referenced area.
    withcontextparagraphs (bool): 
    mode (str): When using the references endpoint: Use mode to determine the type of search semantha should perform. 
            fingerprint: semantic search based on sentences; 
            keyword: keyword: search based on sentences; 
            document: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. Higher scores indicate higher similarity. Please note that the similarity score has no upper limit and is not normalized; 
            document_fingerprint: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. The results are then reranked based on a semantic search. This reranking results in normalized scores and as such represents an enhancement of the mode document; 
            fingerprint_keyword (formerly auto): semantic search, if no results are found a keyword search is performed
            Creating document model: It also defines what structure should be considered for what operator (similarity or extraction).
    withparagraphtype (bool): The type of the paragraph, for example heading, text
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "text": text,
                "type": type,
                "documenttype": documenttype,
                "withareas": withareas,
                "withcontextparagraphs": withcontextparagraphs,
                "mode": mode,
                "withparagraphtype": withparagraphtype,
            },
            headers=RestClient.to_header(MediaType.XLSX),
            q_params=q_params
        ).execute()
        return response.as_bytesio()
    def post_as_docx(
        self,
        file: IOBase = None,
        text: str = None,
        type: str = None,
        documenttype: str = None,
        withareas: bool = None,
        withcontextparagraphs: bool = None,
        mode: str = None,
        withparagraphtype: bool = None,
    ) -> IOBase:
        """
        Creates a list of document models from an input document (pdf, docx, txt, zip, xlsx)
            This service can be used with different accept headers which return the document model as json, pdf or docx. You can send a docx and return it as pdf which is based on the document model.
        Args:
        file (IOBase): Input document (left document).
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    type (str): Choose the structure of a document for similarity or extraction. The type depends on the Use Case you're in.
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    withareas (bool): Gives back the coordinates of referenced area.
    withcontextparagraphs (bool): 
    mode (str): When using the references endpoint: Use mode to determine the type of search semantha should perform. 
            fingerprint: semantic search based on sentences; 
            keyword: keyword: search based on sentences; 
            document: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. Higher scores indicate higher similarity. Please note that the similarity score has no upper limit and is not normalized; 
            document_fingerprint: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. The results are then reranked based on a semantic search. This reranking results in normalized scores and as such represents an enhancement of the mode document; 
            fingerprint_keyword (formerly auto): semantic search, if no results are found a keyword search is performed
            Creating document model: It also defines what structure should be considered for what operator (similarity or extraction).
    withparagraphtype (bool): The type of the paragraph, for example heading, text
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "text": text,
                "type": type,
                "documenttype": documenttype,
                "withareas": withareas,
                "withcontextparagraphs": withcontextparagraphs,
                "mode": mode,
                "withparagraphtype": withparagraphtype,
            },
            headers=RestClient.to_header(MediaType.DOCX),
            q_params=q_params
        ).execute()
        return response.as_bytesio()

    
    
    