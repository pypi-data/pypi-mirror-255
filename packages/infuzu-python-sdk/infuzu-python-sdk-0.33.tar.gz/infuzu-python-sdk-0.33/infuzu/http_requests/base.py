import json
import requests
from ..authentication.shortcuts import (generate_message_signature, SIGNATURE_HEADER_NAME)
from ..utils.api_calls.serialize import class_str_serializer


class SignatureSession(requests.Session):
    def request(self, method, url, private_key: str = None, **kwargs):
        request_body: any = kwargs.get("data") or kwargs.get("json", '')

        if not isinstance(request_body, str):
            request_body: str = json.dumps(request_body, default=class_str_serializer)
            kwargs['data'] = request_body

        signature: str = generate_message_signature(request_body, private_key=private_key)

        kwargs['headers']: dict[str, any] = kwargs.get('headers')
        if not isinstance(kwargs['headers'], dict):
            kwargs['headers']: dict[str, any] = {}
        headers: dict[str, any] = kwargs['headers']
        headers[SIGNATURE_HEADER_NAME] = signature
        if request_body:
            headers['Content-Type'] = headers.get('Content-Type', 'application/json')

        return super().request(method, url, **kwargs)


signed_requests: SignatureSession = SignatureSession()
