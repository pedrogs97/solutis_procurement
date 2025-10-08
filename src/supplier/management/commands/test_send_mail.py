"""
Comando Django para carregar o fluxo de aprovação baseado na estrutura da empresa.
"""

from django.core.management.base import BaseCommand

from src.shared.backends import Email365Client


class Command(BaseCommand):
    """
    Comando para carregar as fixtures do fluxo de aprovação.
    """

    help = "Carrega as fixtures do fluxo de aprovação padrão da empresa"

    def handle(self, *args, **options):
        """
        Executa o comando para carregar as fixtures.
        """
        self.stdout.write(self.style.SUCCESS("Testando envio de e-mail..."))

        try:
            email_client = Email365Client(
                mail_to="pedrogustavosantana97@gmail.com",
                mail_subject="Teste de E-mail",
                type_message="approval",
                extra={
                    "supplier": "Testando Fornecedor",
                    "approver_name": "Testando Aprovador",
                    "step": "Testando Etapa",
                    "approval_link": "http://localhost:3000/supplier/approval?token=accept_token",
                    "reprove_link": "http://localhost:3000/supplier/approval?token=reject_token",
                },
            )
            email_client.send_message()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao enviar o e-mail: {e}"))
            raise e
