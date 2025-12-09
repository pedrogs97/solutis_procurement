"""Configuração do aplicativo de sincronização."""

from django.apps import AppConfig


class SyncConfig(AppConfig):
    """Configuração do aplicativo de sincronização."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "src.sync"
