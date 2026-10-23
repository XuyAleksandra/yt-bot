import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    KeyboardButton,
    ReplyKeyboardMarkup,
    Message, 
    WebAppInfo
)

TOKEN = "8884918348:AAHKXppba5wpxs1aWKhYZU-_4PTuLjwLSfo"
YOUTUBE_URL = "https://m.youtube.com"
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=TOKEN)
dp = Dispatcher()

main_reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="▶️ Открыть YouTube", web_app=WebAppInfo(url=YOUTUBE_URL))]],
    resize_keyboard=True
)

main_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="▶️ Смотреть YouTube", web_app=WebAppInfo(url=YOUTUBE_URL))]]
)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет!\n\n"
        f"Нажми на кнопку ниже, чтобы запустить YouTube прямо внутри Telegram.",
        reply_markup=main_inline_keyboard
    )
    await message.answer("Кнопка добавлена в меню 👇", reply_markup=main_reply_keyboard)

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Web server started on port {PORT}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
