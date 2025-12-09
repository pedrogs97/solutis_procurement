# pylint: disable=too-many-instance-attributes
"""
Data Transfer Objects for sync operations.
This module contains DTOs used for transferring data from external databases.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SupplierTotvsDTO:
    """DTO for supplier data from TOTVS"""

    trade_name: str
    legal_name: str
    tax_id: str
    email: str
    phone: str
    street: str
    city: str
    state: str
    neighborhood: str
    number: Optional[int]
    postal_code: str
    complement: str
    type_supplier_code: str
    category: str
    municipal_registration: str
    state_registration: str
    active: int

    @property
    def is_active(self) -> bool:
        """Check if supplier is active"""
        return self.active == 1


@dataclass
class SupplierTypeDTO:
    """DTO for supplier type data from TOTVS"""

    code: str
    description: str


@dataclass
class AddressDTO:
    """DTO for address data"""

    street: str
    city: str
    state: str
    neighbourhood: str
    number: Optional[int]
    postal_code: str
    complement: str


@dataclass
class ContactDTO:
    """DTO for contact data"""

    name: str
    email: str
    phone: str


@dataclass
class SupplierPaymentDataDTO:
    """DTO for supplier payment data from TOTVS"""

    company_code: int
    supplier_code: str
    payment_id: int
    payment_method: str
    bank_code: str
    bank_agency: str
    bank_agency_digit: str
    bank_account: str
    bank_account_digit: str
    bank_name: str
    bank_type: int
    bank_favorecido: str
    bank_favorecido_cpf_cnpj: str
    active: int
    pix_key: str
    pix_key_type: int
