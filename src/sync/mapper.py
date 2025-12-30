"""Data Transfer Objects for sync operations."""

PAYMENT_METHOD_MAPPER = {
    "D": "DOC (Comp)",
    "T": "Crédito em Conta Corrente no mesmo Banco",
    "C": "Cheque Administrativo",
    "I": "TÍTULO DE COBRANÇA (BOLETO)",
    "N": "Pagamento Eletrônico a Concessionários",
    "P": "Crédito em Conta de Poupança",
    "R": "Ordem de Pagamento à disposição",
    "X": "Crédito em Conta Real Time",
    "Y": "TED CIP",
    "Z": "TED STR",
    "A": "DARF",
    "G": "GPS",
    "E": "Débito Automático",
    "M": "Crédito em Conta Corrente de Mesma Titularidade",
    "B": "IPTU/ISS/Outros Tributos Municipais",
    "F": "DARJ",
    "J": "GARE - SP ICMS",
    "L": "FGTS - GFIP",
    "O": "GNRE e Tributos Estaduais c/ Cód. Barras",
    "S": "PIX Transferência",
    "Q": "PIX QR Code",
}


PIX_TYPE_MAPPER = {
    1: "Telefone",
    2: "Email",
    3: "CPF",
    4: "CNPJ",
    5: "Chave Aleatória",
}
