import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
from aiogram.enums import ContentType
from dotenv import load_dotenv
from admin import router as admin_router
from logger import logger

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(admin_router)


@dp.message(Command("start"))
async def start_command(message: Message):
    logger.info(f"👤 Пользователь {message.from_user.id} запустил бота")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Купить Звёзды", callback_data="buy_stars"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="info"),
        ]
    ])
    
    await message.answer(
        "🚀 Привет!\n\n"
        "🚀С помощью этого бота можно купить ⭐Звёзды и 🌠Премиум.\n"
        "🚀Выбери действие чтобы перейти к покупке",
        reply_markup=keyboard
    )


@dp.callback_query(F.data == "buy_stars")
async def show_products(callback: types.CallbackQuery):
    """Показываем список товаров"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐ 50 Звёзд — 65 ₽", callback_data="buy_50"),
            InlineKeyboardButton(text=" 100 Звёзд — 130 ₽", callback_data="buy_100"),
            InlineKeyboardButton(text=" 150 Звёзд — 195 ₽", callback_data="buy_150"),
        ],
        [
            InlineKeyboardButton(text="⭐ 200 Звёзд — 260 ₽", callback_data="buy_200"),
            InlineKeyboardButton(text="⭐ 250 Звёзд — 325 ₽", callback_data="buy_250"),
            InlineKeyboardButton(text="⭐ 500 Звёзд — 650 ₽", callback_data="buy_500"),
        ],
        [
            InlineKeyboardButton(text="⭐ 750 Звёзд — 975 ₽", callback_data="buy_750"),
            InlineKeyboardButton(text="⭐ 1000 Звёзд — 1300 ₽", callback_data="buy_1000"),
            InlineKeyboardButton(text="⭐ 1750 Звёзд — 2275 ₽", callback_data="buy_1750"),
        ],
        [
            InlineKeyboardButton(text="⭐ 2500 Звёзд — 3250 ₽", callback_data="buy_2500"),
            InlineKeyboardButton(text="⭐ 5000 Звёзд — 6500 ₽", callback_data="buy_5000"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"),
        ]
    ])
    
    await callback.message.edit_text(
        "🚀 Выбери нужный пакет Звёзд:",
        reply_markup=keyboard
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("buy_"))
async def process_purchase(callback: types.CallbackQuery):
    """Создаем счет для оплаты Stars"""
    
    product_code = callback.data.split("_")[1]
    stars_amount = int(product_code)
    
    prices = {
        50: 65,
        100: 130,
        150: 195,
        200: 260,
        250: 325,
        500: 650,
        750: 975,
        1000: 1300,
        1750: 2275,
        2500: 3250,
        5000: 6500
    }
    
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"🚀 {stars_amount} Звёзд",
        description=f"Покупка {stars_amount} Telegram Звёзд для твоего канала",
        payload=f"stars_{stars_amount}",
        provider_token="",
        currency="XTR",
        prices=[
            LabeledPrice(label=f"{stars_amount} Звёзд", amount=stars_amount)
        ],
        start_parameter="shop",
    )
    
    await callback.answer()


@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """Проверка перед оплатой"""
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    """Оплата прошла успешно!"""
    
    payment = message.successful_payment
    payload = payment.invoice_payload
    stars_amount = payload.split("_")[1]
    
    logger.info(f"💰 Покупка: {message.from_user.id} купил {stars_amount} Звёзд")
    
    await message.answer(
        f"✅ Оплата прошла успешно!\n\n"
        f"🚀 Ты купил {stars_amount} Звёзд.\n"
        f"📦 Товар отправлен на твой баланс.\n\n"
        f"Спасибо за покупку! 🚀"
    )


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Купить Звёзды", callback_data="buy_stars"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="info"),
        ]
    ])
    
    await callback.message.edit_text(
        "🚀 Главное меню:\n\nВыбери действие:",
        reply_markup=keyboard
    )
    await callback.answer()


@dp.callback_query(F.data == "info")
async def show_info(callback: types.CallbackQuery):
    """Информация о боте"""
    await callback.message.edit_text(
        "ℹ️ *О боте*\n\n"
        "Этот бот помогает покупать Telegram Звёзды.\n"
        "Звёзды — это валюта Telegram для поддержки авторов.\n\n"
        "💰 *Как это работает:*\n"
        "1. Выбери нужный пакет\n"
        "2. Оплати внутри Telegram\n"
        "3. Получи Звёзды на свой аккаунт\n\n"
        "🚀 *Курс:* 1 Звезда = 1.3 ₽\n\n"
        "❓ Вопросы? Пиши @vladosuf",
        parse_mode="Markdown"
    )
    await callback.answer()


async def main():
    try:
        logger.info("🚀 Бот запущен и готов к работе!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())