# ==========================================
# SHEETS.PY — Conexão com Google Sheets
# - Proteção contra duplicatas (com debug)
# ==========================================

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_ID = "195QolX1z0dk_DheWrzL6JPmK5Pt37hYBRueSDAlVB-Q"


def conectar():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_json:
        creds_info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file("credenciais.json", scopes=SCOPES)
    cliente = gspread.authorize(creds)
    return cliente.open_by_key(SHEET_ID)


def salvar_conta(dados):
    planilha = conectar()
    aba = planilha.worksheet("Financeiro")

    # ── Proteção contra duplicata ──────────────────────────
    registros = aba.get_all_records()

    emp_novo = str(dados["empresa"]).strip().upper()
    imp_novo = str(dados["descricao"]).strip().upper()
    venc_novo = str(dados["vencimento"]).strip()

    print(f"🔍 DEBUG procurando duplicata: EMP='{emp_novo}' IMP='{imp_novo}' VENC='{venc_novo}'")

    for linha in registros:
        emp_exist = str(linha.get("Empresa", "")).strip().upper()
        imp_exist = str(linha.get("Imposto", "")).strip().upper()
        venc_exist = str(linha.get("Vencimento", "")).strip()
        status_exist = str(linha.get("Status", "")).strip().upper()

        if (emp_exist == emp_novo and
            imp_exist == imp_novo and
            venc_exist == venc_novo and
            status_exist == "PENDENTE"):
            print(f"⚠️ DUPLICATA encontrada! Linha existente: EMP='{emp_exist}' IMP='{imp_exist}' VENC='{venc_exist}' STATUS='{status_exist}'")
            return "duplicata"

    print("✅ Nenhuma duplicata. Salvando...")

    # ── Salva a nova conta ─────────────────────────────────
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    proximo_id = len(aba.get_all_values())

    nova_linha = [
        proximo_id,
        dados["tipo"],
        dados["empresa"],
        "",                   # CNPJ
        dados["categoria"],
        dados["descricao"],
        "",                   # Descrição adicional
        dados["vencimento"],
        dados["valor"],
        dados["status"],
        agora,                # Criado_Em
        "",                   # Pago_Em
        "WhatsApp",
        "",                   # Responsável
        ""                    # Observação
    ]

    aba.append_row(nova_linha)
    print(f"✅ Salvo: {dados['empresa']} - {dados['descricao']} - R${dados['valor']}")
    return "salvo"


def confirmar_pagamento(empresa, imposto, valor_pago=None):
    planilha = conectar()
    aba = planilha.worksheet("Financeiro")

    registros = aba.get_all_records()

    for i, linha in enumerate(registros, start=2):
        if (str(linha.get("Empresa", "")).strip().upper() == empresa.upper() and
            str(linha.get("Imposto", "")).strip().upper() == imposto.upper() and
            str(linha.get("Status", "")).strip().upper() == "PENDENTE"):

            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            aba.update_cell(i, 10, "Pago")    # Status
            aba.update_cell(i, 12, agora)     # Pago_Em

            if valor_pago is not None:
                aba.update_cell(i, 15, f"Valor pago: R$ {valor_pago:.2f}")

            print(f"✅ Pagamento confirmado: {empresa} - {imposto}" +
                  (f" - R$ {valor_pago:.2f}" if valor_pago else ""))
            return True

    print(f"❌ Conta não encontrada ou já paga: {empresa} - {imposto}")
    return False


if __name__ == "__main__":
    dados_teste = {
        "tipo":       "Saida",
        "empresa":    "MAGNAPR",
        "descricao":  "ICMS",
        "vencimento": "20/06",
        "valor":      850.0,
        "categoria":  "Imposto",
        "status":     "Pendente"
    }
    print(salvar_conta(dados_teste))