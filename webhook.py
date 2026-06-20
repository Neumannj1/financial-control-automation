# ==========================================
# WEBHOOK.PY — Servidor FastAPI
# ==========================================

from fastapi import FastAPI, Request
from main import processar_mensagem

app = FastAPI()

@app.get("/")
def home():
    return {"status": "servidor rodando"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print(f"JSON recebido: {data}")

    try:
        # Ignora mensagens enviadas por mim
        if data.get("key", {}).get("fromMe"):
            return {"status": "ignored"}

        # Extrai a mensagem
        message = data.get("message", {})

        mensagem = (
            message.get("conversation") or
            message.get("extendedTextMessage", {}).get("text") or
            ""
        )

        if not mensagem:
            return {"status": "sem mensagem de texto"}

        remetente = data.get("key", {}).get("remoteJid", "")
        print(f"Mensagem recebida de {remetente}: {mensagem}")

        processar_mensagem(mensagem)

        return {"status": "ok"}

    except Exception as e:
        print(f"Erro: {e}")
        return {"status": "erro", "detalhe": str(e)}