# gui/gui_app.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from models.markov_model import MarkovModel
from models.ml_password_model import MLPasswordModel
from generators.adaptive_password_generator import AdaptivePasswordGenerator
from hashcat.hashcat_runner import HashcatRunner
from utils.logger import Logger
from utils.database import Database
from utils.queue_manager import QueueManager
import numpy as np
import threading


class GUIApp:
    """
    Класс для графического интерфейса приложения.
    """

    def __init__(self, root):
        """
        Инициализирует GUI приложение.

        :param root: Корневой элемент Tkinter.
        """
        self.root = root
        self.root.title("Password Cracker GUI")

        # Переменные для хранения значений полей
        self.password_file_var = tk.StringVar()
        self.hash_file_var = tk.StringVar()
        self.length_var = tk.StringVar(value='10')
        self.ngram_var = tk.StringVar(value='3')
        self.batch_size_var = tk.StringVar(value='10000')
        self.hashcat_options_var = tk.StringVar(value='-a 0')
        self.model_type_var = tk.StringVar(value='MarkovModel')
        self.rules_file_var = tk.StringVar(value='hashcat_rules.txt')
        self.model_file_var = tk.StringVar()

        # Инициализация компонентов
        self.build_gui()

        self.password_model = None
        self.password_generator = None
        self.hashcat_runner = None
        self.logger = Logger()
        self.db = Database()
        self.queue_manager = QueueManager(self.db)

    def build_gui(self):
        """
        Создаёт элементы GUI.
        """
        # Фрейм для ввода файлов
        file_frame = ttk.LabelFrame(self.root, text="Файлы")
        file_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        ttk.Label(file_frame, text="Файл с паролями:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.password_file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Выбрать", command=lambda: self.open_file(self.password_file_var)).grid(row=0,
                                                                                                            column=2,
                                                                                                            padx=5,
                                                                                                            pady=5)

        ttk.Label(file_frame, text="Файл с хешами:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.hash_file_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Выбрать", command=lambda: self.open_file(self.hash_file_var)).grid(row=1, column=2,
                                                                                                        padx=5, pady=5)

        # Фрейм для настроек модели
        model_frame = ttk.LabelFrame(self.root, text="Настройки Модели")
        model_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        ttk.Label(model_frame, text="Тип модели:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        ttk.OptionMenu(model_frame, self.model_type_var, "MarkovModel", "MarkovModel", "MLPasswordModel").grid(row=0,
                                                                                                               column=1,
                                                                                                               sticky='w',
                                                                                                               padx=5,
                                                                                                               pady=5)

        ttk.Label(model_frame, text="Длина пароля:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(model_frame, textvariable=self.length_var).grid(row=1, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(model_frame, text="Размер N-граммы:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(model_frame, textvariable=self.ngram_var).grid(row=2, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(model_frame, text="Размер партии паролей:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(model_frame, textvariable=self.batch_size_var).grid(row=3, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(model_frame, text="Параметры Hashcat:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(model_frame, textvariable=self.hashcat_options_var).grid(row=4, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(model_frame, text="Файл с правилами Hashcat:").grid(row=5, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(model_frame, textvariable=self.rules_file_var, width=50).grid(row=5, column=1, padx=5, pady=5)
        ttk.Button(model_frame, text="Загрузить правила", command=self.generate_rules).grid(row=5, column=2, padx=5,
                                                                                            pady=5)

        # Фрейм для управления моделями
        manage_model_frame = ttk.LabelFrame(self.root, text="Управление Моделями")
        manage_model_frame.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

        ttk.Label(manage_model_frame, text="Файл модели:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(manage_model_frame, textvariable=self.model_file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(manage_model_frame, text="Сохранить модель", command=self.save_model).grid(row=0, column=2, padx=5,
                                                                                              pady=5)
        ttk.Button(manage_model_frame, text="Загрузить модель из файла", command=self.load_model_from_file).grid(row=1,
                                                                                                                 column=2,
                                                                                                                 padx=5,
                                                                                                                 pady=5)

        ttk.Button(manage_model_frame, text="Загрузить модель из данных", command=self.load_model).grid(row=1, column=0,
                                                                                                        padx=5, pady=5)
        ttk.Button(manage_model_frame, text="Дообучить модель", command=self.update_model).grid(row=1, column=1, padx=5,
                                                                                                pady=5)

        # Фрейм для атаки
        attack_frame = ttk.LabelFrame(self.root, text="Атака")
        attack_frame.grid(row=3, column=0, padx=10, pady=10, sticky='ew')

        ttk.Button(attack_frame, text="Начать атаку", command=self.start_async_generation).grid(row=0, column=0, padx=5,
                                                                                                pady=10)

        # Фрейм для отображения логов и прогресса
        log_frame = ttk.LabelFrame(self.root, text="Логи и Прогресс")
        log_frame.grid(row=4, column=0, padx=10, pady=10, sticky='nsew')

        self.log_text = tk.Text(log_frame, height=10, state='disabled')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Фрейм для управления сохранёнными моделями
        saved_models_frame = ttk.LabelFrame(self.root, text="Сохранённые Модели")
        saved_models_frame.grid(row=5, column=0, padx=10, pady=10, sticky='nsew')

        self.models_tree = ttk.Treeview(saved_models_frame, columns=("ID", "Тип", "Версия", "Сохранено в"),
                                        show='headings')
        self.models_tree.heading("ID", text="ID")
        self.models_tree.heading("Тип", text="Тип модели")
        self.models_tree.heading("Версия", text="Версия")
        self.models_tree.heading("Сохранено в", text="Сохранено в")
        self.models_tree.pack(fill='both', expand=True, padx=5, pady=5)

        ttk.Button(saved_models_frame, text="Обновить список", command=self.refresh_models_list).pack(pady=5)

        # Настройка растяжения
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def open_file(self, var):
        """
        Открывает диалог выбора файла и устанавливает выбранный путь в переменную.

        :param var: Переменная Tkinter для установки пути к файлу.
        """
        filename = filedialog.askopenfilename()
        var.set(filename)

    def load_passwords(self, filename):
        """
        Загружает пароли из указанного файла.

        :param filename: Путь к файлу с паролями.
        :return: Список паролей.
        """
        try:
            with open(filename, 'r') as file:
                passwords = file.read().splitlines()
            return passwords
        except FileNotFoundError:
            self.log("Ошибка: Файл не найден!")
            return []

    def load_model(self):
        """
        Загружает модель на основе выбранного типа и данных.
        """
        model_type = self.model_type_var.get()
        passwords = self.load_passwords(self.password_file_var.get())
        if not passwords:
            return

        try:
            if model_type == "MarkovModel":
                n = int(self.ngram_var.get())
                self.password_model = MarkovModel(passwords, n)
                self.log("Марковская модель успешно загружена!")
            elif model_type == "MLPasswordModel":
                # Реализуйте загрузку и предварительную обработку реальных данных
                X, y = self.preprocess_passwords(passwords)
                self.password_model = MLPasswordModel((X, y))
                self.log("ML модель успешно загружена!")
            else:
                self.log("Ошибка: Неизвестный тип модели!")
        except ValueError as ve:
            self.log(f"Ошибка: {ve}")
        except Exception as e:
            self.log(f"Ошибка при загрузке модели: {e}")

    def preprocess_passwords(self, passwords):
        """
        Предварительно обрабатывает пароли для обучения ML модели.

        :param passwords: Список паролей.
        :return: Кортеж (X, y) для обучения модели.
        """
        X = []
        y = []
        for pwd in passwords:
            for i in range(len(pwd) - 1):
                X.append(ord(pwd[i]))
                y.append(ord(pwd[i + 1]))
        X = np.array(X).reshape(-1, 1)
        y = np.array(y)
        return X, y

    def update_model(self):
        """
        Дообучает загруженную модель новыми данными.
        """
        if not self.password_model:
            self.log("Ошибка: Модель не загружена!")
            return

        new_passwords = self.load_passwords(self.password_file_var.get())
        if not new_passwords:
            return

        try:
            if isinstance(self.password_model, MarkovModel):
                self.password_model.update_model(new_passwords)
                self.log("Марковская модель успешно дообучена!")
            elif isinstance(self.password_model, MLPasswordModel):
                new_data = self.preprocess_passwords(new_passwords)
                self.password_model.update_model(new_data)
                self.log("ML модель успешно дообучена!")
            else:
                self.log("Ошибка: Тип модели не поддерживает дообучение!")
        except Exception as e:
            self.log(f"Ошибка при дообучении модели: {e}")

    def generate_rules(self):
        """
        Генерирует правила для Hashcat на основе модели.
        """
        if not self.password_model:
            self.log("Ошибка: Модель не загружена!")
            return

        rules_file = self.rules_file_var.get()
        try:
            self.password_model.generate_hashcat_rules(rules_file)
            self.log(f"Правила сохранены в файл: {rules_file}")
        except Exception as e:
            self.log(f"Ошибка при генерации правил: {e}")

    def save_model(self):
        """
        Сохраняет текущую модель в файл и записывает метаданные в базу данных.
        """
        if not self.password_model:
            self.log("Ошибка: Модель не загружена!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pkl",
                                                 filetypes=[("Pickle Files", "*.pkl"), ("All Files", "*.*")])
        if not file_path:
            return

        version = self.password_model.version

        try:
            self.password_model.save_model(file_path, version)
            model_type = self.model_type_var.get()
            self.db.add_model(model_type, file_path, version)
            self.log(f"Модель сохранена в файл: {file_path}")
            self.refresh_models_list()
        except IOError as e:
            self.log(f"Ошибка при сохранении модели: {e}")
        except Exception as e:
            self.log(f"Неизвестная ошибка при сохранении модели: {e}")

    def load_model_from_file(self):
        """
        Загружает модель из файла и обновляет интерфейс.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Pickle Files", "*.pkl"), ("All Files", "*.*")])
        if not file_path:
            return

        model_type = self.model_type_var.get()

        try:
            if model_type == "MarkovModel":
                self.password_model = MarkovModel()
            elif model_type == "MLPasswordModel":
                self.password_model = MLPasswordModel()
            else:
                self.log("Ошибка: Неизвестный тип модели!")
                return

            self.password_model.load_model(file_path)
            self.log(f"Модель успешно загружена из файла: {file_path}")
            self.refresh_models_list()
        except (FileNotFoundError, ValueError, KeyError, IOError) as e:
            self.log(f"Ошибка при загрузке модели: {e}")
        except Exception as e:
            self.log(f"Неизвестная ошибка при загрузке модели: {e}")

    def refresh_models_list(self):
        """
        Обновляет список сохранённых моделей в интерфейсе.
        """
        for item in self.models_tree.get_children():
            self.models_tree.delete(item)
        models = self.db.list_models()
        for model in models:
            self.models_tree.insert('', 'end', values=(model[0], model[1], model[3], model[2]))

    def start_async_generation(self):
        """
        Запускает генерацию паролей и атаку в асинхронном режиме.
        """
        if not self.password_model:
            self.log("Ошибка: Модель не загружена!")
            return

        try:
            length = int(self.length_var.get())
            batch_size = int(self.batch_size_var.get())
        except ValueError:
            self.log("Ошибка: Длина пароля и размер партии должны быть целыми числами!")
            return

        output_file = 'generated_passwords.txt'

        self.password_generator = AdaptivePasswordGenerator(
            self.password_model,
            output_file,
            batch_size,
            self.logger
        )
        self.hashcat_runner = HashcatRunner(
            self.hash_file_var.get(),
            self.hashcat_options_var.get(),
            self.update_progress,
            self.logger
        )

        # Запуск в отдельном потоке
        threading.Thread(target=self.run_attack, args=(length, output_file), daemon=True).start()

    def run_attack(self, length, output_file):
        """
        Выполняет генерацию паролей и запуск Hashcat.

        :param length: Длина генерируемых паролей.
        :param output_file: Путь к файлу для сохранения паролей.
        """
        try:
            self.log("Начата генерация паролей...")
            self.password_generator.generate_password_batch_parallel(length)
            self.log("Генерация паролей завершена.")
            self.log("Запуск Hashcat...")
            successful_attempts = self.hashcat_runner.run_hashcat(output_file)
            self.password_generator.register_success(successful_attempts)
            self.log("Атака завершена!")
        except Exception as e:
            self.log(f"Ошибка во время атаки: {e}")

    def update_progress(self, message):
        """
        Обновляет прогресс атаки в логах.

        :param message: Строка сообщения прогресса.
        """
        self.log(f"Прогресс: {message}")

    def log(self, message):
        """
        Добавляет сообщение в лог.

        :param message: Сообщение для логирования.
        """
        self.log_text.config(state='normal')
        self.log_text.insert('end', message + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')
