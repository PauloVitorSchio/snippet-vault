from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


def _normalize_message_and_details(data: Any) -> tuple[str, Any]:
    if isinstance(data, dict):
        if "detail" in data and isinstance(data["detail"], str):
            return data["detail"], {k: v for k, v in data.items() if k != "detail"} or None
        return "Validation error", data
    if isinstance(data, list):
        return "Validation error", data
    if isinstance(data, str):
        return data, None
    return "Request failed", data


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = exception_handler(exc, context)
    if response is None:
        return None

    default_code = "error"
    if isinstance(exc, APIException):
        default_code = getattr(exc, "default_code", default_code)

    message, details = _normalize_message_and_details(response.data)

    response.data = {
        "error": {
            "code": default_code,
            "message": message,
            "details": details,
        }
    }

    if response.status_code == status.HTTP_204_NO_CONTENT:
        response.status_code = status.HTTP_200_OK

    return response
