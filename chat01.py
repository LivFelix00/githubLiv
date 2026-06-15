import argparse
import json
import requests
import pypdf


API_URL = "http://10.16.6.8:11434/api/generate"
MODEL_NAME = "gpt-oss:20b"


def enviar_prompt(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        resposta = requests.post(API_URL, json=payload)
        resposta.raise_for_status()
        return resposta.json().get("response", "Sem resposta da API")
    except requests.exceptions.RequestException as erro:
        return f"Erro na requisição: {erro}"




def obter_argumentos() -> str:
    parser = argparse.ArgumentParser(
        description="Cliente simples para enviar prompts ao modelo via API"
    )
    parser.add_argument("texto", help="Texto que será enviado para o modelo")
    args = parser.parse_args()
    return args.texto


def main():
    prompt = obter_argumentos()
    resultado = enviar_prompt(prompt)

    print(resultado)
if __name__ == "__main__":
    main()
