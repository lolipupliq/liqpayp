# models/ml_password_model.py

from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OneHotEncoder
import joblib
import numpy as np
from .base_password_model import BasePasswordModel
import os
import logging
import pickle

logging.basicConfig(level=logging.INFO)


class MLPasswordModel(BasePasswordModel):
    """
    Модель паролей на основе многослойного перцептрона (MLP).
    """

    def __init__(self, dataset=None):
        """
        Инициализирует модель с заданным набором данных.

        :param dataset: Кортеж (X, y) для обучения модели.
        """
        super().__init__()
        self.dataset = dataset if dataset is not None else ([], [])
        self.model = MLPClassifier(hidden_layer_sizes=(128, 128), max_iter=1000, random_state=42)
        self.encoder = OneHotEncoder(categories='auto', sparse_output=False)  # Используем 'sparse_output'
        self.char_to_int = {}
        self.int_to_char = {}
        self.num_classes = 0
        self.version = "1.0"

        if len(self.dataset[0]) > 0 and len(self.dataset[1]) > 0:
            self.preprocess_data()
            self.train_model()

    def preprocess_data(self):
        """
        Предварительно обрабатывает данные для обучения модели:
        - Создаёт словари для преобразования символов в числа и обратно.
        - Выполняет One-Hot Encoding для признаков.
        """
        # Преобразуем X и y обратно в символы
        X_chars = [chr(i[0]) for i in self.dataset[0]]
        y_chars = [chr(i) for i in self.dataset[1]]

        # Соберите уникальные символы из всех паролей
        unique_chars = sorted(list(set(X_chars + y_chars)))
        self.char_to_int = {char: idx for idx, char in enumerate(unique_chars)}
        self.int_to_char = {idx: char for idx, char in enumerate(unique_chars)}
        self.num_classes = len(unique_chars)

        logging.info(f"Уникальных символов: {self.num_classes}")

        # Преобразуйте символы в числовые индексы
        X_indices = [[self.char_to_int[char]] for char in X_chars]
        y_indices = [self.char_to_int[char] for char in y_chars]

        # One-Hot Encoding для X
        self.X_encoded = self.encoder.fit_transform(X_indices)
        self.y_encoded = np.array(y_indices)

        logging.info(f"Размерность X_encoded: {self.X_encoded.shape}")
        logging.info(f"Размерность y_encoded: {self.y_encoded.shape}")

    def train_model(self):
        """
        Обучает модель на предоставленных данных.
        """
        try:
            logging.info(f"Начинаем обучение модели с {self.X_encoded.shape[0]} примерами.")
            self.model.fit(self.X_encoded, self.y_encoded)
            logging.info("ML модель успешно обучена.")
        except Exception as e:
            logging.error(f"Ошибка при обучении модели: {e}")
            raise

    def generate_password(self, length=8):
        """
        Генерирует пароль заданной длины на основе обученной модели.

        :param length: Длина генерируемого пароля.
        :return: Сгенерированный пароль в виде строки.
        """
        if not hasattr(self.model, "classes_"):
            raise ValueError("Модель не была обучена.")
        if not self.char_to_int or not self.int_to_char:
            raise ValueError("Словари char_to_int и int_to_char не инициализированы.")

        password = []
        # Выберите случайный начальный символ
        current_char = np.random.choice(list(self.char_to_int.keys()))
        password.append(current_char)

        for _ in range(length - 1):
            current_int = self.char_to_int[current_char]
            current_encoded = self.encoder.transform([[current_int]])
            next_int = self.model.predict(current_encoded)[0]
            next_char = self.int_to_char.get(next_int, '?')  # Используем '?' для неизвестных индексов
            password.append(next_char)
            current_char = next_char

        return ''.join(password)

    def update_model(self, new_data):
        """
        Обновляет модель новыми данными.

        :param new_data: Кортеж (X_new, y_new) для дообучения модели.
        """
        X_new, y_new = new_data
        if len(X_new) == 0 or len(y_new) == 0:
            logging.warning("Нет новых данных для обновления модели.")
            return

        # Преобразуем X_new и y_new обратно в символы
        X_new_chars = [chr(i[0]) for i in X_new]
        y_new_chars = [chr(i) for i in y_new]

        # Проверка наличия новых символов и обновление словарей
        new_unique_chars = set(X_new_chars + y_new_chars) - set(self.char_to_int.keys())
        if new_unique_chars:
            for char in new_unique_chars:
                self.char_to_int[char] = self.num_classes
                self.int_to_char[self.num_classes] = char
                self.num_classes += 1
            # Обновляем OneHotEncoder с новыми категориями
            self.encoder = OneHotEncoder(categories='auto', sparse_output=False)
            self.preprocess_data()

        # Преобразуем новые данные в индексы
        X_new_indices = [[self.char_to_int[char]] for char in X_new_chars]
        y_new_indices = [self.char_to_int[char] for char in y_new_chars]

        # One-Hot Encoding для X_new
        X_new_encoded = self.encoder.transform(X_new_indices)
        y_new_encoded = np.array(y_new_indices)

        # Проверка совместимости размерности
        if X_new_encoded.shape[1] != self.X_encoded.shape[1]:
            logging.error("Размерность X_new_encoded не совпадает с существующими данными.")
            raise ValueError("Размерность новых данных не совпадает с размерностью обучающих данных.")

        # Дообучение модели
        try:
            self.model.partial_fit(X_new_encoded, y_new_encoded)
            logging.info("ML модель успешно дообучена с новыми данными.")
        except AttributeError:
            # Если partial_fit недоступен, переобучите модель полностью
            self.X_encoded = np.vstack([self.X_encoded, X_new_encoded])
            self.y_encoded = np.concatenate([self.y_encoded, y_new_encoded])
            self.train_model()

    def generate_hashcat_rules(self):
        """
        Генерирует правила для Hashcat на основе модели.
        """
        # Здесь можно добавить логику генерации правил на основе модели
        # Пока оставляем пустым или возвращаем стандартные правила
        logging.info("Генерация правил для Hashcat не реализована.")
        return []

    def load_model(self, file_path):
        """
        Загружает модель из файла.

        :param file_path: Путь к файлу модели.
        """
        try:
            # Загружаем модель
            self.model = joblib.load(file_path)
            logging.info(f"Модель загружена из {file_path}.")

            # Также необходимо загрузить словари и encoder
            meta_path = os.path.splitext(file_path)[0] + "_meta.pkl"
            if not os.path.exists(meta_path):
                logging.error(f"Файл метаданных не найден: {meta_path}")
                raise FileNotFoundError(f"Файл метаданных не найден: {meta_path}")

            with open(meta_path, 'rb') as f:
                meta = pickle.load(f)
                self.char_to_int = meta['char_to_int']
                self.int_to_char = meta['int_to_char']
                self.num_classes = meta['num_classes']
                self.encoder = meta['encoder']
            logging.info("Метаданные модели успешно загружены.")
        except Exception as e:
            logging.error(f"Ошибка при загрузке модели: {e}")
            raise

    def save_model(self, file_path):
        """
        Сохраняет модель в файл.

        :param file_path: Путь к файлу для сохранения модели.
        """
        try:
            # Сохраняем модель
            joblib.dump(self.model, file_path)
            logging.info(f"Модель сохранена в {file_path}.")

            # Сохраняем метаданные (словаря и encoder)
            meta = {
                'char_to_int': self.char_to_int,
                'int_to_char': self.int_to_char,
                'num_classes': self.num_classes,
                'encoder': self.encoder
            }
            meta_path = os.path.splitext(file_path)[0] + "_meta.pkl"
            with open(meta_path, 'wb') as f:
                pickle.dump(meta, f)
            logging.info(f"Метаданные модели сохранены в {meta_path}.")
        except Exception as e:
            logging.error(f"Ошибка при сохранении модели: {e}")
            raise
