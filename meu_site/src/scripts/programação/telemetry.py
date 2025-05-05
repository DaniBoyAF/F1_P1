import struct

def process_telemetry_data(data, telemetria):
    telemetry_offset = 24
    car_data_size = 60
    player_car_idx = struct.unpack_from("B", data, 21)[0]
    for i in range(22):
        base = telemetry_offset + i * car_data_size
        if len(data) < base + 16:
            continue
        speed = struct.unpack_from("<H", data, base + 0)[0]
        throttle = struct.unpack_from("<f", data, base + 2)[0]
        brake = struct.unpack_from("<f", data, base + 4)[0]
        lateral_acceleration = struct.unpack_from("<f", data, base + 12)[0]
        fuel = struct.unpack_from("<f", data, base + 14)[0]

        if i == player_car_idx:
            telemetria.update({
                "speed": speed,
                "throttle": throttle * 100,
                "brake": brake * 100,
                "lateralAcceleration": lateral_acceleration,
                "fuel": fuel
            })

