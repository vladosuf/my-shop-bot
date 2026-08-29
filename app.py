import os
import asyncio
import threading
from flask import Flask
from bot import bot, dp
import logging

app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает! 🚀"

@app.route('/health')
def health():
    return "OK"

def run_bot():
    """Запускает бота в отдельном потоке"""
    try:
        asyncio.run(dp.start_polling(bot))
    except Exception as e:
        logging.error(f"Бот упал: {e}")

if __name__ == '__main__':
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logging.info("✅ Бот запущен в фоновом режиме")
    
    # Запускаем веб-сервер
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)