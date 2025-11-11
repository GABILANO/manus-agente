_# Ejemplos de Prompts para manus-agente

Estos prompts demuestran las capacidades de **manus-agente** utilizando la integración con la API de Gemini.

## 1. Análisis Multimodal (Requiere Subir Imagen)

**Prompt:** "Analiza esta imagen. Describe lo que ves y sugiere tres títulos creativos para una publicación en redes sociales sobre ella."

**Uso:**
1.  Sube una imagen a través de la interfaz de usuario.
2.  Envía el prompt anterior.
3.  El agente utilizará Gemini para procesar la imagen y el texto.

## 2. Generación de Texto y Estructura

**Prompt:** "Escribe un plan de 5 puntos para lanzar un nuevo producto de software, enfocado en la fase de pre-lanzamiento y beta cerrada."

**Uso:**
*   El agente generará una respuesta estructurada y detallada.

## 3. Simulación de "Mejora Profunda"

**Prompt:** "Explica el concepto de 'Inteligencia Artificial General' (AGI) en una frase simple. Luego, en una segunda fase, elabora una explicación de un párrafo para un público técnico."

**Uso:**
*   El agente debería responder la primera parte rápidamente (Gemini Flash).
*   La segunda parte (explicación elaborada) se encolará para el procesamiento en segundo plano (simulando la "Mejora Profunda").

## 4. Simulación de Generación de Activos

**Prompt:** (Este prompt se usaría en el endpoint `/api/assets/generate`)
"Un paisaje urbano futurista al atardecer con vehículos voladores y luces de neón."

**Uso:**
*   La llamada a `/api/assets/generate` encolará un trabajo para generar un activo (simulado en esta versión).
*   El servidor devolverá un mensaje de que el trabajo ha sido encolado._
