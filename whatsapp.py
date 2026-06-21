# ==========================================
# WHATSAPP.PY — Envio de mensagens via WAME API
# ==========================================

import requests

WAME_KEY = "3382xe251895ba0"
WAME_URL = f"https://us.api-wa.me/{WAME_KEY}/message/text"

def enviar_mensagem(numero, texto):
    payload = {
        "to": numero,
        "text": texto
    }
    try:
        response = requests.post(WAME_URL, json=payload)
        print(f"✅ Mensagem enviada para {numero}: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return None