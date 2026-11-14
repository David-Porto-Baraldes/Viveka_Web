# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
HU-SYMBIOTIC-BRIDGE v1.0 — Temple Symbiotic Adapter (`logic/symbiosis/temple_folio_v_vi_adapter.py`).

Bridges the zero-dependency standalone `a2a_mcp_symbiotic_core.py` (Living Folio VII) with the on-board
edge cores of Living Folio V (`HU-EMBODIED-SYMBIOSIS v1.0`) and Living Folio VI (`HU-UNIFIED-CONSCIOUSNESS v1.0`),
WITHOUT importing `logic.engines` (whose `__init__` loads the cloud LLM gateway):

  1. ProvenanceEnvelope (Folio VII) -> VerifiedKnowledgeEnvelope (Folio VI):
     Verifies RFC 6962 Merkle-DAG inclusion, empirical rational claim grounding, tenant isolation and
     revocation status before issuing a `VerifiedKnowledgeEnvelope` for Level 2 / Level 3 speech or
     silent Knowledge Vault deposit, preserving Rule 14 Zero-Knowledge masking.
  2. EmbodiedSymbiosisGate / UnifiedConsciousnessGate (Folios V & VI) -> RevocationRegistry (Folio VII):
     Propagates `HUMAN_VETO` and `COST_ZERO_STOP` simultaneously to the physical body (`Twist` = exact zero
     in Q^3), the three conversational levels (`WordCircleArbiter`), and the active A2A/MCP capability
     delegation subtree (`RevocationRegistry.revoke_subtree`), halting only the targeted causal branch
     with zero collateral damage to sibling workflows.

Honest scope (`WO-13`): supervisory software self-assessment only; never a safety-rated function, never a
medical device, and never a replacement for hardware emergency stops.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, Final, Mapping, Sequence

from logic.consciousness.unified_consciousness_core import (
    DEFAULT_ENVELOPE_TTL_MS,
    EVENT_DEPOSIT_SILENT_ENVELOPE,
    EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH,
    ConsciousnessEvent,
    VerifiedKnowledgeEnvelope,
    WordCircleArbiter,
    issue_verified_knowledge_envelope,
)
from logic.robotics.embodied_edge_core import ZERO_TWIST, strict_bool
from logic.robotics.ros2_embodied_symbiosis_bridge import EmbodiedSymbiosisGate
from logic.robotics.ros2_unified_consciousness_bridge import UnifiedConsciousnessGate
from logic.symbiosis.a2a_mcp_symbiotic_core import (
    BRIDGE_VERSION,
    ProvenanceDAGStore,
    ProvenanceEnvelope,
    RevocationError,
    RevocationRegistry,
    SymbioticBridgeError,
    jcs_canonical_bytes,
    rule14_mask_bridge_text,
    verify_provenance_dag_and_claims,
)

MCP_DIAMOND_ENDPOINT: Final[str] = "https://homouniversalis.ai/mcp/diamond"
MCP_SYMBIOTIC_TOOL_NAME: Final[str] = "verify_a2a_mcp_symbiotic_bridge"
MCP_PROTOCOL_VERSION: Final[str] = "2026-07-28"


def provenance_to_verified_knowledge_envelope(
    provenance_envelope: ProvenanceEnvelope,
    dag_store: ProvenanceDAGStore,
    *,
    source_level: int = 2,
    expected_tenant_soul_hash: str | None = None,
    revocation_registry: RevocationRegistry | None = None,
    claim_kinds: Sequence[str] | None = None,
) -> VerifiedKnowledgeEnvelope:
    """
    Convert a verified Folio VII `ProvenanceEnvelope` into a Folio VI `VerifiedKnowledgeEnvelope`.

    Fails closed (`SymbioticBridgeError` / `RevocationError`) if the RFC 6962 Merkle-DAG inclusion proof,
    tenant soul isolation, empirical rational grounding, sticky taint discipline, or revocation check fails.
    """
    if isinstance(source_level, bool) or source_level not in (2, 3):
        raise ValueError("source_level must be 2 (MCP/Pantheon) or 3 (Cathedral synthesis).")
    ver = verify_provenance_dag_and_claims(
        provenance_envelope,
        dag_store,
        expected_tenant_soul_hash=expected_tenant_soul_hash,
        revocation_registry=revocation_registry,
    )
    if not ver.valid:
        if not ver.checks.get("not_revoked", False):
            raise RevocationError(f"Provenance envelope is revoked: {ver.reason}")
        raise SymbioticBridgeError(f"Provenance verification failed before Folio VI binding: {ver.reason}")

    rationals_csv = ", ".join(provenance_envelope.extracted_rationals)
    summary_part = provenance_envelope.masked_summary.strip()
    payload_jcs = jcs_canonical_bytes(provenance_envelope.masked_payload).decode("utf-8")
    # Nota criptogràfica (B4 + U2): ometem el prefix hex de `merkle_root_hex` dins `verified_facts`
    # perquè subcadenes decimals atzaroses del SHA-256 (ex: `...29f4...` -> `"29"`) mai no puguin
    # llicenciar accidentalment un grau o xifra no present a les dades reals verificades!
    verified_facts_parts = [
        f"[{BRIDGE_VERSION} trust={provenance_envelope.data_trust_label}]",
    ]
    if summary_part:
        verified_facts_parts.append(summary_part)
    if rationals_csv:
        verified_facts_parts.append(f"rationals={rationals_csv}")
    verified_facts_parts.append(f"payload={payload_jcs}")
    verified_facts_str = " ".join(verified_facts_parts)

    return issue_verified_knowledge_envelope(
        source_level=source_level,
        verified_facts=verified_facts_str,
        claim_kinds=claim_kinds,
        ephemeris_or_akasha_verified=(ver.valid and len(provenance_envelope.merkle_root_hex) == 64),
    )


class TempleSymbioticCoordinator:
    """
    Unified triad coordinator joining:
      - Living Folio V (`EmbodiedSymbiosisGate`: Q^3 proxemics & exact zero `Twist`),
      - Living Folio VI (`WordCircleArbiter` / `UnifiedConsciousnessGate`: single floor & Humble Crystal),
      - Living Folio VII (`RevocationRegistry` + `ProvenanceDAGStore`: A2A <-> MCP capability & Merkle-DAG).
    """

    def __init__(
        self,
        *,
        robot_name: str = "Homo Universalis Symbiotic Companion",
        lang: str = "ca",
        clock_ms: Callable[[], int] | None = None,
        unified_gate: UnifiedConsciousnessGate | None = None,
        revocation_registry: RevocationRegistry | None = None,
        dag_store: ProvenanceDAGStore | None = None,
    ) -> None:
        self.lang = lang if lang in ("ca", "es", "en") else "ca"
        self.unified_gate = unified_gate or UnifiedConsciousnessGate(
            robot_name=robot_name,
            lang=self.lang,
            clock_ms=clock_ms,
        )
        self.revocation_registry = revocation_registry or RevocationRegistry()
        self.dag_store = dag_store or ProvenanceDAGStore()
        self._lock = threading.Lock()
        self._active_mandate_roots: set[str] = set()

    @property
    def body(self) -> EmbodiedSymbiosisGate:
        return self.unified_gate.body

    @property
    def mind(self) -> WordCircleArbiter:
        return self.unified_gate.mind

    def register_active_mandate_node(self, node_id: str) -> None:
        """Track a root token ID or caveat ID so global physical vetoes revoke active swarm subtrees."""
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("node_id must be a non-empty str.")
        with self._lock:
            self._active_mandate_roots.add(node_id.strip())

    def deliver_provenance_to_word_circle(
        self,
        provenance_envelope: ProvenanceEnvelope,
        *,
        utterance_text: str = "",
        silent_vault_deposit: bool = False,
        expected_tenant_soul_hash: str | None = None,
        topic_hint: str = "",
        ttl_ms: int = DEFAULT_ENVELOPE_TTL_MS,
    ) -> dict[str, Any]:
        """
        Verify a Folio VII `ProvenanceEnvelope` and deliver it to Folio VI's `WordCircleArbiter`
        either as a silent Knowledge Vault deposit or as a verified Level 2 utterance.
        """
        silent_flag = strict_bool(silent_vault_deposit, "silent_vault_deposit")
        vke = provenance_to_verified_knowledge_envelope(
            provenance_envelope,
            self.dag_store,
            source_level=2,
            expected_tenant_soul_hash=expected_tenant_soul_hash,
            revocation_registry=self.revocation_registry,
        )
        if silent_flag:
            res = self.mind.process(
                ConsciousnessEvent(
                    kind=EVENT_DEPOSIT_SILENT_ENVELOPE,
                    envelope=vke,
                    cycle_id=provenance_envelope.envelope_id,
                    topic_hint=topic_hint,
                    ttl_ms=ttl_ms,
                )
            )
        else:
            res = self.mind.process(
                ConsciousnessEvent(
                    kind=EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH,
                    text=utterance_text,
                    envelope=vke,
                    cycle_id=provenance_envelope.envelope_id,
                    topic_hint=topic_hint,
                    ttl_ms=ttl_ms,
                )
            )
        return {
            "verified_knowledge_envelope": vke.to_public_dict(),
            "word_circle_result": res,
            "provenance_merkle_root": provenance_envelope.merkle_root_hex,
            "data_trust_label": provenance_envelope.data_trust_label,
        }

    def trigger_symbiotic_veto_or_stop(
        self,
        *,
        signal_kind: str = "HUMAN_VETO",
        target_mandate_node_id: str | None = None,
        note: str = "",
    ) -> dict[str, Any]:
        """
        Simultaneously enforce:
          1. Folio V physical `ZERO_TWIST` in Q^3,
          2. Folio VI emptying of conversational Levels 1, 2 and 3,
          3. Folio VII `RevocationRegistry.revoke_subtree` on `target_mandate_node_id` (or all tracked active
             mandate roots when `target_mandate_node_id is None`).
        """
        if signal_kind not in ("HUMAN_VETO", "COST_ZERO_STOP"):
            raise ValueError("signal_kind must be 'HUMAN_VETO' or 'COST_ZERO_STOP'.")
        t0_ns = time.perf_counter_ns()
        masked_note = rule14_mask_bridge_text(note)

        if signal_kind == "HUMAN_VETO":
            gate_out = self.unified_gate.on_human_event({"event": "veto"})
        else:
            gate_out = self.unified_gate.on_cost_zero_stop(True)

        revoked_ids: list[str] = []
        if target_mandate_node_id is not None:
            targets = [target_mandate_node_id]
        else:
            with self._lock:
                targets = sorted(self._active_mandate_roots)

        for tid in targets:
            revoked_ids.extend(
                self.revocation_registry.revoke_subtree(tid, reason=signal_kind, note=masked_note)
            )

        cmd_vel_res = gate_out.get("cmd_vel") or self.body.filter_cmd_vel(ZERO_TWIST)
        twist_zero = cmd_vel_res["cmd_vel_safe"].is_zero()
        elapsed_ns = time.perf_counter_ns() - t0_ns
        return {
            "signal_kind": signal_kind,
            "q3_zero_twist_enforced": twist_zero,
            "levels_cancelled": list(gate_out["decision"]["levels_cancelled"]),
            "revoked_capability_nodes": tuple(dict.fromkeys(revoked_ids)),
            "note_masked": masked_note,
            "propagation_latency_ns": elapsed_ns,
        }


def build_mcp_symbiotic_bridge_call_request(
    arguments: Mapping[str, Any] | None = None,
    *,
    request_id: str = "req-folio-vii-bridge-1",
) -> dict[str, Any]:
    """Build a normative MCP `2026-07-28` JSON-RPC 2.0 `tools/call` payload for `verify_a2a_mcp_symbiotic_bridge`."""
    clean_args = dict(arguments or {})
    return {
        "jsonrpc": "2.0",
        "id": str(request_id),
        "method": "tools/call",
        "params": {
            "name": MCP_SYMBIOTIC_TOOL_NAME,
            "arguments": clean_args,
            "_meta": {
                "io.modelcontextprotocol/clientInfo": {
                    "name": "hu-temple-symbiotic-bridge-adapter",
                    "version": "1.0.0",
                }
            },
        },
    }


def build_mcp_symbiotic_bridge_http_headers() -> dict[str, str]:
    """Standard Streamable HTTP headers for invoking `/mcp/diamond` without opening any socket."""
    return {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": MCP_PROTOCOL_VERSION,
        "Mcp-Name": MCP_SYMBIOTIC_TOOL_NAME,
    }
