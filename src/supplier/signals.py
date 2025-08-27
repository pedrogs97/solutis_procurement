"""Supplier signals"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from src.supplier.enums import DomPendecyTypeEnum
from src.supplier.models.attachments import SupplierAttachment
from src.supplier.models.domain import DomSupplierSituation
from src.supplier.models.responsibility_matrix import ResponsibilityMatrix
from src.supplier.models.supplier import Supplier, SupplierSituation


@receiver(post_save, sender=Supplier)
def verify_supplier_pendency(sender, instance: Supplier, created: bool, **kwargs):
    """
    Verify and update the supplier's pendency status.
    """
    is_completed = instance.is_completed_registration
    if is_completed:
        SupplierSituation.objects.get_or_create(
            supplier=instance, status=DomSupplierSituation.objects.get(name="ATIVO")
        )
    elif not is_completed and (
        not instance.situation
        or instance.situation
        and instance.situation.status.name != "PENDENTE"
    ):
        SupplierSituation.objects.get_or_create(
            supplier=instance,
            status=DomSupplierSituation.objects.get(
                name="PENDENTE",
                pendency_type=DomPendecyTypeEnum.PENDENCIA_CADASTRO.value,
            ),
        )


@receiver(post_save, sender=ResponsibilityMatrix)
def verify_responsability_matrix_pendency(
    sender, instance: ResponsibilityMatrix, created: bool, **kwargs
):
    """
    Verify and update the responsibility matrix's pendency status.
    """
    is_completed = instance.is_completed
    supplier = instance.supplier
    if not is_completed and (
        not supplier.situation or supplier.situation.status.name != "PENDENTE"
    ):
        SupplierSituation.objects.get_or_create(
            supplier=supplier,
            status=DomSupplierSituation.objects.get(
                name="PENDENTE",
                pendency_type=DomPendecyTypeEnum.PENDENCIA_MATRIZ_RESPONSABILIDADE.value,
            ),
        )
    elif (
        is_completed
        and supplier.is_completed_registration
        and supplier.situation
        and supplier.situation.status.name != "ATIVO"
    ):
        SupplierSituation.objects.get_or_create(
            supplier=supplier, status=DomSupplierSituation.objects.get(name="ATIVO")
        )


@receiver(post_save, sender=SupplierAttachment)
def verify_supplier_attachment_pendency(
    sender, instance: SupplierAttachment, created: bool, **kwargs
):
    """
    Verify and update the supplier attachment's pendency status.
    """
    is_completed = instance.is_completed_files
    supplier = instance.supplier
    if not is_completed and (
        not supplier.situation or supplier.situation.status.name != "PENDENTE"
    ):
        SupplierSituation.objects.get_or_create(
            supplier=supplier,
            status=DomSupplierSituation.objects.get(
                name="PENDENTE",
                pendency_type=DomPendecyTypeEnum.PENDENCIA_DOCUMENTACAO.value,
            ),
        )
    elif (
        is_completed
        and supplier.is_completed_registration
        and supplier.situation
        and supplier.situation.status.name != "ATIVO"
    ):
        SupplierSituation.objects.get_or_create(
            supplier=supplier, status=DomSupplierSituation.objects.get(name="ATIVO")
        )
