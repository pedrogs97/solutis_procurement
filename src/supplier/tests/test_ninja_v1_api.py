"""Smoke tests for Ninja API v1 endpoints."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from src.supplier.models.approval_workflow import ApprovalStep
from src.supplier.models.attachments import DomAttachmentType
from src.supplier.models.domain import DomBusinessSector, DomCategory, DomTypeSupplier
from src.supplier.models.evaluation import EvaluationCriterion, EvaluationPeriod
from src.supplier.models.responsibility_matrix import ResponsibilityMatrix
from src.supplier.models.supplier import Supplier


def _auth_client() -> APIClient:
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION="Bearer test-token",
        HTTP_X_AUTHENTICATED_USER_ID="1",
        HTTP_X_AUTHENTICATED_USER_EMAIL="tests@solutis.com.br",
        HTTP_X_AUTHENTICATED_USER_FULL_NAME="Test User",
        HTTP_X_AUTHENTICATED_USER_GROUP="Compras",
    )
    return client


@pytest.mark.django_db
def test_ninja_v1_requires_proxy_headers():
    client = APIClient()
    response = client.get("/api/v1/suppliers-list/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_ninja_v1_create_and_list_suppliers():
    baker.make(
        ApprovalStep,
        order=1,
        name="Cadastro inicial",
        description="Validação inicial",
        department="Compras",
        is_mandatory=True,
    )

    client = _auth_client()
    payload = {
        "legalName": "Fornecedor Ninja",
        "taxId": "11122233344499",
    }

    create_response = client.post("/api/v1/suppliers/", payload, format="json")
    assert create_response.status_code == status.HTTP_201_CREATED
    assert create_response.json()["legalName"] == "Fornecedor Ninja"

    list_response = client.get("/api/v1/suppliers-list/")
    assert list_response.status_code == status.HTTP_200_OK
    list_data = list_response.json()
    assert list_data["count"] >= 1
    assert "results" in list_data


@pytest.mark.django_db
def test_ninja_v1_attachments_upload_list_and_download():
    supplier = baker.make(
        Supplier, legal_name="Fornecedor Attach", tax_id="11122233344488"
    )
    attachment_type = baker.make(DomAttachmentType, name="Contrato Social")
    client = _auth_client()

    upload_response = client.post(
        "/api/v1/attachments/upload/",
        {
            "supplier": supplier.pk,
            "attachmentType": attachment_type.pk,
            "description": "Documento teste",
            "file": SimpleUploadedFile(
                "contrato.pdf",
                b"fake-pdf-content",
                content_type="application/pdf",
            ),
        },
    )
    assert upload_response.status_code == status.HTTP_201_CREATED

    list_response = client.get(f"/api/v1/attachments-list/{supplier.pk}/")
    assert list_response.status_code == status.HTTP_200_OK
    list_data = list_response.json()
    assert len(list_data) == 1

    attachment_id = list_data[0]["id"]
    download_response = client.get(f"/api/v1/attachments/{attachment_id}/download/")
    assert download_response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_ninja_v1_approval_endpoints_steps_and_flows():
    step_one = baker.make(
        ApprovalStep,
        order=1,
        name="Cadastro inicial",
        description="Primeira etapa",
        department="Compras",
        is_mandatory=True,
    )
    baker.make(
        ApprovalStep,
        order=2,
        name="Validação",
        description="Segunda etapa",
        department="Financeiro",
        is_mandatory=True,
    )
    supplier = baker.make(
        Supplier, legal_name="Fornecedor Flow", tax_id="11122233344477"
    )
    client = _auth_client()

    start_response = client.post(
        "/api/v1/approval/start/",
        {
            "supplierId": supplier.pk,
            "approverName": "Aprovador Inicial",
            "approverEmail": "aprovador@solutis.com.br",
        },
        format="json",
    )
    assert start_response.status_code == status.HTTP_201_CREATED

    steps_response = client.get("/api/v1/approval/steps/")
    assert steps_response.status_code == status.HTTP_200_OK
    assert any(item["id"] == step_one.pk for item in steps_response.json())

    flows_response = client.get(f"/api/v1/approval/supplier/{supplier.pk}/flows/")
    assert flows_response.status_code == status.HTTP_200_OK
    assert len(flows_response.json()) == 1


@pytest.mark.django_db
def test_ninja_v1_responsibility_matrix_crud_and_delete_blocked():
    supplier = baker.make(
        Supplier, legal_name="Fornecedor Matriz", tax_id="11122233344466"
    )
    client = _auth_client()

    create_response = client.post(
        "/api/v1/responsibility-matrix/",
        {
            "supplier": supplier.pk,
            "contractRequestAdministrative": "R",
            "contractRequestRequestingArea": "A",
        },
        format="json",
    )
    assert create_response.status_code == status.HTTP_201_CREATED

    detail_response = client.get(f"/api/v1/responsibility-matrix/{supplier.pk}/")
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.json()["contractRequestAdministrative"] == "R"

    patch_response = client.patch(
        f"/api/v1/responsibility-matrix/{supplier.pk}/",
        {"contractRequestAdministrative": "A/R"},
        format="json",
    )
    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.json()["contractRequestAdministrative"] == "A/R"

    delete_response = client.delete(f"/api/v1/responsibility-matrix/{supplier.pk}/")
    assert delete_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert ResponsibilityMatrix.objects.filter(supplier=supplier).exists()


@pytest.mark.django_db
def test_ninja_v1_domain_endpoints():
    baker.make(DomBusinessSector, name="Tecnologia")
    client = _auth_client()

    response = client.get("/api/v1/domain/business-sectors/")
    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert isinstance(payload, list)
    assert payload[0]["name"] == "Tecnologia"


@pytest.mark.django_db
def test_ninja_v1_evaluation_endpoints():
    supplier = baker.make(
        Supplier,
        legal_name="Fornecedor Avaliado",
        tax_id="11122233344411",
        category=baker.make(DomCategory, name="Categoria A"),
        type=baker.make(DomTypeSupplier, name="Tipo A"),
    )
    period = EvaluationPeriod.objects.order_by("year", "period_number").first()
    if not period:
        period = baker.make(
            EvaluationPeriod,
            name="Primeiro Quadrimestre 2026",
            start_date="2026-01-01",
            end_date="2026-04-30",
            year=2026,
            period_number=1,
        )
    criterion = baker.make(
        EvaluationCriterion,
        name="Qualidade",
        description="Qualidade do serviço",
        weight="50.00",
        order=1,
    )
    client = _auth_client()

    create_response = client.post(
        "/api/v1/evaluation/evaluations/",
        {
            "supplier": supplier.pk,
            "period": period.pk,
            "evaluatorName": "Avaliador Teste",
            "comments": "Avaliação inicial",
            "criterionScores": [
                {"criterion": criterion.pk, "score": "80.00", "comments": "Bom"}
            ],
        },
        format="json",
    )
    assert create_response.status_code == status.HTTP_201_CREATED

    list_response = client.get("/api/v1/evaluation/evaluations-list/")
    assert list_response.status_code == status.HTTP_200_OK
    list_payload = list_response.json()
    assert list_payload["count"] >= 1

    evaluation_id = list_payload["results"][0]["id"]
    detail_response = client.get(f"/api/v1/evaluation/evaluations/{evaluation_id}/")
    assert detail_response.status_code == status.HTTP_200_OK
    detail_payload = detail_response.json()
    assert detail_payload["supplier"]["id"] == supplier.pk
