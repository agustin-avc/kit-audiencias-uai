# Receta 4 · Tablero para compartir (opcional)

**Para qué sirve:** mostrar los hallazgos en una sola página que se abre en el navegador y se puede adjuntar o proyectar en la presentación final.

**Pedido típico:** "Arma un tablero con lo que tenemos".

## Pasos para el agente

1. Revisa qué hay en `datos/` y `salidas/`: noticias, anotaciones validadas, concordancia, resúmenes de video.
2. Propón al grupo, en una lista corta, qué mostrarás (máximo 4 gráficos o tablas) y espera su visto bueno. Sugerencias:
   - Notas por día y por medio.
   - Distribución de encuadres (solo si su kappa es aceptable).
   - Actores más mencionados.
   - 3 a 5 citas clave con su fuente.
3. Construye **un solo archivo** `salidas/tablero.html` que funcione sin internet ni instalación (todo el código y los datos dentro del archivo; gráficos con SVG o HTML simple).
4. Cada gráfico lleva título, fuente de los datos, fecha de corte y tamaño de la muestra.
5. Agrega una sección final "Cómo se hizo" con el método en 4 líneas y el kappa de cada variable usada.
6. Agrega la entrada en `bitacora_ia.md`.

## Qué debe verificar el equipo

- Que cada número del tablero coincida con los archivos de `datos/`.
- Que el tablero no muestre nada que contradiga las reglas del curso (personas privadas, datos personales).
