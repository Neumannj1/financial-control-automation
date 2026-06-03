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

    try:
        # Extrai a mensagem do JSON da Z-API
        mensagem = data["body"]["text"]["message"]
        remetente = data["body"]["from"]

        print(f"Mensagem recebida de {remetente}: {mensagem}")

        # Processa a mensagem
        processar_mensagem(mensagem)

        return {"status": "ok"}

    except KeyError:
        return {"status": "erro", "detalhe": "formato de mensagem inválido"}