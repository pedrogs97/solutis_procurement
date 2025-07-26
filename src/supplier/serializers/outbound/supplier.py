"""
Serializer for Supplier model.
This module provides serializers for output representations of the Supplier model.
"""

from src.shared.serializers import AddressSerializer, BaseSerializer, ContactSerializer
from src.supplier.models.supplier import (
    CompanyInformation,
    Contract,
    FiscalDetails,
    OrganizationalDetails,
    PaymentDetails,
    Supplier,
)
from src.supplier.serializers.outbound.domain import (
    DomBusinessSectorSerializer,
    DomCategorySerializer,
    DomClassificationSerializer,
    DomCompanySizeSerializer,
    DomCustomerTypeSerializer,
    DomIcmsTaxpayerSerializer,
    DomIncomeTypeSerializer,
    DomIssRegimeSerializer,
    DomIssWithholdingSerializer,
    DomPayerTypeSerializer,
    DomPaymentMethodSerializer,
    DomPixTypeSerializer,
    DomPublicEntitySerializer,
    DomRiskLevelSerializer,
    DomSupplierSituationSerializer,
    DomTaxationMethodSerializer,
    DomTaxationRegimeSerializer,
    DomTaxpayerClassificationSerializer,
    DomTypeSupplierSerializer,
    DomWithholdingTaxSerializer,
)


class ContractOutSerializer(BaseSerializer):
    """
    Serializer for Contract model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for ContractOutSerializer.
        """

        model = Contract
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PaymentDetailsOutSerializer(BaseSerializer):
    """
    Serializer for PaymentDetails model.
    Converts field names to camelCase representation.
    """

    payment_method = DomPaymentMethodSerializer()
    pix_key_type = DomPixTypeSerializer()

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for PaymentDetailsOutSerializer.
        """

        model = PaymentDetails
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class OrganizationalDetailsOutSerializer(BaseSerializer):
    """
    Serializer for OrganizationalDetails model.
    Converts field names to camelCase representation.
    """

    payer_type = DomPayerTypeSerializer()
    business_sector = DomBusinessSectorSerializer()
    taxpayer_classification = DomTaxpayerClassificationSerializer()
    public_entity = DomPublicEntitySerializer()

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for OrganizationalDetailsOutSerializer.
        """

        model = OrganizationalDetails
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class FiscalDetailsOutSerializer(BaseSerializer):
    """
    Serializer for FiscalDetails model.
    Converts field names to camelCase representation.
    """

    iss_withholding = DomIssWithholdingSerializer()
    iss_regime = DomIssRegimeSerializer()
    withholding_tax_nature = DomWithholdingTaxSerializer()

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for FiscalDetailsOutSerializer.
        """

        model = FiscalDetails
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CompanyInformationOutSerializer(BaseSerializer):
    """
    Serializer for CompanyInformation model.
    Converts field names to camelCase representation.
    """

    company_size = DomCompanySizeSerializer()
    icms_taxpayer = DomIcmsTaxpayerSerializer()
    income_type = DomIncomeTypeSerializer()
    taxation_method = DomTaxationMethodSerializer()
    customer_type = DomCustomerTypeSerializer()
    taxation_regime = DomTaxationRegimeSerializer()

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for CompanyInformationOutSerializer.
        """

        model = CompanyInformation
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SupplierOutSerializer(BaseSerializer):
    """
    Serializer for Supplier model.
    Converts field names to camelCase representation.
    """

    address = AddressSerializer()
    contact = ContactSerializer()
    payment_details = PaymentDetailsOutSerializer()
    organizational_details = OrganizationalDetailsOutSerializer()
    fiscal_details = FiscalDetailsOutSerializer()
    company_information = CompanyInformationOutSerializer()
    contract = ContractOutSerializer()
    classification = DomClassificationSerializer()
    category = DomCategorySerializer()
    risk_level = DomRiskLevelSerializer()
    type = DomTypeSupplierSerializer()
    situation = DomSupplierSituationSerializer()

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for SupplierOutSerializer.
        """

        model = Supplier
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
