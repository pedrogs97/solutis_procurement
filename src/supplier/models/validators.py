"""Validation utilities for supplier models."""

from django.db.models import Model
from django.db.models.fields import NOT_PROVIDED
from django.db.models.fields.related import ForeignKey, OneToOneField


def validate_object_complete(obj: Model) -> bool:
    """
    Valida se todos os campos do objeto estão preenchidos diferente do default. Para FKs, valida recursivamente.

    Args:
        obj (Model): Instância do modelo a ser validada.

    Returns:
        bool: True se o objeto estiver completo, False caso contrário.
    """

    for field in obj._meta.fields:
        value = getattr(obj, field.name)
        # Ignora campos auto (como id, auto_now_add, etc)
        if (
            getattr(field, "auto_created", False)
            or getattr(field, "auto_now", False)
            or getattr(field, "auto_now_add", False)
        ):
            continue
        # Se for FK ou OneToOne, valida recursivamente
        if isinstance(field, (ForeignKey, OneToOneField)):
            if value is None:
                return False
            if not validate_object_complete(value):
                return False
        else:
            default = field.default if field.default is not NOT_PROVIDED else None
            # Para campos string, só considera incompleto se for igual ao default
            if (
                hasattr(field, "get_internal_type")
                and field.get_internal_type() == "CharField"
            ):
                if value == default:
                    return False
            else:
                if value == default or value is None:
                    return False
    return True
