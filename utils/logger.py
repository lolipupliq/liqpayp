# utils/logger.py
import json
import os
import threading


class Logger:
    """
    Класс для логирования результатов с поддержкой потокобезопасности.
    """

    def __init__(self, log_file="session_log.json"):
        """
        Инициализирует Logger.

        :param log_file: Путь к файлу для сохранения логов.
        """
        self.log_file = log_file
        self.lock = threading.Lock()
        self.ensure_log_file()

    def ensure_log_file(self):
        """
        Создаёт лог-файл, если он не существует.
        """
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as file:
                json.dump([], file)

    def log_results(self, data):
        """
        Логирует данные в файл.

        :param data: Словарь с данными для логирования.
        """
        with self.lock:
            try:
                with open(self.log_file, 'r') as file:
                    logs = json.load(file)
            except json.JSONDecodeError:
                logs = []
            logs.append(data)
            with open(self.log_file, 'w') as file:
                json.dump(logs, file, indent=4)

    def log_successful_attempts(self, attempts):
        """
        Логирует количество успешных попыток.

        :param attempts: Количество успешных попыток.
        """
        self.log_results({"successful_attempts": attempts})

    def log_failed_attempts(self, attempts):
        """
        Логирует количество неудачных попыток.

        :param attempts: Количество неудачных попыток.
        """
        self.log_results({"failed_attempts": attempts})
