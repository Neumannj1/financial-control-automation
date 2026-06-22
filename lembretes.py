# ==========================================
# LEMBRETES.PY — Avisos automáticos diários
# ==========================================

from sheets import conectar
from whatsapp import enviar_mensagem
from datetime import datetime, timedelta

NUMERO_FINANCEIRO = "5541998495077"  # financeiro recebe lembretes

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

    hoje = datetime.today()
    hoje_str = hoje.strftime("%d/%m")
    proximos = get_dias_uteis(3)
    datas_alerta = [hoje_str] + proximos

    contas_hoje = []
    contas_proximas = []
    contas_atrasadas = []

    for linha in registros:
        if linha.get("Status") != "Pendente":
            continue
        vencimento = str(linha.get("Vencimento", "")).strip()
        if not vencimento:
            continue

        # Verifica atraso
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

    # Monta mensagem
    mensagem = "📋 *Relatório Financeiro Diário*\n\n"

    if contas_atrasadas:
        mensagem += "🚨 *CONTAS EM ATRASO:*\n"
        for c in contas_atrasadas:
            mensagem += f"• {c['Empresa']} - {c['Imposto']} - R${c['Valor']} - Venceu: {c['Vencimento']}\n"
        mensagem += "\n"

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

    if not contas_hoje and not contas_proximas and not contas_atrasadas:
        mensagem += "✅ Nenhuma conta vencendo nos próximos dias."

    enviar_mensagem(NUMERO_FINANCEIRO, mensagem)
    print(f"✅ Lembrete enviado: {datetime.now()}")

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

    enviar_mensagem(NUMERO_FINANCEIRO, mensagem)
    # print(f"MENSAGEM QUE SERIA ENVIADA:\n{mensagem}")
    print(f"✅ Lembrete enviado: {datetime.now()}")

def resumo_semanal():
    planilha = conectar()
    aba = planilha.worksheet("Financeiro")
    registros = aba.get_all_records()

    pagas = [r for r in registros if r.get("Status") == "Pago"]
    pendentes = [r for r in registros if r.get("Status") == "Pendente"]

    total_pago = sum(float(r.get("Valor", 0)) for r in pagas)
    total_pendente = sum(float(r.get("Valor", 0)) for r in pendentes)

    mensagem = "📊 *Resumo Semanal Financeiro*\n\n"
    mensagem += f"✅ Contas pagas: {len(pagas)} - Total: R${total_pago:.2f}\n"
    mensagem += f"⏳ Contas pendentes: {len(pendentes)} - Total: R${total_pendente:.2f}\n\n"

    if pendentes:
        mensagem += "📋 *Pendentes:*\n"
        for c in pendentes:
            mensagem += f"• {c['Empresa']} - {c['Imposto']} - R${c['Valor']} - Venc: {c['Vencimento']}\n"

    enviar_mensagem(NUMERO_FINANCEIRO, mensagem)
    print(f"✅ Resumo semanal enviado: {datetime.now()}")    

if __name__ == "__main__":
    verificar_contas()