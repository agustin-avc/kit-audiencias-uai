# Kit de audiencias y narrativas · UAI

Plantilla de trabajo para el curso **Comunicación Digital y Audiencias (PER514)** del Magíster en Comunicación Política y Asuntos Públicos, Universidad Adolfo Ibáñez, 2026.

Convierte a un agente de IA (Claude Code o Codex) en un asistente de investigación que ya sabe hacer cuatro cosas, con reglas de rigor y ética incorporadas:

1. **Clipping de prensa** desde Google News y RSS de medios chilenos.
2. **Transcripciones** de debates, sesiones o entrevistas en YouTube, con el minuto de cada cita.
3. **Anotación de narrativas** con un codebook y validación humana (kappa de Cohen).
4. **Tablero** para compartir los hallazgos.

Todo queda registrado en una **bitácora de uso de IA**, que es parte de la entrega del trabajo grupal.

## Empezar en 3 pasos

Necesitan: Python, git, y Claude Code o Codex instalados (ver la guía de instalación del curso).

**1. Descargar el kit.** Abran la terminal y escriban (una línea a la vez):

```
cd Desktop
git clone https://github.com/agustin-avc/kit-audiencias-uai.git
cd kit-audiencias-uai
```

Sin git: botón verde **Code → Download ZIP**, descomprimir en el Escritorio y abrir la terminal en esa carpeta.

**2. Abrir el agente dentro de la carpeta.**

```
claude
```
o, si usan ChatGPT:
```
codex
```

**3. Primer pedido.** Escríbanle al agente:

> Lee este repositorio y explícame en simple qué puedes hacer y cómo está organizado.

Después:

> Haz el clipping de los últimos 7 días.

## Cómo está organizado

```
AGENTS.md            Instrucciones para el agente (Codex lo lee directo)
CLAUDE.md            Importa AGENTS.md para que Claude Code lea lo mismo
config/caso.md       EL CASO DE SU GRUPO: actor, pregunta, palabras clave
config/fuentes.csv   Medios con RSS que se consultan
recetas/             Procedimientos paso a paso (clipping, transcripción, narrativas, tablero)
herramientas/        Programas en Python ya probados
narrativas/          Codebook de encuadres
datos/               Lo descargado
salidas/             Lo que se comparte o entrega
bitacora_ia.md       Registro obligatorio de uso de IA
```

## Para el trabajo grupal

1. Una persona del grupo entra a esta página en GitHub, aprieta **Use this template → Create a new repository**, le pone el nombre del caso y lo deja **privado**.
2. En **Settings → Collaborators** invita a sus compañeros.
3. Cada integrante clona el repositorio del grupo (paso 1, con el link nuevo).
4. Le piden al agente: *"Ayúdanos a completar config/caso.md con nuestro caso"*.
5. Cada vez que avancen: *"Guarda el avance"* (el agente hace commit y push).

## Reglas

Solo fuentes públicas. Nada de perfilar a personas privadas. No atribuir autoría sin evidencia. Sin datos personales ni de clientes en el agente. Toda conclusión asistida por IA se valida con criterio humano y queda documentada.

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `python: command not found` | Prueben `python3`. Si tampoco existe, instalen Python (python.org) o pídanle al agente que los guíe |
| La transcripción automática falla | Usen el plan B de `recetas/02_transcripcion.md`: copiar el panel "Mostrar transcripción" de YouTube |
| El clipping trae noticias de otros países | Es ruido de Google News: afinen las palabras clave en `config/caso.md` (frases más específicas) |
| Pocas noticias | Amplíen días (`--dias 7`) o agreguen palabras clave |
| El agente pide permiso para cada comando | Es normal y es una protección: lean qué va a hacer y aprueben |

Material docente: Pablo Matamoros (docente) y Agustín Vidal-Cádiz (ayudante).
