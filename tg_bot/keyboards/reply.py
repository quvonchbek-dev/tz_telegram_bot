from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class Menu:
    FOR_ADMINS = "👨‍💻 Admin panel"
    SOURCES = "📚 Sources"


async def main_menu(admin=False):
    kb = ReplyKeyboardMarkup([[Menu.SOURCES]], resize_keyboard=True)
    if admin:
        kb.add(KeyboardButton(Menu.FOR_ADMINS))
    return kb
