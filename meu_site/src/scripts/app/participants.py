import struct

def process_participants_data(data, posicoes, dados_tempos):
    participants_offset = 24
    num_cars = struct.unpack_from("B", data, participants_offset)[0]
    for i in range(min(num_cars, 22)):
        base = participants_offset + 1 + i * 56
        if len(data) < base + 48:
            continue
        nome = data[base + 19:base + 39].decode("utf-8", errors="ignore").strip("\x00")
        car_number = struct.unpack_from("B", data, base + 2)[0]
        posicoes[i]["nome"] = nome if nome else f"Carro {i}"
        dados_tempos[i]["nome"] = nome if nome else f"Carro {i}"
        dados_tempos[i]["carNumber"] = car_number