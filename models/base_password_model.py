# models/base_password_model.py
from abc import ABC, abstractmethod


class BasePasswordModel(ABC):
    """
    Абстрактный базовый класс для моделей паролей.
    Определяет интерфейс, который должны реализовать все модели паролей.
    """

    @abstractmethod
    def generate_password(self, length):
        """
        Генерирует пароль заданной длины.

        :param length: Длина генерируемого пароля.
        :return: Сгенерированный пароль в виде строки.
        """
        pass

    @abstractmethod
    def generate_hashcat_rules(self, output_file):
        """
        Генерирует правила для Hashcat и сохраняет их в указанный файл.

        :param output_file: Путь к файлу для сохранения правил.
        """
        pass

    @abstractmethod
    def update_model(self, new_data):
        """
        Обновляет модель новыми данными.

        :param new_data: Новые данные для обновления модели.
        """
        pass

    @abstractmethod
    def save_model(self, file_path, version):
        """
        Сохраняет модель в файл.

        :param file_path: Путь к файлу для сохранения модели.
        :param version: Версия модели.
        """
        pass

    @abstractmethod
    def load_model(self, file_path):
        """
        Загружает модель из файла.

        :param file_path: Путь к файлу для загрузки модели.
        """
        pass
