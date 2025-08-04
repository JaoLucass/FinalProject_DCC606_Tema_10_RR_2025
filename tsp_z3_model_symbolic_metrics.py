# tsp_z3_model.py
from z3 import *

def tsp_model(dist):
    n = len(dist)  # número de cidades

    # --- Variáveis de decisão: p_i indica a cidade na posição i da rota
    p = [Int(f"p_{i}") for i in range(n)]

    # --- Criando o solver
    solver = Optimize()

    # --- Restrições: p_i ∈ [0, n-1]
    for i in range(n):
        solver.add(p[i] >= 0, p[i] < n)

    # --- Restrição: todos os p_i devem ser distintos (rota sem repetição)
    solver.add(Distinct(p))

    # --- Função objetivo: custo total da rota
    custo_total = Sum([
        dist[p[i]][p[(i + 1) % n]] for i in range(n)
    ])
    solver.minimize(custo_total)

    # --- Executar a resolução
    if solver.check() == sat:
        modelo = solver.model()
        rota = [modelo.evaluate(p[i]).as_long() for i in range(n)]
        rota.append(rota[0])  # volta à cidade inicial
        custo = sum(dist[rota[i]][rota[i+1]] for i in range(n))
        return rota, custo
    else:
        print("❌ Nenhuma solução encontrada.")
        return None, None

# --- Exemplo de uso
if __name__ == "__main__":
    # matriz de distâncias de exemplo (4 cidades)
    dist = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]
    ]

    rota, custo = tsp_model(dist)
    if rota:
        print("🔁 Melhor rota encontrada:", " → ".join(map(str, rota)))
        print("💰 Custo total:", custo)
