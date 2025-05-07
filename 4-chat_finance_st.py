import time
import streamlit as st
import json
import openai
from dotenv import load_dotenv, find_dotenv
# import yfinance as yf

from alpha_vantage.timeseries import TimeSeries
import os


# Carregar variáveis de ambiente
_ = load_dotenv(find_dotenv())

# API Key da Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Configuração do cliente OpenAI
client = openai.Client()

# Nova função usando Alpha Vantage
def retorna_cotacao(ticker, periodo="1mo", tentativas=3, espera=5):
    try:
        ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
        simbolo = f"{ticker}.SA"  # Formato para ações brasileiras
        dados, _ = ts.get_daily(symbol=simbolo, outputsize="compact")
        dados = dados["4. close"]
        dados.index = dados.index.strftime("%Y-%m-%d")
        dados = dados.sort_index().tail(30)
        return json.dumps(dados.to_dict())
    except Exception as e:
        return json.dumps({"erro": f"Erro ao buscar dados: {str(e)}"})


# Função para buscar cotações do yfinance do YAHOO
#def retorna_cotacao(ticker, periodo="1mo", tentativas=3, espera=5):
#    for tentativa in range(tentativas):
#        try:
#            ticker_obj = yf.Ticker(f"{ticker}.SA")
#            hist = ticker_obj.history(period=periodo)["Close"]
#            hist.index = hist.index.map(lambda x: x.strftime("%Y-%m-%d"))
#            hist = round(hist, 2)
#            if len(hist) > 30:
#                slice_size = int(len(hist) / 30)
#                hist = hist.iloc[::-slice_size][::-1]
#            return hist.to_json()
#        except openai.RateLimitError:
#            if tentativa < tentativas - 1:
#                time.sleep(espera)
#            else:
#                return json.dumps({"erro": "Limite de requisições atingido. Tente novamente em alguns minutos."})
#        except Exception as e:
#            return json.dumps({"erro": f"Erro ao buscar dados: {str(e)}"})


# Ferramentas disponíveis
tools = [
    {
        "type": "function",
        "function": {
            "name": "retorna_cotacao",
            "description": "Retorna a cotação de ações da Ibovespa",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": 
                        "O ticker da ação. Ex: BBAS3, ITSA4, etc"
                    },
                    "periodo": {
                        "type": "string",
                        "description": 
            "Período dos dados históricos: '1d', '5d', '1mo', etc.",
                        "enum": ["compact", "full"]

                    }
                }
            }
        }
    }
]

funcoes_disponiveis = {"retorna_cotacao": retorna_cotacao}

# Função para gerar texto
def gera_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens,
        model="gpt-3.5-turbo-0125",
        tools=tools,
        tool_choice="auto"
    )
    tool_calls = resposta.choices[0].message.tool_calls

    if tool_calls:
        mensagens.append(resposta.choices[0].message.to_dict())
        for tool_call in tool_calls:
            fc_name = tool_call.function.name
            fc_to_call = funcoes_disponiveis[fc_name]
            fc_args = json.loads(tool_call.function.arguments)
            fc_return = fc_to_call(**fc_args)
            mensagens.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": fc_name,
                "content": fc_return
            })
        segunda_resposta = client.chat.completions.create(
            messages=mensagens,
            model="gpt-3.5-turbo-0125"
        )
        mensagens.append(segunda_resposta.choices[0].message.to_dict())
    
    return mensagens

# Configuração da interface do Streamlit
st.set_page_config(page_title="Chatbot com Ações", page_icon="🤖")

# Título
st.title("Chatbot de Cotações de Ações 📈")

# Inicializa o estado das mensagens
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Exibição do histórico de mensagens
for msg in st.session_state.mensagens:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").markdown(msg["content"])
    # elif msg["role"] == "tool":
    #     st.chat_message("assistant").markdown(f"**Ferramenta:** {msg['content']}")

# Entrada de mensagem do usuário
user_input = st.chat_input("Digite sua pergunta sobre cotações de ações...")
if user_input:
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.mensagens.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)
    
    # Processa a mensagem
    st.session_state.mensagens = gera_texto(st.session_state.mensagens)

    # Exibe a resposta do chatbot
    ultima_mensagem = st.session_state.mensagens[-1]
    if ultima_mensagem["role"] == "assistant":
        st.chat_message("assistant").markdown(ultima_mensagem["content"])




