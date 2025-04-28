from flask_socketio import SocketIO
import socket
import struct
import threading
from flask import Flask, jsonify, render_template, request
from threading import Thread
from data_processor.udp_listener import coletar_dados_udp
import os
import json
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')

# Caminho para o arquivo de configurações
SETTINGS_FILE = 'settings.json'

# Configurações padrão
default_settings = {
    'updateInterval': 1000,  # Intervalo de atualização em milissegundos
    'theme': 'dark',         # Tema (dark ou light)
    'udpPort': 20777,        # Porta UDP para telemetria (padrão do F1 24)
    'language': 'en'         # Idioma (ex.: 'en' para inglês)
}

# Função para carregar configurações do arquivo
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return default_settings

# Função para salvar configurações no arquivo
def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

# Carrega as configurações iniciais
settings = load_settings()
app = Flask(__name__, static_folder='.', static_url_path='')
socketio = SocketIO(app)

# Configurações do socket UDP
UDP_IP = "0.0.0.0"
UDP_PORT = 20777

# Estrutura para armazenar dados de telemetria
telemetry_data = {}

# Funções de decodificação (copiadas do script anterior)

app = Flask(__name__)
DATA_PATH = 'data/telemetry_log.json'

# Dados globais
posicoes = {i: {"worldPositionX": 0, "worldPositionZ": 0, "nome": f"Carro {i}", "equipe": f"Equipe {i % 10}"} for i in range(22)}
dados_tempos = {
    i: {
        "position": i + 1,
        "nome": f"Carro {i}",
        "gapLider": 0,
        "gapFrente": 0,
        "tyre": "N/A",
        "penalty": "NONE"
    }
    for i in range(22)
}
track_info = {"trackId": -1, "minX": -1000, "maxX": 1000, "minZ": -1000, "maxZ": 1000}
telemetria = {"speed": 0, "rpm": 0, "gear": 0, "drs": 0, "throttle": 0, "brake": 0, "flag": "NONE", "currentLap": 0, "totalLaps": 0}
track_limits = {
    0: {"minX": -500, "maxX": 500, "minZ": -600, "maxZ": 600},
    -1: {"minX": -1000, "maxX": 1000, "minZ": -1000, "maxZ": 1000},
}
flag_map = {-1: "NONE", 0: "NONE", 1: "GREEN", 2: "BLUE", 3: "YELLOW", 4: "RED"}
modo_atual = "race"  # Pode ser "race" ou "qualy"

@app.route('/start-recording', methods=['POST'])
def start_recording():
    data = request.json
    if not all(key in data for key in ["driver", "lap", "speed", "throttle", "brake"]):
        return jsonify({"status": "error", "message": "Campos obrigatórios ausentes"}), 400

    timestamp = datetime.utcnow().isoformat()
    log = {
        "timestamp": timestamp,
        "driver": data["driver"],
        "lap": data["lap"],
        "speed": data["speed"],
        "throttle": data["throttle"],
        "brake": data["brake"]
    }

    os.makedirs('data', exist_ok=True)
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r') as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log)
    with open(DATA_PATH, 'w') as f:
        json.dump(logs, f, indent=2)

    return jsonify({"status": "recorded", "data": log})

@app.route("/api/posicoes")
def get_posicoes():
    return jsonify({
        "posicoes": list(posicoes.values()),  # Posições dos pilotos
        "track": track_info  # Informações sobre os limites da pista
    })

@app.route("/api/tempos")
def get_tempos():
    if modo_atual == "race":
        sorted_cars = sorted(
            dados_tempos.items(),
            key=lambda x: x[1].get("totalDistance", 0),
            reverse=True
        )
    elif modo_atual == "qualy":
        sorted_cars = sorted(
            dados_tempos.items(),
            key=lambda x: x[1].get("lapTime", float("inf"))
        )
    return jsonify([
        {
            "position": car_data["position"],
            "nome": car_data["nome"],
            "gapLider": car_data["gapLider"],
            "gapFrente": car_data["gapFrente"],
            "tyre": car_data["tyre"],
            "penalty": car_data.get("penalty", "NONE")
        }
        for _, car_data in sorted_cars
    ])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/time')
def time_page():
    return app.send_static_file('time.html')

@app.route('/settings')
def settings_page():
    return app.send_static_file('settings.html')

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    global settings
    new_settings = request.json
    settings.update(new_settings)
    save_settings(settings)
    return jsonify({"status": "success", "settings": settings})


@app.route('/save-telemetry',methods=['POST'])
def save_telemetry():
    try:
        data = request.json  # Recebe os dados do frontend
        os.makedirs('data', exist_ok=True)

        # Salva os dados no arquivo JSON
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(data)

        with open(DATA_PATH, 'w') as f:
            json.dump(logs, f, indent=4)

        return jsonify({"status": "success", "message": "Dados salvos com sucesso!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/mostrar_dados')
def mostrar_dados():
    return render_template('mostrar_dados.html')

@app.route('/save_data')
def save_data():
    return render_template('save_data.html')

@app.route('/api/telemetry-logs')
def get_telemetry_logs():
    file_path = 'data/telemetry_log.json'
    if not os.path.exists(file_path):
        return jsonify([])
    with open(file_path, 'r') as f:
        logs = json.load(f)
    return jsonify(logs)

if __name__ == "__main__":
    udp_thread = Thread(target=coletar_dados_udp, args=(posicoes, track_info, telemetria, track_limits, flag_map, dados_tempos))
    udp_thread.daemon = True
    udp_thread.start()
    app.run(host="0.0.0.0", port=5000)
   