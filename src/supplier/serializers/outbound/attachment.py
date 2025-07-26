from rest_framework import serializers

from src.supplier.models.attachments import SupplierAttachment
from src.supplier.serializers.outbound.supplier import SupplierOutSerializer


class SupplierAttachmentOutSerializer(serializers.ModelSerializer):
    """
    Serializer for SupplierAttachment model output.
    Used for GET requests and responses.
    """

    attachment_type_name = serializers.CharField(
        source="attachment_type.name", read_only=True
    )
    file_name = serializers.ReadOnlyField()

    class Meta:
        model = SupplierAttachment
        fields = [
            "id",
            "attachment_type_name",
            "file_name",
            "description",
        ]
        read_only_fields = [
            "id",
        ]


class SupplierAttachmentBasicOutSerializer(serializers.ModelSerializer):
    """
    Basic serializer for SupplierAttachment without nested relationships.
    Used when we don't need full supplier/attachment_type details.
    """

    file_name = serializers.ReadOnlyField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = SupplierAttachment
        fields = [
            "id",
            "supplier",
            "attachment_type_id",
            "attachment_type_name",
            "file_name",
            "file_url",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_file_url(self, obj):
        """Get the file URL for download."""
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.get_file_url())
            return obj.get_file_url()
        return None
