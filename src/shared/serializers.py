"""
Serializers for the shared app in Django.
This module contains serializers for common models used across the application.
"""

from typing import Dict

from brazilcep.client import WebService, get_address_from_cep
from brazilcep.exceptions import (BrazilCEPException, CEPNotFound,
                                  ConnectionError, InvalidCEP)
from rest_framework import serializers
from src.shared.mixins import SerializerCamelCaseRepresentationMixin
from src.shared.models import Address, Contact
from src.shared.validation import BaseValidationError


class BaseSerializer(
    SerializerCamelCaseRepresentationMixin, serializers.ModelSerializer
):
    """
    Base serializer class for shared models.
    Converts field names to camelCase representation.
    """

    class Meta:
        """
        Meta options for the base serializer.
        """

        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class AddressSerializer(BaseSerializer):
    """
    Serializer for Address model.
    Converts field names to camelCase representation.
    """

    _LIST_SERVICES = [WebService.APICEP, WebService.VIACEP, WebService.OPENCEP]

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the Address serializer.
        """

        model = Address
        fields = [
                "id",
                "postal_code",
                "number",
                "complement",
                "street",
                "city",
                "state",
                "neighbourhood",
        ]
        read_only_fields = ("id",)

    def __validate_postal_code(self, value: str) -> Dict:
        """
        Validate the postal code and return address details.
        Tries multiple services to get the address from the postal code.

        Args:
            value (str): The postal code to validate.

        Returns:
            Dict: Address details if found.
        """
        for service in self._LIST_SERVICES:
            try:
                return get_address_from_cep(value, service)
            except (ConnectionError, BrazilCEPException):
                continue
        raise BaseValidationError(
            "postal_code",
            message="Não foi possível conectar ao serviço de CEP.",
        )

    def validate(self, attrs: Dict) -> Dict:
        """
        Validate the address fields.
        Validates the postal code and retrieves address details.

        Args:
            attrs (Dict): The attributes to validate.

        Returns:
            Dict: Validated attributes with address details.
        """
        attrs = super().validate(attrs)
        postal_code = attrs.get("postal_code", "")
        if not postal_code:
            return attrs
        try:
            address: Dict = self.__validate_postal_code(postal_code)
            attrs["street"] = address.get("street", "")
            attrs["neighbourhood"] = address.get("district", "")
            attrs["city"] = address.get("city", "")
            attrs["state"] = address.get("uf", "")
        except InvalidCEP as exc:
            raise BaseValidationError(
                "postal_code",
                message="Formato de CEP inválido.",
            ) from exc
        except CEPNotFound as exc:
            raise BaseValidationError(
                "postal_code", message="CEP não encontrado."
            ) from exc
        return attrs


class ContactSerializer(BaseSerializer):
    """
    Serializer for Contact model.
    Converts field names to camelCase representation.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the Contact serializer.
        """

        model = Contact

    def validate_email(self, value):
        """
        Validate email field considering the current instance.

        Args:
            value: The email value to validate.

        Returns:
            str: The validated email.

        Raises:
            ValidationError: If email already exists for a different contact.
        """
        if not value:
            return value

        if self.instance and self.instance.email == value:
            return value

        if (
            self.parent
            and self.parent.instance
            and self.parent.instance.contact.email == value
        ):
            return value

        existing_contact = Contact.objects.filter(email=value).first()
        if existing_contact:
            raise BaseValidationError(
                "Este email já está sendo usado por outro contato."
            )

        return value

    def validate(self, attrs: Dict) -> Dict:
        """
        Validate the contact fields.

        Args:
            attrs (Dict): The attributes to validate.
        Returns:
            Dict: Validated attributes.
        """
        attrs = super().validate(attrs)
        email = attrs.get("email", "")
        if email and not serializers.EmailField().run_validation(email):
            raise BaseValidationError("email", message="Email inválido.")
        return attrs
