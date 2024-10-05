# utils/resource_monitor.py
import psutil


class ResourceMonitor:
    """
    Класс для мониторинга ресурсов системы.
    """

    @staticmethod
    def monitor():
        """
        Отслеживает использование CPU и памяти.

        :return: Словарь с данными об использовании ресурсов.
        """
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        return {"cpu": cpu_usage, "memory": memory_usage}
