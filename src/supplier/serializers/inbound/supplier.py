"""
Serializer for Supplier model.
This module provides serializers for input representations of the Supplier model.
"""

from typing import Dict

from django.db.transaction import atomic

from src.shared.models import Address, Contact
from src.shared.serializers import AddressSerializer, BaseSerializer, ContactSerializer
from src.supplier.models.supplier import (
    CompanyInformation,
    Contract,
    FiscalDetails,
    OrganizationalDetails,
    PaymentDetails,
    Supplier,
)


class ContractInSerializer(BaseSerializer):
    """
    Serializer for Contract model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the Contract model serializer.
        """

        model = Contract
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PaymentDetailsInSerializer(BaseSerializer):
    """
    Serializer for PaymentDetails model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the PaymentDetails model serializer.
        """

        model = PaymentDetails
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class OrganizationalDetailsInSerializer(BaseSerializer):
    """
    Serializer for OrganizationalDetails model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the OrganizationalDetails model serializer.
        """

        model = OrganizationalDetails
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class FiscalDetailsInSerializer(BaseSerializer):
    """
    Serializer for FiscalDetails model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the FiscalDetails model serializer.
        """

        model = FiscalDetails
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CompanyInformationInSerializer(BaseSerializer):
    """
    Serializer for CompanyInformation model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the CompanyInformation model serializer.
        """

        model = CompanyInformation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SupplierInSerializer(BaseSerializer):
    """
    Serializer for Supplier model.
    Converts field names to camelCase representation.
    """

    address = AddressSerializer(required=False, allow_null=True)
    contact = ContactSerializer(required=False, allow_null=True)
    contract = ContractInSerializer(required=False, allow_null=True)
    payment_details = PaymentDetailsInSerializer(required=False, allow_null=True)
    organizational_details = OrganizationalDetailsInSerializer(
        required=False, allow_null=True
    )
    fiscal_details = FiscalDetailsInSerializer(required=False, allow_null=True)
    company_information = CompanyInformationInSerializer(
        required=False, allow_null=True
    )

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the Supplier model serializer.
        """

        model = Supplier
        fields = "__all__"
        read_only_fields = ("id", "situation", "created_at", "updated_at")

    @atomic
    def create(self, validated_data: Dict) -> Supplier:
        """
        Create a new Supplier instance with related objects.
        This method handles the creation of related objects like Address, Contact, etc.

        Args:
            validated_data (Dict): The validated data for the Supplier.
        Returns:
            Supplier: The created Supplier instance.
        """
        address_data = validated_data.pop("address", None)
        contact_data = validated_data.pop("contact", None)
        payment_details_data = validated_data.pop("payment_details", None)
        contract_data = validated_data.pop("contract", None)
        organizational_details_data = validated_data.pop(
            "organizational_details", None
        )
        fiscal_details_data = validated_data.pop("fiscal_details", None)
        company_information_data = validated_data.pop("company_information", None)

        address = {}
        contact = {}
        payment_details = {}
        contract = {}
        organizational_details = {}
        fiscal_details = {}
        company_information = {}

        if address_data:
            address = Address.objects.create(**address_data)
        if contact_data:
            contact = Contact.objects.create(**contact_data)
        if payment_details_data:
            payment_details = PaymentDetails.objects.create(**payment_details_data)
        if organizational_details_data:
            organizational_details = OrganizationalDetails.objects.create(
                **organizational_details_data
            )
        if fiscal_details_data:
            fiscal_details = FiscalDetails.objects.create(**fiscal_details_data)
        if company_information_data:
            company_information = CompanyInformation.objects.create(
                **company_information_data
            )
        if contract_data:
            contract = Contract.objects.create(**contract_data)

        validated_data["address_id"] = address.pk if address else None
        validated_data["contact_id"] = contact.pk if contact else None
        validated_data["payment_details_id"] = (
            payment_details.pk if payment_details else None
        )
        validated_data["organizational_details_id"] = (
            organizational_details.pk if organizational_details else None
        )
        validated_data["fiscal_details_id"] = (
            fiscal_details.pk if fiscal_details else None
        )
        validated_data["company_information_id"] = (
            company_information.pk if company_information else None
        )
        validated_data["contract_id"] = contract.pk if contract else None
        return super().create(validated_data)

    def _update_or_create_related(
        self, instance: Supplier, field_name: str, data: Dict, model_class
    ) -> None:
        """
        Update or create a related object on the instance.

        Args:
            instance (Supplier): The Supplier instance to update.
            field_name (str): The name of the field to update.
            data (Dict): The data to update or use for creation.
            model_class: The model class to use for creation.
        """
        if not data:
            return

        related_obj = (
            getattr(instance, field_name, None)
            if hasattr(instance, field_name)
            else None
        )

        if related_obj:
            for attr, value in data.items():
                setattr(related_obj, attr, value)
        else:
            related_obj = model_class.objects.create(**data)
            setattr(instance, field_name, related_obj)

        related_obj.save()

    @atomic
    def update(self, instance: Supplier, validated_data: Dict) -> Supplier:
        """
        Update an existing Supplier instance with related objects.
        This method handles the update of related objects like Address, Contact, etc.

        Args:
            instance (Supplier): The existing Supplier instance to update.
            validated_data (Dict): The validated data for the Supplier.
        Returns:
            Supplier: The updated Supplier instance.
        """
        address_data = validated_data.pop("address", None)
        contact_data = validated_data.pop("contact", None)
        payment_details_data = validated_data.pop("payment_details", None)
        contract_data = validated_data.pop("contract", None)
        organizational_details_data = validated_data.pop("organizational_details", None)
        fiscal_details_data = validated_data.pop("fiscal_details", None)
        company_information_data = validated_data.pop("company_information", None)

        self._update_or_create_related(instance, "address", address_data, Address)
        self._update_or_create_related(instance, "contact", contact_data, Contact)
        self._update_or_create_related(
            instance, "payment_details", payment_details_data, PaymentDetails
        )
        self._update_or_create_related(
            instance,
            "organizational_details",
            organizational_details_data,
            OrganizationalDetails,
        )
        self._update_or_create_related(
            instance, "fiscal_details", fiscal_details_data, FiscalDetails
        )
        self._update_or_create_related(
            instance,
            "company_information",
            company_information_data,
            CompanyInformation,
        )
        self._update_or_create_related(instance, "contract", contract_data, Contract)

        return super().update(instance, validated_data)
