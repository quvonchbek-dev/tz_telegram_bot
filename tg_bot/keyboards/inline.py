from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.db.models import QuerySet

# from backend.models import BotAdmin

back_admin_btn = InlineKeyboardButton("🔙 Back", callback_data="back_admin")
cancel_btn = InlineKeyboardButton("❌ Cancel", callback_data="cancel")


async def cancel_mk():
    kb = InlineKeyboardMarkup()
    kb.add(cancel_btn)
    return kb


async def subscription(ch_list):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(*[InlineKeyboardButton(text=channel.title, url=channel.invite_link) for channel in ch_list])
    kb.add(InlineKeyboardButton("✅ Check", callback_data="check_subscription"))
    return kb


async def select_resource(res_list: QuerySet, admin=False):
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
            InlineKeyboardButton("➕ Add", callback_data="add_resource"),
            back_admin_btn
        )
    return kb


async def res_view(res_id: int, is_admin: bool = False):
    kb = InlineKeyboardMarkup()
    if is_admin:
        kb.add(
            InlineKeyboardButton("❌ Delete", callback_data=f"delete_res {res_id}"),
            InlineKeyboardButton("📝 Edit", callback_data=f"edit_res {res_id}"),
            InlineKeyboardButton("🗑 Trash", callback_data=f"archive_res {res_id}")
        )
    kb.add(InlineKeyboardButton("🔙 Back", callback_data=f"back"))
    return kb


async def admin_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Bot stats", callback_data="stats"),
        InlineKeyboardButton("🧑‍💻 Admins", callback_data="admins"),
        InlineKeyboardButton("📚 Sources", callback_data="sources"),
        InlineKeyboardButton("📣 Channels", callback_data="channels"),
        InlineKeyboardButton("✉ Send AD to users", callback_data="send_post"),
    )
    return kb


async def admins_kb(admins, su=False):
    kb = InlineKeyboardMarkup(row_width=2)
    for x in admins:
        kb.add(InlineKeyboardButton(f"👨‍💻 {x.admin.get_full_name()}", callback_data=f"admin_view {x.id}"))
    if su:
        kb.add(InlineKeyboardButton("➕ Add", callback_data="add_admin"), back_admin_btn)
    else:
        kb.add(back_admin_btn)
    return kb


async def channels_kb(channels):
    kb = InlineKeyboardMarkup(row_width=2)
    for x in channels:
        kb.add(InlineKeyboardButton(f"📣 {x.title}", callback_data=f"channel_view {x.id}"))
    kb.add(
        InlineKeyboardButton("➕ Add", callback_data="add_channel"),
        back_admin_btn
    )
    return kb


async def admin_view(pk: int, su=False):
    kb = InlineKeyboardMarkup()
    if su:
        kb.add(
            InlineKeyboardButton("🗑 Remove", callback_data=f"remove_admin {pk}"),
            InlineKeyboardButton("♻ Change role", callback_data=f"change_role {pk}")
        )
    kb.add(InlineKeyboardButton("🔙 Back", callback_data="admins"))
    return kb


async def back_admin_kb():
    kb = InlineKeyboardMarkup()
    kb.insert(back_admin_btn)
    return kb


async def channel_view(pk: int):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🗑 Remove", callback_data=f"remove_channel {pk}"),
        InlineKeyboardButton("🔙 Back", callback_data="channels")
    )
    return kb
