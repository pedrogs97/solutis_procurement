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
    solicitacao_contratacao_area_solicitante = create_raci_field("-", AREA_SOLICITANTE)
    solicitacao_contratacao_administrativo = create_raci_field("-", ADMINISTRATIVO)
    solicitacao_contratacao_juridico = create_raci_field("-", JURIDICO)
    solicitacao_contratacao_financeiro = create_raci_field("-", FINANCEIRO)
    solicitacao_contratacao_integridade = create_raci_field("-", INTEGRIDADE)
    solicitacao_contratacao_diretoria = create_raci_field("-", DIRETORIA)

    # Atividade: Análise de documentos cadastrais do fornecedor
    analise_documentos_area_solicitante = create_raci_field("I", AREA_SOLICITANTE)
    analise_documentos_administrativo = create_raci_field("A/R", ADMINISTRATIVO)
    analise_documentos_juridico = create_raci_field("-", JURIDICO)
    analise_documentos_financeiro = create_raci_field("-", FINANCEIRO)
    analise_documentos_integridade = create_raci_field("C", INTEGRIDADE)
    analise_documentos_diretoria = create_raci_field("-", DIRETORIA)

    # Atividade: Consulta de risco e verificação de integridade do fornecedor (due diligence)
    consulta_risco_area_solicitante = create_raci_field("I", AREA_SOLICITANTE)
    consulta_risco_administrativo = create_raci_field("R", ADMINISTRATIVO)
    consulta_risco_juridico = create_raci_field("-", JURIDICO)
    consulta_risco_financeiro = create_raci_field("-", FINANCEIRO)
    consulta_risco_integridade = create_raci_field("A", INTEGRIDADE)
    consulta_risco_diretoria = create_raci_field("C", DIRETORIA)

    # Atividade: Avaliação e classificação de risco do fornecedor
    avaliacao_classificacao_area_solicitante = create_raci_field("C", AREA_SOLICITANTE)
    avaliacao_classificacao_administrativo = create_raci_field("A/R", ADMINISTRATIVO)
    avaliacao_classificacao_juridico = create_raci_field("-", JURIDICO)
    avaliacao_classificacao_financeiro = create_raci_field("-", FINANCEIRO)
    avaliacao_classificacao_integridade = create_raci_field("C", INTEGRIDADE)
    avaliacao_classificacao_diretoria = create_raci_field("I", DIRETORIA)

    # Atividade: Criação e/ou atualização do cadastro no sistema (Agile, etc.)
    criacao_atualizacao_area_solicitante = create_raci_field("I", AREA_SOLICITANTE)
    criacao_atualizacao_administrativo = create_raci_field("A/R", ADMINISTRATIVO)
    criacao_atualizacao_juridico = create_raci_field("-", JURIDICO)
    criacao_atualizacao_financeiro = create_raci_field("-", FINANCEIRO)
    criacao_atualizacao_integridade = create_raci_field("-", INTEGRIDADE)
    criacao_atualizacao_diretoria = create_raci_field("I", DIRETORIA)

    # Atividade: Envio e recebimento da ficha cadastral / declarações
    envio_recebimento_area_solicitante = create_raci_field("I", AREA_SOLICITANTE)
    envio_recebimento_administrativo = create_raci_field("A/R", ADMINISTRATIVO)
    envio_recebimento_juridico = create_raci_field("-", JURIDICO)
    envio_recebimento_financeiro = create_raci_field("-", FINANCEIRO)
    envio_recebimento_integridade = create_raci_field("-", INTEGRIDADE)
    envio_recebimento_diretoria = create_raci_field("-", DIRETORIA)

    # Atividade: Elaboração de minuta contratual
    elaboracao_minuta_area_solicitante = create_raci_field("C", AREA_SOLICITANTE)
    elaboracao_minuta_administrativo = create_raci_field("A/R", ADMINISTRATIVO)
    elaboracao_minuta_juridico = create_raci_field("-", JURIDICO)
    elaboracao_minuta_financeiro = create_raci_field("C", FINANCEIRO)
    elaboracao_minuta_integridade = create_raci_field("C", INTEGRIDADE)
    elaboracao_minuta_diretoria = create_raci_field("-", DIRETORIA)

    # Atividade: Validação de cláusulas de compliance, LGPD, trabalho análogo, etc.
    validacao_clausulas_area_solicitante = create_raci_field("C", AREA_SOLICITANTE)
    validacao_clausulas_administrativo = create_raci_field("R", ADMINISTRATIVO)
    validacao_clausulas_juridico = create_raci_field("-", JURIDICO)
    validacao_clausulas_financeiro = create_raci_field("A", FINANCEIRO)
    validacao_clausulas_integridade = create_raci_field("A", INTEGRIDADE)
    validacao_clausulas_diretoria = create_raci_field("-", DIRETORIA)

    # Atividade: Aprovação final para contratação
    aprovacao_final_area_solicitante = create_raci_field("C", AREA_SOLICITANTE)
    aprovacao_final_administrativo = create_raci_field("C", ADMINISTRATIVO)
    aprovacao_final_juridico = create_raci_field("C", JURIDICO)
    aprovacao_final_financeiro = create_raci_field("C", FINANCEIRO)
    aprovacao_final_integridade = create_raci_field("C", INTEGRIDADE)
    aprovacao_final_diretoria = create_raci_field("A/R", DIRETORIA)

    # Atividade: Envio de contrato para assinatura
    envio_contrato_area_solicitante = create_raci_field("I", AREA_SOLICITANTE)
    envio_contrato_administrativo = create_raci_field("A/R", ADMINISTRATIVO)
    envio_contrato_juridico = create_raci_field("-", JURIDICO)
    envio_contrato_financeiro = create_raci_field("-", FINANCEIRO)
    envio_contrato_integridade = create_raci_field("-", INTEGRIDADE)
    envio_contrato_diretoria = create_raci_field("-", DIRETORIA)

    # Atividade: Armazenamento e gestão documental do contrato
    armazenamento_gestao_area_solicitante = create_raci_field("I", AREA_SOLICITANTE)
    armazenamento_gestao_administrativo = create_raci_field("A", ADMINISTRATIVO)
    armazenamento_gestao_juridico = create_raci_field("C", JURIDICO)
    armazenamento_gestao_financeiro = create_raci_field("-", FINANCEIRO)
    armazenamento_gestao_integridade = create_raci_field("-", INTEGRIDADE)
    armazenamento_gestao_diretoria = create_raci_field("-", DIRETORIA)

    # Atividade: Liberação para pagamentos / faturamento
    liberacao_pagamentos_area_solicitante = create_raci_field("I", AREA_SOLICITANTE)
    liberacao_pagamentos_administrativo = create_raci_field("R", ADMINISTRATIVO)
    liberacao_pagamentos_juridico = create_raci_field("-", JURIDICO)
    liberacao_pagamentos_financeiro = create_raci_field("A/R", FINANCEIRO)
    liberacao_pagamentos_integridade = create_raci_field("-", INTEGRIDADE)
    liberacao_pagamentos_diretoria = create_raci_field("-", DIRETORIA)

    def __str__(self):
        return f"Matriz de Responsabilidade - {self.supplier.trade_name}"

    class Meta(TimestampedModel.Meta):
        db_table = "responsibility_matrix"
        verbose_name = "Matriz de Responsabilidade"
        verbose_name_plural = "Matrizes de Responsabilidade"
        abstract = False
