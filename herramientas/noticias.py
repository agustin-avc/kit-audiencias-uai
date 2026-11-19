#!/usr/bin/env python3
"""
Descarga noticias desde Google News y desde los RSS de medios chilenos,
filtra por palabras clave y guarda el resultado en datos/noticias/.

Uso básico (lee las palabras clave de config/caso.md):
    python herramientas/noticias.py

Uso con palabras clave en la línea de comandos:
    python herramientas/noticias.py --q "reforma de pensiones" --q "AFP" --dias 3

Solo usa la biblioteca estándar de Python: no hay que instalar nada.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import email.utils
import html
import json
import random
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# En Windows, cuando el agente lee la salida, la consola puede no aceptar tildes ni símbolos
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parent.parent
CASO = RAIZ / "config" / "caso.md"
FUENTES = RAIZ / "config" / "fuentes.csv"
SALIDA = RAIZ / "datos" / "noticias"
UA = "Mozilla/5.0 (kit-audiencias-uai; uso academico)"


def normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para comparar palabras clave."""
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c)).lower()


def limpiar_html(texto: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", texto or "")
    return re.sub(r"\s+", " ", html.unescape(texto)).strip()


def leer_palabras_clave() -> list[str]:
    """Lee la sección '## Palabras clave' de config/caso.md (una por línea, con '- ' o '* ')."""
    if not CASO.exists():
        return []
    claves, dentro = [], False
    for linea in CASO.read_text(encoding="utf-8").splitlines():
        if linea.strip().lower().startswith("## palabras clave"):
            dentro = True
            continue
        if dentro and linea.startswith("## "):
            break
        if dentro:
            m = re.match(r"\s*[-*]\s+(.+)", linea)
            if m and not m.group(1).strip().startswith("("):
                claves.append(m.group(1).strip().strip('"'))
    return claves


def leer_fuentes() -> list[dict]:
    if not FUENTES.exists():
        return []
    with FUENTES.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("activo", "si").strip().lower() in ("si", "sí", "1", "true")]


def descargar(url: str, timeout: int = 20, intentos: int = 3) -> bytes | None:
    """Descarga con reintentos. Si muchas personas consultan Google News desde la
    misma red (por ejemplo, una sala de clases), Google puede responder 429
    ("demasiadas solicitudes"): se espera un poco y se reintenta."""
    for intento in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and intento < intentos - 1:
                espera = 4 * (intento + 1) + random.uniform(0, 3)
                print(f"  … {e.code} en {url[:50]}: reintento en {espera:.0f} s", file=sys.stderr)
                time.sleep(espera)
                continue
            print(f"  ! No se pudo leer {url[:80]}: {e}", file=sys.stderr)
        except Exception as e:  # una fuente caída no debe botar todo
            print(f"  ! No se pudo leer {url[:80]}: {e}", file=sys.stderr)
        return None
    return None


def fecha_de(texto: str | None) -> dt.datetime | None:
    if not texto:
        return None
    try:
        d = email.utils.parsedate_to_datetime(texto)
    except Exception:
        try:
            d = dt.datetime.fromisoformat(texto.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d


def parsear_rss(contenido: bytes, medio_por_defecto: str) -> list[dict]:
    items = []
    try:
        raiz = ET.fromstring(contenido)
    except ET.ParseError:
        return items
    for it in raiz.iter("item"):
        titulo = limpiar_html(it.findtext("title"))
        link = (it.findtext("link") or "").strip()
        resumen = limpiar_html(it.findtext("description"))
        fuente = it.find("source")
        medio = fuente.text.strip(" -–—\t") if fuente is not None and fuente.text else medio_por_defecto
        # Google News pone " - Medio" al final del título
        if medio_por_defecto == "Google News":
            titulo = re.sub(r"\s+[-–—]\s+" + re.escape(medio) + r"\s*$", "", titulo)
        # En Google News la "descripción" solo repite el título: se descarta
        if normalizar(resumen).startswith(normalizar(titulo)[:40]):
            resumen = ""
        items.append({
            "fecha": fecha_de(it.findtext("pubDate")),
            "medio": medio,
            "titulo": titulo,
            "resumen": resumen[:400],
            "link": link,
        })
    return items


def url_google_news(q: str, dias: int) -> str:
    consulta = f'"{q}" when:{dias}d' if " " in q else f"{q} when:{dias}d"
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": consulta, "hl": "es-419", "gl": "CL", "ceid": "CL:es-419"})


def main() -> int:
    ap = argparse.ArgumentParser(description="Descarga y filtra noticias por palabras clave.")
    ap.add_argument("--q", action="append", help="Palabra clave (se puede repetir). Si no se da, se lee config/caso.md")
    ap.add_argument("--dias", type=int, default=2, help="Ventana de días hacia atrás (por defecto 2)")
    ap.add_argument("--sin-google", action="store_true", help="No consultar Google News")
    ap.add_argument("--sin-medios", action="store_true", help="No consultar los RSS de config/fuentes.csv")
    ap.add_argument("--max-por-clave", type=int, default=40, help="Máximo de noticias de Google News por palabra clave")
    args = ap.parse_args()

    claves = args.q or leer_palabras_clave()
    if not claves:
        print("No hay palabras clave. Escríbelas en config/caso.md (sección '## Palabras clave') o usa --q.")
        return 1

    ahora = dt.datetime.now(dt.timezone.utc)
    desde = ahora - dt.timedelta(days=args.dias)
    claves_norm = [(c, normalizar(c)) for c in claves]
    print(f"Buscando {len(claves)} palabra(s) clave en los últimos {args.dias} día(s)...")

    encontrados: dict[str, dict] = {}

    def registrar(item: dict, clave: str, origen: str):
        if item["fecha"] and item["fecha"] < desde:
            return
        llave = normalizar(item["titulo"])[:90]
        if not llave:
            return
        if llave in encontrados:
            if clave not in encontrados[llave]["palabras_clave"]:
                encontrados[llave]["palabras_clave"].append(clave)
            return
        item = dict(item, palabras_clave=[clave], origen=origen)
        encontrados[llave] = item

    if not args.sin_google:
        for i, (clave, _) in enumerate(claves_norm):
            if i:
                time.sleep(1.5)  # pausa corta para no saturar a Google News
            contenido = descargar(url_google_news(clave, args.dias))
            if contenido:
                items = parsear_rss(contenido, "Google News")[: args.max_por_clave]
                for it in items:
                    registrar(it, clave, "Google News")
                print(f"  Google News · {clave}: {len(items)} resultados")

    if not args.sin_medios:
        for fuente in leer_fuentes():
            contenido = descargar(fuente["url_rss"])
            if not contenido:
                continue
            n = 0
            for it in parsear_rss(contenido, fuente["medio"]):
                texto = normalizar(it["titulo"] + " " + it["resumen"])
                for clave, cn in claves_norm:
                    if cn in texto:
                        registrar(it, clave, "RSS del medio")
                        n += 1
            print(f"  {fuente['medio']}: {n} coincidencias")

    if not encontrados:
        print("\nNo se encontró ninguna noticia. Si apareció el error 429, Google News está limitando a esta red:\n"
              "espera unos minutos, usa --sin-google para consultar solo los medios, o trabaja con el ejemplo:\n"
              "  python herramientas/clipping.py --csv datos/ejemplo/noticias_ejemplo.csv")
        return 1

    filas = sorted(encontrados.values(), key=lambda r: r["fecha"] or desde, reverse=True)
    SALIDA.mkdir(parents=True, exist_ok=True)
    hoy = dt.datetime.now().strftime("%Y-%m-%d")
    ruta_csv = SALIDA / f"{hoy}_noticias.csv"
    ruta_json = SALIDA / f"{hoy}_noticias.json"
    campos = ["fecha", "medio", "titulo", "resumen", "link", "palabras_clave", "origen"]
    with ruta_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in filas:
            w.writerow({**{k: r.get(k, "") for k in campos},
                        "fecha": r["fecha"].astimezone().strftime("%Y-%m-%d %H:%M") if r["fecha"] else "",
                        "palabras_clave": "; ".join(r["palabras_clave"])})
    meta = {
        "generado": ahora.isoformat(timespec="seconds"),
        "palabras_clave": claves,
        "dias": args.dias,
        "total": len(filas),
        "por_medio": {},
    }
    for r in filas:
        meta["por_medio"][r["medio"]] = meta["por_medio"].get(r["medio"], 0) + 1
    ruta_json.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nListo: {len(filas)} noticias únicas → {ruta_csv.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
