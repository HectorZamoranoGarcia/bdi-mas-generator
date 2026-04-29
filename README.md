<div align="center">

# 🧠 BDI-MAS Generator

**Sistema Multi-Agente ADK para Generación Automática de Sistemas BDI en Jason**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google&logoColor=white)](https://github.com/google/adk-python)
[![Jason 3.3](https://img.shields.io/badge/Jason-3.3.0-orange)](https://github.com/jason-lang/jason)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<br>

*Un pipeline multi-agente inteligente que transforma descripciones en lenguaje natural en sistemas multi-agente BDI completamente funcionales.*

</div>

---

## 📋 Descripción

**BDI-MAS Generator** recibe un prompt del usuario describiendo un problema y genera automáticamente un proyecto **Jason/AgentSpeak** completo, incluyendo:

- 📄 Archivo de configuración `.mas2j` con la definición del sistema multi-agente
- 📝 Archivos `.asl` con el código AgentSpeak de cada agente del sistema

El sistema utiliza **Google ADK** como framework de orquestación, implementando los tres tipos de `WorkflowAgent` disponibles para coordinar las distintas fases del proceso de generación.

## 🏗️ Arquitectura

```
root_pipeline (SequentialAgent)
│
├── 1. requirement_analyst        →  Análisis de requisitos del prompt
│
├── 2. research_team (ParallelAgent)
│   ├── github_researcher         →  Búsqueda de ejemplos oficiales en GitHub
│   └── docs_researcher           →  Consulta RAG sobre documentación local
│
├── 3. code_refinement (LoopAgent, max_iterations=5)
│   ├── bdi_developer             →  Generación / corrección de código Jason
│   └── code_reviewer             →  Revisión y validación del código
│
└── 4. code_saver                 →  Persistencia del proyecto final
```

### WorkflowAgents utilizados

| Tipo | Agente | Propósito |
|------|--------|-----------|
| `SequentialAgent` | `root_pipeline` | Orquesta las fases del pipeline con dependencias secuenciales |
| `ParallelAgent` | `research_team` | Ejecuta búsquedas de GitHub y RAG simultáneamente |
| `LoopAgent` | `code_refinement` | Ciclo iterativo de generación → prueba → corrección |

### Herramientas (Tools)

| Tool | Descripción |
|------|-------------|
| `search_github_examples` | Consulta la API de GitHub para obtener ejemplos oficiales de Jason |
| `search_local_docs` | Búsqueda semántica RAG sobre documentación local (ChromaDB) |
| `test_mas_code` | Compila y ejecuta el MAS en un directorio temporal con Jason |
| `save_mas_code` | Guarda el proyecto final en `output/` |
| `exit_loop` | Señal de parada del bucle de refinamiento |

## 📁 Estructura del Proyecto

```
bdi-mas-generator/
├── bdi_mas/                      # Código fuente del sistema
│   ├── __init__.py               # Inicialización del paquete
│   ├── agent.py                  # Arquitectura multi-agente ADK
│   ├── tools.py                  # Herramientas de los agentes
│   ├── rag.py                    # Sistema RAG con ChromaDB
│   ├── model_registry.py         # Registro de modelos LiteLLM
│   ├── update_rag.py             # Utilidad para reconstruir el índice RAG
│   ├── requirements.txt          # Dependencias Python
│   ├── .env.example              # Plantilla de variables de entorno
│   └── docs/                     # Documentación de referencia de Jason
│       ├── jason.pdf
│       ├── Jason FAQ.pdf
│       └── modules-namespaces.pdf
│
├── evaluation/                   # Ejemplos de evaluación
│   ├── fibonacci/                # Serie de Fibonacci
│   ├── ping_pong_v1/             # Ping-Pong (1 iteración)
│   ├── ping_pong_v2/             # Ping-Pong (N iteraciones)
│   └── dutch_auction/            # Subasta Holandesa
│
├── docs/                         # Documentación del proyecto
│   └── informe_tecnico.md        # Informe técnico (máx. 2 páginas)
│
├── README.md
├── .gitignore
└── LICENSE
```

## 🚀 Instalación

### Requisitos previos

- **Python 3.11+**
- **Java 21** (JDK) — necesario para ejecutar Jason
- **Jason 3.3.0** — plataforma BDI

### 1. Clonar el repositorio

```bash
git clone https://github.com/HectorZamoranoGarcia/bdi-mas-generator.git
cd bdi-mas-generator
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r bdi_mas/requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp bdi_mas/.env.example bdi_mas/.env
# Editar bdi_mas/.env con tus API keys
```

### 4. Instalar Jason

```bash
# Descargar desde: https://github.com/jason-lang/jason/releases
# Descomprimir y configurar:

# Linux/macOS
export JASON_BIN=/ruta/al/ejecutable/jason
export PATH=$JASON_BIN/bin:$PATH

# Windows PowerShell
$env:JASON_BIN="C:\ruta\a\jason.bat"
```

### 5. Inicializar la base de datos RAG

```bash
python -m bdi_mas.update_rag
```

## 💡 Uso

### Ejecutar con ADK CLI

```bash
adk run bdi_mas
```

### Ejemplo de prompt

```
Crea un sistema multi-agente en Jason donde un agente subastador
realice una subasta holandesa con 3 participantes. El subastador
comienza con precio 100 y lo baja de 10 en 10 hasta que alguien acepte.
```

El sistema generará automáticamente los archivos `.mas2j` y `.asl` en la carpeta `output/`.

## 📊 Ejemplos de Evaluación

Cada ejemplo incluye el prompt utilizado y los archivos Jason generados:

| Ejemplo | Descripción | Archivos |
|---------|-------------|----------|
| **Fibonacci** | Un agente imprime la serie de Fibonacci hasta un valor dado | `fibonacci.mas2j`, `fibonacci_agent.asl` |
| **Ping-Pong v1** | Dos agentes intercambian Ping/Pong una vez | `ping_pong.mas2j`, `pinger.asl`, `ponger.asl` |
| **Ping-Pong v2** | Dos agentes hacen Ping/Pong durante N iteraciones | `ping_pong_iter.mas2j`, `pinger.asl`, `ponger.asl` |
| **Subasta Holandesa** | Subastador + N participantes con precio descendente | `dutch_auction.mas2j`, `auctioneer.asl`, `participant.asl` |

### Ejecutar un ejemplo manualmente

```bash
cd evaluation/fibonacci
jason mas start --mas2j=fibonacci.mas2j --console
```

## 🛠️ Tecnologías

- **[Google ADK](https://github.com/google/adk-python)** — Framework de orquestación multi-agente
- **[LiteLLM](https://github.com/BerriAI/litellm)** — Proxy para endpoints LLM OpenAI-compatibles
- **[ChromaDB](https://www.trychroma.com/)** — Base de datos vectorial para RAG
- **[Jason](https://github.com/jason-lang/jason)** — Plataforma BDI para AgentSpeak
- **[PoliGPT](https://poligpt.upv.es/)** — Endpoint LLM de la UPV

## 📄 Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).

---

<div align="center">

**Agentes Inteligentes (AIN) — Universitat Politècnica de València**

*Práctica 2: Agentes Workflow · Curso 2025-2026*

</div>
