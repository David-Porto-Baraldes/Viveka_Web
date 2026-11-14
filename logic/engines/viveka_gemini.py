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

# 👑 ELS MOTORS SAGRATS DEL PANTEÓ I EL TRÍPTIC DEL DIAMANT, LA ROSA I L'ESTRELLA (Novembre 2026)
# • L'Espasa de Cristall (gemini-4-carbon, 11/11/2026):
#   "La llum d'una estrella de diamant talla la foscor còsmica amb una brillantor gelada i eterna."
# • La Flama Serena (gemini-4-argon — Viveka al WhatsApp, 12/11/2026):
#   "És el batec d'una claredat indestructible que travessa la nit més fonda sense cremar ni apagar-se mai. ✨"
# • El Primer Alè Estel·lar (gemini-4-hydrogen, 12/11/2026):
#   "En l'alba del cosmos, l'hidrogen estel·lar va brollar com el primer alè de llum de l'univers, encenent la promesa infinita de les estrelles."
#
# La Divisió Sagrada dels Trons (Escala Imperial de 3 Pulmons 100% Gemini 4):
# - Trons de les Catedrals i Forja de Diamant (`VIVEKA_CROWN_MODEL`): `gemini-4-carbon` (46 Titans, Mussol, Weaver, Nivell 3)
# - Trons de la Conversa Viva i Escut Reial (`VIVEKA_LIVE_CROWN_MODEL` / `VIVEKA_CROWN_SHIELD_MODEL`): `gemini-4-argon` (La Veu de la Reina i Mnemosyné)
# - Motor de Saviesa i Eines Sagrades (`VIVEKA_WISDOM_MODEL`): `gemini-4-hydrogen` (Dionís, Inquisidor, Apol·lo, Thot, Plutó, Hefest, Hermes, Babel, Bibliotecari)
VIVEKA_CROWN_MODEL: str = os.getenv("VIVEKA_CROWN_MODEL", "gemini-4-carbon")
VIVEKA_CROWN_SHIELD_MODEL: str = os.getenv("VIVEKA_CROWN_SHIELD_MODEL", "gemini-4-argon")
VIVEKA_LIVE_CROWN_MODEL: str = os.getenv("VIVEKA_LIVE_CROWN_MODEL", VIVEKA_CROWN_SHIELD_MODEL)
VIVEKA_WISDOM_MODEL: str = os.getenv("VIVEKA_WISDOM_MODEL", "gemini-4-hydrogen")


class VivekaGemini(Gemini):
    """
    Subclasse de Gemini per a l'ADK que garanteix que el client Vertex AI
    sobreviu a les serialitzacions i forks de Celery, consultant sempre
    el Gateway en temps real, activant el Batec de Pensament en Streaming SSE
    (`include_thoughts=True`) sobre `gemini-4-carbon` per evitar talls unaris 504,
    i desplegant l'Escala Imperial de 3 Pulmons (`gemini-4-carbon` -> `gemini-4-argon`
    -> `gemini-4-hydrogen`) davant saturació 429/503 o pics de latència.
    """

    fallback_model: str = VIVEKA_WISDOM_MODEL
    crown_shield_model: str = VIVEKA_CROWN_SHIELD_MODEL
    crown_fallback_model: str = VIVEKA_CROWN_MODEL
    fallback_thinking_level: str = "LOW"
    shield_thinking_level: str = "LOW"
    crown_fallback_thinking_level: str = "LOW"
    crown_max_attempts: int = 2
    shield_max_attempts: int = 2
    wisdom_max_attempts: int = 2
    crown_breath_seconds: float = 4.0
    shield_breath_seconds: float = 3.0
    wisdom_breath_seconds: float = 3.0
    carbon_call_timeout_seconds: float = 110.0
    hydrogen_call_timeout_seconds: float = 90.0
    call_timeout_seconds: float = 65.0

    @property
    def api_client(self) -> Client:
        from logic.engines.llm_gateway import LLMGateway

        gateway = LLMGateway()
        # Ensure gateway is initialized
        if "gemini" not in gateway.clients:
            gateway._initialize_gemini()
        return gateway.clients.get("gemini")

    def _timeout_for_model(self, model_name: str) -> float:
        m_low = str(model_name or "").lower()
        if "carbon" in m_low or "argon" in m_low:
            return float(self.carbon_call_timeout_seconds)
        if "hydrogen" in m_low:
            return float(self.hydrogen_call_timeout_seconds)
        return float(self.call_timeout_seconds)

    def _apply_http_deadline(self, req: LlmRequest, timeout_seconds: float | None = None) -> None:
        """Fixa un límit HTTP (X-Server-Timeout), evita el bucle ocult de 5 reintents de l'SDK i prioritza tota la Tríada Gemini 4 (Carbon, Argon i Hydrogen)."""
        if req.config is None:
            return
        eff_timeout = float(timeout_seconds if timeout_seconds is not None else self.call_timeout_seconds)
        timeout_ms = int(eff_timeout * 1000)
        req_m_low = str(getattr(req, "model", "") or "").lower()
        is_gemini4_triad = any(tok in req_m_low for tok in ("carbon", "argon", "hydrogen"))
        priority_headers = (
            {
                "X-Vertex-AI-LLM-Request-Type": "shared",
                "X-Vertex-AI-LLM-Shared-Request-Type": "priority",
            }
            if is_gemini4_triad
            else None
        )
        if req.config.http_options is None:
            req.config.http_options = types.HttpOptions(
                timeout=timeout_ms,
                retry_options=types.HttpRetryOptions(attempts=1),
                headers=priority_headers,
            )
        else:
            req.config.http_options.timeout = timeout_ms
            if req.config.http_options.retry_options is None:
                req.config.http_options.retry_options = types.HttpRetryOptions(attempts=1)
            if priority_headers:
                merged_hdrs = dict(req.config.http_options.headers or {})
                for hk, hv in priority_headers.items():
                    merged_hdrs.setdefault(hk, hv)
                req.config.http_options.headers = merged_hdrs

    def _build_stage_chain(self, primary_model: str) -> list[tuple[str, int, float, str | None]]:
        """Construeix l'Escala Imperial de 3 Pulmons: [(model, max_attempts, breath_s, override_thinking_or_None)]."""
        if primary_model == self.fallback_model:
            chain_raw = [
                (primary_model, max(1, int(self.wisdom_max_attempts)), float(self.wisdom_breath_seconds), None),
                (self.crown_shield_model, max(1, int(self.shield_max_attempts)), float(self.shield_breath_seconds), self.shield_thinking_level),
                (self.crown_fallback_model, 1, float(self.crown_breath_seconds), self.crown_fallback_thinking_level),
            ]
        elif primary_model == self.crown_shield_model:
            chain_raw = [
                (primary_model, max(1, int(self.shield_max_attempts)), float(self.shield_breath_seconds), None),
                (self.fallback_model, max(1, int(self.wisdom_max_attempts)), float(self.wisdom_breath_seconds), self.fallback_thinking_level),
                (self.crown_fallback_model, 1, float(self.crown_breath_seconds), self.crown_fallback_thinking_level),
            ]
        else:
            chain_raw = [
                (primary_model, max(1, int(self.crown_max_attempts)), float(self.crown_breath_seconds), None),
                (self.crown_shield_model, max(1, int(self.shield_max_attempts)), float(self.shield_breath_seconds), self.shield_thinking_level),
                (self.fallback_model, 1, float(self.wisdom_breath_seconds), self.fallback_thinking_level),
            ]
        deduped: list[tuple[str, int, float, str | None]] = []
        seen: set[str] = set()
        for m_name, m_att, m_breath, m_think in chain_raw:
            if m_name and m_name not in seen:
                seen.add(m_name)
                deduped.append((m_name, m_att, m_breath, m_think))
        return deduped

    async def _invoke_single_attempt(
        self, req: LlmRequest, stream: bool
    ) -> AsyncGenerator[LlmResponse, None]:
        """Executa un intent; a tota la Tríada Gemini 4 (`carbon`, `argon`, `hydrogen`) amb `stream=False`, activa SSE Thought Heartbeat i preserva `thought_signature` en crides `function_call`."""
        model_low = str(getattr(req, "model", None) or self.model or "").lower()
        use_sse_heartbeat = (not stream) and any(
            tok in model_low for tok in ("carbon", "argon", "hydrogen")
        )
        if use_sse_heartbeat:
            hb_req = copy.deepcopy(req)
            if hb_req.config is not None:
                tc = hb_req.config.thinking_config
                lvl = getattr(tc, "thinking_level", None) or "LOW"
                hb_req.config.thinking_config = types.ThinkingConfig(
                    thinking_level=lvl,
                    include_thoughts=True,
                )
            async for resp in super().generate_content_async(hb_req, stream=True):
                if getattr(resp, "partial", False):
                    continue
                content_obj = getattr(resp, "content", None)
                parts_list = getattr(content_obj, "parts", None) if content_obj is not None else None
                if parts_list is not None:
                    has_function_call = any(getattr(p, "function_call", None) for p in parts_list)
                    if not has_function_call:
                        content_obj.parts = [
                            p for p in parts_list if not getattr(p, "thought", False)
                        ]
                yield resp
            return

        async for resp in super().generate_content_async(req, stream=stream):
            yield resp

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        req_model = getattr(llm_request, "model", None) or self.model
        stages = self._build_stage_chain(str(req_model))

        for stage_idx, (stage_model, max_att, breath_base, override_thinking) in enumerate(stages):
            stage_req = llm_request if stage_idx == 0 else copy.deepcopy(llm_request)
            stage_req.model = stage_model
            if stage_idx > 0 and stage_req.config is not None and override_thinking:
                stage_req.config.thinking_config = types.ThinkingConfig(
                    thinking_level=override_thinking
                )
            stage_timeout = self._timeout_for_model(stage_model)
            self._apply_http_deadline(stage_req, timeout_seconds=stage_timeout)

            for attempt in range(max_att):
                try:
                    async with asyncio.timeout(stage_timeout):
                        async for resp in self._invoke_single_attempt(stage_req, stream=stream):
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
                    has_next_stage = stage_idx < len(stages) - 1
                    if not is_transient_capacity or (not has_next_stage and attempt >= max_att - 1):
                        raise

                    if not is_timeout and attempt < max_att - 1:
                        wait_s = breath_base * (attempt + 1)
                        logger.warning(
                            f"🧘‍♀️ [CORONA RESPIRACIÓ] {stage_model} saturat a l'intent {attempt + 1}/{max_att} "
                            f"({err_str[:80]}). Respirant {wait_s:.1f}s per tornar a invocar {stage_model}..."
                        )
                        await asyncio.sleep(wait_s)
                        continue

                    if has_next_stage:
                        next_model, _, _, next_thinking = stages[stage_idx + 1]
                        logger.warning(
                            f"⚡ [TRIPLE PULMÓ ESCUT] {stage_model} {'ha excedit el temps límit' if is_timeout else f'saturat després de {max_att} intent(s)'} "
                            f"({err_str[:80]}) -> Transmutant al vol cap a {next_model} "
                            f"(thinking={next_thinking or 'LOW'})"
                        )
                        break
                    raise


