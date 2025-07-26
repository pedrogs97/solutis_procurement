"""Supplier management application configuration for the procurement service."""

from django.apps import AppConfig


class SupplierConfig(AppConfig):
    """Configuration class for the Supplier application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "src.supplier"
