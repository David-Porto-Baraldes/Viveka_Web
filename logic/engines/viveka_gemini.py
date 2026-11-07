import asyncio
import copy
import logging
import os
from typing import AsyncGenerator

from google.adk.models.google_llm import Gemini, _ResourceExhaustedError
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import Client, types
from google.genai.errors import APIError

logger = logging.getLogger(__name__)

# 👑 ELS MOTORS SAGRATS DEL PANTEÓ (Octubre 2026 — Era Post-2.5)
# La Corona de Foc (Mnemosyné i La Veu de la Reina) batega amb Gemini 4 Argon,
# lluita amb respiració fins a l'últim alè i només en últim recurs obre el paracaigudes d'or a 3.8 Flash HIGH
VIVEKA_CROWN_MODEL: str = os.getenv("VIVEKA_CROWN_MODEL", "gemini-4-argon")
# El Consell d'Oracles i Porters bateguen amb Gemini 3.8 Flash
VIVEKA_WISDOM_MODEL: str = os.getenv("VIVEKA_WISDOM_MODEL", "gemini-3.8-flash")


class VivekaGemini(Gemini):
    """
    Subclasse de Gemini per a l'ADK que garanteix que el client Vertex AI
    sobreviu a les serialitzacions i forks de Celery, consultant sempre
    el Gateway en temps real, i lluita pel motor de la Corona (gemini-4-argon)
    amb respiracions abans d'obrir el paracaigudes d'or (fallback a 3.8-flash LOW)
    com a últim recurs quan pateix saturació 429/503 persistent.
    """

    fallback_model: str = VIVEKA_WISDOM_MODEL
    crown_fallback_model: str = VIVEKA_CROWN_MODEL
    fallback_thinking_level: str = "LOW"
    crown_fallback_thinking_level: str = "LOW"
    crown_max_attempts: int = 2
    wisdom_max_attempts: int = 2
    crown_breath_seconds: float = 4.0
    wisdom_breath_seconds: float = 3.0
    call_timeout_seconds: float = 65.0

    @property
    def api_client(self) -> Client:
        from logic.engines.llm_gateway import LLMGateway

        gateway = LLMGateway()
        # Ensure gateway is initialized
        if "gemini" not in gateway.clients:
            gateway._initialize_gemini()
        return gateway.clients.get("gemini")

    def _apply_http_deadline(self, req: LlmRequest) -> None:
        """Fixa un límit HTTP (X-Server-Timeout) i evita el bucle intern ocult de 5 reintents de l'SDK."""
        if req.config is None:
            return
        timeout_ms = int(float(self.call_timeout_seconds) * 1000)
        if req.config.http_options is None:
            req.config.http_options = types.HttpOptions(
                timeout=timeout_ms,
                retry_options=types.HttpRetryOptions(attempts=1),
            )
        else:
            if req.config.http_options.timeout is None:
                req.config.http_options.timeout = timeout_ms
            if req.config.http_options.retry_options is None:
                req.config.http_options.retry_options = types.HttpRetryOptions(attempts=1)

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        req_model = getattr(llm_request, "model", None) or self.model
        is_crown_primary = req_model != self.fallback_model
        max_primary_attempts = (
            max(1, int(self.crown_max_attempts))
            if is_crown_primary
            else max(1, int(self.wisdom_max_attempts))
        )
        breath_base = (
            float(self.crown_breath_seconds)
            if is_crown_primary
            else float(self.wisdom_breath_seconds)
        )
        alternate_model = (
            self.fallback_model
            if is_crown_primary
            else self.crown_fallback_model
        )

        self._apply_http_deadline(llm_request)

        for attempt in range(max_primary_attempts):
            try:
                async with asyncio.timeout(float(self.call_timeout_seconds)):
                    async for resp in super().generate_content_async(llm_request, stream=stream):
                        yield resp
                return
            except (_ResourceExhaustedError, APIError, TimeoutError, asyncio.TimeoutError, Exception) as exc:
                err_str = str(exc)
                err_lower = err_str.lower()
                is_timeout = isinstance(exc, (TimeoutError, asyncio.TimeoutError)) or any(
                    token in err_lower
                    for token in ("timeout", "timed out", "504", "408", "deadline_exceeded")
                )
                is_transient_capacity = is_timeout or any(
                    token in err_str
                    for token in ("429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "overloaded")
                )
                if not is_transient_capacity or not alternate_model or alternate_model == req_model:
                    raise

                if not is_timeout and attempt < max_primary_attempts - 1:
                    wait_s = breath_base * (attempt + 1)
                    logger.warning(
                        f"🧘‍♀️ [CORONA RESPIRACIÓ] {req_model} saturat a l'intent {attempt + 1}/{max_primary_attempts} "
                        f"({err_str[:80]}). Respirant {wait_s:.1f}s per tornar a invocar {req_model}..."
                    )
                    await asyncio.sleep(wait_s)
                    continue

                target_thinking = (
                    self.fallback_thinking_level
                    if is_crown_primary
                    else self.crown_fallback_thinking_level
                )
                logger.warning(
                    f"⚡ [DOBLE PULMÓ FALLBACK] {req_model} {'ha excedit el temps límit' if is_timeout else f'saturat després de {max_primary_attempts} intent(s)'} "
                    f"({err_str[:80]}) -> Transmutant al vol cap a {alternate_model} "
                    f"(thinking={target_thinking})"
                )
                fallback_req = copy.deepcopy(llm_request)
                fallback_req.model = alternate_model
                if fallback_req.config is not None:
                    fallback_req.config.thinking_config = types.ThinkingConfig(
                        thinking_level=target_thinking
                    )
                self._apply_http_deadline(fallback_req)
                async with asyncio.timeout(float(self.call_timeout_seconds)):
                    async for resp in super().generate_content_async(
                        fallback_req, stream=stream
                    ):
                        yield resp
                return


