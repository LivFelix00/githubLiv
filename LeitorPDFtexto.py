from pypdf import PdfReader
import camelot
import pandas as pd
import os


def ler_pdf_texto(caminho_pdf: str) -> str:
    leitor = PdfReader(caminho_pdf)

    texto_completo = ""
    for pagina in leitor.pages:
        texto = pagina.extract_text()
        if texto:
            texto_completo += texto.strip() + "\n"

    return texto_completo


def extrair_tabelas(caminho_pdf: str, pasta_saida="tabelas"):
    os.makedirs(pasta_saida, exist_ok=True)

    print("🔍 Detectando tabelas...")
    tabelas = camelot.read_pdf(caminho_pdf, pages="all", flavor="lattice")

    lista_tabelas = []

    for i, tabela in enumerate(tabelas):
        df = tabela.df  # DataFrame com linhas/colunas estruturadas
        arquivo_csv = os.path.join(pasta_saida, f"tabela_{i}.csv")

        df.to_csv(arquivo_csv, index=False)
        lista_tabelas.append(df)

        print(f"✅ Tabela {i} salva em: {arquivo_csv}")

    return lista_tabelas


def salvar_txt(conteudo: str, caminho_txt: str):
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(conteudo)


# ==========================
# EXECUÇÃO
# ==========================

arquivo_pdf = r"Docs\ASO_NR35.pdf"
arquivo_txt = r"Docs\ASO_NR35.txt"

# Texto normal
texto = ler_pdf_texto(arquivo_pdf)
salvar_txt(texto, arquivo_txt)

# Tabelas estruturadas
tabelas = extrair_tabelas(arquivo_pdf)

print("\n✅ Processo concluído!")