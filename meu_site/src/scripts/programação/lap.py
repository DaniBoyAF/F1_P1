import struct

def process_lap_data(data, dados_tempos, telemetria, telemetria_volta):
    lap_data_offset = 24
    car_data_size = 53
    num_cars = 22

    # Verifica o tamanho mínimo necessário para processar todos os carros
    required_size = lap_data_offset + num_cars * car_data_size
    if len(data) < required_size:
        return

    # Extrai o índice do carro do jogador
    player_car_idx = struct.unpack_from("B", data, 21)[0]

    # Formato para decodificar todos os dados de uma vez
    # Cada carro tem: last_lap_time (f), current_lap (B), total_distance (f), sector1_time (f), sector2_time (f), lap_distance (f), pit_status (B)
    format_string = f"<{num_cars * 5}f{num_cars * 2}B"  # 5 floats + 2 bytes por carro

    # Calcula os offsets para todos os carros
    offsets = [lap_data_offset + i * car_data_size for i in range(num_cars)]

    # Monta um buffer com os dados relevantes
    buffer = bytearray()
    for offset in offsets:
        buffer.extend(data[offset:offset + 4])           # last_lap_time (float)
        buffer.extend(data[offset + 4:offset + 5])      # current_lap (uint8)
        buffer.extend(data[offset + 8:offset + 12])     # total_distance (float)
        buffer.extend(data[offset + 12:offset + 16])    # sector1_time (float)
        buffer.extend(data[offset + 16:offset + 20])    # sector2_time (float)
        buffer.extend(data[offset + 20:offset + 24])    # lap_distance (float)
        buffer.extend(data[offset + 26:offset + 27])    # pit_status (uint8)

    # Decodifica todos os dados de uma vez
    unpacked_data = struct.unpack(format_string, buffer)

    # Processa os dados para cada carro
    for i in range(num_cars):
        idx = i * 7  # Índice no array de dados descompactados (5 floats + 2 bytes por carro)
        last_lap_time = unpacked_data[idx]
        current_lap = unpacked_data[idx + 1]
        total_distance = unpacked_data[idx + 2]
        sector1_time = unpacked_data[idx + 3]
        sector2_time = unpacked_data[idx + 4]
        lap_distance = unpacked_data[idx + 5]
        pit_status = unpacked_data[idx + 6]

        # Validação dos tempos
        last_lap_time = last_lap_time if last_lap_time > 0 and last_lap_time < 600 else dados_tempos[i]["lapTime"]  # Limite de 10 minutos
        sector1_time = sector1_time if sector1_time > 0 and sector1_time < 300 else dados_tempos[i]["s1"]  # Limite de 5 minutos
        sector2_time = sector2_time if sector2_time > 0 and sector2_time < 300 else dados_tempos[i]["s2"]

        # Atualiza dados_tempos
        dados_tempos[i].update({
            "lapTime": last_lap_time,
            "s1": sector1_time,
            "s2": sector2_time,
            "totalDistance": total_distance if total_distance >= 0 else dados_tempos[i]["totalDistance"],
            "status": "PIT" if pit_status == 1 else "RUN",
            "currentLap": current_lap
        })

        # Calcula o tempo do setor 3
        if last_lap_time > 0 and sector1_time > 0 and sector2_time > 0:
            s3 = last_lap_time - (sector1_time + sector2_time)
            dados_tempos[i]["s3"] = max(s3, 0)  # Garante que s3 não seja negativo

        # Atualiza telemetria do jogador
        if i == player_car_idx:
            telemetria["currentLap"] = current_lap

        # Atualiza telemetria_volta
        if telemetria_volta[i]["currentLap"] != current_lap:
            # Reseta as listas, mantendo a estrutura
            for key in ["lapDistance", "speed", "throttle", "brake", "gear", "rpm", "gapLider"]:
                telemetria_volta[i][key].clear()
            telemetria_volta[i]["currentLap"] = current_lap

        # Adiciona lap_distance, com validação
        if 0 <= lap_distance <= 100000:  # Limite razoável para distância da volta
            telemetria_volta[i]["lapDistance"].append(lap_distance)
            # Limita o tamanho da lista para evitar crescimento excessivo
            if len(telemetria_volta[i]["lapDistance"]) > 1000:
                telemetria_volta[i]["lapDistance"] = telemetria_volta[i]["lapDistance"][-1000:]