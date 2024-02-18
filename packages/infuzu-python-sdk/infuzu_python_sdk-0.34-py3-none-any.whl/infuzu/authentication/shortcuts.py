import base64
import json
import os
from .base import (InfuzuKeys, InfuzuPrivateKey, InfuzuPublicKey)


def generate_key_pair():
    return InfuzuKeys.generate()


def get_private_key_str(private_key_str: str = None) -> str:
    if private_key_str is not None:
        return private_key_str
    else:
        return os.environ.get("INFUZU_SECRET_KEY")


def get_private_key(private_key_str: str = None) -> InfuzuPrivateKey:
    return InfuzuPrivateKey.from_base64(get_private_key_str(private_key_str))


def get_public_key(public_key_str: str) -> InfuzuPublicKey:
    return InfuzuPublicKey.from_base64(public_key_str)


SIGNATURE_HEADER_NAME = "Infuzu-Signature"


def generate_message_signature(message: str, private_key: str = None) -> str:
    if not isinstance(message, str):
        raise TypeError("message must be a string")
    infuzu_keys: InfuzuKeys = InfuzuKeys(private_key=get_private_key(private_key))
    signature: str = infuzu_keys.private_key.sign_message(message)
    return signature


def verify_message_signature(message: str, signature: str, public_key: str) -> bool:
    if not isinstance(message, str):
        raise TypeError("message must be a string")
    if not isinstance(signature, str):
        raise TypeError("signature must be a string")
    public_key: InfuzuPublicKey = InfuzuPublicKey.from_base64(public_key)
    return public_key.verify_signature(message, signature)


def get_key_pair_id_from_signature(signature: str) -> str:
    try:
        signature_data: dict[str, any] = json.loads(base64.urlsafe_b64decode(signature))
        sig_id: str = signature_data["id"]
        return sig_id
    except (json.JSONDecodeError, KeyError):
        return ""
