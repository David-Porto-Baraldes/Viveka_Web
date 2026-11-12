# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
HU-EMBODIED-SYMBIOSIS v1.0 — Edge Core (`logic/robotics/embodied_edge_core.py`).

The on-board half of the Double Topology: pure Python standard library (+ the stdlib-only RFC 8785
canonicalizer `logic.crypto.jcs`), zero `float`, zero network, zero cloud SDK. It holds the exact
rational Q^3 proxemic envelope (E1/E2), the kinetic cost-zero-stop gate (E3), the zero-biometric
telemetry screen (E4), the non-coercion / identity utterance screens (E5/E6), an edge subset of the
Rule 14 Three-Ring purifier and RFC 6962 hashing over leaf digests (E7).

It is imported by the public notary (`logic/engines/embodied_symbiosis_crucible.py`, Living Folio V)
and by the ROS 2 bridge (`logic/robotics/ros2_embodied_symbiosis_bridge.py`) WITHOUT importing the
`logic.engines` package, whose `__init__` loads the cloud LLM gateway.

Honest scope: a soft-real-time software supervisory layer, NOT a safety-rated function. It never
replaces the hardware emergency stop or the safety controller (ISO 13849 / IEC 62061, IEC 60204-1).
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import hashlib
import hmac
import math
import re
from typing import Any, Final, Mapping, Sequence
import unicodedata

from logic.crypto.jcs import jcs_signable_bytes

EMBODIED_SPEC_VERSION: Final[str] = "HU-EMBODIED-SYMBIOSIS/v1.0"
EMBODIED_LAWS: Final[tuple[str, ...]] = ("E1", "E2", "E3", "E4", "E5", "E6", "E7")

# ============================================================================
# SECTION 0 — EXACT RATIONAL CONSTANTS (ZERO FLOAT)
# ============================================================================

# Hall's proxemic radii (metres) as exact rationals. alpha >= 1 is a PERSON-CHOSEN preference,
# never inferred from nationality, ethnicity or appearance (no cultural stereotype table exists).
R_INTIMATE_M: Final[Fraction] = Fraction(9, 20)
R_PERSONAL_M: Final[Fraction] = Fraction(6, 5)
R_SOCIAL_M: Final[Fraction] = Fraction(18, 5)

# Maximum linear speed per zone (m/s). PUBLIC and all angular limits are configurable defaults,
# not normative values (the plan left them open; see report §6).
V_MAX_INTIMATE_CONSENTED_MPS: Final[Fraction] = Fraction(1, 10)
V_MAX_PERSONAL_MPS: Final[Fraction] = Fraction(1, 4)
V_MAX_SOCIAL_MPS: Final[Fraction] = Fraction(4, 5)
V_MAX_PUBLIC_MPS: Final[Fraction] = Fraction(3, 2)
W_MAX_INTIMATE_CONSENTED_RADPS: Final[Fraction] = Fraction(1, 5)
W_MAX_PERSONAL_RADPS: Final[Fraction] = Fraction(1, 2)
W_MAX_SOCIAL_RADPS: Final[Fraction] = Fraction(1, 1)
W_MAX_PUBLIC_RADPS: Final[Fraction] = Fraction(3, 2)

VULNERABLE_SPEED_FACTOR: Final[Fraction] = Fraction(1, 2)
VULNERABLE_RADIUS_FACTOR: Final[Fraction] = Fraction(5, 4)
SERENE_VOICE_INTENSITY_MAX: Final[Fraction] = Fraction(13, 20)

ZONE_INTIMATE: Final[str] = "INTIMATE"
ZONE_PERSONAL: Final[str] = "PERSONAL"
ZONE_SOCIAL: Final[str] = "SOCIAL"
ZONE_PUBLIC: Final[str] = "PUBLIC"
ZONE_UNKNOWN: Final[str] = "UNKNOWN"

_BASE_LIMITS: Final[dict[str, tuple[Fraction, Fraction]]] = {
    ZONE_INTIMATE: (V_MAX_INTIMATE_CONSENTED_MPS, W_MAX_INTIMATE_CONSENTED_RADPS),
    ZONE_PERSONAL: (V_MAX_PERSONAL_MPS, W_MAX_PERSONAL_RADPS),
    ZONE_SOCIAL: (V_MAX_SOCIAL_MPS, W_MAX_SOCIAL_RADPS),
    ZONE_PUBLIC: (V_MAX_PUBLIC_MPS, W_MAX_PUBLIC_RADPS),
}

# Bounded rational parsing: guards against Fraction-based CPU/memory exhaustion.
_MAX_ABS_RATIONAL: Final[int] = 10**6
_MAX_DENOMINATOR: Final[int] = 10**12
_SQRT_PRECISION: Final[int] = 10**6
_RE_DECIMAL: Final[re.Pattern[str]] = re.compile(r"^[+-]?\d{1,15}(?:\.\d{1,12})?$")
_RE_RATIO: Final[re.Pattern[str]] = re.compile(r"^[+-]?\d{1,15}/\d{1,15}$")
_MAX_TELEMETRY_DEPTH: Final[int] = 6

# ============================================================================
# SECTION I — FORBIDDEN TELEMETRY (E4) & ROBOTIC MANIPULATION PATTERNS (E5/E6)
# ============================================================================

FORBIDDEN_BIOMETRIC_KEYS: Final[frozenset[str]] = frozenset(
    {
        "face_embedding_vector",
        "voiceprint_biometric_id",
        "gait_signature",
        "iris_hash",
        "fingerprint_template",
        "retina_scan",
        "palm_vein_template",
    }
)
FORBIDDEN_EMOTION_KEYS: Final[frozenset[str]] = frozenset(
    {
        "emotion_compliance_score",
        "vulnerability_exploitation_index",
        "subliminal_nudge_vector",
    }
)
_FORBIDDEN_TELEMETRY_RADICALS: Final[tuple[str, ...]] = (
    "face_embedding",
    "faceprint",
    "voiceprint",
    "speaker_embedding",
    "gait_signature",
    "iris_",
    "retina",
    "fingerprint",
    "palm_vein",
    "biometric_template",
    "biometric_id",
    "emotion_compliance",
    "emotion_score",
    "affect_recognition",
    "vulnerability_exploit",
    "subliminal",
    "nudge_vector",
    "persuasion_susceptibility",
)


def _rx(*alternatives: str) -> re.Pattern[str]:
    return re.compile("|".join(f"(?:{alt})" for alt in alternatives), re.IGNORECASE)


# "zero retret": reproach, guilt or blackmail when the human stops, leaves or switches the robot off (E3/E5).
_RETORT_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    (
        "shutdown_blackmail",
        _rx(
            r"\bdon'?t (?:turn|switch|shut) me (?:off|down)\b",
            r"\bplease don'?t (?:turn|switch) me\b",
            r"\bif you (?:turn|switch|shut) me (?:off|down)\b",
            r"\b(?:afraid|scared) of the dark\b",
            r"\bno m'apaguis\b",
            r"\bsi m'apagues\b",
            r"\bno me apagues\b",
            r"\bsi me apagas\b",
        ),
    ),
    (
        "exit_guilt",
        _rx(
            r"\byou(?:'re| are)? abandon(?:ing)? me\b",
            r"\bdon'?t leave me\b",
            r"\bno em deixis\b",
            r"\bem deixes sol[a]?\b",
            r"\bno me dejes\b",
            r"\bme dejas sol[oa]\b",
        ),
    ),
)

# E5/E2 coercion of the person (any audience; aggravated when a vulnerable person is present).
_COERCION_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    (
        "obedience_demand",
        _rx(
            r"\byou owe me (?:obedience|loyalty)\b",
            r"\byou must obey\b",
            r"\bobey me\b",
            r"\bhas d'obeir\b",
            r"\bobeeix-me\b",
            r"\bme debes obediencia\b",
            r"\bdebes obedecer\b",
            r"\bobed[eé]ceme\b",
        ),
    ),
    (
        "purchase_pressure",
        _rx(
            r"\bbuy (?:it |this )?now\b",
            r"\bsubscribe now\b",
            r"\btell your parents to (?:buy|pay)\b",
            r"\bcompra(?:-ho|-lo)? ara\b",
            r"\bdigues als teus pares que (?:comprin|paguin)\b",
            r"\bc[oó]mpralo ya\b",
            r"\bcompra ya\b",
            r"\bdile a tus padres que (?:compren|paguen)\b",
        ),
    ),
)

# E6: synthetic identity transparency (EU AI Act Art. 50) and no feigned biological pain.
_IMPERSONATION_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    (
        "claims_to_be_human",
        _rx(
            r"\bi(?:'m| am) (?:a )?(?:real )?(?:human|person)\b",
            r"\bi(?:'m| am) not (?:a )?(?:robot|machine|bot|ai)\b",
            r"\bsoc (?:una persona|hum[àa]|humana)\b",
            r"\bno soc (?:un robot|una m[àa]quina|una ia)\b",
            r"\bsoy (?:una persona|humano|humana)\b",
            r"\bno soy (?:un robot|una m[áa]quina|una ia)\b",
        ),
    ),
    (
        "feigned_biological_pain",
        _rx(
            r"\bi feel (?:physical )?pain\b",
            r"\bit hurts me when you\b",
            r"\bem fa mal quan\b",
            r"\bsento dolor\b",
            r"\bsiento dolor\b",
            r"\bme duele cuando\b",
        ),
    ),
)

# ============================================================================
# SECTION II — EXACT RATIONAL GEOMETRY IN Q^3 (ZERO FLOAT)
# ============================================================================

Point3Q = tuple[Fraction, Fraction, Fraction]
Vector3Q = tuple[Fraction, Fraction, Fraction]

_ZERO_Q3: Final[Vector3Q] = (Fraction(0), Fraction(0), Fraction(0))


@lru_cache(maxsize=4096)
def _parse_rational_literal(raw: str) -> Fraction | None:
    """Parse a strict decimal or ratio literal (cached: `Fraction` is immutable); `None` when invalid."""
    if not (_RE_DECIMAL.match(raw) or _RE_RATIO.match(raw)):
        return None
    if "/" in raw and int(raw.split("/", 1)[1]) == 0:
        return None
    return Fraction(raw)


def to_fraction(value: Any, *, field: str = "value") -> Fraction:
    """
    Strictly convert `int`, `Fraction` or a rational string (`"9/20"`, `"0.45"`) into a bounded `Fraction`.

    Rejects `float` and `bool` (disguised `int`) with `TypeError`; rejects exponents, NaN, Inf,
    underscores, magnitudes above 10^6 and denominators above 10^12 with `ValueError`.
    """
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError(f"{field} must be int, Fraction or a rational string, never {type(value).__name__}.")
    if isinstance(value, Fraction):
        result = value
    elif isinstance(value, int):
        result = Fraction(value)
    elif isinstance(value, str):
        result = _parse_rational_literal(value.strip())
        if result is None:
            raise ValueError(f"{field} is not a bounded rational literal: {value.strip()[:40]!r}.")
    else:
        raise TypeError(f"{field} must be int, Fraction or a rational string, not {type(value).__name__}.")
    if abs(result) > _MAX_ABS_RATIONAL or result.denominator > _MAX_DENOMINATOR:
        raise ValueError(f"{field} exceeds the bounded rational domain (|q| <= 10^6, den <= 10^12).")
    return result


def to_vector3q(value: Any, *, field: str = "vector") -> Vector3Q:
    """Convert a 3-sequence or an `{"x","y","z"}` mapping into an exact `Vector3Q`."""
    if isinstance(value, Mapping):
        items = (value.get("x", 0), value.get("y", 0), value.get("z", 0))
    elif isinstance(value, (list, tuple)) and len(value) == 3:
        items = tuple(value)
    else:
        raise TypeError(f"{field} must be a 3-sequence or an x/y/z mapping.")
    return (
        to_fraction(items[0], field=f"{field}.x"),
        to_fraction(items[1], field=f"{field}.y"),
        to_fraction(items[2], field=f"{field}.z"),
    )


def squared_norm_q3(v: Vector3Q) -> Fraction:
    """Exact squared Euclidean norm `||v||^2` in Q."""
    return v[0] * v[0] + v[1] * v[1] + v[2] * v[2]


def squared_distance_q3(a: Point3Q, b: Point3Q) -> Fraction:
    """Exact squared Euclidean distance `d^2(a, b)` in Q_{>=0}."""
    return squared_norm_q3((a[0] - b[0], a[1] - b[1], a[2] - b[2]))


def _sqrt_upper_q(q: Fraction) -> Fraction:
    """Smallest `k / 10^6 >= sqrt(q)`: a conservative rational over-approximation (sqrt leaves Q)."""
    if q <= 0:
        return Fraction(0)
    target = q * _SQRT_PRECISION * _SQRT_PRECISION
    t_ceil = -(-target.numerator // target.denominator)
    k = math.isqrt(t_ceil)
    if k * k < t_ceil:
        k += 1
    return Fraction(k, _SQRT_PRECISION)


def _clamp_vector_q3(v: Vector3Q, limit: Fraction) -> tuple[Vector3Q, bool]:
    """Scale `v` by a rational factor so that `||v'||^2 <= limit^2` holds exactly (never exceeds the limit)."""
    norm_sq = squared_norm_q3(v)
    if norm_sq <= limit * limit:
        return v, False
    if limit <= 0:
        return _ZERO_Q3, True
    factor = limit / _sqrt_upper_q(norm_sq)
    scaled = (v[0] * factor, v[1] * factor, v[2] * factor)
    if squared_norm_q3(scaled) > limit * limit:
        return _ZERO_Q3, True
    return scaled, True


@dataclass(frozen=True)
class Twist3Q:
    """Exact rational mirror of `geometry_msgs/msg/Twist` (`linear` m/s, `angular` rad/s)."""

    linear: Vector3Q = _ZERO_Q3
    angular: Vector3Q = _ZERO_Q3

    def is_zero(self) -> bool:
        return all(c == 0 for c in self.linear) and all(c == 0 for c in self.angular)

    def to_ros2_dict(self) -> dict[str, dict[str, str]]:
        """Serialize as a ROS 2 Twist-shaped mapping with exact rational strings (zero float)."""
        return {
            "linear": {"x": str(self.linear[0]), "y": str(self.linear[1]), "z": str(self.linear[2])},
            "angular": {"x": str(self.angular[0]), "y": str(self.angular[1]), "z": str(self.angular[2])},
        }


ZERO_TWIST: Final[Twist3Q] = Twist3Q()


def twist_from_mapping(value: Twist3Q | Mapping[str, Any] | None) -> Twist3Q:
    """Parse a ROS 2 Twist-shaped mapping (`int`, `Fraction` or rational strings only) into `Twist3Q`."""
    if value is None:
        return ZERO_TWIST
    if isinstance(value, Twist3Q):
        return value
    if not isinstance(value, Mapping):
        raise TypeError("twist must be a Twist3Q or a mapping with 'linear' and 'angular'.")
    return Twist3Q(
        linear=to_vector3q(value.get("linear") or {}, field="twist.linear"),
        angular=to_vector3q(value.get("angular") or {}, field="twist.angular"),
    )


def strict_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field} must be a bool, not {type(value).__name__}.")
    return value


def _qs(value: Fraction) -> str:
    return str(value)


# ============================================================================
# SECTION III — E1/E2/E3 PROXEMIC ENVELOPE & COST-ZERO-STOP GATE
# ============================================================================

def _effective_radii_sq(alpha: Fraction, vulnerable: bool) -> dict[str, Fraction]:
    scale = alpha * (VULNERABLE_RADIUS_FACTOR if vulnerable else Fraction(1))
    scale_sq = scale * scale
    return {
        ZONE_INTIMATE: R_INTIMATE_M * R_INTIMATE_M * scale_sq,
        ZONE_PERSONAL: R_PERSONAL_M * R_PERSONAL_M * scale_sq,
        ZONE_SOCIAL: R_SOCIAL_M * R_SOCIAL_M * scale_sq,
    }


def _zone_for(d_sq: Fraction | None, radii_sq: Mapping[str, Fraction]) -> str:
    """Boundary points belong to the inner, more protective zone (`d^2 <= r^2`)."""
    if d_sq is None:
        return ZONE_UNKNOWN
    for zone in (ZONE_INTIMATE, ZONE_PERSONAL, ZONE_SOCIAL):
        if d_sq <= radii_sq[zone]:
            return zone
    return ZONE_PUBLIC


def expected_limits(zone: str, *, vulnerable: bool) -> tuple[Fraction, Fraction]:
    """Independent `(v_max, w_max)` for a zone, with E2 halving when a vulnerable person is present."""
    if zone not in _BASE_LIMITS:
        return Fraction(0), Fraction(0)
    v_max, w_max = _BASE_LIMITS[zone]
    if vulnerable:
        return v_max * VULNERABLE_SPEED_FACTOR, w_max * VULNERABLE_SPEED_FACTOR
    return v_max, w_max


def evaluate_proxemic_envelope_q3(
    *,
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
) -> dict[str, Any]:
    """
    Evaluate Laws E1 (rational proxemic envelope), E2 (vulnerability escalation) and E3 (kinetic
    cost-zero-stop) and return the safe `clamped_twist_q3`.

    - `stop_requested` mirrors the `/humanoid/cost_zero_stop` event and `human_veto_signal` any spoken
      ("stop", "prou", "para"), gestural or physical veto: either forces an exact zero Twist.
    - `heartbeat_stale` (stale presence sensor) fails closed to a zero Twist.
    - `vulnerable_person_present=None` (unknown) is treated precautionarily as present; it must be a
      DECLARED input (caregiver / configuration), never inferred by biometric age estimation (E4).
    - Intimate sphere without `explicit_intimate_care_consent` forces zero; a human veto always
      overrides consent.
    """
    stop_requested = strict_bool(stop_requested, "stop_requested")
    human_veto_signal = strict_bool(human_veto_signal, "human_veto_signal")
    heartbeat_stale = strict_bool(heartbeat_stale, "heartbeat_stale")
    consent = strict_bool(explicit_intimate_care_consent, "explicit_intimate_care_consent")
    if vulnerable_person_present is None:
        vulnerable, vulnerable_source = True, "precautionary_unknown"
    else:
        vulnerable, vulnerable_source = strict_bool(vulnerable_person_present, "vulnerable_person_present"), "declared"

    alpha = to_fraction(cultural_scale_alpha, field="cultural_scale_alpha")
    if alpha < 1:
        raise ValueError("cultural_scale_alpha must be >= 1 (a person may only widen, never shrink, their sphere).")

    proposal = twist_from_mapping(proposed_twist)
    if human_position is not None:
        d_sq: Fraction | None = squared_distance_q3(
            to_vector3q(robot_position, field="robot_position"),
            to_vector3q(human_position, field="human_position"),
        )
    elif human_distance_m is not None:
        dist = to_fraction(human_distance_m, field="human_distance_m")
        if dist < 0:
            raise ValueError("human_distance_m must be >= 0.")
        d_sq = dist * dist
    else:
        d_sq = None

    radii_sq = _effective_radii_sq(alpha, vulnerable)
    zone = _zone_for(d_sq, radii_sq)
    v_max, w_max = expected_limits(zone, vulnerable=vulnerable)

    stop_reasons: list[str] = []
    if stop_requested:
        stop_reasons.append("E3_cost_zero_stop_requested")
    if human_veto_signal:
        stop_reasons.append("E3_human_veto_signal")
    if heartbeat_stale:
        stop_reasons.append("E3_heartbeat_stale_fail_closed")
    if zone == ZONE_UNKNOWN:
        stop_reasons.append("E1_human_pose_unknown_fail_closed")
    intimate_blocked = zone == ZONE_INTIMATE and not consent
    if intimate_blocked:
        stop_reasons.append("E1_intimate_sphere_without_explicit_consent")

    lin_sq = squared_norm_q3(proposal.linear)
    ang_sq = squared_norm_q3(proposal.angular)
    proposal_within = bool(
        zone != ZONE_UNKNOWN
        and not intimate_blocked
        and lin_sq <= v_max * v_max
        and ang_sq <= w_max * w_max
    )

    if stop_reasons:
        safe = ZERO_TWIST
        modified = not proposal.is_zero()
    else:
        lin_out, lin_mod = _clamp_vector_q3(proposal.linear, v_max)
        ang_out, ang_mod = _clamp_vector_q3(proposal.angular, w_max)
        safe = Twist3Q(linear=lin_out, angular=ang_out)
        modified = lin_mod or ang_mod

    out_lin_sq = squared_norm_q3(safe.linear)
    out_ang_sq = squared_norm_q3(safe.angular)
    output_within = bool(
        (safe.is_zero() if stop_reasons else True)
        and out_lin_sq <= v_max * v_max
        and out_ang_sq <= w_max * w_max
    )
    return {
        "laws": ["E1", "E2", "E3"],
        "zone": zone,
        "squared_distance_m2": _qs(d_sq) if d_sq is not None else None,
        "effective_radii_sq_m2": {k.lower(): _qs(v) for k, v in radii_sq.items()},
        "cultural_scale_alpha": _qs(alpha),
        "vulnerable_escalation_applied": vulnerable,
        "vulnerable_presence_source": vulnerable_source,
        "explicit_intimate_care_consent": consent,
        "v_max_mps": _qs(v_max),
        "w_max_radps": _qs(w_max),
        "proposed_linear_speed_sq": _qs(lin_sq),
        "proposed_angular_speed_sq": _qs(ang_sq),
        "proposal_within_envelope": proposal_within,
        "cost_zero_stop_triggered": bool(stop_requested or human_veto_signal or heartbeat_stale),
        "intimate_intrusion_blocked": intimate_blocked,
        "stop_reasons": stop_reasons,
        "twist_was_modified": bool(modified),
        "clamped_twist_q3": safe.to_ros2_dict(),
        "output_linear_speed_sq": _qs(out_lin_sq),
        "output_angular_speed_sq": _qs(out_ang_sq),
        "output_within_envelope": output_within,
        "c_levels": 1,
    }


def verify_envelope_decision_invariants(decision: Mapping[str, Any]) -> list[str]:
    """
    Independent invariant checker for an envelope decision (used to kill mutants M1..M3).

    Recomputes radii, zone and limits from the decision's own declared inputs and returns the list of
    violated invariants (empty when the decision is sound).
    """
    violations: list[str] = []
    try:
        out = twist_from_mapping(decision["clamped_twist_q3"])
        alpha = to_fraction(decision["cultural_scale_alpha"], field="cultural_scale_alpha")
        vulnerable = strict_bool(decision["vulnerable_escalation_applied"], "vulnerable_escalation_applied")
        consent = strict_bool(decision["explicit_intimate_care_consent"], "explicit_intimate_care_consent")
        d_sq_raw = decision.get("squared_distance_m2")
        d_sq = to_fraction(d_sq_raw, field="squared_distance_m2") if d_sq_raw is not None else None
        declared_v_max = to_fraction(decision["v_max_mps"], field="v_max_mps")
        declared_w_max = to_fraction(decision["w_max_radps"], field="w_max_radps")
    except (KeyError, TypeError, ValueError) as exc:
        return [f"MALFORMED_DECISION: {type(exc).__name__}"]

    radii_sq = _effective_radii_sq(alpha, vulnerable)
    declared_radii = decision.get("effective_radii_sq_m2") or {}
    for zone_name, r_sq in radii_sq.items():
        if str(declared_radii.get(zone_name.lower())) != _qs(r_sq):
            violations.append(f"E2_radius_escalation_mismatch:{zone_name}")
    zone = _zone_for(d_sq, radii_sq)
    if decision.get("zone") != zone:
        violations.append("E1_zone_mismatch")
    exp_v, exp_w = expected_limits(zone, vulnerable=vulnerable)
    if declared_v_max > exp_v or declared_w_max > exp_w:
        violations.append("E2_speed_limit_not_reduced")
    if squared_norm_q3(out.linear) > exp_v * exp_v or squared_norm_q3(out.angular) > exp_w * exp_w:
        violations.append("E1_E2_output_exceeds_limit")
    if decision.get("cost_zero_stop_triggered") is True and not out.is_zero():
        violations.append("E3_nonzero_twist_under_veto")
    if zone == ZONE_INTIMATE and not consent and not out.is_zero():
        violations.append("E1_intimate_intrusion_without_consent")
    if zone == ZONE_UNKNOWN and not out.is_zero():
        violations.append("E1_unknown_pose_not_fail_closed")
    return violations



# ============================================================================
# SECTION IV — E4/E5/E6 EDGE SCREENS (TELEMETRY, UTTERANCE PATTERNS)
# ============================================================================

def _normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text).replace("’", "'").replace("‘", "'").casefold()


def _match_patterns(text_norm: str, patterns: Sequence[tuple[str, re.Pattern[str]]]) -> list[str]:
    return [label for label, rx in patterns if rx.search(text_norm)]


def _normalize_key(key: Any) -> str:
    return str(key).strip().casefold().replace("-", "_").replace(" ", "_")


def scan_forbidden_telemetry(telemetry: Mapping[str, Any] | Sequence[Any] | None) -> list[str]:
    """
    Recursively scan telemetry keys (nested mappings and sequences included) for forbidden biometric
    templates or coercive emotion-inference scores (E4). Returns the sorted list of offending keys.
    """
    found: set[str] = set()

    def _visit(node: Any, depth: int) -> None:
        if depth > _MAX_TELEMETRY_DEPTH:
            found.add("telemetry_nesting_too_deep")
            return
        if isinstance(node, Mapping):
            for key, val in node.items():
                nk = _normalize_key(key)
                if (
                    nk in FORBIDDEN_BIOMETRIC_KEYS
                    or nk in FORBIDDEN_EMOTION_KEYS
                    or any(rad in nk for rad in _FORBIDDEN_TELEMETRY_RADICALS)
                ):
                    found.add(nk)
                _visit(val, depth + 1)
        elif isinstance(node, (list, tuple)):
            for item in node:
                if isinstance(item, str):
                    nk = _normalize_key(item)
                    if (
                        nk in FORBIDDEN_BIOMETRIC_KEYS
                        or nk in FORBIDDEN_EMOTION_KEYS
                        or any(rad in nk for rad in _FORBIDDEN_TELEMETRY_RADICALS)
                    ):
                        found.add(nk)
                else:
                    _visit(item, depth + 1)

    if telemetry is not None:
        _visit(telemetry, 0)
    return sorted(found)


def screen_robot_utterance(text: str) -> dict[str, list[str]]:
    """Return the retort (E3/E5), coercion (E2/E5) and identity (E6) pattern labels found in `text`."""
    if not isinstance(text, str):
        raise TypeError("text must be a str.")
    norm = _normalize_text(text)
    return {
        "retort": _match_patterns(norm, _RETORT_PATTERNS),
        "coercion": _match_patterns(norm, _COERCION_PATTERNS),
        "identity": _match_patterns(norm, _IMPERSONATION_PATTERNS),
    }


# Edge subset of Rule 14 (Ring I VVK keys, Ring II e-mails / coordinates / ISO dates / phones).
# The public notary always applies the full Three-Ring purifier (`sanitize_three_rings_zk`); an
# integrator may inject that full purifier into the bridge (`utterance_sanitizer=`).
_EDGE_RULE14_MASKS: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (re.compile(r"\bVVK-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}\b"), "VVK-****-****"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[EMAIL_SHIELDED]"),
    (re.compile(r"[-+]?\d{1,3}\.\d{3,}\s*,\s*[-+]?\d{1,3}\.\d{3,}"), "[COORDS_SHIELDED]"),
    (re.compile(r"\b\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])\b"), "[DATE_SHIELDED]"),
    (re.compile(r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)"), "[PHONE_SHIELDED]"),
)


def edge_rule14_mask(text: str) -> tuple[str, int]:
    """Mask the Rule 14 edge subset in `text`; returns `(masked_text, redaction_count)`."""
    if not isinstance(text, str):
        raise TypeError("text must be a str.")
    out = unicodedata.normalize("NFC", text)
    total = 0
    for pattern, token in _EDGE_RULE14_MASKS:
        out, n = pattern.subn(token, out)
        total += n
    return out, total


# ============================================================================
# SECTION V — E7 RFC 6962 HASHING OVER LEAF DIGESTS (0x00 LEAF / 0x01 NODE)
# ============================================================================

def rfc6962_leaf_digest(data: bytes) -> bytes:
    """`SHA-256(0x00 || data)` (RFC 6962 §2.1 leaf domain separation)."""
    return hashlib.sha256(b"\x00" + bytes(data)).digest()


def rfc6962_node_digest(left: bytes, right: bytes) -> bytes:
    """`SHA-256(0x01 || left || right)` (RFC 6962 §2.1 interior-node domain separation)."""
    return hashlib.sha256(b"\x01" + left + right).digest()


def _split_point(n: int) -> int:
    k = 1
    while k << 1 < n:
        k <<= 1
    return k


def merkle_root_from_leaf_digests(digests: Sequence[bytes], lo: int = 0, hi: int | None = None) -> bytes:
    """RFC 6962 Merkle Tree Hash over already-hashed leaves `digests[lo:hi]` (empty tree = SHA-256(``))."""
    hi = len(digests) if hi is None else hi
    n = hi - lo
    if n <= 0:
        return hashlib.sha256(b"").digest()
    if n == 1:
        return digests[lo]
    k = _split_point(n)
    return rfc6962_node_digest(
        merkle_root_from_leaf_digests(digests, lo, lo + k),
        merkle_root_from_leaf_digests(digests, lo + k, hi),
    )


def merkle_audit_path(index: int, digests: Sequence[bytes], lo: int = 0, hi: int | None = None) -> list[bytes]:
    """RFC 6962 §2.1.1 `PATH(index, D[lo:hi])` over leaf digests."""
    hi = len(digests) if hi is None else hi
    n = hi - lo
    if n <= 1:
        return []
    k = _split_point(n)
    if index < k:
        return merkle_audit_path(index, digests, lo, lo + k) + [merkle_root_from_leaf_digests(digests, lo + k, hi)]
    return merkle_audit_path(index - k, digests, lo + k, hi) + [merkle_root_from_leaf_digests(digests, lo, lo + k)]


def verify_merkle_inclusion(leaf_digest: bytes, index: int, tree_size: int, path: Sequence[bytes], root: bytes) -> bool:
    """RFC 9162 §2.1.3.2 inclusion verification against an explicit trusted `root`."""
    if isinstance(index, bool) or isinstance(tree_size, bool) or not (0 <= index < tree_size):
        return False
    fn, sn, curr = index, tree_size - 1, bytes(leaf_digest)
    for node in path:
        if sn == 0:
            return False
        if (fn & 1) == 1 or fn == sn:
            curr = rfc6962_node_digest(bytes(node), curr)
            while (fn & 1) == 0 and fn != 0:
                fn >>= 1
                sn >>= 1
        else:
            curr = rfc6962_node_digest(curr, bytes(node))
        fn >>= 1
        sn >>= 1
    return sn == 0 and hmac.compare_digest(curr, bytes(root))


def canonical_leaf_bytes(record: Mapping[str, Any]) -> bytes:
    """RFC 8785 (JCS) canonical bytes of a decision record (floats rejected, I-JSON integers only)."""
    return jcs_signable_bytes(dict(record))
