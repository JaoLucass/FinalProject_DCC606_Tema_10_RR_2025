import os
import csv
import time
from z3 import *

def tsp_model_original(dist, verbose=False, metrics_csv=None, label=None, dist_threshold=None):
    """
    Variante original: MBQI + subtour + lazy constraints (igual à função tsp_model).
    """
    return tsp_model(dist, verbose=verbose, metrics_csv=metrics_csv, label=label, dist_threshold=dist_threshold)

def tsp_model_mbqi(dist, verbose=False, metrics_csv=None, label=None, dist_threshold=None):
    """
    Variante MBQI puro: sem restrição de subtours (MTZ/lazy).
    """
    n = len(dist)
    p = [Int(f"p_{i}") for i in range(n)]
    solver = Optimize()
    constraints = []
    for i in range(n):
        constraints.append(p[i] >= 0)
        constraints.append(p[i] < n)
    constraints.append(Distinct(p))
    solver.add(*constraints)
    # MBQI: Adiciona restrições para pares (a, b) com dist[a][b] > threshold
    if dist_threshold is not None:
        for a in range(n):
            for b in range(n):
                if a != b and dist[a][b] > dist_threshold:
                    for i in range(n):
                        solver.add(Or(p[i] != a, p[(i+1)%n] != b))
    custo_total = Sum([
        Sum([
            If(And(p[i] == a, p[(i + 1) % n] == b), dist[a][b], 0)
            for a in range(n) for b in range(n) if a != b
        ])
        for i in range(n)
    ])
    solver.minimize(custo_total)
    t0 = time.time()
    result = solver.check()
    t1 = time.time()
    num_restricoes = len(solver.assertions())
    if result == sat:
        modelo = solver.model()
        rota = [modelo.evaluate(p[i]).as_long() for i in range(n)]
        rota.append(rota[0])
        custo = sum(dist[rota[i]][rota[i+1]] for i in range(n))
        print(f"[MBQI] Tempo total: {t1-t0:.4f}s | Custo: {custo} | Rota: {rota}")
        if metrics_csv is not None:
            _salvar_metricas_csv(
                metrics_csv,
                {
                    "instancia": label if label else "",
                    "n": n,
                    "num_vars": len(p),
                    "num_restricoes": num_restricoes,
                    "tempo_modelagem_s": t1-t0,
                    "tempo_resolucao_s": 0,
                    "tempo_total_s": t1-t0,
                    "custo": custo,
                    "rota": "-".join(map(str, rota)),
                }
            )
        return rota, custo
    else:
        print("[MBQI] Nenhuma solução encontrada.")
        if metrics_csv is not None:
            _salvar_metricas_csv(
                metrics_csv,
                {
                    "instancia": label if label else "",
                    "n": n,
                    "num_vars": len(p),
                    "num_restricoes": num_restricoes,
                    "tempo_modelagem_s": t1-t0,
                    "tempo_resolucao_s": 0,
                    "tempo_total_s": t1-t0,
                    "custo": "",
                    "rota": "",
                }
            )
        return None, None

def tsp_model_mbqi_subtour(dist, verbose=False, metrics_csv=None, label=None, dist_threshold=None):
    """
    Variante MBQI + restrição de subtours (igual à função tsp_model atual).
    """
    return tsp_model(dist, verbose=verbose, metrics_csv=metrics_csv, label=label, dist_threshold=dist_threshold)

def tsp_model(dist, verbose=False, metrics_csv=None, label=None, dist_threshold=None):
    
    n = len(dist)
    p = [Int(f"p_{i}") for i in range(n)]
    solver = Optimize()

    # --- Tempo: início modelagem
    t0 = time.time()

    # Vamos acumular restrições para poder contar
    constraints = []

    # Domínio de cada variável
    for i in range(n):
        constraints.append(p[i] >= 0)
        constraints.append(p[i] < n)

    # Todas as cidades distintas
    constraints.append(Distinct(p))

    # Adiciona todas as restrições ao solver
    solver.add(*constraints)

    # --- Poda simbólica com quantificadores (MBQI)
    if dist_threshold is not None:
        for a in range(n):
            for b in range(n):
                if a != b and dist[a][b] > dist_threshold:
                    for i in range(n):
                        solver.add(Or(p[i] != a, p[(i+1)%n] != b))

    # --- Restrição de subtours (MTZ)
    # Variáveis auxiliares u[i] para cada cidade
    u = [Int(f"u_{i}") for i in range(n)]
    # Domínio das variáveis auxiliares
    for i in range(n):
        solver.add(u[i] >= 0, u[i] < n)
    # MTZ: Para todo i != j, se p[i] == a e p[(i+1)%n] == b e a != 0 e b != 0, então u[a] + 1 == u[b]
    for i in range(n):
        for j in range(n):
            if i != j and i != 0 and j != 0:
                solver.add(Implies(And(p[i] == i, p[(i+1)%n] == j), u[i] + 1 == u[j]))

    # --- Função objetivo simbólica SEM filtro de threshold
    custo_total = Sum([
        Sum([
            If(And(p[i] == a, p[(i + 1) % n] == b), dist[a][b], 0)
            for a in range(n) for b in range(n) if a != b
        ])
        for i in range(n)
    ])
    solver.minimize(custo_total)

    # --- Tempo: fim modelagem
    t1 = time.time()
    modelagem_tempo = t1 - t0

    # --- Tempo: resolução
    t2 = time.time()
    # --- Lazy constraints para subtours ---
    subtour_found = True
    max_lazy_iters = 20
    lazy_iter = 0
    tempo_resolucao = 0
    rota = None
    custo = None
    while subtour_found and lazy_iter < max_lazy_iters:
        t2_iter = time.time()
        result = solver.check()
        t3_iter = time.time()
        tempo_resolucao += t3_iter - t2_iter
        num_restricoes = len(solver.assertions())
        if result == sat:
            modelo = solver.model()
            rota = [modelo.evaluate(p[i]).as_long() for i in range(n)]
            rota.append(rota[0])
            # Detecta subtours
            visited = set()
            subtours = []
            for start in range(n):
                if start in visited:
                    continue
                tour = [start]
                visited.add(start)
                next_city = modelo.evaluate(p[(tour[-1]+1)%n]).as_long()
                while next_city not in tour:
                    tour.append(next_city)
                    visited.add(next_city)
                    next_city = modelo.evaluate(p[(tour[-1]+1)%n]).as_long()
                if len(tour) < n:
                    subtours.append(tour)
            if subtours:
                # Adiciona restrição para proibir cada subtour
                for st in subtours:
                    solver.add(Or([p[i] != i for i in st]))
                lazy_iter += 1
            else:
                subtour_found = False
                custo = sum(dist[rota[i]][rota[i+1]] for i in range(n))
        else:
            subtour_found = False
            rota = None
            custo = None
    tempo_total = modelagem_tempo + tempo_resolucao
    # Impressão opcional
    if rota is not None:
        print("\n📊 Métricas de Execução")
        print(f"🔖 Instância: {label if label else '(sem rótulo)'}")
        print(f"🔢 Número de cidades (n): {n}")
        print(f"🧩 Variáveis simbólicas: {len(p)}")
        print(f"📐 Restrições adicionadas: {num_restricoes}")
        print(f"⏱️ Tempo de modelagem: {modelagem_tempo:.4f} s")
        print(f"⚙️ Tempo de resolução: {tempo_resolucao:.4f} s")
        print(f"⏳ Tempo total: {tempo_total:.4f} s")
        print(f"💰 Custo total da rota: {custo}")
        print(f"🔁 Rota: {' → '.join(map(str, rota))}")
        if verbose:
            print("\n📤 Modelo SMT:")
            for v in p:
                print(f"{v} = {modelo.evaluate(v)}")
        if metrics_csv is not None:
            _salvar_metricas_csv(
                metrics_csv,
                {
                    "instancia": label if label else "",
                    "n": n,
                    "num_vars": len(p),
                    "num_restricoes": num_restricoes,
                    "tempo_modelagem_s": modelagem_tempo,
                    "tempo_resolucao_s": tempo_resolucao,
                    "tempo_total_s": tempo_total,
                    "custo": custo,
                    "rota": "-".join(map(str, rota)),
                }
            )
        return rota, custo
    else:
        print("❌ Nenhuma solução encontrada.")
        if metrics_csv is not None:
            _salvar_metricas_csv(
                metrics_csv,
                {
                    "instancia": label if label else "",
                    "n": n,
                    "num_vars": len(p),
                    "num_restricoes": num_restricoes,
                    "tempo_modelagem_s": modelagem_tempo,
                    "tempo_resolucao_s": tempo_resolucao,
                    "tempo_total_s": tempo_total,
                    "custo": "",
                    "rota": "",
                }
            )
        return None, None


def _salvar_metricas_csv(caminho, dados):
    """
    Salva (append) uma linha de métricas em arquivo CSV.
    Cria cabeçalho se o arquivo ainda não existir.
    """
    existe = os.path.exists(caminho)
    campos = [
        "instancia", "n", "num_vars", "num_restricoes",
        "tempo_modelagem_s", "tempo_resolucao_s", "tempo_total_s",
        "custo", "rota"
    ]
    with open(caminho, mode="a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        if not existe:
            w.writeheader()
        w.writerow(dados)


def calcular_threshold(dist, percentil=90):
    """
    Calcula o valor de threshold para distâncias baseado em um percentil.
    """
    # Flatten all distances except diagonal
    all_distances = [dist[i][j] for i in range(len(dist)) for j in range(len(dist)) if i != j]
    all_distances.sort()
    k = int(len(all_distances) * percentil / 100)
    if k >= len(all_distances):
        k = len(all_distances) - 1
    return all_distances[k]

# --- Exemplo de uso isolado
if __name__ == "__main__":
    dist = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]
    ]
    # Defina output_csv_path e instancia_nome para evitar NameError
    output_csv_path = "tsp_metrics.csv"
    instancia_nome = "exemplo_n4"
    threshold = calcular_threshold(dist, percentil=90)
    tsp_model(dist, verbose=False, metrics_csv=output_csv_path, label=instancia_nome, dist_threshold=threshold)
