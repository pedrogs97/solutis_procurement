# Generated migration for Approver model
from django.db import migrations, models


def create_approvers_from_existing_data(apps, schema_editor):
    """
    Migra dados existentes de StepApproval para criar registros de Approver.
    """
    step_approval_model = apps.get_model("supplier", "StepApproval")
    approver_model = apps.get_model("supplier", "Approver")

    # Obter todos os aprovadores únicos dos dados existentes
    existing_approvals = step_approval_model.objects.all()
    approvers_data = set()

    for approval in existing_approvals:
        # Usar nome e departamento para criar um email único
        if hasattr(approval, "approver_name") and hasattr(
            approval, "approver_department"
        ):
            name = approval.approver_name
            department = approval.approver_department.lower().replace(" ", "")
            email = f"{name.lower().replace(' ', '.')}@{department}.company.com"
            approvers_data.add((name, email))

    # Criar registros de Approver
    for name, email in approvers_data:
        approver_model.objects.get_or_create(name=name, email=email)


def reverse_migration(apps, schema_editor):
    """
    Reverter a migration removendo todos os Approver criados.
    """
    approver_model = apps.get_model("supplier", "Approver")
    approver_model.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("supplier", "0027_approvalstep_approvalflow_stepapproval"),
    ]

    operations = [
        # 1. Criar o modelo Approver
        migrations.CreateModel(
            name="Approver",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        help_text="Nome completo do aprovador",
                        max_length=255,
                        verbose_name="Nome",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="Email do aprovador",
                        max_length=254,
                        verbose_name="Email",
                    ),
                ),
            ],
            options={
                "verbose_name": "Aprovador",
                "verbose_name_plural": "Aprovadores",
                "db_table": "approver",
                "ordering": ["name"],
                "abstract": False,
            },
        ),
        # 2. Migrar dados existentes
        migrations.RunPython(create_approvers_from_existing_data, reverse_migration),
    ]
