# utils/database.py
import sqlite3
import threading
import os


class Database:
    """
    Класс для управления базой данных.
    """

    def __init__(self, db_file="password_cracker.db"):
        """
        Инициализирует подключение к базе данных.

        :param db_file: Путь к файлу базы данных.
        """
        self.db_file = db_file
        self.lock = threading.Lock()
        self.connect()
        self.create_tables()

    def connect(self):
        """
        Устанавливает соединение с базой данных.
        """
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """
        Создаёт необходимые таблицы в базе данных.
        """
        with self.lock:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS attacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT,
                    status TEXT,
                    result TEXT
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_type TEXT,
                    file_path TEXT,
                    version TEXT,
                    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()

    def add_attack(self, task, status="In Progress", result=None):
        """
        Добавляет новую атаку в базу данных.

        :param task: Описание задачи атаки.
        :param status: Статус задачи.
        :param result: Результат атаки.
        """
        with self.lock:
            self.cursor.execute('''
                INSERT INTO attacks (task, status, result) VALUES (?, ?, ?)
            ''', (task, status, result))
            self.conn.commit()

    def update_attack_status(self, task, status, result):
        """
        Обновляет статус и результат атаки.

        :param task: Описание задачи атаки.
        :param status: Новый статус.
        :param result: Результат атаки.
        """
        with self.lock:
            self.cursor.execute('''
                UPDATE attacks SET status = ?, result = ? WHERE task = ?
            ''', (status, result, task))
            self.conn.commit()

    def list_attacks(self):
        """
        Получает список всех атак.

        :return: Список кортежей с данными атак.
        """
        with self.lock:
            self.cursor.execute('''
                SELECT * FROM attacks
            ''')
            return self.cursor.fetchall()

    def add_model(self, model_type, file_path, version):
        """
        Добавляет информацию о сохранённой модели в базу данных.

        :param model_type: Тип модели (MarkovModel, MLPasswordModel).
        :param file_path: Путь к файлу модели.
        :param version: Версия модели.
        """
        with self.lock:
            self.cursor.execute('''
                INSERT INTO models (model_type, file_path, version) VALUES (?, ?, ?)
            ''', (model_type, file_path, version))
            self.conn.commit()

    def list_models(self):
        """
        Получает список всех сохранённых моделей.

        :return: Список кортежей с данными моделей.
        """
        with self.lock:
            self.cursor.execute('''
                SELECT * FROM models
            ''')
            return self.cursor.fetchall()

    def get_model(self, model_id):
        """
        Получает информацию о модели по её идентификатору.

        :param model_id: Идентификатор модели.
        :return: Кортеж с данными модели.
        """
        with self.lock:
            self.cursor.execute('''
                SELECT * FROM models WHERE id = ?
            ''', (model_id,))
            return self.cursor.fetchone()
