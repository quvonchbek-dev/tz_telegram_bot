from aiogram.types import ChatMemberLeft

from tg_bot.loader import db, bot


async def is_subscribed(user_id):
    ch_list = await db.get_channels_list()
    must_subscribe = []
    for channel in ch_list:
        chat_id = channel.chat_id
        try:
            g = await bot.get_chat_member(int(chat_id), user_id)
            if isinstance(g, ChatMemberLeft):
                must_subscribe.append(channel)
        except Exception:
            must_subscribe.append(channel)
    return must_subscribe
