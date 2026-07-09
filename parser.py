# ==========================================
# WEBHOOK.PY — Servidor FastAPI + Agendador
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
# AGENDADOR
# ==========================================

def rodar_lembrete():
    if datetime.now().weekday() < 5:
        print(f"Rodando lembrete: {datetime.now()}")
        verificar_contas()

def iniciar_agendador():
    schedule.every().day.at("11:30").do(rodar_lembrete)      # 08:30 Brasilia
    schedule.every().monday.at("10:00").do(resumo_semanal)   # 07:00 Brasilia
    while True:
        schedule.run_pending()
        time.sleep(30)

thread = threading.Thread(target=iniciar_agendador, daemon=True)
thread.start()

# ==========================================
# FORMATACAO DAS RESPOSTAS
# ==========================================

def formatar_valor(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"R$ {valor}"

def montar_resposta(resultado):
    """Recebe o dicionario do processar_mensagem e devolve o texto para o WhatsApp."""

    # 1) Erro / duplicata / ajuda  → SEMPRE tem prioridade
    if "erro" in resultado:
        return resultado["erro"]

    # 2) Resposta de consulta (relatorio / resumo)
    if "resposta_texto" in resultado:
        return resultado["resposta_texto"]

    # 3) Confirmacao de pagamento
    if resultado.get("confirmado"):
        texto = (
            "✅ Pagamento confirmado!\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🏢 {resultado.get('empresa')} · {resultado.get('imposto')}"
        )
        if resultado.get("valor_pago"):
            texto += f"\n💰 Pago: {formatar_valor(resultado['valor_pago'])}"
        return texto

    # 4) Cadastro de conta
    if resultado.get("empresa"):
        texto = (
            "✅ Conta cadastrada!\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🏢 {resultado.get('empresa')} · {resultado.get('descricao')}\n"
            f"📅 Venc: {resultado.get('vencimento')}\n"
            f"💰 {formatar_valor(resultado.get('valor'))}"
        )
        # Alerta suave se o imposto não é reconhecido (não impede o cadastro)
        if resultado.get("alerta_imposto"):
            texto += f"\n\n{resultado['alerta_imposto']}"
        return texto

    # 5) Fallback
    return "✅ Processado."

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

        # Filtra apenas numeros autorizados
        numero_limpo = remetente.replace("@s.whatsapp.net", "").replace("@lid", "")
        if not any(auth in numero_limpo for auth in NUMEROS_AUTORIZADOS):
            print(f"Ignorado: {remetente}")
            return {"status": "ignorado"}

        print(f"Mensagem de {remetente}: {mensagem}")
        print(f"Mensagem recebida: '{mensagem}'")

        resultado = processar_mensagem(mensagem)
        resposta = montar_resposta(resultado)
        enviar_mensagem(remetente, resposta)

        return {"status": "ok"}

    except Exception as e:
        print(f"Erro: {e}")
        return {"status": "erro", "detalhe": str(e)}