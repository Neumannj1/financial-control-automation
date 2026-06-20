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
        print(f"Mensagem recebida de {remetente}: {mensagem}")

        processar_mensagem(mensagem)

        return {"status": "ok"}

    except Exception as e:
        print(f"Erro: {e}")
        return {"status": "erro", "detalhe": str(e)}