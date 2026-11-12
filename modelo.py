"""
modelo.py - El problema de matrícula formulado como problema de búsqueda.

Para volverlo determinista y discreto se simplificó así:
  - Se trabaja con los cupos de un momento fijo. Si un grupo tiene cupo, se asume que se puede
    inscribir; el riesgo de perderlo se cobra como un costo extra en los grupos con pocos cupos.
  - El tiempo se divide en bloques de 2 horas (6 por día, de lunes a sábado).
  - No se consideran los otros estudiantes mientras se busca.
  - Los prerrequisitos se revisan antes de buscar y los cursos que no cumplen se descartan.

Estado: tupla de n posiciones, una por curso elegible.
  estado[i] = -1  -> el curso i todavía no tiene grupo
  estado[i] = j   -> el curso i quedó en su grupo número j
"""
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

DIAS = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb")
BLOQUES = ("6-8", "8-10", "10-12", "14-16", "16-18", "18-20")
N_BLOQUES = len(BLOQUES)

# Parámetros del costo (todos >= 0)
PEN_BLOQUE = (2, 0, 0, 1, 1, 3)  # castigo por sesión según la franja
PEN_DIA_NUEVO = 2                # castigo por cada día más que hay que ir
PEN_RIESGO_CUPO = 2              # castigo si el grupo tiene pocos cupos
UMBRAL_CUPO = 5                  # pocos cupos = cupo <= 5


@dataclass(frozen=True)
class Curso:
    codigo: str
    nombre: str
    creditos: int
    prerrequisitos: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Grupo:
    id: str
    curso: str
    sesiones: Tuple[Tuple[int, int], ...]  # (día, bloque) de cada sesión
    cupo: int

    @property
    def mascara(self) -> int:
        """Entero con un bit por franja ocupada; dos grupos se cruzan si el AND de sus máscaras no es 0."""
        m = 0
        for d, b in self.sesiones:
            m |= 1 << (d * N_BLOQUES + b)
        return m

    @property
    def mascara_dias(self) -> int:
        m = 0
        for d, _ in self.sesiones:
            m |= 1 << d
        return m

    @property
    def costo_base(self) -> int:
        """Costo del grupo solo: franjas + riesgo de cupo."""
        c = sum(PEN_BLOQUE[b] for _, b in self.sesiones)
        if self.cupo <= UMBRAL_CUPO:
            c += PEN_RIESGO_CUPO
        return c


def _bits(x: int) -> int:
    return bin(x).count("1")


class ProblemaMatricula:
    """Elegir un grupo para cada curso elegible, sin cruces y sin pasarse de créditos."""

    def __init__(self, cursos: Dict[str, Curso], grupos: Iterable[Grupo],
                 aprobadas: Iterable[str], deseadas: Iterable[str], max_creditos: int):
        aprobadas = set(aprobadas)
        grupos = list(grupos)
        self.max_creditos = max_creditos
        self.excluidas: List[Tuple[str, str]] = []  # (código, motivo)
        self.cursos: List[Curso] = []
        self.opciones: List[List[Grupo]] = []
        for cod in deseadas:
            c = cursos[cod]
            faltan = [p for p in c.prerrequisitos if p not in aprobadas]
            if faltan:
                self.excluidas.append((cod, "prerrequisito sin aprobar: " + ", ".join(faltan)))
                continue
            ops = [g for g in grupos if g.curso == cod and g.cupo > 0]
            if not ops:
                self.excluidas.append((cod, "sin grupos con cupo"))
                continue
            self.cursos.append(c)
            self.opciones.append(ops)
        self.n = len(self.cursos)
        self._mascaras = [[g.mascara for g in ops] for ops in self.opciones]
        self._dias = [[g.mascara_dias for g in ops] for ops in self.opciones]
        self._base = [[g.costo_base for g in ops] for ops in self.opciones]
        self._hmin = [min(b) for b in self._base]  # grupo más barato de cada curso
        # Mínimo de días: un día tiene 6 franjas, así que con X sesiones se necesitan al menos X/6 días (redondeado hacia arriba)
        sesiones_min = sum(min(len(g.sesiones) for g in ops) for ops in self.opciones)
        self._dias_min = -(-sesiones_min // N_BLOQUES)

    # Formalización del problema
    def estado_inicial(self) -> Tuple[int, ...]:
        """Ningún curso tiene grupo."""
        return (-1,) * self.n

    def _ocupacion(self, s):
        occ = dias = cred = 0
        for i, j in enumerate(s):
            if j >= 0:
                occ |= self._mascaras[i][j]
                dias |= self._dias[i][j]
                cred += self.cursos[i].creditos
        return occ, dias, cred

    def acciones(self, s):
        """Acción (i, j): inscribir el curso i en su grupo j. Solo se permiten las que no cruzan ni pasan el máximo de créditos."""
        occ, _, cred = self._ocupacion(s)
        return [(i, j) for i in range(self.n) if s[i] < 0
                and cred + self.cursos[i].creditos <= self.max_creditos
                for j in range(len(self.opciones[i])) if not (self._mascaras[i][j] & occ)]

    def resultado(self, s, a):
        """Transición: pone el grupo j en la posición i."""
        i, j = a
        return s[:i] + (j,) + s[i + 1:]

    def es_meta(self, s) -> bool:
        """Meta: todos los cursos tienen grupo (las acciones ya garantizan que no hay cruces)."""
        return all(j >= 0 for j in s)

    def costo_paso(self, s, a) -> int:
        """Costo base del grupo + castigo por cada día nuevo que agrega. Nunca es negativo."""
        i, j = a
        _, dias, _ = self._ocupacion(s)
        return self._base[i][j] + PEN_DIA_NUEVO * _bits(self._dias[i][j] & ~dias)

    def sucesores(self, s):
        """Devuelve (acción, estado siguiente, costo). Es lo mismo que acciones + resultado + costo_paso, pero en un solo recorrido."""
        occ, dias, cred = self._ocupacion(s)
        out = []
        for i in range(self.n):
            if s[i] >= 0 or cred + self.cursos[i].creditos > self.max_creditos:
                continue
            for j in range(len(self.opciones[i])):
                if self._mascaras[i][j] & occ:
                    continue
                c = self._base[i][j] + PEN_DIA_NUEVO * _bits(self._dias[i][j] & ~dias)
                out.append(((i, j), s[:i] + (j,) + s[i + 1:], c))
        return out

    # Heurística
    def h(self, s) -> int:
        """Suma del grupo más barato de cada curso pendiente, más el castigo por los días
        que todavía faltan para llegar al mínimo. Ignora cruces y créditos, así que nunca
        sobreestima el costo real (admisible y consistente)."""
        _, dias, _ = self._ocupacion(s)
        base = sum(self._hmin[i] for i in range(self.n) if s[i] < 0)
        return base + PEN_DIA_NUEVO * max(0, self._dias_min - _bits(dias))

    def h_cero(self, s) -> int:
        return 0

    # Utilidades
    def es_valido(self, s) -> bool:
        """Revisa por aparte que no haya cruces ni se pase del máximo de créditos."""
        occ = 0
        cred = 0
        for i, j in enumerate(s):
            if j < 0:
                continue
            if occ & self._mascaras[i][j]:
                return False
            occ |= self._mascaras[i][j]
            cred += self.cursos[i].creditos
        return cred <= self.max_creditos

    def costo_total(self, s) -> int:
        """Costo de un horario completo: costos base + castigo por los días usados."""
        _, dias, _ = self._ocupacion(s)
        base = sum(self._base[i][j] for i, j in enumerate(s) if j >= 0)
        return base + PEN_DIA_NUEVO * _bits(dias)

    def describir(self, s) -> List[str]:
        out = []
        for i, j in enumerate(s):
            if j < 0:
                continue
            g = self.opciones[i][j]
            ses = ", ".join(f"{DIAS[d]} {BLOQUES[b]}" for d, b in g.sesiones)
            out.append(f"{self.cursos[i].codigo:5s} {g.id:7s} {ses}  (cupo {g.cupo})")
        return out
