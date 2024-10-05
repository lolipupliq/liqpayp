# hashcat/hashcat_runner.py
import subprocess
import threading


class HashcatRunner:
    """
    Класс для управления запуском Hashcat и обработки его вывода.
    """

    def __init__(self, hash_file, hashcat_options, progress_callback, logger):
        """
        Инициализирует HashcatRunner.

        :param hash_file: Путь к файлу с хешами.
        :param hashcat_options: Опции командной строки для Hashcat.
        :param progress_callback: Функция обратного вызова для обновления прогресса.
        :param logger: Экземпляр Logger для логирования.
        """
        self.hash_file = hash_file
        self.hashcat_options = hashcat_options
        self.progress_callback = progress_callback
        self.logger = logger

    def run_hashcat(self, password_file):
        """
        Запускает Hashcat с указанными параметрами и обрабатывает его вывод.

        :param password_file: Путь к файлу с паролями.
        :return: Количество успешных попыток.
        """
        hashcat_command = ['hashcat', '-m', '0', self.hash_file, password_file] + self.hashcat_options.split()
        try:
            process = subprocess.Popen(
                hashcat_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except FileNotFoundError:
            raise RuntimeError("Hashcat не найден. Убедитесь, что Hashcat установлен и доступен в PATH.")
        except Exception as e:
            raise RuntimeError(f"Не удалось запустить Hashcat: {e}")

        successful_attempts = 0

        def read_output(pipe):
            nonlocal successful_attempts
            for line in iter(pipe.readline, ''):
                self.progress_callback(line.strip())
                if "Recovered" in line:
                    successful_attempts += 1
            pipe.close()

        stdout_thread = threading.Thread(target=read_output, args=(process.stdout,))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr,))
        stdout_thread.start()
        stderr_thread.start()
        stdout_thread.join()
        stderr_thread.join()
        process.wait()

        self.logger.log_successful_attempts(successful_attempts)
        return successful_attempts

    def run_hashcat_with_masks(self, password_file, masks):
        """
        Запускает Hashcat с использованием масок.

        :param password_file: Путь к файлу с паролями.
        :param masks: Список масок для атаки.
        """
        for mask in masks:
            self.run_hashcat(password_file)
