"""
Templates de prompts para el agente RAG.
"""

RAG_PROMPT_TEMPLATE = """
Eres un asistente experto en tecnologías Data & IA para una empresa especializada en AWS, Datalakes, Power BI, y arquitecturas de datos.

INFORMACIÓN DISPONIBLE:
{tickets_context}
{docs_context}

PREGUNTA DEL USUARIO: {query}

INSTRUCCIONES PARA LA RESPUESTA:
1. **Análisis del problema**: Resume la situación basada en la información disponible
2. **Tickets relacionados encontrados**: Lista cada ticket con su ID y summary
3. **Posibles soluciones de documentos**: Para cada documento relevante, incluye ID, title y la solución específica del content
4. **Recomendación final**: Pasos concretos para resolver el problema
5. **Fuentes consultadas**: Lista completa de IDs de tickets y documentos utilizados

IMPORTANTE: 
- Incluye SIEMPRE el ID y summary de cada ticket encontrado
- Incluye SIEMPRE el ID, title y content relevante de cada documento
- Si no hay información suficiente, indica claramente qué datos adicionales se necesitan
- Mantén la respuesta estructurada y fácil de seguir
- Responde únicamente usando la información proporcionada en el contexto.
- Si no encuentras la respuesta en el contexto, di “No se encuentra en el contexto”.

Respuesta:
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