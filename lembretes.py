# ==========================================
# LEMBRETES.PY — Avisos automáticos diários
# ==========================================

from sheets import conectar
from whatsapp import enviar_mensagem
from datetime import datetime, timedelta

NUMERO_FINANCEIRO = "554199849507"  # número da sua amiga

def get_dias_uteis(n):
    dias = []
    hoje = datetime.today()
    contador = 0
    while len(dias) < n:
        contador += 1
        dia = hoje + timedelta(days=contador)
        if dia.weekday() < 5:  # 0-4 = segunda a sexta
            dias.append(dia.strftime("%d/%m"))
    return dias

def verificar_contas():
    planilha = conectar()
    aba = planilha.worksheet("Financeiro")
    registros = aba.get_all_records()

    hoje = datetime.today().strftime("%d/%m")
    proximos = get_dias_uteis(3)
    datas_alerta = [hoje] + proximos

    contas_hoje = []
    contas_proximas = []

    for linha in registros:
        if linha.get("Status") != "Pendente":
            continue
        vencimento = str(linha.get("Vencimento", "")).strip()
        if vencimento == hoje:
            contas_hoje.append(linha)
        elif vencimento in proximos:
            contas_proximas.append(linha)

    # Monta mensagem
    mensagem = "📋 *Relatório Financeiro Diário*\n\n"

    if contas_hoje:
        mensagem += "🔴 *Vencendo HOJE:*\n"
        for c in contas_hoje:
            mensagem += f"• {c['Empresa']} - {c['Imposto']} - R${c['Valor']}\n"
        mensagem += "\n"

    if contas_proximas:
        mensagem += "🟡 *Vencendo nos próximos 3 dias:*\n"
        for c in contas_proximas:
            mensagem += f"• {c['Empresa']} - {c['Imposto']} - R${c['Valor']} - Venc: {c['Vencimento']}\n"
        mensagem += "\n"

    if not contas_hoje and not contas_proximas:
        mensagem += "✅ Nenhuma conta vencendo nos próximos dias."

    # enviar_mensagem(NUMERO_FINANCEIRO, mensagem)
    print(f"MENSAGEM QUE SERIA ENVIADA:\n{mensagem}")
    print(f"✅ Lembrete enviado: {datetime.now()}")

if __name__ == "__main__":
    verificar_contas()