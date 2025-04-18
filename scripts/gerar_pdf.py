import pdfkit
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
# Caminho do HTML e destino do PDF
html_path = "relatorios/relatorio_reuniao1_com_logo.html"
pdf_path = "relatorios/relatorio_reuniao1_com_logo.pdf"

# Configuração (necessária no Windows)
config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

# Gerar o PDF
try:
    pdfkit.from_file(html_path, pdf_path, configuration=config)
    print(f"✅ PDF gerado com sucesso: {pdf_path}")
except OSError as e:
    print("❌ Erro ao gerar PDF:", e)
