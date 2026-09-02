import sqlite3
import os

DB_PATH = "users.db"

def init_db():
    """Создаёт базу данных и таблицы"""
    print("🔧 ВХОД В init_db()!")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица покупок Звёзд
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                stars_amount INTEGER,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица покупок Премиума
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS premium_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                duration TEXT,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица сообщений
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_text TEXT,
                message_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Таблицы созданы/проверены")
        return True
    except Exception as e:
        print(f"❌ Ошибка при инициализации БД: {e}")
        return False

def add_user(user_id, username=None, first_name=None, last_name=None):
    """Добавляет пользователя в базу данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, last_active)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, username, first_name, last_name))
        conn.commit()
        conn.close()
        print(f"✅ Пользователь {user_id} добавлен в БД")
        return True
    except Exception as e:
        print(f"❌ Ошибка при добавлении пользователя: {e}")
        return False

def update_user_activity(user_id):
    """Обновляет время последней активности пользователя"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET last_active = CURRENT_TIMESTAMP 
            WHERE user_id = ?
        """, (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка при обновлении активности: {e}")
        return False

def get_all_users():
    """Возвращает список всех user_id"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        print(f"❌ Ошибка при получении пользователей: {e}")
        return []

def get_user_count():
    """Возвращает количество пользователей"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"❌ Ошибка при подсчёте пользователей: {e}")
        return 0

def get_all_users_with_details():
    """Возвращает список всех пользователей с их данными и активностью"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, first_name, last_name, joined_at, last_active FROM users ORDER BY last_active DESC")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"❌ Ошибка при получении данных пользователей: {e}")
        return []

def get_inactive_users(days=30):
    """Возвращает пользователей, неактивных более N дней"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, last_active 
            FROM users 
            WHERE last_active < datetime('now', '-' || ? || ' days')
        """, (days,))
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"❌ Ошибка при получении неактивных пользователей: {e}")
        return []

def remove_user(user_id):
    """Удаляет пользователя из базы данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        print(f"🗑️ Пользователь {user_id} удалён из БД")
        return True
    except Exception as e:
        print(f"❌ Ошибка при удалении пользователя: {e}")
        return False

def add_purchase(user_id, stars_amount):
    """Добавляет запись о покупке Звёзд в базу данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO purchases (user_id, stars_amount)
            VALUES (?, ?)
        """, (user_id, stars_amount))
        conn.commit()
        conn.close()
        print(f"✅ Покупка: {user_id} купил {stars_amount} Звёзд")
        return True
    except Exception as e:
        print(f"❌ Ошибка при добавлении покупки: {e}")
        return False

def get_total_stars_sold():
    """Возвращает общее количество проданных Звёзд"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(stars_amount) FROM purchases")
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0
    except Exception as e:
        print(f"❌ Ошибка при подсчёте Звёзд: {e}")
        return 0

def get_today_stars_sold():
    """Возвращает количество Звёзд, проданных сегодня"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(stars_amount) FROM purchases 
            WHERE DATE(purchase_date) = DATE('now')
        """)
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0
    except Exception as e:
        print(f"❌ Ошибка при подсчёте Звёзд за сегодня: {e}")
        return 0

def get_today_purchases_count():
    """Возвращает количество покупок сегодня"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM purchases 
            WHERE DATE(purchase_date) = DATE('now')
        """)
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0
    except Exception as e:
        print(f"❌ Ошибка при подсчёте покупок за сегодня: {e}")
        return 0

def add_premium_purchase(user_id, duration):
    """Добавляет запись о покупке Премиума в базу данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO premium_purchases (user_id, duration)
            VALUES (?, ?)
        """, (user_id, duration))
        conn.commit()
        conn.close()
        print(f"✅ Покупка Премиума: {user_id} купил {duration} месяцев")
        return True
    except Exception as e:
        print(f"❌ Ошибка при добавлении покупки Премиума: {e}")
        return False

def get_total_premium_sold():
    """Возвращает общее количество проданных Премиумов"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM premium_purchases")
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0
    except Exception as e:
        print(f"❌ Ошибка при подсчёте Премиумов: {e}")
        return 0

def get_today_premium_sold():
    """Возвращает количество Премиумов, проданных сегодня"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM premium_purchases 
            WHERE DATE(purchase_date) = DATE('now')
        """)
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0
    except Exception as e:
        print(f"❌ Ошибка при подсчёте Премиумов за сегодня: {e}")
        return 0

def get_active_users_today():
    """Возвращает количество пользователей, активных сегодня"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM users 
            WHERE DATE(last_active) = DATE('now')
        """)
        count = cursor.fetchone()[0]
        conn.close()
        return count or 0
    except Exception as e:
        print(f"❌ Ошибка при подсчёте активных пользователей: {e}")
        return 0

def get_total_messages():
    """Возвращает общее количество сообщений, отправленных боту"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM messages")
        count = cursor.fetchone()[0]
        conn.close()
        return count or 0
    except Exception as e:
        print(f"❌ Ошибка при подсчёте сообщений: {e}")
        return 0

def add_message(user_id, text):
    """Добавляет сообщение в базу данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (user_id, message_text)
            VALUES (?, ?)
        """, (user_id, text[:500]))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка при добавлении сообщения: {e}")
        return False

def get_messages_by_user(limit=20):
    """Возвращает сообщения, сгруппированные по пользователям с username"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                m.user_id,
                u.username,
                u.first_name,
                GROUP_CONCAT(m.message_text, ' | ') as messages,
                COUNT(m.id) as count,
                MAX(m.message_date) as last_date
            FROM messages m
            LEFT JOIN users u ON m.user_id = u.user_id
            GROUP BY m.user_id
            ORDER BY last_date DESC 
            LIMIT ?
        """, (limit,))
        messages = cursor.fetchall()
        conn.close()
        return messages
    except Exception as e:
        print(f"❌ Ошибка при получении сообщений по пользователям: {e}")
        return []

def get_user_messages(user_id, limit=20):
    """Возвращает сообщения конкретного пользователя с правильным временем"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT message_text, 
                   datetime(message_date, '+7 hours') as local_time
            FROM messages 
            WHERE user_id = ?
            ORDER BY message_date DESC 
            LIMIT ?
        """, (user_id, limit))
        messages = cursor.fetchall()
        conn.close()
        return messages
    except Exception as e:
        print(f"❌ Ошибка при получении сообщений пользователя: {e}")
        return []

def clear_all_messages():
    """Удаляет все сообщения из базы данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages")
        conn.commit()
        conn.close()
        print("🗑️ Все сообщения удалены!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при удалении сообщений: {e}")
        return False

def reset_db():
    """Удаляет старую базу данных и создаёт новую"""
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print(f"🗑️ Старая база {DB_PATH} удалена!")
        init_db()
        print("✅ База данных пересоздана!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при пересоздании БД: {e}")
        return False

def add_action(user_id, action_text):
    """Сохраняет действие пользователя (нажатие на кнопку)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (user_id, message_text)
            VALUES (?, ?)
        """, (user_id, f"🔄 {action_text}"))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении действия: {e}")
        return False

def get_recent_messages_all(limit=20):
    """Возвращает последние 20 сообщений (включая действия)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                m.user_id,
                u.username,
                u.first_name,
                m.message_text,
                datetime(m.message_date, '+7 hours') as local_time
            FROM messages m
            LEFT JOIN users u ON m.user_id = u.user_id
            ORDER BY m.message_date DESC 
            LIMIT ?
        """, (limit,))
        messages = cursor.fetchall()
        conn.close()
        return messages
    except Exception as e:
        print(f"❌ Ошибка при получении последних сообщений: {e}")
        return []

def add_action(user_id, action_text):
    """Сохраняет действие пользователя (нажатие на кнопку)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (user_id, message_text)
            VALUES (?, ?)
        """, (user_id, f"🔄 {action_text}"))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении действия: {e}")
        return False

def init_db():
    """Создаёт базу данных и таблицы"""
    print("🔧 ВХОД В init_db()!")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица покупок Звёзд
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                stars_amount INTEGER,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица покупок Премиума
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS premium_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                duration TEXT,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица сообщений
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_text TEXT,
                message_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 👇 НОВАЯ ТАБЛИЦА ДЛЯ БЛОКИРОВКИ
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocked_users (
                user_id INTEGER PRIMARY KEY,
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Таблицы созданы/проверены")
        return True
    except Exception as e:
        print(f"❌ Ошибка при инициализации БД: {e}")
        return False

# ============================================
# ФУНКЦИИ ДЛЯ БЛОКИРОВКИ
# ============================================

def block_user(user_id, reason="Без причины"):
    """Блокирует пользователя"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO blocked_users (user_id, reason)
            VALUES (?, ?)
        """, (user_id, reason))
        conn.commit()
        conn.close()
        print(f"🔒 Пользователь {user_id} заблокирован! Причина: {reason}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при блокировке: {e}")
        return False

def unblock_user(user_id):
    """Разблокирует пользователя"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blocked_users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        print(f"🔓 Пользователь {user_id} разблокирован!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при разблокировке: {e}")
        return False

def is_user_blocked(user_id):
    """Проверяет, заблокирован ли пользователь"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT reason FROM blocked_users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return True, result[0]
        return False, None
    except Exception as e:
        print(f"❌ Ошибка при проверке блокировки: {e}")
        return False, None

def get_blocked_users():
    """Возвращает список заблокированных пользователей"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.user_id, u.username, u.first_name, b.reason, b.blocked_at
            FROM blocked_users b
            LEFT JOIN users u ON b.user_id = u.user_id
            ORDER BY b.blocked_at DESC
        """)
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"❌ Ошибка при получении заблокированных пользователей: {e}")
        return []
