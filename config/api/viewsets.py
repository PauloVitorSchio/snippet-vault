from __future__ import annotations

from typing import Any

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class ErrorResponseMixin:
    def error_response(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: Any | None = None,
    ) -> Response:
        return Response(
            {"error": {"code": code, "message": message, "details": details}},
            status=status_code,
        )


class BaseViewSet(ErrorResponseMixin, GenericViewSet):
    pass
