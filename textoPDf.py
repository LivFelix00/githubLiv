from pypdf import PdfReader


def ler_pdf(caminho_pdf: str) -> str:
    leitor = PdfReader(caminho_pdf)

    texto_completo = ""
    for pagina in leitor.pages:
        texto = pagina.extract_text()
        if texto:
            texto_completo += texto.strip() + "\n"

    return texto_completo


def salvar_txt(conteudo: str, caminho_txt: str):
    with open(caminho_txt, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)


# Caminhos dos arquivos
arquivo_pdf = r"Docs\ASO_NR35.pdf"
arquivo_txt = r"Docs\ASO_NR35.txt"

# Executa leitura e conversão
conteudo = ler_pdf(arquivo_pdf)
salvar_txt(conteudo, arquivo_txt)

# Exibe no terminal também (opcional)
print(conteudo)