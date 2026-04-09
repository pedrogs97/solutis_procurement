"""
Integration tests for supplier create/update endpoints.
"""

from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from src.shared.models import Contact
from src.supplier.models.approval_workflow import ApprovalStep
from src.supplier.models.attachments import SupplierAttachment
from src.supplier.models.domain import DomAttachmentType, DomRiskLevel
from src.supplier.models.supplier import Supplier


def _build_authenticated_client() -> APIClient:
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
@patch("src.shared.serializers.get_address_from_cep")
def test_create_supplier_allows_missing_optional_nested_blocks(mock_get_address):
    """
    Supplier creation should work even when optional nested blocks are omitted.
    """
    mock_get_address.return_value = {
        "street": "Avenida Paulista",
        "district": "Bela Vista",
        "city": "São Paulo",
        "uf": "SP",
    }

    baker.make(
        ApprovalStep,
        order=1,
        name="Cadastro inicial",
        description="Validação inicial",
        department="Compras",
        is_mandatory=True,
    )

    client = _build_authenticated_client()
    payload = {
        "legalName": "Fornecedor API",
        "taxId": "11122233344455",
        "address": {
            "postalCode": "01310100",
            "number": 123,
            "street": "",
            "neighbourhood": "",
            "city": "",
            "state": "",
            "complement": "",
        },
        "contact": {
            "name": "Contato Teste",
            "phone": "11999999999",
            "email": "fornecedor.api@solutis.com.br",
        },
        "contract": {
            "hasContractRenewal": False,
            "warningContractRenewal": False,
            "warningOnTermination": False,
            "warningOnRenewal": False,
            "warningOnPeriod": False,
        },
        "fiscalDetails": {
            "issTaxpayer": False,
            "simplesNacionalParticipant": False,
            "cooperativeMember": False,
        },
        "companyInformation": {},
    }

    response = client.post("/api/suppliers/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["legalName"] == "Fornecedor API"
    assert response.data["paymentDetails"] is None
    assert response.data["organizationalDetails"] is None


@pytest.mark.django_db
def test_patch_supplier_allows_clearing_contact_email():
    """
    Supplier update should allow clearing optional string fields.
    """
    contact = baker.make(
        Contact, name="Contato", email="old.email@solutis.com.br", phone="11999999999"
    )
    supplier = baker.make(
        Supplier,
        legal_name="Fornecedor Patch LTDA",
        tax_id="11122233344456",
        contact=contact,
    )

    client = _build_authenticated_client()
    payload = {
        "contact": {
            "name": "Contato",
            "phone": "11999999999",
            "email": "",
        }
    }

    response = client.patch(f"/api/suppliers/{supplier.pk}/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    supplier.refresh_from_db()
    assert supplier.contact.email == ""


@pytest.mark.django_db
@patch("src.shared.serializers.get_address_from_cep")
def test_create_supplier_accepts_responsible_manager(mock_get_address):
    """
    Supplier creation should accept the new responsible manager field while keeping legacy fields optional.
    """
    mock_get_address.return_value = {
        "street": "Avenida Paulista",
        "district": "Bela Vista",
        "city": "São Paulo",
        "uf": "SP",
    }

    baker.make(
        ApprovalStep,
        order=1,
        name="Cadastro inicial",
        description="Validação inicial",
        department="Compras",
        is_mandatory=True,
    )

    client = _build_authenticated_client()
    payload = {
        "legalName": "Fornecedor com gestor",
        "taxId": "11122233344459",
        "address": {
            "postalCode": "01310100",
            "number": 123,
            "street": "",
            "neighbourhood": "",
            "city": "",
            "state": "",
            "complement": "",
        },
        "contact": {
            "name": "Contato Teste",
            "phone": "11999999999",
            "email": "gestor@solutis.com.br",
        },
        "organizationalDetails": {
            "costCenter": "CC-001",
            "businessUnit": "TI",
            "responsibleExecutive": "Maria Silva",
            "responsibleManager": "João Souza",
        },
    }

    response = client.post("/api/suppliers/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["organizationalDetails"]["responsibleManager"] == "João Souza"


@pytest.mark.django_db
@patch("src.shared.serializers.get_address_from_cep")
def test_create_supplier_accepts_payload_without_hidden_front_fields(mock_get_address):
    """
    Supplier creation should work when the frontend omits the fields hidden from the new UI.
    """
    mock_get_address.return_value = {
        "street": "Avenida Paulista",
        "district": "Bela Vista",
        "city": "São Paulo",
        "uf": "SP",
    }

    baker.make(
        ApprovalStep,
        order=1,
        name="Cadastro inicial",
        description="Validação inicial",
        department="Compras",
        is_mandatory=True,
    )

    client = _build_authenticated_client()
    payload = {
        "legalName": "Fornecedor sem campos ocultos",
        "taxId": "11122233344460",
        "address": {
            "postalCode": "01310100",
            "number": 123,
            "street": "",
            "neighbourhood": "",
            "city": "",
            "state": "",
            "complement": "",
        },
        "contact": {
            "name": "Contato Teste",
            "phone": "11999999999",
            "email": "sem-campos-ocultos@solutis.com.br",
        },
        "organizationalDetails": {
            "costCenter": "CC-001",
            "businessUnit": "TI",
            "responsibleExecutive": "Maria Silva",
            "responsibleManager": "João Souza",
            "businessSector": None,
        },
        "fiscalDetails": {
            "simplesNacionalParticipant": False,
        },
        "companyInformation": {
            "companySize": None,
        },
        "contract": {
            "hasContractRenewal": False,
            "warningContractRenewal": False,
            "warningOnTermination": False,
            "warningOnRenewal": False,
            "warningOnPeriod": False,
        },
    }

    response = client.post("/api/suppliers/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["organizationalDetails"]["responsibleManager"] == "João Souza"
    assert response.data["organizationalDetails"]["payerType"] is None
    assert response.data["organizationalDetails"]["taxpayerClassification"] is None
    assert response.data["organizationalDetails"]["publicEntity"] is None
    assert response.data["fiscalDetails"]["issWithholding"] is None
    assert response.data["fiscalDetails"]["issRegime"] is None
    assert response.data["fiscalDetails"]["withholdingTaxNature"] is None
    assert response.data["companyInformation"]["taxationRegime"] is None
    assert response.data["companyInformation"]["icmsTaxpayer"] is None
    assert response.data["companyInformation"]["incomeType"] is None
    assert response.data["companyInformation"]["taxationMethod"] is None
    assert response.data["companyInformation"]["customerType"] is None


@pytest.mark.django_db
def test_create_supplier_without_approval_steps_returns_validation_error():
    """
    Supplier creation should return validation error (not 500) when no approval steps exist.
    """
    ApprovalStep.objects.all().delete()

    client = _build_authenticated_client()
    payload = {
        "legalName": "Fornecedor sem fluxo de aprovação",
        "taxId": "11122233344457",
    }

    response = client.post("/api/suppliers/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "approvalWorkflow" in response.data
    assert "Nenhum passo de aprovação definido." in response.data["approvalWorkflow"][0]
    assert not Supplier.objects.filter(legal_name=payload["legalName"]).exists()


@pytest.mark.django_db
def test_attachment_list_returns_attachment_type_id_for_frontend_mapping():
    """
    Attachment list response should include attachmentTypeId for deterministic mapping on edit.
    """
    risk_level = baker.make(DomRiskLevel, name="Baixo")
    attachment_type = baker.make(
        DomAttachmentType,
        name="Contrato Social",
        risk_level=risk_level,
    )
    supplier = baker.make(
        Supplier,
        legal_name="Fornecedor com anexo",
        tax_id="11122233344458",
    )
    test_file = SimpleUploadedFile(
        "contrato-social.pdf", b"fake-pdf-content", content_type="application/pdf"
    )
    baker.make(
        SupplierAttachment,
        supplier=supplier,
        attachment_type=attachment_type,
        file=test_file,
        description="Documento principal",
    )

    client = _build_authenticated_client()
    response = client.get(f"/api/attachments-list/{supplier.pk}/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["attachmentTypeId"] == attachment_type.pk
