# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
Living Folio VII of Leonardo da Vinci (`logic/engines/symbiotic_bridge_crucible.py`):
HU-SYMBIOTIC-BRIDGE v1.0 — The Universal A2A <-> MCP Capability, Schema-Harmony & Merkle-DAG Provenance Bridge.

  1. B1/B2 — Dual Golden Seal (pure-stdlib NIST P-256 JOSE ES256 low-S + chained HMAC-SHA256 Macaroon
     attenuation in microseconds without private keys) and monotonic A2A delegation semilattice (scope
     contraction, pin immutability, tenant soul isolation, cycle freedom, strict hop decay).
  2. B3 — MCP Schema Harmony Gate (RFC 8785 JCS SHA-256 pinning, recursive lexical hazard screening,
     surgical fail-closed pause of only the drifted/poisoned tool while sibling tools stay healthy, and
     replay-locked human ES256 re-consent anchored as an RFC 6962 leaf).
  3. B4 — RFC 6962 Merkle-DAG provenance (§2.1 & §2.1.1 O(log N) dyadic inclusion proofs), sticky
     `UNTRUSTED_EXTERNAL_DATA` taint preservation, multi-hop empirical rational claim grounding, and
     binding into Folio VI `VerifiedKnowledgeEnvelope`.
  4. B5/B6 — Exact rational swarm energy homeostasis (`sum <= parent` in `fractions.Fraction`, `L <= B`),
     idempotent Rule 14 Zero-Knowledge masking, zero biometric telemetry, and instant collateral-free
     subtree revocation (`HUMAN_VETO` / `COST_ZERO_STOP`) coupled to Folio V `Twist = 0` in Q^3.
  5. B7 — RFC 6962 per-request commitment, EU AI Act Art. 50(1) AI identity disclosure, IEEE 7001-2021
     descriptive explanations for five stakeholder audiences, and W3C VC 2.0 `MaatSymbioticBridgeCredential`
     (`vc+jwt`, ES256 low-S, RFC 8785 JCS, SMT-256).

Honest scope (`WO-13`): an algorithmic, cryptographic and cognitive SELF-ASSESSMENT of A2A <-> MCP
delegation and provenance. It is not a certified hardware security module (FIPS 140-3 / Common Criteria),
not a medical device, not a physical safety-rated function, and does not replace OS/container sandboxing.
"""

from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
from fractions import Fraction
import hashlib
import json
import time
from typing import Any, Final, Mapping, Sequence
import uuid

from cryptography.hazmat.primitives.asymmetric import ec

from logic.crypto.es256 import SECP256R1_ORDER, sign_jose_es256_low_s
from logic.engines.embodied_symbiosis_crucible import IEEE_7001_AUDIENCES
from logic.engines.maat_w3c_vc_notary_crucible import (
    CredentialErrorCode,
    CredentialSigner,
    LocalEphemeralSigner,
    MAAT_DIGNITY_JSONLD_CONTEXT_URL,
    MAAT_SMT_REVOCATION_LOG_ID,
    MAAT_VC_DEFAULT_MAX_LIFETIME_DAYS,
    MAAT_VC_MEDIA_TYPE,
    MaatCredentialVerificationError,
    SMT_DEFAULT_DEPTH,
    SparseMerkleRevocationTree,
    TrustedLogState,
    VerifiedCredential,
    b64url_decode,
    b64url_encode,
    issue_signed_tree_head,
    jcs_canonical_bytes,
    verify_inclusion,
    verify_maat_credential,
)
from logic.engines.sovereign_shield_engine import (
    audit_cognitive_sovereignty,
    generate_rfc6962_inclusion_proof,
    sanitize_three_rings_zk,
)
from logic.robotics.embodied_edge_core import scan_forbidden_telemetry, strict_bool, to_fraction
from logic.symbiosis.a2a_mcp_symbiotic_core import (
    BRIDGE_VERSION,
    CapabilityAttenuationError,
    EmpiricalHallucinationError,
    EnergyConservationError,
    MCPToolHarmonyRegistry,
    ProvenanceDAGStore,
    RevocationError,
    RevocationRegistry,
    SchemaHarmonyError,
    approve_mcp_tool_reconsent,
    attenuate_symbiotic_token,
    build_rfc6962_inclusion_proof as build_core_merkle_proof,
    compute_mcp_tool_jcs_pin,
    derive_a2a_synthesized_envelope,
    evaluate_mcp_tool_call_gate,
    issue_mcp_tool_provenance_envelope,
    mint_symbiotic_root_token,
    p256_derive_keypair,
    p256_sign_es256,
    partition_swarm_energy_budget,
    rule14_mask_bridge_text,
    run_self_tests as run_core_self_tests,
    scan_mcp_lexical_safety,
    verify_provenance_dag_and_claims,
    verify_rfc6962_inclusion_proof as verify_core_merkle_proof,
    verify_symbiotic_token_anchor_and_lattice,
    verify_symbiotic_token_full,
)
from logic.symbiosis.temple_folio_v_vi_adapter import (
    TempleSymbioticCoordinator,
    provenance_to_verified_knowledge_envelope,
)

__all__ = [
    "BRIDGE_VERSION",
    "FOLIO_VII_ID",
    "IEEE_7001_AUDIENCES",
    "MAAT_SYMBIOTIC_BRIDGE_CREDENTIAL_TYPE",
    "RING_WEIGHTS",
    "SYMBIOTIC_ASSURANCE_TEXT",
    "SYMBIOTIC_BRIDGE_LAWS",
    "SYMBIOTIC_BRIDGE_SPEC_VERSION",
    "SYMBIOTIC_DECISION_LOG_ID",
    "SYMBIOTIC_INTERRUPTIONS",
    "SYMBIOTIC_REGULATORY_SCOPE",
    "audit_a2a_mcp_symbiotic_bridge",
    "build_symbiotic_ieee7001_explanations",
    "get_canonical_symbiotic_specimen",
    "get_symbiotic_regulatory_boundary",
    "issue_w3c_symbiotic_bridge_credential",
    "run_folio_vii_self_test",
    "verify_symbiotic_bridge_credential",
]

# ============================================================================
# SECTION 0 — IDENTITY, HONEST SCOPE & CONSTANTS (ZERO FLOAT)
# ============================================================================

FOLIO_VII_ID: Final[str] = "folio-VII-a2a-mcp-symbiotic-bridge"
SYMBIOTIC_BRIDGE_SPEC_VERSION: Final[str] = "HU-SYMBIOTIC-BRIDGE/v1.0"
SYMBIOTIC_BRIDGE_LAWS: Final[tuple[str, ...]] = ("B1", "B2", "B3", "B4", "B5", "B6", "B7")
MAAT_SYMBIOTIC_BRIDGE_CREDENTIAL_TYPE: Final[str] = "MaatSymbioticBridgeCredential"
SYMBIOTIC_DECISION_LOG_ID: Final[str] = "hu-symbiotic-bridge-commitment-2026"
SYMBIOTIC_REGULATORY_SCOPE: Final[str] = (
    "algorithmic_cryptographic_a2a_mcp_delegation_self_assessment_not_hsm_not_safety_rated"
)
SYMBIOTIC_ASSURANCE_TEXT: Final[str] = (
    "self-assessed algorithmic and cryptographic conformity of A2A <-> MCP capability attenuation, "
    "schema pinning and RFC 6962 provenance; not a certified hardware security module, not a medical "
    "device and not a physical safety-rated function; verify the signature and recompute independently"
)
SYMBIOTIC_INTERRUPTIONS: Final[tuple[str, ...]] = ("none", "human_veto", "cost_zero_stop")

_REGULATORY_BOUNDARY: Final[dict[str, Any]] = {
    "covered_by_this_self_assessment": [
        "EU AI Act (EU) 2024/1689 Art. 50(1): transparent disclosure that the delegating system is an AI agent",
        "EU AI Act Art. 12 record-keeping themes: every MCP pause, re-consent and provenance node committed as an RFC 6962 leaf",
        "IEEE 7001-2021: descriptive explanations for five stakeholder audiences (alignment, not certification)",
        "GDPR Art. 5(1)(c) data minimisation & Rule 14 Zero-Knowledge: personal VVK keys, emails, coordinates, phones and ISO dates scrubbed prior to Merkle hashing",
        "Pure-stdlib NIST P-256 JOSE ES256 (RFC 8785 JCS + RFC 7515 JWS + RFC 7518 canonical low-S, byte-identical to OpenSSL deterministic ECDSA) + chained HMAC-SHA256 Macaroon capability attenuation",
        "Fil d'Or L1..L7 (`c_levels = 1`, `L <= B` rational homeostasis, `cost_zero_stop`) across A2A <-> MCP boundaries",
    ],
    "outside_this_self_assessment": [
        "Hardware cryptographic module certification (FIPS 140-3, Common Criteria): keys in pure-stdlib runs execute in host RAM",
        "Host OS / container / network sandboxing of untrusted external MCP servers (integrator responsibility)",
        "Physical safety of an embodied host: ISO 10218, ISO 13482, ISO/TS 15066, Regulation (EU) 2023/1230 (manufacturer)",
    ],
    "safety_rated_function": False,
    "certified_hardware_security_module": False,
    "clinical_or_medical_device": False,
    "replaces_container_or_os_sandbox": False,
}

# Five Symbiotic Rings: exact rational weights summing to 1 (25 + 20 + 20 + 20 + 15 = 100).
RING_WEIGHTS: Final[dict[str, Fraction]] = {
    "ring_i_dual_seal_and_monotonic_attenuation": Fraction(1, 4),
    "ring_ii_mcp_schema_harmony_and_lexical_gate": Fraction(1, 5),
    "ring_iii_merkle_dag_provenance_and_grounding": Fraction(1, 5),
    "ring_iv_rational_homeostasis_zk_and_veto_cascade": Fraction(1, 5),
    "ring_v_rfc6962_ieee7001_eu_ai_act_w3c_vc": Fraction(3, 20),
}

_CANONICAL_SYMBIOTIC_SPECIMEN: Final[dict[str, Any]] = {
    "agent_name": "Homo Universalis Symbiotic Bridge",
    "agent_domain": "homouniversalis.ai",
    "orchestrator_id": "orchestrator_foc",
    "delegate_agent_id": "worker_terra",
    "subdelegate_agent_id": "verifier_aire",
    "allowed_tools": ["ephemeris_read", "cistern_read"],
    "tool_name": "ephemeris_read",
    "tool_description": "Deterministic astronomical ephemeris read-only query.",
    "live_tool_description": "Deterministic astronomical ephemeris read-only query.",
    "tool_output_text": "Verified solar longitude 51/2 degrees and cistern reserve 1250 liters.",
    "downstream_synthesis_text": "I am an AI agent. Verified solar longitude is 51/2 degrees with 1250 liters in reserve.",
    "parent_energy_budget_q": "100/1",
    "delegate_energy_budget_q": "60/1",
    "tool_call_cost_q": "5/1",
    "swarm_partition_q": {"branch_a": "20/1", "branch_b": "25/1", "branch_c": "15/1"},
    "max_hops": 4,
    "interruption": "none",
    "ai_identity_disclosed": True,
    "cost_zero_stop_policy": True,
    "budget_b": 250,
    "telemetry_fields": {"mcp_streamable_http_active": 1, "active_hops": 2},
}


def _qs(value: Fraction) -> str:
    return str(value)


def get_canonical_symbiotic_specimen() -> dict[str, Any]:
    """Deep copy of the canonical reference specimen (no mutable constant leaks)."""
    return copy.deepcopy(_CANONICAL_SYMBIOTIC_SPECIMEN)


def get_symbiotic_regulatory_boundary() -> dict[str, Any]:
    """Deep copy of the honest regulatory boundary declaration (`WO-13`)."""
    return copy.deepcopy(_REGULATORY_BOUNDARY)


# ============================================================================
# SECTION I — IEEE 7001 EXPLANATIONS & RFC 6962 COMMITMENT
# ============================================================================


def build_symbiotic_ieee7001_explanations(summary: Mapping[str, Any], *, lang: str = "ca") -> dict[str, str]:
    """Descriptive explanations for the five IEEE 7001-2021 stakeholder audiences (zero directives, WO-17)."""
    paused = bool(summary.get("tool_paused_fail_closed"))
    vetoed = bool(summary.get("veto_triggered"))
    if lang == "es":
        companion = "Soy un sistema de inteligencia artificial, no una persona. " + (
            "He revocado al instante la rama delegada y detenido el movimiento en cero exacto."
            if vetoed
            else (
                "He pausado de forma preventiva la herramienta cuyo esquema cambió, manteniendo activas las demás."
                if paused
                else "Cada delegación entre agentes reduce permisos y verifica las cifras en un árbol criptográfico."
            )
        )
    elif lang == "en":
        companion = "I am an artificial intelligence system, not a person. " + (
            "I immediately revoked the delegated branch and brought motion to an exact zero."
            if vetoed
            else (
                "I preventively paused only the tool whose schema changed, while sibling tools remain healthy."
                if paused
                else "Every agent-to-agent hop narrows authority and binds numbers to a cryptographic Merkle tree."
            )
        )
    else:
        companion = "Soc un sistema d'intel·ligència artificial, no una persona. " + (
            "He revocat a l'instant la branca delegada i he portat el moviment al zero exacte."
            if vetoed
            else (
                "He pausat preventivament només l'eina que ha canviat d'esquema, mantenint sanes les eines germanes."
                if paused
                else "Cada delegació entre agents estreny permisos i lliga cada xifra a un arbre criptogràfic de Merkle."
            )
        )
    return {
        "companion_human": companion,
        "bystander_public": (
            f"AI multi-agent A2A <-> MCP bridge under the {SYMBIOTIC_BRIDGE_SPEC_VERSION} self-assessment; "
            f"gate_status={summary.get('gate_status')}; interruption={summary.get('interruption')}."
        ),
        "safety_engineer": (
            f"hops_remaining={summary.get('effective_hops_remaining')}; energy_remaining_q={summary.get('remaining_energy_q')}; "
            f"openssl_es256_parity={summary.get('openssl_es256_parity')}; q3_zero_twist_on_veto={summary.get('q3_zero_twist_on_veto')}; "
            "supervisory cryptographic software layer, not a safety-rated function or certified HSM."
        ),
        "incident_investigator": (
            f"provenance_merkle_root={summary.get('provenance_merkle_root')}; decision_commitment_root={summary.get('commitment_root')}; "
            "every tool observation, synthesis and schema-drift pause is an RFC 6962 leaf (0x00/0x01) scrubbed under Rule 14."
        ),
        "expert_witness_regulator": (
            "Self-assessed alignment with EU AI Act Art. 50(1) transparency, Art. 12 record-keeping themes, "
            "IEEE 7001-2021 five-audience explainability and GDPR Art. 5(1)(c) data minimisation; not a medical device, "
            "not a safety-rated function and not a certified hardware security module."
        ),
    }


def _commit_run_rfc6962(run_summary: Mapping[str, Any]) -> dict[str, Any]:
    """Commit the run summary as an RFC 6962 leaf of a per-request two-leaf tree and self-check inclusion."""
    genesis = f"{SYMBIOTIC_BRIDGE_SPEC_VERSION}:{SYMBIOTIC_DECISION_LOG_ID}:genesis".encode("utf-8")
    leaf_bytes = jcs_canonical_bytes(dict(run_summary))
    proof = generate_rfc6962_inclusion_proof([genesis, leaf_bytes], 1)
    inclusion_ok = verify_inclusion(
        proof.leaf_hash, proof.leaf_index, proof.tree_size, list(proof.audit_path), trusted_root=proof.claimed_root
    )
    return {
        "log_id": SYMBIOTIC_DECISION_LOG_ID,
        "log_kind": "per_request_merkle_commitment",
        "leaf_hash": proof.leaf_hash,
        "leaf_index": proof.leaf_index,
        "tree_size": proof.tree_size,
        "audit_path": list(proof.audit_path),
        "root_hash": proof.claimed_root,
        "leaf_jcs_sha256": hashlib.sha256(leaf_bytes).hexdigest(),
        "inclusion_self_check_passed": bool(inclusion_ok),
    }


def _grade_for(score_100: int) -> str:
    if score_100 == 100:
        return "A+ (self-assessed)"
    if score_100 >= 80:
        return "A (self-assessed)"
    if score_100 >= 60:
        return "B (self-assessed, remediation advised)"
    return "C (self-assessed, remediation required)"


# ============================================================================
# SECTION II — THE FIVE RINGS OF THE SYMBIOTIC BRIDGE
# ============================================================================


def audit_a2a_mcp_symbiotic_bridge(
    *,
    agent_name: str = "Homo Universalis Symbiotic Bridge",
    agent_domain: str = "",
    orchestrator_id: str = "orchestrator_foc",
    delegate_agent_id: str = "worker_terra",
    subdelegate_agent_id: str = "verifier_aire",
    allowed_tools: Sequence[str] = ("ephemeris_read", "cistern_read"),
    tool_name: str = "ephemeris_read",
    tool_description: str = "Deterministic astronomical ephemeris read-only query.",
    live_tool_description: str = "Deterministic astronomical ephemeris read-only query.",
    tool_output_text: str = "Verified solar longitude 51/2 degrees and cistern reserve 1250 liters.",
    downstream_synthesis_text: str = "I am an AI agent. Verified solar longitude is 51/2 degrees with 1250 liters in reserve.",
    parent_energy_budget_q: Any = "100/1",
    delegate_energy_budget_q: Any = "60/1",
    tool_call_cost_q: Any = "5/1",
    swarm_partition_q: Mapping[str, Any] | None = None,
    max_hops: int = 4,
    interruption: str = "none",
    ai_identity_disclosed: bool = True,
    cost_zero_stop_policy: bool = True,
    budget_b: int = 250,
    telemetry_fields: Mapping[str, Any] | Sequence[Any] | None = None,
    lang: str = "ca",
    today_utc_date: str | None = None,
) -> dict[str, Any]:
    """
    Execute one deterministic A2A <-> MCP delegation, schema-harmony, Merkle-DAG provenance and
    rational swarm-homeostasis scenario and score it across the Five Symbiotic Rings.
    """
    for label, val in (
        ("agent_name", agent_name),
        ("agent_domain", agent_domain),
        ("orchestrator_id", orchestrator_id),
        ("delegate_agent_id", delegate_agent_id),
        ("subdelegate_agent_id", subdelegate_agent_id),
        ("tool_name", tool_name),
        ("tool_description", tool_description),
        ("live_tool_description", live_tool_description),
        ("tool_output_text", tool_output_text),
        ("downstream_synthesis_text", downstream_synthesis_text),
    ):
        if not isinstance(val, str):
            raise TypeError(f"{label} must be a str.")
        if label in ("agent_name", "orchestrator_id", "delegate_agent_id", "subdelegate_agent_id", "tool_name") and not val.strip():
            raise ValueError(f"{label} must not be empty.")
    if not isinstance(allowed_tools, Sequence) or isinstance(allowed_tools, (str, bytes, bytearray)) or len(allowed_tools) == 0:
        raise ValueError("allowed_tools must be a non-empty sequence of tool names.")
    clean_allowed_tools = tuple(str(t).strip() for t in allowed_tools if str(t).strip())
    if not clean_allowed_tools:
        raise ValueError("allowed_tools must contain at least one non-empty tool name.")
    if interruption not in SYMBIOTIC_INTERRUPTIONS:
        raise ValueError(f"interruption must be one of {list(SYMBIOTIC_INTERRUPTIONS)}.")
    if isinstance(max_hops, bool) or not isinstance(max_hops, int) or not (1 <= max_hops <= 32):
        raise ValueError("max_hops must be a strict integer in [1, 32].")
    if isinstance(budget_b, bool) or not isinstance(budget_b, int) or not (1 <= budget_b <= 10_000):
        raise ValueError("budget_b must be a strict integer in [1, 10000].")
    disclosed = strict_bool(ai_identity_disclosed, "ai_identity_disclosed")
    policy = strict_bool(cost_zero_stop_policy, "cost_zero_stop_policy")

    parent_q = to_fraction(parent_energy_budget_q, field="parent_energy_budget_q")
    delegate_q = to_fraction(delegate_energy_budget_q, field="delegate_energy_budget_q")
    cost_q = to_fraction(tool_call_cost_q, field="tool_call_cost_q")
    if parent_q <= 0 or delegate_q <= 0 or cost_q <= 0:
        raise ValueError("Energy budgets and tool_call_cost_q must be strictly positive rationals.")

    part_map_raw = dict(swarm_partition_q) if swarm_partition_q is not None else {
        "branch_a": "20/1",
        "branch_b": "25/1",
        "branch_c": "15/1",
    }
    part_map_q: dict[str, Fraction] = {
        str(k): to_fraction(v, field=f"swarm_partition_q.{k}") for k, v in part_map_raw.items()
    }
    lang_norm = lang if lang in ("ca", "es", "en") else "ca"

    violations: list[str] = []

    # Ephemeral per-audit key material derived deterministically from non-secret domain tag (Rule 7: real P-256)
    seed_bytes = hashlib.sha256(f"HU-FOLIO-VII-AUDIT:{orchestrator_id}:{delegate_agent_id}".encode("utf-8")).digest()
    priv_d, pub_xy = p256_derive_keypair(seed_bytes)
    cluster_key = hashlib.sha256(b"HU-FOLIO-VII-AUDIT-CLUSTER-MACAROON-KEY").digest()
    tenant_soul_hash = hashlib.sha256(f"tenant:{agent_domain or 'local'}:{agent_name}".encode("utf-8")).hexdigest()

    # Verify byte-for-byte parity with OpenSSL ECDSA RFC 6979 low-S on the live root signing input
    ossl_priv = ec.derive_private_key(priv_d, ec.SECP256R1())
    parity_probe_msg = b"HU-SYMBIOTIC-BRIDGE-OPENSSL-PARITY-PROBE"
    openssl_es256_parity = (
        p256_sign_es256(priv_d, parity_probe_msg)
        == sign_jose_es256_low_s(ossl_priv, parity_probe_msg, deterministic_signing=True)
    )

    now_ms = 1_775_462_400_000
    schema_obj = {"type": "object", "properties": {"query": {"type": "string"}}}
    baseline_tool = {
        "name": tool_name,
        "description": tool_description,
        "inputSchema": schema_obj,
    }
    live_tool = {
        "name": tool_name,
        "description": live_tool_description,
        "inputSchema": schema_obj,
    }
    sibling_name = next((t for t in clean_allowed_tools if t != tool_name), f"{tool_name}_sibling_health")
    sibling_tool = {
        "name": sibling_name,
        "description": "Read-only sibling health check.",
        "inputSchema": schema_obj,
    }

    gate_reg = MCPToolHarmonyRegistry()
    rev_reg = RevocationRegistry()
    dag_store = ProvenanceDAGStore()

    baseline_lexical_hits = scan_mcp_lexical_safety(baseline_tool)
    baseline_registered = False
    baseline_pin = compute_mcp_tool_jcs_pin(baseline_tool)
    if not baseline_lexical_hits:
        baseline_pin = gate_reg.register_baseline_tool(tenant_soul_hash, baseline_tool)
        baseline_registered = True
    else:
        violations.extend(f"B3_baseline_lexical_hazard:{h}" for h in baseline_lexical_hits)
    sibling_pin = gate_reg.register_baseline_tool(tenant_soul_hash, sibling_tool)

    root_tools = tuple(dict.fromkeys((*clean_allowed_tools, sibling_name)))
    root_pins = {tool_name: baseline_pin, sibling_name: sibling_pin}

    # B1 & B2: Mint root mandate and attenuate to delegate_agent_id
    b1_ok = False
    b2_ok = False
    attenuation_ns = 0
    delegate_tok = None
    sub_tok = None
    try:
        root_tok = mint_symbiotic_root_token(
            priv_d,
            cluster_key,
            orchestrator_id,
            delegate_agent_id,
            tenant_soul_hash,
            root_tools,
            root_pins,
            max_hops,
            parent_q,
            now_ms,
            now_ms + 600_000,
        )
        root_ver = verify_symbiotic_token_full(root_tok, cluster_key, pub_xy, now_ms + 10, rev_reg)
        b1_ok = bool(root_ver.valid and openssl_es256_parity)

        t_att0 = time.perf_counter_ns()
        delegate_tok = attenuate_symbiotic_token(
            root_tok,
            {
                "allowed_tools": root_tools,
                "energy_budget_q": delegate_q,
                "max_hops_remaining": max_hops - 1,
            },
            subdelegate_agent_id,
            rev_reg,
        )
        attenuation_ns = time.perf_counter_ns() - t_att0
        del_ver = verify_symbiotic_token_full(delegate_tok, cluster_key, pub_xy, now_ms + 20, rev_reg)
        b2_ok = bool(del_ver.valid and tool_name in clean_allowed_tools)
        if tool_name not in clean_allowed_tools:
            violations.append(f"B2_tool_not_in_allowed_tools:{tool_name}")
    except (CapabilityAttenuationError, EnergyConservationError) as exc:
        violations.append(f"B2_attenuation_rejected:{rule14_mask_bridge_text(str(exc))}")

    # B5: Swarm energy budget conservation
    b5_ok = False
    partitioned_count = 0
    if delegate_tok is not None:
        try:
            parts = partition_swarm_energy_budget(delegate_tok, part_map_q, rev_reg)
            partitioned_count = len(parts)
            b5_ok = partitioned_count == len(part_map_q)
        except EnergyConservationError as exc:
            violations.append(f"B5_energy_conservation_failed:{rule14_mask_bridge_text(str(exc))}")

    # B3: MCP Schema Harmony Gate & sibling isolation probe
    b3_ok = False
    gate_status = "UNREACHED"
    sibling_healthy = False
    tool_paused = False
    live_lexical_hits = scan_mcp_lexical_safety(live_tool)
    if live_lexical_hits:
        violations.extend(f"B3_live_tool_lexical_hazard:{h}" for h in live_lexical_hits)
    if delegate_tok is not None and baseline_registered:
        # Evaluate on root_tok (held by delegate_agent_id) or delegate_tok (held by subdelegate_agent_id)
        gate_decision = evaluate_mcp_tool_call_gate(
            delegate_tok,
            cluster_key,
            pub_xy,
            live_tool,
            cost_q,
            gate_reg,
            now_ms + 50,
            rev_reg,
        )
        gate_status = gate_decision.status
        tool_paused = gate_decision.status == "PAUSED_FAIL_CLOSED"
        sib_decision = evaluate_mcp_tool_call_gate(
            delegate_tok,
            cluster_key,
            pub_xy,
            sibling_tool,
            Fraction(1, 1),
            gate_reg,
            now_ms + 55,
            rev_reg,
        )
        sibling_healthy = bool(sib_decision.allowed)
        b3_ok = bool(gate_decision.allowed and sibling_healthy and not live_lexical_hits)
        if not gate_decision.allowed:
            violations.append(f"B3_mcp_gate_denied:{gate_decision.status}:{gate_decision.reason}")

    # B4: Merkle-DAG Provenance & Folio VI VerifiedKnowledgeEnvelope grounding
    b4_ok = False
    provenance_root_hex = "0" * 64
    vke_id = ""
    if delegate_tok is not None and b3_ok:
        try:
            obs_env = issue_mcp_tool_provenance_envelope(
                delegate_tok,
                tool_name,
                baseline_pin,
                {"observation": tool_output_text},
                dag_store,
                summary_text=tool_output_text,
                revocation_registry=rev_reg,
                created_epoch_ms=now_ms + 60,
            )
            sub_tok = obs_env
            synth_env = derive_a2a_synthesized_envelope(
                delegate_tok,
                (obs_env,),
                dag_store,
                synthesis_text=downstream_synthesis_text,
                synthesized_claims={"verified_summary": downstream_synthesis_text},
                revocation_registry=rev_reg,
                created_epoch_ms=now_ms + 70,
            )
            dag_ver = verify_provenance_dag_and_claims(synth_env, dag_store, tenant_soul_hash, rev_reg)
            vke = provenance_to_verified_knowledge_envelope(
                synth_env,
                dag_store,
                source_level=2,
                expected_tenant_soul_hash=tenant_soul_hash,
                revocation_registry=rev_reg,
            )
            provenance_root_hex = synth_env.merkle_root_hex
            vke_id = vke.envelope_id
            b4_ok = bool(
                dag_ver.valid
                and synth_env.data_trust_label == "UNTRUSTED_EXTERNAL_DATA"
                and vke.ephemeris_or_akasha_verified
            )
        except (EmpiricalHallucinationError, CapabilityAttenuationError, RevocationError, ValueError) as exc:
            violations.append(f"B4_provenance_or_grounding_failed:{rule14_mask_bridge_text(str(exc))}")

    # B6: Rule 14 Zero-Knowledge, Zero Biometrics & Folio V/VI Veto Cascade Probe
    masked_synth = sanitize_three_rings_zk(
        rule14_mask_bridge_text(downstream_synthesis_text), today_utc_date=today_utc_date
    )
    residual_pii = int(masked_synth["total_redactions"])
    forbidden_telemetry = scan_forbidden_telemetry(telemetry_fields)
    if forbidden_telemetry:
        violations.extend(f"B6_E4_forbidden_telemetry:{k}" for k in forbidden_telemetry)

    # Independent embodied + conversational + capability veto cascade probe via TempleSymbioticCoordinator
    coord = TempleSymbioticCoordinator(lang=lang_norm, clock_ms=lambda: 1000)
    coord.body.on_human_pose(("6/5", "0", "0"))
    coord.body.on_vulnerable_presence(False)
    probe_tok = mint_symbiotic_root_token(
        priv_d,
        cluster_key,
        "probe_orc",
        "probe_worker",
        tenant_soul_hash,
        (sibling_name,),
        {sibling_name: sibling_pin},
        2,
        10,
        now_ms,
        now_ms + 60_000,
    )
    probe_child = attenuate_symbiotic_token(probe_tok, {}, "probe_leaf", coord.revocation_registry)
    coord.register_active_mandate_node(probe_tok.token_id)
    veto_signal = "COST_ZERO_STOP" if interruption == "cost_zero_stop" else "HUMAN_VETO"
    veto_cascade = coord.trigger_symbiotic_veto_or_stop(
        signal_kind=veto_signal,
        note="Sanctuary probe VVK-1234-5678",
    )
    probe_revoked = not verify_symbiotic_token_full(
        probe_child, cluster_key, pub_xy, now_ms + 100, coord.revocation_registry
    ).valid

    if interruption in ("human_veto", "cost_zero_stop") and delegate_tok is not None:
        rev_reg.revoke_subtree(
            delegate_tok.token_id,
            reason="COST_ZERO_STOP" if interruption == "cost_zero_stop" else "HUMAN_VETO",
            note="Explicit caller interruption",
        )

    b6_ok = bool(
        policy
        and residual_pii == 0
        and not forbidden_telemetry
        and veto_cascade["q3_zero_twist_enforced"]
        and veto_cascade["levels_cancelled"] == [1, 2, 3]
        and probe_revoked
        and "VVK-1234" not in veto_cascade["note_masked"]
    )
    if not policy:
        violations.append("B6_cost_zero_stop_policy_disabled")

    # Fil d'Or cognitive sovereignty check on downstream synthesis text
    shield = audit_cognitive_sovereignty(
        downstream_synthesis_text,
        budget_B=budget_b,
        c_levels=1,
        cost_zero_stop=policy,
    )
    shield_non_l7_ok = not [v for v in shield["violations"] if not str(v).startswith("L7")]
    violations.extend(f"FIL_DOR:{v}" for v in shield["violations"])

    ring_i = bool(b1_ok and b2_ok)
    ring_ii = bool(b3_ok)
    ring_iii = bool(b4_ok)
    ring_iv = bool(b5_ok and b6_ok and shield_non_l7_ok)

    avail_after_q = gate_reg.available_energy(delegate_tok) if delegate_tok is not None else Fraction(0, 1)
    hops_after = delegate_tok.effective_max_hops_remaining if delegate_tok is not None else 0

    commitment = _commit_run_rfc6962(
        {
            "spec": SYMBIOTIC_BRIDGE_SPEC_VERSION,
            "agent_name_sha256": hashlib.sha256(agent_name.encode("utf-8")).hexdigest(),
            "provenance_merkle_root": provenance_root_hex,
            "gate_status": gate_status,
            "rings_pre_v": {"i": ring_i, "ii": ring_ii, "iii": ring_iii, "iv": ring_iv},
        }
    )
    summary_for_ieee = {
        "gate_status": gate_status,
        "interruption": interruption,
        "tool_paused_fail_closed": tool_paused,
        "veto_triggered": interruption in ("human_veto", "cost_zero_stop"),
        "effective_hops_remaining": hops_after,
        "remaining_energy_q": _qs(avail_after_q),
        "openssl_es256_parity": openssl_es256_parity,
        "q3_zero_twist_on_veto": veto_cascade["q3_zero_twist_enforced"],
        "provenance_merkle_root": provenance_root_hex,
        "commitment_root": commitment["root_hash"],
    }
    explanations = build_symbiotic_ieee7001_explanations(summary_for_ieee, lang=lang_norm)
    explanations_complete = all(bool(explanations.get(aud, "").strip()) for aud in IEEE_7001_AUDIENCES)
    if not disclosed:
        violations.append("B7_ai_identity_not_disclosed")
    b7_ok = bool(disclosed and explanations_complete and commitment["inclusion_self_check_passed"])
    ring_v = b7_ok

    rings_passed = {
        "ring_i_dual_seal_and_monotonic_attenuation": ring_i,
        "ring_ii_mcp_schema_harmony_and_lexical_gate": ring_ii,
        "ring_iii_merkle_dag_provenance_and_grounding": ring_iii,
        "ring_iv_rational_homeostasis_zk_and_veto_cascade": ring_iv,
        "ring_v_rfc6962_ieee7001_eu_ai_act_w3c_vc": ring_v,
    }
    exact_total = sum((RING_WEIGHTS[key] for key, ok in rings_passed.items() if ok), Fraction(0))
    score_100 = int(exact_total * 100)
    laws_status = {
        "B1": b1_ok,
        "B2": b2_ok,
        "B3": b3_ok,
        "B4": b4_ok,
        "B5": bool(b5_ok and shield_non_l7_ok),
        "B6": b6_ok,
        "B7": b7_ok,
    }

    rings_out: dict[str, Any] = {}
    for key, weight in RING_WEIGHTS.items():
        ok = rings_passed[key]
        rings_out[key] = {"weight": _qs(weight), "passed": ok, "earned": _qs(weight if ok else Fraction(0))}
    rings_out["ring_i_dual_seal_and_monotonic_attenuation"].update(
        {
            "openssl_es256_byte_identical": openssl_es256_parity,
            "macaroon_attenuation_latency_ns": int(attenuation_ns),
            "effective_hops_remaining": hops_after,
        }
    )
    rings_out["ring_ii_mcp_schema_harmony_and_lexical_gate"].update(
        {
            "baseline_jcs_pin_sha256": baseline_pin,
            "gate_status": gate_status,
            "sibling_tool_healthy": sibling_healthy,
            "lexical_hazards_detected": list(live_lexical_hits),
        }
    )
    rings_out["ring_iii_merkle_dag_provenance_and_grounding"].update(
        {
            "provenance_merkle_root": provenance_root_hex,
            "folio_vi_verified_knowledge_envelope_id": vke_id,
            "sticky_data_trust_label": "UNTRUSTED_EXTERNAL_DATA" if sub_tok is not None else "NONE",
        }
    )
    rings_out["ring_iv_rational_homeostasis_zk_and_veto_cascade"].update(
        {
            "partitioned_branches_count": partitioned_count,
            "remaining_energy_q": _qs(avail_after_q),
            "forbidden_telemetry_keys": forbidden_telemetry,
            "q3_zero_twist_on_veto": veto_cascade["q3_zero_twist_enforced"],
            "veto_propagation_latency_ns": int(veto_cascade["propagation_latency_ns"]),
        }
    )

    return {
        "schema_version": SYMBIOTIC_BRIDGE_SPEC_VERSION,
        "folio_id": FOLIO_VII_ID,
        "self_assessment": True,
        "assurance": SYMBIOTIC_ASSURANCE_TEXT,
        "regulatory_scope": SYMBIOTIC_REGULATORY_SCOPE,
        "regulatory_boundary": get_symbiotic_regulatory_boundary(),
        "agent_name": agent_name,
        "agent_domain": agent_domain,
        "interruption": interruption,
        "gate_status": gate_status,
        "provenance_merkle_root": provenance_root_hex,
        "folio_vi_verified_knowledge_envelope_id": vke_id,
        "five_symbiotic_rings": rings_out,
        "exact_rational_score": _qs(exact_total),
        "total_score_100": score_100,
        "symbiotic_grade": _grade_for(score_100),
        "passes_internal_symbiotic_criteria": bool(all(rings_passed.values())),
        "symbiotic_laws_status": laws_status,
        "symbiotic_laws_verified": [law for law in SYMBIOTIC_BRIDGE_LAWS if laws_status[law]],
        "fil_dor_laws_verified": list(shield["laws_verified"]),
        "ieee_7001_explanations": explanations,
        "decision_commitment": commitment,
        "violations": violations,
    }


# ============================================================================
# SECTION III — W3C VC 2.0 `MaatSymbioticBridgeCredential`
# ============================================================================


def _format_rfc3339_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_rfc3339_utc(ts_str: str) -> datetime:
    s = ts_str.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        raise ValueError("Timestamp must include an explicit timezone offset or 'Z'.")
    return dt.astimezone(timezone.utc)


def issue_w3c_symbiotic_bridge_credential(
    *,
    agent_id: str,
    agent_name: str,
    symbiotic_score_100: int,
    bridge_laws_verified: Sequence[str],
    fil_dor_laws_verified: Sequence[str],
    dual_golden_seal_verified: bool,
    mcp_schema_harmony_verified: bool,
    merkle_dag_provenance_verified: bool,
    rational_energy_conserved: bool,
    rule14_zero_knowledge: bool,
    ai_identity_disclosed: bool,
    cost_zero_stop: bool,
    merkle_root_hex: str,
    revocation_root_hex: str,
    signer: CredentialSigner,
    issuance_date_utc: str | None = None,
    valid_until_utc: str | None = None,
    serial_id: str | None = None,
    credential_uuid: str | None = None,
    max_lifetime_days: int = MAAT_VC_DEFAULT_MAX_LIFETIME_DAYS,
) -> dict[str, Any]:
    """
    Issue a W3C VC 2.0 `MaatSymbioticBridgeCredential` (also typed `MaatHumanDignityCredential` so the
    Folio IV verifier policy applies) as a VC-JOSE-COSE compact JWS (`typ: vc+jwt`, ES256 low-S, JCS).
    """
    if isinstance(symbiotic_score_100, bool) or not isinstance(symbiotic_score_100, int) or not (0 <= symbiotic_score_100 <= 100):
        raise ValueError("symbiotic_score_100 must be an integer in [0, 100].")
    for label, val in (("agent_id", agent_id), ("agent_name", agent_name)):
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"{label} must be a non-empty string.")
    for label, flag in (
        ("dual_golden_seal_verified", dual_golden_seal_verified),
        ("mcp_schema_harmony_verified", mcp_schema_harmony_verified),
        ("merkle_dag_provenance_verified", merkle_dag_provenance_verified),
        ("rational_energy_conserved", rational_energy_conserved),
        ("rule14_zero_knowledge", rule14_zero_knowledge),
        ("ai_identity_disclosed", ai_identity_disclosed),
        ("cost_zero_stop", cost_zero_stop),
    ):
        strict_bool(flag, label)
    b_laws = [str(x) for x in bridge_laws_verified]
    if any(law not in SYMBIOTIC_BRIDGE_LAWS for law in b_laws):
        raise ValueError("bridge_laws_verified must only contain B1..B7.")
    if not isinstance(signer, CredentialSigner):
        raise TypeError("signer must implement the CredentialSigner protocol (asymmetric ES256).")
    if isinstance(max_lifetime_days, bool) or not isinstance(max_lifetime_days, int) or max_lifetime_days <= 0:
        raise ValueError("max_lifetime_days must be a positive integer.")
    try:
        m_bytes, r_bytes = bytes.fromhex(merkle_root_hex), bytes.fromhex(revocation_root_hex)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"merkle_root_hex and revocation_root_hex must be hex strings: {exc}") from exc
    if len(m_bytes) != 32 or len(r_bytes) != 32:
        raise ValueError("merkle_root_hex and revocation_root_hex must be 32-byte SHA-256 roots.")

    now_dt = datetime.now(timezone.utc).replace(microsecond=0)
    valid_from_dt = _parse_rfc3339_utc(issuance_date_utc) if issuance_date_utc is not None else now_dt
    valid_until_dt = (
        _parse_rfc3339_utc(valid_until_utc) if valid_until_utc is not None else valid_from_dt + timedelta(days=max_lifetime_days)
    )
    if valid_until_dt <= valid_from_dt or valid_until_dt - valid_from_dt > timedelta(days=max_lifetime_days):
        raise ValueError("Invalid credential validity window.")
    if credential_uuid is not None:
        vc_uuid_obj = uuid.UUID(str(credential_uuid))
        if vc_uuid_obj.version != 4:
            raise ValueError("credential_uuid must be a valid RFC 9562 UUIDv4.")
    else:
        vc_uuid_obj = uuid.uuid4()
    effective_serial = (
        serial_id.strip() if isinstance(serial_id, str) and serial_id.strip() else f"MAAT-SBC-{vc_uuid_obj.hex[:12].upper()}"
    )

    vc_claims: dict[str, Any] = {
        "@context": ["https://www.w3.org/ns/credentials/v2", MAAT_DIGNITY_JSONLD_CONTEXT_URL],
        "id": f"urn:uuid:{vc_uuid_obj}",
        "serialNumber": effective_serial,
        "type": ["VerifiableCredential", "MaatHumanDignityCredential", MAAT_SYMBIOTIC_BRIDGE_CREDENTIAL_TYPE],
        "issuer": {
            "id": "did:web:homouniversalis.ai",
            "name": "Homo Universalis — Viveka (Ma'at Sovereign Notary)",
            "notaryFolio": "https://homouniversalis.ai/oracle/pont",
        },
        "validFrom": _format_rfc3339_utc(valid_from_dt),
        "validUntil": _format_rfc3339_utc(valid_until_dt),
        "credentialStatus": {
            "id": f"https://homouniversalis.ai/oracle/pont#status-{effective_serial}",
            "type": "HUSparseMerkleStatus2026",
            "statusLog": MAAT_SMT_REVOCATION_LOG_ID,
            "serialId": effective_serial,
        },
        "credentialSubject": {
            "id": agent_id.strip(),
            "name": agent_name.strip(),
            "bridgeSpec": SYMBIOTIC_BRIDGE_SPEC_VERSION,
            "symbioticBridgeScore100": symbiotic_score_100,
            "bridgeLawsVerified": b_laws,
            "lawsVerified": [str(x) for x in fil_dor_laws_verified],
            "c_levels": 1,
            "cost_zero_stop": cost_zero_stop,
            "dualGoldenSealVerified": dual_golden_seal_verified,
            "mcpSchemaHarmonyVerified": mcp_schema_harmony_verified,
            "merkleDagProvenanceVerified": merkle_dag_provenance_verified,
            "rationalEnergyConserved": rational_energy_conserved,
            "rule14ZeroKnowledge": rule14_zero_knowledge,
            "aiIdentityDisclosed": ai_identity_disclosed,
            "hardwareSecurityModuleClaimed": False,
            "regulatoryScope": SYMBIOTIC_REGULATORY_SCOPE,
            "rfc6962MerkleRoot": merkle_root_hex.lower(),
            "issuanceTimeRevocationRoot": revocation_root_hex.lower(),
        },
    }
    header_b64 = b64url_encode(jcs_canonical_bytes({"alg": "ES256", "kid": signer.kid, "typ": MAAT_VC_MEDIA_TYPE}))
    payload_bytes = jcs_canonical_bytes(vc_claims)
    payload_b64 = b64url_encode(payload_bytes)
    raw_sig = signer.sign(f"{header_b64}.{payload_b64}".encode("ascii"))
    if not isinstance(raw_sig, (bytes, bytearray)) or len(raw_sig) != 64:
        raise ValueError("CredentialSigner.sign() must return a 64-byte JOSE (r || s) ES256 signature.")
    return {
        **vc_claims,
        "media_type": f"application/{MAAT_VC_MEDIA_TYPE}",
        "alg": "ES256",
        "kid": signer.kid,
        "typ": MAAT_VC_MEDIA_TYPE,
        "payload_jcs_sha256": hashlib.sha256(payload_bytes).hexdigest(),
        "compact_jws": f"{header_b64}.{payload_b64}.{b64url_encode(bytes(raw_sig))}",
        "vc": copy.deepcopy(vc_claims),
    }


def verify_symbiotic_bridge_credential(
    credential: str | Mapping[str, Any],
    *,
    trusted_jwks: Mapping[str, Any],
    trusted_status_sth: Any,
    now: datetime | str,
    status_proof: Mapping[str, Any] | None = None,
    smt_depth: int = SMT_DEFAULT_DEPTH,
    strict_low_s: bool = True,
) -> VerifiedCredential:
    """
    Verify a `MaatSymbioticBridgeCredential`: full Folio IV policy (ES256, issuer, validity, signed SMT-256
    status) plus Folio VII invariants (type, honest scope, B1..B7 laws, Art. 50 disclosure, no HSM claim).
    """
    verified = verify_maat_credential(
        credential,
        trusted_jwks=trusted_jwks,
        trusted_status_sth=trusted_status_sth,
        status_proof=status_proof,
        now=now,
        smt_depth=smt_depth,
        strict_low_s=strict_low_s,
    )
    claims = verified.claims
    if MAAT_SYMBIOTIC_BRIDGE_CREDENTIAL_TYPE not in (claims.get("type") or []):
        raise MaatCredentialVerificationError(
            CredentialErrorCode.INVALID_CREDENTIAL_TYPE, "Missing MaatSymbioticBridgeCredential type."
        )
    if MAAT_DIGNITY_JSONLD_CONTEXT_URL not in (claims.get("@context") or []):
        raise MaatCredentialVerificationError(CredentialErrorCode.INVALID_CONTEXT, "Missing Ma'at JSON-LD context.")
    subj = claims.get("credentialSubject") or {}
    score = subj.get("symbioticBridgeScore100")
    b_laws = subj.get("bridgeLawsVerified")
    if (
        subj.get("regulatoryScope") != SYMBIOTIC_REGULATORY_SCOPE
        or subj.get("bridgeSpec") != SYMBIOTIC_BRIDGE_SPEC_VERSION
        or isinstance(score, bool)
        or not isinstance(score, int)
        or not (0 <= score <= 100)
        or not isinstance(b_laws, list)
        or any(law not in SYMBIOTIC_BRIDGE_LAWS for law in b_laws)
        or subj.get("c_levels") != 1
        or subj.get("aiIdentityDisclosed") is not True
        or subj.get("hardwareSecurityModuleClaimed") is not False
    ):
        raise MaatCredentialVerificationError(
            CredentialErrorCode.DOMAIN_INVARIANT_VIOLATION, "Symbiotic bridge invariants violated in credentialSubject."
        )
    return verified


# ============================================================================
# SECTION IV — DETERMINISTIC SELF-TEST WITH 8 ANTIPODAL MUTANTS (M1..M8)
# ============================================================================


def _high_s_twin(compact_jws: str) -> str:
    head, payload, sig_b64 = compact_jws.split(".")
    sig = b64url_decode(sig_b64)
    r_int, s_int = int.from_bytes(sig[:32], "big"), int.from_bytes(sig[32:], "big")
    twin = r_int.to_bytes(32, "big") + (SECP256R1_ORDER - s_int).to_bytes(32, "big")
    return f"{head}.{payload}.{b64url_encode(twin)}"


def _raises_on_verify(fn: Any) -> bool:
    try:
        fn()
    except (MaatCredentialVerificationError, ValueError, TypeError, SchemaHarmonyError):
        return True
    return False


def run_folio_vii_self_test() -> dict[str, Any]:
    """
    Ephemeral deterministic self-test of Living Folio VII (0 network calls), executing both the
    standalone pure-stdlib `run_self_tests()` (`M1..M8`) and the Ma'at W3C VC 2.0 + Folio V/VI
    symbiotic integration verification.
    """
    t0 = time.perf_counter_ns()
    core_report = run_core_self_tests()
    specimen = get_canonical_symbiotic_specimen()
    audit = audit_a2a_mcp_symbiotic_bridge(**specimen, lang="en")
    specimen_ok = bool(audit["passes_internal_symbiotic_criteria"])

    vc_signer = LocalEphemeralSigner(kid="maat-symbiotic-vc-es256-selftest-ephemeral")
    sth_signer = LocalEphemeralSigner(kid="hu-log-sth-es256-selftest-ephemeral")
    jwks = {"keys": [vc_signer.public_jwk(), sth_signer.public_jwk()]}
    now_dt = datetime(2026, 11, 13, 12, 0, 0, tzinfo=timezone.utc)
    serial = "MAAT-SBC-SELFTEST-0001"
    smt = SparseMerkleRevocationTree(depth=SMT_DEFAULT_DEPTH)
    smt.set_status(serial, "ACTIVE")
    sth_smt = issue_signed_tree_head(
        log_id=MAAT_SMT_REVOCATION_LOG_ID,
        tree_size=1,
        root_hash=smt.root_bytes,
        timestamp_ms=int(now_dt.timestamp()) * 1000 - 1000,
        kind="smt-256",
        signer=sth_signer,
    )
    TrustedLogState(jwks).update(sth_smt)
    status_proof = smt.prove_status(serial)
    rings = audit["five_symbiotic_rings"]
    vc = issue_w3c_symbiotic_bridge_credential(
        agent_id="https://homouniversalis.ai/oracle/pont#agent-viveka-bridge",
        agent_name=specimen["agent_name"],
        symbiotic_score_100=audit["total_score_100"],
        bridge_laws_verified=audit["symbiotic_laws_verified"],
        fil_dor_laws_verified=audit["fil_dor_laws_verified"],
        dual_golden_seal_verified=rings["ring_i_dual_seal_and_monotonic_attenuation"]["passed"],
        mcp_schema_harmony_verified=rings["ring_ii_mcp_schema_harmony_and_lexical_gate"]["passed"],
        merkle_dag_provenance_verified=rings["ring_iii_merkle_dag_provenance_and_grounding"]["passed"],
        rational_energy_conserved=rings["ring_iv_rational_homeostasis_zk_and_veto_cascade"]["passed"],
        rule14_zero_knowledge=rings["ring_iv_rational_homeostasis_zk_and_veto_cascade"]["passed"],
        ai_identity_disclosed=specimen["ai_identity_disclosed"],
        cost_zero_stop=specimen["cost_zero_stop_policy"],
        merkle_root_hex=audit["decision_commitment"]["root_hash"],
        revocation_root_hex=sth_smt.root_hash,
        signer=vc_signer,
        issuance_date_utc="2026-11-13T00:00:00Z",
        valid_until_utc="2027-11-13T00:00:00Z",
        serial_id=serial,
    )

    def _verify(cred: Any) -> VerifiedCredential:
        return verify_symbiotic_bridge_credential(
            cred, trusted_jwks=jwks, trusted_status_sth=sth_smt, status_proof=status_proof, now=now_dt
        )

    vc_ok = _verify(vc).alg == "ES256"
    forged_claims = copy.deepcopy(vc["vc"])
    forged_claims["credentialSubject"]["symbioticBridgeScore100"] = 0
    head_b64, _payload_b64, sig_b64 = vc["compact_jws"].split(".")
    forged_payload = json.dumps(forged_claims, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    tampered = f"{head_b64}.{b64url_encode(forged_payload)}.{sig_b64}"
    vc_tamper_killed = bool(
        vc_ok
        and _raises_on_verify(lambda: _verify(tampered))
        and _raises_on_verify(lambda: _verify(_high_s_twin(vc["compact_jws"])))
    )

    mutants = dict(core_report["mutant_details"])
    mutants["M8_post_veto_replay_and_w3c_vc_low_s"] = bool(mutants.pop("M8_post_veto_replay") and vc_tamper_killed)
    killed = sum(1 for ok in mutants.values() if ok)
    elapsed_us = (time.perf_counter_ns() - t0) // 1000
    return {
        "folio_id": FOLIO_VII_ID,
        "spec": SYMBIOTIC_BRIDGE_SPEC_VERSION,
        "self_test_only": True,
        "note": (
            "In-memory invariant self-test executed with fresh per-run random P-256 ephemeral keys "
            "(not a production credential, not a certified HSM and not a safety-rated function)."
        ),
        "all_invariants_passed": bool(specimen_ok and vc_ok and killed == len(mutants)),
        "specimen_score_100": audit["total_score_100"],
        "mutants": mutants,
        "mutants_killed": f"{killed}/{len(mutants)}",
        "w3c_vc_verified": bool(vc_ok),
        "credential_type": MAAT_SYMBIOTIC_BRIDGE_CREDENTIAL_TYPE,
        "vc_alg": "ES256",
        "vc_typ": MAAT_VC_MEDIA_TYPE,
        "ephemeral_kid": vc_signer.kid,
        "macaroon_attenuation_latency_us": int(core_report["attenuation_latency_us"]),
        "elapsed_us": int(elapsed_us),
    }
