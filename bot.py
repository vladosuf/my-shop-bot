import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
from aiogram.enums import ContentType
from dotenv import load_dotenv
from admin import router as admin_router

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


dp.include_router(admin_router)

@dp.message(Command("start"))
async def start_command(message: Message):
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
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐ 100 Stars — 150 ₽", callback_data="buy_100"),
            InlineKeyboardButton(text="⭐ 500 Stars — 700 ₽", callback_data="buy_500"),
        ],
        [
            InlineKeyboardButton(text="⭐ 1000 Stars — 1350 ₽", callback_data="buy_1000"),
            InlineKeyboardButton(text="⭐ 5000 Stars — 6500 ₽", callback_data="buy_5000"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"),
        ]
    ])
    await callback.message.edit_text("Выбери нужный пакет Stars:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def process_purchase(callback: types.CallbackQuery):
    product_code = callback.data.split("_")[1]
    stars_amount = int(product_code)
    prices = {100: 150, 500: 700, 1000: 1350, 5000: 6500}
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
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())