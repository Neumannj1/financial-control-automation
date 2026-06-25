# ==========================================
# LEMBRETES.PY — Avisos automáticos diários
# ==========================================

from sheets import conectar
from whatsapp import enviar_mensagem
from datetime import datetime, timedelta

NUMEROS_DESTINO = [
    "5541998495077",   # financeiro (Andreia)
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
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"R$ {valor}"

def verificar_contas():
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

    # Calcula total em aberto
    todas = contas_atrasadas + contas_hoje + contas_proximas
    total_aberto = sum(float(c.get("Valor", 0)) for c in todas)

    # Monta mensagem
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

    for numero in NUMEROS_DESTINO:
        enviar_mensagem(numero, mensagem)

    print(f"✅ Lembrete enviado: {datetime.now()}")

def resumo_semanal():
    planilha = conectar()
    aba = planilha.worksheet("Financeiro")
    registros = aba.get_all_records()

    hoje_str = datetime.today().strftime("%d/%m")
    pagas = [r for r in registros if r.get("Status") == "Pago"]
    pendentes = [r for r in registros if r.get("Status") == "Pendente"]

    total_pago = sum(float(r.get("Valor", 0)) for r in pagas)
    total_pendente = sum(float(r.get("Valor", 0)) for r in pendentes)

    mensagem = f"📊 *Resumo Semanal · {hoje_str}*\n"
    mensagem += "━━━━━━━━━━━━━━━━━━━━\n\n"
    mensagem += f"✅ *Pagas:* {len(pagas)} contas · {formatar_valor(total_pago)}\n"
    mensagem += f"⏳ *Pendentes:* {len(pendentes)} contas · {formatar_valor(total_pendente)}\n\n"

    if pendentes:
        mensagem += "📋 *Contas pendentes:*\n"
        for c in pendentes:
            mensagem += f"• {c['Empresa']} · {c['Imposto']} · {c['Vencimento']} · {formatar_valor(c['Valor'])}\n"

    mensagem += "\n━━━━━━━━━━━━━━━━━━━━\n"
    mensagem += f"💰 *Total em aberto: {formatar_valor(total_pendente)}*"

    for numero in NUMEROS_DESTINO:
        enviar_mensagem(numero, mensagem)

    print(f"✅ Resumo semanal enviado: {datetime.now()}")

if __name__ == "__main__":
    verificar_contas()