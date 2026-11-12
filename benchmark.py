"""
benchmark.py - Corre BFS, DFS, A* y UCS desde el mismo estado inicial.
Uso: python benchmark.py  (muestra las tablas y guarda resultados.csv)
Los nodos y el costo siempre dan igual; el tiempo es la mediana de varias corridas.
"""
import csv
import statistics
from datos import construir_instancia
from busqueda import bfs, dfs, a_estrella, ramificacion_efectiva

REPETICIONES = 7
ALGORITMOS = [("BFS", bfs), ("DFS", dfs), ("A*", a_estrella),
              ("UCS (h=0)", lambda p: a_estrella(p, usar_h=False))]


def correr(p):
    filas = []
    for nombre, f in ALGORITMOS:
        rs = [f(p) for _ in range(REPETICIONES)]
        r = rs[0]
        r.tiempo_ms = statistics.median(x.tiempo_ms for x in rs)
        r.algoritmo = nombre
        filas.append(r)
    return filas


def main():
    p = construir_instancia(7)
    print(f"Cursos elegibles: {[c.codigo for c in p.cursos]}  | excluidos: {p.excluidas}")
    print(f"Grupos con cupo por curso: {[len(o) for o in p.opciones]}  | h(s0) = {p.h(p.estado_inicial())}")
    filas = correr(p)
    copt = min(r.costo for r in filas)
    print("\n== Tabla 1. Benchmark (instancia principal, n = 7 cursos) ==")
    print(f"{'Algoritmo':10s} {'Costo':>5s} {'Expand.':>8s} {'Gener.':>7s} {'Mem.pico':>8s} {'ms':>8s} {'b*':>5s} {'Óptimo':>6s}")
    with open("resultados.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "algoritmo", "costo", "expandidos", "generados", "memoria_pico", "tiempo_ms", "b_efectivo"])
        for r in filas:
            b = ramificacion_efectiva(r.generados, p.n)
            print(f"{r.algoritmo:10s} {r.costo:5d} {r.expandidos:8d} {r.generados:7d} {r.memoria_pico:8d} "
                  f"{r.tiempo_ms:8.1f} {b:5.2f} {'sí' if r.costo == copt else 'no':>6s}")
            w.writerow([p.n, r.algoritmo, r.costo, r.expandidos, r.generados, r.memoria_pico,
                        round(r.tiempo_ms, 2), round(b, 3)])
        print("\nSolución de A*:")
        print("\n".join("  " + l for l in p.describir(filas[2].estado_meta)))

        print("\n== Tabla 2. Escalamiento: nodos expandidos según n ==")
        print(f"{'n':>2s} {'BFS':>7s} {'DFS':>6s} {'A*':>7s} {'UCS':>7s} | costos BFS/DFS/A*")
        for n in range(3, 9):
            q = construir_instancia(n)
            rs = correr(q)
            print(f"{n:2d} {rs[0].expandidos:7d} {rs[1].expandidos:6d} {rs[2].expandidos:7d} {rs[3].expandidos:7d}"
                  f" | {rs[0].costo}/{rs[1].costo}/{rs[2].costo}")
            for r in rs:
                w.writerow([n, r.algoritmo, r.costo, r.expandidos, r.generados, r.memoria_pico,
                            round(r.tiempo_ms, 2), round(ramificacion_efectiva(r.generados, n), 3)])


if __name__ == "__main__":
    main()
