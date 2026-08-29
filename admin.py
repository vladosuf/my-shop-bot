from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message

# Создаём роутер для админских команд
router = Router()

# ⚠️ ВАЖНО: Замените этот ID на свой!
# Как узнать свой ID: напишите @userinfobot в Telegram
ADMIN_IDS = [1238597483]  # <-- ВСТАВЬТЕ СВОЙ ID СЮДА!


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Показывает админ-панель"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="📊 Статистика", callback_data="admin_stats"
                ),
                types.InlineKeyboardButton(
                    text="👥 Пользователи", callback_data="admin_users"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="📨 Рассылка", callback_data="admin_mailing"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="ℹ️ О боте", callback_data="admin_info"
                ),
            ]
        ]
    )

    await message.answer(
        "🛡️ *Админ-панель*\n\nВыберите действие:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    """Статистика"""
    stats = (
        "📊 *Статистика*\n\n"
        "👥 Всего пользователей: 0\n"
        "🟢 Активных сегодня: 0\n"
        "⭐ Всего покупок: 0"
    )
    await callback.message.edit_text(stats, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    """Управление пользователями"""
    text = "👥 *Управление пользователями*\n\nЗдесь будет список пользователей."
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_mailing")
async def admin_mailing(callback: types.CallbackQuery):
    """Рассылка"""
    text = (
        "📨 *Рассылка*\n\n"
        "Напишите сообщение для рассылки.\n"
        "Для отмены напишите /cancel"
    )
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_info")
async def admin_info(callback: types.CallbackQuery):
    """Информация"""
    text = (
        "ℹ️ *О боте*\n\n"
        "🤖 Бот для продажи Telegram Stars\n"
        "🚀 Версия: 1.0.0"
    )
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()