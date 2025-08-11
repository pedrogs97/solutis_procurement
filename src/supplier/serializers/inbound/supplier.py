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

    address = AddressSerializer()
    contact = ContactSerializer()
    contract = ContractInSerializer()
    payment_details = PaymentDetailsInSerializer()
    organizational_details = OrganizationalDetailsInSerializer()
    fiscal_details = FiscalDetailsInSerializer()
    company_information = CompanyInformationInSerializer()

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the Supplier model serializer.
        """

        model = Supplier
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

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
        address_data = validated_data.pop("address")
        contact_data = validated_data.pop("contact")
        payment_details_data = validated_data.pop("payment_details")
        contract_data = validated_data.pop("contract")
        organizational_details_data = validated_data.pop("organizational_details")
        fiscal_details_data = validated_data.pop("fiscal_details")
        company_information_data = validated_data.pop("company_information")

        address = {}
        contact = {}
        payment_details = {}
        contract = {}
        organizational_details = {}
        fiscal_details = {}
        company_information = {}

        # Create related objects first
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
        # Create the Supplier instance with related objects
        validated_data["address"] = address
        validated_data["contact"] = contact
        validated_data["payment_details"] = payment_details
        validated_data["organizational_details"] = organizational_details
        validated_data["fiscal_details"] = fiscal_details
        validated_data["company_information"] = company_information
        validated_data["contract"] = contract

        return super().create(validated_data)

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

        if address_data:
            for attr, value in address_data.items():
                setattr(instance.address, attr, value)
            instance.address.save()

        if contact_data:
            for attr, value in contact_data.items():
                setattr(instance.contact, attr, value)
            instance.contact.save()

        if payment_details_data:
            for attr, value in payment_details_data.items():
                setattr(instance.payment_details, attr, value)
            instance.payment_details.save()

        if organizational_details_data:
            for attr, value in organizational_details_data.items():
                setattr(instance.organizational_details, attr, value)
            instance.organizational_details.save()

        if fiscal_details_data:
            for attr, value in fiscal_details_data.items():
                setattr(instance.fiscal_details, attr, value)
            instance.fiscal_details.save()

        if company_information_data:
            for attr, value in company_information_data.items():
                setattr(instance.company_information, attr, value)
            instance.company_information.save()

        if contract_data:
            for attr, value in contract_data.items():
                setattr(instance.contract, attr, value)
            instance.contract.save()

        return super().update(instance, validated_data)
