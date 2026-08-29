import os
import threading
from flask import Flask
from bot import bot, dp
from aiogram.types import Update
import asyncio
import logging

app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает! 🚀"

@app.route('/health')
def health():
    return "OK"

def run_bot():
    asyncio.run(dp.start_polling(bot))

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)