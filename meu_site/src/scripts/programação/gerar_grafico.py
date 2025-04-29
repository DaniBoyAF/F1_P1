import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def carregar_corrida(caminho):
    with open(caminho) as f:
        return json.load(f)

def gerar_grafico(path_arquivo):
    dados = carregar_corrida(path_arquivo)
    voltas = []

    for piloto in dados["pilotos"]:
        nome = piloto["nome"]
        pneus = piloto.get("pneus", [])
        for v in piloto["voltas"]:
            voltas.append({
                "piloto": nome,
                "volta": v["numero"],
                "tempo": v["tempo"],
                "pneu": pneus[v["numero"]] if v["numero"] < len(pneus) else "?"
            })

    df = pd.DataFrame(voltas)

    # Boxplot
    plt.figure(figsize=(14, 7))
    sns.boxplot(data=df, x="piloto", y="tempo", palette="tab20", showmeans=True)
    plt.title("Boxplot - Tempos por Piloto")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("graficos/boxplot.png")
    plt.close()

    # Lap Time Line Plot
    plt.figure(figsize=(14, 7))
    for piloto in df["piloto"].unique():
        linha = df[df["piloto"] == piloto]
        sns.lineplot(x="volta", y="tempo", data=linha, label=piloto)

    plt.title("Desempenho por Volta")
    plt.xlabel("Volta")
    plt.ylabel("Tempo (s)")
    plt.legend(loc="upper right", ncol=2)
    plt.tight_layout()
    plt.savefig("graficos/lap_times.png")
    plt.close()

    print("[✔] Gráficos salvos na pasta graficos/")

if __name__ == "__main__":
    arquivos = sorted(os.listdir("corridas_salvas"))
    if arquivos:
        gerar_grafico(f"corridas_salvas/{arquivos[-1]}")
