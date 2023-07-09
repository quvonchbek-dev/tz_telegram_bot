from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
import django
from aiogram.dispatcher.filters.state import StatesGroup, State

if True:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
    django.setup()

from tg_bot.utils import manager as db
from backend.models import BotAdmin

BOT_TOKEN = "5286332608:AAE3PzEgmkPM_kEK_10jtNZRtuNj-kH9Apk"

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def get_admin_ids():
    return [int(admin.admin.chat_id) for admin in BotAdmin.admins.all()]


class Form(StatesGroup):
    nothing = State()
    add_resource = State()
    add_channel = State()
    add_admin = State()

    delete_resource = State()
    send_post = State()
    edit_caption = State()
    edit_ch_link = State()
