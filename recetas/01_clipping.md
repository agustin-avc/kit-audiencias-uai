# Receta 1 · Clipping de prensa

**Para qué sirve:** tener en minutos qué se publicó sobre el caso, quién lo está cubriendo y con qué encuadre. Es el insumo base para el memo.

**Pedido típico:** "Haz el clipping de hoy" o "Haz el clipping de los últimos 5 días".

## Pasos para el agente

1. Lee `config/caso.md` y confirma en una línea qué palabras clave vas a usar y cuántos días hacia atrás.
2. Descarga las noticias:
   ```
   python herramientas/noticias.py --dias 3
   ```
   (Ajusta `--dias` al período del caso. Si hay menos de 10 noticias, sugiere ampliar los días o las palabras clave.)
3. Abre el CSV que se generó en `datos/noticias/` y revísalo:
   - Marca las notas que **no son del caso** (otros países, homónimos, temas que solo comparten una palabra). No las borres del CSV: menciónalas en la lectura como ruido.
   - Identifica los 3 a 5 hechos o temas principales.
4. Escribe la "Lectura del día" en `salidas/AAAA-MM-DD_lectura.md`, con 5 a 8 viñetas cortas. Cada viñeta parte con **Dato:**, **Interpretación:** o **Pregunta abierta:** y lleva su fuente como link `[Medio](url)`. Incluye:
   - Qué pasó (los hechos principales).
   - Quién está instalando la agenda (qué actores aparecen como protagonistas o fuentes).
   - Encuadre dominante (conflicto, responsabilidad, consecuencias económicas, interés humano, moralidad; ver `narrativas/codebook.md`).
   - Qué medios cubren más y cuáles no aparecen.
   - Qué ruido encontraste y cuánto pesa.
5. Genera el clipping con la lectura incluida:
   ```
   python herramientas/clipping.py --resumen salidas/AAAA-MM-DD_lectura.md
   ```
6. Dile al grupo dónde quedó el HTML (`salidas/clipping_AAAA-MM-DD.html`) y que lo abran con doble clic.
7. Agrega la entrada en `bitacora_ia.md`.

## Qué debe verificar el equipo

- Abrir al menos 3 links y confirmar que la lectura dice lo que dicen las notas.
- Revisar si faltan medios relevantes para su caso (se agregan en `config/fuentes.csv`).
- Recordar que Google News ordena y filtra con su propio algoritmo: el clipping **no es una muestra representativa** de toda la prensa.
