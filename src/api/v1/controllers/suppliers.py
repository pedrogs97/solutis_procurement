"""Controller functions for supplier-related operations."""

from typing import Any, Dict, Optional, Type, Union

from django.db.models import Model
from django.db.transaction import atomic

from src.api.v1.schemas.common import CamelSchema
from src.api.v1.schemas.suppliers import SupplierCreateIn, SupplierUpdateIn
from src.shared.models import Address, Contact
from src.supplier.models.supplier import (
    CompanyInformation,
    Contract,
    FiscalDetails,
    OrganizationalDetails,
    PaymentDetails,
    Supplier,
)


def _to_payload_dict(payload: Any) -> Dict[str, Any]:
    """Normalize payloads coming from Ninja schemas or plain dictionaries."""
    if payload is None:
        return {}
    if isinstance(payload, dict):
        return payload

    model_dump = getattr(payload, "model_dump", None)
    if callable(model_dump):
        return model_dump(by_alias=False, exclude_none=True)

    dict_method = getattr(payload, "dict", None)
    if callable(dict_method):
        return dict_method(by_alias=False, exclude_none=True)

    raise TypeError(f"Unsupported payload type: {type(payload)!r}")


def _create_or_update_related(
    instance, attr_name: str, payload: Optional[CamelSchema], model_cls: Type[Model]
):
    """Create or update a related object based on the provided payload."""
    if payload is None:
        return
    data = _to_payload_dict(payload)

    related_obj = getattr(instance, attr_name, None)
    if related_obj:
        for key, value in data.items():
            setattr(related_obj, key, value)
        related_obj.save()
    else:
        related_obj = model_cls.objects.create(**data)
        setattr(instance, attr_name, related_obj)


@atomic
def apply_supplier_payload(
    instance: Optional[Supplier],
    payload: Union[SupplierCreateIn, SupplierUpdateIn],
) -> Supplier:
    """Persist supplier payload and nested objects."""
    supplier_data = _to_payload_dict(payload)
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


def serialize_supplier_list(instance: Supplier) -> Dict[str, Any]:
    """Serialize supplier list item output in camelCase."""
    situation = instance.situation
    data: Dict[str, Any] = {
        "id": instance.pk,
        "legalName": instance.legal_name,
        "taxId": instance.tax_id,
        "situation": {
            "status": {
                "name": situation.status.name if situation else None,
            }
        },
        "riskLevel": {
            "name": instance.risk_level.name if instance.risk_level else None,
        },
        "contract": {
            "contractStartDate": (
                instance.contract.contract_start_date.isoformat()
                if instance.contract and instance.contract.contract_start_date
                else None
            ),
            "contractEndDate": (
                instance.contract.contract_end_date.isoformat()
                if instance.contract and instance.contract.contract_end_date
                else None
            ),
        },
    }
    return data
