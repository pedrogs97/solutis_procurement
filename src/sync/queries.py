"""
SQL queries for TOTVS database synchronization.
This module contains all SQL queries used in the sync process.
"""

GET_SUPPLIERS_BY_TAX_IDS = """
    SELECT
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
        ATIVO
    FROM FCFO
    WHERE ATIVO = 1 AND CGCCFO IN ({tax_ids_list})
"""

GET_SUPPLIER_TYPE_BY_CODE = """
    SELECT CODTCF, DESCRICAO
    FROM FTCF
    WHERE CODTCF = '{type_code}'
"""

GET_SUPPLIER_PAYMENT_DATA = """
    SELECT
        CODCOLIGADA
        ,CODCFO
        ,IDPGTO
        ,FORMAPAGAMENTO
        ,NUMEROBANCO
        ,CODIGOAGENCIA
        ,DIGITOAGENCIA
        ,CONTACORRENTE
        ,DIGITOCONTA
        ,NOMEAGENCIA
        ,TIPOCONTA
        ,FAVORECIDO
        ,CGCFAVORECIDO
        ,ATIVO
        ,CHAVE
        ,TIPOPIX
    FROM FDADOSPGTO
    WHERE CODCFO='{tax_id}';
"""
