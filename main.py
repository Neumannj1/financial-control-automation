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
        return

    if resultado.get("acao") == "confirmar":
        confirmar_pagamento(resultado["empresa"], resultado["imposto"])
    else:
        salvar_conta(resultado)


# ==========================================
# TESTES
# ==========================================

if __name__ == "__main__":
    mensagens_teste = [
        "adicionar QUANTUM ICMS 30/06 500",   # cadastra
        "paguei QUANTUM ICMS",                 # confirma pagamento
        "paguei QUANTUM ICMS",                 # tenta confirmar de novo (já pago)
    ]

    for msg in mensagens_teste:
        processar_mensagem(msg)