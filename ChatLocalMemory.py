
import argparse
import requests
import os
import threading
import time

#porta 1714 - http://10.16.6.8:11434/api/generate"
API_URL = "http://10.16.6.8:1714/api/generate"
MODEL_NAME = "gpt-oss:20b"

MEMORY_FILE = "memory.txt"

# Memória de conversa
historico = []
MAX_MENSAGENS = 6


# 📂 =========================
# 📚 MEMÓRIA LOCAL
# 📂 =========================
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


# 🧠 =========================
# 🪟 CONTEXTO DE CONVERSA
# 🧠 =========================
def montar_prompt_com_contexto(nova_mensagem: str) -> str:
    contexto = ""

    for msg in historico:
        contexto += msg + "\n"

    contexto += f"Usuário: {nova_mensagem}\nAssistente:"
    return contexto


def atualizar_memoria(usuario_msg: str, resposta: str):
    historico.append(f"Usuário: {usuario_msg}")
    historico.append(f"Assistente: {resposta}")

    if len(historico) > MAX_MENSAGENS * 2:
        historico.pop(0)
        historico.pop(0)


# ⏳ =========================
# 🤔 ANIMAÇÃO "PENSANDO"
# ⏳ =========================
def animacao_pensando(parar_flag):
    while not parar_flag["parar"]:
        for ponto in ["", ".", "..", "..."]:
            if parar_flag["parar"]:
                break
            print(f"\r🤔 IA pensando{ponto}   ", end="", flush=True)
            time.sleep(0.5)


# 🌐 =========================
# 🤖 CHAMADA À API
# 🌐 =========================
def enviar_prompt(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        resposta = requests.post(
            API_URL,
            json=payload,
            timeout=(5, 120)  # conexão, leitura
        )
        resposta.raise_for_status()
        return resposta.json().get("response", "Sem resposta da API")

    except requests.exceptions.Timeout:
        return "⏱️ Erro: tempo de resposta excedido."

    except requests.exceptions.RequestException as erro:
        return f"Erro na requisição: {erro}"


# 💬 =========================
# 🎮 CHAT PRINCIPAL
# 💬 =========================
def chat():
    memoria_local = carregar_memoria_local()

    print("💬 Chat iniciado (digite 'sair' para encerrar)\n")

    while True:
        entrada = input("Você: ")

        if entrada.lower() == "sair":
            break

        # 📚 1. Verifica memória local
        resposta_memoria = buscar_resposta_memoria(entrada, memoria_local)

        if resposta_memoria:
            print(f"\n📚 (Memória local)")
            print(f"IA: {resposta_memoria}\n")
            atualizar_memoria(entrada, resposta_memoria)

        else:
            # 🤔 2. Animação enquanto pensa
            parar_flag = {"parar": False}
            thread = threading.Thread(target=animacao_pensando, args=(parar_flag,))
            thread.start()

            prompt = montar_prompt_com_contexto(entrada)
            resposta = enviar_prompt(prompt)

            parar_flag["parar"] = True
            thread.join()

            print("\r", end="")  # limpa linha
            print(f"🤖 IA: {resposta}\n")

            atualizar_memoria(entrada, resposta)


# 🚀 =========================
# 🏁 MAIN
# 🚀 =========================
def main():
    parser = argparse.ArgumentParser(
        description="Chat com memória local + IA + animação"
    )
    parser.add_argument(
        "--modo",
        choices=["chat", "simples"],
        default="chat"
    )
    parser.add_argument("texto", nargs="?", help="Texto no modo simples")

    args = parser.parse_args()

    memoria_local = carregar_memoria_local()

    if args.modo == "simples":
        if args.texto:
            resposta_memoria = buscar_resposta_memoria(args.texto, memoria_local)

            if resposta_memoria:
                print(resposta_memoria)
            else:
                print(enviar_prompt(args.texto))
        else:
            print("Digite um texto.")

    else:
        chat()


if __name__ == "__main__":
    main()