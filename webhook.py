# ==========================================
# WEBHOOK.PY — Servidor FastAPI
# ==========================================

from fastapi import FastAPI, Request
from main import processar_mensagem
from whatsapp import enviar_mensagem
from lembretes import verificar_contas, resumo_semanal
import schedule
import threading
import time
from datetime import datetime

app = FastAPI()

NUMEROS_AUTORIZADOS = [
    "5541998495077",   # financeiro
    "76845722657008",  # financeiro LID
    "5541998866873",   # Jean - testes
    "215199504154859", # Jean - LID
]

# ==========================================
# AGENDADOR (fallback — pode não rodar no Render Free)
# ==========================================

def rodar_lembrete():
    if datetime.now().weekday() < 5:
        print(f"Rodando lembrete: {datetime.now()}")
        verificar_contas()

def iniciar_agendador():
    schedule.every().day.at("11:30").do(rodar_lembrete)
    schedule.every().monday.at("10:00").do(resumo_semanal)
    while True:
        schedule.run_pending()
        time.sleep(30)

thread = threading.Thread(target=iniciar_agendador, daemon=True)
thread.start()

# ==========================================
# ROTAS
# ==========================================

@app.get("/")
def home():
    return {"status": "servidor rodando", "hora_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}

@app.get("/ping")
def ping():
    """UptimeRobot bate aqui a cada 5 minutos para manter o servidor vivo."""
    return {"status": "ok", "hora_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}

@app.post("/disparar-lembrete")
def disparar_lembrete():
    """Render Cron Job chama este endpoint todo dia útil às 11:30 UTC."""
    try:
        if datetime.utcnow().weekday() < 5:
            verificar_contas()
            return {"status": "lembrete enviado", "hora_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
        return {"status": "fim de semana, ignorado"}
    except Exception as e:
        print(f"Erro no lembrete: {e}")
        return {"status": "erro", "detalhe": str(e)}

@app.post("/disparar-resumo")
def disparar_resumo():
    """Render Cron Job chama este endpoint toda segunda às 10:00 UTC."""
    try:
        resumo_semanal()
        return {"status": "resumo enviado", "hora_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
    except Exception as e:
        print(f"Erro no resumo: {e}")
        return {"status": "erro", "detalhe": str(e)}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print(f"JSON recebido: {data}")

    try:
        inner = data.get("data", {})

        if inner.get("key", {}).get("fromMe"):
            return {"status": "ignored"}

        mensagem = (
            inner.get("msgContent", {}).get("conversation") or
            inner.get("msgContent", {}).get("extendedTextMessage", {}).get("text") or
            inner.get("message", {}).get("conversation") or
            inner.get("message", {}).get("extendedTextMessage", {}).get("text") or
            ""
        )

        if not mensagem:
            return {"status": "sem mensagem de texto"}

        remetente = inner.get("key", {}).get("remoteJid", "")

        numero_limpo = remetente.replace("@s.whatsapp.net", "").replace("@lid", "")
        if not any(auth in numero_limpo for auth in NUMEROS_AUTORIZADOS):
            print(f"Ignorado: {remetente}")
            return {"status": "ignorado"}

        print(f"Mensagem de {remetente}: {mensagem}")

        resultado = processar_mensagem(mensagem)

        if resultado and "erro" not in resultado:
            if resultado.get("confirmado"):
                valor_pago = resultado.get("valor_pago")
                if valor_pago:
                    msg = f"✅ Pagamento confirmado!\n*{resultado.get('empresa')} · {resultado.get('imposto')}*\nValor pago: R$ {valor_pago:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                else:
                    msg = f"✅ Pagamento confirmado!\n*{resultado.get('empresa')} · {resultado.get('imposto')}*"
                enviar_mensagem(remetente, msg)
            else:
                msg = (
                    f"✅ Conta cadastrada!\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🏢 *{resultado.get('empresa')}* · {resultado.get('descricao')}\n"
                    f"📅 Venc: {resultado.get('vencimento')}\n"
                    f"💰 R$ {resultado.get('valor'):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
                enviar_mensagem(remetente, msg)
        elif resultado and "erro" in resultado:
            enviar_mensagem(remetente, resultado.get("erro"))

        return {"status": "ok"}

    except Exception as e:
        print(f"Erro: {e}")
        return {"status": "erro", "detalhe": str(e)}