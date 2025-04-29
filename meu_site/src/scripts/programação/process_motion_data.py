import struct

def process_motion_data(data, posicoes):
    motion_data_offset = 24
    car_data_size = 60
    num_cars = 22
    float_size = 4  # Tamanho de um float em bytes

    # Calcula o tamanho mínimo necessário para processar todos os carros
    required_size = motion_data_offset + num_cars * car_data_size
    if len(data) < required_size:
        return  # Sai da função se os dados forem insuficientes

    # Formato para decodificar worldPositionX e worldPositionZ de todos os carros de uma vez
    # Cada carro tem 2 floats (x e z), então são 2 * num_cars floats no total
    format_string = f"<{num_cars * 2}f"  # Ex.: "<44f" para 22 carros (2 floats por carro)

    # Calcula os offsets para todos os carros
    offsets = [motion_data_offset + i * car_data_size for i in range(num_cars)]

    # Extrai todos os dados de uma vez
    # Vamos pular os bytes intermediários (como worldPositionY e outros) ajustando o buffer
    buffer = bytearray()
    for offset in offsets:
        buffer.extend(data[offset:offset + float_size])  # worldPositionX
        buffer.extend(data[offset + 2 * float_size:offset + 3 * float_size])  # worldPositionZ

    # Decodifica todos os valores de uma vez
    positions = struct.unpack(format_string, buffer)

    # Atualiza as posições
    for i in range(num_cars):
        posicoes[i]["worldPositionX"] = positions[i * 2]      # worldPositionX
        posicoes[i]["worldPositionZ"] = positions[i * 2 + 1]  # worldPositionZ