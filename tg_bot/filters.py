from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
#
# class Sub(BoundFilter):
#     async def check(self, message: types.Message) -> bool:
#         user = await db.select_user(telegram_id=message.from_user.id)
#         return user.isadmin or message.from_user.id in ADMINS