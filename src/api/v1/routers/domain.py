"""Domain endpoints for Ninja API v1."""

from ninja import Router

from src.api.v1.schemas.common import DomainRefOut
from src.api.v1.schemas.domain import DomainItemOut, SupplierSituationOut
from src.supplier.models.domain import (
    DomBusinessSector,
    DomCategory,
    DomClassification,
    DomCompanySize,
    DomCustomerType,
    DomIcmsTaxpayer,
    DomIncomeType,
    DomIssRegime,
    DomIssWithholding,
    DomPayerType,
    DomPaymentMethod,
    DomPixType,
    DomPublicEntity,
    DomRiskLevel,
    DomSupplierSituation,
    DomTaxationMethod,
    DomTaxationRegime,
    DomTaxpayerClassification,
    DomTypeSupplier,
    DomWithholdingTax,
)

router = Router(tags=["domain"])


def _serialize_domain_items(queryset):
    return [
        DomainItemOut(id=item.id, name=item.name).model_dump(by_alias=True)
        for item in queryset
    ]


@router.get("/classifications/", url_name="domain-classifications-v1")
def list_classifications(request):
    """List domain classifications."""
    return _serialize_domain_items(DomClassification.objects.all().order_by("name"))


@router.get("/categories/", url_name="domain-categories-v1")
def list_categories(request):
    """List supplier categories."""
    return _serialize_domain_items(DomCategory.objects.all().order_by("name"))


@router.get("/risk-levels/", url_name="domain-risk-levels-v1")
def list_risk_levels(request):
    """List supplier risk levels."""
    return _serialize_domain_items(DomRiskLevel.objects.all().order_by("name"))


@router.get("/supplier-types/", url_name="domain-supplier-types-v1")
def list_supplier_types(request):
    """List supplier types."""
    return _serialize_domain_items(DomTypeSupplier.objects.all().order_by("name"))


@router.get("/supplier-situations/", url_name="domain-supplier-situations-v1")
def list_supplier_situations(request):
    """List supplier situations."""
    queryset = (
        DomSupplierSituation.objects.select_related("pendency_type")
        .all()
        .order_by("name")
    )
    return [
        SupplierSituationOut(
            id=item.id,
            name=item.name,
            pendency_type=DomainRefOut.model_validate(item.pendency_type)
            if item.pendency_type
            else None,
        ).model_dump(by_alias=True)
        for item in queryset
    ]


@router.get("/pix-types/", url_name="domain-pix-types-v1")
def list_pix_types(request):
    """List PIX key types."""
    return _serialize_domain_items(DomPixType.objects.all().order_by("name"))


@router.get("/payment-methods/", url_name="domain-payment-methods-v1")
def list_payment_methods(request):
    """List payment methods."""
    return _serialize_domain_items(DomPaymentMethod.objects.all().order_by("name"))


@router.get("/payer-types/", url_name="domain-payer-types-v1")
def list_payer_types(request):
    """List payer types."""
    return _serialize_domain_items(DomPayerType.objects.all().order_by("name"))


@router.get("/business-sectors/", url_name="domain-business-sectors-v1")
def list_business_sectors(request):
    """List business sectors."""
    return _serialize_domain_items(DomBusinessSector.objects.all().order_by("name"))


@router.get("/company-sizes/", url_name="domain-company-sizes-v1")
def list_company_sizes(request):
    """List company sizes."""
    return _serialize_domain_items(DomCompanySize.objects.all().order_by("name"))


@router.get("/customer-types/", url_name="domain-customer-types-v1")
def list_customer_types(request):
    """List customer types."""
    return _serialize_domain_items(DomCustomerType.objects.all().order_by("name"))


@router.get("/taxpayer-classifications/", url_name="domain-taxpayer-classifications-v1")
def list_taxpayer_classifications(request):
    """List taxpayer classifications."""
    return _serialize_domain_items(
        DomTaxpayerClassification.objects.all().order_by("name")
    )


@router.get("/taxation-regimes/", url_name="domain-taxation-regimes-v1")
def list_taxation_regimes(request):
    """List taxation regimes."""
    return _serialize_domain_items(DomTaxationRegime.objects.all().order_by("name"))


@router.get("/taxation-methods/", url_name="domain-taxation-methods-v1")
def list_taxation_methods(request):
    """List taxation methods."""
    return _serialize_domain_items(DomTaxationMethod.objects.all().order_by("name"))


@router.get("/icms-taxpayers/", url_name="domain-icms-taxpayers-v1")
def list_icms_taxpayers(request):
    """List ICMS taxpayer types."""
    return _serialize_domain_items(DomIcmsTaxpayer.objects.all().order_by("name"))


@router.get("/withholding-taxes/", url_name="domain-withholding-taxes-v1")
def list_withholding_taxes(request):
    """List withholding taxes."""
    return _serialize_domain_items(DomWithholdingTax.objects.all().order_by("name"))


@router.get("/iss-withholdings/", url_name="domain-iss-withholdings-v1")
def list_iss_withholdings(request):
    """List ISS withholding types."""
    return _serialize_domain_items(DomIssWithholding.objects.all().order_by("name"))


@router.get("/iss-regimes/", url_name="domain-iss-regimes-v1")
def list_iss_regimes(request):
    """List ISS regimes."""
    return _serialize_domain_items(DomIssRegime.objects.all().order_by("name"))


@router.get("/income-types/", url_name="domain-income-types-v1")
def list_income_types(request):
    """List income types."""
    return _serialize_domain_items(DomIncomeType.objects.all().order_by("name"))


@router.get("/public-entities/", url_name="domain-public-entities-v1")
def list_public_entities(request):
    """List public entities."""
    return _serialize_domain_items(DomPublicEntity.objects.all().order_by("name"))
