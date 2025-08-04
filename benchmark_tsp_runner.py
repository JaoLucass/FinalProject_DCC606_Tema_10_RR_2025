# benchmark_tsp_runner.py
import os
import random
import numpy as np
from tsp_z3_model_symbolic_metrics import tsp_model

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
    output_csv_path = os.path.join(pasta_benchmark, output_csv)
    for n in range(n_min, n_max + 1):
        for seed in range(1, seeds + 1):
            instancia_nome = f"n={n}_seed{seed}"
            print(f"\n🚀 Executando instância {instancia_nome}...")
            dist = gerar_matriz_distancias(n, seed=seed)
            tsp_model(dist, verbose=False, metrics_csv=output_csv_path, label=instancia_nome)

if __name__ == "__main__":
    benchmark_variando_n_seeds()
