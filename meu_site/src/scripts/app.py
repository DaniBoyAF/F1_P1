from flask import Flask, jsonify, request
import json
import os

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

@app.route('/')
def index():
    return app.send_static_file('index.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)