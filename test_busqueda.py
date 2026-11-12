"""Pruebas: soluciones válidas, A* óptimo y heurística admisible y consistente.
Ejecutar: python test_busqueda.py"""
from functools import lru_cache
from datos import construir_instancia
from busqueda import bfs, dfs, a_estrella
from modelo import ProblemaMatricula


def costo_optimo_desde(p):
    """Costo óptimo real hasta la meta desde cada estado (programación dinámica)."""
    @lru_cache(maxsize=None)
    def hstar(s):
        if p.es_meta(s):
            return 0
        suc = p.sucesores(s)
        return min((c + hstar(s2) for _, s2, c in suc), default=float("inf"))
    return hstar


def test_soluciones_validas_y_optimo():
    for n in (3, 4, 5, 6):
        p = construir_instancia(n)
        opt = costo_optimo_desde(p)(p.estado_inicial())
        for alg in (bfs, dfs, a_estrella):
            r = alg(p)
            assert p.es_meta(r.estado_meta) and p.es_valido(r.estado_meta), (n, r.algoritmo)
            assert r.costo == p.costo_total(r.estado_meta)
        assert a_estrella(p).costo == opt, f"A* no óptimo con n={n}"
        assert a_estrella(p, usar_h=False).costo == opt


def test_h_admisible_y_consistente():
    p = construir_instancia(5)
    hstar = costo_optimo_desde(p)
    visto, pila = set(), [p.estado_inicial()]
    while pila:
        s = pila.pop()
        if s in visto:
            continue
        visto.add(s)
        assert p.h(s) <= hstar(s), f"h no admisible en {s}"
        for _, s2, c in p.sucesores(s):
            assert p.h(s) <= c + p.h(s2), f"h no consistente en {s}->{s2}"
            pila.append(s2)
    print(f"h admisible y consistente en {len(visto)} estados")


def test_acciones_equivalentes_a_sucesores():
    p = construir_instancia(5)
    s = p.estado_inicial()
    for _ in range(3):
        suc = p.sucesores(s)
        assert [a for a, _, _ in suc] == p.acciones(s)
        for a, s2, c in suc:
            assert s2 == p.resultado(s, a) and c == p.costo_paso(s, a)
        s = suc[0][1]


def test_prerrequisitos_y_creditos():
    p = construir_instancia(7)
    assert [c for c, _ in p.excluidas] == ["CAL4"]          # falta CAL3
    from datos import CURSOS, APROBADAS, generar_grupos, LISTA_DESEADA
    chico = ProblemaMatricula(CURSOS, generar_grupos(), APROBADAS, LISTA_DESEADA[:7], max_creditos=18)
    assert a_estrella(chico).estado_meta is None            # 22 créditos > 18, no hay solución


if __name__ == "__main__":
    test_soluciones_validas_y_optimo()
    test_h_admisible_y_consistente()
    test_acciones_equivalentes_a_sucesores()
    test_prerrequisitos_y_creditos()
    print("Todas las pruebas pasaron")
