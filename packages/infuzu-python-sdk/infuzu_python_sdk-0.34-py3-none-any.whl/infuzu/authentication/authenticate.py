from .base import (InfuzuPublicKey, InfuzuKeys)
from .requests import (Application, AuthenticationKey, get_application_information)
from .shortcuts import (get_key_pair_id_from_signature, verify_message_signature)


def verify_diverse_message_signature(
        message: str, message_signature: str, public_key: AuthenticationKey | InfuzuPublicKey | InfuzuKeys | str
) -> bool:
    if isinstance(public_key, AuthenticationKey):
        public_key_b64: str = public_key.public_key_b64
    elif isinstance(public_key, InfuzuPublicKey):
        public_key_b64: str = public_key.to_base64()
    elif isinstance(public_key, InfuzuKeys):
        public_key_b64: str = public_key.public_key.to_base64()
    elif isinstance(public_key, str):
        public_key_b64: str = public_key
    else:
        raise TypeError("public_key must be of type AuthenticationKey, InfuzuPublicKey, InfuzuKeys, or str")
    if not public_key_b64:
        return False
    return verify_message_signature(message, message_signature, public_key_b64)


def convert_message_signature_to_application_and_verify(message_signature: str, message: str) -> Application | None:
    pair_id: str = get_key_pair_id_from_signature(message_signature)
    if not pair_id:
        return None
    authentication_key: AuthenticationKey = get_application_information(pair_id)
    if not authentication_key.public_key_b64:
        return None
    sig_is_valid: bool = verify_diverse_message_signature(message, message_signature, authentication_key)
    if not sig_is_valid:
        return None
    return authentication_key.application


def application_is_valid(application: any) -> bool:
    if not isinstance(application, Application):
        return False
    return True


def application_is_internal(application: any) -> bool:
    if not application_is_valid(application):
        return False
    if not application.is_internal:
        return False
    return True


def application_is_in_list(application: any, app_ids: list[str]) -> bool:
    if not application_is_valid(application):
        return False
    if application.id not in app_ids:
        return False
    return True
