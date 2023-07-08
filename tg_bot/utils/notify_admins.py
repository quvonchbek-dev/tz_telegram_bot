from aiogram import Dispatcher
from django.db.models import QuerySet

from backend.models import BotAdmin


async def on_startup_notify(dp: Dispatcher, admins: QuerySet[BotAdmin]):
    for admin in admins:
        await dp.bot.send_message(admin.admin.chat_id, "🏃 The bot is running.")
