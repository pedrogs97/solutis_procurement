"""
Responsibility matrix for supplier management in procurement service.
This module defines the responsibility matrix model used to manage supplier-related activities and their respective responsibilities.
"""

from django.db import models

from src.shared.models import TimestampedModel

# Choices reutilizáveis para todos os campos da matriz RACI (definidas fora da classe)
RACI_CHOICES = [
    ("A", "A - Accountable (Responsável)"),
    ("R", "R - Responsible (Executa)"),
    ("C", "C - Consulted (Consultado)"),
    ("I", "I - Informed (Informado)"),
    ("-", "- Não Envolvido"),
    ("A/R", "A/R - Responsável e Executa"),
]

# Labels das áreas/responsáveis (definidas fora da classe)
AREA_SOLICITANTE = "Área Solicitante"
ADMINISTRATIVO = "Administrativo / Cadastro"
JURIDICO = "Jurídico"
FINANCEIRO = "Financeiro"
INTEGRIDADE = "Integridade / Compliance"
DIRETORIA = "Diretoria / Gestão"


def create_raci_field(default_value, help_text):
    """Helper function para criar campos RACI padronizados"""
    return models.CharField(
        max_length=3,
        choices=RACI_CHOICES,
        default=default_value,
        help_text=help_text,
    )


class ResponsibilityMatrix(TimestampedModel):
    """
    Matriz de Responsabilidade - Cadastro e Contratação de Fornecedores

    Legenda:
    A = Responsável pela atividade (Accountable). Só pode haver um "A" por atividade.
    R = Realiza/executa a atividade (Responsible). Pode haver mais de um "R" envolvido na atividade.
    C = Consulta para tomada de decisão (Consulted). Normalmente, especialistas ou áreas que contribuem com informações.
    I = Informado sobre o andamento ou resultado (Informed)
    """

    # Relacionamento one-to-one com Supplier
    supplier = models.OneToOneField(
        "Supplier",
        on_delete=models.CASCADE,
        related_name="responsibility_matrix",
        help_text="Fornecedor vinculado à matriz",
    )

    # Atividade: Solicitação e justificativa de contratação
    contract_request_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    contract_request_administrative = create_raci_field("-", ADMINISTRATIVO)
    contract_request_legal = create_raci_field("-", JURIDICO)
    contract_request_financial = create_raci_field("-", FINANCEIRO)
    contract_request_integrity = create_raci_field("-", INTEGRIDADE)
    contract_request_board = create_raci_field("-", DIRETORIA)

    # Atividade: Análise de documentos cadastrais do fornecedor
    document_analysis_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    document_analysis_administrative = create_raci_field("-", ADMINISTRATIVO)
    document_analysis_legal = create_raci_field("-", JURIDICO)
    document_analysis_financial = create_raci_field("-", FINANCEIRO)
    document_analysis_integrity = create_raci_field("-", INTEGRIDADE)
    document_analysis_board = create_raci_field("-", DIRETORIA)

    # Atividade: Consulta de risco e verificação de integridade do fornecedor (due diligence)
    risk_consultation_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    risk_consultation_administrative = create_raci_field("-", ADMINISTRATIVO)
    risk_consultation_legal = create_raci_field("-", JURIDICO)
    risk_consultation_financial = create_raci_field("-", FINANCEIRO)
    risk_consultation_integrity = create_raci_field("-", INTEGRIDADE)
    risk_consultation_board = create_raci_field("-", DIRETORIA)

    # Atividade: Avaliação e classificação de risco do fornecedor
    risk_assessment_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    risk_assessment_administrative = create_raci_field("-", ADMINISTRATIVO)
    risk_assessment_legal = create_raci_field("-", JURIDICO)
    risk_assessment_financial = create_raci_field("-", FINANCEIRO)
    risk_assessment_integrity = create_raci_field("-", INTEGRIDADE)
    risk_assessment_board = create_raci_field("-", DIRETORIA)

    # Atividade: Criação e/ou atualização do cadastro no sistema (Agile, etc.)
    system_registration_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    system_registration_administrative = create_raci_field("-", ADMINISTRATIVO)
    system_registration_legal = create_raci_field("-", JURIDICO)
    system_registration_financial = create_raci_field("-", FINANCEIRO)
    system_registration_integrity = create_raci_field("-", INTEGRIDADE)
    system_registration_board = create_raci_field("-", DIRETORIA)

    # Atividade: Envio e recebimento da ficha cadastral / declarações
    form_handling_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    form_handling_administrative = create_raci_field("-", ADMINISTRATIVO)
    form_handling_legal = create_raci_field("-", JURIDICO)
    form_handling_financial = create_raci_field("-", FINANCEIRO)
    form_handling_integrity = create_raci_field("-", INTEGRIDADE)
    form_handling_board = create_raci_field("-", DIRETORIA)

    # Atividade: Elaboração de minuta contratual
    contract_draft_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    contract_draft_administrative = create_raci_field("-", ADMINISTRATIVO)
    contract_draft_legal = create_raci_field("-", JURIDICO)
    contract_draft_financial = create_raci_field("-", FINANCEIRO)
    contract_draft_integrity = create_raci_field("-", INTEGRIDADE)
    contract_draft_board = create_raci_field("-", DIRETORIA)

    # Atividade: Validação de cláusulas de compliance, LGPD, trabalho análogo, etc.
    compliance_validation_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    compliance_validation_administrative = create_raci_field("-", ADMINISTRATIVO)
    compliance_validation_legal = create_raci_field("-", JURIDICO)
    compliance_validation_financial = create_raci_field("-", FINANCEIRO)
    compliance_validation_integrity = create_raci_field("-", INTEGRIDADE)
    compliance_validation_board = create_raci_field("-", DIRETORIA)

    # Atividade: Aprovação final para contratação
    final_approval_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    final_approval_administrative = create_raci_field("-", ADMINISTRATIVO)
    final_approval_legal = create_raci_field("-", JURIDICO)
    final_approval_financial = create_raci_field("-", FINANCEIRO)
    final_approval_integrity = create_raci_field("-", INTEGRIDADE)
    final_approval_board = create_raci_field("-", DIRETORIA)

    # Atividade: Envio de contrato para assinatura
    contract_signing_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    contract_signing_administrative = create_raci_field("-", ADMINISTRATIVO)
    contract_signing_legal = create_raci_field("-", JURIDICO)
    contract_signing_financial = create_raci_field("-", FINANCEIRO)
    contract_signing_integrity = create_raci_field("-", INTEGRIDADE)
    contract_signing_board = create_raci_field("-", DIRETORIA)

    # Atividade: Armazenamento e gestão documental do contrato
    document_management_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    document_management_administrative = create_raci_field("-", ADMINISTRATIVO)
    document_management_legal = create_raci_field("-", JURIDICO)
    document_management_financial = create_raci_field("-", FINANCEIRO)
    document_management_integrity = create_raci_field("-", INTEGRIDADE)
    document_management_board = create_raci_field("-", DIRETORIA)

    # Atividade: Liberação para pagamentos / faturamento
    payment_release_requesting_area = create_raci_field("-", AREA_SOLICITANTE)
    payment_release_administrative = create_raci_field("-", ADMINISTRATIVO)
    payment_release_legal = create_raci_field("-", JURIDICO)
    payment_release_financial = create_raci_field("-", FINANCEIRO)
    payment_release_integrity = create_raci_field("-", INTEGRIDADE)
    payment_release_board = create_raci_field("-", DIRETORIA)

    # Atividade: Acompanhamento da execução do contrato.
    contract_execution_monitoring_requesting_area = create_raci_field(
        "-", AREA_SOLICITANTE
    )
    contract_execution_monitoring_administrative = create_raci_field(
        "-", ADMINISTRATIVO
    )
    contract_execution_monitoring_legal = create_raci_field("-", JURIDICO)
    contract_execution_monitoring_financial = create_raci_field("-", FINANCEIRO)
    contract_execution_monitoring_integrity = create_raci_field("-", INTEGRIDADE)
    contract_execution_monitoring_board = create_raci_field("-", DIRETORIA)

    def __str__(self):
        return f"Matriz de Responsabilidade - {self.supplier.trade_name}"

    class Meta(TimestampedModel.Meta):
        """
        Meta options for the ResponsibilityMatrix model.
        """

        db_table = "responsibility_matrix"
        verbose_name = "Matriz de Responsabilidade"
        verbose_name_plural = "Matrizes de Responsabilidade"
        abstract = False
