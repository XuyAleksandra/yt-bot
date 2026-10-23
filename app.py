import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    Message, 
    WebAppInfo,
    CallbackQuery
)

TOKEN = "8884918348:AAHKXppba5wpxs1aWKhYZU-_4PTuLjwLSfo"
# Прямая ссылка на мобильный YouTube без сторонних прокси
YOUTUBE_URL = "https://m.youtube.com"
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=TOKEN)
dp = Dispatcher()

main_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Открыть YouTube", web_app=WebAppInfo(url=YOUTUBE_URL))],
        [InlineKeyboardButton(text="🔄 Перезапустить", callback_data="restart")]
    ]
)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        await message.delete()
    except Exception:
        pass
    
    await message.answer(
        f"Привет!\n\n"
        f"Нажми на кнопку ниже, чтобы запустить YouTube:",
        reply_markup=main_inline_keyboard
    )

@dp.callback_query(F.data == "restart")
async def restart_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        f"Привет!\n\n"
        f"Бот перезапущен. Нажми кнопку ниже:",
        reply_markup=main_inline_keyboard
    )
    await callback.answer("Готово!")

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    # Запуск локального веб-сервера для Render
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Web server successfully started on port {PORT}")

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
