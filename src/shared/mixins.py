"""
Mixins for the shared app in Django.
"""

from typing import Any

from src.utils.parse import to_camel_case


class SerializerCamelCaseRepresentationMixin:
    """
    Mixin to convert serializer field names to camelCase in the representation.
    """

    def to_representation(self, instance) -> Any:
        representation = super().to_representation(instance)
        return self._convert_to_camel_case(representation)

    def _convert_to_camel_case(self, data: Any) -> Any:
        """
        Convert dictionary keys to camelCase.
        """
        if isinstance(data, dict):
            return {
                to_camel_case(key): self._convert_to_camel_case(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._convert_to_camel_case(item) for item in data]
        return data
