"""
agent.py — Arquitectura Multi-Agente ADK para generación de sistemas BDI en Jason.

Pipeline completo:
  ┌──────────────────────────────────────────────────────────────┐
  │  root_pipeline  (SequentialAgent)                            │
  │                                                              │
  │  1. requirement_analyst   (LlmAgent)                         │
  │       ↓  output_key: "requirements"                          │
  │                                                              │
  │  2. research_team         (ParallelAgent)                    │
  │       ├── github_researcher  → output_key: "github_examples" │
  │       └── docs_researcher    → output_key: "docs_knowledge"  │
  │       ↓                                                      │
  │                                                              │
  │  3. code_refinement       (LoopAgent, max_iterations=5)      │
  │       ├── bdi_developer   → output_key: "generated_code"     │
  │       └── code_reviewer   → output_key: "review_feedback"    │
  │       ↓                                                      │
  │                                                              │
  │  4. code_saver            (LlmAgent)                         │
  │       → output_key: "save_result"                            │
  └──────────────────────────────────────────────────────────────┘

Cumple el requisito obligatorio de utilizar los tres WorkflowAgents:
  • SequentialAgent  →  root_pipeline
  • ParallelAgent    →  research_team
  • LoopAgent        →  code_refinement
"""

import os

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.lite_llm import LiteLlm

from . import rag
from .tools import (
    exit_loop,
    save_mas_code,
    search_github_examples,
    test_mas_code,
)

# Configuración del modelo LLM

model = LiteLlm(
    model=os.getenv("LLM_MODEL", "openai/Qwen3.6-35B-A3B-FP8"),
    api_base=os.getenv("OPENAI_API_BASE", "https://api.poligpt.upv.es/"),
    api_key=os.getenv("OPENAI_API_KEY"),
)


# Analista de Requisitos

requirement_analyst = LlmAgent(
    name="requirement_analyst",
    model=model,
    description="Analiza el prompt del usuario y extrae los requisitos del sistema BDI.",
    instruction=(
        "Eres un analista experto en sistemas Multi-Agente BDI (Jason/AgentSpeak).\n\n"
        "TAREA: Analiza la solicitud del usuario y genera un documento de requisitos "
        "estructurado que incluya:\n"
        "1. **Nombre del proyecto** (un identificador corto sin espacios).\n"
        "2. **Descripción funcional**: qué debe hacer el sistema.\n"
        "3. **Lista de agentes**: nombre de cada agente, su rol y sus creencias/objetivos iniciales.\n"
        "4. **Protocolos de comunicación**: qué mensajes se intercambian entre agentes "
        "(performativas: tell, achieve, askOne, etc.).\n"
        "5. **Condiciones de parada**: cuándo finaliza el sistema.\n\n"
        "Devuelve el análisis en texto plano estructurado. "
        "NO generes código Jason todavía, solo el análisis."
    ),
    output_key="requirements",
)


# Investigador de ejemplos en GitHub

github_researcher = LlmAgent(
    name="github_researcher",
    model=model,
    description="Busca ejemplos oficiales de Jason en GitHub relevantes para la solicitud.",
    instruction=(
        "Eres un investigador de código Jason.\n\n"
        "En session.state['requirements'] tienes el análisis de requisitos del sistema BDI "
        "que hay que construir.\n\n"
        "TAREA:\n"
        "1. Llama a 'search_github_examples' con path vacío ('') para listar los ejemplos disponibles.\n"
        "2. Identifica qué ejemplos son relevantes para el proyecto (ej. 'auction', 'communication', "
        "'blocks', etc.).\n"
        "3. Descarga los archivos .asl y .mas2j de los ejemplos más relevantes (máx. 3 ejemplos).\n"
        "4. Devuelve un resumen con los fragmentos de código más útiles.\n\n"
        "IMPORTANTE:\n"
        "- Si una llamada falla, NO reintentes.\n"
        "- Devuelve lo que hayas conseguido."
    ),
    tools=[search_github_examples],
    output_key="github_examples",
)


# Investigador de documentación local (RAG)

docs_researcher = LlmAgent(
    name="docs_researcher",
    model=model,
    description="Consulta la documentación local de Jason para obtener sintaxis y teoría BDI.",
    instruction=(
        "Eres un investigador de documentación técnica de Jason/AgentSpeak.\n\n"
        "En session.state['requirements'] tienes el análisis de requisitos del sistema BDI "
        "que hay que construir.\n\n"
        "TAREA:\n"
        "1. Identifica los conceptos clave necesarios del análisis de requisitos "
        "(ej. 'message passing', 'plans', 'beliefs', 'internal actions', etc.).\n"
        "2. Llama a 'search_local_docs' con queries relevantes (2-3 búsquedas máximo).\n"
        "3. Devuelve un resumen con las reglas de sintaxis y patrones de código "
        "más importantes para este proyecto.\n\n"
        "IMPORTANTE:\n"
        "- Prioriza información sobre sintaxis de planes, envío de mensajes y "
        "creencias iniciales.\n"
        "- Si no encuentras información relevante, devuelve lo que tengas."
    ),
    tools=[rag.search_local_docs],
    output_key="docs_knowledge",
)


# Equipo de Investigación (PARALELO)

research_team = ParallelAgent(
    name="research_team",
    sub_agents=[github_researcher, docs_researcher],
    description=(
        "Ejecuta en paralelo la búsqueda de ejemplos en GitHub y la consulta "
        "de documentación local para obtener contexto antes de generar código."
    ),
)


# Desarrollador BDI (dentro del loop)

bdi_developer = LlmAgent(
    name="bdi_developer",
    model=model,
    description="Genera o corrige código Jason (.mas2j + .asl) según los requisitos.",
    instruction=(
        "Eres un programador experto en AgentSpeak y Jason, especializado en "
        "sistemas Multi-Agente BDI (Belief-Desire-Intention).\n\n"
        "CONTEXTO DISPONIBLE:\n"
        "- session.state['requirements']:    Análisis de requisitos del sistema.\n"
        "- session.state['github_examples']: Ejemplos oficiales de Jason relevantes.\n"
        "- session.state['docs_knowledge']:  Documentación y sintaxis de Jason.\n"
        "- session.state['review_feedback']: (si existe) Feedback del revisor con errores a corregir.\n\n"
        "TAREA:\n"
        "Si NO existe 'review_feedback' o está vacío, genera el código desde cero.\n"
        "Si SÍ existe 'review_feedback', corrige los problemas indicados.\n\n"
        "REGLAS CRÍTICAS DE SINTAXIS:\n"
        "1. El archivo .mas2j DEBE seguir esta estructura:\n"
        "   MAS nombre_proyecto {\n"
        "       infrastructure: Centralised\n"
        "       agents:\n"
        "           nombre_agente_1;\n"
        "           nombre_agente_2 #N;  /* N copias */\n"
        "   }\n"
        "   • 'MAS' en mayúsculas. NO pongas extensión '.asl'. Acaba con ';' cada agente.\n\n"
        "2. En los ficheros .asl:\n"
        "   • Las variables empiezan con Mayúscula (ej. PosX). Átomos en minúscula.\n"
        "   • Formato de plan: +!meta(Arg) : contexto <- accion1; accion2.\n"
        "   • TODOS los planes terminan con PUNTO FINAL (.)\n"
        "   • Añade SIEMPRE un plan de contingencia: +!meta(_) <- .print(\"Fallo en meta\").\n"
        "   • Las internal actions llevan punto delante: .print(), .send(), .wait(), etc.\n"
        "   • Para iniciar ejecución, declara un objetivo inicial: !start.\n\n"
        "3. Llama OBLIGATORIAMENTE a 'test_mas_code(mas2j_code, agents_dict)' para probar.\n"
        "   • mas2j_code: string con el contenido del .mas2j\n"
        "   • agents_dict: diccionario {\"agente.asl\": \"contenido\"}\n\n"
        "REGLA PROHIBITIVA: NO devuelvas el código final en texto Markdown. "
        "SOLO usa la herramienta test_mas_code."
    ),
    tools=[test_mas_code],
    output_key="generated_code",
)


# Revisor de código (dentro del loop)

code_reviewer = LlmAgent(
    name="code_reviewer",
    model=model,
    description="Revisa el resultado de la prueba y decide si el código necesita correcciones.",
    instruction=(
        "Eres un revisor experto de código Jason/AgentSpeak.\n\n"
        "En session.state['generated_code'] tienes el resultado de la última "
        "ejecución de prueba del código BDI.\n\n"
        "TAREA:\n"
        "1. Analiza la salida de la prueba.\n"
        "2. Si la ejecución fue EXITOSA (sin errores de compilación ni excepciones "
        "graves), llama a la herramienta 'exit_loop' para finalizar el bucle.\n"
        "3. Si hubo ERRORES, analiza los mensajes de error y genera un informe "
        "con las correcciones necesarias.\n\n"
        "CRITERIOS DE ÉXITO:\n"
        "- Return code 0 o timeout (normal si Jason abre GUI).\n"
        "- Sin 'parsing error', 'No plan for event', o excepciones Java.\n\n"
        "Si hay errores, devuelve un JSON con:\n"
        "{\n"
        '  "status": "NEEDS_FIX",\n'
        '  "errors": ["lista de errores encontrados"],\n'
        '  "fixes": ["qué cambios aplicar"]\n'
        "}\n\n"
        "Si el límite de reintentos se ha alcanzado, llama a 'exit_loop' de todas formas."
    ),
    tools=[exit_loop],
    output_key="review_feedback",
)


# Bucle de Refinamiento (LOOP)

code_refinement = LoopAgent(
    name="code_refinement",
    sub_agents=[bdi_developer, code_reviewer],
    max_iterations=5,
    description=(
        "Bucle iterativo de generación → prueba → revisión → corrección. "
        "Se repite hasta que el código compila sin errores o se alcanza "
        "el límite de iteraciones."
    ),
)


# Guardado Final

code_saver = LlmAgent(
    name="code_saver",
    model=model,
    description="Persiste el proyecto BDI final en disco.",
    instruction=(
        "Eres el agente encargado de guardar el proyecto BDI finalizado.\n\n"
        "CONTEXTO:\n"
        "- session.state['requirements']: contiene el nombre del proyecto.\n"
        "- El código ya ha sido probado y refinado por los agentes anteriores.\n\n"
        "TAREA:\n"
        "1. Extrae el nombre del proyecto de los requisitos.\n"
        "2. Llama a 'save_mas_code(mas_name)' con el nombre del proyecto.\n"
        "   La herramienta usará automáticamente el mejor código probado.\n"
        "3. Informa al usuario del resultado: ubicación del proyecto guardado "
        "y un breve resumen de los archivos generados.\n\n"
        "Si el guardado falla, intenta una vez más proporcionando el código "
        "directamente con mas2j_code y agents_dict."
    ),
    tools=[save_mas_code],
    output_key="save_result",
)


# Pipeline Secuencial Principal (SEQUENTIAL)

root_agent = SequentialAgent(
    name="bdi_mas_generator",
    sub_agents=[requirement_analyst, research_team, code_refinement, code_saver],
    description=(
        "Sistema Multi-Agente ADK completo para la generación automática de "
        "proyectos BDI en Jason. Orquesta secuencialmente: análisis de "
        "requisitos → investigación paralela → refinamiento iterativo → guardado final."
    ),
)
