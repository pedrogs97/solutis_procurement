"""
Serializer for ResponsibilityMatrix model.
This module provides serializers for creating and updating supplier responsibility matrices,
including validation for supplier existence and RACI values.
"""

from src.shared.serializers import BaseSerializer
from src.shared.validation import BaseValidationError
from src.supplier.models.responsibility_matrix import RACI_CHOICES, ResponsibilityMatrix
from src.supplier.models.supplier import Supplier
from src.supplier.serializers.validators import validate_supplier


class ResponsibilityMatrixInSerializer(BaseSerializer):
    """
    Serializer for ResponsibilityMatrix model input.
    Used for POST, PUT, and PATCH requests.
    """

    class Meta(BaseSerializer.Meta):
        """
        Meta options for the ResponsibilityMatrix input serializer.
        """

        model = ResponsibilityMatrix

    def validate_supplier(self, value) -> Supplier:
        """Validate that the supplier exists and is active."""
        return validate_supplier(value)

    def validate(self, attrs):
        """
        Validate RACI matrix rules and business logic.
        """
        # Get all RACI field values from attrs
        raci_fields = self._extract_raci_fields(attrs)

        # Validate RACI business rules
        self._validate_raci_business_rules(raci_fields)

        return attrs

    def _extract_raci_fields(self, attrs):
        """Extract RACI fields grouped by activity."""
        raci_fields = {}
        activity_prefixes = self._get_activity_prefixes()

        for field in self.Meta.model._meta.get_fields():
            if not hasattr(field, "name"):
                continue

            field_name = field.name
            matching_prefix = self._find_matching_prefix(field_name, activity_prefixes)

            if matching_prefix:
                field_value = attrs.get(field_name)
                if field_value:
                    activity = field_name.rsplit("_", 1)[0]
                    self._add_to_raci_fields(raci_fields, activity, field_value)

        return raci_fields

    def _get_activity_prefixes(self):
        """Get list of activity prefixes."""
        return [
            "contract_request_",
            "document_analysis_",
            "risk_consultation_",
            "risk_assessment_",
            "system_registration_",
            "form_handling_",
            "contract_draft_",
            "compliance_validation_",
            "final_approval_",
            "contract_signing_",
            "document_management_",
            "payment_release_",
        ]

    def _find_matching_prefix(self, field_name, prefixes):
        """Find if field name matches any activity prefix."""
        for prefix in prefixes:
            if field_name.startswith(prefix):
                return prefix
        return None

    def _add_to_raci_fields(self, raci_fields, activity, field_value):
        """Add field value to the appropriate activity group."""
        if activity not in raci_fields:
            raci_fields[activity] = []
        raci_fields[activity].append(field_value)

    def _validate_raci_business_rules(self, raci_fields):
        """Validate RACI business rules for all activities."""
        for activity, values in raci_fields.items():
            self._validate_single_accountable(activity, values)
            self._validate_minimum_involvement(activity, values)

    def _validate_single_accountable(self, activity, values):
        """Validate that only one person is accountable per activity."""
        accountable_count = values.count("A") + values.count("A/R")
        if accountable_count > 1:
            raise BaseValidationError(
                activity,
                f"Atividade '{activity}': Só pode haver um responsável (A ou A/R) por atividade.",
            )

    def _validate_minimum_involvement(self, activity, values):
        """Validate that at least one person is involved in each activity."""
        if all(value == "-" for value in values):
            raise BaseValidationError(
                activity,
                f"Atividade '{activity}': Pelo menos uma área deve estar envolvida na atividade.",
            )

    def validate_raci_field(self, value, field_name):
        """
        Generic validation for RACI fields.
        """
        valid_choices = [choice[0] for choice in RACI_CHOICES]
        if value not in valid_choices:
            raise BaseValidationError(
                field_name,
                f"Valor inválido para {field_name}. Escolhas válidas: {valid_choices}",
            )
        return value
