import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message
from database import get_all_users, get_user_count
from logger import logger

router = Router()

# Твой Telegram ID (найди через @userinfobot)
ADMIN_IDS = [486661245]  # Замени на свой ID!

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
    
    user_count = get_user_count()
    
    stats = (
        "📊 *Статистика*\n\n"
        f"👥 Всего пользователей: *{user_count}*\n"
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
    
    users = get_all_users()
    user_count = len(users)
    
    text = (
        "👥 *Управление пользователями*\n\n"
        f"👥 Всего пользователей: *{user_count}*\n"
        f"🆔 ID первых 10 пользователей:\n"
    )
    
    for i, user_id in enumerate(users[:10], 1):
        text += f"{i}. `{user_id}`\n"
    
    if user_count > 10:
        text += f"\n...и ещё {user_count - 10} пользователей"
    
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
    
    user_count = get_user_count()
    
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
                    text="📊 Статистика пользователей",
                    callback_data="mailing_stats"
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
        f"👥 Всего пользователей: *{user_count}*\n\n"
        "Чтобы начать рассылку, нажми кнопку ниже\n"
        "и отправь сообщение для рассылки."
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
        "Напиши текст, который будет отправлен всем пользователям.\n"
        "Это может быть текст, фото, видео или ссылка.\n\n"
        "⚠️ *Важно:* Отправь именно то сообщение,\n"
        "которое хочешь разослать.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    # Сохраняем состояние "ожидание сообщения для рассылки"
    mailing_data[callback.from_user.id] = {"waiting": True}
    await callback.answer()


@router.callback_query(lambda c: c.data == "mailing_stats")
async def mailing_stats(callback: types.CallbackQuery):
    """Статистика пользователей"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    users = get_all_users()
    user_count = len(users)
    
    text = (
        "📊 *Статистика пользователей*\n\n"
        f"👥 Всего пользователей: *{user_count}*\n"
        f"🆔 ID первых 10 пользователей:\n"
    )
    
    for i, user_id in enumerate(users[:10], 1):
        text += f"{i}. `{user_id}`\n"
    
    if user_count > 10:
        text += f"\n...и ещё {user_count - 10} пользователей"
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="admin_mailing"
                ),
            ]
        ]
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# ============================================
# ОБРАБОТЧИК РАССЫЛКИ
# ============================================
@router.message(lambda msg: msg.text and not msg.text.startswith("/") and msg.from_user.id in ADMIN_IDS)
async def handle_mailing_message(message: types.Message):
    """Обрабатывает сообщение для рассылки"""
    user_id = message.from_user.id
    
    # Проверяем, ожидает ли админ сообщение для рассылки
    if user_id not in mailing_data or not mailing_data[user_id].get("waiting"):
        return
    
    # Получаем всех пользователей
    users = get_all_users()
    
    if not users:
        await message.answer("❌ Нет пользователей для рассылки.")
        mailing_data.pop(user_id, None)
        return
    
    # Отправляем сообщение о начале
    await message.answer(f"⏳ Начинаю рассылку для {len(users)} пользователей...")
    
    success = 0
    failed = 0
    
    # Отправляем сообщение каждому пользователю
    for i, user_id in enumerate(users):
        try:
            # Используем message.bot вместо прямого импорта bot
            await message.bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"❌ Не удалось отправить пользователю {user_id}: {e}")
        
        # Задержка, чтобы не превысить лимиты Telegram
        if i % 10 == 0:
            await asyncio.sleep(0.5)
    
    # Отправляем отчёт админу
    await message.answer(
        f"✅ *Рассылка завершена!*\n\n"
        f"📤 Отправлено: *{success}*\n"
        f"❌ Не доставлено: *{failed}*\n"
        f"👥 Всего: *{len(users)}*",
        parse_mode="Markdown"
    )
    
    # Очищаем состояние ожидания
    mailing_data.pop(message.from_user.id, None)


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