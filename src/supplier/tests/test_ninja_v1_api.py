"""Smoke tests for Ninja API v1 endpoints."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from src.supplier.models.approval_workflow import ApprovalStep
from src.supplier.models.attachments import DomAttachmentType
from src.supplier.models.domain import (
    DomBusinessSector,
    DomCategory,
    DomClassification,
    DomCompanySize,
    DomPaymentMethod,
    DomPixType,
    DomRiskLevel,
    DomTypeSupplier,
)
from src.supplier.models.evaluation import EvaluationCriterion
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


def _read_streaming_response(response) -> bytes:
    return b"".join(response.streaming_content)


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
    create_data = create_response.json()
    assert create_data["legalName"] == "Fornecedor Ninja"
    assert create_data["responsibilityMatrix"] is not None
    assert ResponsibilityMatrix.objects.filter(
        supplier_id=create_data["id"],
    ).exists()

    list_response = client.get("/api/v1/suppliers-list/")
    assert list_response.status_code == status.HTTP_200_OK
    list_data = list_response.json()
    assert list_data["count"] >= 1
    assert "results" in list_data


@pytest.mark.django_db
def test_ninja_v1_supplier_openapi_contract_is_explicit():
    client = APIClient()

    response = client.get("/api/v1/openapi.json")

    assert response.status_code == status.HTTP_200_OK
    spec = response.json()
    supplier_collection = spec["paths"]["/api/v1/suppliers/"]
    supplier_detail = spec["paths"]["/api/v1/suppliers/{pk}/"]
    supplier_list = spec["paths"]["/api/v1/suppliers-list/"]

    assert supplier_collection["post"]["operationId"] == "createSupplier"
    assert (
        spec["paths"]["/api/v1/domain/risk-levels/"]["get"]["operationId"]
        == "listRiskLevels"
    )
    assert (
        supplier_collection["post"]["responses"]["201"]["content"]["application/json"][
            "schema"
        ]["$ref"]
        == "#/components/schemas/SupplierOut"
    )
    assert supplier_detail["patch"]["operationId"] == "patchSupplier"
    assert (
        supplier_detail["patch"]["responses"]["200"]["content"]["application/json"][
            "schema"
        ]["$ref"]
        == "#/components/schemas/SupplierOut"
    )
    assert (
        supplier_list["get"]["responses"]["200"]["content"]["application/json"][
            "schema"
        ]["$ref"]
        == "#/components/schemas/PaginatedSupplierListOut"
    )

    create_schema = spec["components"]["schemas"]["SupplierCreateIn"]
    out_schema = spec["components"]["schemas"]["SupplierOut"]
    assert "riskLevel" in create_schema["properties"]
    assert "riskLevel" in out_schema["properties"]
    assert "paymentDetails" in out_schema["properties"]


@pytest.mark.django_db
def test_ninja_v1_supplier_create_and_patch_persist_select_fields_after_middleware():
    baker.make(
        ApprovalStep,
        order=1,
        name="Cadastro inicial",
        description="Validação inicial",
        department="Compras",
        is_mandatory=True,
    )

    classification = baker.make(DomClassification, name="Fornecedor")
    classification_2 = baker.make(DomClassification, name="Parceiro")
    category = baker.make(DomCategory, name="Servico")
    category_2 = baker.make(DomCategory, name="Produto")
    risk_level_1 = baker.make(DomRiskLevel, name="Baixo")
    risk_level_2 = baker.make(DomRiskLevel, name="Alto")
    supplier_type = baker.make(DomTypeSupplier, name="Pessoa Juridica")
    supplier_type_2 = baker.make(DomTypeSupplier, name="Pessoa Fisica")
    business_sector = baker.make(DomBusinessSector, name="Tecnologia")
    business_sector_2 = baker.make(DomBusinessSector, name="Consultoria")
    company_size = baker.make(DomCompanySize, name="Grande")
    company_size_2 = baker.make(DomCompanySize, name="Media")
    payment_method = baker.make(DomPaymentMethod, name="PIX")
    payment_method_2 = baker.make(DomPaymentMethod, name="Boleto")
    pix_type = baker.make(DomPixType, name="CNPJ")
    pix_type_2 = baker.make(DomPixType, name="E-mail")

    client = _auth_client()
    payload = {
        "legalName": "Fornecedor Selects",
        "taxId": "11122233344477",
        "classification": classification.pk,
        "category": category.pk,
        "riskLevel": risk_level_1.pk,
        "type": supplier_type.pk,
        "organizationalDetails": {
            "businessSector": business_sector.pk,
        },
        "companyInformation": {
            "companySize": company_size.pk,
        },
        "paymentDetails": {
            "paymentMethod": payment_method.pk,
            "pixKeyType": pix_type.pk,
            "paymentDate": "05 de cada mês",
        },
    }

    create_response = client.post("/api/v1/suppliers/", payload, format="json")
    assert create_response.status_code == status.HTTP_201_CREATED
    created_payload = create_response.json()
    supplier_id = created_payload["id"]

    assert created_payload["classification"]["id"] == classification.pk
    assert created_payload["category"]["id"] == category.pk
    assert created_payload["riskLevel"]["id"] == risk_level_1.pk
    assert created_payload["type"]["id"] == supplier_type.pk
    assert (
        created_payload["organizationalDetails"]["businessSector"] == business_sector.pk
    )
    assert created_payload["companyInformation"]["companySize"] == company_size.pk
    assert created_payload["paymentDetails"]["paymentMethod"] == payment_method.pk
    assert created_payload["paymentDetails"]["pixKeyType"] == pix_type.pk
    assert created_payload["paymentDetails"]["paymentDate"] == "05 de cada mês"

    patch_response = client.patch(
        f"/api/v1/suppliers/{supplier_id}/",
        {
            "classification": classification_2.pk,
            "category": category_2.pk,
            "riskLevel": risk_level_2.pk,
            "type": supplier_type_2.pk,
            "organizationalDetails": {
                "businessSector": business_sector_2.pk,
            },
            "companyInformation": {
                "companySize": company_size_2.pk,
            },
            "paymentDetails": {
                "paymentMethod": payment_method_2.pk,
                "pixKeyType": pix_type_2.pk,
                "paymentDate": "Dia 10",
            },
        },
        format="json",
    )

    assert patch_response.status_code == status.HTTP_200_OK
    patched_payload = patch_response.json()
    assert patched_payload["classification"]["id"] == classification_2.pk
    assert patched_payload["category"]["id"] == category_2.pk
    assert patched_payload["riskLevel"]["id"] == risk_level_2.pk
    assert patched_payload["type"]["id"] == supplier_type_2.pk
    assert (
        patched_payload["organizationalDetails"]["businessSector"]
        == business_sector_2.pk
    )
    assert patched_payload["companyInformation"]["companySize"] == company_size_2.pk
    assert patched_payload["paymentDetails"]["paymentMethod"] == payment_method_2.pk
    assert patched_payload["paymentDetails"]["pixKeyType"] == pix_type_2.pk
    assert patched_payload["paymentDetails"]["paymentDate"] == "Dia 10"

    supplier = Supplier.objects.get(pk=supplier_id)
    assert supplier.classification_id == classification_2.pk
    assert supplier.category_id == category_2.pk
    assert supplier.risk_level_id == risk_level_2.pk
    assert supplier.type_id == supplier_type_2.pk
    assert supplier.organizational_details.business_sector_id == business_sector_2.pk
    assert supplier.company_information.company_size_id == company_size_2.pk
    assert supplier.payment_details.payment_method_id == payment_method_2.pk
    assert supplier.payment_details.pix_key_type_id == pix_type_2.pk
    assert supplier.payment_details.payment_date == "Dia 10"


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
def test_ninja_v1_attachment_history_by_type():
    supplier = baker.make(
        Supplier, legal_name="Fornecedor Historico", tax_id="11122233344433"
    )
    attachment_type = baker.make(DomAttachmentType, name="Comprovante")
    client = _auth_client()

    first_upload = client.post(
        "/api/v1/attachments/upload/",
        {
            "supplier": supplier.pk,
            "attachmentType": attachment_type.pk,
            "description": "Versao 1",
            "file": SimpleUploadedFile(
                "comprovante-v1.pdf",
                b"fake-content-v1",
                content_type="application/pdf",
            ),
        },
    )
    assert first_upload.status_code == status.HTTP_201_CREATED

    second_upload = client.post(
        "/api/v1/attachments/upload/",
        {
            "supplier": supplier.pk,
            "attachmentType": attachment_type.pk,
            "description": "Versao 2",
            "file": SimpleUploadedFile(
                "comprovante-v2.pdf",
                b"fake-content-v2",
                content_type="application/pdf",
            ),
        },
    )
    assert second_upload.status_code == status.HTTP_201_CREATED

    history_response = client.get(
        f"/api/v1/attachments/history/{supplier.pk}/{attachment_type.pk}/"
    )
    assert history_response.status_code == status.HTTP_200_OK
    versions = history_response.json()
    assert len(versions) == 2
    assert versions[0]["isCurrent"] is True
    assert versions[0]["source"] == "current"
    assert versions[0]["downloadId"] == versions[0]["id"]
    assert versions[0]["description"] == "Versao 2"
    assert versions[1]["isCurrent"] is False
    assert versions[1]["source"] == "history"
    assert versions[1]["downloadId"] == versions[1]["id"]
    assert versions[1]["description"] == "Versao 1"

    history_id = versions[1]["id"]
    history_download = client.get(f"/api/v1/attachments/history-download/{history_id}/")
    assert history_download.status_code == status.HTTP_200_OK
    assert _read_streaming_response(history_download) == b"fake-content-v1"


@pytest.mark.django_db
def test_ninja_v1_attachment_type_crud():
    risk_level = baker.make(DomRiskLevel, name="Alto")
    client = _auth_client()

    create_response = client.post(
        "/api/v1/attachment-types/",
        {"name": "Comprovante Fiscal", "riskLevel": risk_level.pk},
        format="json",
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    created_payload = create_response.json()
    assert created_payload["name"] == "Comprovante Fiscal"
    assert created_payload["riskLevel"] == risk_level.pk

    attachment_type_id = created_payload["id"]
    patch_response = client.patch(
        f"/api/v1/attachment-types/{attachment_type_id}/",
        {"name": "Comprovante Fiscal Atualizado"},
        format="json",
    )
    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.json()["name"] == "Comprovante Fiscal Atualizado"

    delete_response = client.delete(f"/api/v1/attachment-types/{attachment_type_id}/")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_ninja_v1_attachment_type_rejects_invalid_risk_level():
    client = _auth_client()

    response = client.post(
        "/api/v1/attachment-types/",
        {"name": "Comprovante Invalido", "riskLevel": 9999999},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Nivel de risco nao encontrado." in response.json()["detail"]


@pytest.mark.django_db
def test_ninja_v1_attachment_type_delete_rejects_when_in_use():
    supplier = baker.make(
        Supplier, legal_name="Fornecedor Attach Delete", tax_id="11122233344455"
    )
    attachment_type = baker.make(DomAttachmentType, name="Documento Uso")
    client = _auth_client()

    upload_response = client.post(
        "/api/v1/attachments/upload/",
        {
            "supplier": supplier.pk,
            "attachmentType": attachment_type.pk,
            "description": "Documento em uso",
            "file": SimpleUploadedFile(
                "documento.pdf",
                b"fake-content",
                content_type="application/pdf",
            ),
        },
    )
    assert upload_response.status_code == status.HTTP_201_CREATED

    delete_response = client.delete(f"/api/v1/attachment-types/{attachment_type.pk}/")
    assert delete_response.status_code == status.HTTP_400_BAD_REQUEST


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

    upsert_response = client.post(
        "/api/v1/responsibility-matrix/",
        {
            "supplier": supplier.pk,
            "contractRequestAdministrative": "C",
        },
        format="json",
    )
    assert upsert_response.status_code == status.HTTP_200_OK
    assert upsert_response.json()["contractRequestAdministrative"] == "C"

    detail_response = client.get(f"/api/v1/responsibility-matrix/{supplier.pk}/")
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.json()["contractRequestAdministrative"] == "C"

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
            "evaluationYear": 2026,
            "periodType": "QUADRIMESTER",
            "periodNumber": 1,
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
    assert detail_payload["evaluationYear"] == 2026
    assert detail_payload["periodType"] == "QUADRIMESTER"
    assert detail_payload["periodNumber"] == 1


@pytest.mark.django_db
def test_ninja_v1_evaluation_rejects_mixed_period_type_same_supplier_year():
    supplier = baker.make(
        Supplier,
        legal_name="Fornecedor Misto",
        tax_id="11122233344888",
        category=baker.make(DomCategory, name="Categoria Misto"),
        type=baker.make(DomTypeSupplier, name="Tipo Misto"),
    )
    criterion = baker.make(
        EvaluationCriterion,
        name="Atendimento",
        description="Qualidade do atendimento",
        weight="40.00",
        order=2,
    )
    client = _auth_client()

    first_response = client.post(
        "/api/v1/evaluation/evaluations/",
        {
            "supplier": supplier.pk,
            "evaluationYear": 2026,
            "periodType": "SEMESTER",
            "periodNumber": 1,
            "evaluatorName": "Avaliador 1",
            "criterionScores": [
                {"criterion": criterion.pk, "score": "70.00", "comments": "ok"}
            ],
        },
        format="json",
    )
    assert first_response.status_code == status.HTTP_201_CREATED

    second_response = client.post(
        "/api/v1/evaluation/evaluations/",
        {
            "supplier": supplier.pk,
            "evaluationYear": 2026,
            "periodType": "QUADRIMESTER",
            "periodNumber": 2,
            "evaluatorName": "Avaliador 2",
        },
        format="json",
    )

    assert second_response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_ninja_v1_evaluation_create_with_evaluation_date_returns_iso_string():
    """POST with evaluationDate must not raise AttributeError on serialization."""
    supplier = baker.make(
        Supplier,
        legal_name="Fornecedor Com Data",
        tax_id="11122233300001",
        category=baker.make(DomCategory, name="Categoria Data"),
        type=baker.make(DomTypeSupplier, name="Tipo Data"),
    )
    client = _auth_client()

    response = client.post(
        "/api/v1/evaluation/evaluations/",
        {
            "supplier": supplier.pk,
            "evaluationYear": 2026,
            "periodType": "QUADRIMESTER",
            "periodNumber": 1,
            "evaluatorName": "Avaliador Data",
            "evaluationDate": "2026-04-14",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["evaluationDate"] == "2026-04-14"


@pytest.mark.django_db
def test_ninja_v1_evaluation_put_with_evaluation_date_no_attribute_error():
    """PUT with evaluationDate must not raise AttributeError on serialization."""
    supplier = baker.make(
        Supplier,
        legal_name="Fornecedor PUT Data",
        tax_id="11122233300002",
        category=baker.make(DomCategory, name="Categoria PUT"),
        type=baker.make(DomTypeSupplier, name="Tipo PUT"),
    )
    client = _auth_client()

    create_response = client.post(
        "/api/v1/evaluation/evaluations/",
        {
            "supplier": supplier.pk,
            "evaluationYear": 2026,
            "periodType": "SEMESTER",
            "periodNumber": 1,
            "evaluatorName": "Avaliador PUT",
        },
        format="json",
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    evaluation_id = create_response.json()["id"]

    put_response = client.put(
        f"/api/v1/evaluation/evaluations/{evaluation_id}/",
        {
            "supplier": supplier.pk,
            "evaluationYear": 2026,
            "periodType": "SEMESTER",
            "periodNumber": 1,
            "evaluatorName": "Avaliador PUT Atualizado",
            "evaluationDate": "2026-03-01",
        },
        format="json",
    )
    assert put_response.status_code == status.HTTP_200_OK
    assert put_response.json()["evaluationDate"] == "2026-03-01"


@pytest.mark.django_db
def test_ninja_v1_evaluation_patch_with_evaluation_date_no_attribute_error():
    """PATCH with evaluationDate must not raise AttributeError on serialization."""
    supplier = baker.make(
        Supplier,
        legal_name="Fornecedor PATCH Data",
        tax_id="11122233300003",
        category=baker.make(DomCategory, name="Categoria PATCH"),
        type=baker.make(DomTypeSupplier, name="Tipo PATCH"),
    )
    client = _auth_client()

    create_response = client.post(
        "/api/v1/evaluation/evaluations/",
        {
            "supplier": supplier.pk,
            "evaluationYear": 2026,
            "periodType": "SEMESTER",
            "periodNumber": 2,
            "evaluatorName": "Avaliador PATCH",
        },
        format="json",
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    evaluation_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/api/v1/evaluation/evaluations/{evaluation_id}/",
        {"evaluationDate": "2026-02-15"},
        format="json",
    )
    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.json()["evaluationDate"] == "2026-02-15"


@pytest.mark.django_db
def test_legacy_drf_supplier_routes_are_not_exposed_anymore():
    client = _auth_client()

    legacy_paths = [
        "/api/suppliers-list/",
        "/api/domain/business-sectors/",
        "/api/evaluation/evaluations-list/",
        "/api/approval/steps/",
        "/api/attachments-list/1/",
        "/api/responsibility-matrix/1/",
    ]

    for path in legacy_paths:
        response = client.get(path)
        assert response.status_code == status.HTTP_404_NOT_FOUND
