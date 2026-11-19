# Codebook de encuadres y narrativas

Este es el libro de códigos que usan la IA y el equipo para anotar cada unidad (una noticia: título y bajada; o un párrafo de transcripción). Para que el kappa tenga sentido, **la IA y las personas deben usar exactamente estas categorías**. Si el grupo cambia una definición, la cambia aquí y vuelve a anotar.

## 1. `encuadre` (lista cerrada, se elige UNA)

Basado en los cinco encuadres genéricos de Semetko y Valkenburg (2000), muy usados para estudiar cobertura política.

| Valor | Se usa cuando la unidad... | Pregunta de decisión |
|---|---|---|
| `conflicto` | pone el foco en el desacuerdo entre personas, partidos, poderes o grupos: quién gana, quién pierde, quién ataca a quién | ¿El centro es la pelea? |
| `responsabilidad` | atribuye a alguien (gobierno, institución, persona) la causa de un problema o la obligación de resolverlo | ¿El centro es quién tiene la culpa o quién debe actuar? |
| `consecuencias_economicas` | pone el foco en costos, montos, efectos en el bolsillo, el empleo o el crecimiento | ¿El centro son los pesos y sus efectos? |
| `interes_humano` | cuenta el tema a través de una persona, una familia o un caso concreto, apelando a la emoción | ¿El centro es una historia personal? |
| `moralidad` | lo presenta como cuestión de principios, valores, justicia o ética | ¿El centro es lo correcto o lo incorrecto? |
| `otro` | es descriptivo o informativo sin un encuadre claro de los anteriores | Ninguna de las anteriores domina |

**Regla de desempate:** si caben dos, elige el que aparece en el **título**. Si los dos están en el título, elige el primero de la tabla.

## 2. `tono` (lista cerrada, hacia el actor principal)

| Valor | Criterio |
|---|---|
| `positivo` | El actor principal aparece logrando algo, con apoyo o elogio |
| `negativo` | Aparece criticado, perdiendo, acusado o en problemas |
| `neutro` | Información sin valoración, o valoraciones equilibradas |

## 3. `actor_principal` (texto, forma normalizada)

El actor (persona pública, institución, partido o grupo) que protagoniza la unidad. Escribirlo siempre igual, en su forma más corta reconocible: `Gobierno`, `Ministerio de Hacienda`, `Senado`, `Cámara de Diputados`, `Oposición`, `Gremios`, `Estudiantes`. El grupo puede fijar su propia lista en `config/caso.md` (sección Notas).

## 4. Narrativa (texto libre, no entra en el kappa)

La estructura que se vio en clase: **actor, conflicto, causa y solución**.

- `causa`: a qué o a quién atribuye el problema la unidad, en pocas palabras. Vacío si no lo dice.
- `solucion`: qué salida propone o sugiere. Vacío si no lo dice.

## 5. Evidencia y certeza

- `cita_textual`: fragmento **exacto** del texto que justifica el encuadre. Es la principal defensa contra las alucinaciones: si la IA no puede señalar el fragmento, el código es débil.
- `certeza`: `alta` (el encuadre es evidente en el título), `media` (se infiere de la bajada), `baja` (dudoso o con poco texto).

## Ejemplos ilustrativos (inventados para explicar el criterio)

| Texto | encuadre | tono | actor_principal |
|---|---|---|---|
| "Oposición acusa al ministro de esconder recortes en salud" | `conflicto` | `negativo` | `Ministerio de Hacienda` |
| "El ajuste dejaría sin financiamiento a 40 programas sociales" | `consecuencias_economicas` | `neutro` | `Gobierno` |
| "Madre de Iquique espera hace dos años su operación: el hospital no llega" | `interes_humano` | `negativo` | `Gobierno` |

## Referencia

Semetko, H. A., y Valkenburg, P. M. (2000). Framing European politics: A content analysis of press and television news. *Journal of Communication, 50*(2), 93–109.
