# generators/adaptive_password_generator.py
import concurrent.futures
import threading


class AdaptivePasswordGenerator:
    """
    Генератор паролей с адаптивной стратегией на основе производительности модели.
    """

    def __init__(self, model, output_file, batch_size, logger, success_threshold=5):
        """
        Инициализирует генератор паролей.

        :param model: Модель для генерации паролей.
        :param output_file: Путь к файлу для сохранения сгенерированных паролей.
        :param batch_size: Размер партии паролей.
        :param logger: Экземпляр Logger для логирования.
        :param success_threshold: Порог успешных попыток для адаптации стратегии.
        """
        self.model = model
        self.output_file = output_file
        self.batch_size = batch_size
        self.logger = logger
        self.success_threshold = success_threshold
        self.successful_attempts = 0
        self.lock = threading.Lock()

    def adapt_strategy(self):
        """
        Адаптирует стратегию генерации паролей на основе успешных попыток.
        """
        with self.lock:
            if self.successful_attempts < self.success_threshold and hasattr(self.model, 'n'):
                self.model.n = min(self.model.n + 1, 10)

    def generate_password_batch(self, length):
        """
        Генерирует пароли и сохраняет их в файл.

        :param length: Длина генерируемых паролей.
        """
        try:
            with open(self.output_file, 'a') as f:
                for _ in range(self.batch_size):
                    password = self.model.generate_password(length=length)
                    f.write(password + '\n')
        except Exception as e:
            self.logger.log_failed_attempts(1)
            raise IOError(f"Не удалось сгенерировать пароли: {e}")

    def generate_password_batch_parallel(self, length, num_threads=4):
        """
        Генерирует пароли параллельно с использованием нескольких потоков.

        :param length: Длина генерируемых паролей.
        :param num_threads: Количество потоков.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(self.generate_password_batch, length) for _ in range(num_threads)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.log_failed_attempts(1)
                    print(f"Ошибка при генерации паролей: {e}")

    def generate_hashcat_rules(self, rules_file):
        """
        Генерирует правила для Hashcat с использованием модели.

        :param rules_file: Путь к файлу для сохранения правил.
        """
        try:
            self.model.generate_hashcat_rules(rules_file)
        except Exception as e:
            self.logger.log_failed_attempts(1)
            raise IOError(f"Не удалось сгенерировать правила Hashcat: {e}")

    def register_success(self, successful_attempts):
        """
        Регистрирует количество успешных попыток и адаптирует стратегию.

        :param successful_attempts: Количество успешных попыток.
        """
        with self.lock:
            self.successful_attempts = successful_attempts
            self.logger.log_successful_attempts(successful_attempts)
            self.adapt_strategy()
