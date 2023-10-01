from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "🔄 Qayta ishga tushirish "),
            # types.BotCommand("stats", "📊 Bot stats"),
            # types.BotCommand("add_admin", "🧑‍💻 Add admin"),
            # types.BotCommand("send_post", "✉ Send AD to users"),
            types.BotCommand("about", "ℹ️ Bot haqida"),
        ]
    )
