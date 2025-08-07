# benchmark_tsp_runner.py
import os
import random
import numpy as np
from tsp_z3_model_symbolic_metrics import tsp_model_mbqi, tsp_model_mbqi_subtour, tsp_model_original

def gerar_matriz_distancias(n, seed=0, min_val=5, max_val=100):
    """
    Gera uma matriz simétrica de distâncias aleatórias para n cidades.
    """
    random.seed(seed)
    dist = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            d = random.randint(min_val, max_val)
            dist[i][j] = dist[j][i] = d
    return dist

def calcular_threshold(dist, percentil=90):
    n = len(dist)
    dists = [dist[i][j] for i in range(n) for j in range(n) if i != j]
    return np.percentile(dists, percentil)

def benchmark_variando_n_seeds(n_min=4, n_max=10, seeds=6, output_csv="benchmark_tsp_z3.csv"):
    pasta_benchmark = "resultados_benchmark"
    os.makedirs(pasta_benchmark, exist_ok=True)
    output_csv_path_mbqi = os.path.join(pasta_benchmark, "benchmark_mbqi_" + output_csv)
    output_csv_path_subtour = os.path.join(pasta_benchmark, "benchmark_mbqi_subtour_" + output_csv)
    output_csv_path_original = os.path.join(pasta_benchmark, "benchmark_tsp_z3.csv")
    for n in range(n_min, n_max + 1):
        for seed in range(1, seeds + 1):
            instancia_nome = f"n={n}_seed{seed}"
            dist = gerar_matriz_distancias(n, seed=seed)
            threshold = calcular_threshold(dist, percentil=90)
            print(f"\n🚀 Executando ORIGINAL {instancia_nome}...")
            tsp_model_original(dist, verbose=False, metrics_csv=output_csv_path_original, label=instancia_nome, dist_threshold=threshold)
            print(f"\n🚀 Executando MBQI {instancia_nome}...")
            tsp_model_mbqi(dist, verbose=False, metrics_csv=output_csv_path_mbqi, label=instancia_nome, dist_threshold=threshold)
            print(f"\n🚀 Executando MBQI+Subtour {instancia_nome}...")
            tsp_model_mbqi_subtour(dist, verbose=False, metrics_csv=output_csv_path_subtour, label=instancia_nome, dist_threshold=threshold)

if __name__ == "__main__":
    benchmark_variando_n_seeds()
