from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
from google.generativeai import GenerativeModel
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
# Setup
pergunta_usuario = input("Digite sua pergunta sobre a reunião: ")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.Client()
collection = client.get_or_create_collection(name="reunioes_auditadas", embedding_function=ef)

# Busca trechos relevantes
resultados = collection.query(
    query_texts=[pergunta_usuario],
    n_results=3
)
trechos = "\n\n".join([f"{i+1}. {doc}" for i, doc in enumerate(resultados["documents"][0])])

# Prompt para o Gemini
prompt_qa = f"""
Você é um analista experiente de Customer Success. Baseando-se apenas nos trechos abaixo da reunião, responda à pergunta com precisão e assertividade:

**Pergunta:** "{pergunta_usuario}"

**Trechos relevantes extraídos:**
{trechos}

**Resposta:**
"""

# Gemini responde
model = GenerativeModel("gemini-1.5-pro")
resposta = model.generate_content(prompt_qa).text

print("\nResposta:\n" + resposta)
