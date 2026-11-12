"""
busqueda.py - BFS, DFS y A* (UCS es A* con h = 0).

Los tres guardan los estados ya visitados, porque la misma matrícula se puede armar en
muchos órdenes distintos. Se miden nodos expandidos y generados, memoria pico, tiempo y costo.
"""
import heapq
import time
from collections import deque
from dataclasses import dataclass
from itertools import count
from typing import List, Optional


class Nodo:
    __slots__ = ("estado", "padre", "accion", "g")

    def __init__(self, estado, padre, accion, g):
        self.estado, self.padre, self.accion, self.g = estado, padre, accion, g


@dataclass
class Resultado:
    algoritmo: str
    estado_meta: Optional[tuple]
    costo: Optional[int]
    expandidos: int
    generados: int
    memoria_pico: int      # estados guardados a la vez (visitados + frontera)
    tiempo_ms: float
    profundidad: int


def _final(nombre, nodo, exp, gen, mem, t0):
    prof = 0
    n = nodo
    while n is not None and n.padre is not None:
        prof += 1
        n = n.padre
    return Resultado(nombre, nodo.estado if nodo else None, nodo.g if nodo else None,
                     exp, gen, mem, (time.perf_counter() - t0) * 1000, prof)


def bfs(p) -> Resultado:
    """Búsqueda en anchura. Revisa la meta al generar. Solo sería óptima si todos los costos fueran iguales."""
    t0 = time.perf_counter()
    raiz = Nodo(p.estado_inicial(), None, None, 0)
    if p.es_meta(raiz.estado):
        return _final("BFS", raiz, 0, 1, 1, t0)
    frontera, visitados = deque([raiz]), {raiz.estado}
    exp, gen = 0, 1
    while frontera:
        n = frontera.popleft()
        exp += 1
        for a, s2, c in p.sucesores(n.estado):
            if s2 in visitados:
                continue
            hijo = Nodo(s2, n, a, n.g + c)
            gen += 1
            if p.es_meta(s2):
                return _final("BFS", hijo, exp, gen, len(visitados) + 1, t0)
            visitados.add(s2)
            frontera.append(hijo)
    return _final("BFS", None, exp, gen, len(visitados), t0)


def dfs(p) -> Resultado:
    """Búsqueda en profundidad con pila. Revisa la meta al generar. No es óptima."""
    t0 = time.perf_counter()
    raiz = Nodo(p.estado_inicial(), None, None, 0)
    if p.es_meta(raiz.estado):
        return _final("DFS", raiz, 0, 1, 1, t0)
    pila, visitados = [raiz], {raiz.estado}
    exp, gen = 0, 1
    while pila:
        n = pila.pop()
        exp += 1
        hijos = []
        for a, s2, c in p.sucesores(n.estado):
            if s2 in visitados:
                continue
            hijo = Nodo(s2, n, a, n.g + c)
            gen += 1
            if p.es_meta(s2):
                return _final("DFS", hijo, exp, gen, len(visitados) + 1, t0)
            visitados.add(s2)
            hijos.append(hijo)
        pila.extend(reversed(hijos))  # así se explora primero la primera acción
    return _final("DFS", None, exp, gen, len(visitados), t0)


def a_estrella(p, usar_h: bool = True) -> Resultado:
    """A* con f = g + h. Con usar_h=False queda como costo uniforme (UCS).
    La meta se revisa al sacar el nodo de la frontera; así, con h admisible, la solución es óptima."""
    nombre = "A*" if usar_h else "UCS (h=0)"
    h = p.h if usar_h else p.h_cero
    t0 = time.perf_counter()
    raiz = Nodo(p.estado_inicial(), None, None, 0)
    cnt = count()
    frontera = [(h(raiz.estado), h(raiz.estado), next(cnt), raiz)]
    mejor_g = {raiz.estado: 0}
    cerrados = set()
    exp, gen, mem = 0, 1, 1
    while frontera:
        _, _, _, n = heapq.heappop(frontera)
        if n.estado in cerrados:
            continue
        if p.es_meta(n.estado):
            return _final(nombre, n, exp, gen, max(mem, len(mejor_g)), t0)
        cerrados.add(n.estado)
        exp += 1
        for a, s2, c in p.sucesores(n.estado):
            g2 = n.g + c
            if s2 in cerrados or g2 >= mejor_g.get(s2, float("inf")):
                continue
            mejor_g[s2] = g2
            gen += 1
            hijo = Nodo(s2, n, a, g2)
            hs = h(s2)
            heapq.heappush(frontera, (g2 + hs, hs, next(cnt), hijo))
        mem = max(mem, len(mejor_g))
    return _final(nombre, None, exp, gen, mem, t0)


def ramificacion_efectiva(generados: int, profundidad: int) -> float:
    """Ramificación efectiva b*: la que cumple generados + 1 = 1 + b* + ... + b*^d (Russell y Norvig, 2021). Se calcula por bisección."""
    if profundidad <= 0 or generados <= profundidad:
        return 1.0
    lo, hi = 1.0, float(generados)
    for _ in range(200):
        mid = (lo + hi) / 2
        total = sum(mid ** k for k in range(profundidad + 1))
        if total < generados + 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
