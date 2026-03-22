"""Supplier schemas and mappers for Ninja v1."""

from typing import Any

from src.api.v1.schemas.common import CamelSchema, DomainRefOut
from src.shared.models import Address, Contact
from src.supplier.models.supplier import (
    CompanyInformation,
    Contract,
    FiscalDetails,
    OrganizationalDetails,
    PaymentDetails,
    Supplier,
)


class AddressPayload(CamelSchema):
    """Address payload used in supplier create/update."""

    postal_code: str | None = None
    number: int | None = None
    complement: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    neighbourhood: str | None = None


class ContactPayload(CamelSchema):
    """Contact payload used in supplier create/update."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None


class ContractPayload(CamelSchema):
    """Contract payload used in supplier create/update."""

    object_contract: str | None = None
    executed_activities: str | None = None
    contract_start_date: str | None = None
    contract_end_date: str | None = None
    contract_type: str | None = None
    contract_period: str | None = None
    has_contract_renewal: bool | None = None
    warning_contract_renewal: bool | None = None
    warning_contract_period: str | None = None
    warning_on_termination: bool | None = None
    warning_on_renewal: bool | None = None
    warning_on_period: bool | None = None


class PaymentDetailsPayload(CamelSchema):
    """Payment details payload used in supplier create/update."""

    payment_frequency: str | None = None
    payment_date: str | None = None
    contract_total_value: float | None = None
    contract_monthly_value: float | None = None
    checking_account: str | None = None
    bank: str | None = None
    bank_code: str | None = None
    agency: str | None = None
    payment_method: int | None = None
    pix_key_type: int | None = None
    pix_key: str | None = None


class OrganizationalDetailsPayload(CamelSchema):
    """Organizational details payload used in supplier create/update."""

    cost_center: str | None = None
    business_unit: str | None = None
    responsible_executive: str | None = None
    payer_type: int | None = None
    business_sector: int | None = None
    taxpayer_classification: int | None = None
    public_entity: int | None = None


class FiscalDetailsPayload(CamelSchema):
    """Fiscal details payload used in supplier create/update."""

    iss_withholding: int | None = None
    iss_regime: int | None = None
    iss_taxpayer: bool | None = None
    simples_nacional_participant: bool | None = None
    cooperative_member: bool | None = None
    withholding_tax_nature: int | None = None


class CompanyInformationPayload(CamelSchema):
    """Company information payload used in supplier create/update."""

    company_size: int | None = None
    icms_taxpayer: int | None = None
    taxation_regime: int | None = None
    income_type: int | None = None
    taxation_method: int | None = None
    customer_type: int | None = None
    nit: str | None = None


class SupplierCreateIn(CamelSchema):
    """Supplier creation payload."""

    legal_name: str
    tax_id: str
    trade_name: str | None = None
    state_business_registration: str | None = None
    municipal_business_registration: str | None = None
    classification: int | None = None
    category: int | None = None
    risk_level: int | None = None
    type: int | None = None
    address: AddressPayload | None = None
    contact: ContactPayload | None = None
    payment_details: PaymentDetailsPayload | None = None
    organizational_details: OrganizationalDetailsPayload | None = None
    fiscal_details: FiscalDetailsPayload | None = None
    company_information: CompanyInformationPayload | None = None
    contract: ContractPayload | None = None


class SupplierUpdateIn(CamelSchema):
    """Supplier update payload."""

    legal_name: str | None = None
    tax_id: str | None = None
    trade_name: str | None = None
    state_business_registration: str | None = None
    municipal_business_registration: str | None = None
    classification: int | None = None
    category: int | None = None
    risk_level: int | None = None
    type: int | None = None
    address: AddressPayload | None = None
    contact: ContactPayload | None = None
    payment_details: PaymentDetailsPayload | None = None
    organizational_details: OrganizationalDetailsPayload | None = None
    fiscal_details: FiscalDetailsPayload | None = None
    company_information: CompanyInformationPayload | None = None
    contract: ContractPayload | None = None


class SupplierListOut(CamelSchema):
    """Paginated supplier list response."""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[dict[str, Any]]


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
            "createdAt": situation.created_at.isoformat()
            if situation.created_at
            else None,
            "updatedAt": situation.updated_at.isoformat()
            if situation.updated_at
            else None,
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


def _payload_to_dict(payload):
    if payload is None:
        return None
    return payload.model_dump(by_alias=False, exclude_none=True)


def _create_or_update_related(instance, attr_name: str, payload, model_cls):
    data = _payload_to_dict(payload)
    if data is None:
        return

    related_obj = getattr(instance, attr_name, None)
    if related_obj:
        for key, value in data.items():
            setattr(related_obj, key, value)
        related_obj.save()
    else:
        related_obj = model_cls.objects.create(**data)
        setattr(instance, attr_name, related_obj)


def apply_supplier_payload(
    instance: Supplier | None,
    payload: SupplierCreateIn | SupplierUpdateIn,
) -> Supplier:
    """Persist supplier payload and nested objects."""
    supplier_data = payload.model_dump(by_alias=False, exclude_none=True)
    nested = {
        "address": supplier_data.pop("address", None),
        "contact": supplier_data.pop("contact", None),
        "payment_details": supplier_data.pop("payment_details", None),
        "organizational_details": supplier_data.pop("organizational_details", None),
        "fiscal_details": supplier_data.pop("fiscal_details", None),
        "company_information": supplier_data.pop("company_information", None),
        "contract": supplier_data.pop("contract", None),
    }

    if instance is None:
        instance = Supplier.objects.create(**supplier_data)
    else:
        for key, value in supplier_data.items():
            setattr(instance, key, value)

    _create_or_update_related(instance, "address", nested["address"], Address)
    _create_or_update_related(instance, "contact", nested["contact"], Contact)
    _create_or_update_related(
        instance, "payment_details", nested["payment_details"], PaymentDetails
    )
    _create_or_update_related(
        instance,
        "organizational_details",
        nested["organizational_details"],
        OrganizationalDetails,
    )
    _create_or_update_related(
        instance, "fiscal_details", nested["fiscal_details"], FiscalDetails
    )
    _create_or_update_related(
        instance,
        "company_information",
        nested["company_information"],
        CompanyInformation,
    )
    _create_or_update_related(instance, "contract", nested["contract"], Contract)

    instance.save()
    return instance
