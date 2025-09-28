# Generated migration to update StepApproval with Approver FK
import django.db.models.deletion
from django.db import migrations, models


def link_step_approvals_to_approvers(apps, schema_editor):
    """
    Liga StepApproval existentes aos registros de Approver correspondentes.
    """
    step_approval_model = apps.get_model("supplier", "StepApproval")
    approver_model = apps.get_model("supplier", "Approver")

    for approval in step_approval_model.objects.all():
        if hasattr(approval, "approver_name") and hasattr(
            approval, "approver_department"
        ):
            name = approval.approver_name
            department = approval.approver_department.lower().replace(" ", "")
            email = f"{name.lower().replace(' ', '.')}@{department}.company.com"

            try:
                approver = approver_model.objects.get(name=name, email=email)
                approval.approver_id = approver.id
                approval.save()
            except approver_model.DoesNotExist:
                # Se não encontrar, criar um novo aprovador
                approver = approver_model.objects.create(name=name, email=email)
                approval.approver_id = approver.id
                approval.save()


def reverse_link_migration(apps, schema_editor):
    """
    Reverter a ligação entre StepApproval e Approver.
    """
    pass  # Não há necessidade de reverter pois os campos antigos serão restaurados


class Migration(migrations.Migration):

    dependencies = [
        ("supplier", "0028_add_approver_model"),
    ]

    operations = [
        # 1. Adicionar o campo approver como nullable temporariamente
        migrations.AddField(
            model_name="stepapproval",
            name="approver",
            field=models.ForeignKey(
                null=True,
                blank=True,
                help_text="Usuário que realizou a aprovação",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="step_approvals",
                to="supplier.approver",
                verbose_name="Aprovador",
            ),
        ),
        # 2. Migrar dados existentes
        migrations.RunPython(link_step_approvals_to_approvers, reverse_link_migration),
        # 3. Tornar o campo obrigatório
        migrations.AlterField(
            model_name="stepapproval",
            name="approver",
            field=models.ForeignKey(
                help_text="Usuário que realizou a aprovação",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="step_approvals",
                to="supplier.approver",
                verbose_name="Aprovador",
            ),
        ),
        # 4. Remover campos antigos
        migrations.RemoveField(
            model_name="stepapproval",
            name="approver_department",
        ),
        migrations.RemoveField(
            model_name="stepapproval",
            name="approver_name",
        ),
    ]
