"""Exception handlers for Ninja v1 API."""

from django.http import Http404
from loguru import logger
from ninja import NinjaAPI
from ninja.errors import ValidationError as NinjaValidationError
from pydantic import ValidationError as PydanticValidationError
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError

from src.utils.parse import to_camel_case


def _pydantic_errors_to_list(exc: PydanticValidationError) -> list:
    """Convert Pydantic v2 validation errors to a frontend-friendly list."""
    result = []
    for error in exc.errors(include_url=False):
        loc = error.get("loc", ())
        parts = []
        for part in loc:
            if isinstance(part, str):
                parts.append(to_camel_case(part))
            else:
                parts.append(str(part))
        field = ".".join(parts) if parts else None
        result.append({"field": field, "message": error["msg"]})
    return result


def _ninja_errors_to_list(errors: list) -> list:
    """Convert Ninja request-validation errors (loc/msg dicts) to {field, message} list."""
    result = []
    for error in errors:
        loc = error.get("loc", ())
        # loc is e.g. ("body", "legalName") or ("body", "address", "postalCode")
        # Skip the first element ("body") and convert remaining parts to camelCase
        parts = []
        for i, part in enumerate(loc):
            if i == 0:
                continue  # skip "body" prefix
            if isinstance(part, str):
                parts.append(to_camel_case(part))
            elif isinstance(part, int):
                parts.append(str(part))
        field = ".".join(parts) if parts else None
        result.append({"field": field, "message": error.get("msg", "")})
    return result


def register_exception_handlers(api: NinjaAPI) -> None:
    """Register API-wide exception handlers."""

    @api.exception_handler(NinjaValidationError)
    def handle_ninja_validation_error(request, exc):
        errors = _ninja_errors_to_list(exc.errors)
        logger.warning("Ninja request validation error on {}: {}", request.path, errors)
        return api.create_response(
            request,
            {"detail": "Dados inválidos.", "errors": errors},
            status=422,
        )

    @api.exception_handler(PydanticValidationError)
    def handle_pydantic_validation_error(request, exc):
        errors = _pydantic_errors_to_list(exc)
        logger.warning("Pydantic validation error on {}: {}", request.path, errors)
        return api.create_response(
            request,
            {"detail": "Dados inválidos.", "errors": errors},
            status=400,
        )

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
