import datetime
from dataclasses import dataclass
from requests import Response
from .. import constants
from ..http_requests import signed_requests


@dataclass
class DocumentVersion:
    id: str
    document: str | None
    vector_store_version: str | None
    page_content: str
    meta_data: dict[str, any] | None
    created_at: str

    @property
    def created_at_datetime(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.created_at)

    @classmethod
    def retrieve(cls, id: str, private_key: str = None) -> 'DocumentVersion':
        api_response: Response = signed_requests.request(
            method="GET",
            url=f"{constants.COGITOBOT_BASE_URL}"
                f"{constants.COGITOBOT_RETRIEVE_DOCUMENT_VERSION_ENDPOINT.replace('<str:document_version_id>', id)}",
            private_key=private_key
        )
        if api_response.status_code == 200:
            return cls(**api_response.json())
