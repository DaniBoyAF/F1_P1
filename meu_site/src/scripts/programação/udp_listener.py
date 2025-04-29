import socket
import struct
from process_motion_data import process_motion_data
from programação.session import process_session_data
from track_data import track_limits, flag_map ,compound_map,track_paths,track_info
from programação.car_status import process_car_status_data
from threading import Thread
import struct
from flask import Flask

UDP_IP = "0.0.0.0"
UDP_PORT = 20777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

def coletar_dados_udp(posicoes, track_info, telemetria, track_limits, flag_map, dados_tempos, telemetria_volta):
    while True:
        data, addr = sock.recvfrom(2048)
        if len(data) < 6:
            continue
        packet_id = struct.unpack_from("B", data, 5)[0]
        if packet_id == 0:
            process_motion_data(data, posicoes)
        elif packet_id == 1:
            process_session_data(data, track_info, telemetria, track_limits, flag_map)
        elif packet_id == 2:
            process_lap_data(data, dados_tempos, telemetria, telemetria_volta)
        elif packet_id == 4:  # Packet ID 4: Participants Data
            process_participants_data(data, posicoes)

def process_lap_data(data, dados_tempos, telemetria, telemetria_volta):
    lap_data_offset = 24
    car_data_size = 53
    player_car_idx = struct.unpack_from("B", data, 21)[0]
    for i in range(22):
        base = lap_data_offset + i * car_data_size
        if len(data) < base + 24:
            continue
        last_lap_time = struct.unpack_from("<f", data, base + 0)[0]
        sector1_time = struct.unpack_from("<f", data, base + 12)[0]
        sector2_time = struct.unpack_from("<f", data, base + 16)[0]
        total_distance = struct.unpack_from("<f", data, base + 8)[0]
        pit_status = struct.unpack_from("B", data, base + 26)[0]
        current_lap = struct.unpack_from("B", data, base + 4)[0]

        dados_tempos[i]["lapTime"] = last_lap_time if last_lap_time > 0 else dados_tempos[i]["lapTime"]
        dados_tempos[i]["s1"] = sector1_time if sector1_time > 0 else dados_tempos[i]["s1"]
        dados_tempos[i]["s2"] = sector2_time if sector2_time > 0 else dados_tempos[i]["s2"]
        if dados_tempos[i]["lapTime"] > 0 and dados_tempos[i]["s1"] > 0 and dados_tempos[i]["s2"] > 0:
            dados_tempos[i]["s3"] = dados_tempos[i]["lapTime"] - (dados_tempos[i]["s1"] + dados_tempos[i]["s2"])
        dados_tempos[i]["totalDistance"] = total_distance
        dados_tempos[i]["status"] = "PIT" if pit_status == 1 else "RUN"
        dados_tempos[i]["currentLap"] = current_lap

        if i == player_car_idx:
            telemetria["currentLap"] = current_lap

        if telemetria_volta[i]["currentLap"] != current_lap:
            telemetria_volta[i] = {
                "lapDistance": [],
                "speed": [],
                "throttle": [],
                 "brake": [],
                "gear": [],
                "rpm": [],
                "gapLider": [],
                "currentLap": current_lap
            }
    print(f"Dados de tempos atualizados: {dados_tempos}")

def verificar_limites_pista(posicao_x, posicao_z, track_limits, track_id):
    limites = track_limits.get(track_id, track_limits[-1])  # Obtém os limites da pista atual ou os padrões
    if not (limites["minX"] <= posicao_x <= limites["maxX"] and limites["minZ"] <= posicao_z <= limites["maxZ"]):
        return False  # Fora dos limites
    return True  # Dentro dos limites



def process_participants_data(data, posicoes):
    # O Packet Participants Data começa no byte 24
    header_size = 24
    participant_data_size = 56  # Cada piloto ocupa 56 bytes
    num_active_cars = struct.unpack_from("B", data, header_size - 1)[0]  # Número de carros ativos

    for i in range(num_active_cars):
        offset = header_size + (i * participant_data_size)
        name_bytes = struct.unpack_from("c" * 48, data, offset + 9)  # Nome do piloto (48 bytes)
        name = b"".join(name_bytes).decode("utf-8").strip("\x00")  # Decodifica e remove caracteres nulos
        posicoes[i]["nome"] = name  # Atualiza o nome do piloto na variável global

if __name__ == "__main__":
    # Inicialize a variável telemetria_volta
    telemetria_volta = {i: {"lapDistance": [], "speed": [], "throttle": [], "brake": [], "gear": [], "rpm": [], "gapLider": [], "currentLap": 0} for i in range(22)}

    # Inicialize a variável posicoes
    posicoes = {i: {"x": 0.0, "y": 0.0, "z": 0.0} for i in range(22)}

    # Inicialize a variável telemetria
    telemetria = {}

    # Inicialize a variável dados_tempos
    dados_tempos = {i: {"lapTime": 0, "s1": 0, "s2": 0, "s3": 0, "totalDistance": 0, "status": "", "currentLap": 0} for i in range(22)}

    # Inicie a thread para coletar dados UDP
    udp_thread = Thread(target=coletar_dados_udp, args=(posicoes, track_info, telemetria, track_limits, flag_map, dados_tempos, telemetria_volta))
    udp_thread.daemon = True
    udp_thread.start()
    # Inicie o servidor Flask
    app = Flask(__name__)
    # Inicie o servidor Flask
    app.run(host="0.0.0.0", port=5000)