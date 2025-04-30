from openai import OpenAI
from dotenv import load_dotenv
import os
from colorama import Fore, Style, init

# Carrega as variáveis do arquivo .env
load_dotenv()

# Cria o cliente da OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Resto do código...

#inicializando o colorama
init(autoreset=True)

def geracao_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens,
        model="gpt-3.5-turbo-0125",
        max_tokens=1000,
        temperature=0,
        stream=True
    )
    print(f"{Fore.CYAN} Bot:", end="")
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
    print(f"{Fore.YELLOW} Bem vindo ao Chatbot")
    mensagens = []
    while True:
        in_user = input(f"{Fore.GREEN} User: {Style.RESET_ALL}")
        mensagens.append({"role": "user", "content":in_user})
        mensagens = geracao_texto(mensagens)