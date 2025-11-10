"""
Comando Django para carregar todas as fixtures.
"""

import os

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    """
    Comando para carregar todas as fixtures necessárias.
    """

    help = "Carrega todas as fixtures necessárias para a aplicação"

    def handle(self, *args, **options):
        """
        Executa o comando para carregar as fixtures.
        """
        self.stdout.write(self.style.SUCCESS("Carregando todas as fixtures..."))

        try:
            for fixture in os.listdir("src/supplier/fixtures"):
                if fixture.endswith(".json"):
                    self.stdout.write(f"Carregando fixture: {fixture}")
                    try:
                        call_command("loaddata", f"src/supplier/fixtures/{fixture}")
                    except IntegrityError:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Fixture {fixture} já carregada. Pulando..."
                            )
                        )
            for fixture in os.listdir("src/supplier/fixtures/evaluation"):
                if fixture.endswith(".json"):
                    self.stdout.write(f"Carregando fixture: {fixture}")
                    try:
                        call_command(
                            "loaddata", f"src/supplier/fixtures/evaluation/{fixture}"
                        )
                    except IntegrityError:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Fixture {fixture} já carregada. Pulando..."
                            )
                        )

            self.stdout.write(
                self.style.SUCCESS("Todas as fixtures foram carregadas com sucesso!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao carregar fixtures: {e}"))
            raise e
