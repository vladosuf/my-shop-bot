import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery, BotCommand
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


# ============================================
# НАСТРОЙКА КНОПКИ МЕНЮ
# ============================================
async def set_main_menu():
    """Устанавливает кнопку Меню рядом со строкой поиска"""
    menu_commands = [
        BotCommand(command="start", description="🚀 Главное меню"),
        BotCommand(command="help", description="ℹ️ Помощь"),
        BotCommand(command="menu", description="📋 Обновить меню"),
    ]
    await bot.set_my_commands(menu_commands)


@dp.message(Command("start"))
async def start_command(message: Message):
    logger.info(f"👤 Пользователь {message.from_user.id} запустил бота")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Купить Звёзды", callback_data="buy_stars"),
        ],
        [
            InlineKeyboardButton(text="🎁 Подарить другу", callback_data="gift_friend"),
        ],
        [
            InlineKeyboardButton(text="🆘 Поддержка", callback_data="support"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="info"),
        ]
    ])
    
    await message.answer(
        "🚀 Привет!\n\n"
        "С помощью этого бота можно купить ⭐Telegram Звёзды.\n"
        "Выбери действие ниже:",
        reply_markup=keyboard
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    """Команда помощи - открывает главное меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Купить Звёзды", callback_data="buy_stars"),
        ],
        [
            InlineKeyboardButton(text="🎁 Подарить другу", callback_data="gift_friend"),
        ],
        [
            InlineKeyboardButton(text="🆘 Поддержка", callback_data="support"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="info"),
        ]
    ])
    
    await message.answer(
        "🚀 *Главное меню*\n\n"
        "Покупай ⭐Telegram Звёзды и дари их друзьям!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.message(Command("menu"))
async def menu_command(message: Message):
    """Принудительная установка кнопки Меню"""
    menu_commands = [
        BotCommand(command="start", description="🚀 Главное меню"),
        BotCommand(command="help", description="ℹ️ Помощь"),
        BotCommand(command="menu", description="📋 Обновить меню"),
    ]
    await bot.set_my_commands(menu_commands)
    await message.answer("✅ Кнопка Меню обновлена! Перезапусти Telegram, чтобы увидеть изменения.")


# ============================================
# КНОПКА: КУПИТЬ ЗВЁЗДЫ
# ============================================
@dp.callback_query(F.data == "buy_stars")
async def show_products(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐ 50 — 65 ₽", callback_data="buy_50"),
            InlineKeyboardButton(text="⭐ 100 — 130 ₽", callback_data="buy_100"),
        ],
        [
            InlineKeyboardButton(text="⭐ 150 — 195 ₽", callback_data="buy_150"),
            InlineKeyboardButton(text="⭐ 200 — 260 ₽", callback_data="buy_200"),
        ],
        [
            InlineKeyboardButton(text="⭐ 250 — 325 ₽", callback_data="buy_250"),
            InlineKeyboardButton(text="⭐ 500 — 650 ₽", callback_data="buy_500"),
        ],
        [
            InlineKeyboardButton(text="⭐ 750 — 975 ₽", callback_data="buy_750"),
            InlineKeyboardButton(text="⭐ 1000 — 1300 ₽", callback_data="buy_1000"),
        ],
        [
            InlineKeyboardButton(text="⭐ 1750 — 2275 ₽", callback_data="buy_1750"),
            InlineKeyboardButton(text="⭐ 2500 — 3250 ₽", callback_data="buy_2500"),
        ],
        [
            InlineKeyboardButton(text="⭐ 5000 — 6500 ₽", callback_data="buy_5000"),
            InlineKeyboardButton(text="📝 Своё число", callback_data="custom_amount"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"),
        ],
    ])
    
    await callback.message.edit_text(
        "🚀 Выбери пакет Звёзд:\n\n"
        "⭐ Нажми на готовый пакет или выбери Своё число\n"
        "📌 Курс: 1 Звезда = 1.3 ₽",
        reply_markup=keyboard
    )
    await callback.answer()


# ============================================
# КНОПКА: ПОДАРИТЬ ДРУГУ
# ============================================
@dp.callback_query(F.data == "gift_friend")
async def gift_friend(callback: types.CallbackQuery):
    """Подарить другу"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"),
        ]
    ])
    
    await callback.message.edit_text(
        "🎁 *Подарок другу*\n\n"
        "Чтобы подарить Звёзды другу:\n"
        "1. Выбери пакет Звёзд\n"
        "2. Укажи username друга\n"
        "3. Оплати\n\n"
        "⭐ Звёзды будут зачислены на счёт друга!\n\n"
        "🚀 *Скоро появится!*",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# ============================================
# КНОПКА: ПОДДЕРЖКА
# ============================================
@dp.callback_query(F.data == "support")
async def support(callback: types.CallbackQuery):
    """Поддержка"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"),
        ]
    ])
    
    await callback.message.edit_text(
        "🆘 *Поддержка*\n\n"
        "Если у тебя возникли вопросы или проблемы:\n\n"
        "📧 Свяжись с нами:\n"
        "👤 @vladosuf\n\n"
        "📌 Мы ответим в ближайшее время!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# ============================================
# РУЧНОЙ ВВОД КОЛИЧЕСТВА
# ============================================
@dp.callback_query(F.data == "custom_amount")
async def custom_amount_input(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад к пакетам", callback_data="buy_stars"),
        ]
    ])
    
    await callback.message.edit_text(
        "📝 Введи нужное количество Звёзд:\n\n"
        "Например: 100 или 2500\n\n"
        "💰 Цена: твоё_число × 1.3 ₽\n\n"
        "Просто напиши число в чат!",
        reply_markup=keyboard
    )
    await callback.answer()


@dp.message(lambda msg: msg.text and msg.text.isdigit())
async def handle_custom_amount(message: Message):
    stars_amount = int(message.text)
    
    if stars_amount < 1:
        await message.answer("❌ Минимум — 1 Звезда. Попробуй ещё раз.")
        return
    
    if stars_amount > 10000:
        await message.answer("❌ Максимум — 10000 Звёзд за раз. Попробуй ещё раз.")
        return
    
    price = stars_amount * 1.3
    price_rub = int(price)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"✅ Купить {stars_amount} Звёзд за {price_rub} ₽",
                callback_data=f"buy_{stars_amount}"
            ),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад к пакетам", callback_data="buy_stars"),
        ]
    ])
    
    await message.answer(
        f"📝 Ты выбрал {stars_amount} Звёзд\n\n"
        f"💰 Стоимость: {price_rub} ₽\n"
        f"📌 Курс: 1 Звезда = 1.3 ₽\n\n"
        f"👇 Нажми кнопку, чтобы подтвердить покупку:",
        reply_markup=keyboard
    )


# ============================================
# ОФОРМЛЕНИЕ ЗАКАЗА И ОПЛАТА
# ============================================
@dp.callback_query(F.data.startswith("buy_"))
async def process_purchase(callback: types.CallbackQuery):
    product_code = callback.data.split("_")[1]
    stars_amount = int(product_code)
    
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
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
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


# ============================================
# НАЗАД В МЕНЮ
# ============================================
@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Купить Звёзды", callback_data="buy_stars"),
        ],
        [
            InlineKeyboardButton(text="🎁 Подарить другу", callback_data="gift_friend"),
        ],
        [
            InlineKeyboardButton(text="🆘 Поддержка", callback_data="support"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="info"),
        ]
    ])
    
    await callback.message.edit_text(
        "🚀 Главное меню:\n\n"
        "Покупай ⭐Telegram Звёзды и дари их друзьям!",
        reply_markup=keyboard
    )
    await callback.answer()


# ============================================
# КНОПКА: О БОТЕ
# ============================================
@dp.callback_query(F.data == "info")
async def show_info(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ О боте\n\n"
        "Этот бот помогает покупать Telegram Звёзды.\n"
        "Звёзды — это валюта Telegram для поддержки авторов.\n\n"
        "💰 Как это работает:\n"
        "1. Выбери нужный пакет\n"
        "2. Оплати внутри Telegram\n"
        "3. Получи Звёзды на свой аккаунт\n\n"
        "🚀 Курс: 1 Звезда = 1.3 ₽\n\n"
        "❓ Вопросы? Пиши @vladosuf"
    )
    await callback.answer()


# ============================================
# ЗАПУСК БОТА
# ============================================
async def main():
    try:
        await set_main_menu()
        logger.info("✅ Кнопка Меню установлена!")
        logger.info("🚀 Бот запущен и готов к работе!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())