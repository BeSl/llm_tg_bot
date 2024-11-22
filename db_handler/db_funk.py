import json
import aiosqlite
from sqlalchemy import BigInteger, Integer, String, TIMESTAMP, JSON, Boolean
from decouple import config

# Путь к базе данных SQLite
db_path = config('DB_PATH')
# Функция для создания таблицы пользователей
async def create_table_users():
    async with aiosqlite.connect(db_path) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            full_name TEXT,
            user_login TEXT,
            in_dialog BOOLEAN,
            date_reg TIMESTAMP
        )
        ''')
        await db.commit()


async def create_table_dialog_history():
    async with aiosqlite.connect(db_path) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS dialog_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id BIGINT,
            message TEXT,
            data_message TEXT
        )
        ''')
        await db.commit()

async def create_table_dialog_mode():
    async with aiosqlite.connect(db_path) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS dialog_mode (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id BIGINT,
            mode TEXT
        )
        ''')
        await db.commit()

# Функция для получения информации по конкретному пользователю
async def get_user_data(user_id: int):
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user_data = await cursor.fetchone()
        if user_data:
            return dict(user_data)
        return None

# Функция для получения всех пользователей
async def get_all_users(count=False):
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute('SELECT * FROM users')
        all_users = await cursor.fetchall()
        if count:
            return len(all_users)
        else:
            return [dict(user) for user in all_users]


# Функция для добавления пользователя в базу данных
async def insert_user(user_data: dict):
    async with aiosqlite.connect(db_path) as db:
        await db.execute('''
        INSERT OR IGNORE INTO users (user_id, full_name, user_login, in_dialog, date_reg) 
        VALUES (?, ?, ?, ?, ?)
        ''', (user_data['user_id'], user_data['full_name'], user_data['user_login'], user_data['in_dialog'], user_data['date_reg']))
        await db.commit()


# Функция для получения истории диалога
async def get_dialog_history(user_id: int):
    dialog_history_msg = []
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute('SELECT message FROM dialog_history WHERE user_id = ?', (user_id,))
        dialog_history = await cursor.fetchall()
        for msg in dialog_history:
            # message = json.loads(msg[0])  # msg[0] - это текст сообщения
            message = json.loads(msg[0])
            dialog_history_msg.append(message)
    return dialog_history_msg


# Функция для добавления сообщения в историю диалога
async def add_message_to_dialog_history(user_id: int, message: dict, return_history=False, msgtext = ""):
    # print(message)
    async with aiosqlite.connect(db_path) as db:
        await db.execute('''
        INSERT INTO dialog_history (user_id, message, data_message) 
        VALUES (?, ?, ?)
        ''', (user_id, json.dumps(message), msgtext))
        await db.commit()

        if return_history:
            return await get_dialog_history(user_id)


# Функция для обновления статуса диалога пользователя
async def update_dialog_status(user_id: int, status: bool):
    async with aiosqlite.connect(db_path) as db:
        await db.execute('''
        UPDATE users SET in_dialog = ? WHERE user_id = ?
        ''', (status, user_id))
        await db.commit()


# Функция для очистки диалога
async def clear_dialog(user_id: int, dialog_status: bool):
    async with aiosqlite.connect(db_path) as db:
        await db.execute('DELETE FROM dialog_history WHERE user_id = ?', (user_id,))
        await db.commit()
        await update_dialog_status(user_id, dialog_status)

# Функция для получения статуса диалога пользователя
async def get_dialog_status(user_id: int):
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute('SELECT in_dialog FROM users WHERE user_id = ?', (user_id,))
        user_data = await cursor.fetchone()
        if user_data:
            return user_data[0]
        return None
    
# Функция для получения режима диалога пользователя
async def get_user_mode_dialog(user_id: int):
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute('SELECT TOP 1 * FROM dialog_mode WHERE user_id = ? order by id desc ', (user_id,))
        user_data = await cursor.fetchone()
        if user_data:
            return dict(user_data)
        return None
    
# Функция для установки режима диалога пользователя
async def set_user_mode_dialog(user_id: int, mode_dialog: str):
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(' UPDATE dialog_mode SET mode = ? WHERE user_id = ?', (mode_dialog, user_id))
        user_data = await cursor.fetchone()
        if user_data:
            return dict(user_data)
        return None