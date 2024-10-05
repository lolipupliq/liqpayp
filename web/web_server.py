# web/web_server.py
import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request
from utils.database import Database
from utils.queue_manager import QueueManager
import threading

app = Flask(__name__)
db = Database()
queue_manager = QueueManager(db)


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Password Cracker API is running."}), 200


@app.route('/api/start', methods=['POST'])
def start_attack():
    """
    Эндпоинт для добавления новой задачи атаки.

    Ожидает JSON с ключом 'task'.
    """
    data = request.json
    task = data.get('task')
    if not task:
        return jsonify({"status": "error", "message": "Task not provided"}), 400
    queue_manager.add_task(task)
    return jsonify({"status": "Task added to queue", "task": task}), 200


@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Эндпоинт для получения статуса задач.
    """
    results = []
    while True:
        result = queue_manager.get_result()
        if not result:
            break
        results.append(result)
    return jsonify({"status": "In Progress", "results": results}), 200


@app.route('/api/attacks', methods=['GET'])
def list_attacks():
    """
    Эндпоинт для получения списка всех атак.
    """
    attacks = db.list_attacks()
    attacks_list = []
    for attack in attacks:
        attacks_list.append({
            "id": attack[0],
            "task": attack[1],
            "status": attack[2],
            "result": attack[3]
        })
    return jsonify({"attacks": attacks_list}), 200


@app.route('/api/models', methods=['GET'])
def list_models():
    """
    Эндпоинт для получения списка всех сохранённых моделей.
    """
    models = db.list_models()
    models_list = []
    for model in models:
        models_list.append({
            "id": model[0],
            "model_type": model[1],
            "file_path": model[2],
            "version": model[3],
            "saved_at": model[4]
        })
    return jsonify({"models": models_list}), 200


@app.route('/api/models/<int:model_id>', methods=['GET'])
def get_model(model_id):
    """
    Эндпоинт для получения информации о конкретной модели.

    :param model_id: Идентификатор модели.
    """
    model = db.get_model(model_id)
    if not model:
        return jsonify({"status": "error", "message": "Model not found"}), 404
    model_info = {
        "id": model[0],
        "model_type": model[1],
        "file_path": model[2],
        "version": model[3],
        "saved_at": model[4]
    }
    return jsonify({"model": model_info}), 200


if __name__ == '__main__':
    port = 5001  # Значение по умолчанию
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Порт должен быть целым числом.")
            sys.exit(1)
    app.run(host='0.0.0.0', port=port)
