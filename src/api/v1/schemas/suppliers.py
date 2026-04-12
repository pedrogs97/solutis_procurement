"""Supplier schemas and mappers for Ninja v1."""

from typing import Any, Optional

from src.api.v1.schemas.common import CamelSchema, DomainRefOut
from src.supplier.models.supplier import Supplier


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
    payment_method: Optional[int] = None
    pix_key_type: Optional[int] = None
    pix_key: Optional[str] = None


class OrganizationalDetailsPayload(CamelSchema):
    """Organizational details payload used in supplier create/update."""

    cost_center: Optional[str] = None
    business_unit: Optional[str] = None
    responsible_executive: Optional[str] = None
    payer_type: Optional[int] = None
    business_sector: Optional[int] = None
    taxpayer_classification: Optional[int] = None
    public_entity: Optional[int] = None


class FiscalDetailsPayload(CamelSchema):
    """Fiscal details payload used in supplier create/update."""

    iss_withholding: Optional[int] = None
    iss_regime: Optional[int] = None
    iss_taxpayer: Optional[bool] = None
    simples_nacional_participant: Optional[bool] = None
    cooperative_member: Optional[bool] = None
    withholding_tax_nature: Optional[int] = None


class CompanyInformationPayload(CamelSchema):
    """Company information payload used in supplier create/update."""

    company_size: Optional[int] = None
    icms_taxpayer: Optional[int] = None
    taxation_regime: Optional[int] = None
    income_type: Optional[int] = None
    taxation_method: Optional[int] = None
    customer_type: Optional[int] = None
    nit: Optional[str] = None


class SupplierCreateIn(CamelSchema):
    """Supplier creation payload."""

    legal_name: str
    tax_id: str
    trade_name: Optional[str] = None
    state_business_registration: Optional[str] = None
    municipal_business_registration: Optional[str] = None
    classification: Optional[int] = None
    category: Optional[int] = None
    risk_level: Optional[int] = None
    type: Optional[int] = None
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
    classification: Optional[int] = None
    category: Optional[int] = None
    risk_level: Optional[int] = None
    type: Optional[int] = None
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
        if field.is_relation:
            data[field.name] = getattr(model, field.attname)
            continue
        data[field.name] = getattr(model, field.name)
    data["id"] = model.id
    data["createdAt"] = model.created_at.isoformat() if model.created_at else None
    data["updatedAt"] = model.updated_at.isoformat() if model.updated_at else None
    return CamelSchema.model_validate(data).model_dump(by_alias=True)


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
        matrix_data = {}
        for (
            field
        ) in (
            instance.responsibility_matrix._meta.fields
        ):  # pylint: disable=protected-access
            if field.name in {"supplier"}:
                continue
            value = getattr(instance.responsibility_matrix, field.name)
            matrix_data[field.name] = (
                value.isoformat() if hasattr(value, "isoformat") else value
            )
        data["responsibilityMatrix"] = CamelSchema.model_validate(
            matrix_data
        ).model_dump(by_alias=True)
    else:
        data["responsibilityMatrix"] = None

    return data
