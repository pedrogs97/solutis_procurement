"""
URL patterns for domain-related views in the supplier application.
This module defines URL patterns for all domain model list views.
"""

from django.urls import path

from src.supplier.views.domain import (
    DomBusinessSectorListView,
    DomCategoryListView,
    DomClassificationListView,
    DomCompanySizeListView,
    DomCustomerTypeListView,
    DomIcmsTaxpayerListView,
    DomIncomeTypeListView,
    DomIssRegimeListView,
    DomIssWithholdingListView,
    DomPayerTypeListView,
    DomPaymentMethodListView,
    DomPixTypeListView,
    DomPublicEntityListView,
    DomRiskLevelListView,
    DomSupplierSituationListView,
    DomTaxationMethodListView,
    DomTaxationRegimeListView,
    DomTaxpayerClassificationListView,
    DomTypeSupplierListView,
    DomWithholdingTaxListView,
)

urlpatterns = [
    # Domain Classifications
    path(
        "classifications/",
        DomClassificationListView.as_view(),
        name="dom-classification-list",
    ),
    path(
        "categories/",
        DomCategoryListView.as_view(),
        name="dom-category-list",
    ),
    path(
        "risk-levels/",
        DomRiskLevelListView.as_view(),
        name="dom-risk-level-list",
    ),
    # Supplier Types and Situations
    path(
        "supplier-types/",
        DomTypeSupplierListView.as_view(),
        name="dom-supplier-type-list",
    ),
    path(
        "supplier-situations/",
        DomSupplierSituationListView.as_view(),
        name="dom-supplier-situation-list",
    ),
    # Payment Related
    path(
        "pix-types/",
        DomPixTypeListView.as_view(),
        name="dom-pix-type-list",
    ),
    path(
        "payment-methods/",
        DomPaymentMethodListView.as_view(),
        name="dom-payment-method-list",
    ),
    path(
        "payer-types/",
        DomPayerTypeListView.as_view(),
        name="dom-payer-type-list",
    ),
    # Business and Company
    path(
        "business-sectors/",
        DomBusinessSectorListView.as_view(),
        name="dom-business-sector-list",
    ),
    path(
        "company-sizes/",
        DomCompanySizeListView.as_view(),
        name="dom-company-size-list",
    ),
    path(
        "customer-types/",
        DomCustomerTypeListView.as_view(),
        name="dom-customer-type-list",
    ),
    # Tax Related
    path(
        "taxpayer-classifications/",
        DomTaxpayerClassificationListView.as_view(),
        name="dom-taxpayer-classification-list",
    ),
    path(
        "taxation-regimes/",
        DomTaxationRegimeListView.as_view(),
        name="dom-taxation-regime-list",
    ),
    path(
        "taxation-methods/",
        DomTaxationMethodListView.as_view(),
        name="dom-taxation-method-list",
    ),
    path(
        "icms-taxpayers/",
        DomIcmsTaxpayerListView.as_view(),
        name="dom-icms-taxpayer-list",
    ),
    path(
        "withholding-taxes/",
        DomWithholdingTaxListView.as_view(),
        name="dom-withholding-tax-list",
    ),
    # ISS Related
    path(
        "iss-withholdings/",
        DomIssWithholdingListView.as_view(),
        name="dom-iss-withholding-list",
    ),
    path(
        "iss-regimes/",
        DomIssRegimeListView.as_view(),
        name="dom-iss-regime-list",
    ),
    # Income and Public Entity
    path(
        "income-types/",
        DomIncomeTypeListView.as_view(),
        name="dom-income-type-list",
    ),
    path(
        "public-entities/",
        DomPublicEntityListView.as_view(),
        name="dom-public-entity-list",
    ),
]
