from dotenv import load_dotenv
import os

load_dotenv(override=True)
print("✅ GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))