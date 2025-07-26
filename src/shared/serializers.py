"""
Serializers for the shared app in Django.
This module contains serializers for common models used across the application.
"""

from typing import Dict

from brazilcep.client import WebService, get_address_from_cep
from brazilcep.exceptions import (
    BrazilCEPException,
    CEPNotFound,
    ConnectionError,
    InvalidCEP,
)
from rest_framework import serializers

from src.shared.mixins import SerializerCamelCaseRepresentationMixin
from src.shared.models import Address, Contact
from src.shared.validation import BaseValidationError


class AddressSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for Address model.
    Converts field names to camelCase representation.
    """

    _LIST_SERVICES = [WebService.APICEP, WebService.VIACEP, WebService.OPENCEP]

    class Meta:
        model = Address
        fields = [
            "id",
            "postal_code",
            "number",
            "complement",
        ]
        read_only_fields = ("id",)

    def __validate_postal_code(self, value: str) -> Dict:
        for service in self._LIST_SERVICES:
            try:
                return get_address_from_cep(value, service)
            except (ConnectionError, BrazilCEPException):
                continue
        raise BaseValidationError(
            "postal_code",
            message="Não foi possível conectar ao serviço de CEP.",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        postal_code = attrs.get("postal_code", "")
        try:
            address: Dict = self.__validate_postal_code(postal_code)
            attrs["street"] = address.get("street", "")
            attrs["neighbourhood"] = address.get("district", "")
            attrs["city"] = address.get("city", "")
            attrs["state"] = address.get("uf", "")
        except InvalidCEP:
            raise BaseValidationError(
                "postal_code",
                message="Formato de CEP inválido.",
            )
        except CEPNotFound:
            raise BaseValidationError("postal_code", message="CEP não encontrado.")
        return attrs


class ContactSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Serializer for Contact model.
    Converts field names to camelCase representation.
    """

    class Meta:
        model = Contact
        fields = ["id", "email", "phone"]
        read_only_fields = ("id",)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        email = attrs.get("email", "")
        if email and not serializers.EmailField().run_validation(email):
            raise BaseValidationError("email", message="Email inválido.")
        return attrs
