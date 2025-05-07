import datetime
import re
import streamlit as st
import sys
from pathlib import Path
from entities.cliente import ClienteHandler
from entities.produto import ProdutoHandler
from entities.endereco import EnderecoHandler
from services.api_service import APIService
from utils.formatters import (
    formatar_cliente_detalhado,
    formatar_clientes,
    formatar_produto_detalhado,
    formatar_produtos,
    formatar_enderecos,
)

# ================== CONFIGURAÇÃO INICIAL ==================
# Adiciona o diretório raiz ao caminho de importação
sys.path.append(str(Path(__file__).parent.parent))

BASE_URL = "https://4dd2-186-235-59-239.ngrok-free.app"

# ================== DICIONÁRIOS E CONSTANTES ==================
AJUDA_ESPECIFICA = {
    "cliente": """
    **Ajuda sobre Clientes** 📋
    Comandos disponíveis:
    • `clientes` - Lista todos
    • `cliente com nome [X]` - Filtra por nome
    • `cliente com CNPJ [X]` - Busca por CNPJ exato
    • `cliente com telefone [X]` - Busca por telefone
    • `cliente com email [X]` - Busca por e-mail
    """,
    "produto": """
    **Ajuda sobre Produtos** 🛍️
    Comandos disponíveis:
    • `produtos` - Lista todos
    • `produto com código [X]` - Busca por código exato
    • `produto com valor entre [X] e [Y]` - Faixa de preço
    • `produtos com estoque abaixo de [X]` - Filtra por estoque
    """,
    "endereco": """
**Ajuda sobre Endereços** 🏠
Comandos disponíveis:
• `endereços` - Lista todos
• `endereços na cidade [X]` - Filtra por cidade
• `endereços no estado [X]` - Filtra por UF
• `endereços com CEP [X]` - Busca por CEP exato
• `endereços na rua [X]` - Filtra por nome da rua
• `endereços no bairro [X]` - Filtra por bairro
""",
}

SAUDACOES = ["oi", "olá", "ola", "eae", "ei", "bom dia", "boa tarde", "boa noite"]
DESPEDIDAS = ["tchau", "adeus", "até mais", "flw", "bye"]

st.set_page_config(page_title="Chatbot Teste", page_icon="🤖")

# ================== MEMÓRIA DE CONVERSA ==================
if "historico" not in st.session_state:
    st.session_state.historico = {"ultimo_topico": None, "detalhes_consulta": {}}

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []


# ================== FUNÇÕES AUXILIARES ==================
@st.cache_resource
def inicializar_servicos():
    api = APIService(BASE_URL)
    return {
        "cliente": ClienteHandler(api),
        "produto": ProdutoHandler(api),
        "endereco": EnderecoHandler(api),
    }


servicos = inicializar_servicos()


def atualizar_contexto(topico=None, detalhes=None):
    if topico:
        st.session_state.historico["ultimo_topico"] = topico
    if detalhes:
        st.session_state.historico["detalhes_consulta"].update(detalhes)


def verificar_saudacao(mensagem):
    mensagem = mensagem.lower().strip()
    for palavra in SAUDACOES + DESPEDIDAS:
        if mensagem.startswith(palavra):
            return True
    return False


def sugerir_ajuda(topico):
    return f"💡 Experimente 'ajuda {topico}' para mais comandos." if topico else ""


# ================== LÓGICA PRINCIPAL ==================
def processar_pergunta(pergunta):
    pergunta = pergunta.lower().strip()
    ctx = st.session_state.historico

    # ------ Tratamento de Saudações/Despedidas ------
    if verificar_saudacao(pergunta):
        if any(p in pergunta for p in DESPEDIDAS):
            return "Até logo! 👋 Volte quando precisar!"
        
        hora_atual = datetime.datetime.now().hour
        periodo = "boa noite" if hora_atual >= 18 else "boa tarde" if hora_atual >= 12 else "bom dia"
        titulos_ajuda = ["Clientes 📋", "Produtos 🛍️", "Endereços 🏠"]
        
        return (
            f"{periodo.capitalize()}! 👋\nSou seu assistente. Posso ajudar com:\n\n"
            f"- {titulos_ajuda[0]}\n"
            f"- {titulos_ajuda[1]}\n"
            f"- {titulos_ajuda[2]}"
        )

    # ... (restante da função permanece igual)

    # ------ Comandos de Ajuda ------
    if "ajuda" in pergunta:
        if "cliente" in pergunta:
            atualizar_contexto("cliente")
            return AJUDA_ESPECIFICA["cliente"]
        elif "produto" in pergunta:
            atualizar_contexto("produto")
            return AJUDA_ESPECIFICA["produto"]
        elif "endereço" in pergunta or "endereco" in pergunta:
            atualizar_contexto("endereco")
            return AJUDA_ESPECIFICA["endereco"]
        else:
            return (
                "Digite:\n- `ajuda clientes`\n- `ajuda produtos`\n- `ajuda endereços`"
            )

    # ------ Processamento Normal ------
    resposta = ""

    # CLIENTES
    if "cliente" in pergunta:
        atualizar_contexto("cliente")
        clientes = servicos["cliente"].buscar_todos()

        # Filtros detalhados
        if "cnpj" in pergunta:
            cnpj = re.search(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}", pergunta)
            if cnpj:
                clientes = [c for c in clientes if c["cnpj"] == cnpj.group()]
                if len(clientes) == 1:
                    return formatar_cliente_detalhado(clientes[0])

        elif "telefone" in pergunta:
            telefone = re.search(r"\(\d{2}\) \d{4,5}-\d{4}", pergunta)
            if telefone:
                clientes = [c for c in clientes if telefone.group() in c["telefone"]]

        elif "email" in pergunta or "e-mail" in pergunta:
            email = pergunta.split("@")[1] if "@" in pergunta else pergunta.split()[-1]
            clientes = [c for c in clientes if email.lower() in c["email"].lower()]

        # Filtros básicos
        elif "com nome" in pergunta:
            nome = pergunta.split("com nome")[-1].strip()
            clientes = [c for c in clientes if nome.lower() in c["nomeEmpresa"].lower()]

        elif "nome" in pergunta:
            return "\n".join([c["nomeEmpresa"] for c in clientes])

        elif "cnpj" in pergunta:
            return "\n".join([c["cnpj"] for c in clientes])

        resposta = formatar_clientes(clientes)

    # PRODUTOS
    elif "produto" in pergunta:
        atualizar_contexto("produto")
        produtos = servicos["produto"].buscar_todos()

        # Filtros detalhados
        if "código" in pergunta or "codigo" in pergunta:
            codigo = (
                pergunta.split("código")[-1].strip()
                if "código" in pergunta
                else pergunta.split("codigo")[-1].strip()
            )
            produtos = [
                p for p in produtos if p["codigoProduto"].lower() == codigo.lower()
            ]
            if len(produtos) == 1:
                return formatar_produto_detalhado(produtos[0])

        elif "valor entre" in pergunta:
            valores = re.findall(r"\d+\.?\d*", pergunta)
            if len(valores) == 2:
                min_val, max_val = map(float, valores)
                produtos = [
                    p
                    for p in produtos
                    if min_val <= float(p["valorUnitario"]) <= max_val
                ]

        # Filtros básicos
        elif "descrição" in pergunta or "descricao" in pergunta:
            return "\n".join([p["descricao"] for p in produtos])

        elif "valor" in pergunta:
            return "\n".join(
                [f'{p["descricao"]}: R$ {p["valorUnitario"]}' for p in produtos]
            )

        resposta = formatar_produtos(produtos)

    # ENDEREÇOS
    elif "endereço" in pergunta or "endereco" in pergunta:
        atualizar_contexto("endereco")
        enderecos = servicos["endereco"].buscar_todos()

        # Filtros detalhados
        if "cep" in pergunta:
            cep = re.search(r"\d{5}-?\d{3}", pergunta)
            if cep:
                enderecos = [e for e in enderecos if e["cep"] == cep.group()]

        elif "rua" in pergunta:
            rua = pergunta.split("rua")[-1].strip()
            enderecos = [e for e in enderecos if rua.lower() in e["rua"].lower()]

        elif "bairro" in pergunta:
            bairro = pergunta.split("bairro")[-1].strip()
            enderecos = [e for e in enderecos if bairro.lower() in e["bairro"].lower()]

        # Filtros básicos
        elif "cidade" in pergunta:
            cidade = pergunta.split("cidade")[-1].strip()
            enderecos = [e for e in enderecos if cidade.lower() in e["cidade"].lower()]

        resposta = formatar_enderecos(enderecos)

    # ------ Finalização ------
    if resposta:
        if ctx["ultimo_topico"]:
            resposta = f"**Sobre {ctx['ultimo_topico']}**:\n\n{resposta}"
        return resposta + "\n\n" + sugerir_ajuda(ctx["ultimo_topico"])

    return "Desculpe, não entendi. Tente perguntas como:\n- Mostrar cliente com nome João\n- Buscar produto com código P123\n- Endereço da cidade São Paulo"


# ================== INTERFACE STREAMLIT ==================
st.title("Chatbot de Dados da Aplicação 💬")

for msg in st.session_state.mensagens:
    st.chat_message(msg["role"]).markdown(msg["content"])

user_input = st.chat_input("Pergunte sobre clientes, produtos ou endereços:")
if user_input:
    st.session_state.mensagens.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    resposta = processar_pergunta(user_input)
    st.session_state.mensagens.append({"role": "assistant", "content": resposta})
    st.chat_message("assistant").markdown(resposta)
