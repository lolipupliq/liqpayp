# models/markov_model.py
import pickle
from collections import defaultdict, Counter
import random
from .base_password_model import BasePasswordModel


class MarkovModel(BasePasswordModel):
    """
    Модель паролей на основе цепей Маркова.
    """

    def __init__(self, passwords=None, n=3):
        """
        Инициализирует модель с заданным набором паролей и размером N-грамм.

        :param passwords: Список паролей для обучения модели.
        :param n: Размер N-грамм.
        """
        self.passwords = passwords if passwords is not None else []
        self.n = n
        self.markov_model = defaultdict(Counter)
        self.version = "1.0"
        if self.passwords:
            self.build_model()
            self.normalize_model()

    def generate_ngrams(self):
        """
        Генерирует N-граммы из списка паролей.

        :return: Список N-грамм.
        """
        ngrams = []
        for password in self.passwords:
            for i in range(len(password) - self.n + 1):
                ngrams.append(password[i:i + self.n])
        return ngrams

    def build_model(self):
        """
        Строит модель цепей Маркова на основе N-грамм.
        """
        ngrams = self.generate_ngrams()
        for ngram in ngrams:
            prefix, next_char = ngram[:-1], ngram[-1]
            self.markov_model[prefix][next_char] += 1

    def normalize_model(self):
        """
        Нормализует частоты переходов для вероятностного выбора следующего символа.
        """
        for prefix, next_chars in self.markov_model.items():
            total = sum(next_chars.values())
            for char in next_chars:
                next_chars[char] /= total

    def generate_password(self, length=8):
        """
        Генерирует пароль заданной длины на основе модели Маркова.

        :param length: Длина генерируемого пароля.
        :return: Сгенерированный пароль в виде строки.
        """
        if not self.markov_model:
            raise ValueError("Марковская модель не была построена.")
        start = random.choice(list(self.markov_model.keys()))
        password = list(start)
        for _ in range(length - len(start)):
            current_prefix = ''.join(password[-(self.n - 1):])
            if current_prefix in self.markov_model:
                next_char = random.choices(
                    list(self.markov_model[current_prefix].keys()),
                    weights=self.markov_model[current_prefix].values()
                )[0]
                password.append(next_char)
            else:
                break
        return ''.join(password)

    def update_model(self, new_passwords):
        """
        Обновляет модель новыми паролями.

        :param new_passwords: Список новых паролей.
        """
        self.passwords.extend(new_passwords)
        self.build_model()
        self.normalize_model()

    def generate_hashcat_rules(self, output_file):
        """
        Генерирует правила для Hashcat и сохраняет их в указанный файл.

        :param output_file: Путь к файлу для сохранения правил.
        """
        with open(output_file, 'w') as f:
            for prefix, next_chars in self.markov_model.items():
                for next_char, weight in next_chars.items():
                    rule = f'[{prefix}]{next_char} # weight: {weight}\n'
                    f.write(rule)

    def save_model(self, file_path, version):
        """
        Сохраняет модель Маркова в файл с помощью pickle.

        :param file_path: Путь к файлу для сохранения модели.
        :param version: Версия модели.
        """
        try:
            with open(file_path, 'wb') as f:
                pickle.dump({
                    'version': version,
                    'passwords': self.passwords,
                    'n': self.n,
                    'markov_model': self.markov_model
                }, f)
        except Exception as e:
            raise IOError(f"Не удалось сохранить модель: {e}")

    def load_model(self, file_path):
        """
        Загружает модель Маркова из файла с помощью pickle.

        :param file_path: Путь к файлу для загрузки модели.
        """
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                self.version = data.get('version', '1.0')
                self.passwords = data['passwords']
                self.n = data['n']
                self.markov_model = data['markov_model']
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл модели не найден: {file_path}")
        except pickle.UnpicklingError:
            raise ValueError("Ошибка при загрузке модели: файл повреждён или несовместим.")
        except KeyError as e:
            raise KeyError(f"Отсутствует необходимый ключ в данных модели: {e}")
        except Exception as e:
            raise IOError(f"Не удалось загрузить модель: {e}")
