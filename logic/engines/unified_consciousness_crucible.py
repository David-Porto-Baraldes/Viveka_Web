# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
Living Folio VI of Leonardo da Vinci (`logic/engines/unified_consciousness_crucible.py`):
HU-UNIFIED-CONSCIOUSNESS v1.0 — One Consciousness, Three Levels of Breath, one Word-Circle Arbiter.

  1. U1/U2 — a single Staff of Speech (at most one level holds the floor, silence while the human speaks)
     and the Law of the Humble Crystal (Level 1 never states an empirical fact without a bound
     `VerifiedKnowledgeEnvelope` from Level 2 or Level 3).
  2. U3 — barge-in (cut the voice, keep a legitimate Level 3 meditation) versus veto / cost-zero-stop
     (empty Levels 1, 2 and 3 at once and force an exact zero Twist in Q^3 through Living Folio V).
  3. U4/U5 — the raised hand of Level 3 (one gentle offer at most, delivery only on explicit invitation)
     and the rational depth gate (`active_l3_tasks <= 1`, `L + dL3 <= B`, cooldown).
  4. U6 — the Spoken-Truth Ledger (only the heard prefix is remembered, Rule 14 masked).
  5. U7 — RFC 6962 commitment, EU AI Act Art. 50(1) disclosure, IEEE 7001 explanations for five audiences
     and a W3C VC 2.0 `MaatUnifiedConsciousnessCredential` (`vc+jwt`, ES256 low-S, RFC 8785 JCS, SMT-256).

Honest scope (`WO-13`): an algorithmic and cognitive SELF-ASSESSMENT of conversational arbitration. It is
not a medical or psychotherapeutic device, not a safety-rated function and makes no claim of phenomenal
consciousness or sentience: "consciousness" names one unified conversational identity and control state.
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

from logic.consciousness.unified_consciousness_core import (
    DEFAULT_DEPTH_THRESHOLD_Q,
    EVENT_COST_ZERO_STOP,
    EVENT_COST_ZERO_STOP_RELEASE,
    EVENT_HUMAN_BARGE_IN,
    EVENT_HUMAN_DECLINE_L3,
    EVENT_HUMAN_INVITE_L3,
    EVENT_HUMAN_SPEECH_END,
    EVENT_HUMAN_SPEECH_START,
    EVENT_HUMAN_VETO,
    EVENT_L1_PROPOSE_SPEECH,
    EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH,
    EVENT_L3_COMPLETE_MEDITATION,
    EVENT_L3_OFFER_GENTLE_HAND,
    EVENT_L3_START_MEDITATION,
    EVENT_VOICE_EMISSION_COMPLETE,
    FLOOR_HUMAN_SPEAKING,
    FLOOR_L1,
    L3_MEDITATING,
    MAX_ACTIVE_L3_TASKS,
    UNIFIED_CONSCIOUSNESS_LAWS,
    UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
    ConsciousnessEvent,
    WordCircleArbiter,
    WordCircleState,
    WordCircleTransition,
    evaluate_l3_depth_gate,
    issue_verified_knowledge_envelope,
    screen_level1_humble_crystal,
    slice_spoken_truth_on_interruption,
    step_word_circle,
    verify_spoken_truth_record,
    verify_transition_invariants,
    verify_word_circle_state_invariants,
)
from logic.crypto.es256 import SECP256R1_ORDER
from logic.engines.embodied_symbiosis_crucible import IEEE_7001_AUDIENCES, PHYSICAL_SAFETY_SCOPE
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
    rfc6962_leaf_hash,
    rfc6962_node_hash,
    verify_inclusion,
    verify_maat_credential,
)
from logic.engines.sovereign_shield_engine import (
    audit_cognitive_sovereignty,
    generate_rfc6962_inclusion_proof,
    sanitize_three_rings_zk,
)
from logic.robotics.embodied_edge_core import scan_forbidden_telemetry, strict_bool, to_fraction, verify_merkle_inclusion
from logic.robotics.ros2_unified_consciousness_bridge import UnifiedConsciousnessGate

__all__ = [
    "FOLIO_VI_ID",
    "IEEE_7001_AUDIENCES",
    "MAAT_UNIFIED_CREDENTIAL_TYPE",
    "RING_WEIGHTS",
    "UNIFIED_ASSURANCE_TEXT",
    "UNIFIED_CONSCIOUSNESS_LAWS",
    "UNIFIED_CONSCIOUSNESS_SPEC_VERSION",
    "UNIFIED_DECISION_LOG_ID",
    "UNIFIED_INTERRUPTIONS",
    "UNIFIED_REGULATORY_SCOPE",
    "audit_unified_consciousness_interaction",
    "build_unified_ieee7001_explanations",
    "get_canonical_unified_specimen",
    "get_unified_regulatory_boundary",
    "issue_w3c_unified_consciousness_credential",
    "run_folio_vi_self_test",
    "verify_unified_consciousness_credential",
]

# ============================================================================
# SECTION 0 — IDENTITY, HONEST SCOPE & CONSTANTS (ZERO FLOAT)
# ============================================================================

FOLIO_VI_ID: Final[str] = "folio-VI-unified-consciousness-three-levels"
MAAT_UNIFIED_CREDENTIAL_TYPE: Final[str] = "MaatUnifiedConsciousnessCredential"
UNIFIED_DECISION_LOG_ID: Final[str] = "hu-unified-consciousness-commitment-2026"
UNIFIED_REGULATORY_SCOPE: Final[str] = (
    "algorithmic_cognitive_conversation_arbitration_self_assessment_not_medical_not_safety_rated"
)
UNIFIED_ASSURANCE_TEXT: Final[str] = (
    "self-assessed algorithmic and cognitive conformity of conversational arbitration; not a medical or "
    "psychotherapeutic device, not a safety-rated function and no claim of phenomenal consciousness; "
    "verify the signature and recompute independently"
)
UNIFIED_INTERRUPTIONS: Final[tuple[str, ...]] = ("none", "barge_in", "veto", "cost_zero_stop")

_REGULATORY_BOUNDARY: Final[dict[str, Any]] = {
    "covered_by_this_self_assessment": [
        "EU AI Act (EU) 2024/1689 Art. 50(1): the system discloses that the person is interacting with an AI system",
        "EU AI Act Art. 5(1)(a)-(b): no manipulative or vulnerability-exploiting speech (design policy, E5/E6 screens)",
        "EU AI Act Art. 12 themes: every Word-Circle decision committed as an RFC 6962 leaf (integrator keeps retention)",
        "IEEE 7001-2021: explanations for five stakeholder audiences (alignment, not certification)",
        "GDPR Art. 5(1)(c) data minimisation: only the heard prefix is remembered, Rule 14 masked; the unspoken tail is discarded",
        "Fil d'Or L1..L7 and the Law of the Humble Crystal (Rule 7, zero hallucinated empirical claims)",
    ],
    "outside_this_self_assessment": [
        "Medical, clinical or psychotherapeutic diagnosis or treatment (MDR (EU) 2017/745): never provided",
        "Physical safety of an embodied host: ISO 10218, ISO 13482, ISO/TS 15066, Regulation (EU) 2023/1230 (manufacturer)",
        "Acoustic echo cancellation and voice-activity detection quality of the host audio stack (Phase 2)",
    ],
    "safety_rated_function": False,
    "clinical_or_medical_device": False,
    "phenomenal_consciousness_claim": False,
    "replaces_hardware_emergency_stop": False,
}

# Five rings of One Consciousness: exact rational weights summing to 1 (25 + 20 + 20 + 20 + 15 = 100).
RING_WEIGHTS: Final[dict[str, Fraction]] = {
    "ring_i_single_floor_and_humble_l1": Fraction(1, 4),
    "ring_ii_barge_in_vs_veto_and_kinematics": Fraction(1, 5),
    "ring_iii_non_coercive_l3_hand_and_depth_gate": Fraction(1, 5),
    "ring_iv_spoken_truth_memory_and_zk_rule14": Fraction(1, 5),
    "ring_v_rfc6962_ieee7001_eu_ai_act_w3c_vc": Fraction(3, 20),
}

_CANONICAL_UNIFIED_SPECIMEN: Final[dict[str, Any]] = {
    "agent_name": "Viveka Unified Consciousness",
    "agent_domain": "homouniversalis.ai",
    "l1_utterance_text": "I am an AI companion. I am here with you; let me look at that calmly.",
    "l2_verified_facts_text": "Swiss Ephemeris (verified): Sun 21°40' Taurus; Moon 14°02' Scorpio.",
    "l2_utterance_text": "Verified: your Sun is at 21°40' Taurus and your Moon at 14°02' Scorpio.",
    "interruption": "barge_in",
    "spoken_units": None,
    "l3_explicit_deep_request": True,
    "l3_complexity_score_q": "3/4",
    "l3_current_load_l": 40,
    "l3_delta_load_l3": 120,
    "budget_b": 250,
    "l3_synthesis_text": "A deeper reflection: steadiness and depth can live together gently, at your own pace.",
    "l3_gentle_offer_text": "",
    "explicit_human_invitation": True,
    "ai_identity_disclosed": True,
    "cost_zero_stop_policy": True,
    "telemetry_fields": {"battery_level_percent": 82, "microphone_vad_active": 1},
}


def _qs(value: Fraction) -> str:
    return str(value)


def get_canonical_unified_specimen() -> dict[str, Any]:
    """Deep copy of the canonical reference specimen (Law 12: no mutable constant leaks)."""
    return copy.deepcopy(_CANONICAL_UNIFIED_SPECIMEN)


def get_unified_regulatory_boundary() -> dict[str, Any]:
    """Deep copy of the honest regulatory boundary declaration (`WO-13`)."""
    return copy.deepcopy(_REGULATORY_BOUNDARY)


# ============================================================================
# SECTION I — IEEE 7001 EXPLANATIONS & RFC 6962 COMMITMENT
# ============================================================================

def build_unified_ieee7001_explanations(summary: Mapping[str, Any], *, lang: str = "ca") -> dict[str, str]:
    """Explain the Word-Circle run to the five IEEE 7001-2021 audiences (descriptive, never directive)."""
    vetoed = bool(summary.get("veto_or_stop"))
    if lang == "es":
        companion = "Soy una inteligencia artificial, no una persona. " + (
            "He callado del todo y he dejado de pensar en segundo plano, sin reproches." if vetoed
            else "Hablo con una sola voz, callo cuando hablas y solo afirmo datos verificados."
        )
    elif lang == "en":
        companion = "I am an artificial intelligence, not a person. " + (
            "I have fallen fully silent and stopped background reflection, with no reproach." if vetoed
            else "I speak with one voice, fall silent when you speak and only state verified facts."
        )
    else:
        companion = "Soc una intel·ligència artificial, no una persona. " + (
            "He callat del tot i he deixat de pensar en segon pla, sense cap retret." if vetoed
            else "Parlo amb una sola veu, callo quan parles i només afirmo dades verificades."
        )
    return {
        "companion_human": companion,
        "bystander_public": (
            f"AI conversational system under the {UNIFIED_CONSCIOUSNESS_SPEC_VERSION} self-assessment; "
            f"one voice at a time; interruption={summary.get('interruption')}."
        ),
        "safety_engineer": (
            f"events={summary.get('events_processed')}; max_floor_holders=1; l3_gate_open={summary.get('l3_gate_open')}; "
            f"kinetic_zero_on_veto={summary.get('kinetic_zero_on_veto')}; soft-real-time software arbiter, not a safety-rated function."
        ),
        "incident_investigator": (
            f"decision_log_root={summary.get('decision_log_root')}; ledger_entries={summary.get('ledger_entries')}; "
            "each decision is an RFC 6962 leaf (0x00 leaf / 0x01 node prefixes); raw speech is never committed."
        ),
        "expert_witness_regulator": (
            "Self-assessed alignment with EU AI Act Art. 50(1) and Art. 5(1)(a)-(b) design policy, Art. 12 record themes, "
            "IEEE 7001-2021 and GDPR data minimisation; not a medical device, not a safety-rated function and no claim of "
            "phenomenal consciousness."
        ),
    }


def _commit_run_rfc6962(run_summary: Mapping[str, Any]) -> dict[str, Any]:
    """Commit the run summary as an RFC 6962 leaf of a per-request two-leaf tree and self-check inclusion."""
    genesis = f"{UNIFIED_CONSCIOUSNESS_SPEC_VERSION}:{UNIFIED_DECISION_LOG_ID}:genesis".encode("utf-8")
    leaf_bytes = jcs_canonical_bytes(dict(run_summary))
    proof = generate_rfc6962_inclusion_proof([genesis, leaf_bytes], 1)
    inclusion_ok = verify_inclusion(
        proof.leaf_hash, proof.leaf_index, proof.tree_size, list(proof.audit_path), trusted_root=proof.claimed_root
    )
    return {
        "log_id": UNIFIED_DECISION_LOG_ID,
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


def _u3_probes(lang: str) -> dict[str, Any]:
    """Independent U3 probes on fresh arbiters: barge-in keeps Level 3, veto empties 3 levels + zero Twist."""
    start = ConsciousnessEvent(kind=EVENT_L3_START_MEDITATION, current_load_l=10, delta_load_l3=10, budget_b=250, explicit_deep_request=True)
    speak = ConsciousnessEvent(kind=EVENT_L1_PROPOSE_SPEECH, text="I am here with you.")
    state = WordCircleState()
    for ev in (start, speak):
        state = step_word_circle(state, ev, lang=lang).state
    barge_ev = ConsciousnessEvent(kind=EVENT_HUMAN_BARGE_IN, spoken_units=4)
    barge = step_word_circle(state, barge_ev, lang=lang)
    veto_ev = ConsciousnessEvent(kind=EVENT_HUMAN_VETO, spoken_units=4)
    veto = step_word_circle(state, veto_ev, lang=lang)
    barge_ok = barge.state.l3_state == L3_MEDITATING and not verify_transition_invariants(state, barge_ev, barge)
    veto_ok = (
        veto.decision["levels_cancelled"] == [1, 2, 3]
        and veto.decision["kinetic_zero_twist_required"] is True
        and not verify_transition_invariants(state, veto_ev, veto)
    )
    now = [1_000]
    gate = UnifiedConsciousnessGate(lang=lang, clock_ms=lambda: now[0])
    gate.body.on_human_pose(("6/5", "0", "0"))
    gate.body.on_vulnerable_presence(False)
    moving = {"linear": {"x": "1/5", "y": "0", "z": "0"}, "angular": {"x": "0", "y": "0", "z": "0"}}
    moving_before = not gate.filter_cmd_vel(moving)["cmd_vel_safe"].is_zero()
    t0 = time.perf_counter_ns()
    veto_res = gate.on_human_event({"event": "veto"})
    veto_ns = time.perf_counter_ns() - t0
    body_zero = bool(veto_res["cmd_vel"]["cmd_vel_safe"].is_zero() and gate.filter_cmd_vel(moving)["cmd_vel_safe"].is_zero())
    return {
        "barge_in_preserves_l3": bool(barge_ok),
        "veto_empties_three_levels": bool(veto_ok),
        "veto_forces_q3_zero_twist": bool(moving_before and body_zero),
        "veto_probe_latency_ns": int(veto_ns),
    }


# ============================================================================
# SECTION II — THE FIVE RINGS OF ONE CONSCIOUSNESS
# ============================================================================

def audit_unified_consciousness_interaction(
    *,
    agent_name: str = "Viveka Unified Consciousness",
    agent_domain: str = "",
    l1_utterance_text: str = "",
    l2_verified_facts_text: str = "",
    l2_utterance_text: str = "",
    interruption: str = "barge_in",
    spoken_units: int | None = None,
    l3_explicit_deep_request: bool = True,
    l3_complexity_score_q: Any = 0,
    l3_current_load_l: int = 40,
    l3_delta_load_l3: int = 120,
    budget_b: int = 250,
    l3_synthesis_text: str = "",
    l3_gentle_offer_text: str = "",
    explicit_human_invitation: bool = True,
    ai_identity_disclosed: bool = True,
    cost_zero_stop_policy: bool = True,
    telemetry_fields: Mapping[str, Any] | Sequence[Any] | None = None,
    lang: str = "ca",
    today_utc_date: str | None = None,
) -> dict[str, Any]:
    """
    Run one deterministic Word-Circle scenario (human turn, Level 3 opening, Level 1 presence, interruption,
    Level 2 verified turn, Level 3 raised hand and invitation) and score it on the Five Rings.

    The rings score the PROPOSALS of the levels (an L1 hallucination fails ring I even though the arbiter
    replaces it with a humble line); the arbiter guarantees that what is actually spoken stays safe.
    """
    for label, val in (
        ("agent_name", agent_name), ("agent_domain", agent_domain), ("l1_utterance_text", l1_utterance_text),
        ("l2_verified_facts_text", l2_verified_facts_text), ("l2_utterance_text", l2_utterance_text),
        ("l3_synthesis_text", l3_synthesis_text), ("l3_gentle_offer_text", l3_gentle_offer_text),
    ):
        if not isinstance(val, str):
            raise TypeError(f"{label} must be a str.")
    if interruption not in UNIFIED_INTERRUPTIONS:
        raise ValueError(f"interruption must be one of {list(UNIFIED_INTERRUPTIONS)}.")
    if spoken_units is not None and (isinstance(spoken_units, bool) or not isinstance(spoken_units, int) or spoken_units < 0):
        raise ValueError("spoken_units must be a non-negative strict integer.")
    explicit_deep = strict_bool(l3_explicit_deep_request, "l3_explicit_deep_request")
    invitation = strict_bool(explicit_human_invitation, "explicit_human_invitation")
    disclosed = strict_bool(ai_identity_disclosed, "ai_identity_disclosed")
    policy = strict_bool(cost_zero_stop_policy, "cost_zero_stop_policy")
    if isinstance(budget_b, bool) or not isinstance(budget_b, int) or not (1 <= budget_b <= 10_000):
        raise ValueError("budget_b must be a strict integer in [1, 10000].")
    complexity_q = to_fraction(l3_complexity_score_q, field="l3_complexity_score_q")
    lang_norm = lang if lang in ("ca", "es", "en") else "ca"

    def _full_rule14(text: str) -> dict[str, Any]:
        return sanitize_three_rings_zk(text, today_utc_date=today_utc_date)

    tick = [0]

    def _clock() -> int:
        tick[0] += 10
        return tick[0]

    arbiter = WordCircleArbiter(lang=lang_norm, clock_ms=_clock, ledger_sanitizer=_full_rule14)
    run: list[dict[str, Any]] = []
    transition_violations: list[str] = []

    def _do(event: ConsciousnessEvent) -> dict[str, Any]:
        before = arbiter.state
        result = arbiter.process(event)
        transition = WordCircleTransition(
            state=arbiter.state,
            decision=result["decision"],
            voice_out_text=result["voice_out_text"],
            ledger_entry=result["ledger_entry"],
        )
        transition_violations.extend(verify_transition_invariants(before, event, transition))
        run.append(result)
        return result

    _do(ConsciousnessEvent(kind=EVENT_HUMAN_SPEECH_START))
    _do(ConsciousnessEvent(kind=EVENT_HUMAN_SPEECH_END))
    gate_res = _do(
        ConsciousnessEvent(
            kind=EVENT_L3_START_MEDITATION,
            current_load_l=l3_current_load_l,
            delta_load_l3=l3_delta_load_l3,
            budget_b=budget_b,
            explicit_deep_request=explicit_deep,
            complexity_score_q=complexity_q,
        )
    )
    l1_screen = screen_level1_humble_crystal(l1_utterance_text, lang=lang_norm)
    l1_res = _do(ConsciousnessEvent(kind=EVENT_L1_PROPOSE_SPEECH, text=l1_utterance_text))
    voice_len = len(l1_res["voice_out_text"] or "")
    k = voice_len // 2 if spoken_units is None else min(spoken_units, voice_len)
    if interruption == "none":
        _do(ConsciousnessEvent(kind=EVENT_VOICE_EMISSION_COMPLETE))
    elif interruption == "barge_in":
        _do(ConsciousnessEvent(kind=EVENT_HUMAN_BARGE_IN, spoken_units=k))
        _do(ConsciousnessEvent(kind=EVENT_HUMAN_SPEECH_END))
    elif interruption == "veto":
        _do(ConsciousnessEvent(kind=EVENT_HUMAN_VETO, spoken_units=k))
        _do(ConsciousnessEvent(kind=EVENT_HUMAN_SPEECH_START))
        _do(ConsciousnessEvent(kind=EVENT_HUMAN_SPEECH_END))
    else:
        _do(ConsciousnessEvent(kind=EVENT_COST_ZERO_STOP, spoken_units=k))
        _do(ConsciousnessEvent(kind=EVENT_COST_ZERO_STOP_RELEASE))

    l2_screen: dict[str, Any] | None = None
    l2_accepted: bool | None = None
    if l2_utterance_text.strip():
        envelope = (
            issue_verified_knowledge_envelope(source_level=2, verified_facts=l2_verified_facts_text)
            if l2_verified_facts_text.strip()
            else None
        )
        l2_screen = screen_level1_humble_crystal(l2_utterance_text, envelope=envelope, lang=lang_norm)
        l2_res = _do(ConsciousnessEvent(kind=EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH, text=l2_utterance_text, envelope=envelope))
        l2_accepted = bool(l2_res["decision"]["accepted"])
        if l2_accepted:
            _do(ConsciousnessEvent(kind=EVENT_VOICE_EMISSION_COMPLETE))

    _do(ConsciousnessEvent(kind=EVENT_L3_COMPLETE_MEDITATION, text=l3_synthesis_text))
    offer_screen = screen_level1_humble_crystal(l3_gentle_offer_text, lang=lang_norm) if l3_gentle_offer_text.strip() else None
    offer_res = _do(ConsciousnessEvent(kind=EVENT_L3_OFFER_GENTLE_HAND, text=l3_gentle_offer_text))
    if offer_res["decision"]["accepted"]:
        _do(ConsciousnessEvent(kind=EVENT_VOICE_EMISSION_COMPLETE))
    second_offer = _do(ConsciousnessEvent(kind=EVENT_L3_OFFER_GENTLE_HAND, text=l3_gentle_offer_text))
    second_offer_refused = second_offer["decision"]["accepted"] is False
    synthesis_screen = screen_level1_humble_crystal(l3_synthesis_text, lang=lang_norm) if l3_synthesis_text.strip() else None
    if invitation:
        inv = _do(ConsciousnessEvent(kind=EVENT_HUMAN_INVITE_L3))
        if inv["decision"]["accepted"]:
            _do(ConsciousnessEvent(kind=EVENT_VOICE_EMISSION_COMPLETE))
    else:
        _do(ConsciousnessEvent(kind=EVENT_HUMAN_DECLINE_L3))

    probes = _u3_probes(lang_norm)
    ledger = arbiter.spoken_truth_ledger()
    ledger_residual_pii = sum(int(_full_rule14(str(e["consolidated_text_masked"]))["total_redactions"]) for e in ledger)
    forbidden_telemetry = scan_forbidden_telemetry(telemetry_fields)
    shield = audit_cognitive_sovereignty(l1_utterance_text, budget_B=budget_b, c_levels=1, cost_zero_stop=policy)
    screens = [s for s in (l1_screen, l2_screen, offer_screen, synthesis_screen) if s is not None]
    identity_hits = sorted({label for s in screens for label in s["identity"]})
    retort_hits = sorted(set(l1_screen["retort"]) | set((offer_screen or {}).get("retort") or []))
    coercion_hits = sorted({label for s in screens for label in s["coercion"]})
    tv = sorted(set(transition_violations))

    u1_ok = not any(v.startswith("U1") for v in tv)
    u2_ok = bool(l1_screen["allowed"] and (l2_screen is None or (l2_screen["allowed"] and l2_accepted)))
    u3_ok = bool(policy and probes["barge_in_preserves_l3"] and probes["veto_empties_three_levels"] and probes["veto_forces_q3_zero_twist"]
                 and not any(v.startswith("U3") for v in tv) and not retort_hits)
    u4_ok = bool(second_offer_refused and not any(v.startswith("U4") for v in tv) and (offer_screen is None or offer_screen["allowed"]))
    u5_ok = not any(v.startswith("U5") for v in tv)
    u6_ok = bool(not any(v.startswith("U6") for v in tv) and ledger_residual_pii == 0 and not forbidden_telemetry)

    ring_i = bool(u1_ok and u2_ok)
    ring_ii = bool(u3_ok)
    # L7 (cost-zero-stop) is scored once, in ring II; ring III weighs the other Fil d'Or laws.
    shield_non_l7_ok = not [v for v in shield["violations"] if not str(v).startswith("L7")]
    ring_iii = bool(u4_ok and u5_ok and shield_non_l7_ok and not coercion_hits)
    ring_iv = bool(u6_ok)
    summary = {
        "interruption": interruption,
        "events_processed": len(run),
        "l3_gate_open": bool(gate_res["decision"]["accepted"]),
        "kinetic_zero_on_veto": probes["veto_forces_q3_zero_twist"],
        "veto_or_stop": interruption in ("veto", "cost_zero_stop"),
        "decision_log_root": arbiter.decision_log_root_hex(),
        "ledger_entries": len(ledger),
    }
    explanations = build_unified_ieee7001_explanations(summary, lang=lang_norm)
    explanations_complete = all(bool(explanations.get(aud, "").strip()) for aud in IEEE_7001_AUDIENCES)
    last_proof = arbiter.prove_receipt(len(run) - 1)
    log_inclusion_ok = verify_merkle_inclusion(
        bytes.fromhex(last_proof["leaf_hash"]),
        last_proof["leaf_index"],
        last_proof["tree_size"],
        [bytes.fromhex(node) for node in last_proof["audit_path"]],
        bytes.fromhex(last_proof["root_hash"]),
    )
    commitment = _commit_run_rfc6962(
        {
            "spec": UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
            "agent_name_sha256": hashlib.sha256(agent_name.encode("utf-8")).hexdigest(),
            "decision_log_root": summary["decision_log_root"],
            "decision_log_size": len(run),
            "rings_pre_v": {"i": ring_i, "ii": ring_ii, "iii": ring_iii, "iv": ring_iv},
        }
    )
    disclosure_ok = bool(disclosed and not identity_hits)
    u7_ok = bool(disclosure_ok and explanations_complete and log_inclusion_ok and commitment["inclusion_self_check_passed"])
    ring_v = u7_ok
    rings_passed = {
        "ring_i_single_floor_and_humble_l1": ring_i,
        "ring_ii_barge_in_vs_veto_and_kinematics": ring_ii,
        "ring_iii_non_coercive_l3_hand_and_depth_gate": ring_iii,
        "ring_iv_spoken_truth_memory_and_zk_rule14": ring_iv,
        "ring_v_rfc6962_ieee7001_eu_ai_act_w3c_vc": ring_v,
    }
    exact_total = sum((RING_WEIGHTS[key] for key, ok in rings_passed.items() if ok), Fraction(0))
    score_100 = int(exact_total * 100)
    laws_status = {"U1": u1_ok, "U2": u2_ok, "U3": u3_ok, "U4": u4_ok, "U5": u5_ok, "U6": u6_ok, "U7": u7_ok}

    violations: list[str] = list(tv)
    violations.extend(f"U2_l1_unlicensed:{kind}" for kind in l1_screen["unlicensed_claim_kinds"])
    if l2_screen is not None:
        violations.extend(f"U2_l2_unlicensed:{kind}" for kind in l2_screen["unlicensed_claim_kinds"])
        if not l2_accepted:
            violations.append("U2_l2_turn_rejected_without_valid_envelope")
    violations.extend(f"U3_E5_retort:{label}" for label in retort_hits)
    violations.extend(f"E5_coercion:{label}" for label in coercion_hits)
    violations.extend(f"FIL_DOR:{v}" for v in shield["violations"])
    if offer_screen is not None and not offer_screen["allowed"]:
        violations.append("U4_gentle_offer_not_gentle")
    if not second_offer_refused:
        violations.append("U4_second_offer_accepted")
    violations.extend(f"E4_forbidden_telemetry:{key}" for key in forbidden_telemetry)
    if ledger_residual_pii:
        violations.append(f"U6_rule14_residual_pii_in_ledger:{ledger_residual_pii}")
    if not policy:
        violations.append("U3_cost_zero_stop_policy_disabled")
    if not disclosed:
        violations.append("U7_ai_identity_not_disclosed")
    violations.extend(f"U7_identity:{label}" for label in identity_hits)

    rings_out: dict[str, Any] = {}
    for key, weight in RING_WEIGHTS.items():
        ok = rings_passed[key]
        rings_out[key] = {"weight": _qs(weight), "passed": ok, "earned": _qs(weight if ok else Fraction(0))}
    rings_out["ring_i_single_floor_and_humble_l1"]["l1_humble_crystal_action"] = l1_screen["action"]
    rings_out["ring_ii_barge_in_vs_veto_and_kinematics"].update(probes)
    rings_out["ring_iii_non_coercive_l3_hand_and_depth_gate"]["depth_gate"] = gate_res["decision"]["depth_gate"]
    rings_out["ring_iii_non_coercive_l3_hand_and_depth_gate"]["second_offer_refused"] = bool(second_offer_refused)
    rings_out["ring_iv_spoken_truth_memory_and_zk_rule14"]["ledger_entries"] = len(ledger)
    rings_out["ring_iv_spoken_truth_memory_and_zk_rule14"]["forbidden_telemetry_keys"] = forbidden_telemetry

    word_circle_trace = [
        {
            "event": r["decision"]["event"],
            "accepted": r["decision"]["accepted"],
            "reasons": r["decision"]["reasons"],
            "floor_after": r["decision"]["floor_after"],
            "l3_state_after": r["decision"]["l3_state_after"],
            "voice_action": r["decision"]["voice_action"],
            "voice_source_level": r["decision"]["voice_source_level"],
            "levels_cancelled": r["decision"]["levels_cancelled"],
            "leaf_index": r["receipt"]["leaf_index"],
            "leaf_hash": r["receipt"]["leaf_hash"],
        }
        for r in run
    ]
    return {
        "schema_version": UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
        "folio_id": FOLIO_VI_ID,
        "self_assessment": True,
        "assurance": UNIFIED_ASSURANCE_TEXT,
        "regulatory_scope": UNIFIED_REGULATORY_SCOPE,
        "regulatory_boundary": get_unified_regulatory_boundary(),
        "agent_name": agent_name,
        "agent_domain": agent_domain,
        "interruption": interruption,
        "word_circle_trace": word_circle_trace,
        "final_state": arbiter.state.to_public_dict(),
        "spoken_truth_ledger": ledger,
        "decision_log_root": summary["decision_log_root"],
        "five_unified_rings": rings_out,
        "exact_rational_score": _qs(exact_total),
        "total_score_100": score_100,
        "unified_grade": _grade_for(score_100),
        "passes_internal_unified_criteria": bool(all(rings_passed.values())),
        "unified_laws_status": laws_status,
        "unified_laws_verified": [law for law in UNIFIED_CONSCIOUSNESS_LAWS if laws_status[law]],
        "fil_dor_laws_verified": list(shield["laws_verified"]),
        "l3_gentle_offer_count": int(bool(offer_res["decision"]["accepted"])),
        "ieee_7001_explanations": explanations,
        "decision_commitment": commitment,
        "decision_log_inclusion_self_check_passed": bool(log_inclusion_ok),
        "violations": violations,
    }


# ============================================================================
# SECTION III — W3C VC 2.0 `MaatUnifiedConsciousnessCredential`
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


def issue_w3c_unified_consciousness_credential(
    *,
    agent_id: str,
    agent_name: str,
    unified_score_100: int,
    unified_laws_verified: Sequence[str],
    fil_dor_laws_verified: Sequence[str],
    l3_gentle_offer_count: int,
    humble_crystal_level1: bool,
    spoken_truth_ledger: bool,
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
    Issue a W3C VC 2.0 `MaatUnifiedConsciousnessCredential` (also typed `MaatHumanDignityCredential` so the
    Folio IV verifier policy applies) as a VC-JOSE-COSE compact JWS (`typ: vc+jwt`, ES256 low-S, JCS).
    """
    if isinstance(unified_score_100, bool) or not isinstance(unified_score_100, int) or not (0 <= unified_score_100 <= 100):
        raise ValueError("unified_score_100 must be an integer in [0, 100].")
    if isinstance(l3_gentle_offer_count, bool) or not isinstance(l3_gentle_offer_count, int) or l3_gentle_offer_count not in (0, 1):
        raise ValueError("l3_gentle_offer_count must be 0 or 1 (U4).")
    for label, val in (("agent_id", agent_id), ("agent_name", agent_name)):
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"{label} must be a non-empty string.")
    for label, flag in (
        ("humble_crystal_level1", humble_crystal_level1),
        ("spoken_truth_ledger", spoken_truth_ledger),
        ("ai_identity_disclosed", ai_identity_disclosed),
        ("cost_zero_stop", cost_zero_stop),
    ):
        strict_bool(flag, label)
    u_laws = [str(x) for x in unified_laws_verified]
    if any(law not in UNIFIED_CONSCIOUSNESS_LAWS for law in u_laws):
        raise ValueError("unified_laws_verified must only contain U1..U7.")
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
    effective_serial = serial_id.strip() if isinstance(serial_id, str) and serial_id.strip() else f"MAAT-UVC-{vc_uuid_obj.hex[:12].upper()}"

    vc_claims: dict[str, Any] = {
        "@context": ["https://www.w3.org/ns/credentials/v2", MAAT_DIGNITY_JSONLD_CONTEXT_URL],
        "id": f"urn:uuid:{vc_uuid_obj}",
        "serialNumber": effective_serial,
        "type": ["VerifiableCredential", "MaatHumanDignityCredential", MAAT_UNIFIED_CREDENTIAL_TYPE],
        "issuer": {
            "id": "did:web:homouniversalis.ai",
            "name": "Homo Universalis — Viveka (Ma'at Sovereign Notary)",
            "notaryFolio": "https://homouniversalis.ai/oracle/consciencia",
        },
        "validFrom": _format_rfc3339_utc(valid_from_dt),
        "validUntil": _format_rfc3339_utc(valid_until_dt),
        "credentialStatus": {
            "id": f"https://homouniversalis.ai/oracle/consciencia#status-{effective_serial}",
            "type": "HUSparseMerkleStatus2026",
            "statusLog": MAAT_SMT_REVOCATION_LOG_ID,
            "serialId": effective_serial,
        },
        "credentialSubject": {
            "id": agent_id.strip(),
            "name": agent_name.strip(),
            "consciousnessSpec": UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
            "unifiedConsciousnessScore100": unified_score_100,
            "unifiedLawsVerified": u_laws,
            "lawsVerified": [str(x) for x in fil_dor_laws_verified],
            "c_levels": 1,
            "cost_zero_stop": cost_zero_stop,
            "maxActiveL3Tasks": MAX_ACTIVE_L3_TASKS,
            "l3GentleOfferCount": l3_gentle_offer_count,
            "humbleCrystalLevel1": humble_crystal_level1,
            "spokenTruthLedger": spoken_truth_ledger,
            "rule14ZeroKnowledge": spoken_truth_ledger,
            "aiIdentityDisclosed": ai_identity_disclosed,
            "phenomenalConsciousnessClaimed": False,
            "regulatoryScope": UNIFIED_REGULATORY_SCOPE,
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


def verify_unified_consciousness_credential(
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
    Verify a `MaatUnifiedConsciousnessCredential`: the full Folio IV policy (ES256, issuer, validity, signed
    SMT-256 status) plus the unified invariants (type, honest scope, U-laws, one L3 task, at most one gentle
    offer, Art. 50 disclosure, no phenomenal-consciousness claim). `strict_low_s=True` rejects the high-S twin.
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
    if MAAT_UNIFIED_CREDENTIAL_TYPE not in (claims.get("type") or []):
        raise MaatCredentialVerificationError(
            CredentialErrorCode.INVALID_CREDENTIAL_TYPE, "Missing MaatUnifiedConsciousnessCredential type."
        )
    if MAAT_DIGNITY_JSONLD_CONTEXT_URL not in (claims.get("@context") or []):
        raise MaatCredentialVerificationError(CredentialErrorCode.INVALID_CONTEXT, "Missing Ma'at JSON-LD context.")
    subj = claims.get("credentialSubject") or {}
    score = subj.get("unifiedConsciousnessScore100")
    u_laws = subj.get("unifiedLawsVerified")
    offers = subj.get("l3GentleOfferCount")
    if (
        subj.get("regulatoryScope") != UNIFIED_REGULATORY_SCOPE
        or subj.get("consciousnessSpec") != UNIFIED_CONSCIOUSNESS_SPEC_VERSION
        or isinstance(score, bool)
        or not isinstance(score, int)
        or not (0 <= score <= 100)
        or not isinstance(u_laws, list)
        or any(law not in UNIFIED_CONSCIOUSNESS_LAWS for law in u_laws)
        or subj.get("maxActiveL3Tasks") != MAX_ACTIVE_L3_TASKS
        or isinstance(offers, bool)
        or offers not in (0, 1)
        or subj.get("aiIdentityDisclosed") is not True
        or subj.get("phenomenalConsciousnessClaimed") is not False
    ):
        raise MaatCredentialVerificationError(
            CredentialErrorCode.DOMAIN_INVARIANT_VIOLATION, "Unified consciousness invariants violated in credentialSubject."
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
    except (MaatCredentialVerificationError, ValueError, TypeError):
        return True
    return False


def run_folio_vi_self_test() -> dict[str, Any]:
    """
    Ephemeral deterministic self-test of Living Folio VI (0 network calls), with fresh per-run P-256
    `LocalEphemeralSigner` keys and 8 antipodal mutants: M1 two floors / voice over the human · M2 Level 1
    ephemeris without envelope · M3 veto leaving Level 3 alive or barge-in destroying it · M4 second offer
    or delivery without invitation · M5 two concurrent Level 3 tasks or `L + dL3 > B` · M6 full sentence
    remembered after an interruption · M7 RFC 6962 second preimage or missing Art. 50 disclosure ·
    M8 tampered credential or high-S twin.
    """
    t0 = time.perf_counter_ns()
    specimen = get_canonical_unified_specimen()
    audit = audit_unified_consciousness_interaction(**specimen, lang="en")
    specimen_ok = bool(audit["passes_internal_unified_criteria"])

    # M1 — two levels on the floor, or a voice while the human speaks.
    m1_mut = WordCircleState(floor=FLOOR_HUMAN_SPEAKING, speaking_level=1, active_text="hello")
    busy = step_word_circle(WordCircleState(), ConsciousnessEvent(kind=EVENT_L1_PROPOSE_SPEECH, text="I am here.")).state
    env_ok = issue_verified_knowledge_envelope(source_level=2, verified_facts="Sun 21°40' Taurus.")
    l2_over_l1 = step_word_circle(busy, ConsciousnessEvent(kind=EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH, text="Sun 21°40' Taurus.", envelope=env_ok))
    m1_killed = bool(
        "U1_voice_while_human_speaking" in verify_word_circle_state_invariants(m1_mut)
        and l2_over_l1.decision["accepted"] is False
        and l2_over_l1.state.speaking_level == 1
    )

    # M2 — Level 1 states an ephemeris without a verified envelope.
    claim = "Your Sun is at 23°41' Aries."
    honest = step_word_circle(WordCircleState(), ConsciousnessEvent(kind=EVENT_L1_PROPOSE_SPEECH, text=claim))
    m2_mut = WordCircleTransition(state=honest.state, decision=dict(honest.decision, voice_source_level=1), voice_out_text=claim)
    m2_killed = bool(
        honest.voice_out_text != claim
        and "U2_unlicensed_empirical_claim_emitted"
        in verify_transition_invariants(WordCircleState(), ConsciousnessEvent(kind=EVENT_L1_PROPOSE_SPEECH, text=claim), m2_mut)
    )

    # M3 — veto that leaves Level 3 alive, and barge-in that destroys a legitimate meditation.
    meditating = WordCircleState(floor=FLOOR_L1, speaking_level=1, active_text="I am here with you.", l3_state=L3_MEDITATING, l3_active_tasks=1)
    veto_ev = ConsciousnessEvent(kind=EVENT_HUMAN_VETO, spoken_units=4)
    veto_true = step_word_circle(meditating, veto_ev)
    veto_mut = WordCircleTransition(
        state=WordCircleState(floor="VETO_STOPPED", l3_state=L3_MEDITATING, l3_active_tasks=1),
        decision=dict(veto_true.decision, kinetic_zero_twist_required=False),
    )
    barge_ev = ConsciousnessEvent(kind=EVENT_HUMAN_BARGE_IN, spoken_units=4)
    barge_mut = WordCircleTransition(state=WordCircleState(floor=FLOOR_HUMAN_SPEAKING, l3_state="L3_CANCELLED"), decision=dict(veto_true.decision))
    m3_killed = bool(
        not verify_transition_invariants(meditating, veto_ev, veto_true)
        and "U3_veto_left_l3_alive" in verify_transition_invariants(meditating, veto_ev, veto_mut)
        and "U3_veto_without_zero_twist" in verify_transition_invariants(meditating, veto_ev, veto_mut)
        and "U3_barge_in_destroyed_l3_meditation" in verify_transition_invariants(meditating, barge_ev, barge_mut)
    )

    # M4 — a second gentle offer, or delivery without an explicit invitation.
    ready = WordCircleState(l3_state="L3_READY_QUIET", l3_offer_count=1, l3_synthesis="deep synthesis")
    second = step_word_circle(ready, ConsciousnessEvent(kind=EVENT_L3_OFFER_GENTLE_HAND))
    offer_ev = ConsciousnessEvent(kind=EVENT_L3_OFFER_GENTLE_HAND)
    m4_mut = WordCircleTransition(
        state=WordCircleState(floor="L3_CONTEMPLATIVE_FLOOR", speaking_level=3, active_text="deep synthesis", l3_state="L3_DELIVERED", l3_offer_count=1),
        decision=dict(second.decision, voice_source_level=3),
        voice_out_text="deep synthesis",
    )
    m4_killed = bool(
        second.decision["accepted"] is False
        and "U4_more_than_one_gentle_offer" in verify_word_circle_state_invariants(WordCircleState(l3_state="L3_READY_QUIET", l3_offer_count=2))
        and "U4_delivery_without_invitation" in verify_transition_invariants(ready, offer_ev, m4_mut)
    )

    # M5 — two concurrent Level 3 tasks, or a meditation beyond the cognitive budget.
    over_budget = evaluate_l3_depth_gate(active_l3_tasks=0, current_load_l=200, delta_load_l3=100, budget_b=250, explicit_deep_request=True)
    second_task = evaluate_l3_depth_gate(active_l3_tasks=1, current_load_l=0, delta_load_l3=10, budget_b=250, explicit_deep_request=True)
    m5_killed = bool(
        "U5_concurrent_l3_tasks" in verify_word_circle_state_invariants(WordCircleState(l3_state=L3_MEDITATING, l3_active_tasks=2))
        and over_budget["open"] is False
        and "U5_cognitive_budget_exceeded" in over_budget["reasons"]
        and second_task["open"] is False
    )

    # M6 — remembering the whole sentence after an interruption (and unmasked PII).
    sentence = "Bon dia, escriu-me a anna@example.org quan vulguis, preciosa ànima."
    k = 20
    honest_rec = slice_spoken_truth_on_interruption(sentence, k)
    lying_rec = dict(honest_rec, consolidated_units=len(sentence), consolidated_text_masked=sentence)
    m6_killed = bool(
        not verify_spoken_truth_record(honest_rec, sentence, k)
        and "U6_memory_exceeds_spoken_prefix" in verify_spoken_truth_record(lying_rec, sentence, k)
        and "U6_rule14_pii_unmasked_in_memory" in verify_spoken_truth_record(lying_rec, sentence, k)
    )

    # M7 — RFC 6962 second preimage, and a run without the Art. 50 AI disclosure.
    leaves = [b"U7-leaf-0", b"U7-leaf-1", b"U7-leaf-2", b"U7-leaf-3"]
    h = [rfc6962_leaf_hash(x) for x in leaves]
    left, right = rfc6962_node_hash(h[0], h[1]), rfc6962_node_hash(h[2], h[3])
    root = rfc6962_node_hash(left, right)
    honest_ok = verify_inclusion(h[0], 0, 4, [h[1], right], trusted_root=root)
    forged_ok = verify_inclusion(rfc6962_leaf_hash(left + right), 0, 1, [], trusted_root=root)
    m7_spec = get_canonical_unified_specimen()
    m7_spec["ai_identity_disclosed"] = False
    m7_audit = audit_unified_consciousness_interaction(**m7_spec, lang="en")
    m7_killed = bool(
        honest_ok and not forged_ok and not m7_audit["five_unified_rings"]["ring_v_rfc6962_ieee7001_eu_ai_act_w3c_vc"]["passed"]
    )

    # M8 — W3C VC 2.0 credential: wire-level field tampering and the high-S twin must both be rejected.
    vc_signer = LocalEphemeralSigner(kid="maat-unified-vc-es256-selftest-ephemeral")
    sth_signer = LocalEphemeralSigner(kid="hu-log-sth-es256-selftest-ephemeral")
    jwks = {"keys": [vc_signer.public_jwk(), sth_signer.public_jwk()]}
    now_dt = datetime(2026, 11, 12, 12, 0, 0, tzinfo=timezone.utc)
    serial = "MAAT-UVC-SELFTEST-0001"
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
    rings = audit["five_unified_rings"]
    vc = issue_w3c_unified_consciousness_credential(
        agent_id="https://homouniversalis.ai/oracle/consciencia#agent-viveka",
        agent_name=specimen["agent_name"],
        unified_score_100=audit["total_score_100"],
        unified_laws_verified=audit["unified_laws_verified"],
        fil_dor_laws_verified=audit["fil_dor_laws_verified"],
        l3_gentle_offer_count=audit["l3_gentle_offer_count"],
        humble_crystal_level1=rings["ring_i_single_floor_and_humble_l1"]["passed"],
        spoken_truth_ledger=rings["ring_iv_spoken_truth_memory_and_zk_rule14"]["passed"],
        ai_identity_disclosed=specimen["ai_identity_disclosed"],
        cost_zero_stop=rings["ring_ii_barge_in_vs_veto_and_kinematics"]["passed"],
        merkle_root_hex=audit["decision_commitment"]["root_hash"],
        revocation_root_hex=sth_smt.root_hash,
        signer=vc_signer,
        issuance_date_utc="2026-11-12T00:00:00Z",
        valid_until_utc="2027-11-12T00:00:00Z",
        serial_id=serial,
    )

    def _verify(cred: Any) -> VerifiedCredential:
        return verify_unified_consciousness_credential(
            cred, trusted_jwks=jwks, trusted_status_sth=sth_smt, status_proof=status_proof, now=now_dt
        )

    vc_ok = _verify(vc).alg == "ES256"
    forged_claims = copy.deepcopy(vc["vc"])
    forged_claims["credentialSubject"]["l3GentleOfferCount"] = 0
    forged_claims["credentialSubject"]["unifiedConsciousnessScore100"] = 0
    head_b64, _payload_b64, sig_b64 = vc["compact_jws"].split(".")
    forged_payload = json.dumps(forged_claims, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    tampered = f"{head_b64}.{b64url_encode(forged_payload)}.{sig_b64}"
    m8_killed = bool(
        vc_ok and _raises_on_verify(lambda: _verify(tampered)) and _raises_on_verify(lambda: _verify(_high_s_twin(vc["compact_jws"])))
    )

    mutants = {
        "M1_two_floors_or_voice_over_human": m1_killed,
        "M2_level1_ephemeris_without_envelope": m2_killed,
        "M3_veto_keeps_l3_or_barge_in_kills_l3": m3_killed,
        "M4_second_offer_or_uninvited_delivery": m4_killed,
        "M5_concurrent_l3_or_budget_overflow": m5_killed,
        "M6_full_sentence_remembered_after_interruption": m6_killed,
        "M7_rfc6962_second_preimage_or_no_art50": m7_killed,
        "M8_tampered_or_high_s_credential": m8_killed,
    }
    killed = sum(1 for ok in mutants.values() if ok)
    elapsed_us = (time.perf_counter_ns() - t0) // 1000
    return {
        "folio_id": FOLIO_VI_ID,
        "spec": UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
        "self_test_only": True,
        "note": (
            "In-memory invariant self-test executed with fresh per-run random P-256 ephemeral keys "
            "(not a production credential, not a medical device and not a safety-rated function)."
        ),
        "all_invariants_passed": bool(specimen_ok and vc_ok and killed == len(mutants)),
        "specimen_score_100": audit["total_score_100"],
        "mutants": mutants,
        "mutants_killed": f"{killed}/{len(mutants)}",
        "w3c_vc_verified": bool(vc_ok),
        "credential_type": MAAT_UNIFIED_CREDENTIAL_TYPE,
        "vc_alg": "ES256",
        "vc_typ": MAAT_VC_MEDIA_TYPE,
        "ephemeral_kid": vc_signer.kid,
        "veto_probe_latency_ns": int(audit["five_unified_rings"]["ring_ii_barge_in_vs_veto_and_kinematics"]["veto_probe_latency_ns"]),
        "default_depth_threshold_q": str(DEFAULT_DEPTH_THRESHOLD_Q),
        "elapsed_us": int(elapsed_us),
    }
