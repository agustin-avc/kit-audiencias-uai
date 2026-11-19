#!/usr/bin/env python3
"""
Validación humana de la anotación hecha por IA. Dos pasos:

  1) Sacar una muestra al azar para que una persona la codifique a ciegas
     (sin ver lo que respondió la IA):
        python herramientas/concordancia.py muestra --n 20

     Crea datos/anotaciones/validacion_humana.csv con las mismas filas y las columnas de código vacías.

  2) Comparar la codificación humana con la de la IA:
        python herramientas/concordancia.py comparar

     Calcula, para cada variable, el porcentaje de acuerdo y el kappa de Cohen,
     y lista los desacuerdos. Escribe el informe en salidas/concordancia.md
     (va directo al anexo metodológico del trabajo).

Solo usa la biblioteca estándar de Python.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import random
import sys
import unicodedata
from collections import Counter
from pathlib import Path

# En Windows, cuando el agente lee la salida, la consola puede no aceptar tildes ni símbolos
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parent.parent
ANOT = RAIZ / "datos" / "anotaciones"
IA_POR_DEFECTO = ANOT / "anotacion_ia.csv"
HUMANO_POR_DEFECTO = ANOT / "validacion_humana.csv"
VARIABLES_POR_DEFECTO = ["encuadre", "tono", "actor_principal"]
COLUMNAS_CONTEXTO = ["id", "fuente", "fecha", "texto"]


def norm(v: str) -> str:
    v = unicodedata.normalize("NFKD", (v or "").strip().lower())
    return "".join(c for c in v if not unicodedata.combining(c)).replace(" ", "_")


def leer(ruta: Path) -> list[dict]:
    if not ruta.exists():
        sys.exit(f"No existe {ruta.relative_to(RAIZ) if ruta.is_relative_to(RAIZ) else ruta}. "
                 "Revisa la receta recetas/03_narrativas.md.")
    with ruta.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def kappa(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    if pe == 1:
        return 1.0 if po == 1 else 0.0
    return (po - pe) / (1 - pe)


def lectura(k: float | None) -> str:
    """Escala de Landis y Koch (1977), la más citada para reportar kappa."""
    if k is None:
        return "sin datos"
    if k < 0:
        return "peor que el azar"
    for limite, txt in [(0.20, "leve"), (0.40, "regular"), (0.60, "moderado"), (0.80, "sustancial"), (1.01, "casi perfecto")]:
        if k <= limite:
            return txt
    return "casi perfecto"


def cmd_muestra(args) -> int:
    filas = leer(Path(args.ia))
    variables = args.variables or [v for v in VARIABLES_POR_DEFECTO if filas and v in filas[0]]
    random.seed(args.semilla)
    n = min(args.n, len(filas))
    muestra = random.sample(filas, n)
    contexto = [c for c in COLUMNAS_CONTEXTO if filas and c in filas[0]]
    salida = Path(args.salida)
    if salida.exists() and not args.forzar:
        sys.exit(f"{salida.name} ya existe. Si quieres reemplazarlo, agrega --forzar (perderás lo ya codificado).")
    with salida.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=contexto + variables + ["comentario"])
        w.writeheader()
        for r in muestra:
            w.writerow({**{c: r.get(c, "") for c in contexto}, **{v: "" for v in variables}, "comentario": ""})
    print(f"Muestra de {n} filas (semilla {args.semilla}) → {salida.relative_to(RAIZ) if salida.is_relative_to(RAIZ) else salida}")
    print("Ábrela en Excel o Google Sheets y codifica SIN mirar la columna de la IA. Usa las categorías de narrativas/codebook.md.")
    return 0


def cmd_comparar(args) -> int:
    ia = {r["id"]: r for r in leer(Path(args.ia))}
    humano = [r for r in leer(Path(args.humano)) if r.get("id") in ia]
    variables = args.variables or [v for v in VARIABLES_POR_DEFECTO if humano and v in humano[0]]
    if not humano:
        sys.exit("No hay filas en común entre la anotación de la IA y la humana (revisa la columna id).")

    lineas = ["# Concordancia entre la anotación con IA y la codificación humana", "",
              f"- Fecha: {dt.datetime.now():%d/%m/%Y}",
              f"- Archivo IA: `{Path(args.ia).name}` · Archivo humano: `{Path(args.humano).name}`",
              f"- Unidades comparadas: {len(humano)}",
              "- Medidas: porcentaje de acuerdo y kappa de Cohen (corrige el acuerdo esperable por azar). "
              "Lectura según Landis y Koch (1977).", "",
              "| Variable | n | % acuerdo | Kappa | Lectura |", "|---|---|---|---|---|"]
    desacuerdos = []
    print(f"{'Variable':<18}{'n':>4}{'% acuerdo':>11}{'kappa':>8}  lectura")
    for v in variables:
        pares = [(norm(ia[r["id"]].get(v, "")), norm(r.get(v, "")), r["id"]) for r in humano]
        pares = [p for p in pares if p[1]]  # solo filas que la persona sí codificó
        a, b = [p[0] for p in pares], [p[1] for p in pares]
        n = len(pares)
        acuerdo = sum(x == y for x, y in zip(a, b)) / n if n else 0
        k = kappa(a, b)
        ktxt = f"{k:.2f}" if k is not None else "s/d"
        print(f"{v:<18}{n:>4}{acuerdo:>10.0%}{ktxt:>8}  {lectura(k)}")
        lineas.append(f"| {v} | {n} | {acuerdo:.0%} | {ktxt} | {lectura(k)} |")
        desacuerdos += [(i, v, x, y) for x, y, i in pares if x != y]

    lineas += ["", "## Desacuerdos para revisar", ""]
    if desacuerdos:
        lineas += ["| id | Variable | IA | Humano |", "|---|---|---|---|"]
        lineas += [f"| {i} | {v} | {x} | {y} |" for i, v, x, y in desacuerdos]
    else:
        lineas.append("Sin desacuerdos.")
    lineas += ["", "## Cómo reportarlo en el anexo metodológico", "",
               "Indiquen el tamaño de la muestra, quién codificó, si lo hizo sin ver la respuesta de la IA, "
               "el kappa por variable y qué hicieron con las variables bajo 0,60 (redefinir la categoría en el codebook, "
               "volver a anotar o no usarla para conclusiones)."]
    salida = RAIZ / "salidas" / "concordancia.md"
    salida.write_text("\n".join(lineas), encoding="utf-8")
    print(f"\n{len(desacuerdos)} desacuerdos. Informe → salidas/concordancia.md")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Validación humana de anotaciones hechas con IA.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("muestra", help="Crear muestra a ciegas para codificación humana")
    m.add_argument("--ia", default=str(IA_POR_DEFECTO))
    m.add_argument("--n", type=int, default=20)
    m.add_argument("--semilla", type=int, default=2026, help="Semilla para que la muestra sea reproducible")
    m.add_argument("--variables", nargs="*")
    m.add_argument("--salida", default=str(HUMANO_POR_DEFECTO))
    m.add_argument("--forzar", action="store_true")
    c = sub.add_parser("comparar", help="Comparar IA y humano")
    c.add_argument("--ia", default=str(IA_POR_DEFECTO))
    c.add_argument("--humano", default=str(HUMANO_POR_DEFECTO))
    c.add_argument("--variables", nargs="*")
    args = ap.parse_args()
    return cmd_muestra(args) if args.cmd == "muestra" else cmd_comparar(args)


if __name__ == "__main__":
    sys.exit(main())
