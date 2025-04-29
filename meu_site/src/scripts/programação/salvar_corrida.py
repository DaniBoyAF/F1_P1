import os
import json
from datetime import datetime
from udp_listener import get_final_race_data  # Ajuste isso conforme seu listener real

def salvar_corrida():
    dados_corrida = get_final_race_data()  # coleta do seu sistema
    pista = dados_corrida["track_name"].replace(" ", "_").lower()
    data = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"corridas_salvas/corrida_{pista}_{data}.json"

    os.makedirs("corridas_salvas", exist_ok=True)

    with open(nome_arquivo, "w") as f:
        json.dump(dados_corrida, f, indent=2)

    print(f"[✔] Corrida salva em {nome_arquivo}")

if __name__ == "__main__":
    salvar_corrida()
