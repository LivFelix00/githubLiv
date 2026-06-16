from pypdf import PdfReader
import pdfplumber
import pytesseract
from pdf2image import convert_from_path

# ⚠️ Ajuste se necessário (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def ler_pdf_completo(caminho_pdf: str) -> str:
    texto_completo = ""


    # 1. TEXTO COM PYPDF (seu método original)
   
    leitor = PdfReader(caminho_pdf)

    for i, pagina in enumerate(leitor.pages):
        texto = pagina.extract_text()
        if texto:
            texto_completo += f"\n--- Página {i+1} (Texto) ---\n"
            texto_completo += texto.strip() + "\n"

    
    # 2. TABELAS COM PDFPLUMBER
   
    with pdfplumber.open(caminho_pdf) as pdf:
        for i, pagina in enumerate(pdf.pages):
            tabelas = pagina.extract_tables()

            for t_idx, tabela in enumerate(tabelas):
                texto_completo += f"\n--- Página {i+1} (Tabela {t_idx+1}) ---\n"

                for linha in tabela:
                    linha_formatada = " | ".join(
                        str(celula) if celula else "" for celula in linha
                    )
                    texto_completo += linha_formatada + "\n"

    # 3. OCR (IMAGENS)
    
    print("🔍 Executando OCR...")

    imagens = convert_from_path(caminho_pdf)

    for i, img in enumerate(imagens):
        texto_ocr = pytesseract.image_to_string(img, lang="por+eng")

        if texto_ocr.strip():
            texto_completo += f"\n--- Página {i+1} (OCR Imagem) ---\n"
            texto_completo += texto_ocr + "\n"

    return texto_completo


def salvar_txt(conteudo: str, caminho_txt: str):
    with open(caminho_txt, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)



# EXECUÇÃO


arquivo_pdf = r"Docs\ASO_NR35.pdf"
arquivo_txt = r"Docs\ASO_NR35.txt"

conteudo = ler_pdf_completo(arquivo_pdf)
salvar_txt(conteudo, arquivo_txt)

print(conteudo)

# OCR pode errar acentos
# tabelas muito complexas podem vir desalinhadas
# fórmulas matemáticas não ficam perfeitas

#como o .TXT fica
#Página 1 (Texto) ---
#conteúdo normal...

#Página 1 (Tabela 1) ---
#coluna1 | coluna2 | coluna3

#Página 1 (OCR Imagem) ---
#texto detectado da imagem..