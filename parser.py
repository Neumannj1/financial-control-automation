# ==========================================
# PARSER FINANCEIRO v2 — com empresas
# ==========================================

# Apelidos das empresas (virão do Sheets futuramente)
# Por enquanto fixo aqui para testar
EMPRESAS = [
    "QUANTUM", "VELOZ", "SABOR", "HORIZONTE",
    "NEXO", "METAL", "BEMESTAR", "ESTRELA",
    "LETRA", "SENTINELA", "ESTILO", "AGUIA"
]

# Tipos de transação
PALAVRAS_SAIDA        = ["adicionar", "gastei"]
PALAVRAS_ENTRADA      = ["recebi", "entrou"]
PALAVRAS_CONFIRMACAO  = ["paguei", "confirmei", "quitei"]

# Categorias
CATEGORIAS = {
    "Imposto":      ["icms", "iss", "irpj", "csll", "pis", "cofins"],
    "Fornecedor":   ["fornecedor", "nota", "nf"],
    "Alimentação":  ["mercado", "ifood", "restaurante"],
    "Transporte":   ["uber", "gasolina", "combustivel"],
}

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

def parsear_mensagem(mensagem):
    partes = mensagem.strip().split()

    acao = partes[0].lower()

    if acao in PALAVRAS_CONFIRMACAO and len(partes) < 3:
        return {"erro": "Formato inválido. Para confirmar pagamento use: paguei EMPRESA IMPOSTO\nEx: paguei QUANTUM ICMS"}

    if acao not in PALAVRAS_CONFIRMACAO and len(partes) < 4:
        return {"erro": "Formato inválido. Para cadastrar use: adicionar EMPRESA IMPOSTO DATA VALOR\nEx: adicionar QUANTUM ICMS 30/06 850"}

    # Identifica tipo
    if acao in PALAVRAS_CONFIRMACAO:
        empresa = identificar_empresa(partes)
        if not empresa:
            return {"erro": f"Empresa não encontrada. Empresas válidas: {', '.join(EMPRESAS)}"}
        descricao = [p for p in partes[1:] if p.upper() != empresa][0]
        return {
            "acao":    "confirmar",
            "empresa": empresa,
            "imposto": descricao.upper()
        }

    if acao in PALAVRAS_SAIDA:
        tipo = "Saida"
    elif acao in PALAVRAS_ENTRADA:
        tipo = "Entrada"
    else:
        return {"erro": f"Ação '{acao}' não reconhecida. Use: adicionar, paguei, recebi"}

    # Identifica empresa
    empresa = identificar_empresa(partes)
    if not empresa:
        return {"erro": f"Empresa não encontrada. Empresas válidas: {', '.join(EMPRESAS)}"}

    # Remove ação e empresa das partes para pegar o resto
    partes_restantes = [p for p in partes[1:] if p.upper() != empresa]

    if len(partes_restantes) < 3:
        return {"erro": "Faltam informações. Ex: adicionar QUANTUM ICMS 20/06 850"}

    descricao  = partes_restantes[0]
    vencimento = partes_restantes[1]
    valor_str  = partes_restantes[2]

    # Valida valor
    try:
        valor = float(valor_str.replace(",", "."))
    except ValueError:
        return {"erro": f"Valor '{valor_str}' inválido. Use números. Ex: 850 ou 1200,50"}

    categoria = identificar_categoria(descricao)

    if acao in PALAVRAS_CONFIRMACAO:
        return {
            "acao":    "confirmar",
            "empresa": empresa,
            "imposto": descricao.upper()
        }

    return {
        "tipo":       tipo,
        "empresa":    empresa,
        "descricao":  descricao.upper(),
        "vencimento": vencimento,
        "valor":      valor,
        "categoria":  categoria,
        "status":     "Pendente"
    }


# ==========================================
# TESTES
# ==========================================

mensagens_teste = [
    "adicionar QUANTUM ICMS 20/06 850",
    "adicionar VELOZ ISS 15/06 320",
    "adicionar SABOR fornecedor 22/06 1200,50",
    "adicionar NEXO ICMS 10/06 abc",
    "adicionar INVALIDA ICMS 10/06 500",
    "oi tudo bem",
]

for msg in mensagens_teste:
    resultado = parsear_mensagem(msg)
    print(f"Mensagem : '{msg}'")
    print(f"Resultado: {resultado}")
    print("---")