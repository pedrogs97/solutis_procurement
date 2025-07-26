import os


def supplier_attachment_upload_path(instance, filename) -> str:
    """
    Generate the upload path for supplier attachments.
    Organizes files in subfolders by supplier ID.

    Args:
        instance: The supplier instance.
        filename: The original file name.

    Returns:
        str: The upload path for the supplier attachment.
    """
    return os.path.join(
        "supplier_files",
        str(instance.supplier.id),
        filename,
    )
