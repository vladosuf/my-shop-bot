import sqlite3
import os

DB_PATH = "users.db"

def init_db():
    """Создаёт базу данных и таблицы пользователей и покупок"""
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
        
        # Таблица покупок
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                stars_amount INTEGER,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Таблицы users и purchases созданы/проверены")
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

def add_purchase(user_id, stars_amount):
    """Добавляет запись о покупке в базу данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Создаём таблицу покупок, если её нет
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                stars_amount INTEGER,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
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