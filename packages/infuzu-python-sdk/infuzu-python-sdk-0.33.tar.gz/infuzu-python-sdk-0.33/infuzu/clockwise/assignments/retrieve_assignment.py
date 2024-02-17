from dataclasses import dataclass
from requests import Response
from ... import constants
from ...http_requests import signed_requests
from ...utils.enums.api_calls import HttpMethod
from ..errors import NoContentError


@dataclass
class Assignment:
    rule_id: str
    url: str
    private_key_b64: str
    http_method: HttpMethod = HttpMethod.GET
    headers: dict[str, any] | None = None
    body: dict[str, any] | None = None
    max_retries: int = 0
    timeout: int = 30

    @classmethod
    def from_dict(cls, assignment_dict: dict[str, any]) -> 'Assignment':
        rule_id: str = assignment_dict.get("rule_id")
        url: str = assignment_dict.get("url")
        private_key_b64: str = assignment_dict.get("private_key_b64")
        http_method: str = assignment_dict.get("http_method")
        headers: dict[str, any] | None = assignment_dict.get("headers")
        body: dict[str, any] | None = assignment_dict.get("body")
        max_retries: int = assignment_dict.get("max_retries")
        timeout: int = assignment_dict.get("timeout")

        http_method: HttpMethod = HttpMethod.from_name(http_method)

        return cls(
            rule_id=rule_id,
            url=url,
            private_key_b64=private_key_b64,
            http_method=http_method,
            headers=headers,
            body=body,
            max_retries=max_retries,
            timeout=timeout
        )

    def to_dict(self) -> dict[str, any]:
        return {
            "rule_id": self.rule_id,
            "url": self.url,
            "http_method": self.http_method,
            "headers": self.headers,
            "body": self.body,
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }


def get_assignment() -> Assignment:
    response: Response = signed_requests.get(
        url=f"{constants.CLOCKWISE_BASE_URL}{constants.CLOCKWISE_RETRIEVE_ASSIGNMENT_ENDPOINT}"
    )
    if response.status_code == 204:
        raise NoContentError()
    if response.status_code == 200:
        return Assignment.from_dict(response.json())
    else:
        raise ValueError(
            f"Status Code: {response.status_code}, Content: {response.content}"
        )
