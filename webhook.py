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
    "5541998495077",  # financeiro
    "5541998866873",  # Jean - testes
]
# AGENDADOR
# ==========================================

def rodar_lembrete():
    if datetime.now().weekday() < 5:
        print(f"Rodando lembrete: {datetime.now()}")
        verificar_contas()

def iniciar_agendador():
    schedule.every().day.at("08:30").do(rodar_lembrete)
    schedule.every().monday.at("07:00").do(resumo_semanal)
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
    return {"status": "servidor rodando"}

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

        # Filtra apenas números autorizados
        numero_limpo = remetente.replace("@s.whatsapp.net", "").replace("@lid", "")
        if not any(auth in numero_limpo for auth in NUMEROS_AUTORIZADOS):
            print(f"Ignorado: {remetente}")
            return {"status": "ignorado"}

        print(f"Mensagem recebida de {remetente}: {mensagem}")

        resultado = processar_mensagem(mensagem)

        if resultado and "erro" not in resultado:
            if resultado.get("confirmado"):
                enviar_mensagem(remetente, f"Pagamento confirmado: {resultado.get('empresa')} - {resultado.get('imposto')}")
            else:
                enviar_mensagem(remetente, f"Conta cadastrada: {resultado.get('empresa')} - {resultado.get('descricao')} - R${resultado.get('valor')} - Venc: {resultado.get('vencimento')}")
        elif resultado and "erro" in resultado:
            enviar_mensagem(remetente, f"{resultado.get('erro')}")

        return {"status": "ok"}

    except Exception as e:
        print(f"Erro: {e}")
        return {"status": "erro", "detalhe": str(e)}