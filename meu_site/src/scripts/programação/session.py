import struct

def process_session_data(data, track_info, telemetria, track_limits, flag_map):
    session_data_offset = 24
    if len(data) < session_data_offset + 3:
        return
    track_id = struct.unpack_from("b", data, session_data_offset + 0)[0]
    flag = struct.unpack_from("b", data, session_data_offset + 1)[0]
    total_laps = struct.unpack_from("B", data, session_data_offset + 2)[0]
    track_info["trackId"] = track_id
    limits = track_limits.get(track_id, track_limits[-1])
    track_info.update(limits)
    telemetria["flag"] = flag_map.get(flag, "NONE")
    telemetria["totalLaps"] = total_laps
    telemetria["currentLap"] = struct.unpack_from("B", data, session_data_offset + 3)[0]
    telemetria["lapDistance"] = struct.unpack_from("f", data, session_data_offset + 4)[0]   
TRACK_IDS = {
    0: "Melbourne",
    1: "Paul Ricard",
    2: "Shanghai",
    3: "Sakhir (Bahrain)",
    4: "Catalunya",
    5: "Monaco",
    6: "Montreal",
    7: "Silverstone",
    8: "Hockenheim",
    9: "Hungaroring",
    10: "Spa",
    11: "Monza",
    12: "Singapore",
    13: "Suzuka",
    14: "Abu Dhabi",
    15: "Texas",
    16: "Brazil",
    17: "Austria",
    18: "Sochi",
    19: "Mexico",
    20: "Baku",
    21: "Sakhir Short",
    22: "Silverstone Short",
    23: "Texas Short",
    24: "Suzuka Short",
    25: "Hanoi",
    26: "Zandvoort",
    27: "Imola",
    28: "Portimão",
    29: "Jeddah",
    30: "Miami",
    31: "Las Vegas",
    32: "Qatar",
    33: "Shanghai Alternate",  # Fictício, exemplo
    34: "COTA Alternate"       # Fictício, exemplo
    # ...adicione mais conforme os IDs de 2024
}

def get_track_name(track_id):
    return TRACK_IDS.get(track_id, f"Pista desconhecida (ID {track_id})")
