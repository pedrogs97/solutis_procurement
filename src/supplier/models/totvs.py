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
