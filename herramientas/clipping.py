#!/usr/bin/env python3
"""
Convierte el CSV de noticias del día en un clipping HTML listo para compartir.

Uso:
    python herramientas/clipping.py                       # usa el CSV más reciente de datos/noticias/
    python herramientas/clipping.py --resumen salidas/lectura.md
    python herramientas/clipping.py --csv datos/noticias/2026-11-19_noticias.csv --titulo "Clipping Presupuesto 2027"

--resumen agrega arriba una "Lectura del día" escrita por el agente (y revisada por ustedes) en markdown.
Solo usa la biblioteca estándar de Python.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# En Windows, cuando el agente lee la salida, la consola puede no aceptar tildes ni símbolos
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parent.parent
CASO = RAIZ / "config" / "caso.md"


def titulo_del_caso() -> str:
    if CASO.exists():
        for linea in CASO.read_text(encoding="utf-8").splitlines():
            m = re.match(r"#\s+(.+)", linea)
            if m:
                return m.group(1).strip()
    return "Clipping de prensa"


def md_a_html(texto: str) -> str:
    """Markdown mínimo: párrafos, viñetas, **negrita**, *cursiva* y [enlaces](url)."""
    def inline(t):
        t = html.escape(t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"<em>\1</em>", t)
        t = re.sub(r"\[(.+?)\]\((https?://[^\s)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
        return t
    salida, lista = [], False
    for linea in texto.splitlines():
        l = linea.strip()
        if re.match(r"^[-*]\s+", l):
            if not lista:
                salida.append("<ul>")
                lista = True
            item = re.sub(r"^[-*]\s+", "", l)
            salida.append(f"<li>{inline(item)}</li>")
            continue
        if lista:
            salida.append("</ul>")
            lista = False
        if not l:
            continue
        if l.startswith("#"):
            salida.append(f"<h3>{inline(l.lstrip('#').strip())}</h3>")
        else:
            salida.append(f"<p>{inline(l)}</p>")
    if lista:
        salida.append("</ul>")
    return "\n".join(salida)


CSS = """
:root{--azul:#009FE3;--negro:#15171A;--gris:#5B6168;--linea:#E3E6EA;--fondo:#F6F7F9}
*{box-sizing:border-box}body{margin:0;font-family:Roboto,'Helvetica Neue',Arial,sans-serif;color:var(--negro);background:var(--fondo);line-height:1.5}
header{background:var(--negro);color:#fff;padding:32px 24px}
header .wrap,main{max-width:860px;margin:0 auto}
.kicker{color:var(--azul);font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:12px}
h1{font-size:30px;line-height:1.15;margin:6px 0 10px}
.meta{color:#B8BEC6;font-size:14px}
main{padding:24px}
section{background:#fff;border:1px solid var(--linea);border-radius:10px;padding:20px 22px;margin-bottom:18px}
h2{font-size:18px;margin:0 0 12px}
h3{font-size:16px;margin:16px 0 6px}
.lectura{border-left:4px solid var(--azul)}
.lectura a{color:#0079AD}
.barras{display:grid;grid-template-columns:150px 1fr 36px;gap:6px 10px;align-items:center;font-size:14px}
.barra{height:10px;background:var(--azul);border-radius:5px}
.nota{display:grid;grid-template-columns:120px 1fr;gap:12px;padding:10px 0;border-top:1px solid var(--linea)}
.nota:first-of-type{border-top:0}
.nota .cuando{font-size:13px;color:var(--gris)}
.nota .medio{font-weight:700;font-size:13px;color:var(--negro)}
.nota a{color:var(--negro);text-decoration:none;font-weight:500}
.nota a:hover{color:var(--azul);text-decoration:underline}
.nota .resumen{font-size:14px;color:var(--gris);margin-top:2px}
.chip{display:inline-block;font-size:12px;background:#E6F6FD;color:#00739F;border-radius:999px;padding:1px 9px;margin-right:4px}
footer{max-width:860px;margin:0 auto;padding:0 24px 32px;font-size:12px;color:var(--gris)}
@media(max-width:600px){.nota{grid-template-columns:1fr}.barras{grid-template-columns:100px 1fr 30px}}
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera un clipping HTML desde el CSV de noticias.")
    ap.add_argument("--csv", help="CSV de entrada (por defecto, el más reciente en datos/noticias/)")
    ap.add_argument("--resumen", help="Archivo markdown con la 'Lectura del día' (opcional)")
    ap.add_argument("--titulo", help="Título del clipping (por defecto, el título de config/caso.md)")
    ap.add_argument("--salida", help="Ruta del HTML (por defecto salidas/clipping_AAAA-MM-DD.html)")
    args = ap.parse_args()

    if args.csv:
        ruta_csv = Path(args.csv)
    else:
        candidatos = sorted((RAIZ / "datos" / "noticias").glob("*_noticias.csv"))
        if not candidatos:
            print("No hay noticias descargadas. Corre primero: python herramientas/noticias.py")
            return 1
        ruta_csv = candidatos[-1]

    with ruta_csv.open(encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        print("El CSV está vacío: prueba con más días (--dias 5) o con otras palabras clave.")
        return 1

    titulo = args.titulo or titulo_del_caso()
    hoy = dt.datetime.now()
    por_medio = Counter(r["medio"] for r in filas)
    por_clave = defaultdict(list)
    for r in filas:
        clave = (r.get("palabras_clave") or "Sin clasificar").split(";")[0].strip()
        por_clave[clave].append(r)

    partes = [f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titulo)} · {hoy:%d/%m/%Y}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header><div class="wrap"><div class="kicker">Clipping de prensa</div><h1>{html.escape(titulo)}</h1>
<div class="meta">{hoy:%d/%m/%Y, %H:%M} · {len(filas)} notas · {len(por_medio)} medios</div></div></header><main>"""]

    if args.resumen and Path(args.resumen).exists():
        partes.append(f'<section class="lectura"><h2>Lectura del día</h2>{md_a_html(Path(args.resumen).read_text(encoding="utf-8"))}</section>')

    maximo = max(por_medio.values())
    barras = "".join(
        f'<div>{html.escape(m)}</div><div class="barra" style="width:{max(4, round(100 * n / maximo))}%"></div><div>{n}</div>'
        for m, n in por_medio.most_common(12))
    partes.append(f'<section><h2>¿Quién está cubriendo el tema?</h2><div class="barras">{barras}</div></section>')

    for clave, notas in sorted(por_clave.items(), key=lambda kv: -len(kv[1])):
        partes.append(f'<section><h2>{html.escape(clave)} <span class="chip">{len(notas)}</span></h2>')
        for r in notas:
            texto = r.get("resumen") or ""
            if len(texto) > 220:
                texto = texto[:220].rsplit(" ", 1)[0] + "…"
            resumen = f'<div class="resumen">{html.escape(texto)}</div>' if texto else ""
            partes.append(
                f'<div class="nota"><div><div class="medio">{html.escape(r["medio"])}</div><div class="cuando">{html.escape(r["fecha"])}</div></div>'
                f'<div><a href="{html.escape(r["link"])}" target="_blank" rel="noopener">{html.escape(r["titulo"])}</a>{resumen}</div></div>')
        partes.append("</section>")

    partes.append(f"""</main><footer>Fuentes: Google News y RSS públicos de medios (ver config/fuentes.csv). Archivo base: {html.escape(ruta_csv.name)}.
Generado con el kit de audiencias UAI. La lectura del día fue redactada con IA y revisada por el equipo.</footer></body></html>""")

    salida = Path(args.salida) if args.salida else RAIZ / "salidas" / f"clipping_{hoy:%Y-%m-%d}.html"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text("\n".join(partes), encoding="utf-8")
    print(f"Clipping listo → {salida.relative_to(RAIZ) if salida.is_relative_to(RAIZ) else salida}")
    print("Ábrelo con doble clic o arrástralo al navegador.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
