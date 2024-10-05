# utils/queue_manager.py
import queue
import threading
from utils.database import Database


class QueueManager:
    """
    Класс для управления очередью задач и результатами.
    """

    def __init__(self, db):
        """
        Инициализирует QueueManager.

        :param db: Экземпляр Database для взаимодействия с базой данных.
        """
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.db = db
        self.worker_thread = threading.Thread(target=self.worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def add_task(self, task):
        """
        Добавляет новую задачу в очередь и базу данных.

        :param task: Описание задачи.
        """
        self.db.add_attack(task)
        self.task_queue.put(task)

    def get_result(self):
        """
        Получает результат из очереди результатов.

        :return: Результат задачи или None, если нет доступных результатов.
        """
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None

    def worker(self):
        """
        Рабочий поток для обработки задач из очереди.
        """
        while True:
            task = self.task_queue.get()
            # Обработать задачу (реализуйте логику обработки)
            result = self.process_task(task)
            self.result_queue.put(result)
            self.task_queue.task_done()

    def process_task(self, task):
        """
        Обрабатывает задачу и возвращает результат.

        :param task: Задача для обработки.
        :return: Результат обработки задачи.
        """
        # Реализуйте логику обработки задачи
        # Пример:
        result = {"task": task, "status": "Completed"}
        return result
