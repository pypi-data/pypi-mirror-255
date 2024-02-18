from typing import Callable
from ...authentication import SIGNATURE_HEADER_NAME
from ...authentication.authenticate import (
    application_is_valid, application_is_internal, application_is_in_list, verify_diverse_message_signature
)
from ...authentication.base import (InfuzuPublicKey, InfuzuKeys)
from ...authentication.requests import (Application, AuthenticationKey)


def ensure_there_is_valid_application(func: Callable) -> Callable:
    def wrapper(request, *args, **kwargs) -> any:
        application: Application | None = getattr(request, 'application', None)
        if not application_is_valid(application):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Access Denied - Signature is invalid")
        return func(request, *args, **kwargs)
    return wrapper


def ensure_application_is_internal(func: Callable) -> Callable:
    def wrapper(request, *args, **kwargs) -> any:
        application: Application | None = getattr(request, 'application', None)
        if not application_is_internal(application):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Access Denied - Signature is invalid")
        return func(request, *args, **kwargs)
    return wrapper


def ensure_valid_application_ids(allowed_app_ids: list[str]) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(request, *args, **kwargs) -> any:
            application: Application | None = getattr(request, 'application', None)
            if not application_is_in_list(application, allowed_app_ids):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("Access Denied - Application ID is not allowed")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def ensure_message_is_valid_from_public_key(
        public_key: AuthenticationKey | InfuzuPublicKey | InfuzuKeys | str
) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(request, *args, **kwargs) -> any:
            signature: str = request.headers.get(SIGNATURE_HEADER_NAME, '')
            if not signature or not verify_diverse_message_signature(
                    message=request.body.decode('utf-8'), message_signature=signature, public_key=public_key
            ):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("Access Denied - Message is not properly signed")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def ensure_message_is_valid_from_public_keys(
        public_keys: list[AuthenticationKey | InfuzuPublicKey | InfuzuKeys | str]
) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(request, *args, **kwargs) -> any:
            signature: str = request.headers.get(SIGNATURE_HEADER_NAME, '')
            if signature:
                for public_key in public_keys:
                    if verify_diverse_message_signature(
                        message=request.body.decode('utf-8'), message_signature=signature, public_key=public_key
                    ):
                        return func(request, *args, **kwargs)
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Access Denied - Message is not properly signed")
        return wrapper
    return decorator
