import streamlit as st
import os
import base64
import tempfile
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
from faster_whisper import WhisperModel
import ffmpeg
from pathlib import Path
import webbrowser
from tkinter import Tk, filedialog

# ============ CONFIGURAÇÕES ============
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ============ UI ============
st.set_page_config(page_title="Auditor Jettax - Full", layout="wide")
st.title("🧠 Auditoria Inteligente de Reuniões - Jettax")

modelo_whisper = st.selectbox("🧠 Modelo do Whisper", ["tiny", "base", "small", "medium", "large"])
tipo_dispositivo = st.radio("💻 Dispositivo", ["cpu", "cuda"], horizontal=True)
default_cudnn_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin"
cudnn_path = st.text_input("📁 Caminho do cuDNN (para uso com GPU)", value=default_cudnn_path)
os.environ["PATH"] += f";{cudnn_path}"

# Selecionar pasta via explorador
st.markdown("### 🗂️ Pasta de destino")
if st.button("📂 Selecionar pasta de saída"):
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory()
    root.destroy()
    if folder:
        st.session_state['output_dir'] = folder
output_dir = st.session_state.get('output_dir', str(Path.cwd()))
st.info(f"Pasta atual selecionada: `{output_dir}`")

# Carregar vídeo
video_path = st.file_uploader("🎞️ Selecione o vídeo da reunião", type=["mp4", "mp3", "wav"])

# Prompt customizado
st.markdown("### ✏️ Prompt de Análise (personalizado - substitui o padrão, não recomendado):")
custom_prompt = st.text_area("Prompt (opcional):", placeholder="Deixe em branco para usar o prompt padrão.", height=150)

# ============ GERAÇÃO ============
def gerar_html_jettax(conteudo: str, titulo: str, nome_arquivo: str, salvar_em: Path):
    conteudo_formatado = conteudo.replace("\n", "<br>")
    html_template = f"""<!DOCTYPE html>
    <html lang='pt-BR'>
    <head>
      <meta charset='UTF-8'>
      <title>{titulo}</title>
      <style>
        body {{
          font-family: 'Segoe UI', sans-serif;
          background-color: #F5F7FA;
          color: #1A1F71;
          padding: 40px;
        }}
        header {{
          text-align: center;
          margin-bottom: 40px;
        }}
        header img {{
          max-width: 250px;
        }}
        h1 {{
          color: #00AEEF;
          margin-top: 10px;
          font-size: 28px;
        }}
        h2, h3, strong {{
          font-size: 22px;
          font-weight: bold;
        }}
        section {{
          background: white;
          padding: 30px;
          border-radius: 10px;
          box-shadow: 0 0 10px rgba(0,0,0,0.1);
          font-size: 18px;
        }}
        .btn {{
          display: inline-block;
          margin-top: 30px;
          padding: 10px 20px;
          background-color: #1A1F71;
          color: white;
          text-decoration: none;
          border-radius: 5px;
        }}
        .conclusao {{
          margin-top: 40px;
          padding: 20px;
          background-color: #e0f7fa;
          border-left: 5px solid #00acc1;
          font-weight: bold;
        }}
      </style>
    </head>
    <body>
      <header>
        <img src='logo.webp' alt='Logo Jettax'>
        <h1>Relatório de Reunião</h1>
        <p>{titulo}</p>
      </header>
      <section>
        {conteudo_formatado}
        <br><br>
        <a class='btn' href='http://localhost:8501#Perguntar-sobre-a-reunião'>🔎 Fazer perguntas sobre esta reunião</a>
      </section>
    </body>
    </html>"""
    output_path = salvar_em / f"{nome_arquivo}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    return output_path

# ============ LÓGICA PRINCIPAL ============
if st.button("🚀 Iniciar Análise Completa"):
    if not video_path:
        st.warning("Selecione um vídeo primeiro.")
    else:
        progress = st.progress(0)
        status = st.empty()

        filename_base = Path(video_path.name).stem
        prefixo = f"reuniao-{filename_base}"
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        audio_path = output_dir_path / f"{prefixo}.wav"
        trans_path = output_dir_path / f"{prefixo}.txt"

        status.text("🎧 Extraindo áudio do vídeo...")
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(video_path.read())
            tmp_path = tmp.name
        ffmpeg.input(tmp_path).output(str(audio_path), ac=1, ar='16k').run(overwrite_output=True, quiet=True)
        progress.progress(10)

        status.text(f"📝 Transcrevendo com Whisper ({modelo_whisper} - {tipo_dispositivo})...")
        model_whisper = WhisperModel(modelo_whisper, device=tipo_dispositivo, compute_type="float32")
        segments, _ = model_whisper.transcribe(str(audio_path), beam_size=5)
        transcricao = "\n".join([seg.text for seg in segments])
        with open(trans_path, "w", encoding="utf-8") as f:
            f.write(transcricao)
        progress.progress(30)

        status.text("🤖 Gerando relatório com Gemini...")
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        prompt_final = custom_prompt if custom_prompt.strip() else f"""
Você é um auditor sênior de Customer Success. Com base na transcrição a seguir, gere um relatório com:

1. Sentimento do cliente (com exemplos reais citados)
2. Postura e clareza do analista (com embasamento nas falas)
3. Alinhamento entre discurso e entrega (com menções claras de desalinhamento)
4. Sinais de churn (se houver)
5. Oportunidades reais de melhoria
6. Recomendação objetiva

Ao final, conclua com uma das 4 categorias (e apenas uma):
- Possui pontos de Atenção – Acionar Fluxo Manter Acompanhamento e Notificar Analista – Playbook Acionado.
- Risco Alto – Possui Risco Alto de Churn – Notificar Liderança. Playbook Acionado.
- Sem Risco – Não notificar.
- Reunião Exemplar – Notificar Liderança Para Feedback Positivo.

A resposta deve ser formatada com títulos destacados, claros, usando <strong> para destacar os títulos no HTML.
Não deve haver sugestões como "envolver desenvolvimento" ou ações que não são de alçada do time de CS.
Não inclua cabeçalhos com nome do cliente ou data da reunião.
"""
        resposta = model.generate_content(f"{prompt_final}\n\nTranscrição:\n{transcricao}").text
        progress.progress(60)

        status.text("📄 Salvando relatório em HTML...")
        html_path = gerar_html_jettax(resposta, f"Reunião analisada - {filename_base}", prefixo, output_dir_path)
        progress.progress(80)

        status.text("🔎 Indexando para perguntas inteligentes...")
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        client = chromadb.Client()
        collection = client.get_or_create_collection(name="reunioes_auditadas", embedding_function=ef)
        blocos = [p.strip() for p in transcricao.split("\n\n") if len(p.strip()) > 20]
        for idx, trecho in enumerate(blocos):
            collection.upsert(
                documents=[trecho],
                metadatas=[{"origem": filename_base}],
                ids=[f"{filename_base}_{idx}"]
            )
        progress.progress(100)

        status.success("✅ Processo concluído!")
        st.markdown(f"📁 [Baixar HTML]({html_path})")
        if st.button("📂 Abrir relatório gerado"):
            webbrowser.open(str(html_path))

# ============ PERGUNTAS ============
st.divider()
st.markdown("### ❓ Perguntar sobre a reunião")
pergunta = st.text_input("Digite sua pergunta:")
if pergunta:
    with st.spinner("Consultando..."):
        total_docs = len(collection.get()["documents"])
        resultados = collection.query(query_texts=[pergunta], n_results=min(3, total_docs))
        trechos = "\n\n".join([f"{i+1}. {doc}" for i, doc in enumerate(resultados["documents"][0])])
        prompt_qa = f"""Você é um analista de CS. Com base apenas nos trechos abaixo, responda com precisão:

Pergunta: {pergunta}
Trechos:
{trechos}

Resposta:"""
        resposta = model.generate_content(prompt_qa).text
        st.markdown("### 💡 Resposta do Gemini:")
        st.write(resposta)
