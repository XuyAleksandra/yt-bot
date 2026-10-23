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
        [InlineKeyboardButton(text="▶️ Открыть YouTube App", web_app=WebAppInfo(url=YOUTUBE_URL))],
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
        f"Нажми на кнопку ниже, чтобы запустить каталог YouTube:",
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

# HTML/JS интерфейс каталога YouTube с плеером внутри Mini App
async def handle_player(request):
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube Mini App</title>
        <style>
            body, html {
                margin: 0; padding: 0; width: 100%; height: 100%;
                background: #0f0f0f; color: #fff; font-family: Roboto, Arial, sans-serif;
                overflow-x: hidden;
            }
            .header {
                position: sticky; top: 0; background: #212121; padding: 12px 16px;
                display: flex; align-items: center; justify-content: space-between;
                box-shadow: 0 2px 5px rgba(0,0,0,0.5); z-index: 100;
            }
            .logo { font-size: 18px; font-weight: bold; color: #ff0000; display: flex; align-items: center; gap: 6px; }
            
            .feed {
                padding: 12px; display: flex; flex-direction: column; gap: 16px;
            }
            .video-card {
                background: #1f1f1f; border-radius: 12px; overflow: hidden; cursor: pointer;
                transition: transform 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }
            .video-card:active { transform: scale(0.98); }
            .thumbnail-container {
                position: relative; width: 100%; aspect-ratio: 16/9; background: #000;
            }
            .thumbnail-container img {
                width: 100%; height: 100%; object-fit: cover;
            }
            .video-info {
                padding: 10px 12px;
            }
            .video-title {
                font-size: 15px; font-weight: 500; margin-bottom: 4px;
                display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
            }
            .video-channel {
                font-size: 13px; color: #aaa;
            }

            /* Экран плеера */
            #playerView {
                display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: #0f0f0f; z-index: 200; flex-direction: column;
            }
            .player-header {
                background: #212121; padding: 12px 16px; display: flex; align-items: center; gap: 12px;
            }
            .back-btn {
                background: none; border: none; color: #fff; font-size: 16px; cursor: pointer; font-weight: bold;
            }
            .player-container {
                width: 100%; aspect-ratio: 16/9; background: #000;
            }
            .player-container iframe {
                width: 100%; height: 100%; border: none;
            }
        </style>
    </head>
    <body>

        <div class="header">
            <div class="logo">▶ YouTube Mini</div>
        </div>

        <!-- Лента видео -->
        <div class="feed" id="videoFeed"></div>

        <!-- Полноэкранный плеер внутри приложения -->
        <div id="playerView">
            <div class="player-header">
                <button class="back-btn" onclick="closePlayer()">← Назад</button>
                <span>Просмотр видео</span>
            </div>
            <div class="player-container" id="iframeBox"></div>
        </div>

        <script>
            const videos = [
                { id: "jfKfPfyJRdk", title: "lofi hip hop radio - beats to study/relax to", channel: "Lofi Girl" },
                { id: "5qap5aO4i9A", title: "Lofi Hip Hop - Beats to Relax/Study to [Live]", channel: "Lofi Girl Live" },
                { id: "dQw4w9WgXcQ", title: "Rick Astley - Never Gonna Give You Up (Official Music Video)", channel: "Rick Astley" },
                { id: "9bZkp7q19f0", title: "PSY - GANGNAM STYLE(강남스타일) M/V", channel: "officialpsy" }
            ];

            const feed = document.getElementById('videoFeed');

            videos.forEach(video => {
                const card = document.createElement('div');
                card.className = 'video-card';
                card.onclick = () => openPlayer(video.id);
                
                card.innerHTML = `
                    <div class="thumbnail-container">
                        <img src="https://img.youtube.com/vi/${video.id}/hqdefault.jpg" alt="thumbnail">
                    </div>
                    <div class="video-info">
                        <div class="video-title">${video.title}</div>
                        <div class="video-channel">${video.channel}</div>
                    </div>
                `;
                feed.appendChild(card);
            });

            function openPlayer(id) {
                const playerView = document.getElementById('playerView');
                const iframeBox = document.getElementById('iframeBox');
                
                iframeBox.innerHTML = `<iframe src="https://www.youtube.com/embed/${id}?autoplay=1" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
                playerView.style.display = 'flex';
            }

            function closePlayer() {
                const playerView = document.getElementById('playerView');
                const iframeBox = document.getElementById('iframeBox');
                
                iframeBox.innerHTML = '';
                playerView.style.display = 'none';
            }
        </script>
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
