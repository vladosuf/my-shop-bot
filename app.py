import os
import asyncio
import logging
from flask import Flask
from bot import bot, dp
import nest_asyncio  # <-- Новая библиотека для решения проблемы!

# Применяем патч для asyncio
nest_asyncio.apply()

app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает! 🚀"

@app.route('/health')
def health():
    return "OK"

async def run_bot():
    """Запускает бота в асинхронном режиме"""
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Бот упал с ошибкой: {e}")

if __name__ == '__main__':
    # Запускаем бота в том же потоке, где и веб-сервер
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Запускаем бота как фоновую задачу
    bot_task = loop.create_task(run_bot())
    
    # Запускаем веб-сервер (Flask) в том же потоке
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)