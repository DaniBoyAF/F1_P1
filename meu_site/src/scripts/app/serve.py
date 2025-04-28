from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO
import json
import os
import socket
import threading
import f1_data_parser  # Importa o módulo personalizado

app = Flask(__name__, static_folder='.', static_url_path='')
socketio = SocketIO(app)

# Configurações do socket UDP
UDP_IP = "0.0.0.0"
UDP_PORT = 20777

# Estrutura para armazenar dados de telemetria
telemetry_data = {}

# Função para receber dados UDP e enviar via WebSocket
def receive_udp_data():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("Iniciando captura de dados do F1 24 via UDP...")
    
    try:
        while True:
            data, addr = sock.recvfrom(2048)
            parsed_data = f1_data_parser.parse_packet(data)  # Usa a função do módulo
            if parsed_data:
                telemetry_data.update(parsed_data)
                socketio.emit('telemetry_update', telemetry_data)
    finally:
        sock.close()
