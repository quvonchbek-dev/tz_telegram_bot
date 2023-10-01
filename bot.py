from aiogram import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType

from tg_bot import config
from tg_bot.keyboards import inline, reply
from tg_bot.loader import bot, dp, db, Form, get_admin_ids
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


async def is_superuser(chat_id) -> bool:
    adm = await db.get_admin(chat_id=chat_id)
    if adm:
        return adm.role == "superuser"
    return False


def is_admin(msg):
    return msg.chat.id in get_admin_ids()


async def return_main_menu(msg: Message):
    text = "Bosh menyu"
    await msg.answer(text, reply_markup=await reply.main_menu(admin=is_admin(msg)))


async def send_sources_menu(msg: Message):
    section = config.SECTION_ITEMS.index(msg.text)
    text = msg.text
    res_list = await db.get_resources(1, section)
    if not res_list.exists() and not is_admin(msg):
        await msg.answer("🔍 Bu bo'limda ma'lumotlar topilmadi.")
        return
    # msg_temp = await msg.answer(text, reply_markup=ReplyKeyboardRemove())
    # await msg_temp.delete()
    await msg.answer(f"{text} bo'limi", reply_markup=await inline.select_resource(res_list, is_admin(msg), section))


"""
Command handlers
"""


@dp.message_handler(commands=["start"], state="*")
async def start_message(msg: Message):
    await Form.nothing.set()
    new = await db.add_user(msg.chat)
    await msg.answer(
        "🏛 Hisob(Calculus) BOT\n\n👋 Salom! Botimizga xush kelibsiz.\n\nKerakli bo'limni pastdan tanlashingiz mumkin 👇.",
        reply_markup=await reply.main_menu(is_admin(msg)))


@dp.message_handler(commands=["about"], state="*")
async def about(msg: Message):
    await msg.answer("Ushbu bot 🏛 TATU talabalariga Hisob(Calculus) fanidan foydali manbalarni ulashish uchun "
                     "yaratildi.\n\n🧑‍🏫 Ustoz: Shohjahon Eshmirzayev\n\n👨‍💻Yaratuvchi: @quvonchbek_dev")


@dp.message_handler(is_admin, commands=['add_resource'], state="*")
async def add_resource_command(msg: Message):
    await msg.answer("📁 Yaxshi, menga fayl yoki videoni sarlavhasi bilan yuboring.",
                     reply_markup=await inline.cancel_mk())
    await Form.add_resource.set()


"""
Post handler
"""


@dp.message_handler(state=Form.add_resource, content_types=[ContentType.VIDEO, ContentType.DOCUMENT])
async def new_post(msg: Message, state: FSMContext):
    section = (await state.get_data()).get("section")
    res = await db.add_resource(msg, section if section else 0)
    await msg.reply(f"✅ <code>{res.file_name}</code> <b>{config.SECTION_ITEMS[section]}</b> bo'limiga qo'shildi!")
    await Form.nothing.set()
    await state.finish()


@dp.message_handler(state=Form.add_admin)
async def add_admin(msg: Message):
    await bot.delete_message(msg.chat.id, msg.message_id - 1)
    adm = await db.add_admin(msg)
    kb = await inline.cancel_mk()
    txt = "⚠ Unable to add admin. The error has been occurred. Please try again."
    if adm:
        txt = f"✅ {adm.admin.get_full_name()} adminlar ro'yxatiga qo'shildi."
        await Form.nothing.set()
        kb = await inline.admins_kb(
            await db.get_admins(),
            await is_superuser(msg.chat.id)
        )

    await msg.answer(txt, reply_markup=kb)


@dp.message_handler(state=Form.add_channel, content_types=ContentType.ANY)
async def add_channel_(msg: Message):
    await bot.delete_message(msg.chat.id, msg.message_id - 1)
    chn = await db.add_channel(msg, bot)
    if chn:
        channels = await db.get_channels()
        title = msg.forward_from_chat.title
        await msg.answer(
            f"➕ <b>{title}</b> kanallar ro'yxatiga qo'shildi.",
            reply_markup=await inline.channels_kb(channels))
        await Form.nothing.set()
    else:
        await msg.answer(
            "⚠ Unable to add channel to channels list. Something is wrong, please try again.",
            reply_markup=await inline.cancel_mk()
        )


@dp.message_handler(state=Form.send_post, content_types=ContentType.ANY)
async def send_post_users(msg: Message):
    await bot.delete_message(msg.chat.id, msg.message_id - 1)
    await Form.nothing.set()
    ch_id = msg.chat.id
    msg_id = int(msg.message_id)
    users = await db.get_users()
    cnt_suc = 0
    cnt_err = 0
    st = "⌛️⏳"
    await msg.answer("⏳ Yuborilmoqda...")
    for cnt, user in enumerate(users):
        try:
            if user.chat_id != str(ch_id):
                await msg.copy_to(user.chat_id)
                if cnt % 5 == 0:
                    await bot.edit_message_text(f"{st[cnt_suc % 2]}Yuborilmoqda...  {user.get_full_name()}", ch_id,
                                                msg_id + 1)
                cnt_suc += 1

        except Exception as e:
            # print(e)
            cnt_err += 1
    await bot.delete_message(ch_id, msg.message_id + 1)
    await bot.send_message(
        ch_id, f"✅ Yuborildi: {cnt_suc} kishi.\n\n❌ Yuborilmadi: {cnt_err} kishi.",
        reply_markup=await reply.main_menu(True)
    )


"""
Text message handler
"""


@dp.message_handler(content_types=["text"], state=Form.edit_caption)
async def edit_caption(msg: Message, state: FSMContext):
    await bot.delete_message(msg.chat.id, msg.message_id - 1)
    caption = msg.text
    pk = (await state.get_data()).get("pk")
    try:
        source = await db.get_resource(pk)
        source.title = caption
        source.save()
        await Form.nothing.set()
        await msg.answer(f"✅ <code>{source.file_name}</code> ning sarlavhasi yangilandi.")
        await return_main_menu(msg)
    except Exception as e:
        await msg.reply(
            f"⚠ Unable to edit caption. Below error has been occurred:\n\n<code>{e}</code>\n\nPlease try again.",
            reply_markup=await inline.cancel_mk()
        )


@dp.message_handler(content_types=["text"], state="*")
async def text_handler(msg: Message):
    if msg.text == "14MY0UR0WN3R":
        await db.add_admin(msg, "superuser")
        await msg.reply("⚡ Xush kelibsiz SuperUser!\n\n🔐 Maxfiy so'z qabul qilindi :)\n\n/start ni bosing.")
        return
    ch_id = msg.chat.id
    channels = await is_subscribed(ch_id)
    if channels:
        await bot.send_message(
            ch_id, "✅ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling.",
            reply_markup=await inline.subscription(channels)
        )
        return
    if msg.text in config.SECTION_ITEMS:
        await send_sources_menu(msg)
    elif msg.text == reply.Menu.FOR_ADMINS:
        if ch_id not in get_admin_ids():
            await msg.answer("😐 Afsus, siz adminlar ro'yxatida emassiz.")
            return
        await msg.answer("👤 Admin panel", reply_markup=await inline.admin_menu())
    else:
        await msg.answer("404 command not found :) 👉 /start")


"""
CallBack Query handlers
"""


@dp.callback_query_handler(Text(startswith="edit_res"), state="*")
async def edit_res_(call: CallbackQuery, state: FSMContext):
    dc = {"pk": int(call.data.split()[-1])}
    await call.message.delete()
    await bot.send_message(
        call.from_user.id, "📝 Yaxshi, menga fayl uchun sarlavha yuboring.",
        reply_markup=await inline.cancel_mk())
    await state.set_data(dc)
    await Form.edit_caption.set()


@dp.callback_query_handler(Text("check_subscription"), state="*")
async def check_subs(call: CallbackQuery):
    ch_id = call.message.chat.id
    msg_id = call.message.message_id
    ch_list = await is_subscribed(ch_id)
    if ch_list:
        try:
            await bot.edit_message_reply_markup(ch_id, msg_id, reply_markup=await inline.subscription(ch_list))
        except Exception:
            await bot.answer_callback_query(call.id, "Iltimos hamma kanallarga obuna bo'ling :)", show_alert=True)
    else:
        await bot.delete_message(ch_id, msg_id)
        await bot.send_message(
            ch_id,
            "😊 Siz hamma kanallarga obuna bo'ldingiz. Botdan foydalanishingiz mumkin.",
            reply_markup=await reply.main_menu(await is_superuser(ch_id))
        )


@dp.callback_query_handler(Text("back_admin"), state="*")
async def back_admin(call: CallbackQuery):
    await call.message.edit_text("👨‍💻 Admin Panel", reply_markup=await inline.admin_menu())


@dp.callback_query_handler(lambda call: "delete" in call.data or "archive" in call.data, state="*")
async def delete_r(call: CallbackQuery):
    await call.message.delete()
    data = call.data.split()
    r_id = int(data[-1])
    ch_id = call.message.chat.id
    res = await db.get_resource(r_id)
    res.status = 2 if data[0] == "archive_res" else 3
    res.save()
    await Form.nothing.set()
    await bot.send_message(
        ch_id,
        f"🗑 <code>{res.file_name}</code> fayli o'chirildi. Qayta tiklash uchun Server adminiga murojaat qiling."
    )
    await return_main_menu(call.message)


@dp.callback_query_handler(Text(contains="res_view"), state="*")
async def view(call: CallbackQuery):
    if is_admin(call.message):
        await call.message.delete()
    else:
        await call.answer()
    data = call.data.split()
    r_id = int(data[-1])
    ch_id = call.message.chat.id
    obj = await db.get_resource(r_id)
    kb = await inline.res_view(r_id, is_admin(call.message), obj.section)
    if obj.file_type == "VIDEO":
        await bot.send_video(ch_id, obj.file_id, caption=obj.title, reply_markup=kb)
    else:
        await bot.send_document(ch_id, obj.file_id, caption=obj.title, reply_markup=kb)


@dp.callback_query_handler(Text("back"), state="*")
async def back_button(call: CallbackQuery):
    await call.message.delete()
    await return_main_menu(call.message)


@dp.callback_query_handler(Text(startswith="back_to_menu"), state="*")
async def back_to_menu(call: CallbackQuery):
    await call.message.delete()

    section = int(call.data.split()[1])
    text = config.SECTION_ITEMS[section]
    res_list = await db.get_resources(1, section)
    if not res_list.exists():
        await call.message.edit_text("🔍 Bu bo'limda ma'lumotlar topilmadi.")
        return
    await call.message.answer(f"{text} bo'limi",
                              reply_markup=await inline.select_resource(res_list, is_admin(call.message), section))
    # await call.message.edit_reply_markup(reply_markup=await inline.select_resource())


@dp.callback_query_handler(Text("sources"), state="*")
async def sources_(call: CallbackQuery):
    await call.message.delete()
    await return_main_menu(call.message)


@dp.callback_query_handler(Text(startswith="add_resource"), state="*")
async def _add_source(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    section = int(call.data.split()[1])
    await state.set_data({"section": section})
    await add_resource_command(call.message)


@dp.callback_query_handler(Text("stats"), state="*")
async def _add_source(call: CallbackQuery):
    txt = await stats_info()
    await call.message.edit_text(txt, reply_markup=await inline.back_admin_kb())


@dp.callback_query_handler(Text("send_post"), state="*")
async def _send_post(call: CallbackQuery):
    await call.message.edit_text(
        "📩 Yaxshi, menga xabar yuboring, men uni foydalanuvchilarga yuboraman.",
        reply_markup=await inline.cancel_mk())
    await Form.send_post.set()


@dp.callback_query_handler(Text("add_admin"), state="*")
async def add_admin_(call: CallbackQuery):
    await call.message.edit_text(
        "Yaxshi, menga qo'shmoqchi bo'lgan adminingizdan xabarni Ulashing(Forward qiling).",
        reply_markup=await inline.cancel_mk()
    )
    await Form.add_admin.set()


@dp.callback_query_handler(Text("add_channel"), state="*")
async def add_channel(call: CallbackQuery):
    await call.message.edit_text("Qo'shmoqchi bo'lgan kanalingizdan xabar ulashing.",
                                 reply_markup=await inline.cancel_mk())
    await Form.add_channel.set()


@dp.callback_query_handler(Text("admins"), state="*")
async def admins_call(call: CallbackQuery):
    admins = await db.get_admins()
    chat_id = call.message.chat.id
    await call.message.edit_text(
        "Bot admins list", reply_markup=await inline.admins_kb(admins, await is_superuser(chat_id)))


@dp.callback_query_handler(Text(startswith="admin_view"), state="*")
async def admin_view(call: CallbackQuery):
    data = call.data
    pk = data.split()[-1]
    txt = await get_admin_info(pk)
    chat_id = call.message.chat.id
    await call.answer()
    await call.message.edit_text(txt, reply_markup=await inline.admin_view(pk, await is_superuser(chat_id)))


@dp.callback_query_handler(Text(startswith="change_role"), state="*")
async def change_role(call: CallbackQuery):
    data = call.data
    pk = data.split()[-1]
    await db.change_role(pk)

    txt = await get_admin_info(pk)
    chat_id = call.message.chat.id
    await call.answer()
    await call.message.edit_text(txt)
    await call.message.edit_reply_markup(reply_markup=await inline.admin_view(pk, await is_superuser(chat_id)))


@dp.callback_query_handler(Text(startswith="remove_admin"), state="*")
async def remove_admin(call: CallbackQuery):
    data = call.data
    pk = data.split()[-1]
    name = (await db.get_admin(pk)).admin.get_full_name()
    await db.remove_admin(pk)
    await call.answer(f"{name} adminlar ro'yxatidan o'chirildi.")
    await admins_call(call)


@dp.callback_query_handler(Text(contains="cancel"), state="*")
async def cancel(call: CallbackQuery):
    await call.message.delete()
    await Form.nothing.set()
    await call.answer("⭕ Sessiya bekor qilindi.")
    await return_main_menu(call.message)


@dp.callback_query_handler(Text(contains="remove_channel"), state="*")
async def remove_channel(call: CallbackQuery):
    data = call.data
    pk = data.split()[-1]
    channel = await db.get_channel(pk)
    name = channel.title
    channel.delete()
    await call.answer(f"{name} kanallar ro'yxatidan o'chirildi.")
    await channels_call(call)


"""
Channels
"""


@dp.callback_query_handler(Text("channels"), state="*")
async def channels_call(call: CallbackQuery):
    channels = await db.get_channels()
    txt = "📣 Channels list." if channels else "Kanallar ro'yxati bo'sh"
    await call.message.edit_text(txt, reply_markup=await inline.channels_kb(channels))


@dp.callback_query_handler(Text(startswith="channel_view"), state="*")
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
