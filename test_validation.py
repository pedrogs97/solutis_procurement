#!/usr/bin/env python
"""
Teste para validar se BaseValidationError está funcionando corretamente
"""
import os
import sys

import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from src.shared.validation import BaseValidationError


def test_base_validation_error():
    """Testa se BaseValidationError está funcionando"""
    try:
        raise BaseValidationError("test_field", "Mensagem de teste")
    except BaseValidationError as e:
        print("✅ BaseValidationError funcionando corretamente!")
        print(f"   Detalhes: {e.detail}")
        return True
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


if __name__ == "__main__":
    success = test_base_validation_error()
    sys.exit(0 if success else 1)
