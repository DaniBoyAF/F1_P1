from flask import Flask, jsonify, render_template, request, session, redirect
from flask_socketio import SocketIO
from threading import Thread
from datetime import datetime
import os
import json
import struct
from programação.udp_listener import coletar_dados_udp
from flask_cors import CORS
from programação.udp_listener import car_positions
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# ==== Configurações do Flask e SocketIO ====
app = Flask(__name__, static_folder='.', static_url_path='')
socketio = SocketIO(app)

# ==== Arquivos e diretórios ====
DATA_PATH = 'data/telemetry_log.json'
SETTINGS_FILE = 'settings.json'

# ==== Configurações padrão ====
default_settings = {
    'updateInterval': 1000,
    'theme': 'dark',
    'udpPort': 20777,
    'language': 'en'
}

# ==== Funções auxiliares ====
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def process_participants_data(data, posicoes):
    header_size = 24
    participant_data_size = 56
    num_active_cars = struct.unpack_from("B", data, header_size - 1)[0]

    for i in range(num_active_cars):
        offset = header_size + (i * participant_data_size)
        name_bytes = struct.unpack_from("c" * 48, data, offset + 9)
        name = b"".join(name_bytes).decode("utf-8").strip("\x00")
        posicoes[i]["nome"] = name

# ==== Dados Globais ====
settings = load_settings()
modo_atual = "race"  # "race" ou "qualy"

posicoes = {i: {"worldPositionX": 0, "worldPositionZ": 0, "nome": f"Carro {i}", "equipe": f"Equipe {i % 10}"} for i in range(22)}
track_info = {"trackId": -1, "minX": -1000, "maxX": 1000, "minZ": -1000, "maxZ": 1000}
track_limits = {0: {"minX": -500, "maxX": 500, "minZ": -600, "maxZ": 600}, -1: {"minX": -1000, "maxX": 1000, "minZ": -1000, "maxZ": 1000}}
flag_map = {-1: "NONE", 0: "NONE", 1: "GREEN", 2: "BLUE", 3: "YELLOW", 4: "RED"}

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

telemetria_volta = {
    i: {
        "lapDistance": [], "speed": [], "throttle": [], "brake": [],
        "gear": [], "rpm": [], "gapLider": [], "currentLap": 0
    }
    for i in range(22)
}

telemetria = {
    "speed": 0, "rpm": 0, "gear": 0, "drs": 0,
    "throttle": 0, "brake": 0, "flag": "NONE",
    "currentLap": 0, "totalLaps": 0
}

# ==== Rotas ====
  # Import direto

app = Flask(__name__)
CORS(app)

@app.route("/api/map_data")
def map_data():
    return jsonify(car_positions)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/time')
def time_page():
    return app.send_static_file('time.html')

@app.route('/settings')
def settings_page():
    return app.send_static_file('settings.html')

@app.route('/mostrar_dados')
def mostrar_dados():
    return render_template('mostrar_dados.html')

@app.route('/save_data')
def save_data():
    return render_template('save_data.html')

@app.route("/api/posicoes")
def get_posicoes():
    return jsonify({
        "posicoes": list(posicoes.values()),
        "track": track_info
    })

@app.route("/api/tempos")
def get_tempos():
    if modo_atual == "race":
        sorted_cars = sorted(dados_tempos.items(), key=lambda x: x[1].get("totalDistance", 0), reverse=True)
    else:
        sorted_cars = sorted(dados_tempos.items(), key=lambda x: x[1].get("lapTime", float("inf")))

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

@app.route('/api/telemetry-logs')
def get_telemetry_logs():
    if not os.path.exists(DATA_PATH):
        return jsonify([])
    with open(DATA_PATH, 'r') as f:
        return jsonify(json.load(f))

@app.route('/start-recording', methods=['POST'])
def start_recording():
    data = request.json
    required = ["driver", "lap", "speed", "throttle", "brake"]
    if not all(key in data for key in required):
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
    logs = []
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r') as f:
            logs = json.load(f)
    logs.append(log)
    with open(DATA_PATH, 'w') as f:
        json.dump(logs, f, indent=2)

    return jsonify({"status": "recorded", "data": log})

@app.route('/save-telemetry', methods=['POST'])
def save_telemetry():
    try:
        data = request.json
        os.makedirs('data', exist_ok=True)

        logs = []
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, 'r') as f:
                logs = json.load(f)
        logs.append(data)
        with open(DATA_PATH, 'w') as f:
            json.dump(logs, f, indent=4)

        return jsonify({"status": "success", "message": "Dados salvos com sucesso!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

app = Flask(__name__)
app.secret_key = "segredo123"  # Use algo seguro!

def get_db():
    return sqlite3.connect('telemetria.db')

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return redirect('/')
    except sqlite3.IntegrityError:
        return "Usuário já existe"

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM usuarios WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result and check_password_hash(result[0], password):
        session['username'] = username
        return redirect('/')
    else:
        return "Usuário ou senha inválidos"

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

# ==== Inicialização ====
if __name__ == "__main__":
    udp_thread = Thread(target=coletar_dados_udp, args=(posicoes, track_info, telemetria, track_limits, flag_map, dados_tempos, telemetria_volta))
    udp_thread.daemon = True
    udp_thread.start()

    app.run(host="0.0.0.0", port=5000)
