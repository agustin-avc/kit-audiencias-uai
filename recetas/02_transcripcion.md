# Receta 2 · Transcribir y resumir un video

**Para qué sirve:** convertir un debate, una sesión del Congreso, una entrevista o un punto de prensa en texto citable, con el minuto exacto de cada intervención.

**Pedido típico:** "Transcribe y resume este video: https://www.youtube.com/watch?v=..."

## Pasos para el agente

1. Intenta la vía automática:
   ```
   python herramientas/transcribir.py --url "LINK_DEL_VIDEO"
   ```
   Si dice que falta una librería, instálala con `pip install youtube-transcript-api` (o `pip3`, o `python -m pip install ...`) y repite.
2. **Si falla** (YouTube a veces bloquea redes compartidas, como la wifi de una universidad), usa el plan B y explícaselo al grupo:
   - En YouTube, bajo el video: "...más" → "Mostrar transcripción".
   - Seleccionar todo el texto del panel, copiarlo y pegarlo en `datos/transcripciones/pegado.txt`.
   - Correr: `python herramientas/transcribir.py --pegado datos/transcripciones/pegado.txt --url "LINK_DEL_VIDEO"`
3. Lee la transcripción generada en `datos/transcripciones/` y escribe un resumen en `salidas/AAAA-MM-DD_resumen_<tema>.md` con:
   - **Ficha:** título, canal, fecha, link, duración.
   - **Síntesis** en 5 líneas.
   - **Quién habla:** actores que intervienen y su posición en una línea cada uno. Si la transcripción no dice quién habla, indícalo como inferencia y con certeza baja.
   - **Citas clave:** 5 citas **textuales** copiadas de la transcripción, cada una con su minuto y el link `&t=` que ya viene en el archivo. Nunca corrijas ni completes una cita: si la transcripción tiene un error evidente, ponlo igual y anótalo con [sic].
   - **Encuadres y narrativa:** actor, conflicto, causa y solución que propone cada lado (ver `narrativas/codebook.md`).
   - **Cruce con prensa (opcional):** si hay un clipping del mismo período, compara cómo se contó el mismo hecho en el video y en los medios. ¿Qué frase saltó a los titulares? ¿Qué se perdió?
4. Agrega la entrada en `bitacora_ia.md`.

## Qué debe verificar el equipo

- Escuchar en el video cada cita antes de usarla en el memo (los subtítulos automáticos fallan con nombres propios, siglas y cifras).
- No atribuir una frase a alguien si en el video no se ve o escucha claramente quién la dice.
