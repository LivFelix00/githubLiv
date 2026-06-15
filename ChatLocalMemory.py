import argparse
import requests
import os

API_URL = "http://10.16.6.8:11434/api/generate"
MODEL_NAME = "gpt-oss:20b"

MEMORY_FILE = "memory.txt"

#Memória de conversa (curto prazo)
historico = []
MAX_MENSAGENS = 6


# MEMÓRIA LOCAL (BASE FIXA)

def carregar_memoria_local():
    if not os.path.exists(MEMORY_FILE):
        return {}

    memoria = {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        for linha in f:
            if "|" in linha:
                chave, valor = linha.strip().split("|", 1)
                memoria[chave.lower()] = valor
    return memoria


def buscar_resposta_memoria(pergunta, memoria):
    pergunta = pergunta.lower()

    for chave in memoria:
        if chave in pergunta:
            return memoria[chave]

    return None


# JANELA DE CONTEXTO

def montar_prompt_com_contexto(nova_mensagem: str) -> str:
    contexto = ""

    for msg in historico:
        contexto += msg + "\n"

    contexto += f"Usuário: {nova_mensagem}\nAssistente:"
    return contexto


def atualizar_memoria(usuario_msg: str, resposta: str):
    historico.append(f"Usuário: {usuario_msg}")
    historico.append(f"Assistente: {resposta}")

    # Limita o tamanho da memória
    if len(historico) > MAX_MENSAGENS * 2:
        historico.pop(0)
        historico.pop(0)


# CHAMADA À API

def enviar_prompt(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        resposta = requests.post(API_URL, json=payload, timeout=50)
        resposta.raise_for_status()
        return resposta.json().get("response", "Sem resposta da API")
    except requests.exceptions.RequestException as erro:
        return f"Erro na requisição: {erro}"


# CHAT INTELIGENTE
def chat():
    memoria_local = carregar_memoria_local()

    print("💬 Chat iniciado (digite 'sair' para encerrar)\n")

    while True:
        entrada = input("Você: ")

        if entrada.lower() == "sair":
            break

        #  1. Verifica memória local primeiro
        resposta_memoria = buscar_resposta_memoria(entrada, memoria_local)

        if resposta_memoria:
            resposta = resposta_memoria
            print(f" (Memória local)\nIA: {resposta}\n")
        else:
            #  2. Usa IA com contexto
            prompt = montar_prompt_com_contexto(entrada)
            resposta = enviar_prompt(prompt)

            print(f" IA: {resposta}\n")

        #  Atualiza a memória da conversa
        atualizar_memoria(entrada, resposta)


# MAIN
def main():
    parser = argparse.ArgumentParser(
        description="Cliente com memória local + contexto"
    )
    parser.add_argument(
        "--modo",
        choices=["chat", "simples"],
        default="chat"
    )
    parser.add_argument("texto", nargs="?", help="Texto no modo simples")

    args = parser.parse_args()

    if args.modo == "simples":
        memoria_local = carregar_memoria_local()

        if args.texto:
            resposta_memoria = buscar_resposta_memoria(args.texto, memoria_local)

            if resposta_memoria:
                print(resposta_memoria)
            else:
                print(enviar_prompt(args.texto))
        else:
            print("Digite um texto")

    else:
        chat()


if __name__ == "__main__":
    main()