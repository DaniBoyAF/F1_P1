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