# utils/report_generator.py
import matplotlib.pyplot as plt


class ReportGenerator:
    """
    Класс для генерации отчетов по успешным и неудачным атакам.
    """

    def generate_success_report(self, success_attempts):
        """
        Генерирует график успешных атак.

        :param success_attempts: Список количеств успешных атак по партиям.
        """
        plt.figure(figsize=(10, 5))
        plt.plot(success_attempts, label='Успешные попытки', marker='o')
        plt.xlabel('Партия')
        plt.ylabel('Количество успешных атак')
        plt.title('График успешных атак')
        plt.legend()
        plt.grid(True)
        plt.savefig('success_report.png')
        plt.close()

    def generate_failure_report(self, failure_attempts):
        """
        Генерирует график неудачных атак.

        :param failure_attempts: Список количеств неудачных атак по партиям.
        """
        plt.figure(figsize=(10, 5))
        plt.plot(failure_attempts, label='Неудачные попытки', color='red', marker='x')
        plt.xlabel('Партия')
        plt.ylabel('Количество неудачных атак')
        plt.title('График неудачных атак')
        plt.legend()
        plt.grid(True)
        plt.savefig('failure_report.png')
        plt.close()
