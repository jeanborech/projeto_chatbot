from openai import OpenAI
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

# Cria o cliente da OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Resto do código...

def geracao_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens,
        model="gpt-3.5-turbo-0125",
        max_tokens=1000,
        temperature=0,
        stream=True
    )
    print("Bot:", end="")
    texto_completo = ""
    for resposta_stream in resposta:
        texto = resposta_stream.choices[0].delta.content
        if texto:
            print(texto, end="")
            texto_completo += texto
            
    print()
    mensagens.append({"role":"assistant", "content":texto_completo})
    return mensagens

if __name__ == "__main__":
    print("Bem vindo ao Chatbot")
    mensagens = []
    while True:
        in_user = input("User:")
        mensagens.append({"role": "user", "content":in_user})
        mensagens = geracao_texto(mensagens)