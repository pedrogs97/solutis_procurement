"""
Serializer for SupplierAttachment model.
This module provides serializers for output representations of the SupplierAttachment model.
"""

from src.shared.serializers import BaseSerializer
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
    DomPendencyType,
    DomWithholdingTax,
)


class DomClassificationSerializer(BaseSerializer):
    """
    Serializer for DomClassification model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomClassificationSerializer.
        """

        model = DomClassification
        fields = "__all__"
        read_only_fields = ("id",)


class DomCategorySerializer(BaseSerializer):
    """
    Serializer for DomCategory model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomCategorySerializer.
        """

        model = DomCategory
        fields = "__all__"
        read_only_fields = ("id",)


class DomRiskLevelSerializer(BaseSerializer):
    """
    Serializer for DomRiskLevel model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomRiskLevelSerializer.
        """

        model = DomRiskLevel
        fields = "__all__"
        read_only_fields = ("id",)


class DomTypeSupplierSerializer(BaseSerializer):
    """
    Serializer for DomTypeSupplier model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomTypeSupplierSerializer.
        """

        model = DomTypeSupplier
        fields = "__all__"
        read_only_fields = ("id",)


class DomPendencyTypeSerializer(BaseSerializer):
    """
    Serializer for DomPendencyType model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomPendencyTypeSerializer.
        """

        model = DomPendencyType
        fields = "__all__"
        read_only_fields = ("id",)


class DomSupplierSituationSerializer(BaseSerializer):
    """
    Serializer for DomSupplierSituation model.
    Converts field names to camelCase representation.
    """

    pendency_type = DomPendencyTypeSerializer()

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomSupplierSituationSerializer.
        """

        model = DomSupplierSituation
        fields = "__all__"
        read_only_fields = ("id",)


class DomPixTypeSerializer(BaseSerializer):
    """
    Serializer for DomPixType model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomPixTypeSerializer.
        """

        model = DomPixType
        fields = "__all__"
        read_only_fields = ("id",)


class DomPaymentMethodSerializer(BaseSerializer):
    """
    Serializer for DomPaymentMethod model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomPaymentMethodSerializer.
        """

        model = DomPaymentMethod
        fields = "__all__"
        read_only_fields = ("id",)


class DomPayerTypeSerializer(BaseSerializer):
    """
    Serializer for DomPayerType model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomPayerTypeSerializer.
        """

        model = DomPayerType
        fields = "__all__"
        read_only_fields = ("id",)


class DomBusinessSectorSerializer(BaseSerializer):
    """
    Serializer for DomBusinessSector model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomBusinessSectorSerializer.
        """

        model = DomBusinessSector
        fields = "__all__"
        read_only_fields = ("id",)


class DomTaxpayerClassificationSerializer(BaseSerializer):
    """
    Serializer for DomTaxpayerClassification model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomTaxpayerClassificationSerializer.
        """

        model = DomTaxpayerClassification
        fields = "__all__"
        read_only_fields = ("id",)


class DomPublicEntitySerializer(BaseSerializer):
    """
    Serializer for DomPublicEntity model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomPublicEntitySerializer.
        """

        model = DomPublicEntity
        fields = "__all__"
        read_only_fields = ("id",)


class DomIssWithholdingSerializer(BaseSerializer):
    """
    Serializer for DomIssWithholding model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomIssWithholdingSerializer.
        """

        model = DomIssWithholding
        fields = "__all__"
        read_only_fields = ("id",)


class DomIssRegimeSerializer(BaseSerializer):
    """
    Serializer for DomIssRegime model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomIssRegimeSerializer.
        """

        model = DomIssRegime
        fields = "__all__"
        read_only_fields = ("id",)


class DomWithholdingTaxSerializer(BaseSerializer):
    """
    Serializer for DomWithholdingTax model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomWithholdingTaxSerializer.
        """

        model = DomWithholdingTax
        fields = "__all__"
        read_only_fields = ("id",)


class DomCompanySizeSerializer(BaseSerializer):
    """
    Serializer for DomCompanySize model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomCompanySizeSerializer.
        """

        model = DomCompanySize
        fields = "__all__"
        read_only_fields = ("id",)


class DomIcmsTaxpayerSerializer(BaseSerializer):
    """
    Serializer for DomIcmsTaxpayer model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomIcmsTaxpayerSerializer.
        """

        model = DomIcmsTaxpayer
        fields = "__all__"
        read_only_fields = ("id",)


class DomIncomeTypeSerializer(BaseSerializer):
    """
    Serializer for DomIncomeType model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomIncomeTypeSerializer.
        """

        model = DomIncomeType
        fields = "__all__"
        read_only_fields = ("id",)


class DomTaxationMethodSerializer(BaseSerializer):
    """
    Serializer for DomTaxationMethod model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomTaxationMethodSerializer.
        """

        model = DomTaxationMethod
        fields = "__all__"
        read_only_fields = ("id",)


class DomCustomerTypeSerializer(BaseSerializer):
    """
    Serializer for DomCustomerType model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomCustomerTypeSerializer.
        """

        model = DomCustomerType
        fields = "__all__"
        read_only_fields = ("id",)


class DomTaxationRegimeSerializer(BaseSerializer):
    """
    Serializer for DomTaxationRegime model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta configuration for DomTaxationRegimeSerializer.
        """

        model = DomTaxationRegime
        fields = "__all__"
        read_only_fields = ("id",)
