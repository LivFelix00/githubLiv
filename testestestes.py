from pypdf import PdfReader
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import re

# Caminho do Tesseract (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


#REGEX LINKS

def extrair_links_texto(texto: str):
    padrao = r'https?://[^\s]+|www\.[^\s]+'
    return re.findall(padrao, texto)


# LIMPEZA OCR

def corrigir_texto_ocr(texto: str):
    texto = texto.replace(" ", "")
    texto = texto.replace("h ttps", "https")
    texto = texto.replace("htt ps", "https")
    texto = texto.replace("http:/", "http://")
    texto = texto.replace("https:/", "https://")
    return texto


# LINKS CLICÁVEIS POR PÁGINA

def extrair_links_pagina(page):
    links = []

    if "/Annots" in page:
        for annot in page["/Annots"]:
            obj = annot.get_object()

            if "/A" in obj and "/URI" in obj["/A"]:
                links.append(str(obj["/A"]["/URI"]))

    return links


# FUNÇÃO PRINCIPAL

def ler_pdf_completo(caminho_pdf: str) -> str:
    texto_completo = ""

    leitor = PdfReader(caminho_pdf)
    pdf_plumber = pdfplumber.open(caminho_pdf)
    imagens = convert_from_path(caminho_pdf)

    total_paginas = len(leitor.pages)

    for i in range(total_paginas):
        texto_completo += f"\n=============================\n"
        texto_completo += f"📄 PÁGINA {i+1}\n"
        texto_completo += f"=============================\n"

        # =============================
        # 1. TEXTO
        # =============================
        pagina = leitor.pages[i]
        texto = pagina.extract_text()

        if texto:
            texto_completo += "\n--- TEXTO ---\n"
            texto_completo += texto.strip() + "\n"

        # =============================
        # 2. TABELAS
        # =============================
        pagina_plumber = pdf_plumber.pages[i]
        tabelas = pagina_plumber.extract_tables()

        if tabelas:
            texto_completo += "\n--- TABELAS ---\n"

            for t_idx, tabela in enumerate(tabelas):
                texto_completo += f"\n[Tabela {t_idx+1}]\n"

                for linha in tabela:
                    linha_formatada = " | ".join(
                        str(celula) if celula else "" for celula in linha
                    )
                    texto_completo += linha_formatada + "\n"

        # =============================
        # 3. OCR (IMAGEM)
        # =============================
        img = imagens[i]

        config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:/._-'

        texto_ocr = pytesseract.image_to_string(
            img, lang="eng+por", config=config
        )

        if texto_ocr.strip():
            texto_completo += "\n--- OCR (IMAGEM) ---\n"

            texto_ocr_corrigido = corrigir_texto_ocr(texto_ocr)
            texto_completo += texto_ocr_corrigido + "\n"

        # =============================
        # 4. LINKS
        # =============================
        texto_completo += "\n--- LINKS ENCONTRADOS ---\n"

        links_totais = []

        # links clicáveis
        links_pdf = extrair_links_pagina(pagina)
        links_totais.extend(links_pdf)

        # links do texto
        if texto:
            links_totais.extend(extrair_links_texto(texto))

        # links do OCR
        if texto_ocr.strip():
            links_totais.extend(
                extrair_links_texto(corrigir_texto_ocr(texto_ocr))
            )

        # remover duplicados
        links_unicos = list(set(links_totais))

        if links_unicos:
            for link in links_unicos:
                texto_completo += link + "\n"
        else:
            texto_completo += "Nenhum link encontrado\n"

    pdf_plumber.close()
    return texto_completo



# SALVAR TXT
def salvar_txt(conteudo: str, caminho_txt: str):
    with open(caminho_txt, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)



# EXECUÇÃO

arquivo_pdf = r"Docs\formulas.pdf"
arquivo_txt = r"Docs\formulas.txt"

conteudo = ler_pdf_completo(arquivo_pdf)
salvar_txt(conteudo, arquivo_txt)

print(conteudo)