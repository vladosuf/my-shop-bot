import asyncio
from datetime import datetime
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message
from database import (
    get_all_users, 
    get_user_count, 
    get_all_users_with_details, 
    remove_user, 
    get_inactive_users, 
    update_user_activity,
    get_total_stars_sold,
    get_today_stars_sold,
    get_today_purchases_count,
    get_total_premium_sold,
    get_today_premium_sold,
    get_active_users_today,
    get_total_messages,
    get_recent_messages
)
from logger import logger

router = Router()

# ТВОЙ TELEGRAM ID (замени на свой!)
ADMIN_IDS = [1238597483]  # ← ВСТАВЬ СВОЙ ID СЮДА!

# Временное хранилище для рассылки
mailing_data = {}


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Админ-панель"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У тебя нет доступа к этой команде!")
        return
    
    # Обновляем активность админа
    update_user_activity(message.from_user.id)
    
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
                types.InlineKeyboardButton(text="📨 Сообщения", callback_data="admin_messages"),
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
    """Статистика с информацией о продажах"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    user_count = get_user_count()
    active_today = get_active_users_today()
    total_messages = get_total_messages()
    total_stars = get_total_stars_sold()
    today_stars = get_today_stars_sold()
    today_purchases = get_today_purchases_count()
    total_premium = get_total_premium_sold()
    today_premium = get_today_premium_sold()
    
    await callback.message.edit_text(
        f"📊 *Статистика*\n\n"
        f"👥 Всего пользователей: *{user_count}*\n"
        f"🟢 Активных сегодня: *{active_today}*\n"
        f"📨 Отправлено сообщений: *{total_messages}*\n\n"
        f"⭐ *Продажи Звёзд*\n"
        f"📦 Всего продано: *{total_stars}*\n"
        f"📈 За сегодня: *{today_stars}*\n"
        f"🛒 Покупок сегодня: *{today_purchases}*\n\n"
        f"🌠 *Продажи Премиума*\n"
        f"📦 Всего продано: *{total_premium}*\n"
        f"📈 За сегодня: *{today_premium}*",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    """Пользователи с подробной информацией и активностью"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    users = get_all_users_with_details()
    user_count = len(users)
    
    text = f"👥 *Пользователи*\n\n👥 Всего: *{user_count}*\n\n"
    
    if user_count == 0:
        text += "Пока нет пользователей."
    else:
        for i, user in enumerate(users[:20], 1):
            user_id, username, first_name, last_name, joined_at, last_active = user
            
            name = first_name or "Без имени"
            username_str = f"@{username}" if username else "❌ Нет username"
            
            if last_active:
                days = (datetime.now() - datetime.strptime(last_active, "%Y-%m-%d %H:%M:%S")).days
                if days == 0:
                    status = "🟢 Сегодня"
                elif days == 1:
                    status = "🟡 Вчера"
                elif days < 7:
                    status = f"🟠 {days} дня назад"
                else:
                    status = f"🔴 {days} дней назад"
            else:
                status = "⚪ Неизвестно"
            
            text += f"{i}. *{name}*\n"
            text += f"   🆔 `{user_id}`\n"
            text += f"   📛 {username_str}\n"
            text += f"   ⏱ {status}\n\n"
        
        if user_count > 20:
            text += f"...и ещё {user_count - 20} пользователей"
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🗑️ Удалить неактивных (30+ дней)",
                    callback_data="admin_cleanup"
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
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_cleanup")
async def admin_cleanup(callback: types.CallbackQuery):
    """Удаляет неактивных пользователей"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    inactive_users = get_inactive_users(30)
    
    if not inactive_users:
        await callback.message.edit_text(
            "✅ Нет неактивных пользователей для удаления.",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    removed = 0
    for user_id, last_active in inactive_users:
        if remove_user(user_id):
            removed += 1
    
    await callback.message.edit_text(
        f"🗑️ Удалено *{removed}* неактивных пользователей (активность более 30 дней).",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_mailing")
async def admin_mailing(callback: types.CallbackQuery):
    """Рассылка"""
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
                    text="🔙 Назад",
                    callback_data="admin_panel"
                ),
            ]
        ]
    )
    
    await callback.message.edit_text(
        f"📨 *Рассылка*\n\n"
        f"👥 Всего пользователей: *{user_count}*\n\n"
        "Чтобы начать рассылку, нажми кнопку ниже.",
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
        "Напиши текст, который будет отправлен всем пользователям.",
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
    
    await callback.message.edit_text(
        "⚙️ *Настройки*\n\n"
        "Пока что настройки не добавлены.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
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
                types.InlineKeyboardButton(text="📨 Сообщения", callback_data="admin_messages"),
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
    
    await callback.message.edit_text(
        "ℹ️ *О боте*\n\n"
        "Бот для продажи Telegram Stars\n"
        "Версия: 2.0.0\n"
        "Автор: Ты 🚀\n\n"
        "Бот работает на сервере 24/7",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# ============================================
# ПРОСМОТР СООБЩЕНИЙ
# ============================================
@router.callback_query(lambda c: c.data == "admin_messages")
async def admin_messages(callback: types.CallbackQuery):
    """Показывает последние сообщения"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    messages = get_recent_messages(20)
    
    if not messages:
        await callback.message.edit_text(
            "📨 *Нет сообщений.*\n\n"
            "Сообщения начнут появляться, когда пользователи напишут боту.",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    text = "📨 *Последние сообщения*\n\n"
    for msg in messages:
        user_id, text_msg, date = msg
        # Обрезаем длинные сообщения
        if len(text_msg) > 80:
            text_msg = text_msg[:80] + "..."
        text += f"👤 `{user_id}`\n"
        text += f"📝 {text_msg}\n"
        text += f"🕐 {date}\n\n"
    
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


# ============================================
# ОБРАБОТЧИК РАССЫЛКИ
# ============================================
@router.message(lambda msg: msg.text and not msg.text.startswith("/") and msg.from_user.id in ADMIN_IDS)
async def handle_mailing_message(message: types.Message):
    """Обрабатывает сообщение для рассылки"""
    user_id = message.from_user.id
    
    if user_id not in mailing_data or not mailing_data[user_id].get("waiting"):
        return
    
    users = get_all_users()
    
    if not users:
        await message.answer("❌ Нет пользователей для рассылки.")
        mailing_data.pop(user_id, None)
        return
    
    await message.answer(f"⏳ Начинаю рассылку для {len(users)} пользователей...")
    
    success = 0
    failed = 0
    
    for i, user_id in enumerate(users):
        try:
            await message.bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"❌ Не удалось отправить пользователю {user_id}: {e}")
        
        if i % 10 == 0:
            await asyncio.sleep(0.5)
    
    await message.answer(
        f"✅ *Рассылка завершена!*\n\n"
        f"📤 Отправлено: *{success}*\n"
        f"❌ Не доставлено: *{failed}*\n"
        f"👥 Всего: *{len(users)}*",
        parse_mode="Markdown"
    )
    
    mailing_data.pop(message.from_user.id, None)