# Dicionários existentes
track_info = {
    "trackId": -1,
    "minX": -1000,
    "maxX": 1000,
    "minZ": -1000,
    "maxZ": 1000,
    "trackTemp": 0,
    "airTemp": 0
}

track_limits = {
    0: {"minX": -500, "maxX": 500, "minZ": -600, "maxZ": 600},
    1: {"minX": -700, "maxX": 700, "minZ": -800, "maxZ": 800},
    -1: {"minX": -1000, "maxX": 1000, "minZ": -1000, "maxZ": 1000},
}

track_paths = {
    0: [
        (-400, 500), (-300, 550), (-200, 500), (-100, 400), (0, 300),
        (100, 200), (200, 100), (300, 0), (400, -100), (450, -200),
        (400, -300), (300, -400), (200, -450), (100, -500), (0, -550),
        (-100, -500), (-200, -400), (-300, -300), (-400, -200), (-450, 0),
        (-400, 200), (-400, 400)
    ],
    -1: []
}

# Função para calcular limites com base no traçado
def calculate_track_limits(track_id, path, margin=20):
    if not path:  # Se o traçado estiver vazio, usa limites padrão
        return {"minX": -1000, "maxX": 1000, "minZ": -1000, "maxZ": 1000}
    
    x_coords = [x for x, z in path]
    z_coords = [z for x, z in path]
    
    min_x = min(x_coords) - margin
    max_x = max(x_coords) + margin
    min_z = min(z_coords) - margin
    max_z = max(z_coords) + margin
    
    return {"minX": min_x, "maxX": max_x, "minZ": min_z, "maxZ": max_z}

# Atualiza os limites para todas as pistas
def update_all_track_limits():
    for track_id, path in track_paths.items():
        new_limits = calculate_track_limits(track_id, path)
        track_limits[track_id] = new_limits
        print(f"Limites atualizados para trackId {track_id}: {new_limits}")

# Atualiza os limites
update_all_track_limits()

# Atualiza track_info com os limites da pista atual
current_track_id = track_info["trackId"]
current_limits = track_limits.get(current_track_id, track_limits[-1])
track_info.update(current_limits)
track_info["trackTemp"] = 20
print(f"track_info atualizado: {track_info}")