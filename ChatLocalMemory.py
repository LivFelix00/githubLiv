

import argparse
import requests
import os

API_URL = "http://10.16.6.8:11434/api/generate"
MODEL_NAME = "gpt-oss:20b"

MEMORY_FILE = "memory.txt"

historico = []
MAX_MENSAGENS = 6



#  MEMÓRIA DO USUÁRIO

def carregar_memoria():
    memoria = {}

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            for linha in f:
                if "=" in linha:
                    chave, valor = linha.strip().split("=", 1)
                    memoria[chave] = valor

    return memoria


def salvar_memoria(memoria):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        for chave, valor in memoria.items():
            f.write(f"{chave}={valor}\n")



#  MEMÓRIA COM IA

def extrair_memoria_com_ia(texto: str) -> dict:
    prompt = f"""
Analise a frase abaixo e extraia informações relevantes sobre o usuário.

Regras:
- Retorne SOMENTE dados úteis
- Formato: chave=valor
- Se não houver nada relevante, retorne: NADA

Frase:
\"{texto}\"
"""
    resposta = enviar_prompt(prompt).strip()

    memoria_extraida = {}

    if "NADA" in resposta.upper():
        return memoria_extraida

    for linha in resposta.split("\n"):
        if "=" in linha:
            chave, valor = linha.split("=", 1)
            memoria_extraida[chave.strip()] = valor.strip()

    return memoria_extraida


def atualizar_memoria_com_ia(texto: str, memoria: dict):
    nova_info = extrair_memoria_com_ia(texto)

    if nova_info:
        print(f"\n Memória atualizada: {nova_info}\n")

    memoria.update(nova_info)
    salvar_memoria(memoria)


def memoria_para_contexto(memoria: dict) -> str:
    if not memoria:
        return ""

    contexto = "Informações conhecidas sobre o usuário:\n"

    for chave, valor in memoria.items():
        contexto += f"{chave}: {valor}\n"

    contexto += "\n"
    return contexto



#  CONTEXTO

def montar_prompt(nova_msg, memoria):
    contexto = ""

    contexto += memoria_para_contexto(memoria)

    for msg in historico:
        contexto += msg + "\n"

    contexto += f"Usuário: {nova_msg}\nAssistente:"

    return contexto


def atualizar_historico(usuario, resposta):
    historico.append(f"Usuário: {usuario}")
    historico.append(f"Assistente: {resposta}")

    while len(historico) > MAX_MENSAGENS * 2:
        historico.pop(0)



# API

def enviar_prompt(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        r = requests.post(API_URL, json=payload, timeout=(5, 120))
        r.raise_for_status()
        return r.json().get("response", "")

    except requests.exceptions.Timeout:
        return "⏱ Tempo esgotado."

    except requests.exceptions.RequestException as e:
        return f"Erro: {e}"



# CHAT 

def chat():
    memoria = carregar_memoria()

    print("💬 Chat com memória inteligente (digite 'sair' quando acabar))\n")

    while True:
        entrada = input("Você: ")

        if entrada.lower() == "sair":
            break

        # ✅ Aparece IMEDIATAMENTE
        print(" Pensando...\n")
        
        # processamento
        atualizar_memoria_com_ia(entrada, memoria)

        prompt = montar_prompt(entrada, memoria)
        resposta = enviar_prompt(prompt)

        print(f" IA: {resposta}\n")

        atualizar_historico(entrada, resposta)



#  MAIN

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", choices=["chat", "simples"], default="chat")
    parser.add_argument("texto", nargs="?")

    args = parser.parse_args()

    memoria = carregar_memoria()

    if args.modo == "simples":
        if args.texto:
            print(" Pensando...\n")
            atualizar_memoria_com_ia(args.texto, memoria)
            print(enviar_prompt(args.texto))
        else:
            print("Digite um texto")
    else:
        chat()


if __name__ == "__main__":
    main()