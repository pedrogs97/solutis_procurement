"""Exception handlers for Ninja v1 API."""

from django.http import Http404
from ninja import NinjaAPI
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError


def register_exception_handlers(api: NinjaAPI) -> None:
    """Register API-wide exception handlers."""

    @api.exception_handler(DRFValidationError)
    def handle_drf_validation_error(request, exc):
        return api.create_response(request, exc.detail, status=400)

    @api.exception_handler(APIException)
    def handle_drf_api_exception(request, exc):
        detail = exc.detail
        status_code = getattr(exc, "status_code", 400)
        return api.create_response(request, detail, status=status_code)

    @api.exception_handler(Http404)
    def handle_http_404(request, exc):
        return api.create_response(request, {"detail": "Not Found"}, status=404)

    @api.exception_handler(ValueError)
    def handle_value_error(request, exc):
        return api.create_response(request, {"detail": str(exc)}, status=400)
