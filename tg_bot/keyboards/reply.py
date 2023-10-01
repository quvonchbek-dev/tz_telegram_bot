from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from tg_bot import config


class Menu:
    FOR_ADMINS = "👨‍💻 Admin panel"
    SOURCES = "📚 Sources"
    LECTURE = "📚 Ma'ruza"
    PRACTICAL = "📝 Amaliy"
    VIDEO = "📹 Videodarslar"
    INDIVIDUAL = "🎓 Shaxsiy T."
    LITERATURE = "📚 Adabiyotlar"


async def main_menu(admin=False):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for button in config.SECTION_ITEMS:
        kb.insert(button)
    if admin:
        kb.insert(KeyboardButton(Menu.FOR_ADMINS))
    return kb
