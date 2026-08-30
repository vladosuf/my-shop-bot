import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message
from logger import logger

router = Router()

# Твой Telegram ID (найди через @userinfobot)
ADMIN_IDS = [1238597483]  # Замени на свой ID!

# Временное хранилище для сообщений рассылки
mailing_data = {}


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Админ-панель"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У тебя нет доступа к этой команде!")
        return
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
                types.InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            ],
            [
                types.InlineKeyboardButton(text="📨 Рассылка", callback_data="admin_mailing"),
                types.InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings"),
            ],
            [
                types.InlineKeyboardButton(text="ℹ️ О боте", callback_data="admin_info"),
            ]
        ]
    )
    
    await message.answer(
        "🛡️ *Админ-панель*\n\n"
        "Выбери действие:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    """Показывает статистику"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    stats = (
        "📊 *Статистика*\n\n"
        "👥 Всего пользователей: 0\n"
        "🟢 Активных сегодня: 0\n"
        "📨 Отправлено сообщений: 0\n"
        "⭐ Всего покупок: 0"
    )
    await callback.message.edit_text(stats, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    """Управление пользователями"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    text = (
        "👥 *Управление пользователями*\n\n"
        "👥 Всего пользователей: 0\n"
        "База данных не подключена."
    )
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="admin_panel"
                ),
            ]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_mailing")
async def admin_mailing(callback: types.CallbackQuery):
    """Запуск рассылки"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="📤 Начать рассылку",
                    callback_data="mailing_start"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="admin_panel"
                ),
            ]
        ]
    )
    
    text = (
        "📨 *Рассылка*\n\n"
        "👥 Всего пользователей: 0\n\n"
        "Чтобы начать рассылку, нажми кнопку ниже\n"
        "и отправь сообщение для рассылки.\n\n"
        "⚠️ *Важно:* База данных не подключена.\n"
        "Рассылка работает только для тестов."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "mailing_start")
async def mailing_start(callback: types.CallbackQuery):
    """Начало рассылки"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔙 Отмена",
                    callback_data="admin_mailing"
                ),
            ]
        ]
    )
    
    await callback.message.edit_text(
        "📨 *Отправь сообщение для рассылки*\n\n"
        "Напиши текст, который будет отправлен всем пользователям.\n\n"
        "⚠️ *Важно:* База данных не подключена.\n"
        "Сообщение отправится только тебе.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    mailing_data[callback.from_user.id] = {"waiting": True}
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_settings")
async def admin_settings(callback: types.CallbackQuery):
    """Настройки"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    text = (
        "⚙️ *Настройки*\n\n"
        "Пока что настройки не добавлены."
    )
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="admin_panel"
                ),
            ]
        ]
    )
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_panel")
async def admin_panel_back(callback: types.CallbackQuery):
    """Возврат в админ-панель"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
                types.InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            ],
            [
                types.InlineKeyboardButton(text="📨 Рассылка", callback_data="admin_mailing"),
                types.InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings"),
            ],
            [
                types.InlineKeyboardButton(text="ℹ️ О боте", callback_data="admin_info"),
            ]
        ]
    )
    
    await callback.message.edit_text(
        "🛡️ *Админ-панель*\n\n"
        "Выбери действие:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_info")
async def admin_info(callback: types.CallbackQuery):
    """Информация о боте"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    text = (
        "ℹ️ *О боте*\n\n"
        "Бот для продажи Telegram Stars\n"
        "Версия: 2.0.0\n"
        "Автор: Ты 🚀\n\n"
        "Бот работает на сервере 24/7"
    )
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="admin_panel"
                ),
            ]
        ]
    )
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


# Обработчик сообщений для рассылки (тестовый)
@router.message(lambda msg: msg.text and not msg.text.startswith("/") and msg.from_user.id in ADMIN_IDS)
async def handle_mailing_message(message: types.Message):
    """Обрабатывает сообщение для рассылки (тестовый режим)"""
    user_id = message.from_user.id
    
    if user_id not in mailing_data or not mailing_data[user_id].get("waiting"):
        return
    
    await message.answer("⏳ Начинаю тестовую рассылку...")
    await asyncio.sleep(1)
    await message.answer(
        "✅ *Тестовая рассылка завершена!*\n\n"
        "📤 Отправлено: 1\n"
        "❌ Не доставлено: 0\n"
        "👥 Всего: 1\n\n"
        "⚠️ *База данных не подключена.*\n"
        "Сообщение отправлено только тебе.",
        parse_mode="Markdown"
    )
    
    mailing_data.pop(user_id, None)