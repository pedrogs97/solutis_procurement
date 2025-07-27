"""
Serializer for Supplier model.
This module provides serializers for input representations of the Supplier model.
"""

from typing import Dict

from django.db.transaction import atomic
from rest_framework import serializers

from src.shared.mixins import SerializerCamelCaseRepresentationMixin
from src.shared.models import Address, Contact
from src.shared.serializers import AddressSerializer, ContactSerializer
from src.supplier.models.supplier import (
    CompanyInformation,
    Contract,
    FiscalDetails,
    OrganizationalDetails,
    PaymentDetails,
    Supplier,
)


class ContractInSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for Contract model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta options for the Contract model serializer.
        """

        model = Contract
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PaymentDetailsInSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for PaymentDetails model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta options for the PaymentDetails model serializer.
        """

        model = PaymentDetails
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class OrganizationalDetailsInSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for OrganizationalDetails model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta options for the OrganizationalDetails model serializer.
        """

        model = OrganizationalDetails
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class FiscalDetailsInSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for FiscalDetails model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta options for the FiscalDetails model serializer.
        """

        model = FiscalDetails
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CompanyInformationInSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for CompanyInformation model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta options for the CompanyInformation model serializer.
        """

        model = CompanyInformation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SupplierInSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
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

    class Meta:
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
        # Create related objects first
        address = Address.objects.create(**address_data)
        contact = Contact.objects.create(**contact_data)
        payment_details = PaymentDetails.objects.create(**payment_details_data)
        organizational_details = OrganizationalDetails.objects.create(
            **organizational_details_data
        )
        fiscal_details = FiscalDetails.objects.create(**fiscal_details_data)
        company_information = CompanyInformation.objects.create(
            **company_information_data
        )
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
