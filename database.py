import sqlite3
import os

DB_PATH = "users.db"

def init_db():
    """Создаёт базу данных и таблицу пользователей"""
    print("🔧 ВХОД В init_db()!") 
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        print("✅ Таблица users создана/проверена")
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
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
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

def get_all_users_with_details():
    """Возвращает список всех пользователей с их данными"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, first_name, last_name, joined_at FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"❌ Ошибка при получении данных пользователей: {e}")
        return []