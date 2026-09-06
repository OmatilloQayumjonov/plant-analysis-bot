import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# .env faylini o'qish
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
TEMPLATE_PATH = BASE_DIR / "DPPH_template.xlsx"
OUTPUT_DIR = BASE_DIR / "outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)
