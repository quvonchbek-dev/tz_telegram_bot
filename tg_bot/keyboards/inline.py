from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.db.models import QuerySet

# from backend.models import BotAdmin

back_admin_btn = InlineKeyboardButton("🔙 Orqaga", callback_data="back_admin")
cancel_btn = InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")
back_btn = InlineKeyboardButton("🔙 Orqaga", callback_data=f"back")


async def cancel_mk():
    kb = InlineKeyboardMarkup()
    kb.add(cancel_btn)
    return kb


async def subscription(ch_list):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(*[InlineKeyboardButton(text=channel.title, url=channel.invite_link) for channel in ch_list])
    kb.add(InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription"))
    return kb


async def select_resource(res_list: QuerySet, admin=False, section=0):
    sm = {"VIDEO": "📹", "DOCUMENT": "📚", "PHOTO": '🖼'}
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(*[
        InlineKeyboardButton(
            f"{sm[obj.file_type]} {obj.file_name}",
            callback_data=f"res_view {obj.id}")
        for i, obj in enumerate(res_list)
    ])
    if admin:
        kb.add(
            InlineKeyboardButton("➕ Qo'shish", callback_data=f"add_resource {section}"),
            back_btn
        )
    if not admin:
        kb.add(back_btn)
    return kb


async def res_view(res_id: int, is_admin: bool = False, section=0):
    kb = InlineKeyboardMarkup()
    if is_admin:
        kb.add(
            # InlineKeyboardButton("❌ O'chirish", callback_data=f"delete_res {res_id}"),
            InlineKeyboardButton("📝 Tahrirlash", callback_data=f"edit_res {res_id}"),
            InlineKeyboardButton("🗑 O'chirish", callback_data=f"archive_res {res_id}"),
        )
        kb.add(InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"back_to_menu {section}"))
    return kb


async def admin_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Bot statistikasi", callback_data="stats"),
        InlineKeyboardButton("🧑‍💻 Adminlar", callback_data="admins"),
        # InlineKeyboardButton("📚 Manba'lar", callback_data="sources"),
        InlineKeyboardButton("📣 Kanallar", callback_data="channels"),
        InlineKeyboardButton("✉ Foydalanuvchilarga xabar yuborish", callback_data="send_post"),
        back_btn
    )
    return kb


async def admins_kb(admins, su=False):
    kb = InlineKeyboardMarkup(row_width=2)
    for x in admins:
        kb.add(InlineKeyboardButton(f"👨‍💻 {x.admin.get_full_name()}", callback_data=f"admin_view {x.id}"))
    if su:
        kb.add(InlineKeyboardButton("➕ Qo'shish", callback_data="add_admin"), back_admin_btn)
    else:
        kb.add(back_admin_btn)
    return kb


async def channels_kb(channels):
    kb = InlineKeyboardMarkup(row_width=2)
    for x in channels:
        kb.add(InlineKeyboardButton(f"📣 {x.title}", callback_data=f"channel_view {x.id}"))
    kb.add(
        InlineKeyboardButton("➕ Qo'shish", callback_data="add_channel"),
        back_admin_btn
    )
    return kb


async def admin_view(pk: int | str, su=False):
    kb = InlineKeyboardMarkup()
    if su:
        kb.add(
            InlineKeyboardButton("🗑 O'chirish", callback_data=f"remove_admin {pk}"),
            InlineKeyboardButton("♻ Rolini o'zgartirish", callback_data=f"change_role {pk}")
        )
    kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admins"))
    return kb


async def back_admin_kb():
    kb = InlineKeyboardMarkup()
    kb.insert(back_admin_btn)
    return kb


async def channel_view(pk: int | str):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🗑 O'chirish", callback_data=f"remove_channel {pk}"),
        InlineKeyboardButton("🔙 Orqaga", callback_data="channels")
    )
    return kb
