from src.shared.models import DomType


class DomClassification(DomType):
    class Meta(DomType.Meta):
        db_table = "classification"
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"
        abstract = False


class DomCategory(DomType):
    class Meta(DomType.Meta):
        db_table = "category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        abstract = False


class DomRiskLevel(DomType):
    class Meta(DomType.Meta):
        db_table = "risk_level"
        verbose_name = "Risk Level"
        verbose_name_plural = "Risk Levels"
        abstract = False


class DomTypeSupplier(DomType):
    class Meta(DomType.Meta):
        db_table = "type_supplier"
        verbose_name = "Type Supplier"
        verbose_name_plural = "Type Suppliers"
        abstract = False


class DomSupplierSituation(DomType):
    class Meta(DomType.Meta):
        db_table = "supplier_situation"
        verbose_name = "Supplier Situation"
        verbose_name_plural = "Supplier Situations"
        abstract = False


class DomPixType(DomType):
    class Meta(DomType.Meta):
        db_table = "pix_type"
        verbose_name = "Pix Type"
        verbose_name_plural = "Pix Types"
        abstract = False


class DomPaymentMethod(DomType):
    class Meta(DomType.Meta):
        db_table = "payment_method"
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
        abstract = False


class DomPayerType(DomType):
    class Meta(DomType.Meta):
        db_table = "payer_type"
        verbose_name = "Payer Type"
        verbose_name_plural = "Payer Types"
        abstract = False


class DomBusinessSector(DomType):
    class Meta(DomType.Meta):
        db_table = "business_sector"
        verbose_name = "Business Sector"
        verbose_name_plural = "Business Sectors"
        abstract = False


class DomTaxpayerClassification(DomType):
    class Meta(DomType.Meta):
        db_table = "taxpayer_classification"
        verbose_name = "Taxpayer Classification"
        verbose_name_plural = "Taxpayer Classifications"
        abstract = False


class DomPublicEntity(DomType):
    class Meta(DomType.Meta):
        db_table = "public_entity"
        verbose_name = "Public Entity"
        verbose_name_plural = "Public Entities"
        abstract = False


class DomIssWithholding(DomType):
    class Meta(DomType.Meta):
        db_table = "iss_withholding"
        verbose_name = "ISS Withholding"
        verbose_name_plural = "ISS Withholdings"
        abstract = False


class DomIssRegime(DomType):
    class Meta(DomType.Meta):
        db_table = "iss_regime"
        verbose_name = "ISS Regime"
        verbose_name_plural = "ISS Regimes"
        abstract = False


class DomWithholdingTax(DomType):
    class Meta(DomType.Meta):
        db_table = "withholding_tax"
        verbose_name = "Withholding Tax"
        verbose_name_plural = "Withholding Taxes"
        abstract = False


class DomCompanySize(DomType):
    class Meta(DomType.Meta):
        db_table = "company_size"
        verbose_name = "Company Size"
        verbose_name_plural = "Company Sizes"
        abstract = False


class DomIcmsTaxpayer(DomType):
    class Meta(DomType.Meta):
        db_table = "icms_taxpayer"
        verbose_name = "ICMS Taxpayer"
        verbose_name_plural = "ICMS Taxpayers"
        abstract = False


class DomIncomeType(DomType):
    class Meta(DomType.Meta):
        db_table = "income_type"
        verbose_name = "Income Type"
        verbose_name_plural = "Income Types"
        abstract = False


class DomTaxationMethod(DomType):
    class Meta(DomType.Meta):
        db_table = "taxation_method"
        verbose_name = "Taxation Method"
        verbose_name_plural = "Taxation Methods"
        abstract = False


class DomCustomerType(DomType):
    class Meta(DomType.Meta):
        db_table = "customer_type"
        verbose_name = "Customer Type"
        verbose_name_plural = "Customer Types"
        abstract = False


class DomTaxationRegime(DomType):
    class Meta(DomType.Meta):
        db_table = "taxation_regime"
        verbose_name = "Taxation Regime"
        verbose_name_plural = "Taxation Regimes"
        abstract = False


class DomAttachmentType(DomType):
    class Meta(DomType.Meta):
        db_table = "attachment_type"
        verbose_name = "Attachment Type"
        verbose_name_plural = "Attachment Types"
        abstract = False
