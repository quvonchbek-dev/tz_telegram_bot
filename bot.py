from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType
from tg_bot.keyboards import inline, reply
from tg_bot.loader import bot, dp, db, Form, get_admin_ids
from aiogram import executor
from django.core.exceptions import ValidationError
from tg_bot.utils.notify_admins import on_startup_notify
from tg_bot.utils.set_default_commands import set_default_commands
from tg_bot.utils.tools import is_subscribed


async def get_admin_info(pk) -> str:
    admin = await db.get_admin(pk)
    user = admin.admin
    txt = f'👨‍💻 Admin: <a href="tg://user?id={user.chat_id}">{user.get_full_name()}</a>\n\n' \
          f'📛 Username: @{user.username or "null"}\n' \
          f'🆔 Chat ID: <code>{user.chat_id}</code>\n' \
          f'🔰 Role: <code>{admin.role}</code>'
    return txt


async def stats_info() -> str:
    total, active, blocked, today_used, today_joined = await db.get_stats()
    txt = f"<b><i>📊 Bot Stats 📊</i></b>\n\n" \
          f"👤 Total: {total}\n" \
          f"🟢 Active: {active}\n" \
          f"🔴 Blocked: {blocked}\n" \
          f"📱 Today used: {today_used}\n" \
          f"➕ Today joined: {today_joined}\n"
    return txt


async def get_channel_info(pk):
    channel = await db.get_channel(pk)
    txt = f'📣 Channel: {channel.title}\n\n' \
          f'🆔 Chat ID: <code>{channel.chat_id}</code>\n' \
          f'🔗 Link: {channel.invite_link}'
    return txt


async def is_superuser(chat_id):
    return (await db.get_admin(chat_id=chat_id)).role == "superuser"


async def send_sources(msg: Message):
    res_list = await db.get_resources(1)
    text = "Sources to use, I'm glad if you find it useful."
    if not res_list.exists():
        text = "🔍 There is not any resource."
    await msg.answer(text, reply_markup=await inline.select_resource(res_list, msg.chat.id in get_admin_ids()))


"""
Command handlers
"""


@dp.message_handler(commands=["start"], state="*")
async def start_message(msg: Message):
    await Form.nothing.set()
    new = await db.add_user(msg.chat)
    send_text = "😊 I'm glad to see you again!"
    if new:
        send_text = "👋 Hello, Welcome!"
    await msg.answer(send_text, reply_markup=await reply.main_menu(msg.chat.id in get_admin_ids()))


# @dp.message_handler(lambda msg: msg.chat.id in get_admin_ids(), commands=['add_admin'], state="*")
# async def add_admin_handler(msg: Message):
#     await msg.answer(
#         "Okay, send me a message from the person you want to add to admin.", reply_markup=await inline.cancel_mk())
#     await Form.add_admin.set()


# @dp.message_handler(lambda msg: msg.chat.id in get_admin_ids(), commands=['send_post'], state="*")
# async def send_post(msg: Message):
#     await msg.answer("Well, you can send me a Post or forward to send to users.",
#     reply_markup=await inline.cancel_mk())
#     await Form.send_post.set()


@dp.message_handler(lambda msg: msg.chat.id in get_admin_ids(), commands=['add_resource'], state="*")
async def add_resource_command(msg: Message):
    await msg.answer("📁 Ok, send me the file or video with the title.", reply_markup=await inline.cancel_mk())
    await Form.add_resource.set()


"""
Post handler
"""


@dp.message_handler(state=Form.add_resource, content_types=[ContentType.VIDEO, ContentType.DOCUMENT])
async def new_post(msg: Message):
    res = await db.add_resource(msg)
    await msg.reply(f"<code>{res.file_name}</code> has been added Successfully!")

    await Form.nothing.set()


@dp.message_handler(state=Form.add_admin)
async def add_admin(msg: Message):
    adm = await db.add_admin(msg)
    kb = await inline.cancel_mk()
    txt = "Unable to add admin. The error has been occurred."
    if adm:
        txt = f"{adm.admin.get_full_name()} has been added to list of admins."
        await Form.nothing.set()
        kb = await inline.admins_kb(
            await db.get_admins(),
            await is_superuser(msg.chat.id)
        )

    await msg.answer(txt, reply_markup=kb)


@dp.message_handler(state=Form.add_channel, content_types=ContentType.ANY)
async def add_channel_(msg: Message):
    chn = await db.add_channel(msg, bot)
    if chn:
        channels = await db.get_channels()
        title = msg.forward_from_chat.title
        await msg.answer(
            f"➕ <b>{title}</b> has been added to channels list successfully.",
            reply_markup=await inline.channels_kb(channels))
        await Form.nothing.set()
    else:
        await msg.answer(
            "Unable to add channel to channels list. Something is wrong, please try again.",
            reply_markup=await inline.cancel_mk()
        )


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
    await bot.delete_message(ch_id, msg.message_id + 1)
    await bot.send_message(
        ch_id, f"✅ Post sent to {cnt_suc} users.\n\n❌ Not sent to {cnt_err} users.",
        reply_markup=await reply.main_menu(True)
    )


"""
Text message handler
"""


@dp.message_handler(content_types=["text"], state=Form.edit_caption)
async def edit_caption(msg: Message, state: FSMContext):
    caption = msg.text
    pk = await state.get_data("pk")
    try:
        source = await db.get_resource(pk)
        source.title = caption
        await Form.nothing.set()
        await state.finish()
        await msg.reply("✅ Invite link of channel has been updated successfully.")
        await send_sources(msg)
    except ValidationError as e:
        await msg.reply(
            f"Unable to add channel. Below error has been occurred:\n\n<code>{e}</code>",
            reply_markup=await inline.cancel_mk()
        )


@dp.message_handler(content_types=["text"], state="*")
async def text_handler(msg: Message):
    if msg.text == "I AM YOUR OWNER!":
        await db.add_admin(msg, "superuser")
        await msg.reply("⚡ Welcome! You are SuperUser!\n\nHit /start to restart.")
        return
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


@dp.callback_query_handler(lambda call: call.data == "back_admin", state="*")
async def back_admin(call: CallbackQuery):
    await call.message.edit_text("👨‍💻 Admin Menu", reply_markup=await inline.admin_menu())


@dp.callback_query_handler(lambda call: "delete" in call.data or "archive" in call.data, state="*")
async def delete_r(call: CallbackQuery):
    data = call.data.split()
    r_id = int(data[-1])
    ch_id = call.message.chat.id
    res = await db.get_resource(r_id)
    res.status = 2 if data[0] == "archive_res" else 3
    res.save()
    await Form.nothing.set()
    await call.message.delete()
    await bot.send_message(
        ch_id,
        f"The <code>{res.file_name}</code> has been {data[0].replace('_res', 'd')} successfully."
    )
    await send_sources(call.message)


@dp.callback_query_handler(lambda call: "res_view" in call.data, state="*")
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
    txt = await stats_info()
    await call.message.edit_text(txt, reply_markup=await inline.back_admin_kb())
    # await call.message.delete()


@dp.callback_query_handler(lambda call: call.data == "send_post", state="*")
async def _send_post(call: CallbackQuery):
    await call.message.edit_text(
        "📩 Well, you can send me a Post or forward to send to users.",
        reply_markup=await inline.cancel_mk())
    await Form.send_post.set()


@dp.callback_query_handler(lambda call: call.data == "add_admin", state="*")
async def add_admin_(call: CallbackQuery):
    await call.message.edit_text(
        "Okay, send me a message from the person you want to add to admin.",
        reply_markup=await inline.cancel_mk()
    )
    await Form.add_admin.set()


@dp.callback_query_handler(lambda call: call.data == "add_channel", state="*")
async def add_channel(call: CallbackQuery):
    await call.message.edit_text("Ok, forward me some message from channel.", reply_markup=await inline.cancel_mk())
    await Form.add_channel.set()


@dp.callback_query_handler(lambda call: call.data == "admins", state="*")
async def admins_call(call: CallbackQuery):
    admins = await db.get_admins()
    chat_id = call.message.chat.id
    await call.message.edit_text(
        "Bot admins list", reply_markup=await inline.admins_kb(admins, await is_superuser(chat_id)))


@dp.callback_query_handler(lambda call: "admin_view" in call.data, state="*")
async def admin_view(call: CallbackQuery):
    data = call.data
    pk = data.split()[-1]
    txt = await get_admin_info(pk)
    chat_id = call.message.chat.id
    await call.answer()
    await call.message.edit_text(txt, reply_markup=await inline.admin_view(pk, await is_superuser(chat_id)))


@dp.callback_query_handler(lambda call: "change_role" in call.data, state="*")
async def change_role(call: CallbackQuery):
    data = call.data
    pk = data.split()[-1]
    await db.change_role(pk)

    txt = await get_admin_info(pk)
    chat_id = call.message.chat.id
    await call.answer()
    await call.message.edit_text(txt)
    await call.message.edit_reply_markup(reply_markup=await inline.admin_view(pk, await is_superuser(chat_id)))


@dp.callback_query_handler(lambda call: "remove_admin" in call.data, state="*")
async def remove_admin(call: CallbackQuery):
    data = call.data
    pk = data.split()[-1]
    name = (await db.get_admin(pk)).admin.get_full_name()
    await db.remove_admin(pk)
    await call.answer(f"{name} removed from admins list.")
    await admins_call(call)


@dp.callback_query_handler(lambda call: "cancel" in call.data, state="*")
async def cancel(call: CallbackQuery):
    await Form.nothing.set()
    await call.answer("⭕ Session has been cancelled")
    await back_admin(call)


@dp.callback_query_handler(lambda call: "remove_channel" in call.data, state="*")
async def remove_channel(call: CallbackQuery):
    data = call.data
    pk = data.split()[-1]
    channel = await db.get_channel(pk)
    name = channel.title
    channel.delete()
    await call.answer(f"{name} removed from Channels list.")
    await channels_call(call)


"""
Channels
"""


@dp.callback_query_handler(lambda call: call.data == "channels", state="*")
async def channels_call(call: CallbackQuery):
    channels = await db.get_channels()
    txt = "📣 Channels list." if channels else "The channels list is empty"
    await call.message.edit_text(txt, reply_markup=await inline.channels_kb(channels))


@dp.callback_query_handler(lambda call: "channel_view" in call.data, state="*")
async def channel_view(call: CallbackQuery):
    data = call.data
    pk = data.split()[-1]
    txt = await get_channel_info(pk)
    await call.answer()
    await call.message.edit_text(txt, reply_markup=await inline.channel_view(pk), disable_web_page_preview=True)


"""
Running bot
"""


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher, await db.get_admins())


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
