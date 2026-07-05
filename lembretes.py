# ==========================================
# LEMBRETES.PY — Avisos automáticos + geração de relatórios
# ==========================================

from sheets import conectar
from whatsapp import enviar_mensagem
from datetime import datetime, timedelta

NUMEROS_DESTINO = [
    "5541998495077",   # financeiro
    "5541998866873",   # Jean (testes)
]

def get_dias_uteis(n):
    dias = []
    hoje = datetime.today()
    contador = 0
    while len(dias) < n:
        contador += 1
        dia = hoje + timedelta(days=contador)
        if dia.weekday() < 5:
            dias.append(dia.strftime("%d/%m"))
    return dias

def formatar_valor(valor):
    try:
        return f"R$ {limpar_valor(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"R$ {valor}"

def limpar_valor(valor):
    """Converte para float aceitando '50000', '50000.00', 'R$ 50.000,00' etc."""
    if isinstance(valor, (int, float)):
        return float(valor)
    s = str(valor).strip()
    if not s:
        return 0.0
    # Remove R$, espaços e outros caracteres não numéricos exceto , . -
    s = s.replace("R$", "").replace(" ", "").strip()
    # Formato brasileiro: 50.000,00 -> remove pontos de milhar, vírgula vira ponto
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0.0

# ==========================================
# MONTAGEM DAS MENSAGENS (retornam texto)
# ==========================================

def montar_relatorio():
    """Monta o texto do relatório diário (atrasadas / hoje / próximos 3 dias)."""
    planilha = conectar()
    aba = planilha.worksheet("Financeiro")
    registros = aba.get_all_records()

    hoje = datetime.today()
    hoje_str = hoje.strftime("%d/%m")
    proximos = get_dias_uteis(3)

    contas_hoje = []
    contas_proximas = []
    contas_atrasadas = []

    for linha in registros:
        if linha.get("Status") != "Pendente":
            continue
        vencimento = str(linha.get("Vencimento", "")).strip()
        if not vencimento:
            continue

        try:
            dia, mes = vencimento.split("/")
            data_venc = datetime(hoje.year, int(mes), int(dia))
            if data_venc.date() < hoje.date():
                contas_atrasadas.append(linha)
                continue
        except:
            pass

        if vencimento == hoje_str:
            contas_hoje.append(linha)
        elif vencimento in proximos:
            contas_proximas.append(linha)

    todas = contas_atrasadas + contas_hoje + contas_proximas
    total_aberto = sum(limpar_valor(c.get("Valor", 0)) for c in todas)

    mensagem = f"📊 *Controle Fiscal · {hoje_str}*\n"
    mensagem += "━━━━━━━━━━━━━━━━━━━━\n\n"

    if contas_atrasadas:
        mensagem += "⚠️ *EM ATRASO*\n"
        for c in contas_atrasadas:
            mensagem += f"• {c['Empresa']} · {c['Imposto']} · {formatar_valor(c['Valor'])} _(venceu {c['Vencimento']})_\n"
        mensagem += "\n"

    if contas_hoje:
        mensagem += "🔴 *VENCE HOJE*\n"
        for c in contas_hoje:
            mensagem += f"• {c['Empresa']} · {c['Imposto']} · {formatar_valor(c['Valor'])}\n"
        mensagem += "\n"

    if contas_proximas:
        mensagem += "🟡 *PRÓXIMOS 3 DIAS*\n"
        for c in contas_proximas:
            mensagem += f"• {c['Empresa']} · {c['Imposto']} · {c['Vencimento']} · {formatar_valor(c['Valor'])}\n"
        mensagem += "\n"

    if not contas_hoje and not contas_proximas and not contas_atrasadas:
        mensagem += "✅ Nenhuma conta vencendo nos próximos dias.\n\n"

    mensagem += "━━━━━━━━━━━━━━━━━━━━\n"
    mensagem += f"💰 *Total em aberto: {formatar_valor(total_aberto)}*"

    return mensagem


def montar_resumo():
    """Monta o texto do resumo geral (pagas / pendentes / total)."""
    planilha = conectar()
    aba = planilha.worksheet("Financeiro")
    registros = aba.get_all_records()

    hoje_str = datetime.today().strftime("%d/%m")
    pagas = [r for r in registros if r.get("Status") == "Pago"]
    pendentes = [r for r in registros if r.get("Status") == "Pendente"]

    total_pago = sum(limpar_valor(r.get("Valor", 0)) for r in pagas)
    total_pendente = sum(limpar_valor(r.get("Valor", 0)) for r in pendentes)

    mensagem = f"📊 *Resumo Geral · {hoje_str}*\n"
    mensagem += "━━━━━━━━━━━━━━━━━━━━\n\n"
    mensagem += f"✅ *Pagas:* {len(pagas)} contas · {formatar_valor(total_pago)}\n"
    mensagem += f"⏳ *Pendentes:* {len(pendentes)} contas · {formatar_valor(total_pendente)}\n\n"

    if pendentes:
        mensagem += "📋 *Contas pendentes:*\n"
        for c in pendentes:
            mensagem += f"• {c['Empresa']} · {c['Imposto']} · {c['Vencimento']} · {formatar_valor(c['Valor'])}\n"

    mensagem += "\n━━━━━━━━━━━━━━━━━━━━\n"
    mensagem += f"💰 *Total em aberto: {formatar_valor(total_pendente)}*"

    return mensagem


# ==========================================
# ENVIO ATIVO (agendador / cron job)
# ==========================================

def verificar_contas():
    mensagem = montar_relatorio()
    for numero in NUMEROS_DESTINO:
        enviar_mensagem(numero, mensagem)
    print(f"✅ Lembrete enviado: {datetime.now()}")

def resumo_semanal():
    mensagem = montar_resumo()
    for numero in NUMEROS_DESTINO:
        enviar_mensagem(numero, mensagem)
    print(f"✅ Resumo semanal enviado: {datetime.now()}")


if __name__ == "__main__":
    print(montar_relatorio())
    print()
    print(montar_resumo())