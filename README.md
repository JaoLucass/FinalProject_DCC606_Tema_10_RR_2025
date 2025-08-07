
# FinalProject_DCC606_Tema_10_RR_2025

Trabalho final da disciplina de Análise de Algoritmos (2025.1)

## Descrição
Este projeto implementa e compara variantes do problema do Caixeiro Viajante (TSP) usando modelagem simbólica com o solver Z3. O objetivo é analisar o impacto de diferentes restrições simbólicas e técnicas de otimização na resolução do TSP.

## Estrutura do Projeto
- `tsp_z3_model_symbolic_metrics.py`: Implementa três variantes do modelo TSP:
  - **Original**: MBQI + restrição de subtours (MTZ) + lazy constraints.
  - **MBQI**: Apenas poda simbólica com quantificadores (sem subtour/lazy).
  - **MBQI+Subtour**: MBQI + restrição de subtours (MTZ), sem lazy constraints.
- `benchmark_tsp_runner.py`: Executa benchmarks variando o número de cidades e seeds, salvando métricas de tempo e custo em arquivos CSV separados para cada variante.
- `analisar_resultados_tsp.py`: Analisa os resultados dos benchmarks, gerando gráficos comparativos de tempo e custo entre as variantes.

## Como Executar
1. Instale as dependências:
   - Python 3.8+
   - z3-solver
   - pandas
   - matplotlib
   - numpy

2. Execute o benchmark:
   ```bash
   python benchmark_tsp_runner.py
   ```
   Os resultados serão salvos na pasta `resultados_benchmark`.

3. Analise os resultados e gere gráficos:
   ```bash
   python analisar_resultados_tsp.py
   ```
   Os gráficos serão salvos na pasta `resultados_analise`.

## Variantes do Modelo
- **Original**: Utiliza todas as restrições simbólicas e lazy constraints para garantir solução ótima e evitar subtours.
- **MBQI**: Utiliza apenas poda simbólica baseada em quantificadores, sem restrição explícita de subtours.
- **MBQI+Subtour**: Combina MBQI com restrição de subtours (MTZ), sem lazy constraints.

## Resultados e Análise
Os gráficos gerados mostram o tempo de execução e o custo médio das rotas para cada variante, permitindo comparar desempenho e qualidade das soluções conforme o número de cidades aumenta.

## Observação
Este projeto foi executado dentro de um ambiente virtual Python (venv), garantindo o isolamento das dependências e reprodutibilidade dos experimentos.

## Créditos
Autor: [João Lucas Sidney Rodrigues]
Disciplina: DCC606 - Análise de Algoritmos
Ano/Semestre: 2025.1
