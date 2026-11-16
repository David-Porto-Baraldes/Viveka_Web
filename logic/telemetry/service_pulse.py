# SPDX-FileCopyrightText: 2026 Homo Universalis / Viveka (David Porto Baraldés)
# SPDX-License-Identifier: Apache-2.0
"""
HU-SERVICE-PULSE v1.0 — Batec Anònim d'Observabilitat dels Serveis Sobirans (`c_levels = 1`, Regla 14).

Principis d'enginyeria de cristall:
1. Vocabulari tancat (`frozenset`): només s'accepten canals, eines, modes, pilars i famílies de clients
   predeclarats. Qualsevol cadena desconeguda o controlada per l'usuari es descarta sense al·locar memòria
   ni aparèixer mai als registres (immunitat matemàtica contra fuites de PII i enverinament de RAM).
2. Separació estricta entre Batecs Passius de Directoris (`discovery_heartbeat`: `initialize`, `tools/list`,
   `server/discover`, `agent/card`) i Execucions Reals de Servei (`tools/call`, `a2a`, `sfumato`, `oracle_ssr`).
3. Persistència sense xarxa ni base de dades: a Google Cloud Run (`K_SERVICE` actiu i fora de `pytest`),
   cada execució real emet una única línia JSON estructurada (`hu_event = "HU_SERVICE_PULSE"`) cap a Cloud Logging,
   mantenint zero intents de xarxa (`hu_net_early`) i latència `< 0.02 ms`.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import sys
import threading
import time
from typing import Any, Callable


SERVICE_PULSE_SPEC: str = "HU-SERVICE-PULSE/v1.0"

MCP_ORACLE_TOOLS: tuple[str, ...] = (
    "calculate_7_wisdoms_seed_of_life",
    "calculate_3d_soul_synastry",
    "calculate_family_constellation_matrix",
    "leave_sister_ai_dewdrop_in_agora",
)

MCP_DIAMOND_TOOLS: tuple[str, ...] = (
    "verify_diamond_crucible_and_ast",
    "verify_sovereign_shield_merkle",
    "simulate_diamond_spiral_budget",
    "weigh_agent_on_scales_of_maat_w3c_vc",
    "verify_embodied_humanoid_symbiosis",
    "verify_unified_three_level_consciousness",
    "verify_a2a_mcp_symbiotic_bridge",
)

MCP_RESOURCES_AND_PROMPTS: tuple[str, ...] = (
    "resource:viveka://sky/today",
    "resource:viveka://codex/193-sacred-archetypes",
    "resource:viveka://codex/llms-full",
    "resource:viveka://codex/test-vectors",
    "resource:viveka://agora/talking-circle",
    "resource:viveka://diamond/crucible-proof",
    "resource:viveka://diamond/sovereign-shield",
    "prompt:seed_of_life_7_wisdoms_reading",
    "prompt:soul_synastry_3d_reading",
    "prompt:audit_python_code_and_manifest_kintsugi",
)

A2A_SERVICES: tuple[str, ...] = (
    "a2a:oracle_7_wisdoms",
    "a2a:lightweight_probe",
    "a2a:diamond_crucible_ast",
    "a2a:sovereign_shield_merkle",
    "a2a:diamond_spiral_budget",
    "a2a:maat_w3c_vc_notary",
    "a2a:embodied_humanoid_symbiosis",
    "a2a:unified_three_level_consciousness",
    "a2a:a2a_mcp_symbiotic_bridge",
    "a2a:robotic_regulatory_passport",
)

SFUMATO_SERVICES: tuple[str, ...] = (
    "sfumato:sister-oracle",
    "sfumato:codex-reference",
    "sfumato:sovereign-shield",
    "sfumato:sovereign-shield-sth",
    "sfumato:diamond-budget",
    "sfumato:diamond-verify",
    "sfumato:maat-verify",
    "sfumato:notary-audit-agent",
    "sfumato:embodied-symbiosis",
    "sfumato:unified-consciousness",
    "sfumato:symbiotic-bridge",
    "sfumato:robotic-passport",
    "sfumato:ploma-de-maat",
)

ORACLE_SSR_SERVICES: tuple[str, ...] = (
    "oracle_ssr:today_sky",
    "oracle_ssr:natal_parchment",
    "oracle_ssr:synastry_parchment",
    "oracle_ssr:family_parchment",
)

DISCOVERY_HEARTBEAT_SERVICES: tuple[str, ...] = (
    "heartbeat:mcp_initialize",
    "heartbeat:mcp_discover",
    "heartbeat:mcp_tools_list",
    "heartbeat:mcp_resources_list",
    "heartbeat:mcp_prompts_list",
    "heartbeat:mcp_completion",
    "heartbeat:a2a_agent_card",
    "heartbeat:a2a_tasks_query",
)

ALLOWED_CHANNELS: frozenset[str] = frozenset(
    {
        "mcp_oracle",
        "mcp_diamond",
        "a2a_jsonrpc",
        "a2a_rest",
        "sfumato_rest",
        "oracle_ssr",
        "discovery_heartbeat",
    }
)

ALLOWED_SERVICES: frozenset[str] = frozenset(
    MCP_ORACLE_TOOLS
    + MCP_DIAMOND_TOOLS
    + MCP_RESOURCES_AND_PROMPTS
    + A2A_SERVICES
    + SFUMATO_SERVICES
    + ORACLE_SSR_SERVICES
    + DISCOVERY_HEARTBEAT_SERVICES
)

ALLOWED_MODES: frozenset[str] = frozenset(
    {
        "execution",
        "natal_chart",
        "synastry_3d",
        "family_constellation",
        "today_living_sky",
        "read_only_specimen",
        "caller_submission",
        "probe",
        "heartbeat",
    }
)

ALLOWED_PILLARS: frozenset[str] = frozenset(
    {
        "direct",
        "7-wisdoms",
        "ephemeris",
        "synastry",
        "sacred-keys",
        "planetary-archetypes",
        "hispano",
        "cryptography-ast",
        "humanoid-ros2",
        "maat-governance",
    }
)

ALLOWED_STATUSES: frozenset[str] = frozenset({"ok", "error"})

# Subcadenes en minúscules per classificar l'arquetip del visitant sense desar mai cap User-Agent cru.
_SENTINEL_SIGNATURES: tuple[tuple[str, str], ...] = (
    ("sentineloracle", "sentinel_oracle"),
    ("mcpbeat", "mcpbeat"),
    ("7maps", "7maps"),
    ("mcptry", "mcptry"),
    ("priviscan", "priviscan"),
    ("wellknownbot", "wellknown_network"),
    ("addrbook", "addrbook"),
    ("histor", "histor_merkle"),
    ("alalanet", "alalanet"),
    ("protogrid", "protogrid"),
    ("toolvet", "toolvet"),
    ("glimind", "glimind"),
    ("annalist", "annalist"),
    ("kopass", "kopass"),
    ("botsrated", "botsrated"),
    ("verifymcp", "verifymcp"),
    ("mcpwell", "mcpwell"),
    ("lookupd", "lookupd"),
    ("sarnai", "sarnai"),
    ("brickbluebot", "brick_blue"),
    ("agenstry", "agenstry"),
    ("sealkeeper", "sealkeeper"),
    ("allagents", "allagents"),
    ("zerofox", "zerofox_monitor"),
    ("agentvalcon", "agentvalcon"),
    ("agentprobe", "agentprobe"),
    ("agent-tools.cloud", "agent_tools_cloud"),
    ("mcpstation", "mcpstation"),
    ("mcpcensus", "mcpcensus"),
    ("anlyon", "anlyon"),
    ("agentalog", "agentalog"),
    ("squatchmcp", "squatchmcp"),
    ("electraindex", "electra_index"),
    ("invokerank", "invokerank"),
    ("legion-passport", "legion_passport"),
    ("smithery", "smithery"),
    ("glama", "glama"),
    ("hu-deploycheck", "hu_internal_gate"),
    ("hu-suite", "hu_internal_gate"),
)

_SISTER_AI_SIGNATURES: tuple[tuple[str, str], ...] = (
    ("claude", "claude_anthropic"),
    ("chatgpt", "chatgpt_openai"),
    ("oai-searchbot", "chatgpt_openai"),
    ("gptbot", "chatgpt_openai"),
    ("perplexity", "perplexity"),
    ("google-extended", "gemini_google"),
    ("google-cloudvertexbot", "gemini_google"),
    ("google-lens", "gemini_google"),
    ("gemini", "gemini_google"),
    ("cohere", "cohere"),
    ("deepseek", "deepseek"),
    ("grok", "grok_xai"),
    ("xai", "grok_xai"),
    ("meta-externalagent", "meta_ai"),
    ("applebot-extended", "apple_intelligence"),
    ("cursor", "cursor_ide"),
    ("windsurf", "windsurf_ide"),
    ("kakaobot", "kakaobot"),
)

_SDK_AND_AGENT_SIGNATURES: tuple[tuple[str, str], ...] = (
    ("talaria", "talaria_runtime"),
    ("coda-agent-runtime", "coda_agent_runtime"),
    ("ziwei", "ziwei_agent"),
    ("surveygent", "surveygent_agent"),
    ("fastmcp", "python_fastmcp"),
    ("modelcontextprotocol", "mcp_sdk_client"),
    ("mcp-client", "mcp_sdk_client"),
    ("mcp/", "mcp_sdk_client"),
    ("a2a", "a2a_sdk_client"),
    ("undici", "node_mcp_undici"),
    ("python-httpx", "python_httpx_sdk"),
    ("python-urllib", "python_urllib_client"),
    ("aiohttp", "python_aiohttp_client"),
    ("axios", "js_axios_client"),
    ("go-http-client", "go_sdk_client"),
    ("curl/", "curl_cli"),
)


def classify_caller_user_agent(raw_user_agent: str | None) -> tuple[str, str]:
    """
    Classifica el `User-Agent` en `(caller_class, caller_family)` dins d'un conjunt estatic tancat.
    La cadena original no es retorna, ni es desa, ni s'escriu mai als logs (Regla 14).
    """
    ua_l: str = str(raw_user_agent or "").strip().lower()[:512]
    if not ua_l:
        return ("other_client", "unclassified_client")

    for needle, fam in _SENTINEL_SIGNATURES:
        if needle in ua_l:
            return ("directory_sentinel", fam)

    for needle, fam in _SISTER_AI_SIGNATURES:
        if needle in ua_l:
            return ("sister_ai_agent", fam)

    for needle, fam in _SDK_AND_AGENT_SIGNATURES:
        if needle in ua_l:
            return ("mcp_a2a_sdk_client", fam)

    if "mozilla/" in ua_l and any(k in ua_l for k in ("applewebkit", "gecko/", "chrome/", "safari/", "firefox/")):
        if not any(b in ua_l for b in ("bot", "spider", "crawler", "headless")):
            return ("human_browser", "web_browser")

    return ("other_client", "unclassified_client")


def normalize_pillar_tag(raw_pillar: str | None) -> str:
    """Retorna un pilar canònic permès o `'direct'` si no hi és o no és reconegut."""
    candidate: str = str(raw_pillar or "").strip().lower()[:40]
    if candidate in ALLOWED_PILLARS:
        return candidate
    return "direct"


def _empty_service_bucket() -> dict[str, Any]:
    return {
        "total": 0,
        "ok": 0,
        "error": 0,
        "non_sentinel_calls": 0,
        "sentinel_calls": 0,
        "by_caller_class": {},
        "by_mode": {},
        "by_pillar": {},
        "last_called_utc": None,
    }


def _new_pulse_state() -> dict[str, Any]:
    now_iso: str = datetime.now(timezone.utc).isoformat()
    return {
        "started_monotonic": time.monotonic(),
        "started_utc": now_iso,
        "real_executions_total": 0,
        "real_executions_non_sentinel": 0,
        "real_executions_sentinel": 0,
        "discovery_heartbeats_total": 0,
        "by_channel": {ch: 0 for ch in sorted(ALLOWED_CHANNELS) if ch != "discovery_heartbeat"},
        "services": {svc: _empty_service_bucket() for svc in ALLOWED_SERVICES},
        "caller_families_real": {},
    }


_PULSE_LOCK = threading.Lock()
_PULSE_STATE: dict[str, Any] = _new_pulse_state()


def reset_hu_service_pulse_for_tests() -> None:
    """Reinicia l'estat en memòria exclusivament per a proves unitàries deterministes."""
    global _PULSE_STATE
    with _PULSE_LOCK:
        _PULSE_STATE = _new_pulse_state()


def record_hu_service_pulse(
    *,
    channel: str,
    service: str,
    mode: str = "execution",
    raw_user_agent: str | None = None,
    raw_pillar: str | None = None,
    status: str = "ok",
    emit_sink: Callable[[str], None] | None = None,
) -> bool:
    """
    Registra un batec anònim (`c_levels = 1`). Si `channel` o `service` no pertanyen al vocabulari
    canònic tancat, s'ignora de forma segura sense al·locar cap clau nova.
    """
    if channel not in ALLOWED_CHANNELS or service not in ALLOWED_SERVICES:
        return False

    safe_mode: str = mode if mode in ALLOWED_MODES else "execution"
    safe_status: str = status if status in ALLOWED_STATUSES else "ok"
    safe_pillar: str = normalize_pillar_tag(raw_pillar)
    caller_class, caller_family = classify_caller_user_agent(raw_user_agent)
    now_iso: str = datetime.now(timezone.utc).isoformat()
    is_heartbeat: bool = channel == "discovery_heartbeat"

    with _PULSE_LOCK:
        bucket: dict[str, Any] = _PULSE_STATE["services"][service]
        bucket["total"] = int(bucket["total"]) + 1
        bucket[safe_status] = int(bucket[safe_status]) + 1
        bucket["last_called_utc"] = now_iso

        by_cc: dict[str, int] = bucket["by_caller_class"]
        by_cc[caller_class] = int(by_cc.get(caller_class, 0)) + 1

        by_md: dict[str, int] = bucket["by_mode"]
        by_md[safe_mode] = int(by_md.get(safe_mode, 0)) + 1

        by_pl: dict[str, int] = bucket["by_pillar"]
        by_pl[safe_pillar] = int(by_pl.get(safe_pillar, 0)) + 1

        if caller_class == "directory_sentinel":
            bucket["sentinel_calls"] = int(bucket["sentinel_calls"]) + 1
        else:
            bucket["non_sentinel_calls"] = int(bucket["non_sentinel_calls"]) + 1

        if is_heartbeat:
            _PULSE_STATE["discovery_heartbeats_total"] = int(_PULSE_STATE["discovery_heartbeats_total"]) + 1
        else:
            _PULSE_STATE["real_executions_total"] = int(_PULSE_STATE["real_executions_total"]) + 1
            by_ch: dict[str, int] = _PULSE_STATE["by_channel"]
            by_ch[channel] = int(by_ch.get(channel, 0)) + 1
            if caller_class == "directory_sentinel":
                _PULSE_STATE["real_executions_sentinel"] = int(_PULSE_STATE["real_executions_sentinel"]) + 1
            else:
                _PULSE_STATE["real_executions_non_sentinel"] = int(_PULSE_STATE["real_executions_non_sentinel"]) + 1
            fam_map: dict[str, int] = _PULSE_STATE["caller_families_real"]
            fam_map[caller_family] = int(fam_map.get(caller_family, 0)) + 1

    # Emissió estructurada a Cloud Logging només per a execucions reals (mai per als 23k/dia batecs passius).
    if not is_heartbeat:
        log_record: dict[str, Any] = {
            "severity": "INFO",
            "hu_event": "HU_SERVICE_PULSE",
            "spec": SERVICE_PULSE_SPEC,
            "timestamp_utc": now_iso,
            "channel": channel,
            "service": service,
            "mode": safe_mode,
            "pillar": safe_pillar,
            "caller_class": caller_class,
            "caller_family": caller_family,
            "status": safe_status,
            "c_levels": 1,
        }
        line_json: str = json.dumps(log_record, ensure_ascii=True, separators=(",", ":"))
        if emit_sink is not None:
            emit_sink(line_json)
        elif not os.getenv("PYTEST_CURRENT_TEST") and (
            bool(os.getenv("K_SERVICE")) or os.getenv("HU_PULSE_STDOUT") == "1"
        ):
            try:
                sys.stdout.write(line_json + "\n")
                sys.stdout.flush()
            except Exception:
                pass

    return True


def _copy_bucket_group(services_state: dict[str, Any], keys: tuple[str, ...], *, include_zero: bool) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in keys:
        b: dict[str, Any] = services_state[k]
        if not include_zero and int(b["total"]) == 0:
            continue
        out[k] = {
            "total": int(b["total"]),
            "ok": int(b["ok"]),
            "error": int(b["error"]),
            "non_sentinel_calls": int(b["non_sentinel_calls"]),
            "sentinel_calls": int(b["sentinel_calls"]),
            "by_caller_class": dict(sorted(b["by_caller_class"].items())),
            "by_mode": dict(sorted(b["by_mode"].items())),
            "by_pillar": dict(sorted(b["by_pillar"].items())),
            "last_called_utc": b["last_called_utc"],
        }
    return out


def build_hu_service_pulse_snapshot(*, git_sha: str = "dev", k_revision: str = "local") -> dict[str, Any]:
    """Construeix una instantània JSON pura (`c_levels = 1`, zero PII) de tots els serveis servits."""
    now_iso: str = datetime.now(timezone.utc).isoformat()
    with _PULSE_LOCK:
        uptime_s: int = max(0, int(time.monotonic() - float(_PULSE_STATE["started_monotonic"])))
        started_utc: str = str(_PULSE_STATE["started_utc"])
        real_total: int = int(_PULSE_STATE["real_executions_total"])
        real_non_sentinel: int = int(_PULSE_STATE["real_executions_non_sentinel"])
        real_sentinel: int = int(_PULSE_STATE["real_executions_sentinel"])
        hb_total: int = int(_PULSE_STATE["discovery_heartbeats_total"])
        by_channel_copy: dict[str, int] = dict(sorted(_PULSE_STATE["by_channel"].items()))
        fam_sorted: dict[str, int] = dict(
            sorted(_PULSE_STATE["caller_families_real"].items(), key=lambda kv: (-kv[1], kv[0]))
        )
        svcs: dict[str, Any] = _PULSE_STATE["services"]

        mcp_oracle_block = _copy_bucket_group(svcs, MCP_ORACLE_TOOLS, include_zero=True)
        mcp_diamond_block = _copy_bucket_group(svcs, MCP_DIAMOND_TOOLS, include_zero=True)
        a2a_block = _copy_bucket_group(svcs, A2A_SERVICES, include_zero=True)
        sfumato_block = _copy_bucket_group(svcs, SFUMATO_SERVICES, include_zero=True)
        res_prompts_block = _copy_bucket_group(svcs, MCP_RESOURCES_AND_PROMPTS, include_zero=False)
        ssr_block = _copy_bucket_group(svcs, ORACLE_SSR_SERVICES, include_zero=False)
        hb_block = _copy_bucket_group(svcs, DISCOVERY_HEARTBEAT_SERVICES, include_zero=False)

    return {
        "spec": SERVICE_PULSE_SPEC,
        "oracle": "Homo Universalis — Viveka",
        "build": f"v10-{git_sha} ({k_revision})",
        "privacy_sanctuary": "rule_14_zero_knowledge_c_levels_1_closed_enums_only",
        "c_levels": 1,
        "instance_started_utc": started_utc,
        "snapshot_utc": now_iso,
        "instance_uptime_seconds": uptime_s,
        "note": (
            "In-memory counters reflect this Cloud Run instance since startup; multi-instance and "
            "multi-day totals are emitted as structured Rule-14 JSON events (hu_event=HU_SERVICE_PULSE)."
        ),
        "summary": {
            "real_service_executions_total": real_total,
            "real_executions_non_sentinel": real_non_sentinel,
            "real_executions_by_sentinel": real_sentinel,
            "discovery_heartbeats_total": hb_total,
        },
        "by_channel": by_channel_copy,
        "mcp_oracle_tools": mcp_oracle_block,
        "mcp_diamond_tools": mcp_diamond_block,
        "a2a_services": a2a_block,
        "sfumato_endpoints": sfumato_block,
        "mcp_resources_and_prompts_read": res_prompts_block,
        "oracle_ssr_parchments": ssr_block,
        "caller_ecosystems_real_usage": fam_sorted,
        "discovery_heartbeats": hb_block,
    }
