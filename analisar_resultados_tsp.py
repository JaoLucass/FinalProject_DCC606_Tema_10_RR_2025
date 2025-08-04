# analisar_resultados_tsp.py
import os
import pandas as pd
import matplotlib.pyplot as plt

def analisar_csv(caminho_csv="resultados_benchmark/benchmark_tsp_z3.csv", salvar_filtrados=True):
    # --- Pastas de saída
    pasta_analise = "resultados_analise"
    os.makedirs(pasta_analise, exist_ok=True)

    # --- Ler CSV
    df = pd.read_csv(caminho_csv)

    # Converter tempo para float (em caso de falha ou string vazia)
    df = df[pd.to_numeric(df["tempo_total_s"], errors='coerce').notnull()]
    df["tempo_total_s"] = df["tempo_total_s"].astype(float)
    df["n"] = df["n"].astype(int)

    # --- Gráfico 1: tempo médio por n
    plt.figure(figsize=(10, 6))
    df_grouped = df.groupby("n")["tempo_total_s"].agg(["mean", "max", "min", "std"])
    df_grouped["mean"].plot(marker='o', label='Média')
    df_grouped["max"].plot(marker='x', linestyle='--', label='Máximo')
    df_grouped["min"].plot(marker='x', linestyle='--', label='Mínimo')
    plt.title("⏱️ Tempo total vs número de cidades (n)")
    plt.xlabel("n (número de cidades)")
    plt.ylabel("Tempo total (segundos)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_analise, "grafico_tempo_por_n.png"))
    plt.close()

    # --- Gráfico 2: tempo por instância
    plt.figure(figsize=(10, 6))
    df_sorted = df.sort_values("n")
    plt.plot(df_sorted["instancia"], df_sorted["tempo_total_s"], marker='o')
    plt.xticks(rotation=90)
    plt.title("⏱️ Tempo total por instância (seeds)")
    plt.xlabel("Instância")
    plt.ylabel("Tempo total (segundos)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_analise, "grafico_tempo_por_instancia.png"))
    plt.close()

    # --- Gráfico 3: custo médio por n
    if "custo" in df.columns:
        df["custo"] = pd.to_numeric(df["custo"], errors='coerce')
        custo_medio = df.groupby("n")["custo"].mean()
        plt.figure(figsize=(10, 6))
        custo_medio.plot(marker='o')
        plt.title("💰 Custo médio da rota vs n")
        plt.xlabel("n")
        plt.ylabel("Custo médio")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(pasta_analise, "grafico_custo_por_n.png"))
        plt.close()

    # --- Filtrar instâncias difíceis
    threshold = 5  # segundos
    df_dificeis = df[df["tempo_total_s"] > threshold]
    if salvar_filtrados:
        caminho_dificeis = os.path.join(pasta_analise, "instancias_dificeis.csv")
        df_dificeis.to_csv(caminho_dificeis, index=False)
        print(f"🔎 {len(df_dificeis)} instâncias com tempo > {threshold}s salvas em '{caminho_dificeis}'")

    print("✅ Análise finalizada. Gráficos salvos em:")
    print(f" - {os.path.join(pasta_analise, 'grafico_tempo_por_n.png')}")
    print(f" - {os.path.join(pasta_analise, 'grafico_tempo_por_instancia.png')}")
    print(f" - {os.path.join(pasta_analise, 'grafico_custo_por_n.png')}")
    if not df_dificeis.empty:
        print(f" - {os.path.join(pasta_analise, 'instancias_dificeis.csv')}")

if __name__ == "__main__":
    analisar_csv()
