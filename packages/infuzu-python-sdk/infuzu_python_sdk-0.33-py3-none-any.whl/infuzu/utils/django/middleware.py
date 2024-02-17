from ...authentication import (SIGNATURE_HEADER_NAME)
from ...authentication.authenticate import convert_message_signature_to_application_and_verify
from ...authentication.requests import Application


class InfuzuVerifyAndIdentifyMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        signature: str = request.headers.get(SIGNATURE_HEADER_NAME, '')
        application: Application | None = convert_message_signature_to_application_and_verify(
            signature, request.body.decode('utf-8')
        )
        setattr(request, 'application', application)
        response = self.get_response(request)
        return response
