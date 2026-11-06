"""Stable error envelope for DRF API exceptions."""

from rest_framework.views import exception_handler


def json_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    request = context.get("request")
    request_id = getattr(request, "request_id", None)
    details = response.data
    default_message = {
        400: "Invalid request",
        401: "Authentication required",
        403: "Permission denied",
        404: "Resource not found",
        405: "Method not allowed",
        429: "Rate limit exceeded",
    }.get(response.status_code, "Request failed")
    if isinstance(details, dict):
        raw_message = details.get("detail", default_message)
    else:
        raw_message = default_message

    response.data = {
        "error": {
            "code": getattr(exc, "default_code", "api_error"),
            "message": str(raw_message),
            "request_id": request_id,
            "details": details if isinstance(details, (dict, list)) else None,
        }
    }
    return response
