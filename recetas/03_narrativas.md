# Receta 3 · Anotar narrativas con IA y validarlas con codificación humana

**Para qué sirve:** pasar de "leímos las noticias" a "medimos qué encuadres dominan", con un número de confianza que se puede reportar en el anexo metodológico.

**Pedido típico:** "Anota las noticias del clipping con el codebook" y después "compara con nuestra codificación".

## Pasos para el agente

1. **Corpus.** Usa el CSV de noticias más reciente de `datos/noticias/` (o los párrafos de una transcripción, si el grupo lo pide). Descarta las filas que no son del caso y di cuántas quedaron.
2. **Anotación.** Lee `narrativas/codebook.md` completo. Para cada fila, aplica las variables y crea `datos/anotaciones/anotacion_ia.csv` con estas columnas, en este orden:
   `id, fuente, fecha, texto, encuadre, tono, actor_principal, causa, solucion, cita_textual, certeza`
   - `id`: n001, n002, ... (en el mismo orden del CSV de origen).
   - `texto`: título y resumen tal como vienen en los datos.
   - `encuadre` y `tono`: **solo** valores de la lista cerrada del codebook.
   - `cita_textual`: el fragmento exacto del texto que justifica el encuadre. Si no hay uno claro, deja la celda vacía y pon certeza baja.
   - `certeza`: alta, media o baja.
3. **Muestra para validar.** Corre:
   ```
   python herramientas/concordancia.py muestra --n 20
   ```
   Explica al grupo que deben abrir `datos/anotaciones/validacion_humana.csv` (en Excel o Google Sheets), codificar las columnas vacías **sin mirar** lo que puso la IA, guardar como CSV y avisarte.
4. **Comparación.** Cuando el grupo termine:
   ```
   python herramientas/concordancia.py comparar
   ```
   Lee `salidas/concordancia.md` y explica el resultado en simple: qué variable es confiable (kappa sobre 0,60), cuál no, y qué patrón tienen los desacuerdos (¿la IA confunde dos categorías? ¿la definición del codebook es ambigua?).
5. **Resultados.** Solo con las variables confiables, haz un resumen de distribución (cuántas notas por encuadre, por tono y por actor) en `salidas/AAAA-MM-DD_narrativas.md`, con advertencias de tamaño de muestra.
6. Agrega la entrada en `bitacora_ia.md`.

## Qué debe verificar el equipo

- Que la codificación humana se haga a ciegas y la haga más de una persona si es posible.
- Que el anexo metodológico reporte: tamaño de la muestra, quién codificó, kappa por variable y qué se hizo con las variables poco confiables.
- Que ninguna conclusión del memo dependa de una variable con kappa bajo 0,40.
