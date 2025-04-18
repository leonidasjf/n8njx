import streamlit as st
import os
import base64
from datetime import datetime
from google.generativeai import GenerativeModel
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Auditoria de Reuniões - Jettax", layout="wide")
st.title("📊 Auditoria Inteligente de Reuniões - Jettax")

# Inicializa modelos
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.Client()
collection = client.get_or_create_collection(name="reunioes_auditadas", embedding_function=ef)
model = GenerativeModel("gemini-1.5-pro")

st.sidebar.markdown("### ⚙️ Opções")
opcao = st.sidebar.radio("Selecione:", ["🔁 Nova Reunião", "❓ Perguntar sobre Reunião"])

# Página de upload e geração de relatório
if opcao == "🔁 Nova Reunião":
    uploaded_file = st.file_uploader("📤 Faça o upload da transcrição (.txt)", type=["txt"])
    if uploaded_file:
        transcricao = uploaded_file.read().decode("utf-8")
        st.success("Transcrição carregada!")

        if st.button("🚀 Gerar Relatório"):
            prompt = f"""
Você é um auditor sênior de Customer Success. Com base na transcrição completa abaixo, elabore um relatório executivo com os seguintes tópicos:

1. Sentimento geral do cliente
2. Postura e clareza do analista
3. Alinhamento entre discurso comercial e entrega
4. Sinais de risco de churn
5. Oportunidades comerciais ou operacionais
6. Recomendações práticas para o time de CS ou liderança

Transcrição:
{transcricao}
"""
            with st.spinner("Analisando com Gemini..."):
                resposta = model.generate_content(prompt).text

            nome_base = f"relatorio_jettax_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            html_path = f"{nome_base}.html"
           
            with open(html_path, "w", encoding="utf-8") as f:
                f.write("<html><body><pre style='font-family:Poppins,sans-serif'>" + resposta + "</pre></body></html>")

            st.success("✅ Relatório gerado com sucesso!")

            with open(html_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                href = f'<a href="data:text/html;base64,{b64}" download="{html_path}">📥 Baixar Relatório HTML</a>'
                st.markdown(href, unsafe_allow_html=True)

            # Indexação para Q&A
            blocos = [p.strip() for p in transcricao.split("\n\n") if len(p.strip()) > 20]
            for idx, trecho in enumerate(blocos):
                collection.add(
                    documents=[trecho],
                    metadatas=[{"origem": html_path}],
                    ids=[f"{html_path}_{idx}"]
                )
            st.info("Embeddings gerados para Q&A!")

# Página de perguntas
if opcao == "❓ Perguntar sobre Reunião":
    pergunta = st.text_input("Digite sua pergunta sobre a reunião:")
    if pergunta:
        with st.spinner("Consultando..."):
            total_docs = len(collection.get()["documents"])
            resultados = collection.query(query_texts=[pergunta], n_results=min(3, total_docs))
            trechos = "\n\n".join([f"{i+1}. {doc}" for i, doc in enumerate(resultados["documents"][0])])
            prompt_qa = f"""
Você é um analista experiente de Customer Success. Baseando-se apenas nos trechos abaixo da reunião, responda com precisão:

**Pergunta:** {pergunta}

**Trechos relevantes:**
{trechos}

**Resposta:** 
"""
            resposta = model.generate_content(prompt_qa).text
            st.markdown("### 💡 Resposta:")
            st.write(resposta)
