import asyncio
import sqlite3
from datetime import datetime, timedelta
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
    get_messages_by_user,
    clear_all_messages,
    get_user_messages,
    DB_PATH
)
from logger import logger
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
    get_messages_by_user,
    clear_all_messages,
    get_user_messages,
    DB_PATH,
    block_user,
    unblock_user,
    is_user_blocked,
    get_blocked_users
)

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

    update_user_activity(message.from_user.id)

    # Этот блок начинается с 4 пробелов
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
                types.InlineKeyboardButton(text="🔒 Блокировка", callback_data="admin_block"),
            ],
            [
                types.InlineKeyboardButton(text="ℹ️ О боте", callback_data="admin_info"),
            ]
        ]
    )

    # Это сообщение тоже на 4 пробела
    await message.answer(
        "🛡️ *Админ-панель*\n\n"
        "Выбери действие:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    """Статистика"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    try:
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
    except Exception as e:
        await callback.message.edit_text(
            f"❌ *Ошибка при загрузке статистики*\n\n"
            f"```{str(e)}```",
            parse_mode="Markdown"
        )
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    """Пользователи"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    try:
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
    except Exception as e:
        await callback.message.edit_text(
            f"❌ *Ошибка при загрузке пользователей*\n\n"
            f"```{str(e)}```",
            parse_mode="Markdown"
        )
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_cleanup")
async def admin_cleanup(callback: types.CallbackQuery):
    """Удаляет неактивных пользователей"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    try:
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
    except Exception as e:
        await callback.message.edit_text(
            f"❌ *Ошибка при удалении*\n\n```{str(e)}```",
            parse_mode="Markdown"
        )
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_mailing")
async def admin_mailing(callback: types.CallbackQuery):
    """Рассылка"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    try:
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
    except Exception as e:
        await callback.message.edit_text(
            f"❌ *Ошибка*\n\n```{str(e)}```",
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
            types.InlineKeyboardButton(text="🔒 Блокировка", callback_data="admin_block"),
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
# СООБЩЕНИЯ
# ============================================
@router.callback_query(lambda c: c.data == "admin_messages")
async def admin_messages(callback: types.CallbackQuery):
    """Показывает сообщения, сгруппированные по пользователям"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    try:
        messages = get_messages_by_user(15)
        
        if not messages:
            await callback.message.edit_text(
                "📨 *Нет сообщений.*\n\n"
                "Сообщения начнут появляться, когда пользователи напишут боту.",
                parse_mode="Markdown"
            )
            await callback.answer()
            return
        
        total_messages = get_total_messages()
        
        text = f"📨 *Сообщения по пользователям*\n\n"
        text += f"📊 Всего сообщений: *{total_messages}*\n"
        text += f"👥 Пользователей: *{len(messages)}*\n\n"
        text += "┌─────────────────┬──────────┬────────────┐\n"
        text += "│ 👤 Пользователь │ 📝 Всего │ 🕐 Последнее│\n"
        text += "├─────────────────┼──────────┼────────────┤\n"
        
        for user_id, username, first_name, messages_text, count, last_date in messages:
            if username:
                display_name = f"@{username}"
            elif first_name:
                display_name = first_name[:15]
            else:
                display_name = str(user_id)
            
            if last_date:
                try:
                    dt = datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
                    dt_nsk = dt + timedelta(hours=7)
                    last_date_formatted = dt_nsk.strftime("%d.%m %H:%M")
                except:
                    last_date_formatted = last_date[:16] if last_date else "Неизвестно"
            else:
                last_date_formatted = "Неизвестно"
            
            if len(display_name) > 15:
                display_name = display_name[:13] + "…"
            
            text += f"│ {display_name:^15} │ {count:^8} │ {last_date_formatted:^10} │\n"
        
        text += "└─────────────────┴──────────┴────────────┘\n\n"
        text += "📌 Нажми на пользователя, чтобы увидеть его сообщения"
        
        keyboard_buttons = []
        for user_id, username, first_name, messages_text, count, last_date in messages[:10]:
            if username:
                button_text = f"👤 @{username} ({count})"
            elif first_name:
                button_text = f"👤 {first_name[:15]} ({count})"
            else:
                button_text = f"👤 {user_id} ({count})"
            
            keyboard_buttons.append([
                types.InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"msg_user_{user_id}"
                )
            ])
        
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text="🗑️ Очистить все сообщения",
                callback_data="admin_clear_messages"
            ),
        ])
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="admin_panel"
            ),
        ])
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        await callback.message.edit_text(
            f"❌ *Ошибка при загрузке сообщений*\n\n```{str(e)}```",
            parse_mode="Markdown"
        )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("msg_user_"))
async def admin_messages_user(callback: types.CallbackQuery):
    """Показывает сообщения конкретного пользователя"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[2])
    
    try:
        # Получаем данные пользователя
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, first_name 
            FROM users 
            WHERE user_id = ?
        """, (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            username, first_name = user_data
            if username:
                display_name = f"@{username}"
            elif first_name:
                display_name = first_name
            else:
                display_name = str(user_id)
        else:
            display_name = str(user_id)
        
        messages = get_user_messages(user_id, 20)
        
        if not messages:
            await callback.answer("❌ Нет сообщений от этого пользователя", show_alert=True)
            return
        
        text = f"👤 *Сообщения пользователя {display_name}*\n\n"
        
        for msg_text, msg_date in messages[:15]:
            if len(msg_text) > 50:
                msg_text = msg_text[:50] + "..."
            date_formatted = msg_date[:16] if msg_date else "Неизвестно"
            text += f"📝 {msg_text}\n"
            text += f"🕐 {date_formatted}\n\n"
        
        if len(messages) > 15:
            text += f"...и ещё {len(messages) - 15} сообщений"
        
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="🔙 Назад к списку",
                        callback_data="admin_messages"
                    ),
                ]
            ]
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        await callback.message.edit_text(
            f"❌ *Ошибка при загрузке сообщений*\n\n```{str(e)}```",
            parse_mode="Markdown"
        )
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_clear_messages")
async def admin_clear_messages(callback: types.CallbackQuery):
    """Очищает все сообщения"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="✅ Да, удалить всё",
                    callback_data="admin_clear_confirm"
                ),
                types.InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="admin_messages"
                ),
            ]
        ]
    )
    
    await callback.message.edit_text(
        "⚠️ *Подтверждение*\n\n"
        "Ты уверен, что хочешь удалить ВСЕ сообщения?\n"
        "Это действие нельзя отменить!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_clear_confirm")
async def admin_clear_confirm(callback: types.CallbackQuery):
    """Подтверждение очистки сообщений"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    try:
        if clear_all_messages():
            await callback.message.edit_text(
                "✅ *Все сообщения удалены!*\n\n"
                "База сообщений очищена.",
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                "❌ *Ошибка при удалении сообщений.*",
                parse_mode="Markdown"
            )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ *Ошибка*\n\n```{str(e)}```",
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
    
    if user_id not in mailing_data or not mailing_data[user_id].get("waiting"):
        return
    
    try:
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
    except Exception as e:
        await message.answer(
            f"❌ *Ошибка при рассылке*\n\n```{str(e)}```",
            parse_mode="Markdown"
        )
    finally:
        mailing_data.pop(message.from_user.id, None)


@router.callback_query(lambda c: c.data == "admin_block")
async def admin_block(callback: types.CallbackQuery):
    """Управление блокировками"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    blocked_users = get_blocked_users()
    
    text = "🔒 *Управление блокировками*\n\n"
    
    if blocked_users:
        text += "👥 *Заблокированные пользователи:*\n\n"
        for user_id, username, first_name, reason, blocked_at in blocked_users[:10]:
            name = first_name or "Без имени"
            username_str = f"@{username}" if username else "Нет username"
            text += f"• {name} ({username_str})\n"
            text += f"  🆔 `{user_id}`\n"
            text += f"  📝 Причина: {reason}\n"
            text += f"  🕐 {blocked_at[:16]}\n\n"
        if len(blocked_users) > 10:
            text += f"...и ещё {len(blocked_users) - 10} заблокированных"
    else:
        text += "✅ Нет заблокированных пользователей."
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔒 Заблокировать пользователя",
                    callback_data="admin_block_user"
                ),
                types.InlineKeyboardButton(
                    text="🔓 Разблокировать",
                    callback_data="admin_unblock_user"
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


@router.callback_query(lambda c: c.data == "admin_block_user")
async def admin_block_user(callback: types.CallbackQuery):
    """Блокировка пользователя"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔙 Отмена",
                    callback_data="admin_block"
                ),
            ]
        ]
    )
    
    await callback.message.edit_text(
        "🔒 *Блокировка пользователя*\n\n"
        "Напиши в чат ID пользователя и причину блокировки.\n\n"
        "Формат: `ID Причина`\n"
        "Пример: `123456789 Спам`\n\n"
        "Для отмены нажми кнопку ниже.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(lambda msg: msg.text and msg.from_user.id in ADMIN_IDS)
async def handle_block_command(message: types.Message):
    """Обработка команды блокировки"""
    # Проверяем, что это не команда
    if message.text.startswith("/"):
        return
    
    # Проверяем, что мы в режиме блокировки (можно упростить)
    if "Заблокировать пользователя" not in message.text and message.text.count(" ") == 1:
        # Пытаемся распарсить ID и причину
        parts = message.text.split(" ", 1)
        if len(parts) == 2 and parts[0].isdigit():
            user_id = int(parts[0])
            reason = parts[1]
            
            if block_user(user_id, reason):
                await message.answer(f"✅ Пользователь `{user_id}` заблокирован!\nПричина: {reason}", parse_mode="Markdown")
            else:
                await message.answer("❌ Ошибка при блокировке пользователя.")
            return


@router.callback_query(lambda c: c.data == "admin_unblock_user")
async def admin_unblock_user(callback: types.CallbackQuery):
    """Разблокировка пользователя"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    blocked_users = get_blocked_users()
    
    if not blocked_users:
        await callback.message.edit_text(
            "✅ Нет заблокированных пользователей.",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    keyboard_buttons = []
    for user_id, username, first_name, reason, blocked_at in blocked_users[:10]:
        name = first_name or "Без имени"
        keyboard_buttons.append([
            types.InlineKeyboardButton(
                text=f"🔓 Разблокировать {name}",
                callback_data=f"admin_unblock_{user_id}"
            )
        ])
    
    keyboard_buttons.append([
        types.InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="admin_block"
        )
    ])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(
        "🔓 *Выбери пользователя для разблокировки:*",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_unblock_"))
async def admin_unblock_confirm(callback: types.CallbackQuery):
    """Подтверждение разблокировки"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Доступ запрещён!", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[2])
    
    if unblock_user(user_id):
        await callback.message.edit_text(
            f"✅ Пользователь `{user_id}` разблокирован!",
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            f"❌ Ошибка при разблокировке пользователя `{user_id}`.",
            parse_mode="Markdown"
        )
    await callback.answer()