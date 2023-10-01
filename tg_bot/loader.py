from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from tg_bot import config
import os
import django
import logging

logging.basicConfig(level=logging.INFO)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
django.setup()

from tg_bot.utils import manager as db
from backend.models import BotAdmin

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
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
