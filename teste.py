import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-1.5-pro")  # Nome correto do modelo

response = model.generate_content("Olá, qual o seu nome?")
print(response.text)
