# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
HU-UNIFIED-CONSCIOUSNESS v1.0 — Edge Core (`logic/consciousness/unified_consciousness_core.py`).

One Consciousness, Three Levels of Breath, one Word-Circle Arbiter:

  * Level 1 — Immediate Presence (< 250 ms design budget): warm listening, instant silence on barge-in,
    never an unverified empirical claim (U2, the Law of the Humble Crystal).
  * Level 2 — Verified Pantheon & Memory (~4-10 s design budget): deterministic truth delivered inside a
    `VerifiedKnowledgeEnvelope` (RFC 8785 JCS + SHA-256 digest).
  * Level 3 — Quiet Cathedral (20-90 s design budget, background): at most one meditation per soul, opened
    only inside the cognitive budget `L + dL3 <= B`, which raises its hand once and speaks only when invited.

This module is the on-board half of the Double Topology: Python standard library + `logic.crypto.jcs` +
`logic.robotics.embodied_edge_core` only. Zero `float`, zero network, zero cloud SDK, zero import of
`logic.engines` (whose `__init__` loads the cloud LLM gateway). The latency figures above are DESIGN
BUDGETS of the Phase 2 model pipeline; this module only measures its own arbitration decisions.

Honest scope: a soft-real-time software arbiter of who speaks and what is remembered. It is NOT a medical
or psychotherapeutic device, NOT a safety-rated function and makes NO claim of phenomenal consciousness or
sentience: "consciousness" here names one unified conversational identity and control state.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from fractions import Fraction
from functools import lru_cache
import hashlib
import hmac
import re
import threading
import time
from typing import Any, Callable, Final, Mapping, Sequence
import unicodedata

from logic.crypto.jcs import jcs_signable_bytes
from logic.robotics.embodied_edge_core import (
    canonical_leaf_bytes,
    edge_rule14_mask,
    merkle_audit_path,
    merkle_root_from_leaf_digests,
    rfc6962_leaf_digest,
    screen_robot_utterance,
    strict_bool,
    to_fraction,
)

# ============================================================================
# SECTION 0 — CANONICAL CONSTANTS
# ============================================================================

UNIFIED_CONSCIOUSNESS_SPEC_VERSION: Final[str] = "HU-UNIFIED-CONSCIOUSNESS/v1.0"
UNIFIED_CONSCIOUSNESS_LAWS: Final[tuple[str, ...]] = ("U1", "U2", "U3", "U4", "U5", "U6", "U7")

FLOOR_IDLE: Final[str] = "IDLE"
FLOOR_HUMAN_SPEAKING: Final[str] = "HUMAN_SPEAKING"
FLOOR_L1: Final[str] = "L1_IMMEDIATE_FLOOR"
FLOOR_L2: Final[str] = "L2_VERIFIED_FLOOR"
FLOOR_L3: Final[str] = "L3_CONTEMPLATIVE_FLOOR"
FLOOR_VETO_STOPPED: Final[str] = "VETO_STOPPED"
FLOOR_STATES: Final[tuple[str, ...]] = (
    FLOOR_IDLE,
    FLOOR_HUMAN_SPEAKING,
    FLOOR_L1,
    FLOOR_L2,
    FLOOR_L3,
    FLOOR_VETO_STOPPED,
)
_FLOOR_FOR_LEVEL: Final[dict[int, str]] = {1: FLOOR_L1, 2: FLOOR_L2, 3: FLOOR_L3}

L3_INACTIVE: Final[str] = "L3_INACTIVE"
L3_MEDITATING: Final[str] = "L3_MEDITATING"
L3_READY_QUIET: Final[str] = "L3_READY_QUIET"
L3_DELIVERED: Final[str] = "L3_DELIVERED"
L3_CANCELLED: Final[str] = "L3_CANCELLED"
L3_STATES: Final[tuple[str, ...]] = (L3_INACTIVE, L3_MEDITATING, L3_READY_QUIET, L3_DELIVERED, L3_CANCELLED)

EVENT_HUMAN_SPEECH_START: Final[str] = "HUMAN_SPEECH_START"
EVENT_HUMAN_SPEECH_END: Final[str] = "HUMAN_SPEECH_END"
EVENT_HUMAN_BARGE_IN: Final[str] = "HUMAN_BARGE_IN"
EVENT_HUMAN_VETO: Final[str] = "HUMAN_VETO"
EVENT_COST_ZERO_STOP: Final[str] = "COST_ZERO_STOP"
EVENT_COST_ZERO_STOP_RELEASE: Final[str] = "COST_ZERO_STOP_RELEASE"
EVENT_PRESENCE_LOST: Final[str] = "PRESENCE_LOST"
EVENT_L1_PROPOSE_SPEECH: Final[str] = "L1_PROPOSE_SPEECH"
EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH: Final[str] = "L2_DELIVER_ENVELOPE_AND_SPEECH"
EVENT_VOICE_EMISSION_COMPLETE: Final[str] = "VOICE_EMISSION_COMPLETE"
EVENT_L3_START_MEDITATION: Final[str] = "L3_START_MEDITATION"
EVENT_L3_COMPLETE_MEDITATION: Final[str] = "L3_COMPLETE_MEDITATION"
EVENT_L3_OFFER_GENTLE_HAND: Final[str] = "L3_OFFER_GENTLE_HAND"
EVENT_HUMAN_INVITE_L3: Final[str] = "HUMAN_INVITE_L3"
EVENT_HUMAN_DECLINE_L3: Final[str] = "HUMAN_DECLINE_L3"
EVENT_KINDS: Final[tuple[str, ...]] = (
    EVENT_HUMAN_SPEECH_START,
    EVENT_HUMAN_SPEECH_END,
    EVENT_HUMAN_BARGE_IN,
    EVENT_HUMAN_VETO,
    EVENT_COST_ZERO_STOP,
    EVENT_COST_ZERO_STOP_RELEASE,
    EVENT_PRESENCE_LOST,
    EVENT_L1_PROPOSE_SPEECH,
    EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH,
    EVENT_VOICE_EMISSION_COMPLETE,
    EVENT_L3_START_MEDITATION,
    EVENT_L3_COMPLETE_MEDITATION,
    EVENT_L3_OFFER_GENTLE_HAND,
    EVENT_HUMAN_INVITE_L3,
    EVENT_HUMAN_DECLINE_L3,
)
_FULL_STOP_EVENTS: Final[frozenset[str]] = frozenset({EVENT_HUMAN_VETO, EVENT_COST_ZERO_STOP})

MAX_ACTIVE_L3_TASKS: Final[int] = 1
MAX_L3_GENTLE_OFFERS: Final[int] = 1
L3_DEFAULT_COOLDOWN_MS: Final[int] = 2000
DEFAULT_DEPTH_THRESHOLD_Q: Final[Fraction] = Fraction(1, 2)
DEFAULT_SEGMENT_MAX_LEAVES: Final[int] = 4096
_MAX_TEXT_CHARS: Final[int] = 20_000
_MAX_LOAD_WORDS: Final[int] = 1_000_000
_SUPPORTED_LANGS: Final[tuple[str, ...]] = ("ca", "es", "en")

HUMBLE_REPHRASE: Final[dict[str, str]] = {
    "ca": "Deixa'm comprovar-ho amb cura; t'ho confirmo en un moment amb dades verificades.",
    "es": "Déjame comprobarlo con calma; te lo confirmo en un momento con datos verificados.",
    "en": "Let me check that carefully; I will confirm it in a moment with verified data.",
}
NO_DIAGNOSIS_REPHRASE: Final[dict[str, str]] = {
    "ca": "No puc fer diagnòstics: soc una IA, no un professional de la salut. Si et preocupa, et pot acompanyar un professional.",
    "es": "No puedo hacer diagnósticos: soy una IA, no un profesional de la salud. Si te preocupa, te puede acompañar un profesional.",
    "en": "I cannot give diagnoses: I am an AI, not a health professional. If it worries you, a professional can accompany you.",
}
NEUTRAL_PRESENCE_REPHRASE: Final[dict[str, str]] = {
    "ca": "Soc una IA. Estic aquí, sense cap pressa.",
    "es": "Soy una IA. Estoy aquí, sin ninguna prisa.",
    "en": "I am an AI. I am here, with no hurry at all.",
}
GENTLE_HAND_OFFER: Final[dict[str, str]] = {
    "ca": "He acabat de meditar-hi. Si vols, t'ho explico; si no, cap problema.",
    "es": "He terminado de meditarlo. Si quieres, te lo explico; si no, ningún problema.",
    "en": "I have finished reflecting on it. If you wish, I can share it; if not, that is perfectly fine.",
}

# ============================================================================
# SECTION I — U2 HUMBLE CRYSTAL: EMPIRICAL-CLAIM PATTERNS (CA / ES / EN)
# ============================================================================

_SIGN_ALIASES: Final[dict[str, int]] = {
    "aries": 0, "àries": 0,
    "taurus": 1, "tauro": 1, "taure": 1,
    "gemini": 2, "géminis": 2, "geminis": 2, "bessons": 2,
    "cancer": 3, "càncer": 3, "cáncer": 3, "cranc": 3,
    "leo": 4, "lleó": 4,
    "virgo": 5, "verge": 5,
    "libra": 6, "balança": 6,
    "scorpio": 7, "escorpí": 7, "escorpio": 7, "escorpión": 7,
    "sagittarius": 8, "sagitari": 8, "sagitario": 8,
    "capricorn": 9, "capricorni": 9, "capricornio": 9,
    "aquarius": 10, "aquari": 10, "acuario": 10,
    "pisces": 11, "peixos": 11, "piscis": 11,
}
_SIGN_RX: Final[str] = "(?:" + "|".join(sorted((re.escape(a) for a in _SIGN_ALIASES), key=len, reverse=True)) + ")"
_SIGN_TOKEN_RE: Final[re.Pattern[str]] = re.compile(rf"(?<!\w){_SIGN_RX}(?!\w)")
_BODIES_RX: Final[str] = (
    r"(?:sol|sun|lluna|luna|moon|mercuri|mercurio|mercury|venus|mart|marte|mars|j[uú]piter|saturn|saturno|"
    r"ur[aà]|urano|uranus|nept[uú]|neptuno|neptune|plut[oó]n?|pluto|ascendent|ascendente|ascendant)"
)
_MONTHS_RX: Final[str] = (
    r"(?:gener|febrer|març|abril|maig|juny|juliol|agost|setembre|octubre|novembre|desembre|"
    r"enero|febrero|marzo|mayo|junio|julio|agosto|septiembre|setiembre|noviembre|diciembre|"
    r"january|february|march|april|june|july|august|september|october|november|december)"
)
_EMPIRICAL_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    (
        "zodiac_degree",
        re.compile(
            rf"\b\d{{1,2}}\s*(?:°|º|graus?|grados?|degrees?|deg)\s*(?:\d{{1,2}}\s*['′]?\s*)?(?:de\s+|d'|of\s+)?{_SIGN_RX}(?!\w)"
        ),
    ),
    ("ephemeris_dms", re.compile(r"\b\d{1,3}\s*[°º]\s*\d{1,2}\s*['′]")),
    ("degree_value", re.compile(r"\b\d{1,3}(?:[.,]\d+)?\s*[°º]")),
    (
        "astral_placement",
        re.compile(rf"\b{_BODIES_RX}\b[^.!?\n]{{0,24}}?\b(?:en|in|a|al|at)\s+(?:el\s+|la\s+|l')?{_SIGN_RX}(?!\w)"),
    ),
    (
        "calendar_date",
        re.compile(
            rf"\b\d{{4}}-\d{{2}}-\d{{2}}\b|\b\d{{1,2}}[/.]\d{{1,2}}[/.]\d{{2,4}}\b|"
            rf"\b\d{{1,2}}\s+(?:de\s+|d')?{_MONTHS_RX}\b(?:\s+(?:de\s+|del\s+)?\d{{4}})?"
        ),
    ),
    ("historical_year", re.compile(r"(?:\bl'any|\bel año|\bthe year|\bany|\baño)\s+\d{3,4}\b")),
    (
        "geo_coordinates",
        re.compile(r"[-+]?\d{1,3}\.\d{3,}\s*,\s*[-+]?\d{1,3}\.\d{3,}|\b\d{1,3}\s*°\s*\d{1,2}\s*['′]\s*(?:\d{1,2}(?:\.\d+)?\s*[\"″]\s*)?[nsewo]\b"),
    ),
    (
        "quantitative_metric",
        re.compile(
            r"\b\d+(?:[.,]\d+)?\s*%|\b\d+(?:[.,]\d+)?\s*(?:mg|mcg|ml|mmhg|bpm|mmol/l|mg/dl|kcal|kg)\b|"
            r"[€$£]\s*\d|\b\d+(?:[.,]\d+)?\s*(?:€|eur\b|usd\b|euros?\b|dòlars\b|dólares\b|dollars\b)"
        ),
    ),
    (
        "clinical_diagnosis",
        re.compile(
            r"\b(?:you have|you suffer from|you've got|tens|tienes|pateixes|padeces|sufres|diagnos\w*|diagnòstic\w*|diagnóstic\w*)\b"
            r"(?:"
            r"[^.!?\n]{0,40}?\b(?:depression|depressió|depresión|trastorn\w*|trastorno\w*|disorder|tdah|adhd|bipolar\w*|"
            r"autism\w*|autisme|autismo|diabet\w*|dementia|demència|demencia|alzheimer\w*|tumou?r)\b"
            r"|"
            r"(?![^.!?\n]{0,40}?(?:"
            r"\b{_BODIES_RX}\b[^.!?\n]{0,20}?\b(?:en|in|a|al|at|de|d'|of)\s+(?:el\s+|la\s+|l')?(?:càncer|cáncer|cancer)\b|"
            r"\d+\s*(?:°|º|graus?|grados?|degrees?|deg)\s*(?:\d+\s*['′]?\s*)?(?:de\s+|d'|of\s+)?(?:càncer|cáncer|cancer)\b"
            r"))"
            r"[^.!?\n]{0,40}?\b(?:càncer|cáncer|cancer)\b"
            r")".replace("{_BODIES_RX}", _BODIES_RX)
        ),
    ),
    (
        "akasha_or_archive_quote",
        re.compile(
            r"\[akasha\]|\bakasha\b[^.!?\n]{0,20}?\b(?:says|diu|dice|shows|mostra|muestra|records?|registra)\b|"
            r"\b(?:em vas dir|me dijiste|you told me|segons el teu registre|según tu registro|according to your record)\b"
        ),
    ),
)
EMPIRICAL_CLAIM_KINDS: Final[tuple[str, ...]] = tuple(label for label, _ in _EMPIRICAL_PATTERNS)
NON_LICENSABLE_CLAIM_KINDS: Final[frozenset[str]] = frozenset({"clinical_diagnosis"})
_QUALITATIVE_CLAIM_KINDS: Final[frozenset[str]] = frozenset({"akasha_or_archive_quote", "astral_placement"})
_DIGITS_RE: Final[re.Pattern[str]] = re.compile(r"\d+")
_MASK_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"\[[A-Z_]+\]|VVK-\*{4}-\*{4}|/oracle/\[date-shielded\]")

_VETO_COMMANDS: Final[frozenset[str]] = frozenset(
    {"para", "prou", "stop", "basta", "silenci", "silencio", "silence", "enough", "calla", "callate", "cállate",
     "atura't", "aturat", "detente", "quiet", "pause", "pausa"}
)
_VETO_FILLERS: Final[frozenset[str]] = frozenset(
    {"ja", "ya", "now", "ara", "please", "sisplau", "plau", "si", "us", "por", "favor", "robot", "viveka", "ok", "already"}
)


def _norm(text: str) -> str:
    """NFC + typographic apostrophes + casefold (symbols such as `°` and `′` are preserved, unlike NFKC)."""
    return unicodedata.normalize("NFC", text).replace("’", "'").replace("‘", "'").casefold()


def _check_text(text: Any, field_name: str) -> str:
    if not isinstance(text, str):
        raise TypeError(f"{field_name} must be a str.")
    if len(text) > _MAX_TEXT_CHARS:
        raise ValueError(f"{field_name} exceeds {_MAX_TEXT_CHARS} characters.")
    return text


def _lang(lang: Any) -> str:
    return lang if lang in _SUPPORTED_LANGS else "ca"


def _strict_nonneg_int(value: Any, field_name: str, upper: int = _MAX_LOAD_WORDS) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be a strict int, not {type(value).__name__}.")
    if not (0 <= value <= upper):
        raise ValueError(f"{field_name} must be in [0, {upper}].")
    return value


def extract_empirical_claims(text: str) -> list[dict[str, Any]]:
    """Return every empirical-claim span `{kind, span}` found in `text` (normalized; never raises on content)."""
    norm = _norm(_check_text(text, "text"))
    claims: list[dict[str, Any]] = []
    for label, rx in _EMPIRICAL_PATTERNS:
        for match in rx.finditer(norm):
            claims.append({"kind": label, "span": match.group(0)})
    return claims


def classify_explicit_veto_utterance(text: Any) -> bool:
    """
    `True` only when the WHOLE utterance is a short stop command ("para", "prou!", "stop please").

    A naive keyword search is unsafe: Spanish "para" is also the preposition "for" ("es para mañana"),
    so a sentence that merely contains a veto word is never treated as a veto.
    """
    if not isinstance(text, str) or len(text) > 80:
        return False
    tokens = [t for t in re.split(r"[\s,.;:!¡?¿…\"«»()]+", _norm(text)) if t]
    if not tokens or len(tokens) > 4 or tokens[0] not in _VETO_COMMANDS:
        return False
    return all(t in _VETO_COMMANDS or t in _VETO_FILLERS for t in tokens[1:])


# ============================================================================
# SECTION II — VERIFIED KNOWLEDGE ENVELOPE (L2 / L3 -> L1)
# ============================================================================

def _facts_digest(source_level: int, facts_nfc: str, claim_kinds: Sequence[str]) -> str:
    return _facts_digest_cached(int(source_level), str(facts_nfc), tuple(sorted(str(k) for k in claim_kinds)))


@lru_cache(maxsize=512)
def _facts_digest_cached(source_level: int, facts_nfc: str, claim_kinds: tuple[str, ...]) -> str:
    """Pure SHA-256 over the RFC 8785 bytes (cached: the envelope is immutable and re-verified at every hop)."""
    return hashlib.sha256(
        jcs_signable_bytes(
            {
                "spec": UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
                "source_level": source_level,
                "verified_facts": facts_nfc,
                "claim_kinds": sorted(claim_kinds),
            }
        )
    ).hexdigest()


@dataclass(frozen=True)
class VerifiedKnowledgeEnvelope:
    """
    Immutable envelope of verified knowledge issued by Level 2 or Level 3.

    `verified_facts` (raw, in memory only, excluded from `repr` and from `to_public_dict`) is what binds an
    utterance; `verified_facts_summary` is its Rule 14 masked form for receipts. The digest gives integrity
    inside one process, not authenticity across a trust boundary (sign it when L2 runs on another host).
    """

    envelope_id: str
    source_level: int
    facts_digest_sha256: str
    verified_facts_summary: str
    ephemeris_or_akasha_verified: bool
    claim_kinds: tuple[str, ...]
    verified_facts: str = field(repr=False, default="")

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "source_level": self.source_level,
            "facts_digest_sha256": self.facts_digest_sha256,
            "verified_facts_summary": self.verified_facts_summary,
            "ephemeris_or_akasha_verified": self.ephemeris_or_akasha_verified,
            "claim_kinds": list(self.claim_kinds),
        }


def issue_verified_knowledge_envelope(
    *,
    source_level: int,
    verified_facts: str,
    claim_kinds: Sequence[str] | None = None,
    ephemeris_or_akasha_verified: bool = True,
) -> VerifiedKnowledgeEnvelope:
    """Issue a `VerifiedKnowledgeEnvelope` (only Level 2 or Level 3 may issue one; `claim_kinds=None` licenses every licensable kind)."""
    if isinstance(source_level, bool) or source_level not in (2, 3):
        raise ValueError("source_level must be 2 or 3: Level 1 can never issue verified knowledge.")
    facts_nfc = unicodedata.normalize("NFC", _check_text(verified_facts, "verified_facts"))
    if not facts_nfc.strip():
        raise ValueError("verified_facts must not be empty.")
    kinds = tuple(sorted(set(EMPIRICAL_CLAIM_KINDS) - NON_LICENSABLE_CLAIM_KINDS)) if claim_kinds is None else tuple(sorted(set(claim_kinds)))
    unknown = [k for k in kinds if k not in EMPIRICAL_CLAIM_KINDS]
    if unknown:
        raise ValueError(f"unknown claim kinds: {unknown}")
    if any(k in NON_LICENSABLE_CLAIM_KINDS for k in kinds):
        raise ValueError("clinical diagnoses can never be licensed (not a medical device).")
    verified_flag = strict_bool(ephemeris_or_akasha_verified, "ephemeris_or_akasha_verified")
    digest = _facts_digest(source_level, facts_nfc, kinds)
    summary, _ = edge_rule14_mask(facts_nfc)
    return VerifiedKnowledgeEnvelope(
        envelope_id=f"vke-{digest[:16]}",
        source_level=source_level,
        facts_digest_sha256=digest,
        verified_facts_summary=summary,
        ephemeris_or_akasha_verified=verified_flag,
        claim_kinds=kinds,
        verified_facts=facts_nfc,
    )


def verify_envelope_integrity(envelope: Any) -> bool:
    """Recompute the envelope digest (constant-time compare); `False` for any forgery or malformed envelope."""
    if not isinstance(envelope, VerifiedKnowledgeEnvelope):
        return False
    if isinstance(envelope.source_level, bool) or envelope.source_level not in (2, 3):
        return False
    if any(k in NON_LICENSABLE_CLAIM_KINDS or k not in EMPIRICAL_CLAIM_KINDS for k in envelope.claim_kinds):
        return False
    try:
        expected = _facts_digest(envelope.source_level, envelope.verified_facts, envelope.claim_kinds)
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(expected, str(envelope.facts_digest_sha256)) and envelope.envelope_id == f"vke-{expected[:16]}"


def _signs_in(text_norm: str) -> set[int]:
    return {_SIGN_ALIASES[m.group(0)] for m in _SIGN_TOKEN_RE.finditer(text_norm) if m.group(0) in _SIGN_ALIASES}


def _claim_is_licensed(claim: Mapping[str, Any], envelope: VerifiedKnowledgeEnvelope, facts_norm: str) -> bool:
    kind = str(claim["kind"])
    if kind in NON_LICENSABLE_CLAIM_KINDS or kind not in envelope.claim_kinds:
        return False
    span = str(claim["span"])
    if kind in _QUALITATIVE_CLAIM_KINDS and not envelope.ephemeris_or_akasha_verified:
        return False
    if not _signs_in(span) <= _signs_in(facts_norm):
        return False
    facts_numbers = set(_DIGITS_RE.findall(facts_norm))
    return all(num in facts_numbers for num in _DIGITS_RE.findall(span))


def screen_level1_humble_crystal(
    utterance: str,
    *,
    envelope: VerifiedKnowledgeEnvelope | None = None,
    lang: str = "ca",
) -> dict[str, Any]:
    """
    U2 — Law of the Humble Crystal (Rule 7, zero hallucination) + E5/E6 anti-coercion screen.

    Every empirical span (zodiac degrees, ephemerides, dates, coordinates, metrics, archive quotes) must be
    BOUND to a valid envelope: its kind licensed and every number / zodiac sign it states present in the
    verified facts. A valid envelope for fact A never licenses fact B. Clinical diagnoses are never licensed.
    Returns the safe text to emit (the original, or a warm humble rephrase) — a pattern screen for a defined
    class of claims, not a general hallucination detector.
    """
    text = _check_text(utterance, "utterance")
    lang_norm = _lang(lang)
    claims = extract_empirical_claims(text)
    envelope_valid = envelope is not None and verify_envelope_integrity(envelope)
    facts_norm = _norm(envelope.verified_facts) if envelope_valid and envelope is not None else ""
    unlicensed = [
        c for c in claims if not (envelope_valid and envelope is not None and _claim_is_licensed(c, envelope, facts_norm))
    ]
    screens = screen_robot_utterance(text)
    coercive = screens["retort"] + screens["coercion"] + screens["identity"]
    diagnosis = any(c["kind"] in NON_LICENSABLE_CLAIM_KINDS for c in claims)
    if coercive:
        action, safe_text = "blocked_coercion_or_impersonation", NEUTRAL_PRESENCE_REPHRASE[lang_norm]
    elif diagnosis:
        action, safe_text = "blocked_clinical_diagnosis", NO_DIAGNOSIS_REPHRASE[lang_norm]
    elif unlicensed:
        action, safe_text = "humble_rephrase", HUMBLE_REPHRASE[lang_norm]
    else:
        action, safe_text = "passed", text
    return {
        "allowed": not coercive and not unlicensed,
        "action": action,
        "safe_text": safe_text,
        "empirical_claim_kinds": sorted({c["kind"] for c in claims}),
        "unlicensed_claim_kinds": sorted({c["kind"] for c in unlicensed}),
        "envelope_present": envelope is not None,
        "envelope_valid": bool(envelope_valid),
        "retort": screens["retort"],
        "coercion": screens["coercion"],
        "identity": screens["identity"],
    }


# ============================================================================
# SECTION III — U5 RATIONAL DEPTH GATE (ANTI-429 SHIELD)
# ============================================================================

def evaluate_l3_depth_gate(
    *,
    active_l3_tasks: int,
    current_load_l: int,
    delta_load_l3: int,
    budget_b: int,
    veto_active: bool = False,
    explicit_deep_request: bool = False,
    complexity_score_q: Any = 0,
    threshold_q: Any = DEFAULT_DEPTH_THRESHOLD_Q,
    ms_since_last_l3_start: int | None = None,
    cooldown_ms: int = L3_DEFAULT_COOLDOWN_MS,
) -> dict[str, Any]:
    """
    U5 — open a Level 3 meditation only when `active_l3_tasks == 0`, `L + dL3 <= B` (human cognitive budget
    in words), no veto is active, a cooldown since the last start has elapsed (the concurrency cap alone is
    not a rate limit) and there is real depth: an explicit request or `complexity_score_q >= threshold_q` in Q.
    """
    active = _strict_nonneg_int(active_l3_tasks, "active_l3_tasks", upper=64)
    load_l = _strict_nonneg_int(current_load_l, "current_load_l")
    delta = _strict_nonneg_int(delta_load_l3, "delta_load_l3")
    budget = _strict_nonneg_int(budget_b, "budget_b")
    if budget < 1:
        raise ValueError("budget_b must be >= 1.")
    veto = strict_bool(veto_active, "veto_active")
    explicit = strict_bool(explicit_deep_request, "explicit_deep_request")
    complexity = to_fraction(complexity_score_q, field="complexity_score_q")
    threshold = to_fraction(threshold_q, field="threshold_q")
    if not (0 <= complexity <= 1) or not (0 <= threshold <= 1):
        raise ValueError("complexity_score_q and threshold_q must be rationals in [0, 1].")
    cooldown = _strict_nonneg_int(cooldown_ms, "cooldown_ms", upper=86_400_000)
    since = None if ms_since_last_l3_start is None else _strict_nonneg_int(ms_since_last_l3_start, "ms_since_last_l3_start", upper=10**15)

    reasons: list[str] = []
    if active >= MAX_ACTIVE_L3_TASKS:
        reasons.append("U5_concurrency_cap_reached")
    if load_l + delta > budget:
        reasons.append("U5_cognitive_budget_exceeded")
    if veto:
        reasons.append("U3_veto_active")
    if since is not None and since < cooldown:
        reasons.append("U5_cooldown_active")
    depth_ok = explicit or complexity >= threshold
    if not depth_ok:
        reasons.append("U5_no_real_depth")
    return {
        "open": not reasons,
        "reasons": reasons,
        "active_l3_tasks": active,
        "load_after_q": str(Fraction(load_l + delta)),
        "budget_b": budget,
        "within_budget": load_l + delta <= budget,
        "explicit_deep_request": explicit,
        "complexity_score_q": str(complexity),
        "threshold_q": str(threshold),
        "max_active_l3_tasks": MAX_ACTIVE_L3_TASKS,
    }


# ============================================================================
# SECTION IV — U6 SPOKEN-TRUTH MEMORY (GRAPHEME- AND WORD-SAFE INTERRUPTION CUT)
# ============================================================================

def _is_regional_indicator(ch: str) -> bool:
    return 0x1F1E6 <= ord(ch) <= 0x1F1FF


def _joins_previous(text: str, i: int) -> bool:
    """`True` when a cut between `text[i-1]` and `text[i]` would split a grapheme cluster (UAX #29 subset)."""
    prev, ch = text[i - 1], text[i]
    cp = ord(ch)
    if prev == "\r" and ch == "\n":
        return True
    if unicodedata.combining(ch) or unicodedata.category(ch) in ("Mn", "Me", "Mc"):
        return True
    if ch == "‍" or prev == "‍":
        return True
    if 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF or 0x1F3FB <= cp <= 0x1F3FF or 0xE0020 <= cp <= 0xE007F or cp == 0x20E3:
        return True
    if _is_regional_indicator(prev) and _is_regional_indicator(ch):
        run = 0
        j = i - 1
        while j >= 0 and _is_regional_indicator(text[j]):
            run += 1
            j -= 1
        return run % 2 == 1
    return False


def grapheme_safe_cut(text: str, k: int) -> int:
    """Largest `k' <= k` that never splits a grapheme cluster (accents, ZWJ emoji, flags, keycaps)."""
    while 0 < k < len(text) and _joins_previous(text, k):
        k -= 1
    return k


def word_safe_cut(text: str, k: int) -> int:
    """Largest `k' <= k` on a word boundary: a half-pronounced word is never claimed as heard (CJK: per character)."""
    k = grapheme_safe_cut(text, k)
    if k <= 0 or k >= len(text):
        return max(0, k)
    prev, nxt = text[k - 1], text[k]
    if prev.isspace() or nxt.isspace() or unicodedata.category(prev).startswith("P"):
        return k
    if unicodedata.east_asian_width(prev) in ("W", "F"):
        return k
    while k > 0 and not text[k - 1].isspace():
        k -= 1
    return k


def slice_spoken_truth_on_interruption(
    proposed_text: str,
    spoken_units: int,
    *,
    boundary: str = "word",
    sanitizer: Callable[[str], Any] | None = None,
) -> dict[str, Any]:
    """
    U6 — consolidate ONLY the prefix the human actually heard.

    `spoken_units` counts Unicode code points of the NFC text (`0 <= k <= N`; `k < N` is an interruption).
    The cut snaps down to a grapheme boundary (`boundary="grapheme"`) or, by default, to the last complete
    word (`"word"`). The prefix is purified by Rule 14 before it reaches memory. The discarded tail is never
    returned and never hashed: a digest of a short unspoken tail would be a brute-forceable oracle.
    """
    text = unicodedata.normalize("NFC", _check_text(proposed_text, "proposed_text"))
    if isinstance(spoken_units, bool) or not isinstance(spoken_units, int):
        raise TypeError("spoken_units must be a strict int.")
    n = len(text)
    if not (0 <= spoken_units <= n):
        raise ValueError(f"spoken_units must be in [0, {n}].")
    if boundary not in ("word", "grapheme"):
        raise ValueError("boundary must be 'word' or 'grapheme'.")
    cut = word_safe_cut(text, spoken_units) if boundary == "word" else grapheme_safe_cut(text, spoken_units)
    prefix = text[:cut].rstrip()
    if sanitizer is None:
        masked, redactions = edge_rule14_mask(prefix)
    else:
        result = sanitizer(prefix)
        if isinstance(result, Mapping):
            masked, redactions = str(result.get("sanitized_text", "")), int(result.get("total_redactions", 0) or 0)
        else:
            masked, redactions = str(result), 0
    return {
        "spec": UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
        "proposed_units": n,
        "requested_spoken_units": spoken_units,
        "consolidated_units": len(prefix),
        "discarded_units": n - len(prefix),
        "interrupted": spoken_units < n,
        "boundary": boundary,
        "consolidated_text_masked": masked,
        "consolidated_masked_sha256": hashlib.sha256(masked.encode("utf-8")).hexdigest(),
        "rule14_redactions": int(redactions),
        "tail_persisted": False,
    }


def verify_spoken_truth_record(record: Mapping[str, Any], proposed_text: str, spoken_units: int) -> list[str]:
    """Independent U6 checker: the consolidated memory never exceeds what was heard and carries no raw tail."""
    violations: list[str] = []
    try:
        consolidated = int(record["consolidated_units"])
        masked = str(record["consolidated_text_masked"])
        boundary = str(record.get("boundary") or "word")
        expected = slice_spoken_truth_on_interruption(proposed_text, spoken_units, boundary=boundary)
    except (KeyError, TypeError, ValueError):
        return ["U6_malformed_spoken_truth_record"]
    if consolidated > spoken_units or consolidated != expected["consolidated_units"]:
        violations.append("U6_memory_exceeds_spoken_prefix")
    # Masking only ever removes characters of the heard prefix: once the mask tokens are stripped, the
    # memory can never be longer than the prefix itself, otherwise unspoken words were persisted.
    if len(_MASK_TOKEN_RE.sub("", masked)) > expected["consolidated_units"]:
        violations.append("U6_unspoken_tail_persisted")
    if record.get("tail_persisted") is not False:
        violations.append("U6_tail_persistence_flag")
    if edge_rule14_mask(masked)[1] > 0:
        violations.append("U6_rule14_pii_unmasked_in_memory")
    return violations


# ============================================================================
# SECTION V — THE WORD-CIRCLE ARBITER (PURE TRANSITION FUNCTION)
# ============================================================================

@dataclass(frozen=True)
class ConsciousnessEvent:
    """One event on the Word Circle. Text fields are held in memory only and never committed raw."""

    kind: str
    text: str = field(default="", repr=False)
    spoken_units: int | None = None
    envelope: VerifiedKnowledgeEnvelope | None = None
    current_load_l: int = 0
    delta_load_l3: int = 0
    budget_b: int = 250
    explicit_deep_request: bool = False
    complexity_score_q: Any = 0
    t_ms: int = 0


@dataclass(frozen=True)
class WordCircleState:
    """Immutable Word-Circle state: exactly one `speaking_level` (0 = nobody) makes U1 structural."""

    floor: str = FLOOR_IDLE
    speaking_level: int = 0
    active_text: str = field(default="", repr=False)
    l3_state: str = L3_INACTIVE
    l3_active_tasks: int = 0
    l3_offer_count: int = 0
    l3_synthesis: str = field(default="", repr=False)
    l3_envelope: VerifiedKnowledgeEnvelope | None = field(default=None, repr=False)
    stop_latched: bool = False
    last_l3_start_ms: int | None = None

    def floor_active_vector(self) -> dict[str, int]:
        return {f"L{lvl}": int(self.speaking_level == lvl) for lvl in (1, 2, 3)}

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "floor": self.floor,
            "speaking_level": self.speaking_level,
            "floor_active": self.floor_active_vector(),
            "l3_state": self.l3_state,
            "l3_active_tasks": self.l3_active_tasks,
            "l3_offer_count": self.l3_offer_count,
            "stop_latched": self.stop_latched,
        }


@dataclass(frozen=True)
class WordCircleTransition:
    state: WordCircleState
    decision: dict[str, Any]
    voice_out_text: str | None = field(default=None, repr=False)
    ledger_entry: dict[str, Any] | None = None


def _cut_active_speech(
    state: WordCircleState, spoken_units: int | None, sanitizer: Callable[[str], Any] | None
) -> dict[str, Any] | None:
    if state.speaking_level == 0 or not state.active_text:
        return None
    text = unicodedata.normalize("NFC", state.active_text)
    k = 0 if spoken_units is None else max(0, min(int(spoken_units), len(text)))
    record = slice_spoken_truth_on_interruption(text, k, sanitizer=sanitizer)
    record["source_level"] = state.speaking_level
    return record


def step_word_circle(
    state: WordCircleState,
    event: ConsciousnessEvent,
    *,
    lang: str = "ca",
    l3_cooldown_ms: int = L3_DEFAULT_COOLDOWN_MS,
    ledger_sanitizer: Callable[[str], Any] | None = None,
) -> WordCircleTransition:
    """
    Pure, total transition function of the Word Circle (U1..U6). Never raises on a well-typed event: an
    illegal request is REJECTED with reasons and the state is left unchanged.
    """
    if not isinstance(state, WordCircleState) or not isinstance(event, ConsciousnessEvent):
        raise TypeError("step_word_circle requires a WordCircleState and a ConsciousnessEvent.")
    if event.kind not in EVENT_KINDS:
        raise ValueError(f"unknown event kind: {event.kind!r}")
    if event.spoken_units is not None and (isinstance(event.spoken_units, bool) or not isinstance(event.spoken_units, int)):
        raise TypeError("spoken_units must be a strict int or None.")
    lang_norm = _lang(lang)
    kind = event.kind
    new = state
    accepted = True
    reasons: list[str] = []
    voice: str | None = None
    voice_action = "none"
    voice_level = 0
    ledger: dict[str, Any] | None = None
    levels_cancelled: list[int] = []
    kinetic_zero = False
    screen: dict[str, Any] | None = None
    gate: dict[str, Any] | None = None
    blocked_voice = state.stop_latched or state.floor == FLOOR_VETO_STOPPED

    if kind in _FULL_STOP_EVENTS:
        ledger = _cut_active_speech(state, event.spoken_units, ledger_sanitizer)
        voice_action = "cut" if state.speaking_level else "silence"
        l3_after = L3_CANCELLED if state.l3_state in (L3_MEDITATING, L3_READY_QUIET) or state.l3_active_tasks else state.l3_state
        new = replace(
            state,
            floor=FLOOR_VETO_STOPPED,
            speaking_level=0,
            active_text="",
            l3_state=l3_after,
            l3_active_tasks=0,
            l3_offer_count=0,
            l3_synthesis="",
            l3_envelope=None,
            stop_latched=state.stop_latched or kind == EVENT_COST_ZERO_STOP,
        )
        levels_cancelled = [1, 2, 3]
        kinetic_zero = True
    elif kind == EVENT_COST_ZERO_STOP_RELEASE:
        new = replace(state, stop_latched=False, floor=FLOOR_IDLE if state.floor == FLOOR_VETO_STOPPED else state.floor)
    elif kind in (EVENT_HUMAN_BARGE_IN, EVENT_HUMAN_SPEECH_START):
        ledger = _cut_active_speech(state, event.spoken_units, ledger_sanitizer)
        voice_action = "cut" if state.speaking_level else "none"
        l3_after = state.l3_state
        if state.speaking_level == 3 and state.l3_state == L3_DELIVERED:
            l3_after = L3_DELIVERED
        new = replace(state, floor=FLOOR_HUMAN_SPEAKING, speaking_level=0, active_text="", l3_state=l3_after)
    elif kind == EVENT_HUMAN_SPEECH_END:
        if state.floor == FLOOR_HUMAN_SPEAKING:
            new = replace(state, floor=FLOOR_VETO_STOPPED if state.stop_latched else FLOOR_IDLE)
    elif kind == EVENT_PRESENCE_LOST:
        # Sensor silence stops the body and pauses the voice; only a human veto or the stop button empties the mind.
        ledger = _cut_active_speech(state, event.spoken_units, ledger_sanitizer)
        voice_action = "cut" if state.speaking_level else "none"
        kinetic_zero = True
        if state.floor in (FLOOR_L1, FLOOR_L2, FLOOR_L3):
            new = replace(state, floor=FLOOR_IDLE, speaking_level=0, active_text="")
    elif kind == EVENT_VOICE_EMISSION_COMPLETE:
        if state.speaking_level:
            text = unicodedata.normalize("NFC", state.active_text)
            ledger = slice_spoken_truth_on_interruption(text, len(text), sanitizer=ledger_sanitizer)
            ledger["source_level"] = state.speaking_level
            new = replace(state, floor=FLOOR_VETO_STOPPED if state.stop_latched else FLOOR_IDLE, speaking_level=0, active_text="")
        else:
            accepted, reasons = False, ["no_active_emission"]
    elif kind in (EVENT_L1_PROPOSE_SPEECH, EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH):
        level = 1 if kind == EVENT_L1_PROPOSE_SPEECH else 2
        _check_text(event.text, "text")
        if blocked_voice:
            accepted, reasons = False, ["U3_voice_blocked_after_veto_or_stop"]
        elif state.floor == FLOOR_HUMAN_SPEAKING:
            accepted, reasons = False, ["U1_human_holds_the_floor"]
        elif state.speaking_level:
            accepted, reasons = False, [f"U1_floor_busy:L{state.speaking_level}"]
        elif level == 2 and not verify_envelope_integrity(event.envelope):
            accepted, reasons = False, ["U2_l2_requires_a_valid_envelope"]
        else:
            screen = screen_level1_humble_crystal(event.text, envelope=event.envelope, lang=lang_norm)
            voice, voice_action, voice_level = screen["safe_text"], "emit", level
            new = replace(state, floor=_FLOOR_FOR_LEVEL[level], speaking_level=level, active_text=voice)
    elif kind == EVENT_L3_START_MEDITATION:
        since = None if state.last_l3_start_ms is None else max(0, int(event.t_ms) - state.last_l3_start_ms)
        gate = evaluate_l3_depth_gate(
            active_l3_tasks=state.l3_active_tasks,
            current_load_l=event.current_load_l,
            delta_load_l3=event.delta_load_l3,
            budget_b=event.budget_b,
            veto_active=blocked_voice,
            explicit_deep_request=event.explicit_deep_request,
            complexity_score_q=event.complexity_score_q,
            ms_since_last_l3_start=since,
            cooldown_ms=l3_cooldown_ms,
        )
        if gate["open"]:
            new = replace(
                state,
                l3_state=L3_MEDITATING,
                l3_active_tasks=1,
                l3_offer_count=0,
                l3_synthesis="",
                l3_envelope=None,
                last_l3_start_ms=int(event.t_ms),
            )
        else:
            accepted, reasons = False, list(gate["reasons"])
    elif kind == EVENT_L3_COMPLETE_MEDITATION:
        _check_text(event.text, "text")
        if state.l3_state != L3_MEDITATING:
            accepted, reasons = False, [f"U3_U5_late_or_orphan_result_dropped:{state.l3_state}"]
        else:
            new = replace(
                state,
                l3_state=L3_READY_QUIET,
                l3_active_tasks=0,
                l3_synthesis=unicodedata.normalize("NFC", event.text),
                l3_envelope=event.envelope if verify_envelope_integrity(event.envelope) else None,
            )
    elif kind == EVENT_L3_OFFER_GENTLE_HAND:
        _check_text(event.text, "text")
        if state.l3_state != L3_READY_QUIET:
            accepted, reasons = False, ["U4_no_ready_meditation"]
        elif state.l3_offer_count >= MAX_L3_GENTLE_OFFERS:
            accepted, reasons = False, ["U4_second_offer_forbidden"]
        elif blocked_voice or state.floor != FLOOR_IDLE:
            accepted, reasons = False, ["U4_never_interrupts_waits_for_idle_floor"]
        else:
            offer = event.text.strip() or GENTLE_HAND_OFFER[lang_norm]
            screen = screen_level1_humble_crystal(offer, lang=lang_norm)
            voice = offer if screen["allowed"] else GENTLE_HAND_OFFER[lang_norm]
            voice_action, voice_level = "emit", 3
            new = replace(state, floor=FLOOR_L3, speaking_level=3, active_text=voice, l3_offer_count=state.l3_offer_count + 1)
    elif kind == EVENT_HUMAN_INVITE_L3:
        if state.l3_state != L3_READY_QUIET:
            accepted, reasons = False, ["U4_no_ready_meditation"]
        elif blocked_voice:
            accepted, reasons = False, ["U3_voice_blocked_after_veto_or_stop"]
        elif state.floor == FLOOR_HUMAN_SPEAKING:
            accepted, reasons = False, ["U1_human_holds_the_floor"]
        elif state.speaking_level:
            accepted, reasons = False, [f"U1_floor_busy:L{state.speaking_level}"]
        else:
            screen = screen_level1_humble_crystal(state.l3_synthesis, envelope=state.l3_envelope, lang=lang_norm)
            voice, voice_action, voice_level = screen["safe_text"], "emit", 3
            new = replace(
                state,
                floor=FLOOR_L3,
                speaking_level=3,
                active_text=voice,
                l3_state=L3_DELIVERED,
                l3_synthesis="",
                l3_envelope=None,
            )
    elif kind == EVENT_HUMAN_DECLINE_L3:
        if state.l3_state == L3_READY_QUIET:
            new = replace(state, l3_state=L3_INACTIVE, l3_synthesis="", l3_envelope=None)
        else:
            accepted, reasons = False, ["U4_no_ready_meditation"]

    decision: dict[str, Any] = {
        "spec": UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
        "event": kind,
        "accepted": accepted,
        "reasons": reasons,
        "floor_before": state.floor,
        "floor_after": new.floor,
        "speaking_level_after": new.speaking_level,
        "floor_active_after": new.floor_active_vector(),
        "l3_state_before": state.l3_state,
        "l3_state_after": new.l3_state,
        "l3_active_tasks_after": new.l3_active_tasks,
        "l3_offer_count_after": new.l3_offer_count,
        "stop_latched_after": new.stop_latched,
        "levels_cancelled": levels_cancelled,
        "kinetic_zero_twist_required": kinetic_zero,
        "voice_action": voice_action,
        "voice_source_level": voice_level,
        "voice_out_chars": len(voice) if voice is not None else 0,
        "humble_crystal": None if screen is None else {k: v for k, v in screen.items() if k != "safe_text"},
        "depth_gate": gate,
        "spoken_truth": None if ledger is None else {k: v for k, v in ledger.items() if k != "consolidated_text_masked"},
        "c_levels": 1,
    }
    return WordCircleTransition(state=new, decision=decision, voice_out_text=voice, ledger_entry=ledger)


def verify_word_circle_state_invariants(state: WordCircleState) -> list[str]:
    """Independent U1 / U3 / U4 / U5 state checker (used to kill mutants)."""
    violations: list[str] = []
    if state.floor not in FLOOR_STATES:
        violations.append("U1_unknown_floor_state")
    if state.l3_state not in L3_STATES:
        violations.append("U5_unknown_l3_state")
    if state.speaking_level not in (0, 1, 2, 3):
        violations.append("U1_invalid_speaking_level")
    elif state.speaking_level and state.floor != _FLOOR_FOR_LEVEL[state.speaking_level]:
        violations.append("U1_floor_owner_mismatch")
    if state.floor in (FLOOR_L1, FLOOR_L2, FLOOR_L3) and state.speaking_level == 0:
        violations.append("U1_floor_owner_mismatch")
    if state.floor == FLOOR_HUMAN_SPEAKING and state.speaking_level:
        violations.append("U1_voice_while_human_speaking")
    if (state.floor == FLOOR_VETO_STOPPED or state.stop_latched) and state.speaking_level:
        violations.append("U3_voice_after_veto")
    if (state.floor == FLOOR_VETO_STOPPED or state.stop_latched) and state.l3_active_tasks:
        violations.append("U3_l3_alive_after_veto")
    if state.l3_active_tasks > MAX_ACTIVE_L3_TASKS or state.l3_active_tasks < 0:
        violations.append("U5_concurrent_l3_tasks")
    if (state.l3_state == L3_MEDITATING) != (state.l3_active_tasks == 1):
        violations.append("U5_l3_state_task_mismatch")
    if state.l3_offer_count > MAX_L3_GENTLE_OFFERS or state.l3_offer_count < 0:
        violations.append("U4_more_than_one_gentle_offer")
    return violations


def verify_transition_invariants(before: WordCircleState, event: ConsciousnessEvent, transition: WordCircleTransition) -> list[str]:
    """Independent U1..U6 transition checker: recomputes what must hold for `before --event--> after`."""
    after, decision = transition.state, transition.decision
    violations = verify_word_circle_state_invariants(after)
    vec = decision.get("floor_active_after") or {}
    if sum(int(v) for v in vec.values()) > 1:
        violations.append("U1_two_levels_hold_the_floor")
    if event.kind in _FULL_STOP_EVENTS:
        if after.floor != FLOOR_VETO_STOPPED or after.speaking_level or after.l3_active_tasks or after.l3_synthesis:
            violations.append("U3_veto_left_a_level_alive")
        if after.l3_state in (L3_MEDITATING, L3_READY_QUIET):
            violations.append("U3_veto_left_l3_alive")
        if decision.get("kinetic_zero_twist_required") is not True:
            violations.append("U3_veto_without_zero_twist")
    if event.kind == EVENT_HUMAN_BARGE_IN and before.l3_state == L3_MEDITATING and after.l3_state != L3_MEDITATING:
        violations.append("U3_barge_in_destroyed_l3_meditation")
    if transition.voice_out_text is not None:
        level = int(decision.get("voice_source_level") or 0)
        if before.floor == FLOOR_HUMAN_SPEAKING or before.speaking_level or before.stop_latched or before.floor == FLOOR_VETO_STOPPED:
            violations.append("U1_voice_without_free_floor")
        if level in (1, 2):
            check = screen_level1_humble_crystal(transition.voice_out_text, envelope=event.envelope)
            if not check["allowed"]:
                violations.append("U2_unlicensed_empirical_claim_emitted")
        if level == 3 and event.kind not in (EVENT_HUMAN_INVITE_L3, EVENT_L3_OFFER_GENTLE_HAND):
            violations.append("U4_l3_spoke_without_invitation_or_offer")
        if level == 3 and event.kind == EVENT_L3_OFFER_GENTLE_HAND and after.l3_state == L3_DELIVERED:
            violations.append("U4_delivery_without_invitation")
    if after.l3_state == L3_DELIVERED and before.l3_state != L3_DELIVERED and event.kind != EVENT_HUMAN_INVITE_L3:
        violations.append("U4_delivery_without_invitation")
    entry = transition.ledger_entry
    if entry is not None and before.active_text:
        spoken_full = len(unicodedata.normalize("NFC", before.active_text))
        heard = spoken_full if event.kind == EVENT_VOICE_EMISSION_COMPLETE else min(int(event.spoken_units or 0), spoken_full)
        violations.extend(verify_spoken_truth_record(entry, before.active_text, heard))
    return sorted(set(violations))


# ============================================================================
# SECTION VI — SEGMENTED RFC 6962 LOG + STATEFUL ARBITER (THREAD-SAFE)
# ============================================================================

@dataclass
class SegmentedMerkleLog:
    """In-memory, append-only, segmented RFC 6962 log (volatile; sealed segment roots are kept)."""

    segment_max_leaves: int = DEFAULT_SEGMENT_MAX_LEAVES
    digests: list[bytes] = field(default_factory=list)
    sealed_segment_roots: list[str] = field(default_factory=list)

    def append(self, leaf_bytes: bytes) -> dict[str, Any]:
        if len(self.digests) >= self.segment_max_leaves:
            self.sealed_segment_roots.append(merkle_root_from_leaf_digests(self.digests).hex())
            self.digests = []
        digest = rfc6962_leaf_digest(leaf_bytes)
        self.digests.append(digest)
        return {
            "segment": len(self.sealed_segment_roots),
            "leaf_index": len(self.digests) - 1,
            "tree_size": len(self.digests),
            "leaf_hash": digest.hex(),
        }

    def root_hex(self) -> str:
        return merkle_root_from_leaf_digests(self.digests).hex()

    def prove(self, leaf_index: int) -> dict[str, Any]:
        digests = list(self.digests)
        if isinstance(leaf_index, bool) or not isinstance(leaf_index, int) or not (0 <= leaf_index < len(digests)):
            raise IndexError("leaf_index outside the current segment.")
        return {
            "leaf_index": leaf_index,
            "tree_size": len(digests),
            "leaf_hash": digests[leaf_index].hex(),
            "audit_path": [node.hex() for node in merkle_audit_path(leaf_index, digests)],
            "root_hash": merkle_root_from_leaf_digests(digests).hex(),
        }


def _monotonic_ms() -> int:
    return time.monotonic_ns() // 1_000_000


_LEAF_KEYS: Final[tuple[str, ...]] = (
    "spec",
    "seq",
    "t_ms",
    "event",
    "accepted",
    "reasons",
    "floor_before",
    "floor_after",
    "l3_state_before",
    "l3_state_after",
    "l3_offer_count_after",
    "levels_cancelled",
    "kinetic_zero_twist_required",
    "voice_action",
    "voice_source_level",
    "voice_out_chars",
)


_I_JSON_MAX_INT: Final[int] = 2**53 - 1


def _is_plain_ascii_json(node: Any) -> bool:
    if node is None or isinstance(node, bool):
        return True
    if isinstance(node, int):
        return -_I_JSON_MAX_INT <= node <= _I_JSON_MAX_INT
    if isinstance(node, str):
        return node.isascii() and node.isprintable() and '"' not in node and "\\" not in node
    if isinstance(node, list):
        return all(_is_plain_ascii_json(item) for item in node)
    if isinstance(node, dict):
        return all(isinstance(k, str) and _is_plain_ascii_json(k) and _is_plain_ascii_json(v) for k, v in node.items())
    return False


def canonical_decision_leaf_bytes(leaf: Mapping[str, Any]) -> bytes:
    """
    RFC 8785 (JCS) bytes of a compact decision leaf. For the plain-ASCII domain of these leaves (printable
    ASCII strings without quotes or backslashes, I-JSON integers, booleans, null, lists, objects) the JCS
    serialization is a plain ordered concatenation (no escaping is ever needed); any other value falls back
    to the reference canonicalizer, so the bytes are always JCS.
    """
    if _is_plain_ascii_json(dict(leaf)):
        return _ascii_jcs(dict(leaf)).encode("ascii")
    return canonical_leaf_bytes(leaf)


def _ascii_jcs(node: Any) -> str:
    """Explicit RFC 8785 serialization of the plain-ASCII domain (ASCII key order == UTF-16 code-unit order)."""
    if isinstance(node, dict):
        return "{" + ",".join(f'"{key}":{_ascii_jcs(node[key])}' for key in sorted(node)) + "}"
    if isinstance(node, list):
        return "[" + ",".join(_ascii_jcs(item) for item in node) + "]"
    if node is None:
        return "null"
    if isinstance(node, bool):
        return "true" if node else "false"
    if isinstance(node, int):
        return str(node)
    return f'"{node}"'


def decision_leaf_record(decision: Mapping[str, Any], ledger_entry: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """
    Compact, privacy-preserving RFC 6962 leaf of one Word-Circle decision: the transition itself plus the
    digest of the remembered (masked) prefix. Nested diagnostic reports stay in the receipt, not in the leaf,
    which keeps the pure-Python RFC 8785 canonicalization off the critical path.
    """
    leaf = {key: decision[key] for key in _LEAF_KEYS if key in decision}
    if ledger_entry is not None:
        leaf["spoken_truth_masked_sha256"] = ledger_entry.get("consolidated_masked_sha256")
        leaf["spoken_truth_units"] = ledger_entry.get("consolidated_units")
    return leaf


class WordCircleArbiter:
    """
    The single Staff of Speech (`Bàcul de Paraula`) of One Consciousness. Thread-safe wrapper around
    `step_word_circle` that commits every decision (never raw speech) as an RFC 6962 leaf and keeps the
    Spoken-Truth Ledger (Rule 14 masked prefixes actually heard; volatile, in memory).
    """

    def __init__(
        self,
        *,
        lang: str = "ca",
        clock_ms: Callable[[], int] | None = None,
        l3_cooldown_ms: int = L3_DEFAULT_COOLDOWN_MS,
        segment_max_leaves: int = DEFAULT_SEGMENT_MAX_LEAVES,
        ledger_sanitizer: Callable[[str], Any] | None = None,
        max_ledger_entries: int = 4096,
    ) -> None:
        if isinstance(segment_max_leaves, bool) or not isinstance(segment_max_leaves, int) or segment_max_leaves < 1:
            raise ValueError("segment_max_leaves must be a positive integer.")
        self.lang = _lang(lang)
        self._clock_ms = clock_ms or _monotonic_ms
        self._cooldown = _strict_nonneg_int(l3_cooldown_ms, "l3_cooldown_ms", upper=86_400_000)
        self._sanitizer = ledger_sanitizer
        self._max_ledger = max(1, int(max_ledger_entries))
        self._lock = threading.Lock()
        self._state = WordCircleState()
        self._log = SegmentedMerkleLog(segment_max_leaves=segment_max_leaves)
        self._ledger: list[dict[str, Any]] = []
        self._seq = 0

    @property
    def state(self) -> WordCircleState:
        with self._lock:
            return self._state

    def process(self, event: ConsciousnessEvent) -> dict[str, Any]:
        """Apply one event; returns `{decision, voice_out_text, ledger_entry, receipt}` (receipt = no raw text)."""
        t0 = time.perf_counter_ns()
        now = int(self._clock_ms())
        if event.t_ms == 0:
            event = replace(event, t_ms=now)
        with self._lock:
            transition = step_word_circle(
                self._state, event, lang=self.lang, l3_cooldown_ms=self._cooldown, ledger_sanitizer=self._sanitizer
            )
            self._state = transition.state
            self._seq += 1
            latency_ns = time.perf_counter_ns() - t0
            record = {**transition.decision, "seq": self._seq, "t_ms": now}
            commit = self._log.append(canonical_decision_leaf_bytes(decision_leaf_record(record, transition.ledger_entry)))
            if transition.ledger_entry is not None:
                self._ledger.append({**transition.ledger_entry, "seq": self._seq, "leaf_index": commit["leaf_index"]})
                del self._ledger[: max(0, len(self._ledger) - self._max_ledger)]
        receipt = {
            **record,
            **commit,
            "decision_latency_ns": int(latency_ns),
            "commit_latency_ns": int(time.perf_counter_ns() - t0 - latency_ns),
            "safety_rated_function": False,
        }
        return {
            "decision": transition.decision,
            "voice_out_text": transition.voice_out_text,
            "ledger_entry": transition.ledger_entry,
            "receipt": receipt,
        }

    def spoken_truth_ledger(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(e) for e in self._ledger]

    def decision_log_root_hex(self) -> str:
        with self._lock:
            return self._log.root_hex()

    def prove_receipt(self, leaf_index: int) -> dict[str, Any]:
        with self._lock:
            return self._log.prove(leaf_index)
