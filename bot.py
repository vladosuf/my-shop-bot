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


@dp.message(Command("start"))
async def start_command(message: Message):
    logger.info(f"👤 Пользователь {message.from_user.id} запустил бота")


    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛍️ Купить Stars", callback_data="buy_stars"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="info"),
        ]
    ])
    await message.answer( 
        "🌟 Привет! Я бот для продажи Telegram Stars.\n\nЗдесь ты можешь купить звезды для своих каналов и ботов.\nВыбери действие ниже:",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "buy_stars")
async def show_products(callback: types.CallbackQuery):
    """Показываем список товаров"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐ 50 Stars — 65 ₽", callback_data="buy_50"),
            InlineKeyboardButton(text="⭐ 100 Stars — 130 ₽", callback_data="buy_100"),
            InlineKeyboardButton(text="⭐ 150 Stars — 195 ₽", callback_data="buy_150"),
        ],
        [
            InlineKeyboardButton(text="⭐ 200 Stars — 260 ₽", callback_data="buy_200"),
            InlineKeyboardButton(text="⭐ 250 Stars — 325 ₽", callback_data="buy_250"),
            InlineKeyboardButton(text="⭐ 500 Stars — 650 ₽", callback_data="buy_500"),
        ],
        [
            InlineKeyboardButton(text="⭐ 750 Stars — 975 ₽", callback_data="buy_750"),
            InlineKeyboardButton(text="⭐ 1000 Stars — 1300 ₽", callback_data="buy_1000"),
            InlineKeyboardButton(text="⭐ 2500 Stars — 3250 ₽", callback_data="buy_2500"),
        ],
        [
            InlineKeyboardButton(text="⭐ 5000 Stars — 6500 ₽", callback_data="buy_5000"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"),
        ]
    ])
    
    await callback.message.edit_text(
        "🌟 Выбери нужный пакет Stars:",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def process_purchase(callback: types.CallbackQuery):
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
    2500: 3250,
    5000: 6500
}
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"⭐ {stars_amount} Stars",
        description=f"Покупка {stars_amount} Telegram Stars для твоего канала",
        payload=f"stars_{stars_amount}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=f"{stars_amount} Stars", amount=stars_amount)],
        start_parameter="shop",
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    payment = message.successful_payment
    payload = payment.invoice_payload
    stars_amount = payload.split("_")[1]

    logger.info(f"💰 Покупка: {message.from_user.id} купил {stars_amount} Stars")

    await message.answer(
        f"✅ Оплата прошла успешно!\n\nТы купил {stars_amount} Stars.\n📦 Товар отправлен на твой баланс.\n\nСпасибо за покупку! 🌟"
    )

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛍️ Купить Stars", callback_data="buy_stars"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="info"),
        ]
    ])
    await callback.message.edit_text("🌟 Главное меню:\n\nВыбери действие:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "info")
async def show_info(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ *О боте*\n\nЭтот бот помогает покупать Telegram Stars.\nStars — это валюта Telegram для поддержки авторов.\n\n💰 *Как это работает:*\n1. Выбери нужный пакет\n2. Оплати внутри Telegram\n3. Получи Stars на свой аккаунт\n\n❓ Вопросы? Пиши @support_username",
        parse_mode="Markdown"
    )
    await callback.answer()

dp.include_router(admin_router)

async def main():
    try:
        logger.info("🚀 Бот запущен и готов к работе!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())