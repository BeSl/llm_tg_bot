import sqlite3
from typing import List, Optional, Dict


class DialogDatabase:
    def __init__(self, db_path: str = "dialogs.db"):
        """
        Инициализация подключения к базе данных.
        
        :param db_path: Путь к файлу базы данных SQLite.
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        """Создает таблицу для хранения диалогов, если она не существует."""
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS dialogs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    model_name TEXT NOT NULL,
                    vector_db_path TEXT NOT NULL,
                    logging_settings TEXT NOT NULL,
                    user_access TEXT,
                    description TEXT,
                    enabled INTEGER NOT NULL
                )
            """)

    def add_dialog(
        self,
        name: str,
        model_name: str,
        vector_db_path: str,
        logging_settings: Dict[str, str],
        user_access: Optional[List[str]] = None,
        description: Optional[str] = "",
        enabled: bool = True
    ):
        """
        Добавить диалог в базу данных.
        
        :param name: Имя диалога.
        :param model_name: Имя модели LLM.
        :param vector_db_path: Путь к векторной базе данных.
        :param logging_settings: Настройки логирования (в формате словаря).
        :param user_access: Список пользователей (если None, доступ для всех).
        :param description: Описание диалога.
        :param enabled: Флаг активности диалога.
        """
        user_access_str = ",".join(user_access) if user_access else ""
        logging_settings_str = str(logging_settings)
        enabled_int = 1 if enabled else 0

        with self.connection:
            self.connection.execute("""
                INSERT INTO dialogs (name, model_name, vector_db_path, logging_settings, user_access, description, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, model_name, vector_db_path, logging_settings_str, user_access_str, description, enabled_int))

    def get_dialog(self, name: str) -> Optional[dict]:
        """
        Получить информацию о диалоге по имени.
        
        :param name: Имя диалога.
        :return: Словарь с информацией о диалоге или None.
        """
        cursor = self.connection.execute("""
            SELECT * FROM dialogs WHERE name = ?
        """, (name,))
        row = cursor.fetchone()

        if row:
            return self._row_to_dict(row)
        return None

    def list_dialogs(self, enabled_only: bool = False) -> List[dict]:
        """
        Получить список всех диалогов.
        
        :param enabled_only: Если True, возвращаются только активные диалоги.
        :return: Список словарей с информацией о диалогах.
        """
        query = "SELECT * FROM dialogs"
        params = ()

        if enabled_only:
            query += " WHERE enabled = ?"
            params = (1,)

        cursor = self.connection.execute(query, params)
        rows = cursor.fetchall()

        return [self._row_to_dict(row) for row in rows]

    def delete_dialog(self, name: str):
        """
        Удалить диалог из базы данных.
        
        :param name: Имя диалога.
        """
        with self.connection:
            self.connection.execute("""
                DELETE FROM dialogs WHERE name = ?
            """, (name,))

    def update_dialog(
        self,
        name: str,
        model_name: Optional[str] = None,
        vector_db_path: Optional[str] = None,
        logging_settings: Optional[Dict[str, str]] = None,
        user_access: Optional[List[str]] = None,
        description: Optional[str] = None,
        enabled: Optional[bool] = None
    ):
        """
        Обновить данные о диалоге.
        
        :param name: Имя диалога для обновления.
        :param model_name: Новое имя модели (если None, не обновляется).
        :param vector_db_path: Новый путь к векторной базе (если None, не обновляется).
        :param logging_settings: Новые настройки логирования (если None, не обновляются).
        :param user_access: Новый список пользователей (если None, не обновляется).
        :param description: Новое описание (если None, не обновляется).
        :param enabled: Новый статус активности (если None, не обновляется).
        """
        fields = []
        params = []

        if model_name:
            fields.append("model_name = ?")
            params.append(model_name)
        if vector_db_path:
            fields.append("vector_db_path = ?")
            params.append(vector_db_path)
        if logging_settings:
            fields.append("logging_settings = ?")
            params.append(str(logging_settings))
        if user_access:
            fields.append("user_access = ?")
            params.append(",".join(user_access))
        if description is not None:
            fields.append("description = ?")
            params.append(description)
        if enabled is not None:
            fields.append("enabled = ?")
            params.append(1 if enabled else 0)

        if fields:
            query = f"UPDATE dialogs SET {', '.join(fields)} WHERE name = ?"
            params.append(name)

            with self.connection:
                self.connection.execute(query, params)

    def _row_to_dict(self, row) -> dict:
        """Преобразует строку результата SQL в словарь."""
        return {
            "id": row[0],
            "name": row[1],
            "model_name": row[2],
            "vector_db_path": row[3],
            "logging_settings": eval(row[4]),
            "user_access": row[5].split(",") if row[5] else [],
            "description": row[6],
            "enabled": bool(row[7])
        }

    def close(self):
        """Закрыть соединение с базой данных."""
        self.connection.close()
