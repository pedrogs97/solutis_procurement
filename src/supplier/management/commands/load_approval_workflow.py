"""
Comando Django para carregar o fluxo de aprovação baseado na estrutura da empresa.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand

from src.supplier.models.approval_workflow import ApprovalStep


class Command(BaseCommand):
    """
    Comando para carregar as fixtures do fluxo de aprovação.
    """

    help = "Carrega as fixtures do fluxo de aprovação padrão da empresa"

    def handle(self, *args, **options):
        """
        Executa o comando para carregar as fixtures.
        """
        self.stdout.write(
            self.style.SUCCESS("Carregando passos do fluxo de aprovação...")
        )

        try:
            # Carregar fixture dos passos de aprovação
            call_command("loaddata", "src/supplier/fixtures/approval_steps.json")

            self.stdout.write(
                self.style.SUCCESS(
                    "Fluxo de aprovação carregado com sucesso! 8 passos criados:"
                )
            )

            steps = ApprovalStep.objects.all().order_by("order")
            for step in steps:
                self.stdout.write(f"  {step.order}. {step.name} ({step.department})")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Erro ao carregar fluxo de aprovação: {e}")
            )
            raise e
