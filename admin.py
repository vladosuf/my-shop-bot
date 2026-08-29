from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message
import os

router = Router()

# Твой Telegram ID (найди через @userinfobot)
ADMIN_IDS = [1238597483]  # Замени на свой ID!


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
    # Здесь можно добавить реальную статистику из базы данных
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
    text = (
        "👥 *Управление пользователями*\n\n"
        "Здесь будет список пользователей.\n"
        "Пока что база данных не подключена."
    )
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_mailing")
async def admin_mailing(callback: types.CallbackQuery):
    """Рассылка"""
    text = (
        "📨 *Рассылка*\n\n"
        "Для отправки рассылки напиши сообщение\n"
        "в ответ на это сообщение.\n\n"
        "Напиши /cancel чтобы отменить."
    )
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_settings")
async def admin_settings(callback: types.CallbackQuery):
    """Настройки"""
    text = (
        "⚙️ *Настройки*\n\n"
        "Пока что настройки не добавлены."
    )
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_info")
async def admin_info(callback: types.CallbackQuery):
    """Информация о боте"""
    text = (
        "ℹ️ *О боте*\n\n"
        "Бот для продажи Telegram Stars\n"
        "Версия: 1.0.0\n"
        "Автор: Ты 🚀\n\n"
        "Бот работает на сервере 24/7"
    )
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()


# Функция для обработки рассылки
@router.message(lambda msg: msg.text and not msg.text.startswith("/"))
async def handle_mailing(message: Message):
    """Обработчик сообщений для рассылки"""
    if message.reply_to_message and "Рассылка" in message.reply_to_message.text:
        # Тут будет логика рассылки
        await message.answer("⏳ Начинаю рассылку...")
        # Здесь можно добавить отправку всем пользователям
        await message.answer("✅ Рассылка завершена!")