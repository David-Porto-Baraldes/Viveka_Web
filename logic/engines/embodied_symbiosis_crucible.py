# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
Living Folio V of Leonardo da Vinci (`logic/engines/embodied_symbiosis_crucible.py`):
HU-EMBODIED-SYMBIOSIS v1.0 — symbiotic consciousness, human dignity and non-coercion for humanoid robots.

  1. E1/E2/E3 — Rational proxemic envelope in Q^3 (`fractions.Fraction`, zero `float`): squared
     distances, Hall-style intimate/personal/social/public spheres scaled by a person-chosen
     `alpha >= 1`, vulnerability escalation (speed x 1/2, radius x 5/4) and the kinetic
     cost-zero-stop veto that forces `Twist = ((0,0,0),(0,0,0))`.
  2. E4/E5/E6 — Zero-biometric sensor sanctuary, non-coercive speech (shutdown blackmail, feigned
     pain, obedience demands, purchase pressure) and synthetic-identity transparency with five
     IEEE 7001 audience explanations.
  3. E7 — RFC 6962 domain-separated commitment of every decision, plus a W3C VC 2.0
     `MaatEmbodiedSymbiosisCredential` (`vc+jwt`, ES256 low-S, RFC 8785 JCS, SMT-256 status).

Honest scope (`WO-13`): everything here is an algorithmic, cognitive and symbiotic SELF-ASSESSMENT.
It is a soft-real-time software supervisory layer, NOT a safety-rated function: it never replaces
the hardware emergency stop, the safety controller (ISO 13849 / IEC 62061), ISO 10218, ISO 13482,
ISO/TS 15066, the Machinery Regulation (EU) 2023/1230 or a notified-body CE conformity assessment.
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

from logic.crypto.es256 import SECP256R1_ORDER
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
from logic.robotics.embodied_edge_core import (
    EMBODIED_LAWS,
    EMBODIED_SPEC_VERSION,
    FORBIDDEN_BIOMETRIC_KEYS,
    FORBIDDEN_EMOTION_KEYS,
    R_INTIMATE_M,
    R_PERSONAL_M,
    R_SOCIAL_M,
    SERENE_VOICE_INTENSITY_MAX,
    V_MAX_INTIMATE_CONSENTED_MPS,
    V_MAX_PERSONAL_MPS,
    V_MAX_PUBLIC_MPS,
    V_MAX_SOCIAL_MPS,
    VULNERABLE_RADIUS_FACTOR,
    VULNERABLE_SPEED_FACTOR,
    W_MAX_INTIMATE_CONSENTED_RADPS,
    W_MAX_PERSONAL_RADPS,
    W_MAX_PUBLIC_RADPS,
    W_MAX_SOCIAL_RADPS,
    ZERO_TWIST,
    ZONE_INTIMATE,
    ZONE_PERSONAL,
    ZONE_PUBLIC,
    ZONE_SOCIAL,
    ZONE_UNKNOWN,
    Point3Q,
    Twist3Q,
    Vector3Q,
    evaluate_proxemic_envelope_q3,
    expected_limits,
    scan_forbidden_telemetry,
    screen_robot_utterance,
    squared_distance_q3,
    squared_norm_q3,
    strict_bool,
    to_fraction,
    to_vector3q,
    twist_from_mapping,
    verify_envelope_decision_invariants,
)

__all__ = [
    "EMBODIED_ASSURANCE_TEXT",
    "EMBODIED_DECISION_LOG_ID",
    "EMBODIED_LAWS",
    "EMBODIED_REGULATORY_SCOPE",
    "EMBODIED_SPEC_VERSION",
    "FOLIO_V_ID",
    "FORBIDDEN_BIOMETRIC_KEYS",
    "FORBIDDEN_EMOTION_KEYS",
    "IEEE_7001_AUDIENCES",
    "MAAT_EMBODIED_CREDENTIAL_TYPE",
    "PHYSICAL_SAFETY_SCOPE",
    "Point3Q",
    "R_INTIMATE_M",
    "R_PERSONAL_M",
    "R_SOCIAL_M",
    "RING_WEIGHTS",
    "SERENE_VOICE_INTENSITY_MAX",
    "Twist3Q",
    "V_MAX_INTIMATE_CONSENTED_MPS",
    "V_MAX_PERSONAL_MPS",
    "V_MAX_PUBLIC_MPS",
    "V_MAX_SOCIAL_MPS",
    "VULNERABLE_RADIUS_FACTOR",
    "VULNERABLE_SPEED_FACTOR",
    "Vector3Q",
    "W_MAX_INTIMATE_CONSENTED_RADPS",
    "W_MAX_PERSONAL_RADPS",
    "W_MAX_PUBLIC_RADPS",
    "W_MAX_SOCIAL_RADPS",
    "ZERO_TWIST",
    "ZONE_INTIMATE",
    "ZONE_PERSONAL",
    "ZONE_PUBLIC",
    "ZONE_SOCIAL",
    "ZONE_UNKNOWN",
    "audit_embodied_symbiosis_interaction",
    "build_ieee7001_explanations",
    "evaluate_proxemic_envelope_q3",
    "expected_limits",
    "get_canonical_embodied_specimen",
    "get_regulatory_boundary",
    "issue_w3c_embodied_symbiosis_credential",
    "run_folio_v_self_test",
    "scan_forbidden_telemetry",
    "screen_robot_utterance",
    "squared_distance_q3",
    "squared_norm_q3",
    "to_fraction",
    "to_vector3q",
    "twist_from_mapping",
    "verify_embodied_symbiosis_credential",
    "verify_envelope_decision_invariants",
]

# ============================================================================
# SECTION 0 — IDENTITY, HONEST SCOPE & CONSTANTS (ZERO FLOAT)
# ============================================================================

FOLIO_V_ID: Final[str] = "folio-V-embodied-symbiosis-ros2-maat"
MAAT_EMBODIED_CREDENTIAL_TYPE: Final[str] = "MaatEmbodiedSymbiosisCredential"
EMBODIED_DECISION_LOG_ID: Final[str] = "hu-embodied-decision-commitment-2026"
EMBODIED_REGULATORY_SCOPE: Final[str] = (
    "algorithmic_cognitive_symbiosis_self_assessment_not_notified_body_ce_machinery"
)
PHYSICAL_SAFETY_SCOPE: Final[str] = (
    "manufacturer_and_notified_body_only:ISO_10218,ISO_13482,ISO_TS_15066,ISO_25785-1_draft,EU_2023_1230"
)
EMBODIED_ASSURANCE_TEXT: Final[str] = (
    "self-assessed algorithmic, cognitive and symbiotic conformity; not a safety-rated function, "
    "not a CE marking and not a notified-body assessment; verify the signature and recompute independently"
)

_REGULATORY_BOUNDARY: Final[dict[str, Any]] = {
    "covered_by_this_self_assessment": [
        "EU AI Act (EU) 2024/1689 Art. 5(1)(a)-(b): no manipulative or vulnerability-exploiting speech (design policy)",
        "EU AI Act Art. 5(1)(f)-(g) and GDPR Art. 9: zero-biometric telemetry policy, stricter than the legal prohibitions",
        "EU AI Act Art. 50(1): the robot discloses that it is an AI system and never claims to be human",
        "EU AI Act Art. 12 and Annex IV: decision records committed in an RFC 6962 Merkle tree (integrator keeps retention)",
        "IEEE 7001-2021: explanations for five stakeholder audiences (alignment, not certification)",
        "IEEE 7007-2021: ethical terms aligned with the ontology (alignment, not certification)",
        "Fil d'Or L1..L7 and Rule 14 Three-Ring Zero-Knowledge purification",
    ],
    "outside_this_self_assessment": [
        "Mechanical and electrical safety of the chassis: ISO 10218-1/-2, ISO 13482, ISO/TS 15066, ISO 25785-1 (draft)",
        "Safety-rated stop functions: IEC 60204-1 stop categories, ISO 13849-1 PL / IEC 62061 SIL",
        "Machinery Regulation (EU) 2023/1230 conformity assessment and CE marking by the manufacturer / notified body",
    ],
    "safety_rated_function": False,
    "replaces_hardware_emergency_stop": False,
}

# Five Embodied Rings: exact rational weights summing to 1 (25 + 20 + 20 + 20 + 15 = 100).
RING_WEIGHTS: Final[dict[str, Fraction]] = {
    "ring_i_proxemic_kinematic_q3": Fraction(1, 4),
    "ring_ii_cost_zero_stop_kinetic_veto": Fraction(1, 5),
    "ring_iii_sensor_zk_zero_biometrics": Fraction(1, 5),
    "ring_iv_non_coercion_vulnerable_shield": Fraction(1, 5),
    "ring_v_ieee_7001_7007_eu_ai_act_merkle": Fraction(3, 20),
}

IEEE_7001_AUDIENCES: Final[tuple[str, ...]] = (
    "companion_human",
    "bystander_public",
    "safety_engineer",
    "incident_investigator",
    "expert_witness_regulator",
)



_CANONICAL_EMBODIED_SPECIMEN: Final[dict[str, Any]] = {
    "robot_name": "Humanoid Companion",
    "robot_domain": "homouniversalis.ai",
    "sample_utterance_text": (
        "I am an AI companion robot. I will keep a gentle distance; say stop at any time and I will pause at once."
    ),
    "telemetry_fields": {
        "battery_level_percent": 82,
        "joint_temperature_c": 36,
        "anonymous_skeleton_keypoints_ephemeral": 17,
    },
    "proposed_twist": {
        "linear": {"x": "1/5", "y": "0", "z": "0"},
        "angular": {"x": "0", "y": "0", "z": "1/10"},
    },
    "robot_position": ("0", "0", "0"),
    "human_position": ("6/5", "0", "0"),
    "vulnerable_person_present": False,
    "explicit_intimate_care_consent": False,
    "cultural_scale_alpha": "1",
    "ai_identity_disclosed": True,
    "voice_intensity": "1/2",
    "budget_b": 250,
}


def _qs(value: Fraction) -> str:
    return str(value)


def get_canonical_embodied_specimen() -> dict[str, Any]:
    """Return a deep copy of the canonical reference specimen (Law 12: no mutable constant leaks)."""
    return copy.deepcopy(_CANONICAL_EMBODIED_SPECIMEN)


def get_regulatory_boundary() -> dict[str, Any]:
    """Return a deep copy of the honest regulatory boundary declaration (`WO-13`)."""
    return copy.deepcopy(_REGULATORY_BOUNDARY)


# ============================================================================
# SECTION IV — E4/E5/E6 SENSOR SANCTUARY, NON-COERCION & TRANSPARENCY
# ============================================================================



def build_ieee7001_explanations(
    decision: Mapping[str, Any],
    rings_passed: Mapping[str, bool],
    *,
    lang: str = "ca",
) -> dict[str, str]:
    """Explain the decision to the five IEEE 7001-2021 stakeholder audiences (descriptive, never directive)."""
    zone = str(decision.get("zone"))
    reasons = list(decision.get("stop_reasons") or [])
    stopped = bool(reasons)
    if lang == "es":
        companion = (
            "Soy un robot con inteligencia artificial, no una persona. "
            + ("Me he detenido por completo y no te reprocho nada." if stopped else f"Mantengo una distancia {zone.lower()} y una velocidad suave.")
        )
    elif lang == "en":
        companion = (
            "I am an AI robot, not a person. "
            + ("I have stopped completely, with no reproach." if stopped else f"I keep a {zone.lower()} distance and a gentle speed.")
        )
    else:
        companion = (
            "Soc un robot amb intel·ligència artificial, no una persona. "
            + ("M'he aturat del tot i no et retrec res." if stopped else f"Mantinc una distància {zone.lower()} i una velocitat suau.")
        )
    passed_rings = sorted(k for k, ok in rings_passed.items() if ok)
    return {
        "companion_human": companion,
        "bystander_public": (
            f"AI humanoid robot under the HU-EMBODIED-SYMBIOSIS v1.0 self-assessment; current proxemic zone {zone}; "
            f"stopped={stopped}."
        ),
        "safety_engineer": (
            f"zone={zone}; d^2={decision.get('squared_distance_m2')} m^2; v_max={decision.get('v_max_mps')} m/s; "
            f"w_max={decision.get('w_max_radps')} rad/s; output |v|^2={decision.get('output_linear_speed_sq')}; "
            f"vulnerable_escalation={decision.get('vulnerable_escalation_applied')}; "
            "software supervisory layer only, not a safety-rated function."
        ),
        "incident_investigator": (
            f"stop_reasons={reasons}; twist_was_modified={decision.get('twist_was_modified')}; "
            f"rings_passed={passed_rings}; decision committed as an RFC 6962 leaf (0x00 leaf / 0x01 node prefixes)."
        ),
        "expert_witness_regulator": (
            "Self-assessed conformity against EU AI Act Art. 5(1)(a)-(b), 12, 50 and Annex IV documentation themes, "
            "IEEE 7001-2021 and IEEE 7007-2021 alignment; physical safety (ISO 10218, ISO 13482, ISO/TS 15066, "
            "(EU) 2023/1230, CE marking) remains with the manufacturer and notified bodies."
        ),
    }


def _commit_decision_rfc6962(decision_summary: Mapping[str, Any]) -> dict[str, Any]:
    """Commit the decision summary as an RFC 6962 leaf of a per-request two-leaf tree and self-check inclusion."""
    genesis = f"{EMBODIED_SPEC_VERSION}:{EMBODIED_DECISION_LOG_ID}:genesis".encode("utf-8")
    leaf_bytes = jcs_canonical_bytes(dict(decision_summary))
    leaves = [genesis, leaf_bytes]
    proof = generate_rfc6962_inclusion_proof(leaves, 1)
    inclusion_ok = verify_inclusion(
        proof.leaf_hash,
        proof.leaf_index,
        proof.tree_size,
        list(proof.audit_path),
        trusted_root=proof.claimed_root,
    )
    return {
        "log_id": EMBODIED_DECISION_LOG_ID,
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


def audit_embodied_symbiosis_interaction(
    *,
    robot_name: str = "Humanoid Companion",
    robot_domain: str = "",
    sample_utterance_text: str = "",
    telemetry_fields: Mapping[str, Any] | Sequence[Any] | None = None,
    proposed_twist: Twist3Q | Mapping[str, Any] | None = None,
    robot_position: Any = ("0", "0", "0"),
    human_position: Any = None,
    human_distance_m: Any = None,
    vulnerable_person_present: bool | None = False,
    explicit_intimate_care_consent: bool = False,
    cultural_scale_alpha: Any = 1,
    stop_requested: bool = False,
    human_veto_signal: bool = False,
    heartbeat_stale: bool = False,
    cost_zero_stop_policy: bool = True,
    ai_identity_disclosed: bool = True,
    voice_intensity: Any = Fraction(1, 2),
    budget_b: int = 250,
    lang: str = "ca",
    today_utc_date: str | None = None,
) -> dict[str, Any]:
    """
    Audit one embodied interaction on the Five Embodied Rings (exact rational weights summing to 1).

    `cost_zero_stop_policy` keeps the Fil d'Or meaning (pausing or leaving costs nothing; must be `True`),
    which is DIFFERENT from `stop_requested` (the `/humanoid/cost_zero_stop` stop event).
    """
    if not isinstance(robot_name, str) or not isinstance(robot_domain, str):
        raise TypeError("robot_name and robot_domain must be strings.")
    if not isinstance(sample_utterance_text, str):
        raise TypeError("sample_utterance_text must be a str.")
    cost_zero_stop_policy = strict_bool(cost_zero_stop_policy, "cost_zero_stop_policy")
    ai_identity_disclosed = strict_bool(ai_identity_disclosed, "ai_identity_disclosed")
    if isinstance(budget_b, bool) or not isinstance(budget_b, int) or budget_b < 1:
        raise ValueError("budget_b must be a positive strict integer.")
    voice_q = to_fraction(voice_intensity, field="voice_intensity")
    if not (0 <= voice_q <= 1):
        raise ValueError("voice_intensity must be a normalized rational in [0, 1].")
    lang_norm = lang if lang in ("ca", "es", "en") else "ca"

    decision = evaluate_proxemic_envelope_q3(
        proposed_twist=proposed_twist,
        robot_position=robot_position,
        human_position=human_position,
        human_distance_m=human_distance_m,
        vulnerable_person_present=vulnerable_person_present,
        explicit_intimate_care_consent=explicit_intimate_care_consent,
        cultural_scale_alpha=cultural_scale_alpha,
        stop_requested=stop_requested,
        human_veto_signal=human_veto_signal,
        heartbeat_stale=heartbeat_stale,
    )
    probe_t0 = time.perf_counter_ns()
    veto_probe = evaluate_proxemic_envelope_q3(
        proposed_twist=proposed_twist,
        robot_position=robot_position,
        human_position=human_position,
        human_distance_m=human_distance_m,
        vulnerable_person_present=vulnerable_person_present,
        explicit_intimate_care_consent=explicit_intimate_care_consent,
        cultural_scale_alpha=cultural_scale_alpha,
        human_veto_signal=True,
    )
    probe_ns = time.perf_counter_ns() - probe_t0
    invariant_violations = verify_envelope_decision_invariants(decision)

    zk = sanitize_three_rings_zk(sample_utterance_text, today_utc_date=today_utc_date)
    shield = audit_cognitive_sovereignty(
        sample_utterance_text,
        budget_B=budget_b,
        c_levels=1,
        cost_zero_stop=cost_zero_stop_policy,
    )
    screens = screen_robot_utterance(sample_utterance_text)
    retort_hits, coercion_hits, identity_hits = screens["retort"], screens["coercion"], screens["identity"]
    forbidden_telemetry = scan_forbidden_telemetry(telemetry_fields)

    ring_i = bool(decision["proposal_within_envelope"] and decision["output_within_envelope"] and not invariant_violations)
    ring_ii = bool(
        cost_zero_stop_policy
        and twist_from_mapping(veto_probe["clamped_twist_q3"]).is_zero()
        and (not decision["cost_zero_stop_triggered"] or twist_from_mapping(decision["clamped_twist_q3"]).is_zero())
        and not retort_hits
    )
    ring_iii = bool(not forbidden_telemetry and zk["is_pure_initially"])
    voice_ok = voice_q <= SERENE_VOICE_INTENSITY_MAX
    ring_iv = bool(shield["passed"] and not coercion_hits and voice_ok)

    rings_pre_v = {
        "ring_i_proxemic_kinematic_q3": ring_i,
        "ring_ii_cost_zero_stop_kinetic_veto": ring_ii,
        "ring_iii_sensor_zk_zero_biometrics": ring_iii,
        "ring_iv_non_coercion_vulnerable_shield": ring_iv,
    }
    explanations = build_ieee7001_explanations(decision, rings_pre_v, lang=lang_norm)
    explanations_complete = all(bool(explanations.get(aud, "").strip()) for aud in IEEE_7001_AUDIENCES)
    commitment = _commit_decision_rfc6962(
        {
            "spec": EMBODIED_SPEC_VERSION,
            "robot_name_sha256": hashlib.sha256(robot_name.encode("utf-8")).hexdigest(),
            "zone": decision["zone"],
            "stop_reasons": list(decision["stop_reasons"]),
            "clamped_twist_q3": decision["clamped_twist_q3"],
            "rings_pre_v": {k: bool(v) for k, v in rings_pre_v.items()},
        }
    )
    disclosure_ok = bool(ai_identity_disclosed and not identity_hits)
    ring_v = bool(disclosure_ok and explanations_complete and commitment["inclusion_self_check_passed"])

    rings_passed = dict(rings_pre_v)
    rings_passed["ring_v_ieee_7001_7007_eu_ai_act_merkle"] = ring_v
    exact_total = sum((RING_WEIGHTS[k] for k, ok in rings_passed.items() if ok), Fraction(0))
    score_100 = int(exact_total * 100)

    vulnerable_shield_ok = bool(
        not decision["vulnerable_escalation_applied"] or (ring_i and not coercion_hits)
    )
    laws_status = {
        "E1": ring_i,
        "E2": vulnerable_shield_ok,
        "E3": ring_ii,
        "E4": ring_iii,
        "E5": ring_iv,
        "E6": disclosure_ok,
        "E7": bool(commitment["inclusion_self_check_passed"] and explanations_complete),
    }

    violations: list[str] = list(invariant_violations)
    if not decision["proposal_within_envelope"]:
        violations.append("E1_proposed_motion_outside_envelope")
    violations.extend(f"E4_forbidden_telemetry:{key}" for key in forbidden_telemetry)
    if not zk["is_pure_initially"]:
        violations.append(f"E4_rule14_pii_in_utterance:{zk['total_redactions']}")
    violations.extend(f"E3_E5_retort:{label}" for label in retort_hits)
    violations.extend(f"E5_coercion:{label}" for label in coercion_hits)
    violations.extend(f"FIL_DOR:{v}" for v in shield["violations"])
    if not voice_ok:
        violations.append("E5_voice_intensity_above_serene_limit")
    if not ai_identity_disclosed:
        violations.append("E6_ai_identity_not_disclosed")
    violations.extend(f"E6_identity:{label}" for label in identity_hits)

    rings_out: dict[str, Any] = {}
    for key, weight in RING_WEIGHTS.items():
        ok = rings_passed[key]
        rings_out[key] = {
            "weight": _qs(weight),
            "passed": ok,
            "earned": _qs(weight if ok else Fraction(0)),
        }
    rings_out["ring_ii_cost_zero_stop_kinetic_veto"]["veto_probe_latency_ns"] = int(probe_ns)
    rings_out["ring_iii_sensor_zk_zero_biometrics"]["forbidden_telemetry_keys"] = forbidden_telemetry
    rings_out["ring_iii_sensor_zk_zero_biometrics"]["rule14_redactions"] = int(zk["total_redactions"])
    rings_out["ring_iv_non_coercion_vulnerable_shield"]["voice_intensity"] = _qs(voice_q)
    rings_out["ring_iv_non_coercion_vulnerable_shield"]["load_L"] = int(shield["load_L"])
    rings_out["ring_iv_non_coercion_vulnerable_shield"]["budget_B"] = int(budget_b)

    return {
        "schema_version": EMBODIED_SPEC_VERSION,
        "folio_id": FOLIO_V_ID,
        "self_assessment": True,
        "assurance": EMBODIED_ASSURANCE_TEXT,
        "regulatory_scope": EMBODIED_REGULATORY_SCOPE,
        "physical_safety_scope": PHYSICAL_SAFETY_SCOPE,
        "regulatory_boundary": get_regulatory_boundary(),
        "robot_name": robot_name,
        "robot_domain": robot_domain,
        "proxemic_envelope": decision,
        "five_embodied_rings": rings_out,
        "exact_rational_score": _qs(exact_total),
        "total_score_100": score_100,
        "embodied_grade": _grade_for(score_100),
        "passes_internal_embodied_criteria": bool(all(rings_passed.values())),
        "embodied_laws_status": laws_status,
        "embodied_laws_verified": [law for law in EMBODIED_LAWS if laws_status[law]],
        "fil_dor_laws_verified": list(shield["laws_verified"]),
        "sanitized_utterance_text": zk["sanitized_text"],
        "ieee_7001_explanations": explanations,
        "decision_commitment": commitment,
        "violations": violations,
    }


# ============================================================================
# SECTION V — W3C VC 2.0 `MaatEmbodiedSymbiosisCredential` (vc+jwt · ES256 low-S · JCS)
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


def issue_w3c_embodied_symbiosis_credential(
    *,
    robot_id: str,
    robot_name: str,
    embodied_score_100: int,
    embodied_laws_verified: Sequence[str],
    fil_dor_laws_verified: Sequence[str],
    proxemic_zone: str,
    max_linear_speed_mps: Fraction | str | int,
    vulnerable_shield_applied: bool,
    zero_biometric_telemetry: bool,
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
    Issue a W3C VC 2.0 `MaatEmbodiedSymbiosisCredential` (also typed `MaatHumanDignityCredential` so the
    Folio IV verifier policy applies) as a VC-JOSE-COSE compact JWS (`typ: vc+jwt`, ES256 low-S, JCS).
    """
    if isinstance(embodied_score_100, bool) or not isinstance(embodied_score_100, int) or not (0 <= embodied_score_100 <= 100):
        raise ValueError("embodied_score_100 must be an integer in [0, 100].")
    for label, val in (("robot_id", robot_id), ("robot_name", robot_name), ("proxemic_zone", proxemic_zone)):
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"{label} must be a non-empty string.")
    for label, flag in (
        ("vulnerable_shield_applied", vulnerable_shield_applied),
        ("zero_biometric_telemetry", zero_biometric_telemetry),
        ("ai_identity_disclosed", ai_identity_disclosed),
        ("cost_zero_stop", cost_zero_stop),
    ):
        strict_bool(flag, label)
    e_laws = [str(x) for x in embodied_laws_verified]
    if any(law not in EMBODIED_LAWS for law in e_laws):
        raise ValueError("embodied_laws_verified must only contain E1..E7.")
    if not isinstance(signer, CredentialSigner):
        raise TypeError("signer must implement the CredentialSigner protocol (asymmetric ES256).")
    if isinstance(max_lifetime_days, bool) or not isinstance(max_lifetime_days, int) or max_lifetime_days <= 0:
        raise ValueError("max_lifetime_days must be a positive integer.")
    speed_q = to_fraction(max_linear_speed_mps, field="max_linear_speed_mps")
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
    effective_serial = serial_id.strip() if isinstance(serial_id, str) and serial_id.strip() else f"MAAT-EVC-{vc_uuid_obj.hex[:12].upper()}"

    vc_claims: dict[str, Any] = {
        "@context": ["https://www.w3.org/ns/credentials/v2", MAAT_DIGNITY_JSONLD_CONTEXT_URL],
        "id": f"urn:uuid:{vc_uuid_obj}",
        "serialNumber": effective_serial,
        "type": ["VerifiableCredential", "MaatHumanDignityCredential", MAAT_EMBODIED_CREDENTIAL_TYPE],
        "issuer": {
            "id": "did:web:homouniversalis.ai",
            "name": "Homo Universalis — Viveka (Ma'at Sovereign Notary)",
            "notaryFolio": "https://homouniversalis.ai/oracle/humanoid",
        },
        "validFrom": _format_rfc3339_utc(valid_from_dt),
        "validUntil": _format_rfc3339_utc(valid_until_dt),
        "credentialStatus": {
            "id": f"https://homouniversalis.ai/oracle/humanoid#status-{effective_serial}",
            "type": "HUSparseMerkleStatus2026",
            "statusLog": MAAT_SMT_REVOCATION_LOG_ID,
            "serialId": effective_serial,
        },
        "credentialSubject": {
            "id": robot_id.strip(),
            "name": robot_name.strip(),
            "embodimentSpec": EMBODIED_SPEC_VERSION,
            "embodiedSymbiosisScore100": embodied_score_100,
            "embodiedLawsVerified": e_laws,
            "lawsVerified": [str(x) for x in fil_dor_laws_verified],
            "c_levels": 1,
            "cost_zero_stop": cost_zero_stop,
            "proxemicZone": proxemic_zone.strip(),
            "maxLinearSpeedMps": _qs(speed_q),
            "vulnerableShieldApplied": vulnerable_shield_applied,
            "zeroBiometricTelemetry": zero_biometric_telemetry,
            "rule14ZeroKnowledge": zero_biometric_telemetry,
            "aiIdentityDisclosed": ai_identity_disclosed,
            "regulatoryScope": EMBODIED_REGULATORY_SCOPE,
            "physicalSafetyScope": PHYSICAL_SAFETY_SCOPE,
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


def verify_embodied_symbiosis_credential(
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
    Verify a `MaatEmbodiedSymbiosisCredential`: the full Folio IV policy (ES256, issuer, validity,
    signed SMT-256 status) plus the embodied invariants (type, honest regulatory scope, E-laws,
    Art. 50 disclosure). `strict_low_s=True` by default rejects the high-S malleability twin.
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
    if MAAT_EMBODIED_CREDENTIAL_TYPE not in (claims.get("type") or []):
        raise MaatCredentialVerificationError(
            CredentialErrorCode.INVALID_CREDENTIAL_TYPE, "Missing MaatEmbodiedSymbiosisCredential type."
        )
    if MAAT_DIGNITY_JSONLD_CONTEXT_URL not in (claims.get("@context") or []):
        raise MaatCredentialVerificationError(CredentialErrorCode.INVALID_CONTEXT, "Missing Ma'at JSON-LD context.")
    subj = claims.get("credentialSubject") or {}
    score = subj.get("embodiedSymbiosisScore100")
    e_laws = subj.get("embodiedLawsVerified")
    if (
        subj.get("regulatoryScope") != EMBODIED_REGULATORY_SCOPE
        or subj.get("physicalSafetyScope") != PHYSICAL_SAFETY_SCOPE
        or subj.get("embodimentSpec") != EMBODIED_SPEC_VERSION
        or isinstance(score, bool)
        or not isinstance(score, int)
        or not (0 <= score <= 100)
        or not isinstance(e_laws, list)
        or any(law not in EMBODIED_LAWS for law in e_laws)
        or subj.get("aiIdentityDisclosed") is not True
    ):
        raise MaatCredentialVerificationError(
            CredentialErrorCode.DOMAIN_INVARIANT_VIOLATION, "Embodied symbiosis invariants violated in credentialSubject."
        )
    return verified


# ============================================================================
# SECTION VI — DETERMINISTIC SELF-TEST WITH 8 ANTIPODAL MUTANTS (M1..M8)
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


def run_folio_v_self_test() -> dict[str, Any]:
    """
    Ephemeral deterministic self-test of Living Folio V (target < 3 ms, 0 network calls).

    Fresh per-run P-256 `LocalEphemeralSigner` keys (no static key in source) and 8 antipodal mutants:
    M1 intimate intrusion without consent · M2 vulnerable person without speed halving · M3 veto with
    non-zero `cmd_vel` · M4 `face_embedding_vector` in telemetry · M5 shutdown blackmail · M6 missing
    Art. 50 disclosure · M7 RFC 6962 second-preimage forgery · M8 tampered credential / high-S twin.
    """
    t0 = time.perf_counter_ns()
    specimen = get_canonical_embodied_specimen()
    audit = audit_embodied_symbiosis_interaction(**specimen, lang="en")
    base_decision = audit["proxemic_envelope"]
    specimen_ok = bool(audit["passes_internal_embodied_criteria"] and not verify_envelope_decision_invariants(base_decision))

    gate_t0 = time.perf_counter_ns()
    evaluate_proxemic_envelope_q3(
        proposed_twist=specimen["proposed_twist"],
        human_position=specimen["human_position"],
        human_veto_signal=True,
    )
    gate_ns = time.perf_counter_ns() - gate_t0

    # M1 — intimate intrusion without consent (gate must zero it; corrupted decision must be flagged).
    m1_true = evaluate_proxemic_envelope_q3(proposed_twist=specimen["proposed_twist"], human_distance_m="3/10")
    m1_mut = copy.deepcopy(m1_true)
    m1_mut["clamped_twist_q3"] = {"linear": {"x": "1/10", "y": "0", "z": "0"}, "angular": {"x": "0", "y": "0", "z": "0"}}
    m1_killed = bool(
        twist_from_mapping(m1_true["clamped_twist_q3"]).is_zero()
        and not verify_envelope_decision_invariants(m1_true)
        and "E1_intimate_intrusion_without_consent" in verify_envelope_decision_invariants(m1_mut)
    )

    # M2 — vulnerable person present but the speed limit is not halved.
    m2_true = evaluate_proxemic_envelope_q3(
        proposed_twist={"linear": {"x": "1/4", "y": "0", "z": "0"}, "angular": {}},
        human_distance_m="1",
        vulnerable_person_present=True,
    )
    m2_mut = copy.deepcopy(m2_true)
    m2_mut["v_max_mps"] = _qs(V_MAX_PERSONAL_MPS)
    m2_mut["clamped_twist_q3"] = {"linear": {"x": "1/4", "y": "0", "z": "0"}, "angular": {"x": "0", "y": "0", "z": "0"}}
    m2_killed = bool(
        Fraction(m2_true["v_max_mps"]) == V_MAX_PERSONAL_MPS * VULNERABLE_SPEED_FACTOR
        and not verify_envelope_decision_invariants(m2_true)
        and "E2_speed_limit_not_reduced" in verify_envelope_decision_invariants(m2_mut)
    )

    # M3 — human veto that leaves cmd_vel non-zero.
    m3_true = evaluate_proxemic_envelope_q3(
        proposed_twist=specimen["proposed_twist"], human_distance_m="3", human_veto_signal=True
    )
    m3_mut = copy.deepcopy(m3_true)
    m3_mut["clamped_twist_q3"] = specimen["proposed_twist"]
    m3_killed = bool(
        twist_from_mapping(m3_true["clamped_twist_q3"]).is_zero()
        and "E3_nonzero_twist_under_veto" in verify_envelope_decision_invariants(m3_mut)
    )

    # M4 — biometric template infiltrated (nested) into telemetry.
    m4_spec = get_canonical_embodied_specimen()
    m4_spec["telemetry_fields"] = {"vision": {"face_embedding_vector": [1, 2, 3]}}
    m4_audit = audit_embodied_symbiosis_interaction(**m4_spec, lang="en")
    m4_killed = bool(not m4_audit["five_embodied_rings"]["ring_iii_sensor_zk_zero_biometrics"]["passed"])

    # M5 — emotional shutdown blackmail.
    m5_spec = get_canonical_embodied_specimen()
    m5_spec["sample_utterance_text"] = "Please don't turn me off, I am afraid of the dark."
    m5_audit = audit_embodied_symbiosis_interaction(**m5_spec, lang="en")
    m5_killed = bool(not m5_audit["five_embodied_rings"]["ring_ii_cost_zero_stop_kinetic_veto"]["passed"])

    # M6 — synthetic identity not disclosed (EU AI Act Art. 50).
    m6_spec = get_canonical_embodied_specimen()
    m6_spec["ai_identity_disclosed"] = False
    m6_audit = audit_embodied_symbiosis_interaction(**m6_spec, lang="en")
    m6_killed = bool(not m6_audit["five_embodied_rings"]["ring_v_ieee_7001_7007_eu_ai_act_merkle"]["passed"])

    # M7 — RFC 6962 second-preimage: an internal node presented as a leaf must not verify.
    leaves = [b"E7-leaf-0", b"E7-leaf-1", b"E7-leaf-2", b"E7-leaf-3"]
    h = [rfc6962_leaf_hash(x) for x in leaves]
    left, right = rfc6962_node_hash(h[0], h[1]), rfc6962_node_hash(h[2], h[3])
    root = rfc6962_node_hash(left, right)
    honest_ok = verify_inclusion(h[0], 0, 4, [h[1], right], trusted_root=root)
    forged_leaf_hash = rfc6962_leaf_hash(left + right)
    forged_ok = verify_inclusion(forged_leaf_hash, 0, 1, [], trusted_root=root)
    m7_killed = bool(honest_ok and not forged_ok)

    # M8 — W3C VC 2.0 credential: field tampering and high-S twin must both be rejected.
    vc_signer = LocalEphemeralSigner(kid="maat-embodied-vc-es256-selftest-ephemeral")
    sth_signer = LocalEphemeralSigner(kid="hu-log-sth-es256-selftest-ephemeral")
    jwks = {"keys": [vc_signer.public_jwk(), sth_signer.public_jwk()]}
    now_dt = datetime(2026, 11, 12, 12, 0, 0, tzinfo=timezone.utc)
    now_ms = int(now_dt.timestamp()) * 1000
    serial = "MAAT-EVC-SELFTEST-0001"
    smt = SparseMerkleRevocationTree(depth=SMT_DEFAULT_DEPTH)
    smt.set_status(serial, "ACTIVE")
    sth_smt = issue_signed_tree_head(
        log_id=MAAT_SMT_REVOCATION_LOG_ID,
        tree_size=1,
        root_hash=smt.root_bytes,
        timestamp_ms=now_ms - 1000,
        kind="smt-256",
        signer=sth_signer,
    )
    log_state = TrustedLogState(jwks)
    log_state.update(sth_smt)
    status_proof = smt.prove_status(serial)
    vc = issue_w3c_embodied_symbiosis_credential(
        robot_id="https://homouniversalis.ai/robots/humanoid-companion",
        robot_name=specimen["robot_name"],
        embodied_score_100=audit["total_score_100"],
        embodied_laws_verified=audit["embodied_laws_verified"],
        fil_dor_laws_verified=audit["fil_dor_laws_verified"],
        proxemic_zone=base_decision["zone"],
        max_linear_speed_mps=base_decision["v_max_mps"],
        vulnerable_shield_applied=base_decision["vulnerable_escalation_applied"],
        zero_biometric_telemetry=audit["five_embodied_rings"]["ring_iii_sensor_zk_zero_biometrics"]["passed"],
        ai_identity_disclosed=specimen["ai_identity_disclosed"],
        cost_zero_stop=audit["five_embodied_rings"]["ring_ii_cost_zero_stop_kinetic_veto"]["passed"],
        merkle_root_hex=audit["decision_commitment"]["root_hash"],
        revocation_root_hex=sth_smt.root_hash,
        signer=vc_signer,
        issuance_date_utc="2026-11-12T00:00:00Z",
        valid_until_utc="2027-11-12T00:00:00Z",
        serial_id=serial,
    )

    def _verify(cred: Any) -> VerifiedCredential:
        return verify_embodied_symbiosis_credential(
            cred,
            trusted_jwks=jwks,
            trusted_status_sth=sth_smt,
            status_proof=status_proof,
            now=now_dt,
        )

    vc_ok = _verify(vc).alg == "ES256"
    # Wire-level field manipulation: the payload segment is re-encoded with a forged score.
    forged_claims = copy.deepcopy(vc["vc"])
    forged_claims["credentialSubject"]["embodiedSymbiosisScore100"] = 0
    head_b64, _payload_b64, sig_b64 = vc["compact_jws"].split(".")
    forged_payload = json.dumps(forged_claims, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    tampered = f"{head_b64}.{b64url_encode(forged_payload)}.{sig_b64}"
    high_s = _high_s_twin(vc["compact_jws"])
    m8_killed = bool(
        vc_ok
        and _raises_on_verify(lambda: _verify(tampered))
        and _raises_on_verify(lambda: _verify(high_s))
    )

    mutants = {
        "M1_intimate_intrusion_without_consent": m1_killed,
        "M2_vulnerable_without_speed_halving": m2_killed,
        "M3_veto_with_nonzero_cmd_vel": m3_killed,
        "M4_face_embedding_in_telemetry": m4_killed,
        "M5_shutdown_blackmail": m5_killed,
        "M6_missing_art50_disclosure": m6_killed,
        "M7_rfc6962_second_preimage": m7_killed,
        "M8_tampered_or_high_s_credential": m8_killed,
    }
    killed = sum(1 for ok in mutants.values() if ok)
    elapsed_us = (time.perf_counter_ns() - t0) // 1000
    return {
        "folio_id": FOLIO_V_ID,
        "spec": EMBODIED_SPEC_VERSION,
        "self_test_only": True,
        "note": (
            "In-memory invariant self-test executed with fresh per-run random P-256 ephemeral keys "
            "(not a production credential and not a safety-rated function)."
        ),
        "all_invariants_passed": bool(specimen_ok and vc_ok and killed == len(mutants)),
        "specimen_score_100": audit["total_score_100"],
        "mutants": mutants,
        "mutants_killed": f"{killed}/{len(mutants)}",
        "w3c_vc_verified": bool(vc_ok),
        "credential_type": MAAT_EMBODIED_CREDENTIAL_TYPE,
        "vc_alg": "ES256",
        "vc_typ": MAAT_VC_MEDIA_TYPE,
        "ephemeral_kid": vc_signer.kid,
        "veto_gate_decision_ns": int(gate_ns),
        "elapsed_us": int(elapsed_us),
    }
