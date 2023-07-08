from aiogram.types import Message, CallbackQuery, ContentType
from tg_bot.keyboards import inline
from tg_bot.loader import bot, dp, db, Form, get_admin_ids
from aiogram import executor

from tg_bot.utils.notify_admins import on_startup_notify
from tg_bot.utils.set_default_commands import set_default_commands
from tg_bot.utils.tools import is_subscribed

"""
Command handlers
"""


@dp.message_handler(commands=["start"], state="*")
async def start_message(msg: Message):
    new = await db.add_user(msg.chat)
    send_text = "😊 I'm glad to see you again!"
    if new:
        send_text = "👋 Hello, Welcome!"
    await msg.answer(send_text)


@dp.message_handler(lambda msg: msg.chat.id in get_admin_ids(), commands=['add_admin'], state="*")
async def add_admin_handler(msg: Message):
    await msg.answer(
        "Okay, send me a message from the person you want to add to admin. /cancel to cancel")
    await Form.add_admin.set()


@dp.message_handler(lambda msg: msg.chat.id in get_admin_ids(), commands=['admins'], state="*")
async def start_handler(msg: Message):
    adm = db.BotAdmin.admins.all()
    txt = "<b><i>👨‍💻 BOT ADMINS</i></b>\n\n"
    for i, a in enumerate(adm):
        txt += f'<b><i>{i + 1}. <a href="tg://user?id={a.admin.chat_id}">{a.admin.get_full_name()}</a></i></b>\n'
    await msg.answer(txt)
    await Form.nothing.set()


@dp.message_handler(lambda msg: msg.chat.id in get_admin_ids(), commands=['send_post'], state="*")
async def _send_post(msg: Message):
    await msg.answer("Well, you can send me a Post or forward to send to users.\n\n/cancel to cancel session.")
    await Form.send_post.set()


@dp.message_handler(lambda msg: msg.chat.id in get_admin_ids(), commands=["cancel"], state="*")
async def cancel_handler(msg: Message):
    await Form.nothing.set()
    await msg.answer("Canceled.")


@dp.message_handler(commands=["stats"], state="*")
async def stats(msg: Message):
    total, active, blocked, today_used, today_joined = await db.get_stats()
    txt = f"<b><i>📊 BOT STATS 📊</i></b>\n\n" \
          f"👤 Total: {total}\n" \
          f"🟢 Active: {active}\n" \
          f"🔴 Blocked: {blocked}\n" \
          f"📱 Today used: {today_used}\n" \
          f"➕ Today joined: {today_joined}\n"
    await msg.answer(txt)


"""
Post handler
"""


@dp.message_handler(state=Form.add_admin)
async def add_admin(msg: Message):
    adm = await db.add_admin(msg)
    txt = "Unable to add admin. The error has been occurred."
    if adm:
        txt = f"{adm.admin.get_full_name()} has added to list of admins. /admins to see all admins"
        await Form.nothing.set()

    await msg.answer(txt)


@dp.message_handler(state=Form.send_post, content_types=ContentType.ANY)
async def send_post_users(msg: Message):
    await Form.nothing.set()
    ch_id = msg.chat.id
    msg_id = int(msg.message_id)
    users = await db.get_users()
    cnt_suc = 0
    cnt_err = 0
    st = "⌛️⏳"
    await msg.answer("⏳ Sending...")
    for user in users:
        try:
            if user.chat_id != str(ch_id):
                await msg.copy_to(user.chat_id)
                await bot.edit_message_text(f"{st[cnt_suc % 2]}Sending...  {user.get_full_name()}", ch_id, msg_id + 1)
                cnt_suc += 1

        except Exception as e:
            print(e)
            cnt_err += 1
    await bot.edit_message_text(f"✅ Post sent to {cnt_suc} users.\n\n❌ Not sent to {cnt_err} users.", ch_id, msg_id + 1)


"""
Text message handler
"""


@dp.message_handler(content_types=["text"], state="*")
async def text_handler(msg: Message):
    ch_id = msg.chat.id
    channels = await is_subscribed(ch_id)
    if channels:
        await bot.send_message(
            ch_id, "✅ To use the bot, please subscribe to the following channels.",
            reply_markup=inline.subscription(channels)
        )
        return


"""
CallBack Query handlers
"""


@dp.callback_query_handler(lambda call: call.data == "check_subscription", state="*")
async def check_subs(call: CallbackQuery):
    await call.message.answer("😊 You have subscribed to all our channels, now you can use our bot.")


"""
Running bot
"""


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher, await db.get_admins())


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
