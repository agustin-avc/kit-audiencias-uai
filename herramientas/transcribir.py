#!/usr/bin/env python3
"""
Obtiene la transcripción de un video público y la guarda ordenada, con marcas de tiempo,
en datos/transcripciones/. Tiene tres caminos, de más a menos automático:

  1) Desde un link de YouTube (usa los subtítulos que YouTube ya generó):
        python herramientas/transcribir.py --url "https://www.youtube.com/watch?v=XXXXXXXXXXX"
     Requiere instalar una vez:  pip install youtube-transcript-api

  2) Desde texto copiado a mano del panel "Mostrar transcripción" de YouTube
     (plan B si el camino 1 falla, por ejemplo porque YouTube bloquea la red de la universidad):
        python herramientas/transcribir.py --pegado datos/transcripciones/pegado.txt --url "https://www.youtube.com/watch?v=XXXXXXXXXXX"

  3) Desde un archivo de subtítulos .vtt o .srt:
        python herramientas/transcribir.py --subtitulos archivo.vtt --titulo "Debate Senado"

Resultado: un markdown con párrafos de ~60 segundos, cada uno con su minuto y un link
que abre el video en ese punto (útil para citar con precisión).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# En Windows, cuando el agente lee la salida, la consola puede no aceptar tildes ni símbolos
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "datos" / "transcripciones"


def id_de_video(url: str | None) -> str | None:
    if not url:
        return None
    m = re.search(r"(?:v=|youtu\.be/|shorts/|live/|embed/)([A-Za-z0-9_-]{11})", url)
    if m:
        return m.group(1)
    return url if re.fullmatch(r"[A-Za-z0-9_-]{11}", url) else None


def metadatos(video_id: str) -> dict:
    """Título y canal vía oEmbed (público, sin llave)."""
    try:
        url = "https://www.youtube.com/oembed?" + urllib.parse.urlencode(
            {"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"})
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
            return {"titulo": d.get("title", ""), "canal": d.get("author_name", "")}
    except Exception:
        return {}


def a_segundos(marca: str) -> float:
    partes = [float(p.replace(",", ".")) for p in marca.split(":")]
    s = 0.0
    for p in partes:
        s = s * 60 + p
    return s


def mmss(seg: float) -> str:
    seg = int(seg)
    h, r = divmod(seg, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


# ---------- Camino 1: API de subtítulos de YouTube ----------
def desde_youtube(video_id: str) -> list[tuple[float, str]]:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        sys.exit("Falta una librería. Instálala una vez con:  pip install youtube-transcript-api\n"
                 "(o pídele al agente que la instale). Luego vuelve a correr este comando.")
    idiomas = ["es", "es-419", "es-CL", "es-ES", "es-MX"]
    try:
        api = YouTubeTranscriptApi()
        if hasattr(api, "fetch"):  # versión 1.x
            datos = api.fetch(video_id, languages=idiomas)
            return [(s.start, s.text) for s in datos.snippets]
        datos = YouTubeTranscriptApi.get_transcript(video_id, languages=idiomas)  # versiones antiguas
        return [(d["start"], d["text"]) for d in datos]
    except Exception as e:
        nombre = type(e).__name__
        print(f"\nNo se pudo obtener la transcripción automática ({nombre}).", file=sys.stderr)
        print("Plan B, que siempre funciona:\n"
              "  1. Abre el video en YouTube, haz clic en '...más' bajo el video y luego en 'Mostrar transcripción'.\n"
              "  2. Selecciona todo el texto del panel, cópialo y pégalo en datos/transcripciones/pegado.txt\n"
              f"  3. Corre: python herramientas/transcribir.py --pegado datos/transcripciones/pegado.txt --url {video_id}",
              file=sys.stderr)
        sys.exit(2)


# ---------- Camino 2: texto pegado desde el panel de YouTube ----------
MARCA = re.compile(r"^\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*(.*)$")
ETIQUETA_ACCESIBLE = re.compile(r"^\d+\s+(segundos?|minutos?|horas?)(,?\s*(y\s+)?\d+\s+(segundos?|minutos?))*$", re.I)


def desde_pegado(texto: str) -> list[tuple[float, str]]:
    segmentos: list[tuple[float, str]] = []
    actual_t, actual_txt = None, []
    for linea in texto.splitlines():
        l = linea.strip()
        if not l or ETIQUETA_ACCESIBLE.match(l):
            continue
        m = MARCA.match(l)
        if m:
            if actual_t is not None and actual_txt:
                segmentos.append((actual_t, " ".join(actual_txt)))
            actual_t, actual_txt = a_segundos(m.group(1)), ([m.group(2)] if m.group(2) else [])
        elif actual_t is not None:
            actual_txt.append(l)
    if actual_t is not None and actual_txt:
        segmentos.append((actual_t, " ".join(actual_txt)))
    return segmentos


# ---------- Camino 3: archivos .vtt / .srt ----------
TIEMPO = re.compile(r"(\d{1,2}:)?\d{2}:\d{2}[.,]\d{3}\s*-->")


def desde_subtitulos(texto: str) -> list[tuple[float, str]]:
    segmentos, t, buf = [], None, []
    for linea in texto.splitlines():
        l = linea.strip()
        if TIEMPO.search(l):
            if t is not None and buf:
                segmentos.append((t, " ".join(buf)))
            t, buf = a_segundos(l.split("-->")[0].strip()), []
        elif not l or l.isdigit() or l.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        elif t is not None:
            buf.append(re.sub(r"<[^>]+>", "", l))
    if t is not None and buf:
        segmentos.append((t, " ".join(buf)))
    # Los subtítulos automáticos repiten líneas: se quitan duplicados consecutivos
    limpio = []
    for t, txt in segmentos:
        if not limpio or txt != limpio[-1][1]:
            limpio.append((t, txt))
    return limpio


def agrupar(segmentos: list[tuple[float, str]], cada: int = 60) -> list[tuple[float, str]]:
    bloques, inicio, buf = [], None, []
    for t, txt in segmentos:
        txt = re.sub(r"\s+", " ", txt.replace("\n", " ")).strip()
        if not txt:
            continue
        if inicio is None:
            inicio = t
        if t - inicio >= cada and buf:
            bloques.append((inicio, " ".join(buf)))
            inicio, buf = t, []
        buf.append(txt)
    if buf:
        bloques.append((inicio, " ".join(buf)))
    return bloques


def nombre_archivo(texto: str) -> str:
    import unicodedata
    texto = "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))
    texto = re.sub(r"[^\w\s-]", "", texto.lower(), flags=re.UNICODE)
    return re.sub(r"[\s_-]+", "_", texto).strip("_")[:60] or "transcripcion"


def main() -> int:
    ap = argparse.ArgumentParser(description="Transcripción ordenada de un video público.")
    ap.add_argument("--url", help="Link o ID del video de YouTube")
    ap.add_argument("--pegado", help="Archivo .txt con el texto copiado del panel 'Mostrar transcripción'")
    ap.add_argument("--subtitulos", help="Archivo .vtt o .srt")
    ap.add_argument("--titulo", help="Título (si no, se obtiene de YouTube)")
    ap.add_argument("--cada", type=int, default=60, help="Segundos por párrafo (por defecto 60)")
    args = ap.parse_args()

    vid = id_de_video(args.url)
    if args.pegado:
        segmentos = desde_pegado(Path(args.pegado).read_text(encoding="utf-8"))
        via = "texto copiado del panel de transcripción de YouTube"
    elif args.subtitulos:
        segmentos = desde_subtitulos(Path(args.subtitulos).read_text(encoding="utf-8", errors="ignore"))
        via = f"archivo de subtítulos {Path(args.subtitulos).name}"
    elif vid:
        segmentos = desde_youtube(vid)
        via = "subtítulos de YouTube (youtube-transcript-api)"
    else:
        ap.print_help()
        return 1

    if not segmentos:
        print("No se encontró texto con marcas de tiempo. Revisa que copiaste el panel completo, incluidos los minutos.")
        return 1

    meta = metadatos(vid) if vid else {}
    titulo = args.titulo or meta.get("titulo") or (f"Video {vid}" if vid else "Transcripción")
    bloques = agrupar(segmentos, args.cada)
    duracion = segmentos[-1][0]

    lineas = [f"# {titulo}", "",
              f"- **Canal:** {meta.get('canal', 'sin dato')}",
              f"- **Link:** https://www.youtube.com/watch?v={vid}" if vid else "- **Link:** sin dato",
              f"- **Duración aproximada:** {mmss(duracion)}",
              f"- **Obtenida desde:** {via}",
              f"- **Fecha de descarga:** {dt.datetime.now():%d/%m/%Y %H:%M}",
              "- **Advertencia:** transcripción automática; puede tener errores en nombres propios y cifras. Verificar contra el video antes de citar.",
              "", "---", ""]
    for t, txt in bloques:
        enlace = f" ([ver](https://www.youtube.com/watch?v={vid}&t={int(t)}s))" if vid else ""
        lineas.append(f"**[{mmss(t)}]**{enlace} {txt}\n")

    SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = SALIDA / f"{dt.datetime.now():%Y-%m-%d}_{nombre_archivo(titulo)}.md"
    ruta.write_text("\n".join(lineas), encoding="utf-8")
    palabras = sum(len(t.split()) for _, t in bloques)
    print(f"Listo: {len(bloques)} párrafos, {palabras:,} palabras → {ruta.relative_to(RAIZ)}".replace(",", "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
