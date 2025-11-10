"""
Comando Django para carregar fornecedores.
"""

from django.core.management.base import BaseCommand

from src.supplier.models.totvs import ExternalDatabase


class Command(BaseCommand):
    """
    Comando para carregar fornecedores.
    """

    help = "Carrega fornecedores padrão do sistema."

    def handle(self, *args, **options):
        """
        Executa o comando para carregar os fornecedores.
        """
        self.stdout.write(self.style.SUCCESS("Carregando fornecedores..."))

        try:
            external_db = ExternalDatabase()
            external_db.load_suppliers()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao carregar fornecedores: {e}"))
            raise e
