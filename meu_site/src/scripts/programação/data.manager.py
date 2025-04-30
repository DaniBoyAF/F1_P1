import json
import os
from datetime import datetime, time
import asyncio
from flask import Flask, jsonify, request
import websockets
import logging
from threading import Thread
from queue import Queue


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SESSIONS_DIR = "sessions"
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)
    logger.info(f"Diretório {SESSIONS_DIR} criado.")
connected_clients = set()

# Função para salvar os dados em um arquivo JSON
def save_session_data(data, filename=None):
    try:
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(SESSIONS_DIR, f"session_{timestamp}.json")
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Dados da sessão salvos em {filename}")
    except Exception as e:
        logger.error(f"Erro ao salvar dados da sessão: {e}")

# Função para salvar dados periodicamente
def periodic_save(data_queue, interval=60):
    session_filename = os.path.join(SESSIONS_DIR, f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json")
    while True:
        try:
            # Verifica se há dados na fila
            if not data_queue.empty():
                data = data_queue.get()
                save_session_data(data, session_filename)
            time.sleep(interval)
        except Exception as e:
            logger.error(f"Erro no salvamento periódico: {e}")
            time.sleep(interval)

# Função para enviar dados para todos os clientes WebSocket
async def send_to_clients(data):
    if connected_clients:
        message = json.dumps(data)
        tasks = [asyncio.ensure_future(client.send(message)) for client in connected_clients]
        if tasks:
            await asyncio.wait(tasks)

# Função para gerenciar conexões WebSocket
async def websocket_handler(websocket, path):
    connected_clients.add(websocket)
    logger.info(f"Cliente WebSocket conectado: {websocket.remote_address}")
    try:
        async for message in websocket:
            pass
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Cliente WebSocket desconectado: {websocket.remote_address}")
    finally:
        connected_clients.remove(websocket)

# Função para iniciar o servidor WebSocket
def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = websockets.serve(websocket_handler, "0.0.0.0", 8765)
    logger.info("Servidor WebSocket iniciado na porta 8765")
    loop.run_until_complete(server)
    loop.run_forever()

# Função para enviar dados via WebSocket a partir da fila
def websocket_data_sender(data_queue):
    async def send_data():
        while True:
            if not data_queue.empty():
                data = data_queue.get()
                await send_to_clients(data)
            await asyncio.sleep(0.1)  # Evita consumo excessivo de CPU

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_data())

# Funções para rotas Flask
def list_sessions():
    try:
        sessions = [f for f in os.listdir(SESSIONS_DIR) if f.endswith('.json')]
        return jsonify(sessions)
    except Exception as e:
        logger.error(f"Erro ao listar sessões: {e}")
        return jsonify({"error": "Erro ao listar sessões"}), 500

def get_session(filename):
    try:
        filepath = os.path.join(SESSIONS_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "Arquivo não encontrado"}), 404
        with open(filepath, 'r') as f:
            session_data = json.load(f)
        return jsonify(session_data)
    except Exception as e:
        logger.error(f"Erro ao carregar sessão {filename}: {e}")
        return jsonify({"error": "Erro ao carregar sessão"}), 500

# Função para iniciar o gerenciador de dados
def start_data_manager(data_queue):
    # Inicia a thread para salvamento periódico
    save_thread = Thread(target=periodic_save, args=(data_queue, 60))
    save_thread.daemon = True
    save_thread.start()

    # Inicia o servidor WebSocket em uma thread separada
    websocket_thread = Thread(target=start_websocket_server)
    websocket_thread.daemon = True
    websocket_thread.start()

    # Inicia o envio de dados via WebSocket
    websocket_sender_thread = Thread(target=websocket_data_sender, args=(data_queue,))
    websocket_sender_thread.daemon = True
    websocket_sender_thread.start()