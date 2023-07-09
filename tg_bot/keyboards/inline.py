from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.db.models import QuerySet


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
            callback_data=f"view {obj.id}")
        for i, obj in enumerate(res_list)
    ])
    if admin:
        kb.insert(InlineKeyboardButton("➕ Add", callback_data="add_resource"))
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
