"""Supplier schemas and mappers for Ninja v1."""

from typing import Any, Optional

from pydantic import AliasChoices, Field

from src.api.v1.schemas.common import CamelSchema, DomainRefOut
from src.api.v1.schemas.responsibility_matrix import serialize_responsibility_matrix
from src.supplier.models.supplier import Supplier
from src.utils.parse import to_camel_case


class TimestampedOut(CamelSchema):
    """Common timestamp fields returned by persisted nested supplier objects."""

    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AddressOut(TimestampedOut):
    """Supplier address response."""

    postal_code: Optional[str] = None
    number: Optional[int] = None
    complement: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    neighbourhood: Optional[str] = None


class ContactOut(TimestampedOut):
    """Supplier contact response."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ContractOut(TimestampedOut):
    """Supplier contract response."""

    object_contract: Optional[str] = None
    executed_activities: Optional[str] = None
    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None
    contract_type: Optional[str] = None
    contract_period: Optional[str] = None
    has_contract_renewal: Optional[bool] = None
    warning_contract_renewal: Optional[bool] = None
    warning_contract_period: Optional[str] = None
    warning_on_termination: Optional[bool] = None
    warning_on_renewal: Optional[bool] = None
    warning_on_period: Optional[bool] = None


class PaymentDetailsOut(TimestampedOut):
    """Supplier payment details response."""

    payment_frequency: Optional[str] = None
    payment_date: Optional[str] = None
    contract_total_value: Optional[float] = None
    contract_monthly_value: Optional[float] = None
    checking_account: Optional[str] = None
    bank: Optional[str] = None
    bank_code: Optional[str] = None
    agency: Optional[str] = None
    payment_method: Optional[int] = None
    pix_key_type: Optional[int] = None
    pix_key: Optional[str] = None


class OrganizationalDetailsOut(TimestampedOut):
    """Supplier organizational details response."""

    cost_center: Optional[str] = None
    business_unit: Optional[str] = None
    responsible_executive: Optional[str] = None
    responsible_manager: Optional[str] = None
    payer_type: Optional[int] = None
    business_sector: Optional[int] = None
    taxpayer_classification: Optional[int] = None
    public_entity: Optional[int] = None


class FiscalDetailsOut(TimestampedOut):
    """Supplier fiscal details response."""

    iss_withholding: Optional[int] = None
    iss_regime: Optional[int] = None
    iss_taxpayer: Optional[bool] = None
    simples_nacional_participant: Optional[bool] = None
    cooperative_member: Optional[bool] = None
    withholding_tax_nature: Optional[int] = None


class CompanyInformationOut(TimestampedOut):
    """Supplier company information response."""

    company_size: Optional[int] = None
    icms_taxpayer: Optional[int] = None
    taxation_regime: Optional[int] = None
    income_type: Optional[int] = None
    taxation_method: Optional[int] = None
    customer_type: Optional[int] = None
    nit: Optional[str] = None


class SupplierSituationOut(CamelSchema):
    """Current supplier situation response."""

    id: int
    supplier: int
    status: Optional[DomainRefOut] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SupplierOut(CamelSchema):
    """Supplier detail response."""

    id: int
    name: Optional[str] = None
    trade_name: Optional[str] = None
    legal_name: str
    tax_id: str
    state_business_registration: Optional[str] = None
    municipal_business_registration: Optional[str] = None
    address: Optional[AddressOut] = None
    contact: Optional[ContactOut] = None
    payment_details: Optional[PaymentDetailsOut] = None
    organizational_details: Optional[OrganizationalDetailsOut] = None
    fiscal_details: Optional[FiscalDetailsOut] = None
    company_information: Optional[CompanyInformationOut] = None
    contract: Optional[ContractOut] = None
    classification: Optional[DomainRefOut] = None
    category: Optional[DomainRefOut] = None
    risk_level: Optional[DomainRefOut] = None
    type: Optional[DomainRefOut] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    situation: Optional[SupplierSituationOut] = None
    responsibility_matrix: Optional[dict[str, Any]] = None


class SupplierStatusSummaryOut(CamelSchema):
    """Supplier status summary used in list responses."""

    name: Optional[str] = None


class SupplierSituationSummaryOut(CamelSchema):
    """Supplier situation summary used in list responses."""

    status: SupplierStatusSummaryOut


class SupplierRiskLevelSummaryOut(CamelSchema):
    """Supplier risk level summary used in list responses."""

    name: Optional[str] = None


class SupplierContractSummaryOut(CamelSchema):
    """Supplier contract dates used in list responses."""

    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None


class SupplierListItemOut(CamelSchema):
    """Supplier item returned by paginated list endpoint."""

    id: int
    legal_name: str
    tax_id: str
    situation: SupplierSituationSummaryOut
    risk_level: SupplierRiskLevelSummaryOut
    contract: SupplierContractSummaryOut


class PaginatedSupplierListOut(CamelSchema):
    """Paginated supplier list response."""

    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: list[SupplierListItemOut]


class AddressPayload(CamelSchema):
    """Address payload used in supplier create/update."""

    postal_code: Optional[str] = None
    number: Optional[int] = None
    complement: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    neighbourhood: Optional[str] = None


class ContactPayload(CamelSchema):
    """Contact payload used in supplier create/update."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ContractPayload(CamelSchema):
    """Contract payload used in supplier create/update."""

    object_contract: Optional[str] = None
    executed_activities: Optional[str] = None
    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None
    contract_type: Optional[str] = None
    contract_period: Optional[str] = None
    has_contract_renewal: Optional[bool] = None
    warning_contract_renewal: Optional[bool] = None
    warning_contract_period: Optional[str] = None
    warning_on_termination: Optional[bool] = None
    warning_on_renewal: Optional[bool] = None
    warning_on_period: Optional[bool] = None


class PaymentDetailsPayload(CamelSchema):
    """Payment details payload used in supplier create/update."""

    payment_frequency: Optional[str] = None
    payment_date: Optional[str] = None
    contract_total_value: Optional[float] = None
    contract_monthly_value: Optional[float] = None
    checking_account: Optional[str] = None
    bank: Optional[str] = None
    bank_code: Optional[str] = None
    agency: Optional[str] = None
    payment_method_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "paymentMethod", "payment_method", "payment_method_id"
        ),
    )
    pix_key_type_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("pixKeyType", "pix_key_type", "pix_key_type_id"),
    )
    pix_key: Optional[str] = None


class OrganizationalDetailsPayload(CamelSchema):
    """Organizational details payload used in supplier create/update."""

    cost_center: Optional[str] = None
    business_unit: Optional[str] = None
    responsible_executive: Optional[str] = None
    responsible_manager: Optional[str] = None
    payer_type_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("payerType", "payer_type", "payer_type_id"),
    )
    business_sector_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "businessSector", "business_sector", "business_sector_id"
        ),
    )
    taxpayer_classification_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "taxpayerClassification",
            "taxpayer_classification",
            "taxpayer_classification_id",
        ),
    )
    public_entity_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "publicEntity", "public_entity", "public_entity_id"
        ),
    )


class FiscalDetailsPayload(CamelSchema):
    """Fiscal details payload used in supplier create/update."""

    iss_withholding_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "issWithholding", "iss_withholding", "iss_withholding_id"
        ),
    )
    iss_regime_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("issRegime", "iss_regime", "iss_regime_id"),
    )
    iss_taxpayer: Optional[bool] = None
    simples_nacional_participant: Optional[bool] = None
    cooperative_member: Optional[bool] = None
    withholding_tax_nature_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "withholdingTaxNature",
            "withholding_tax_nature",
            "withholding_tax_nature_id",
        ),
    )


class CompanyInformationPayload(CamelSchema):
    """Company information payload used in supplier create/update."""

    company_size_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("companySize", "company_size", "company_size_id"),
    )
    icms_taxpayer_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "icmsTaxpayer", "icms_taxpayer", "icms_taxpayer_id"
        ),
    )
    taxation_regime_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "taxationRegime", "taxation_regime", "taxation_regime_id"
        ),
    )
    income_type_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("incomeType", "income_type", "income_type_id"),
    )
    taxation_method_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "taxationMethod", "taxation_method", "taxation_method_id"
        ),
    )
    customer_type_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "customerType", "customer_type", "customer_type_id"
        ),
    )
    nit: Optional[str] = None


class SupplierCreateIn(CamelSchema):
    """Supplier creation payload."""

    legal_name: str
    tax_id: str
    trade_name: Optional[str] = None
    state_business_registration: Optional[str] = None
    municipal_business_registration: Optional[str] = None
    classification_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("classification", "classification_id"),
    )
    category_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("category", "category_id"),
    )
    risk_level_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("riskLevel", "risk_level", "risk_level_id"),
    )
    type_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("type", "type_id"),
    )
    address: Optional[AddressPayload] = None
    contact: Optional[ContactPayload] = None
    payment_details: Optional[PaymentDetailsPayload] = None
    organizational_details: Optional[OrganizationalDetailsPayload] = None
    fiscal_details: Optional[FiscalDetailsPayload] = None
    company_information: Optional[CompanyInformationPayload] = None
    contract: Optional[ContractPayload] = None


class SupplierUpdateIn(CamelSchema):
    """Supplier update payload."""

    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    trade_name: Optional[str] = None
    state_business_registration: Optional[str] = None
    municipal_business_registration: Optional[str] = None
    classification_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("classification", "classification_id"),
    )
    category_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("category", "category_id"),
    )
    risk_level_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("riskLevel", "risk_level", "risk_level_id"),
    )
    type_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("type", "type_id"),
    )
    address: Optional[AddressPayload] = None
    contact: Optional[ContactPayload] = None
    payment_details: Optional[PaymentDetailsPayload] = None
    organizational_details: Optional[OrganizationalDetailsPayload] = None
    fiscal_details: Optional[FiscalDetailsPayload] = None
    company_information: Optional[CompanyInformationPayload] = None
    contract: Optional[ContractPayload] = None


def _domain_ref(instance):
    if not instance:
        return None
    return DomainRefOut.model_validate(instance).model_dump(by_alias=True)


def _serialize_model(model):
    if not model:
        return None
    data = {}
    for field in model._meta.fields:  # pylint: disable=protected-access
        if field.name in {"id", "created_at", "updated_at"}:
            continue
        key = to_camel_case(field.name)
        if field.is_relation:
            data[key] = getattr(model, field.attname)
            continue
        value = getattr(model, field.name)
        data[key] = value.isoformat() if hasattr(value, "isoformat") else value
    data["id"] = model.id
    data["createdAt"] = model.created_at.isoformat() if model.created_at else None
    data["updatedAt"] = model.updated_at.isoformat() if model.updated_at else None
    return data


def serialize_supplier(instance: Supplier) -> dict[str, Any]:
    """Serialize supplier output with nested objects in camelCase."""
    data: dict[str, Any] = {
        "id": instance.id,
        "name": instance.trade_name or instance.legal_name,
        "tradeName": instance.trade_name,
        "legalName": instance.legal_name,
        "taxId": instance.tax_id,
        "stateBusinessRegistration": instance.state_business_registration,
        "municipalBusinessRegistration": instance.municipal_business_registration,
        "address": _serialize_model(instance.address),
        "contact": _serialize_model(instance.contact),
        "paymentDetails": _serialize_model(instance.payment_details),
        "organizationalDetails": _serialize_model(instance.organizational_details),
        "fiscalDetails": _serialize_model(instance.fiscal_details),
        "companyInformation": _serialize_model(instance.company_information),
        "contract": _serialize_model(instance.contract),
        "classification": _domain_ref(instance.classification),
        "category": _domain_ref(instance.category),
        "riskLevel": _domain_ref(instance.risk_level),
        "type": _domain_ref(instance.type),
        "createdAt": instance.created_at.isoformat() if instance.created_at else None,
        "updatedAt": instance.updated_at.isoformat() if instance.updated_at else None,
    }
    situation = instance.situation
    if situation:
        data["situation"] = {
            "id": situation.id,
            "supplier": situation.supplier_id,
            "status": _domain_ref(situation.status),
            "createdAt": (
                situation.created_at.isoformat() if situation.created_at else None
            ),
            "updatedAt": (
                situation.updated_at.isoformat() if situation.updated_at else None
            ),
        }
    else:
        data["situation"] = None

    if hasattr(instance, "responsibility_matrix") and instance.responsibility_matrix:
        data["responsibilityMatrix"] = serialize_responsibility_matrix(
            instance.responsibility_matrix
        )
    else:
        data["responsibilityMatrix"] = None

    return data
