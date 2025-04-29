import struct

def process_car_status_data(data, dados_pneus, dados_tempos, compound_map):
    car_status_offset = 24
    car_data_size = 60
    for i in range(22):
        base = car_status_offset + i * car_data_size
        if len(data) < base + 28:
            continue
        compound = struct.unpack_from("B", data, base + 23)[0]
        tire_type = compound_map.get(compound, "N/A")
        fl_wear = struct.unpack_from("B", data, base + 24)[0]
        fr_wear = struct.unpack_from("B", data, base + 25)[0]
        rl_wear = struct.unpack_from("B", data, base + 26)[0]
        rr_wear = struct.unpack_from("B", data, base + 27)[0]
        pit_stops = struct.unpack_from("B", data, base + 22)[0]
        avg_wear = (fl_wear + fr_wear + rl_wear + rr_wear) / 4
        dados_pneus[i] = {
            "FL": {"desgaste": fl_wear, "tipo": tire_type},
            "FR": {"desgaste": fr_wear, "tipo": tire_type},
            "RL": {"desgaste": rl_wear, "tipo": tire_type},
            "RR": {"desgaste": rr_wear, "tipo": tire_type},
        }
        dados_tempos[i]["tyre"] = tire_type
        dados_tempos[i]["pitStops"] = pit_stops
        dados_tempos[i]["tyreWear"] = avg_wear