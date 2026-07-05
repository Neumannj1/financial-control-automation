# ==========================================
# PARSER FINANCEIRO v4
# - Sinônimos de "adicionar"
# - Lista completa de impostos brasileiros
# ==========================================

EMPRESAS = [
    "MATRIZ", "PARAUAPEBAS", "MAGNAPR", "MAGNASP",
    "ROL", "PSP", "TRIPORT", "LIDERLIK",
    "PORTER", "OBV", "SANGA", "FILIAL"
]

# ── Ações: sinônimos aceitos ──────────────────────────────
PALAVRAS_SAIDA = [
    "adicionar", "adiciona", "add",
    "incluir", "inclui", "inclua",
    "inserir", "insere", "insira",
    "cadastrar", "cadastra", "cadastre",
    "lancar", "lançar", "lanca", "lança",
    "registrar", "registra", "registre",
    "novo", "nova", "criar", "cria",
    "gastei",
]

PALAVRAS_ENTRADA = ["recebi", "entrou", "recebimento"]

PALAVRAS_CONFIRMACAO = [
    "paguei", "pagar", "pago",
    "confirmei", "confirmar", "confirma",
    "quitei", "quitar", "quita",
    "baixar", "baixa",
]

# ── Comandos de consulta (o bot responde na hora) ─────────
PALAVRAS_RELATORIO = ["relatorio", "relatório", "relatorios", "vencimentos", "vencendo"]
PALAVRAS_RESUMO    = ["resumo", "resumao", "resumão", "geral", "situacao", "situação"]

# ── Impostos e tributos brasileiros ───────────────────────
# Federais, estaduais, municipais + novos da Reforma Tributária
IMPOSTOS_VALIDOS = [
    # Federais
    "IRPJ", "IRPF", "IR", "CSLL", "PIS", "PASEP", "COFINS",
    "IPI", "IOF", "II", "IE", "ITR", "CIDE", "INSS", "CPP", "FGTS",
    # Estaduais
    "ICMS", "IPVA", "ITCMD", "DIFAL",
    # Municipais
    "ISS", "ISSQN", "IPTU", "ITBI",
    # Reforma Tributária (transição a partir de 2026)
    "CBS", "IBS", "IS",
    # Simples Nacional / MEI
    "DAS", "SIMPLES", "DASN",
    # Outros comuns em controle fiscal
    "FUNRURAL", "SENAI", "SESI", "SESC", "SENAC", "INCRA",
]

# Sinônimos/variações que mapeiam para um imposto padrão
ALIAS_IMPOSTOS = {
    "SIMPLES": "DAS",
    "SIMPLESNACIONAL": "DAS",
    "IR": "IRPJ",
    "PASEP": "PIS",
    "ISSQN": "ISS",
}

CATEGORIAS = {
    "Imposto": [i.lower() for i in IMPOSTOS_VALIDOS],
    "Fornecedor": ["fornecedor", "nota", "nf"],
    "Alimentação": ["mercado", "ifood", "restaurante"],
    "Transporte": ["uber", "gasolina", "combustivel"],
}

MENSAGEM_AJUDA = (
    "🤖 *Bot Financeiro*\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "Não entendi sua mensagem. Veja os comandos:\n\n"
    "➕ *Cadastrar conta:*\n"
    "`adicionar EMPRESA IMPOSTO DD/MM VALOR`\n"
    "_Ex: adicionar BRIGHTLED ICMS 30/06 850_\n\n"
    "✅ *Confirmar pagamento:*\n"
    "`paguei EMPRESA IMPOSTO`\n"
    "_Ex: paguei BRIGHTLED ICMS_\n\n"
    "✅ *Confirmar com valor pago:*\n"
    "`paguei EMPRESA IMPOSTO VALOR`\n"
    "_Ex: paguei BRIGHTLED ICMS 850_\n\n"
    "📊 *Consultar:*\n"
    "`relatorio` — contas vencendo e atrasadas\n"
    "`resumo` — visão geral (pagas e pendentes)\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "💡 Você pode usar: adicionar, incluir, inserir,\n"
    "cadastrar, lançar, registrar...\n\n"
    "Empresas cadastradas:\n"
    f"_{', '.join(EMPRESAS)}_"
)

def identificar_categoria(descricao):
    for categoria, palavras in CATEGORIAS.items():
        if descricao.lower() in palavras:
            return categoria
    return "Outros"

def identificar_empresa(partes):
    for parte in partes:
        if parte.upper() in EMPRESAS:
            return parte.upper()
    return None

def normalizar_imposto(imposto):
    """Padroniza sinônimos de impostos (ex: SIMPLES -> DAS)."""
    imp = imposto.upper()
    return ALIAS_IMPOSTOS.get(imp, imp)

def limpar_valor(valor_str):
    """Converte texto em float aceitando '5000', 'R$5000', 'R$ 5.000,00', '1.200,50' etc.
    Retorna None se não for um número válido."""
    s = str(valor_str).strip()
    if not s:
        return None
    s = s.replace("R$", "").replace("r$", "").replace(" ", "").strip()
    # Formato brasileiro com vírgula decimal: 5.000,00 -> 5000.00
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None

def parsear_mensagem(mensagem):
    partes = mensagem.strip().split()

    if not partes:
        return {"erro": MENSAGEM_AJUDA, "ajuda": True}

    # Junta "R$" solto com o número seguinte: ["R$", "5.000,00"] -> ["R$5.000,00"]
    partes_juntas = []
    i = 0
    while i < len(partes):
        atual = partes[i]
        if atual.upper() in ("R$", "RS") and i + 1 < len(partes):
            partes_juntas.append(atual + partes[i + 1])
            i += 2
        else:
            partes_juntas.append(atual)
            i += 1
    partes = partes_juntas

    acao = partes[0].lower()

    # ── Comandos de consulta ──────────────────────────────
    if acao in PALAVRAS_RELATORIO:
        return {"acao": "consulta_relatorio"}
    if acao in PALAVRAS_RESUMO:
        return {"acao": "consulta_resumo"}

    if acao not in PALAVRAS_SAIDA + PALAVRAS_ENTRADA + PALAVRAS_CONFIRMACAO:
        return {"erro": MENSAGEM_AJUDA, "ajuda": True}

    # ── Confirmação de pagamento ──────────────────────────
    if acao in PALAVRAS_CONFIRMACAO:
        if len(partes) < 3:
            return {"erro": "Formato inválido. Use:\n`paguei EMPRESA IMPOSTO` ou `paguei EMPRESA IMPOSTO VALOR`\n_Ex: paguei BRIGHTLED ICMS 850_"}

        empresa = identificar_empresa(partes)
        if not empresa:
            return {"erro": f"Empresa não encontrada. Empresas válidas:\n_{', '.join(EMPRESAS)}_"}

        partes_restantes = [p for p in partes[1:] if p.upper() != empresa]
        imposto = normalizar_imposto(partes_restantes[0])

        valor_pago = None
        if len(partes_restantes) >= 2:
            valor_pago = limpar_valor(partes_restantes[1])
            if valor_pago is None:
                return {"erro": f"Valor '{partes_restantes[1]}' inválido. Use números.\n_Ex: paguei BRIGHTLED ICMS 850_"}

        return {
            "acao":       "confirmar",
            "empresa":    empresa,
            "imposto":    imposto,
            "valor_pago": valor_pago
        }

    # ── Cadastro de conta ─────────────────────────────────
    if acao in PALAVRAS_SAIDA:
        tipo = "Saida"
    else:
        tipo = "Entrada"

    empresa = identificar_empresa(partes)
    if not empresa:
        return {"erro": f"Empresa não encontrada. Empresas válidas:\n_{', '.join(EMPRESAS)}_"}

    partes_restantes = [p for p in partes[1:] if p.upper() != empresa]

    if len(partes_restantes) < 3:
        return {"erro": "Faltam informações. Use:\n`adicionar EMPRESA IMPOSTO DD/MM VALOR`\n_Ex: adicionar BRIGHTLED ICMS 30/06 850_"}

    descricao  = normalizar_imposto(partes_restantes[0])
    vencimento = partes_restantes[1]
    valor_str  = partes_restantes[2]

    valor = limpar_valor(valor_str)
    if valor is None:
        return {"erro": f"Valor '{valor_str}' inválido. Use números.\n_Ex: adicionar BRIGHTLED ICMS 30/06 850_"}

    categoria = identificar_categoria(descricao)

    return {
        "tipo":       tipo,
        "empresa":    empresa,
        "descricao":  descricao,
        "vencimento": vencimento,
        "valor":      valor,
        "categoria":  categoria,
        "status":     "Pendente"
    }