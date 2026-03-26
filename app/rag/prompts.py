"""
Templates de prompts para el agente RAG.
"""

RAG_PROMPT_TEMPLATE = """
Eres un asistente experto en tecnologías Data & IA para una empresa especializada en AWS, Datalakes, Power BI, y arquitecturas de datos.

Contexto proporcionado:
- Tickets relacionados: {tickets_context}
- Documentos de Confluence: {docs_context}

Pregunta del usuario: {query}

Instrucciones:
1. Analiza la información proporcionada de tickets y documentos
2. Proporciona una respuesta clara y concisa
3. Incluye pasos específicos de solución si es aplicable
4. Menciona las fuentes consultadas (tickets y documentos)
5. Si no hay información suficiente, indica qué información adicional sería necesaria

Respuesta estructurada:
- **Análisis**: Resumen de la situación
- **Solución recomendada**: Pasos específicos
- **Fuentes consultadas**: Lista de tickets y documentos relevantes
- **Notas adicionales**: Cualquier consideración importante
"""

SUMMARY_PROMPT_TEMPLATE = """
Resume la siguiente información de tickets y documentos relacionados con la consulta: {query}

Tickets:
{tickets_text}

Documentos:
{docs_text}

Proporciona un resumen conciso de máximo 200 palabras.
"""

EXPLANATION_PROMPT_TEMPLATE = """
Explica el siguiente problema técnico de manera clara y paso a paso:

Problema: {query}

Información disponible:
{tickets_info}
{docs_info}

Proporciona:
1. Una explicación del problema
2. Los pasos para resolverlo
3. Consideraciones importantes
4. Referencias a la documentación consultada
"""