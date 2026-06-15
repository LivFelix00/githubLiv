import argparse
import requests

API_URL = "http://10.16.6.8:11434/api/generate"
MODEL_NAME = "gpt-oss:20b"

# Memória da conversa
historico = []

# Tamanho máximo da janela de contexto
MAX_MENSAGENS = 6


def montar_prompt_com_contexto(nova_mensagem: str) -> str:
    """
    Junta o histórico com a nova mensagem em um único prompt
    """
    contexto = ""

    for mensagem in historico:
        contexto += mensagem + "\n"

    contexto += f"Usuário: {nova_mensagem}\nAssistente:"

    return contexto


def enviar_prompt(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        resposta = requests.post(API_URL, json=payload, timeout=10)
        resposta.raise_for_status()
        return resposta.json().get("response", "Sem resposta da API")
    except requests.exceptions.RequestException as erro:
        return f"Erro na requisição: {erro}"


def atualizar_memoria(usuario_msg: str, resposta: str):
    """
    Adiciona novas mensagens ao histórico e mantém o limite
    """
    historico.append(f"Usuário: {usuario_msg}")
    historico.append(f"Assistente: {resposta}")

    # Mantém somente as últimas mensagens (janela de contexto)
    if len(historico) > MAX_MENSAGENS * 2:
        historico.pop(0)
        historico.pop(0)


def chat():
    print("💬 Chat iniciado (digite 'sair' para encerrar)\n")

    while True:
        entrada = input("Você: ")

        if entrada.lower() == "sair":
            break

        prompt = montar_prompt_com_contexto(entrada)
        resposta = enviar_prompt(prompt)

        print(f"IA: {resposta}\n")

        atualizar_memoria(entrada, resposta)


def main():
    parser = argparse.ArgumentParser(
        description="Cliente com memória de conversa"
    )
    parser.add_argument(
        "--modo",
        choices=["simples", "chat"],
        default="chat",
        help="Modo de execução"
    )
    parser.add_argument("texto", nargs="?", help="Texto para modo simples")

    args = parser.parse_args()

    if args.modo == "simples":
        if not args.texto:
            print("Você precisa fornecer um texto no modo simples.")
            return

        resposta = enviar_prompt(args.texto)
        print(resposta)

    else:
        chat()


if __name__ == "__main__":
    main()