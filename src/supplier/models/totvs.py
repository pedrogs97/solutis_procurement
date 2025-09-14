"""
# para depois
CODRECEITA -> FK classificação Receita (tabela FIRRF)
REGIMEISS -> regime ISS (siglas)
RETENCAOISSO -> retenção ISS (numeros)
NIT -> NIT
TIPORENDIMENTO -> tipo de rendimento (numeros)
FORMATRIBUTACAO -> forma de tributação (numeros)
"""

from django.db import models
from django.db.transaction import atomic

from src.supplier.models.supplier import (
    Address,
    Contact,
    DomRiskLevel,
    DomTypeSupplier,
    Supplier,
)


class SqlServerModel(models.Model):
    """Classe base para modelos que representam tabelas do SQL Server (somente leitura)"""

    class Meta:
        """Meta class for SQL Server models."""

        abstract = True
        managed = False  # Django não gerencia essa tabela


class SupplierTotvs(SqlServerModel):
    """Modelo que mapeia uma tabela de fornecedores da TOTVS"""

    code = models.CharField(max_length=25, primary_key=True, db_column="CODCFO")
    trade_name = models.CharField(max_length=100, db_column="NOMEFANTASIA")
    legal_name = models.CharField(max_length=100, db_column="NOME")
    cnpj = models.CharField(max_length=20, db_column="CGCCFO")
    email = models.EmailField(blank=True, db_column="EMAIL")
    phone = models.CharField(max_length=20, blank=True, db_column="TELEFONE")
    city = models.CharField(max_length=32, blank=True, db_column="CIDADE")
    state = models.CharField(max_length=2, blank=True, db_column="CODETD")
    street = models.CharField(max_length=100, blank=True, db_column="RUA")
    number = models.CharField(max_length=8, blank=True, db_column="NUMERO")
    complement = models.CharField(max_length=60, blank=True, db_column="COMPLEMENTO")
    neighborhood = models.CharField(max_length=80, blank=True, db_column="BAIRRO")
    postal_code = models.CharField(max_length=9, blank=True, db_column="CEP")
    # FCTF
    type_supplier = models.CharField(max_length=25, blank=True, db_column="CODTCF")
    category = models.CharField(max_length=1, blank=True, db_column="PESSOAFISOUJUR")
    municipal_registration = models.CharField(
        max_length=20, blank=True, db_column="INSCRMUNICIPAL"
    )
    state_registration = models.CharField(
        max_length=20, blank=True, db_column="INSCRESTADUAL"
    )
    active = models.SmallIntegerField(db_column="ATIVO")

    class Meta(SqlServerModel.Meta):
        """Meta configuration for SupplierTotvs model."""

        verbose_name = "Fornecedor TOTVS"
        verbose_name_plural = "Fornecedores TOTVS"
        db_table = "FCFO"


class SupplierTypeTotvs(SqlServerModel):
    """Modelo que mapeia uma tabela de tipos de fornecedores da TOTVS"""

    code = models.CharField(max_length=25, primary_key=True, db_column="CODTCF")
    description = models.CharField(max_length=100, db_column="DESCRICAO")

    class Meta(SqlServerModel.Meta):
        """Meta configuration for SupplierTypeTotvs model."""

        verbose_name = "Tipo de Fornecedor TOTVS"
        verbose_name_plural = "Tipos de Fornecedores TOTVS"
        db_table = "FTCF"


@atomic
def load_suppliers():
    """Carrega fornecedores da TOTVS para o sistema local"""
    dict_supplier_risk = {
        "05.607.657/0008-01": "ALTO",
        "07.976.147/0001-60": "MÉDIO",
        "12.639.870/0001-94": "MÉDIO",
        "59.456.277/0001-76": "MÉDIO",
        "53.113.791/0001-22": "ALTO",
        "04.699.639/0001-68": "BAIXO",
        "12.499.520/0001-70": "BAIXO",
        "31.433.149/0001-98": "BAIXO",
    }

    supplier_from_totvs = SupplierTotvs.objects.using("sqlserver").filter(
        active=1,
        cnpj__in=dict_supplier_risk.keys(),
    )

    print("Supplier from TOTVS:", supplier_from_totvs.count())

    for supplier in supplier_from_totvs:
        address = Address.objects.create(
            street=supplier.street or "",
            city=supplier.city or "",
            state=supplier.state or "",
            neighbourhood=supplier.neighborhood or "",
            number=None if isinstance(supplier.number, str) else supplier.number,
            postal_code=supplier.postal_code or "",
            complement=supplier.complement or "",
        )
        address.refresh_from_db()
        contact = Contact.objects.create(
            email=supplier.email or "",
            phone=supplier.phone or "",
        )
        contact.refresh_from_db()
        risk_level = DomRiskLevel.objects.get(name=dict_supplier_risk[supplier.cnpj])
        supplier_type_totvs = (
            SupplierTypeTotvs.objects.using("sqlserver")
            .filter(code=supplier.type_supplier)
            .first()
        )
        if not supplier_type_totvs:
            continue
        supplier_type, _ = DomTypeSupplier.objects.get_or_create(
            name=supplier_type_totvs.description.strip().upper()
        )
        Supplier.objects.create(
            trade_name=supplier.trade_name,
            legal_name=supplier.legal_name,
            tax_id=supplier.cnpj,
            state_business_registration=supplier.state_registration or "",
            municipal_business_registration=supplier.municipal_registration or "",
            address=address,
            contact=contact,
            classification_id=1,
            category_id=1 if supplier.category.upper() == "J" else 2,
            risk_level=risk_level,
            type=supplier_type,
        )
