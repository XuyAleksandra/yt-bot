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
# Рабочая ссылка через Cloudflare Worker для обхода блокировок
YOUTUBE_URL = "https://wispy-sunset-4f8a.strelokklik.workers.dev"
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Клавиатура с кнопкой запуска YouTube и кнопкой перезапуска
main_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Смотреть YouTube", web_app=WebAppInfo(url=YOUTUBE_URL))],
        [InlineKeyboardButton(text="🔄 Перезапустить", callback_data="restart")]
    ]
)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    # Удаляем сообщение пользователя (/start), чтобы не засорять чат
    try:
        await message.delete()
    except Exception:
        pass
    
    # Отправляем приветствие с обновленной клавиатурой
    await message.answer(
        f"Привет!\n\n"
        f"Нажми на кнопку ниже, чтобы запустить YouTube прямо внутри Telegram.",
        reply_markup=main_inline_keyboard
    )

@dp.callback_query(F.data == "restart")
async def restart_callback(callback: CallbackQuery) -> None:
    # Обновляем текущее сообщение при нажатии кнопки перезапуска
    await callback.message.edit_text(
        f"Привет!\n\n"
        f"Бот успешно перезапущен. Нажми на кнопку ниже, чтобы открыть YouTube:",
        reply_markup=main_inline_keyboard
    )
    await callback.answer("Готово!")

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
