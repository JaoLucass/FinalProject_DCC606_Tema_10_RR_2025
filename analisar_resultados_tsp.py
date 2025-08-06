# analisar_resultados_tsp.py
import os
import pandas as pd
import matplotlib.pyplot as plt


def analisar_comparativo_csvs(
    arquivos_metodos={
        "original": "resultados_benchmark/benchmark_tsp_z3.csv",
        "mbqi": "resultados_benchmark/benchmark_mbqi_benchmark_tsp_z3.csv",
        "mbqi_subtour": "resultados_benchmark/benchmark_mbqi_subtour_benchmark_tsp_z3.csv"
    },
    salvar_filtrados=True
):
    pasta_analise = "resultados_analise"
    os.makedirs(pasta_analise, exist_ok=True)
    dfs = []
    for metodo, caminho in arquivos_metodos.items():
        if os.path.exists(caminho):
            df = pd.read_csv(caminho)
            df = df[pd.to_numeric(df["tempo_total_s"], errors='coerce').notnull()]
            df["tempo_total_s"] = df["tempo_total_s"].astype(float)
            df["n"] = df["n"].astype(int)
            if "custo" in df.columns:
                df["custo"] = pd.to_numeric(df["custo"], errors='coerce')
            df["metodo"] = metodo
            dfs.append(df)
        else:
            print(f"Arquivo não encontrado: {caminho}")
    if not dfs:
        print("Nenhum arquivo CSV encontrado para análise.")
        return
    df_all = pd.concat(dfs, ignore_index=True)

    # --- Gráfico comparativo: tempo médio por n e método
    plt.figure(figsize=(10, 6))
    df_grouped = df_all.groupby(["n", "metodo"])["tempo_total_s"].mean().unstack()
    df_grouped.plot(marker='o')
    plt.title("⏱️ Tempo médio por n (comparativo)")
    plt.xlabel("n (número de cidades)")
    plt.ylabel("Tempo médio total (s)")
    plt.grid(True)
    plt.legend(title="Método")
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_analise, "grafico_comparativo_tempo_por_n.png"))
    plt.close()

    # --- Gráfico comparativo: custo médio por n e método
    if "custo" in df_all.columns:
        plt.figure(figsize=(10, 6))
        df_custo = df_all.groupby(["n", "metodo"])["custo"].mean().unstack()
        df_custo.plot(marker='o')
        plt.title("💰 Custo médio por n (comparativo)")
        plt.xlabel("n (número de cidades)")
        plt.ylabel("Custo médio")
        plt.grid(True)
        plt.legend(title="Método")
        plt.tight_layout()
        plt.savefig(os.path.join(pasta_analise, "grafico_comparativo_custo_por_n.png"))
        plt.close()

    # --- Gráfico comparativo: tempo por instância
    plt.figure(figsize=(12, 6))
    for metodo in arquivos_metodos.keys():
        df_metodo = df_all[df_all["metodo"] == metodo].sort_values("n")
        plt.plot(df_metodo["instancia"], df_metodo["tempo_total_s"], marker='o', label=metodo)
    plt.xticks(rotation=90)
    plt.title("⏱️ Tempo total por instância (comparativo)")
    plt.xlabel("Instância")
    plt.ylabel("Tempo total (segundos)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_analise, "grafico_comparativo_tempo_por_instancia.png"))
    plt.close()

    # --- Filtrar instâncias difíceis (qualquer método)
    threshold = 5  # segundos
    df_dificeis = df_all[df_all["tempo_total_s"] > threshold]
    if salvar_filtrados:
        caminho_dificeis = os.path.join(pasta_analise, "instancias_dificeis_comparativo.csv")
        df_dificeis.to_csv(caminho_dificeis, index=False)
        print(f"🔎 {len(df_dificeis)} instâncias com tempo > {threshold}s salvas em '{caminho_dificeis}'")

    print("✅ Análise comparativa finalizada. Gráficos salvos em:")
    print(f" - {os.path.join(pasta_analise, 'grafico_comparativo_tempo_por_n.png')}")
    print(f" - {os.path.join(pasta_analise, 'grafico_comparativo_custo_por_n.png')}")
    print(f" - {os.path.join(pasta_analise, 'grafico_comparativo_tempo_por_instancia.png')}")
    if not df_dificeis.empty:
        print(f" - {os.path.join(pasta_analise, 'instancias_dificeis_comparativo.csv')}")


if __name__ == "__main__":
    analisar_comparativo_csvs()
