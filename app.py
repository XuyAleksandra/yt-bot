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
# Ссылка на ваш Cloudflare Worker для обхода блокировок
YOUTUBE_URL = "https://wispy-sunset-4f8a.strelokklik.workers.dev"
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=TOKEN)
dp = Dispatcher()

main_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Смотреть YouTube", web_app=WebAppInfo(url=YOUTUBE_URL))],
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
        f"Нажми на кнопку ниже, чтобы запустить плеер:",
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

# Легкая и стабильная HTML-страница с плеером YouTube
async def handle_player(request):
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube Player</title>
        <style>
            body, html {
                margin: 0; padding: 0; width: 100%; height: 100%;
                background: #0f0f0f; display: flex; justify-content: center; align-items: center;
                overflow: hidden;
            }
            .video-container {
                width: 100%; height: 100%;
            }
            iframe {
                width: 100%; height: 100%; border: none;
            }
        </style>
    </head>
    <body>
        <div class="video-container">
            <iframe src="https://www.youtube.com/embed/jfKfPfyJRdk?autoplay=1" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
            </iframe>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_player)
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
