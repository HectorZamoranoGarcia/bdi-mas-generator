"""
BDI-MAS Generator — Sistema Multi-Agente ADK para generación de sistemas BDI en Jason.

Este paquete implementa un pipeline multi-agente que utiliza Google ADK con
SequentialAgent, ParallelAgent y LoopAgent para generar, verificar y persistir
proyectos Multi-Agente en AgentSpeak/Jason a partir de un prompt del usuario.
"""

from dotenv import load_dotenv

load_dotenv()

from . import model_registry  # noqa: E402, F401 — registra modelos LiteLLM
from . import agent            # noqa: E402, F401 — expone root_agent
