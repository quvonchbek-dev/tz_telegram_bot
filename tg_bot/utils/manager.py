from aiogram import Bot
from django.utils import timezone
from backend.models import BotUser, Channel, BotAdmin, Resource
from aiogram.types import Chat, Message


async def add_user(chat: Chat) -> bool:
    user = BotUser.objects.filter(chat_id=chat.id)
    if not user.exists():
        BotUser.objects.create(
            chat_id=chat.id,
            first_name=chat.first_name,
            last_name=chat.last_name,
            username=chat.username,
        )
        return True
    user = BotUser.objects.get(chat_id=chat.id)
    user.first_name = chat.first_name
    user.last_name = chat.last_name
    user.username = chat.username
    user.save()
    return False


async def get_users():
    users = BotUser.objects.all()
    return list(users)


async def get_user(msg: Message):
    try:
        await add_user(msg.chat)
        user = BotUser.objects.get(chat_id=str(msg.chat.id))
        return user
    except Exception:
        ...


async def get_channels_list():
    return Channel.objects.all()


async def get_admins():
    return BotAdmin.admins.all()


async def add_admin(msg: Message, role="admin") -> BotAdmin:
    try:
        chat = msg.forward_from or msg.chat
        await add_user(chat)
        user = BotUser.objects.filter(chat_id=str(chat.id)).first()
        admin = BotAdmin.admins.create(admin=user, role=role)
    except Exception as e:
        print(e)
        return False
    return admin


async def get_stats():
    qs = BotUser.objects.all()
    total = qs.count()
    active = qs.filter(status=1).count()
    today = timezone.now()
    today_used = qs.filter(last_seen__month=today.month).filter(last_seen__day=today.day).count()
    today_joined = qs.filter(joined__month=today.month).filter(joined__day=today.day).count()
    return total, active, total - active, today_used, today_joined


async def add_resource(msg: Message, section: int) -> Resource:
    if "document" in msg:
        file_id = msg.document.file_id
        file_name = msg.document.file_name

    elif "video" in msg:
        file_id = msg.video.file_id
        file_name = msg.video.file_name

    else:
        return False
    title = msg.caption
    tp = str(msg.content_type).upper()
    obj = Resource.objects.create(
        title=(title or ""),
        file_name=file_name,
        file_type=tp,
        file_id=file_id,
        publisher=await get_user(msg),
        section=section
    )
    return obj


async def change_status_resource(r_id: int, status: int):
    try:
        res = Resource.objects.get(pk=r_id)
        res.status = status
        res.save()
    except Exception as ex:
        print(ex)
        return False
    return True


async def get_resources(status: int, section: int):
    res = Resource.objects.filter(status=status, section=section)
    return res


async def get_resource(pk: int):
    return Resource.objects.get(pk=pk)


async def get_admin(pk=None, chat_id=None):
    if pk:
        return BotAdmin.admins.get(pk=pk)
    elif chat_id:
        return BotAdmin.admins.filter(admin__chat_id=chat_id).first()


async def remove_admin(pk):
    admin = BotAdmin.admins.get(pk=pk)
    return admin.delete()


async def change_role(pk):
    dc = {"superuser": "admin", "admin": "superuser"}
    admin = await get_admin(pk)
    admin.role = dc[admin.role]
    admin.save()
    return admin.role


async def add_channel(msg: Message, bot: Bot):
    try:
        link = await bot.create_chat_invite_link(msg.forward_from_chat.id)
        chat = msg.forward_from_chat
        Channel.objects.create(
            title=chat.title,
            invite_link=link.invite_link,
            chat_id=chat.id
        )
        return True
    except Exception as e:
        print(e)
        return False


async def get_channels():
    return Channel.objects.all()


async def get_channel(pk):
    return Channel.objects.get(pk=pk)
