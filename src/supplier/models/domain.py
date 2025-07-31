"""
Domain models for the supplier management in procurement service.
This module contains domain models used specifically for supplier-related functionalities.
"""

from src.shared.models import DomType


class DomClassification(DomType):
    """
    Model representing a classification for suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomClassification model.
        """

        db_table = "classification"
        verbose_name = "Classificação"
        verbose_name_plural = "Classificações"
        abstract = False


class DomCategory(DomType):
    """
    Model representing a category for suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomCategory model.
        """

        db_table = "category"
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        abstract = False


class DomRiskLevel(DomType):
    """
    Model representing the risk level associated with suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomRiskLevel model.
        """

        db_table = "risk_level"
        verbose_name = "Grau de Risco"
        verbose_name_plural = "Grau de Risco"
        abstract = False


class DomTypeSupplier(DomType):
    """
    Model representing the type of supplier.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomTypeSupplier model.
        """

        db_table = "type_supplier"
        verbose_name = "Tipo de Fornecedor"
        verbose_name_plural = "Tipos de Fornecedor"
        abstract = False


class DomSupplierSituation(DomType):
    """
    Model representing the situation status of suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomSupplierSituation model.
        """

        db_table = "supplier_situation"
        verbose_name = "Situação do Fornecedor"
        verbose_name_plural = "Situações do Fornecedor"
        abstract = False


class DomPixType(DomType):
    """
    Model representing types of PIX payment keys.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomPixType model.
        """

        db_table = "pix_type"
        verbose_name = "Tipo de Pix"
        verbose_name_plural = "Tipos de Pix"
        abstract = False


class DomPaymentMethod(DomType):
    """
    Model representing payment methods available for suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomPaymentMethod model.
        """

        db_table = "payment_method"
        verbose_name = "Método de Pagamento"
        verbose_name_plural = "Métodos de Pagamento"
        abstract = False


class DomPayerType(DomType):
    """
    Model representing types of payers in financial transactions.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomPayerType model.
        """

        db_table = "payer_type"
        verbose_name = "Tipo de Pagador"
        verbose_name_plural = "Tipos de Pagador"
        abstract = False


class DomBusinessSector(DomType):
    """
    Model representing business sectors for supplier classification.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomBusinessSector model.
        """

        db_table = "business_sector"
        verbose_name = "Ramo de Atividade"
        verbose_name_plural = "Ramos de Atividade"
        abstract = False


class DomTaxpayerClassification(DomType):
    """
    Model representing taxpayer classifications for suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomTaxpayerClassification model.
        """

        db_table = "taxpayer_classification"
        verbose_name = "Classificação de Contribuinte"
        verbose_name_plural = "Classificações de Contribuintes"
        abstract = False


class DomPublicEntity(DomType):
    """
    Model representing public entity classifications for suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomPublicEntity model.
        """

        db_table = "public_entity"
        verbose_name = "Entidade Pública"
        verbose_name_plural = "Entidades Públicas"
        abstract = False


class DomIssWithholding(DomType):
    """
    Model representing ISS (Service Tax) withholding options.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomIssWithholding model.
        """

        db_table = "iss_withholding"
        verbose_name = "ISS Retenção"
        verbose_name_plural = "ISS Retenções"
        abstract = False


class DomIssRegime(DomType):
    """
    Model representing ISS (Service Tax) regime types.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomIssRegime model.
        """

        db_table = "iss_regime"
        verbose_name = "Regime ISS"
        verbose_name_plural = "Regimes ISS"
        abstract = False


class DomWithholdingTax(DomType):
    """
    Model representing withholding tax types for suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomWithholdingTax model.
        """

        db_table = "withholding_tax"
        verbose_name = "Imposto Retido"
        verbose_name_plural = "Impostos Retidos"
        abstract = False


class DomCompanySize(DomType):
    """
    Model representing company size classifications for suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomCompanySize model.
        """

        db_table = "company_size"
        verbose_name = "Tamanho da Empresa"
        verbose_name_plural = "Tamanhos de Empresa"
        abstract = False


class DomIcmsTaxpayer(DomType):
    """
    Model representing ICMS taxpayer classifications for suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomIcmsTaxpayer model.
        """

        db_table = "icms_taxpayer"
        verbose_name = "Contribuinte ICMS"
        verbose_name_plural = "Contribuintes ICMS"
        abstract = False


class DomIncomeType(DomType):
    """
    Model representing income types for supplier classification.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomIncomeType model.
        """

        db_table = "income_type"
        verbose_name = "Tipo de Rendimento"
        verbose_name_plural = "Tipos de Rendimento"
        abstract = False


class DomTaxationMethod(DomType):
    """
    Model representing taxation methods for suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomTaxationMethod model.
        """

        db_table = "taxation_method"
        verbose_name = "Método de Tributação"
        verbose_name_plural = "Métodos de Tributação"
        abstract = False


class DomCustomerType(DomType):
    """
    Model representing customer types for supplier relationships.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomCustomerType model.
        """

        db_table = "customer_type"
        verbose_name = "Tipo de Cliente"
        verbose_name_plural = "Tipos de Cliente"
        abstract = False


class DomTaxationRegime(DomType):
    """
    Model representing taxation regimes for suppliers.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomTaxationRegime model.
        """

        db_table = "taxation_regime"
        verbose_name = "Regime de Tributação"
        verbose_name_plural = "Regimes de Tributação"
        abstract = False


class DomAttachmentType(DomType):
    """
    Model representing attachment types for supplier documents.
    """

    class Meta(DomType.Meta):
        """
        Meta options for the DomAttachmentType model.
        """

        db_table = "attachment_type"
        verbose_name = "Tipo de Anexo"
        verbose_name_plural = "Tipos de Anexo"
        abstract = False
