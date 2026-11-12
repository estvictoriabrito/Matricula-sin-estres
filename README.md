# Matrículas sin estrés – Búsqueda en espacio de estados (BFS, DFS, A*)

Proyecto integrador de **Inteligencia Artificial** – Universidad Militar Nueva Granada (Facultad de Estudios a Distancia).
Autora: Victoria De Los Ángeles Brito Rodríguez · Docente: John Edwin Vera.

El agente de inscripción de materias de la Fase 1 se formaliza como un problema de búsqueda
**determinista y discreto** y se resuelve con BFS, DFS y A* (UCS se incluye como control con h = 0).

## Requisitos
Python 3.9 o superior. **No requiere librerías externas.**

## Ejecución
```bash
python test_busqueda.py   # verifica soluciones válidas, optimalidad de A*, admisibilidad y consistencia de h
python benchmark.py       # imprime las tablas del informe y genera resultados.csv
```
Nodos expandidos/generados y costos son deterministas (semilla 2026); los tiempos varían según la máquina.

## Archivos
| Archivo | Contenido |
|---|---|
| `modelo.py` | Estado, acciones, transición, prueba de meta, función de costo y heurística `h` |
| `busqueda.py` | `bfs`, `dfs`, `a_estrella` (con `usar_h=False` es UCS), métricas y ramificación efectiva b* |
| `datos.py` | Instancia reproducible: catálogo, prerrequisitos, grupos, cupos y horarios |
| `benchmark.py` | Ejecuta los algoritmos sobre el mismo estado inicial y escala n = 3…8 cursos |
| `test_busqueda.py` | Pruebas automáticas |

## Formalización (resumen)
* **Estado:** tupla `s` de n posiciones; `s[i] = -1` (sin grupo) o el índice del grupo elegido para el curso i.
* **Estado inicial:** ningún curso inscrito.
* **Acciones:** inscribir el curso i en el grupo g si no se cruza con lo ya inscrito y no se excede el máximo de créditos.
* **Transición:** determinista; asigna g al curso i.
* **Meta:** todos los cursos elegibles tienen grupo.
* **Costo de paso:** penalización de franja horaria + riesgo por pocos cupos + penalización por cada día nuevo (siempre ≥ 0).
* **Heurística:** suma del menor costo base de los cursos pendientes + cota inferior de días nuevos (admisible y consistente).

## Nota sobre AIMA
Código propio; la interfaz (`estado_inicial`, `acciones`, `resultado`, `es_meta`, `costo_paso`) sigue la clase `Problem` de
[aima-python](https://github.com/aimacode/aima-python).
