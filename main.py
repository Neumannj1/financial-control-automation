# ==========================================
# MAIN.PY — Integração parser + sheets
# ==========================================

from parser import parsear_mensagem, PALAVRAS_CONFIRMACAO
from sheets import salvar_conta, confirmar_pagamento

def processar_mensagem(mensagem):
    print(f"\nMensagem recebida: '{mensagem}'")

    resultado = parsear_mensagem(mensagem)

    if "erro" in resultado:
        print(f"❌ Erro: {resultado['erro']}")
        return resultado

    if resultado.get("acao") == "confirmar":
        sucesso = confirmar_pagamento(resultado["empresa"], resultado["imposto"])
        if sucesso:
            return {"confirmado": True, "empresa": resultado["empresa"], "imposto": resultado["imposto"]}
        else:
            return {"erro": f"Conta não encontrada ou já paga: {resultado['empresa']} - {resultado['imposto']}"}
    else:
        salvar_conta(resultado)
        return resultado


# ==========================================
# TESTES
# ==========================================

if __name__ == "__main__":
    mensagens_teste = [
        "adicionar QUANTUM ICMS 30/06 500",
        "paguei QUANTUM ICMS",
        "paguei QUANTUM ICMS",
    ]

    for msg in mensagens_teste:
        processar_mensagem(msg)