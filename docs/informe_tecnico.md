# Informe Técnico — BDI-MAS Generator

**Asignatura:** Agentes Inteligentes (AIN) · Práctica 2  
**Autores:** Héctor Zamorano García  
**Fecha:** Mayo 2026

---

## 1. Descripción del Sistema

**BDI-MAS Generator** es un sistema multi-agente construido sobre **Google ADK** (Agent Development Kit) que genera automáticamente proyectos multi-agente **BDI** en **Jason/AgentSpeak** a partir de un prompt en lenguaje natural.

El sistema recibe la descripción de un problema por parte del usuario y produce como salida un proyecto Jason completo: un archivo de configuración `.mas2j` y los archivos de código `.asl` correspondientes a cada agente del sistema generado.

## 2. Arquitectura del Sistema

El pipeline multi-agente utiliza obligatoriamente los tres tipos de `WorkflowAgent` disponibles en ADK:

```
root_pipeline (SequentialAgent)
│
├── 1. requirement_analyst (LlmAgent)
│     Analiza el prompt del usuario y extrae requisitos estructurados:
│     nombre del proyecto, agentes necesarios, protocolos de comunicación
│     y condiciones de parada.
│     → output_key: "requirements"
│
├── 2. research_team (ParallelAgent)
│   ├── github_researcher (LlmAgent)
│   │     Busca ejemplos oficiales de Jason en el repositorio
│   │     oficial, seleccionando los más relevantes para el problema.
│   │     → output_key: "github_examples"
│   │
│   └── docs_researcher (LlmAgent)
│         Consulta la documentación local indexada (PDFs de Jason)
│         mediante un sistema RAG basado en ChromaDB.
│         → output_key: "docs_knowledge"
│
├── 3. code_refinement (LoopAgent, max_iterations=5)
│   ├── bdi_developer (LlmAgent)
│   │     Genera o corrige el código .mas2j y .asl, y lo prueba
│   │     invocando el binario de Jason en un directorio temporal.
│   │     → output_key: "generated_code"
│   │
│   └── code_reviewer (LlmAgent)
│         Analiza la salida de la prueba. Si hay errores, genera
│         un informe de correcciones. Si es correcto, llama a
│         exit_loop para detener el bucle.
│         → output_key: "review_feedback"
│
└── 4. code_saver (LlmAgent)
        Persiste el proyecto final (.mas2j + .asl) en la carpeta
        'output/' organizado por nombre de proyecto.
        → output_key: "save_result"
```

### Justificación de los WorkflowAgents

| Tipo | Agente | Justificación |
|------|--------|---------------|
| **SequentialAgent** | `root_pipeline` | Las fases del pipeline tienen dependencias estrictas: no se puede generar código sin antes investigar, ni guardarlo sin antes probarlo. |
| **ParallelAgent** | `research_team` | La búsqueda de ejemplos oficiales y la consulta RAG son independientes entre sí. Ejecutarlas en paralelo reduce la latencia total. |
| **LoopAgent** | `code_refinement` | La generación de código BDI requiere refinamiento iterativo: generar → probar → corregir hasta obtener un resultado sin errores de compilación. |

## 3. Herramientas (Tools)

| Tool | Descripción |
|------|-------------|
| `search_github_examples(path)` | Accede a los ejemplos oficiales del proyecto Jason para consultar código de referencia. |
| `search_local_docs(query, k)` | Búsqueda semántica RAG sobre la documentación local (PDFs) indexada con ChromaDB y embeddings ONNX. |
| `test_mas_code(mas2j_code, agents_dict)` | Compila y ejecuta el MAS en un directorio temporal usando el binario de Jason. Máximo 5 intentos por sesión. |
| `save_mas_code(mas_name, ...)` | Persiste el proyecto final en `output/nombre_proyecto/`. |
| `exit_loop(tool_context)` | Señal de parada para el `LoopAgent` cuando el código es correcto. |

## 4. Tecnologías Utilizadas

- **Google ADK** — Framework de orquestación multi-agente.
- **LiteLLM** — Proxy para conectar con endpoints OpenAI-compatibles (PoliGPT).
- **ChromaDB** — Base de datos vectorial para el sistema RAG.
- **Jason 3.3.0** — Plataforma BDI para compilación y prueba de los MAS generados.
- **Python 3.11+** — Lenguaje de implementación.

## 5. Ejemplos de Evaluación

Se evaluó el sistema con cuatro prompts representativos. Los resultados generados se encuentran en la carpeta `evaluation/`:

1. **Fibonacci** — Un agente imprime la serie de Fibonacci hasta un valor dado.
2. **Ping-Pong v1** — Dos agentes intercambian un mensaje Ping/Pong (una iteración).
3. **Ping-Pong v2** — Dos agentes realizan N iteraciones de Ping/Pong.
4. **Subasta Holandesa** — Un subastador con precio descendente y N participantes con presupuesto aleatorio.
