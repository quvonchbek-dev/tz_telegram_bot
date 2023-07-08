from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def subscription(ch_list):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(*[InlineKeyboardButton(text=channel.title, url=channel.invite_link) for channel in ch_list])
    kb.add(InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription"))
    return kb
