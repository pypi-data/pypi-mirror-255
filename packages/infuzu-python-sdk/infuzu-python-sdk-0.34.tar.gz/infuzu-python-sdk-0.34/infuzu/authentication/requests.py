from dataclasses import dataclass
from requests import Response
from .base import InfuzuPublicKey
from .. import constants
from ..http_requests import signed_requests
from ..utils.caching import CacheSystem


@dataclass
class Application:
    id: str
    name: str
    description: str
    is_internal: bool

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"


@dataclass
class AuthenticationKey:
    valid: bool
    id: str
    name: str
    public_key_b64: str
    private_key_hash: str
    application: Application

    def __str__(self) -> str:
        return f"{self.name} ({self.application})" if self.valid else f"{self.name} (INVALID)"

    @property
    def public_key(self) -> InfuzuPublicKey:
        return InfuzuPublicKey.from_base64(self.public_key_b64)


def _fetch_application_information(key_id: str) -> AuthenticationKey:
    response: Response = signed_requests.get(
        url=constants.INFUZU_KEYS_BASE_URL +
            constants.INFUZU_KEYS_KEY_PAIR_ENDPOINT.replace('<str:key_id>', key_id)
    )
    if response.status_code == 200:
        results: dict[str, any] = response.json()
        valid: bool = "valid" in results
        key_information: dict[str, any] = results['valid' if valid else 'invalid']
        application_information: dict[str, any] = key_information.pop('application')
        application: Application = Application(**application_information)
        authentication_key: AuthenticationKey = AuthenticationKey(
            valid=valid, application=application, **key_information
        )
        return authentication_key
    else:
        raise Exception(f"Error getting key information: {response.text}")


ApplicationInfoCache: CacheSystem = CacheSystem(
    default_fetch_function=_fetch_application_information, default_expiry_time=600
)


def get_application_information(key_id: str) -> AuthenticationKey:
    return ApplicationInfoCache.get(key_id, cache_key_name=key_id)
