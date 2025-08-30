# pylint: disable=import-outside-toplevel
"""Supplier management application configuration for the procurement service."""

from django.apps import AppConfig


class SupplierConfig(AppConfig):
    """Configuration class for the Supplier application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "src.supplier"

    def ready(self):
        """
        Ready method to perform initialization tasks.
        Import signals to ensure they're registered.
        """
        import src.supplier.signals  # noqa  # pylint: disable=unused-import
        import src.supplier.signals.evaluation  # noqa  # pylint: disable=unused-import
        import src.supplier.signals.supplier  # noqa  # pylint: disable=unused-import
