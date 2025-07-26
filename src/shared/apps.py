"""Procurement app configuration for Django."""

from django.apps import AppConfig


class SharedConfig(AppConfig):
    """Configuration for the shared app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "src.shared"
