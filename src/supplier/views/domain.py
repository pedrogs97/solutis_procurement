"""
Views for domain models in the supplier application.
This module provides list views for all domain-related models.
"""

from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

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


class DomainPagination(PageNumberPagination):
    """
    Custom pagination for domain lists.
    """

    page_size = None  # No pagination - return all results
    page_size_query_param = None


class DomClassificationListView(ListAPIView):
    """
    List view for DomClassification model.
    Returns all classification records without pagination or filtering.
    """

    queryset = DomClassification.objects.all().order_by("name")
    serializer_class = DomClassificationSerializer
    pagination_class = DomainPagination


class DomCategoryListView(ListAPIView):
    """
    List view for DomCategory model.
    Returns all category records without pagination or filtering.
    """

    queryset = DomCategory.objects.all().order_by("name")
    serializer_class = DomCategorySerializer
    pagination_class = DomainPagination


class DomRiskLevelListView(ListAPIView):
    """
    List view for DomRiskLevel model.
    Returns all risk level records without pagination or filtering.
    """

    queryset = DomRiskLevel.objects.all().order_by("name")
    serializer_class = DomRiskLevelSerializer
    pagination_class = DomainPagination


class DomTypeSupplierListView(ListAPIView):
    """
    List view for DomTypeSupplier model.
    Returns all supplier type records without pagination or filtering.
    """

    queryset = DomTypeSupplier.objects.all().order_by("name")
    serializer_class = DomTypeSupplierSerializer
    pagination_class = DomainPagination


class DomSupplierSituationListView(ListAPIView):
    """
    List view for DomSupplierSituation model.
    Returns all supplier situation records without pagination or filtering.
    """

    queryset = DomSupplierSituation.objects.all().order_by("name")
    serializer_class = DomSupplierSituationSerializer
    pagination_class = DomainPagination


class DomPixTypeListView(ListAPIView):
    """
    List view for DomPixType model.
    Returns all PIX type records without pagination or filtering.
    """

    queryset = DomPixType.objects.all().order_by("name")
    serializer_class = DomPixTypeSerializer
    pagination_class = DomainPagination


class DomPaymentMethodListView(ListAPIView):
    """
    List view for DomPaymentMethod model.
    Returns all payment method records without pagination or filtering.
    """

    queryset = DomPaymentMethod.objects.all().order_by("name")
    serializer_class = DomPaymentMethodSerializer
    pagination_class = DomainPagination


class DomPayerTypeListView(ListAPIView):
    """
    List view for DomPayerType model.
    Returns all payer type records without pagination or filtering.
    """

    queryset = DomPayerType.objects.all().order_by("name")
    serializer_class = DomPayerTypeSerializer
    pagination_class = DomainPagination


class DomBusinessSectorListView(ListAPIView):
    """
    List view for DomBusinessSector model.
    Returns all business sector records without pagination or filtering.
    """

    queryset = DomBusinessSector.objects.all().order_by("name")
    serializer_class = DomBusinessSectorSerializer
    pagination_class = DomainPagination


class DomTaxpayerClassificationListView(ListAPIView):
    """
    List view for DomTaxpayerClassification model.
    Returns all taxpayer classification records without pagination or filtering.
    """

    queryset = DomTaxpayerClassification.objects.all().order_by("name")
    serializer_class = DomTaxpayerClassificationSerializer
    pagination_class = DomainPagination


class DomPublicEntityListView(ListAPIView):
    """
    List view for DomPublicEntity model.
    Returns all public entity records without pagination or filtering.
    """

    queryset = DomPublicEntity.objects.all().order_by("name")
    serializer_class = DomPublicEntitySerializer
    pagination_class = DomainPagination


class DomIssWithholdingListView(ListAPIView):
    """
    List view for DomIssWithholding model.
    Returns all ISS withholding records without pagination or filtering.
    """

    queryset = DomIssWithholding.objects.all().order_by("name")
    serializer_class = DomIssWithholdingSerializer
    pagination_class = DomainPagination


class DomIssRegimeListView(ListAPIView):
    """
    List view for DomIssRegime model.
    Returns all ISS regime records without pagination or filtering.
    """

    queryset = DomIssRegime.objects.all().order_by("name")
    serializer_class = DomIssRegimeSerializer
    pagination_class = DomainPagination


class DomWithholdingTaxListView(ListAPIView):
    """
    List view for DomWithholdingTax model.
    Returns all withholding tax records without pagination or filtering.
    """

    queryset = DomWithholdingTax.objects.all().order_by("name")
    serializer_class = DomWithholdingTaxSerializer
    pagination_class = DomainPagination


class DomCompanySizeListView(ListAPIView):
    """
    List view for DomCompanySize model.
    Returns all company size records without pagination or filtering.
    """

    queryset = DomCompanySize.objects.all().order_by("name")
    serializer_class = DomCompanySizeSerializer
    pagination_class = DomainPagination


class DomIcmsTaxpayerListView(ListAPIView):
    """
    List view for DomIcmsTaxpayer model.
    Returns all ICMS taxpayer records without pagination or filtering.
    """

    queryset = DomIcmsTaxpayer.objects.all().order_by("name")
    serializer_class = DomIcmsTaxpayerSerializer
    pagination_class = DomainPagination


class DomIncomeTypeListView(ListAPIView):
    """
    List view for DomIncomeType model.
    Returns all income type records without pagination or filtering.
    """

    queryset = DomIncomeType.objects.all().order_by("name")
    serializer_class = DomIncomeTypeSerializer
    pagination_class = DomainPagination


class DomTaxationMethodListView(ListAPIView):
    """
    List view for DomTaxationMethod model.
    Returns all taxation method records without pagination or filtering.
    """

    queryset = DomTaxationMethod.objects.all().order_by("name")
    serializer_class = DomTaxationMethodSerializer
    pagination_class = DomainPagination


class DomCustomerTypeListView(ListAPIView):
    """
    List view for DomCustomerType model.
    Returns all customer type records without pagination or filtering.
    """

    queryset = DomCustomerType.objects.all().order_by("name")
    serializer_class = DomCustomerTypeSerializer
    pagination_class = DomainPagination


class DomTaxationRegimeListView(ListAPIView):
    """
    List view for DomTaxationRegime model.
    Returns all taxation regime records without pagination or filtering.
    """

    queryset = DomTaxationRegime.objects.all().order_by("name")
    serializer_class = DomTaxationRegimeSerializer
    pagination_class = DomainPagination
