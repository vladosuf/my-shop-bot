import os
import asyncio
from flask import Flask
from bot import bot, dp
import threading
import logging
from database import init_db

app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает! 🚀"

@app.route('/health')
def health():
    return "OK"

def run_flask():
    """Запускает веб-сервер в фоновом потоке"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

async def run_bot():
    """Запускает бота в главном потоке"""
    try:
        init_db()
        logging.info("✅ База данных инициализирована!")

        logging.info("🚀 Запуск бота...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Бот упал: {e}")

if __name__ == '__main__':
    # Запускаем Flask в фоновом потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logging.info("✅ Веб-сервер запущен в фоновом режиме")
    
    # Запускаем бота в главном потоке
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")