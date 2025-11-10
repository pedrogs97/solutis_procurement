"""
# para depois
CODRECEITA -> FK classificação Receita (tabela FIRRF)
REGIMEISS -> regime ISS (siglas)
RETENCAOISSO -> retenção ISS (numeros)
NIT -> NIT
TIPORENDIMENTO -> tipo de rendimento (numeros)
FORMATRIBUTACAO -> forma de tributação (numeros)
"""

import os

import pymssql
from django.db import models

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


class ExternalDatabase:
    """Class of SQLServe connection"""

    # Some other example server values are
    # server = 'localhost\sqlexpress' # for a named instance
    # server = 'myserver,port' # to specify an alternate port

    def __init__(self) -> None:
        self.connection = None
        self._cursor = None

    def _try_connect(self, as_dict=True) -> None:
        """Try connect with SQLServer database"""
        # ENCRYPT defaults to yes starting in ODBC Driver 18.
        # It's good to always specify ENCRYPT=yes on the client side to avoid MITM attacks.
        if self.connection is None:
            # pylint: disable=no-member
            self.connection = pymssql.connect(
                server=os.getenv("SQLSERVER_HOST_DB", ""),
                user=os.getenv("SQLSERVER_USER_DB", ""),
                password=os.getenv("SQLSERVER_PASSWORD_DB", ""),
                database=os.getenv("SQLSERVER_NAME_DB", ""),
            )
        if self._cursor is None:
            self._cursor = self.connection.cursor(as_dict)

    def get_connection(self, as_dict=True):
        """Return external connection"""
        if self.connection is None:
            self._try_connect(as_dict)
        return self.connection

    def get_cursor(self, as_dict=True):
        """Return external cursor"""
        if self._cursor is None:
            self._try_connect(as_dict)
        return self._cursor

    def load_suppliers(self):
        """Carrega fornecedores da TOTVS para o sistema local"""
        dict_supplier_risk = {
            "43.649.570/0001-10": "BAIXO",
            "33.571.622/0001-29": "BAIXO",
            "60.143.657/0001-30": "BAIXO",
        }

        cursor = self.get_cursor()
        list_param = ",".join(f"'{cnpj}'" for cnpj in dict_supplier_risk)
        cursor.execute(
            f"""SELECT
            RUA,
            CIDADE,
            BAIRRO,
            CODETD,
            NUMERO,
            CEP,
            COMPLEMENTO,
            NOMEFANTASIA,
            NOME,
            CGCCFO,
            EMAIL,
            TELEFONE,
            CODTCF,
            INSCRESTADUAL,
            INSCRMUNICIPAL,
            PESSOAFISOUJUR,
            ATIVO FROM FCFO WHERE ATIVO = 1 AND CGCCFO IN ({list_param})"""
        )
        rows = cursor.fetchall()

        print("Supplier from TOTVS:", len(rows))

        for row in rows:
            address = Address.objects.create(
                street=row["RUA"] or "",
                city=row["CIDADE"] or "",
                state=row["BAIRRO"] or "",
                neighbourhood=row["CODETD"] or "",
                number=None if isinstance(row["NUMERO"], str) else row["NUMERO"],
                postal_code=row["CEP"] or "",
                complement=row["COMPLEMENTO"] or "",
            )
            address.refresh_from_db()
            contact = Contact.objects.create(
                email=row["EMAIL"] or "",
                phone=row["TELEFONE"] or "",
            )
            contact.refresh_from_db()
            risk_level = DomRiskLevel.objects.get(
                name=dict_supplier_risk[row["CGCCFO"]]
            )

            cursor = self.get_cursor()
            cursor.execute(
                f"SELECT CODTCF, DESCRICAO  FROM FTCF WHERE CODTCF = {row['CODTCF']}"
            )
            rows = cursor.fetchall()

            type_row = rows[0]

            supplier_type, _ = DomTypeSupplier.objects.get_or_create(
                name=type_row["DESCRICAO"].strip().upper()
            )
            Supplier.objects.create(
                trade_name=row["NOMEFANTASIA"],
                legal_name=row["NOME"],
                tax_id=row["CGCCFO"],
                state_business_registration=row["INSCRESTADUAL"] or "",
                municipal_business_registration=row["INSCRMUNICIPAL"] or "",
                address=address,
                contact=contact,
                classification_id=1,
                category_id=1 if row["CODTCF"].upper() == "J" else 2,
                risk_level=risk_level,
                type=supplier_type,
            )
        cnxn = self.get_connection()
        cnxn.close()
        print("Suppliers loaded successfully.")
