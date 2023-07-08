from django.utils import timezone

from backend.models import BotUser, Channel, BotAdmin
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


async def get_channels_list():
    return Channel.objects.all()


async def get_admins():
    return BotAdmin.admins.all()


async def add_admin(msg: Message) -> BotAdmin:
    try:
        user = BotUser.objects.filter(chat_id=str(msg.forward_from.id)).first()
    except AttributeError:
        return False
    if not user:
        # Uzatilgan xabarni o'chirib qo'ysa
        user = await add_user(msg.forward_from)
    return BotAdmin.admins.create(admin=user)


async def get_stats():
    qs = BotUser.objects.all()
    total = qs.count()
    active = qs.filter(status=1).count()
    today = timezone.now()
    today_used = qs.filter(last_seen__month=today.month).filter(last_seen__day=today.day).count()
    today_joined = qs.filter(joined__month=today.month).filter(joined__day=today.day).count()
    print(today)
    return total, active, total - active, today_used, today_joined
