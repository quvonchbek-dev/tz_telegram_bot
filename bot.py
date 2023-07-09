from aiogram.types import Message, CallbackQuery, ContentType
from tg_bot.keyboards import inline, reply
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
    await msg.answer(send_text, reply_markup=await reply.main_menu(msg.chat.id in get_admin_ids()))


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
async def send_post(msg: Message):
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


@dp.message_handler(lambda msg: msg.chat.id in get_admin_ids(), commands=['add_resource'], state="*")
async def add_resource_command(msg: Message):
    await msg.answer("📁 Ok, send me the file or video with the title.\n\n/cancel to cancel session.")
    await Form.add_resource.set()


@dp.message_handler(lambda msg: msg.chat.id in get_admin_ids(), commands=['resources'], state="*")
async def resources_command(msg: Message):
    resources = await db.get_resources(1)
    await msg.answer("Resources to use, I'm glad if you find it useful.")


"""
Post handler
"""


@dp.message_handler(state=Form.add_resource, content_types=[ContentType.VIDEO, ContentType.DOCUMENT])
async def new_post(msg: Message):
    res = await db.add_resource(msg)
    # Res Added Success
    await msg.reply(f"<code>{res.file_name}</code> has added Successfully!")

    await Form.nothing.set()


@dp.message_handler(state=Form.add_admin)
async def add_admin(msg: Message):
    adm = await db.add_admin(msg)
    txt = "Unable to add admin. The error has been occurred.\n\n/cancel to cancel the session."
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


async def send_sources(msg: Message):
    res_list = await db.get_resources(1)
    text = "Resources to use, I'm glad if you find it useful."
    if not res_list.exists():
        text = "🔍 There is not any resource."
    await msg.answer(text, reply_markup=await inline.select_resource(res_list, msg.chat.id in get_admin_ids()))


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
    if msg.text == reply.Menu.SOURCES:
        await send_sources(msg)
    elif msg.text == reply.Menu.FOR_ADMINS:
        if ch_id not in get_admin_ids():
            await msg.answer("😐 Sorry, but You are not in admins list.")
        await msg.answer("👤 Admin panel", reply_markup=await inline.admin_menu())
    else:
        await msg.answer("404 command not found :)")


"""
CallBack Query handlers
"""


@dp.callback_query_handler(lambda call: call.data == "check_subscription", state="*")
async def check_subs(call: CallbackQuery):
    await call.message.answer("😊 You have subscribed to all our channels, now you can use our bot.")


@dp.callback_query_handler(lambda call: "delete" in call.data or "archive" in call.data, state="*")
async def delete_r(call: CallbackQuery):
    data = call.data.split()
    r_id = int(data[-1])
    ch_id = call.message.chat.id
    await db.change_status_resource(r_id, 2 if data[0] == "archive_res" else 3)
    await Form.nothing.set()
    await call.message.delete()
    await bot.send_message(ch_id, f"The file has been {data[0].replace('_res', 'd')} successfully.")
    await send_sources(call.message)


@dp.callback_query_handler(lambda call: "view" in call.data, state="*")
async def view(call: CallbackQuery):
    data = call.data.split()
    r_id = int(data[-1])
    ch_id = call.message.chat.id
    obj = await db.get_resource(r_id)
    kb = await inline.res_view(r_id, ch_id in get_admin_ids())
    if obj.file_type == "VIDEO":
        await bot.send_video(ch_id, obj.file_id, caption=obj.title, reply_markup=kb)
    else:
        await bot.send_document(ch_id, obj.file_id, caption=obj.title, reply_markup=kb)
    # await call.answer()
    await call.message.delete()


@dp.callback_query_handler(lambda call: call.data == "back", state="*")
async def back_button(call: CallbackQuery):
    await send_sources(call.message)
    await call.message.delete()


@dp.callback_query_handler(lambda call: call.data == "sources", state="*")
async def sources_(call: CallbackQuery):
    await send_sources(call.message)
    await call.message.delete()


@dp.callback_query_handler(lambda call: call.data == "add_resource", state="*")
async def _add_source(call: CallbackQuery):
    await add_resource_command(call.message)
    await call.message.delete()


@dp.callback_query_handler(lambda call: call.data == "stats", state="*")
async def _add_source(call: CallbackQuery):
    await stats(call.message)
    # await call.message.delete()


@dp.callback_query_handler(lambda call: call.data == "send_post", state="*")
async def _send_post(call: CallbackQuery):
    await send_post(call.message)
    await call.message.delete()


@dp.callback_query_handler(lambda call: call.data == "admins", state="*")
async def admins_call(call: CallbackQuery):
    admins = await db.get_admins()


"""
Running bot
"""


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher, await db.get_admins())


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
