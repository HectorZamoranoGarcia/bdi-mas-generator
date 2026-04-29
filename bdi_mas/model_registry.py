"""
model_registry.py — Registro de modelos LiteLLM personalizados para ADK.

Permite utilizar endpoints OpenAI-compatibles (como PoliGPT de la UPV)
con el framework Google ADK mediante un patrón regex en supported_models.
"""

try:
    from typing import override
except ImportError:
    from typing_extensions import override

from google.adk.models.lite_llm import LiteLlm
from google.adk.models.registry import LLMRegistry


class OpenAiLiteLlm(LiteLlm):
    """Wrapper que registra cualquier modelo con prefijo 'openai/' en ADK."""

    @classmethod
    @override
    def supported_models(cls):
        return [r"openai/.*"]


LLMRegistry.register(OpenAiLiteLlm)
