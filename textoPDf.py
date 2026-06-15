from pypdf import PdfReader


def ler_pdf(caminho_pdf: str) -> str:
    leitor = PdfReader(caminho_pdf) 
    
    texto_completo = ""
    for pagina in leitor.pages:
        texto_completo += pagina.extract_text().strip() or ""
        
    return texto_completo

conteudo = ler_pdf("ASO_NR35.pdf")   
print(conteudo)
        
      
