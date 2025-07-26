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
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"
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
        verbose_name = "Category"
        verbose_name_plural = "Categories"
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
        verbose_name = "Risk Level"
        verbose_name_plural = "Risk Levels"
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
        verbose_name = "Type Supplier"
        verbose_name_plural = "Type Suppliers"
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
        verbose_name = "Supplier Situation"
        verbose_name_plural = "Supplier Situations"
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
        verbose_name = "Pix Type"
        verbose_name_plural = "Pix Types"
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
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
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
        verbose_name = "Payer Type"
        verbose_name_plural = "Payer Types"
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
        verbose_name = "Business Sector"
        verbose_name_plural = "Business Sectors"
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
        verbose_name = "Taxpayer Classification"
        verbose_name_plural = "Taxpayer Classifications"
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
        verbose_name = "Public Entity"
        verbose_name_plural = "Public Entities"
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
        verbose_name = "ISS Withholding"
        verbose_name_plural = "ISS Withholdings"
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
        verbose_name = "ISS Regime"
        verbose_name_plural = "ISS Regimes"
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
        verbose_name = "Withholding Tax"
        verbose_name_plural = "Withholding Taxes"
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
        verbose_name = "Company Size"
        verbose_name_plural = "Company Sizes"
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
        verbose_name = "ICMS Taxpayer"
        verbose_name_plural = "ICMS Taxpayers"
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
        verbose_name = "Income Type"
        verbose_name_plural = "Income Types"
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
        verbose_name = "Taxation Method"
        verbose_name_plural = "Taxation Methods"
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
        verbose_name = "Customer Type"
        verbose_name_plural = "Customer Types"
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
        verbose_name = "Taxation Regime"
        verbose_name_plural = "Taxation Regimes"
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
        verbose_name = "Attachment Type"
        verbose_name_plural = "Attachment Types"
        abstract = False
