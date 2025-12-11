"""
Supplier synchronization service.
This module handles the synchronization of supplier data from TOTVS to local database.
"""

import logging
from typing import Dict, List, Optional

from django.db import transaction

from src.shared.models import Address, Contact
from src.supplier.models.domain import (
    DomPaymentMethod,
    DomPixType,
    DomRiskLevel,
    DomTypeSupplier,
)
from src.supplier.models.supplier import PaymentDetails, Supplier
from src.sync.dto import (
    AddressDTO,
    ContactDTO,
    SupplierPaymentDataDTO,
    SupplierTotvsDTO,
    SupplierTypeDTO,
)
from src.sync.mapper import PAYMENT_METHOD_MAPPER, PIX_TYPE_MAPPER
from src.sync.queries import (
    GET_SUPPLIER_PAYMENT_DATA,
    GET_SUPPLIER_TYPE_BY_CODE,
    GET_SUPPLIERS_BY_TAX_IDS,
)
from src.sync.services.database_connection import DatabaseConnectionService

logger = logging.getLogger(__name__)


class SupplierSyncService:
    """
    Service for synchronizing supplier data from TOTVS to local database.
    Follows Single Responsibility Principle.
    """

    def __init__(self, db_service: DatabaseConnectionService):
        """
        Initialize the sync service.

        Args:
            db_service: Database connection service instance
        """
        self.db_service = db_service
        self._risk_mapping: Dict[str, str] = {
            "04.699.639/0001-68": "BAIXO",
            "05.607.657/0008-01": "ALTO",
            "07.976.147/0001-60": "MÉDIO",
            "12.499.520/0001-70": "BAIXO",
            "12.639.870/0001-94": "MÉDIO",
            "31.433.149/0001-98": "BAIXO",
            "53.113.791/0001-22": "ALTO",
            "43.649.570/0001-10": "BAIXO",
            "33.571.622/0001-29": "BAIXO",
            "60.143.657/0001-30": "BAIXO",
        }

    def sync_suppliers(self) -> int:
        """
        Synchronize suppliers from TOTVS to local database.

        Returns:
            int: Number of suppliers synchronized

        Raises:
            Exception: If synchronization fails
        """
        try:
            logger.info("Starting supplier synchronization from TOTVS")

            suppliers_dto = self._fetch_suppliers_from_totvs()
            logger.info("Fetched %s suppliers from TOTVS", len(suppliers_dto))

            saved_count = self._save_suppliers(suppliers_dto)
            logger.info("Successfully synchronized %s suppliers", saved_count)

            return saved_count

        except Exception as error:
            logger.error("Error synchronizing suppliers: %s", error)
            raise

        finally:
            self.db_service.close()

    def _fetch_suppliers_from_totvs(self) -> List[SupplierTotvsDTO]:
        """
        Fetch supplier data from TOTVS database.

        Returns:
            List[SupplierTotvsDTO]: List of supplier DTOs
        """
        cursor = self.db_service.get_cursor()

        tax_ids = list(self._risk_mapping.keys())
        params_list = ",".join(f"'{tax_id}'" for tax_id in tax_ids)

        query = GET_SUPPLIERS_BY_TAX_IDS.format(tax_ids_list=params_list)
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows is None:
            return []

        return [self._convert_row_to_supplier_dto(dict(row)) for row in rows]

    def _convert_row_to_supplier_dto(self, row: Dict) -> SupplierTotvsDTO:
        """
        Convert database row to SupplierTotvsDTO.

        Args:
            row: Database row dictionary

        Returns:
            SupplierTotvsDTO: Converted supplier DTO
        """
        return SupplierTotvsDTO(
            trade_name=row["NOMEFANTASIA"] or "",
            legal_name=row["NOME"] or "",
            tax_id=row["CGCCFO"] or "",
            email=row["EMAIL"] or "",
            phone=row["TELEFONE"] or "",
            street=row["RUA"] or "",
            city=row["CIDADE"] or "",
            state=row["CODETD"] or "",
            neighborhood=row["BAIRRO"] or "",
            number=self._parse_number(row["NUMERO"]),
            postal_code=row["CEP"] or "",
            complement=row["COMPLEMENTO"] or "",
            type_supplier_code=row["CODTCF"] or "",
            category=row["PESSOAFISOUJUR"] or "",
            municipal_registration=row["INSCRMUNICIPAL"] or "",
            state_registration=row["INSCRESTADUAL"] or "",
            active=row["ATIVO"],
            contact_name=row["CONTATO"] or "",
        )

    def _parse_number(self, value) -> Optional[int]:
        """
        Parse number field, returning None if value is a string.

        Args:
            value: The value to parse

        Returns:
            Optional[int]: Parsed number or None
        """
        return None if isinstance(value, str) else value

    def _fetch_supplier_type(self, type_code: str) -> SupplierTypeDTO:
        """
        Fetch supplier type from TOTVS.

        Args:
            type_code: Supplier type code

        Returns:
            SupplierTypeDTO: Supplier type DTO
        """
        cursor = self.db_service.get_cursor()
        query = GET_SUPPLIER_TYPE_BY_CODE.format(type_code=type_code)
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            raise ValueError(f"Supplier type not found for code: {type_code}")

        row = dict(rows[0])
        return SupplierTypeDTO(
            code=row["CODTCF"], description=row["DESCRICAO"].strip().upper()
        )

    @transaction.atomic
    def _save_suppliers(self, suppliers_dto: List[SupplierTotvsDTO]) -> int:
        """
        Save or update suppliers in local database.

        Args:
            suppliers_dto: List of supplier DTOs

        Returns:
            int: Number of suppliers saved or updated
        """
        saved_count = 0

        for supplier_dto in suppliers_dto:
            try:
                # Check if supplier already exists
                existing_supplier = Supplier.objects.filter(
                    tax_id=supplier_dto.tax_id
                ).first()

                if existing_supplier:
                    # Update existing supplier
                    print(supplier_dto)
                    self._update_supplier(existing_supplier, supplier_dto)
                    logger.info("Updated supplier: %s", supplier_dto.legal_name)
                else:
                    # Create new supplier
                    self._create_supplier(supplier_dto)
                    logger.info("Created supplier: %s", supplier_dto.legal_name)
                saved_count += 1

            except Exception as error:
                logger.error(
                    "Error processing supplier %s: %s", supplier_dto.legal_name, error
                )
                continue

        return saved_count

    def _create_supplier(self, supplier_dto: SupplierTotvsDTO) -> Supplier:
        """
        Create a new supplier from DTO.

        Args:
            supplier_dto: Supplier DTO

        Returns:
            Supplier: Created supplier instance
        """
        address = self._create_address(
            AddressDTO(
                street=supplier_dto.street,
                city=supplier_dto.city,
                state=supplier_dto.state,
                neighbourhood=supplier_dto.neighborhood,
                number=supplier_dto.number,
                postal_code=supplier_dto.postal_code,
                complement=supplier_dto.complement,
            )
        )

        contact = self._create_contact(
            ContactDTO(
                name=supplier_dto.contact_name,
                email=supplier_dto.email,
                phone=supplier_dto.phone,
            )
        )

        supplier_type_dto = self._fetch_supplier_type(supplier_dto.type_supplier_code)
        supplier_type, _ = DomTypeSupplier.objects.get_or_create(
            name=supplier_type_dto.description
        )

        risk_level = DomRiskLevel.objects.get(
            name=self._risk_mapping[supplier_dto.tax_id]
        )
        payment_details = self._save_supplier_payment_data(supplier_dto.tax_id)

        return Supplier.objects.create(
            trade_name=supplier_dto.trade_name,
            legal_name=supplier_dto.legal_name,
            tax_id=supplier_dto.tax_id,
            state_business_registration=supplier_dto.state_registration,
            municipal_business_registration=supplier_dto.municipal_registration,
            address=address,
            contact=contact,
            classification_id=1,
            category_id=1 if supplier_dto.category.upper() == "J" else 2,
            risk_level=risk_level,
            type=supplier_type,
            payment_details=payment_details,
        )

    def _update_supplier(
        self, supplier: Supplier, supplier_dto: SupplierTotvsDTO
    ) -> None:
        """
        Update existing supplier with data from DTO.

        Args:
            supplier: Existing supplier instance
            supplier_dto: Supplier DTO with updated data
        """
        # Update basic supplier information
        supplier.trade_name = supplier_dto.trade_name
        supplier.legal_name = supplier_dto.legal_name
        supplier.state_business_registration = supplier_dto.state_registration
        supplier.municipal_business_registration = supplier_dto.municipal_registration
        supplier.category_id = 1 if supplier_dto.category.upper() == "J" else 2

        # Update supplier type
        supplier_type_dto = self._fetch_supplier_type(supplier_dto.type_supplier_code)
        supplier_type, _ = DomTypeSupplier.objects.get_or_create(
            name=supplier_type_dto.description
        )
        supplier.type = supplier_type

        # Update address if exists, otherwise create new
        if supplier.address:
            self._update_address(supplier.address, supplier_dto)
        else:
            supplier.address = self._create_address(
                AddressDTO(
                    street=supplier_dto.street,
                    city=supplier_dto.city,
                    state=supplier_dto.state,
                    neighbourhood=supplier_dto.neighborhood,
                    number=supplier_dto.number,
                    postal_code=supplier_dto.postal_code,
                    complement=supplier_dto.complement,
                )
            )

        # Update contact if exists, otherwise create new
        if supplier.contact:
            self._update_contact(supplier.contact, supplier_dto)
        else:
            supplier.contact = self._create_contact(
                ContactDTO(
                    name=supplier_dto.contact_name,
                    email=supplier_dto.email,
                    phone=supplier_dto.phone,
                )
            )

        supplier.save()

    def _create_address(self, address_dto: AddressDTO) -> Address:
        """
        Create address from DTO.

        Args:
            address_dto: Address DTO

        Returns:
            Address: Created address instance
        """
        address = Address.objects.create(
            street=address_dto.street,
            city=address_dto.city,
            state=address_dto.state,
            neighbourhood=address_dto.neighbourhood,
            number=address_dto.number,
            postal_code=address_dto.postal_code,
            complement=address_dto.complement,
        )
        address.refresh_from_db()
        return address

    def _create_contact(self, contact_dto: ContactDTO) -> Contact:
        """
        Create contact from DTO.

        Args:
            contact_dto: Contact DTO

        Returns:
            Contact: Created contact instance
        """
        contact = Contact.objects.create(
            name=contact_dto.name, email=contact_dto.email, phone=contact_dto.phone
        )
        contact.refresh_from_db()
        return contact

    def _update_address(self, address: Address, supplier_dto: SupplierTotvsDTO) -> None:
        """
        Update existing address with data from DTO.

        Args:
            address: Existing address instance
            supplier_dto: Supplier DTO with updated address data
        """
        address.street = supplier_dto.street
        address.city = supplier_dto.city
        address.state = supplier_dto.state
        address.neighbourhood = supplier_dto.neighborhood
        address.number = supplier_dto.number
        address.postal_code = supplier_dto.postal_code
        address.complement = supplier_dto.complement
        address.save()

    def _update_contact(self, contact: Contact, supplier_dto: SupplierTotvsDTO) -> None:
        """
        Update existing contact with data from DTO.

        Args:
            contact: Existing contact instance
            supplier_dto: Supplier DTO with updated contact data
        """
        contact.email = supplier_dto.email
        contact.phone = supplier_dto.phone
        contact.name = supplier_dto.contact_name
        contact.save()

    def _convert_row_to_supplier_payment_data_dto(
        self, row: Dict
    ) -> SupplierPaymentDataDTO:
        """
        Convert database row to SupplierPaymentDataDTO.

        Args:
            row: Database row dictionary

        Returns:
            SupplierPaymentDataDTO: Converted supplier payment data DTO
        """
        return SupplierPaymentDataDTO(
            company_code=row["CODCOLIGADA"],
            supplier_code=row["CODCFO"],
            payment_id=row["IDPGTO"],
            payment_method=row["FORMAPAGAMENTO"],
            bank_code=row["NUMEROBANCO"],
            bank_agency=row["CODIGOAGENCIA"],
            bank_agency_digit=row["DIGITOAGENCIA"],
            bank_account=row["CONTACORRENTE"],
            bank_account_digit=row["DIGITOCONTA"],
            bank_name=row["NOMEAGENCIA"],
            bank_type=row["TIPOCONTA"],
            bank_favorecido=row["FAVORECIDO"],
            bank_favorecido_cpf_cnpj=row["CGCFAVORECIDO"],
            active=row["ATIVO"],
            pix_key=row["CHAVE"],
            pix_key_type=row["TIPOPIX"],
        )

    def _fetch_supplier_payment_data(
        self, tax_id: str
    ) -> Optional[SupplierPaymentDataDTO]:
        """
        Fetch supplier payment data from TOTVS database.

        Args:
            tax_id: Supplier tax ID

        Returns:
            List[SupplierPaymentDataDTO]: List of supplier payment data DTOs
        """
        cursor = self.db_service.get_cursor()
        query = GET_SUPPLIER_PAYMENT_DATA.format(tax_id=tax_id)
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            return None

        row_data = dict(rows[0])
        return self._convert_row_to_supplier_payment_data_dto(row_data)

    def _save_supplier_payment_data(self, tax_id: str) -> Optional[PaymentDetails]:
        """
        Save supplier payment data to local database.

        Args:
            tax_id: Supplier tax ID

        Returns:
            Optional[PaymentDetails]: Payment details if saved, None otherwise
        """
        supplier_payment_data_dto = self._fetch_supplier_payment_data(tax_id)

        if not supplier_payment_data_dto:
            return None

        payment_method = DomPaymentMethod.objects.get(
            name=PAYMENT_METHOD_MAPPER[supplier_payment_data_dto.payment_method]
        )
        pix_type = DomPixType.objects.get(
            name=PIX_TYPE_MAPPER[supplier_payment_data_dto.pix_key_type]
        )
        try:
            payment_details = PaymentDetails.objects.create(
                payment_method=payment_method,
                bank_code=supplier_payment_data_dto.bank_code,
                bank_agency=supplier_payment_data_dto.bank_agency,
                bank_account=supplier_payment_data_dto.bank_account,
                bank_account_digit=supplier_payment_data_dto.bank_account_digit,
                bank_name=supplier_payment_data_dto.bank_name,
                bank_favorecido=supplier_payment_data_dto.bank_favorecido,
                bank_favorecido_cpf_cnpj=supplier_payment_data_dto.bank_favorecido_cpf_cnpj,
                active=supplier_payment_data_dto.active,
                pix_key=supplier_payment_data_dto.pix_key,
                pix_key_type=pix_type,
            )
            payment_details.refresh_from_db()
            logger.info(
                "Saved supplier payment data: %s", supplier_payment_data_dto.payment_id
            )
            return payment_details
        except Exception as error:
            logger.error(
                "Error saving supplier payment data %s: %s",
                supplier_payment_data_dto.payment_id,
                error,
            )
            return None
