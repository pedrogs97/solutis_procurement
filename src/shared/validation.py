"""
Validation module for the shared app in Django.
This module contains custom validation error classes used across the application.
"""

from typing import Optional

from rest_framework.exceptions import ValidationError

from src.utils.parse import to_camel_case


class BaseValidationError(ValidationError):
    """
    Base class for validation errors in the application.
    This can be extended to create specific validation error types.
    """

    default_detail = "Campo inválido."
    default_code = "invalid"

    def __init__(self, field_name: str, message: Optional[str] = None, code=None):
        detail = {
            "field": to_camel_case(field_name),
            "message": message or self.default_detail,
            "code": code or self.default_code,
        }
        super().__init__(detail=detail, code=code)
