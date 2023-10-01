import os

import django
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
SECTION_ITEMS = ["📚 Ma'ruza", "📝 Amaliy", "📹 Videodarslar", "🎓 Shaxsiy T.", "📚 Adabiyotlar"]

