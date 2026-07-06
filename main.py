# ==========================================
# MAIN.PY — Integração parser + sheets
# ==========================================

from parser import parsear_mensagem, PALAVRAS_CONFIRMACAO
from sheets import salvar_conta, confirmar_pagamento
from lembretes import montar_relatorio, montar_resumo

def formatar_valor(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"R$ {valor}"

def processar_mensagem(mensagem):
    print(f"\nMensagem recebida: '{mensagem}'")

    resultado = parsear_mensagem(mensagem)

    if "erro" in resultado:
        print(f"❌ Erro: {resultado['erro']}")
        return resultado

    acao = resultado.get("acao")

    # ── Comandos de consulta ──────────────────────────────
    if acao == "consulta_relatorio":
        return {"resposta_texto": montar_relatorio()}

    if acao == "consulta_resumo":
        return {"resposta_texto": montar_resumo()}

    # ── Confirmação de pagamento ──────────────────────────
    if acao == "confirmar":
        valor_pago = resultado.get("valor_pago")
        sucesso = confirmar_pagamento(resultado["empresa"], resultado["imposto"], valor_pago)

        if sucesso:
            resposta = {
                "confirmado": True,
                "empresa":    resultado["empresa"],
                "imposto":    resultado["imposto"],
            }
            if valor_pago:
                resposta["valor_pago"] = valor_pago
            return resposta
        else:
            return {"erro": f"Conta não encontrada ou já paga: {resultado['empresa']} · {resultado['imposto']}"}

    # ── Cadastro de conta ─────────────────────────────────
    status_save = salvar_conta(resultado)

    if status_save == "duplicata":
        return {"erro": f"⚠️ Esta conta já está cadastrada e pendente:\n{resultado['empresa']} - {resultado['descricao']} - Venc: {resultado['vencimento']}\n\nSe quiser cadastrar mesmo assim, altere algum dado ou confirme o pagamento da anterior."}

    return resultado


if __name__ == "__main__":
    mensagens_teste = [
        "adicionar BRIGHTLED ICMS 30/06 500",
        "relatorio",
        "resumo",
        "paguei BRIGHTLED ICMS 480",
        "oi tudo bem",
    ]
    for msg in mensagens_teste:
        processar_mensagem(msg)