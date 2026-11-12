"""datos.py - Datos de prueba del problema (con semilla fija para que siempre salgan iguales)."""
import random
from modelo import Curso, Grupo, ProblemaMatricula

CURSOS = {c.codigo: c for c in [
    Curso("IA", "Inteligencia Artificial", 3, ("ALG", "PROG")),
    Curso("BD", "Bases de Datos", 3, ("PROG",)),
    Curso("IS", "Ingeniería de Software", 3, ("POO",)),
    Curso("EST", "Estadística", 3, ("CAL2",)),
    Curso("RED", "Redes de Computadores", 3, ("FIS1",)),
    Curso("CAL3", "Cálculo III", 4, ("CAL2",)),
    Curso("SO", "Sistemas Operativos", 3, ("PROG",)),
    Curso("ARQ", "Arquitectura de Computadores", 3, ("FIS1",)),
    Curso("CAL4", "Cálculo IV", 4, ("CAL3",)),   # no elegible: falta CAL3
]}
APROBADAS = ["ALG", "PROG", "POO", "CAL2", "FIS1"]
LISTA_DESEADA = ["IA", "BD", "IS", "EST", "RED", "CAL3", "SO", "ARQ"]
MAX_CREDITOS = 25
PATRONES = [(0, 2), (1, 3), (2, 4), (0, 3), (1, 4), (0, 4)]  # parejas de días de clase


def generar_grupos(semilla: int = 2026, grupos_por_curso: int = 4):
    rnd = random.Random(semilla)
    grupos = []
    for cod in CURSOS:
        for k in range(1, grupos_por_curso + 1):
            dias = rnd.choice(PATRONES)
            bloque = rnd.randrange(6)
            cupo = rnd.choice([0, 3, 5, 9, 15, 22, 30, 40])
            grupos.append(Grupo(f"{cod}-{k}", cod, tuple((d, bloque) for d in dias), cupo))
    return grupos


def construir_instancia(n_cursos: int = 7, con_excluida: bool = True, semilla: int = 2026):
    """n_cursos: cuántos cursos se quieren inscribir. Con con_excluida se pide también CAL4,
    que el filtro de prerrequisitos debe descartar."""
    deseadas = LISTA_DESEADA[:n_cursos] + (["CAL4"] if con_excluida else [])
    return ProblemaMatricula(CURSOS, generar_grupos(semilla), APROBADAS, deseadas, MAX_CREDITOS)
