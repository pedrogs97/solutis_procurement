"""
Serializer for SupplierAttachment model.
This module provides serializers for output representations of the SupplierAttachment model.
"""

from rest_framework import serializers

from src.shared.mixins import SerializerCamelCaseRepresentationMixin
from src.supplier.models.domain import (
    DomBusinessSector,
    DomCategory,
    DomClassification,
    DomCompanySize,
    DomCustomerType,
    DomIcmsTaxpayer,
    DomIncomeType,
    DomIssRegime,
    DomIssWithholding,
    DomPayerType,
    DomPaymentMethod,
    DomPixType,
    DomPublicEntity,
    DomRiskLevel,
    DomSupplierSituation,
    DomTaxationMethod,
    DomTaxationRegime,
    DomTaxpayerClassification,
    DomTypeSupplier,
    DomWithholdingTax,
)


class DomClassificationSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomClassification model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomClassificationSerializer.
        """

        model = DomClassification
        fields = "__all__"
        read_only_fields = ("id",)


class DomCategorySerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomCategory model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomCategorySerializer.
        """

        model = DomCategory
        fields = "__all__"
        read_only_fields = ("id",)


class DomRiskLevelSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomRiskLevel model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomRiskLevelSerializer.
        """

        model = DomRiskLevel
        fields = "__all__"
        read_only_fields = ("id",)


class DomTypeSupplierSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomTypeSupplier model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomTypeSupplierSerializer.
        """

        model = DomTypeSupplier
        fields = "__all__"
        read_only_fields = ("id",)


class DomSupplierSituationSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomSupplierSituation model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomSupplierSituationSerializer.
        """

        model = DomSupplierSituation
        fields = "__all__"
        read_only_fields = ("id",)


class DomPixTypeSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomPixType model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomPixTypeSerializer.
        """

        model = DomPixType
        fields = "__all__"
        read_only_fields = ("id",)


class DomPaymentMethodSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomPaymentMethod model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomPaymentMethodSerializer.
        """

        model = DomPaymentMethod
        fields = "__all__"
        read_only_fields = ("id",)


class DomPayerTypeSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomPayerType model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomPayerTypeSerializer.
        """

        model = DomPayerType
        fields = "__all__"
        read_only_fields = ("id",)


class DomBusinessSectorSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomBusinessSector model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomBusinessSectorSerializer.
        """

        model = DomBusinessSector
        fields = "__all__"
        read_only_fields = ("id",)


class DomTaxpayerClassificationSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomTaxpayerClassification model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomTaxpayerClassificationSerializer.
        """

        model = DomTaxpayerClassification
        fields = "__all__"
        read_only_fields = ("id",)


class DomPublicEntitySerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomPublicEntity model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomPublicEntitySerializer.
        """

        model = DomPublicEntity
        fields = "__all__"
        read_only_fields = ("id",)


class DomIssWithholdingSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomIssWithholding model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomIssWithholdingSerializer.
        """

        model = DomIssWithholding
        fields = "__all__"
        read_only_fields = ("id",)


class DomIssRegimeSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomIssRegime model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomIssRegimeSerializer.
        """

        model = DomIssRegime
        fields = "__all__"
        read_only_fields = ("id",)


class DomWithholdingTaxSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomWithholdingTax model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomWithholdingTaxSerializer.
        """

        model = DomWithholdingTax
        fields = "__all__"
        read_only_fields = ("id",)


class DomCompanySizeSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomCompanySize model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomCompanySizeSerializer.
        """

        model = DomCompanySize
        fields = "__all__"
        read_only_fields = ("id",)


class DomIcmsTaxpayerSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomIcmsTaxpayer model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomIcmsTaxpayerSerializer.
        """

        model = DomIcmsTaxpayer
        fields = "__all__"
        read_only_fields = ("id",)


class DomIncomeTypeSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomIncomeType model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomIncomeTypeSerializer.
        """

        model = DomIncomeType
        fields = "__all__"
        read_only_fields = ("id",)


class DomTaxationMethodSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomTaxationMethod model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomTaxationMethodSerializer.
        """

        model = DomTaxationMethod
        fields = "__all__"
        read_only_fields = ("id",)


class DomCustomerTypeSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomCustomerType model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomCustomerTypeSerializer.
        """

        model = DomCustomerType
        fields = "__all__"
        read_only_fields = ("id",)


class DomTaxationRegimeSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for DomTaxationRegime model.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta configuration for DomTaxationRegimeSerializer.
        """

        model = DomTaxationRegime
        fields = "__all__"
        read_only_fields = ("id",)
