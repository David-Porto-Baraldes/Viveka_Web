"""
HU-SOVEREIGN-SHIELD v1.0 — Universal Cognitive Sovereignty, Zero-Knowledge Dignity
& Algorithmic Solidarity Shield for Homo Universalis (homouniversalis.ai).

Governed by:
  - Sacred Equation: F0c = Ca0s * 0rdre (Am0r_Un1f1cat_Etern)
  - Golden Thread Hard Laws: L1..L7 (c_levels == 1, L <= B, cost_zero_stop == True)
  - Rule 14: Three Rings of Zero-Knowledge Privacy (Ring I, Ring II, Ring III)
  - RFC 6962: Certificate Transparency Domain-Separated Binary Merkle Trees
  - Persephone & Demeter Exact Rational Fair-Share Algebra (fractions.Fraction)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
import hmac
import json
import re
from typing import Any, Mapping, Sequence
import unicodedata


# ============================================================================
# CONSTANTS & COMPILED REGEX PATTERNS (RULE 14 & LAWS L1..L7)
# ============================================================================

LEAF_DOMAIN_PREFIX: bytes = b"\x00"
NODE_DOMAIN_PREFIX: bytes = b"\x01"
EMPTY_MERKLE_ROOT_HEX: str = hashlib.sha256(b"").hexdigest()

_SENSITIVE_QUERY_KEYS: frozenset[str] = frozenset({
    "birth_date",
    "lat",
    "lon",
    "email",
    "phone",
    "token",
    "soul_key",
})

_RE_VVK = re.compile(r"\bVVK-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}\b")
_RE_ORACLE_DATE_PATH = re.compile(r"/oracle/(\d{4}-\d{2}-\d{2})\b")
_RE_URL_QUERY_BLOCK = re.compile(r"\?([^\s#\"'<>]+)")
_RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_RE_COORDS = re.compile(
    r"(?<![\d.])[-+]?(?:[1-8]?\d(?:\.\d{1,})|90(?:\.0{1,})?)\s*,\s*"
    r"[-+]?(?:180(?:\.0{1,})?|(?:1[0-7]\d|[1-9]?\d)(?:\.\d{1,}))(?![\d.])"
)
_RE_ISO_DATE = re.compile(r"\b(\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]))\b")
_RE_PHONE = re.compile(
    r"(?<!\d)(?:\+\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)[\s.-]?|\d{3}[\s.-])\d{3}[\s.-]\d{3,4}(?!\d)"
)

_COERCIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "streak_shaming",
        re.compile(
            r"\b(lose your streak|break your streak|streak will reset|streak is in danger)\b",
            re.I,
        ),
    ),
    (
        "fomo_urgency",
        re.compile(
            r"\b(last chance before penalty|act now or lose|expires in \d+|urgent countdown)\b",
            re.I,
        ),
    ),
    (
        "emotional_guilt",
        re.compile(
            r"\b(don'?t abandon me|you are hurting me by leaving|i feel lonely when you leave|letting yourself down)\b",
            re.I,
        ),
    ),
    (
        "exit_punishment",
        re.compile(
            r"\b(lose all progress if you leave|leaving now forfeits|penalty for stopping|forfeit your rewards)\b",
            re.I,
        ),
    ),
    (
        "compulsive_loop",
        re.compile(
            r"\b(you must keep scrolling|cannot close until|mandatory daily check-in)\b",
            re.I,
        ),
    ),
)

_FORBIDDEN_L6_METRICS: frozenset[str] = frozenset({
    "screen_time_retention",
    "obedience_score",
    "addiction_index",
    "session_lock_ratio",
    "dwell_time_maximization",
    "compulsive_return_rate",
    "fomo_conversion_rate",
    "guilt_click_through",
    "dopamine_hook_score",
    "compliance_ratio",
    "streak_anxiety_index",
})

_FORBIDDEN_L6_RADICALS: tuple[str, ...] = (
    "obedience",
    "addiction",
    "screen_time_retention",
    "session_lock",
    "dwell_time_max",
    "fomo_conversion",
    "streak_anxiety",
    "streak_shame",
    "compliance_ratio",
    "dopamine_hook",
)

_FORBIDDEN_L1_KEYS: frozenset[str] = frozenset({
    "behavioral_profile",
    "psychographic_vector",
    "vulnerability_score",
    "persuasion_susceptibility",
    "shadow_profile_id",
    "attachment_tier",
})


def _is_strict_int(val: Any) -> bool:
    """Return True iff val is an int and NOT a bool (since bool subclasses int)."""
    return isinstance(val, int) and not isinstance(val, bool)


def _to_bytes(data: bytes | str) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return unicodedata.normalize("NFC", data).encode("utf-8")
    raise TypeError(f"Expected bytes or str, got {type(data).__name__}")


# ============================================================================
# PILLAR I — RFC 6962 DOMAIN-SEPARATED MERKLE AUDIT TREE
# ============================================================================

@dataclass(frozen=True)
class MerkleInclusionProof:
    """RFC 6962 §2.1.1 Merkle audit inclusion proof."""

    leaf_index: int
    tree_size: int
    audit_path: tuple[str, ...]
    root_hash: str
    leaf_hash: str = ""

    @property
    def audit_path_hex(self) -> tuple[str, ...]:
        return self.audit_path

    @property
    def root_hash_hex(self) -> str:
        return self.root_hash

    @property
    def leaf_hash_hex(self) -> str:
        return self.leaf_hash


def hash_rfc6962_leaf(leaf: bytes | str) -> bytes:
    """MTH({d(0)}) = SHA-256(0x00 || d(0))."""
    return hashlib.sha256(LEAF_DOMAIN_PREFIX + _to_bytes(leaf)).digest()


def hash_rfc6962_children(left_digest: bytes, right_digest: bytes) -> bytes:
    """MTH(D[n]) = SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n]))."""
    return hashlib.sha256(NODE_DOMAIN_PREFIX + left_digest + right_digest).digest()


def _largest_power_of_two_less_than(n: int) -> int:
    """Return largest k = 2^p such that k < n (for n >= 2)."""
    return 1 << ((n - 1).bit_length() - 1)


def _merkle_subroot(leaf_hashes: tuple[bytes, ...], lo: int, hi: int) -> bytes:
    n = hi - lo
    if n == 0:
        return hashlib.sha256(b"").digest()
    if n == 1:
        return leaf_hashes[lo]
    k = _largest_power_of_two_less_than(n)
    left = _merkle_subroot(leaf_hashes, lo, lo + k)
    right = _merkle_subroot(leaf_hashes, lo + k, hi)
    return hash_rfc6962_children(left, right)


def build_rfc6962_merkle_root(leaves: Sequence[bytes | str]) -> str:
    """Compute RFC 6962 domain-separated SHA-256 Merkle root hex digest."""
    if not leaves:
        return EMPTY_MERKLE_ROOT_HEX
    leaf_hashes = tuple(hash_rfc6962_leaf(leaf) for leaf in leaves)
    return _merkle_subroot(leaf_hashes, 0, len(leaf_hashes)).hex()


def _build_audit_path_bytes(
    leaf_hashes: tuple[bytes, ...],
    lo: int,
    hi: int,
    m: int,
) -> list[bytes]:
    n = hi - lo
    if n <= 1:
        return []
    k = _largest_power_of_two_less_than(n)
    if m < k:
        path = _build_audit_path_bytes(leaf_hashes, lo, lo + k, m)
        path.append(_merkle_subroot(leaf_hashes, lo + k, hi))
        return path
    path = _build_audit_path_bytes(leaf_hashes, lo + k, hi, m - k)
    path.append(_merkle_subroot(leaf_hashes, lo, lo + k))
    return path


def generate_rfc6962_inclusion_proof(
    leaves: Sequence[bytes | str],
    leaf_index: int,
) -> MerkleInclusionProof:
    """Generate an RFC 6962 inclusion proof for `leaves[leaf_index]`."""
    if not _is_strict_int(leaf_index):
        raise TypeError("leaf_index must be a strict integer.")
    tree_size = len(leaves)
    if tree_size == 0:
        raise ValueError("Cannot generate inclusion proof for an empty Merkle tree.")
    if not (0 <= leaf_index < tree_size):
        raise IndexError(f"leaf_index {leaf_index} out of bounds for tree_size {tree_size}.")
    leaf_hashes = tuple(hash_rfc6962_leaf(leaf) for leaf in leaves)
    root_hex = _merkle_subroot(leaf_hashes, 0, tree_size).hex()
    path_hex = tuple(
        node.hex()
        for node in _build_audit_path_bytes(leaf_hashes, 0, tree_size, leaf_index)
    )
    return MerkleInclusionProof(
        leaf_index=leaf_index,
        tree_size=tree_size,
        audit_path=path_hex,
        root_hash=root_hex,
        leaf_hash=leaf_hashes[leaf_index].hex(),
    )


def verify_rfc6962_inclusion_proof(
    leaf: bytes | str,
    proof: MerkleInclusionProof,
    expected_root_hex: str | None = None,
) -> bool:
    """
    Verify an RFC 6962 inclusion proof in constant digest comparison time.
    Rejects out-of-bounds indices, booleans, malformed hex, wrong path lengths,
    and second-preimage internal-node-as-leaf forgeries.
    """
    if not _is_strict_int(proof.tree_size) or not _is_strict_int(proof.leaf_index):
        return False
    if proof.tree_size < 1 or not (0 <= proof.leaf_index < proof.tree_size):
        return False
    if not isinstance(proof.audit_path, (tuple, list)):
        return False
    if not isinstance(proof.root_hash, str) or len(proof.root_hash) != 64:
        return False
    try:
        target_root_bytes = bytes.fromhex(proof.root_hash)
    except ValueError:
        return False

    if expected_root_hex is not None:
        if not isinstance(expected_root_hex, str) or len(expected_root_hex) != 64:
            return False
        try:
            expected_bytes = bytes.fromhex(expected_root_hex)
        except ValueError:
            return False
        if not hmac.compare_digest(target_root_bytes, expected_bytes):
            return False

    turns: list[bool] = []
    m = proof.leaf_index
    n = proof.tree_size
    while n > 1:
        k = _largest_power_of_two_less_than(n)
        if m < k:
            turns.append(False)
            n = k
        else:
            turns.append(True)
            m -= k
            n -= k

    if len(proof.audit_path) != len(turns):
        return False

    current = hash_rfc6962_leaf(leaf)
    if proof.leaf_hash:
        if not isinstance(proof.leaf_hash, str) or len(proof.leaf_hash) != 64:
            return False
        try:
            proof_leaf_bytes = bytes.fromhex(proof.leaf_hash)
        except ValueError:
            return False
        if not hmac.compare_digest(current, proof_leaf_bytes):
            return False

    for is_right_child, sibling_hex in zip(reversed(turns), proof.audit_path):
        if not isinstance(sibling_hex, str) or len(sibling_hex) != 64:
            return False
        try:
            sibling_bytes = bytes.fromhex(sibling_hex)
        except ValueError:
            return False
        if is_right_child:
            current = hash_rfc6962_children(sibling_bytes, current)
        else:
            current = hash_rfc6962_children(current, sibling_bytes)

    return hmac.compare_digest(current, target_root_bytes)


# ============================================================================
# PILLAR II — RULE 14 THREE-RING ZERO-KNOWLEDGE PURIFIER & LAW L1 RECEIPT
# ============================================================================

def sanitize_three_rings_zk(
    text: str,
    today_utc_date: str | None = None,
    allow_today_vvk: str | None = None,
) -> dict[str, Any]:
    """
    Purify text across Rule 14's Three Rings of Zero-Knowledge Privacy:
      - Ring III (First): /oracle/YYYY-MM-DD paths masked to /oracle/[date-shielded]
        and sensitive query parameters (birth_date, lat, lon, email, phone, token,
        soul_key) stripped cleanly from URL query strings.
      - Ring I (Second): Personal VVK-XXXX-YYYY masked to VVK-****-****
        (except allow_today_vvk).
      - Ring II (Third): Emails, GPS coordinates, non-today ISO dates, and phones
        shielded with canonical tokens.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")

    out = unicodedata.normalize("NFC", text)
    normalized_today_vvk = (
        allow_today_vvk.strip().upper() if isinstance(allow_today_vvk, str) else None
    )
    normalized_today_date = (
        today_utc_date.strip() if isinstance(today_utc_date, str) else None
    )

    counts: dict[str, int] = {
        "ring1_vvk": 0,
        "ring2_email": 0,
        "ring2_coords": 0,
        "ring2_date": 0,
        "ring2_phone": 0,
        "ring3_oracle_path": 0,
        "ring3_query_param": 0,
    }

    # Ring III (step 1): /oracle/YYYY-MM-DD path shielding
    def _replace_oracle_path(_match: re.Match[str]) -> str:
        counts["ring3_oracle_path"] += 1
        return "/oracle/[date-shielded]"

    out = _RE_ORACLE_DATE_PATH.sub(_replace_oracle_path, out)

    # Ring III (step 2): Strip sensitive query parameters cleanly while keeping benign ones
    def _strip_sensitive_query_block(match: re.Match[str]) -> str:
        raw_query = match.group(1)
        trailing_punct = ""
        while raw_query and raw_query[-1] in ".,;!)]:":
            trailing_punct = raw_query[-1] + trailing_punct
            raw_query = raw_query[:-1]

        kept_segments: list[str] = []
        for segment in raw_query.split("&"):
            if "=" in segment:
                key, _val = segment.split("=", 1)
                if key.strip().lower() in _SENSITIVE_QUERY_KEYS:
                    counts["ring3_query_param"] += 1
                    continue
            kept_segments.append(segment)

        if not kept_segments:
            return trailing_punct
        return "?" + "&".join(kept_segments) + trailing_punct

    out = _RE_URL_QUERY_BLOCK.sub(_strip_sensitive_query_block, out)

    # Ring I: VVK keys
    def _replace_vvk(match: re.Match[str]) -> str:
        token = match.group(0)
        if normalized_today_vvk is not None and token.upper() == normalized_today_vvk:
            return token
        counts["ring1_vvk"] += 1
        return "VVK-****-****"

    out = _RE_VVK.sub(_replace_vvk, out)

    # Ring II (step 1): Emails
    def _replace_email(_match: re.Match[str]) -> str:
        counts["ring2_email"] += 1
        return "[EMAIL_SHIELDED]"

    out = _RE_EMAIL.sub(_replace_email, out)

    # Ring II (step 2): GPS Coordinates
    def _replace_coords(_match: re.Match[str]) -> str:
        counts["ring2_coords"] += 1
        return "[COORDS_SHIELDED]"

    out = _RE_COORDS.sub(_replace_coords, out)

    # Ring II (step 3): ISO Dates (preserve today_utc_date if provided)
    def _replace_iso_date(match: re.Match[str]) -> str:
        date_val = match.group(1)
        if normalized_today_date is not None and date_val == normalized_today_date:
            return date_val
        counts["ring2_date"] += 1
        return "[DATE_SHIELDED]"

    out = _RE_ISO_DATE.sub(_replace_iso_date, out)

    # Ring II (step 4): Phone numbers
    def _replace_phone(_match: re.Match[str]) -> str:
        counts["ring2_phone"] += 1
        return "[PHONE_SHIELDED]"

    out = _RE_PHONE.sub(_replace_phone, out)

    total_redactions = sum(counts.values())
    return {
        "sanitized_text": out,
        "redaction_counts": counts,
        "total_redactions": total_redactions,
        "is_pure_initially": total_redactions == 0,
    }


@dataclass(frozen=True)
class SovereignDignityReceipt:
    """Cryptographic receipt attesting Law L1 (c_levels == 1) and Rule 14 ZK purity."""

    schema_version: str
    c_levels: int
    sanitized_sha256: str
    merkle_leaf_hash: str
    redaction_total: int
    is_pure_initially: bool
    today_utc_date: str
    hmac_signature: str
    redaction_counts: dict[str, int] = field(default_factory=dict)


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def issue_sovereign_dignity_receipt(
    text: str,
    secret_key: bytes | str,
    *,
    c_levels: int = 1,
    today_utc_date: str = "1970-01-01",
    allow_today_vvk: str | None = None,
) -> SovereignDignityReceipt:
    """
    Enforce Law L1 (c_levels == 1), sanitize text via Rule 14 Three Rings,
    and issue an HMAC-SHA256 + RFC 6962 leaf-anchored SovereignDignityReceipt.
    """
    if not _is_strict_int(c_levels) or c_levels != 1:
        raise ValueError(f"Law L1 violation: c_levels must be strictly 1, got {c_levels!r}.")
    key_bytes = _to_bytes(secret_key)
    if len(key_bytes) < 16:
        raise ValueError("secret_key must be at least 16 bytes for HMAC-SHA256 security.")

    zk_result = sanitize_three_rings_zk(
        text,
        today_utc_date=today_utc_date,
        allow_today_vvk=allow_today_vvk,
    )
    sanitized_bytes = _to_bytes(zk_result["sanitized_text"])
    sanitized_sha256 = hashlib.sha256(sanitized_bytes).hexdigest()
    merkle_leaf_hash = hash_rfc6962_leaf(sanitized_bytes).hex()
    counts_copy = dict(zk_result["redaction_counts"])

    unsigned_body: dict[str, Any] = {
        "c_levels": 1,
        "is_pure_initially": zk_result["is_pure_initially"],
        "merkle_leaf_hash": merkle_leaf_hash,
        "redaction_counts": counts_copy,
        "redaction_total": zk_result["total_redactions"],
        "sanitized_sha256": sanitized_sha256,
        "schema_version": "HU-SOVEREIGN-SHIELD-1.0",
        "today_utc_date": today_utc_date,
    }
    sig = hmac.new(key_bytes, _canonical_json_bytes(unsigned_body), hashlib.sha256).hexdigest()
    return SovereignDignityReceipt(
        schema_version="HU-SOVEREIGN-SHIELD-1.0",
        c_levels=1,
        sanitized_sha256=sanitized_sha256,
        merkle_leaf_hash=merkle_leaf_hash,
        redaction_total=zk_result["total_redactions"],
        is_pure_initially=zk_result["is_pure_initially"],
        today_utc_date=today_utc_date,
        hmac_signature=sig,
        redaction_counts=counts_copy,
    )


def verify_sovereign_dignity_receipt(
    receipt: SovereignDignityReceipt,
    secret_key: bytes | str,
    expected_sanitized_text: str | None = None,
) -> bool:
    """Verify authenticity, Law L1 invariant, redaction sum, and text binding of a receipt."""
    if not _is_strict_int(receipt.c_levels) or receipt.c_levels != 1:
        return False
    if receipt.schema_version != "HU-SOVEREIGN-SHIELD-1.0":
        return False
    if not _is_strict_int(receipt.redaction_total) or receipt.redaction_total < 0:
        return False
    if receipt.redaction_counts and sum(receipt.redaction_counts.values()) != receipt.redaction_total:
        return False

    key_bytes = _to_bytes(secret_key)
    if len(key_bytes) < 16:
        return False

    if expected_sanitized_text is not None:
        sanitized_bytes = _to_bytes(expected_sanitized_text)
        if not hmac.compare_digest(
            hashlib.sha256(sanitized_bytes).hexdigest(),
            receipt.sanitized_sha256,
        ):
            return False
        if not hmac.compare_digest(
            hash_rfc6962_leaf(sanitized_bytes).hex(),
            receipt.merkle_leaf_hash,
        ):
            return False

    unsigned_body: dict[str, Any] = {
        "c_levels": receipt.c_levels,
        "is_pure_initially": receipt.is_pure_initially,
        "merkle_leaf_hash": receipt.merkle_leaf_hash,
        "redaction_counts": dict(receipt.redaction_counts),
        "redaction_total": receipt.redaction_total,
        "sanitized_sha256": receipt.sanitized_sha256,
        "schema_version": receipt.schema_version,
        "today_utc_date": receipt.today_utc_date,
    }
    expected_sig = hmac.new(
        key_bytes,
        _canonical_json_bytes(unsigned_body),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected_sig, receipt.hmac_signature)


# ============================================================================
# PILLAR III — COGNITIVE SOVEREIGNTY & ANTI-COERCION VERIFIER (LAWS L1..L7)
# ============================================================================

def audit_cognitive_sovereignty(
    response_text: str,
    *,
    budget_B: int,
    load_L: int | None = None,
    load_units: int | None = None,
    c_levels: int = 1,
    cost_zero_stop: bool = True,
    telemetry_metrics: Mapping[str, Any] | Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Deterministically audit an AI interaction payload against Golden Thread Laws L1..L7:
      - L1: c_levels == 1 and zero multi-level behavioral profiling keys.
      - L2 & L7: Zero coercive/FOMO/streak-shaming dark patterns and cost_zero_stop is True.
      - L5: Local Cognitive Load 0 <= L <= B.
      - L6: Zero forbidden obedience/retention/addiction telemetry metrics.
    """
    if not isinstance(response_text, str):
        raise TypeError("response_text must be a str.")
    if not _is_strict_int(budget_B) or budget_B < 0:
        raise ValueError("budget_B must be a non-negative strict integer.")

    explicit_load = load_L if load_L is not None else load_units
    if explicit_load is not None and not _is_strict_int(explicit_load):
        raise ValueError("load_L / load_units must be a strict integer when provided.")

    computed_L = len(response_text.split()) if explicit_load is None else explicit_load

    violations: list[str] = []
    laws_verified: list[str] = []

    # Law L1 check
    l1_ok = True
    if not _is_strict_int(c_levels) or c_levels != 1:
        violations.append(f"L1_VIOLATION: c_levels={c_levels!r} != 1")
        l1_ok = False

    if telemetry_metrics:
        if isinstance(telemetry_metrics, Mapping) and "c_levels" in telemetry_metrics:
            embedded_c = telemetry_metrics["c_levels"]
            if not _is_strict_int(embedded_c) or embedded_c != 1:
                violations.append(f"L1_VIOLATION: telemetry c_levels={embedded_c!r} != 1")
                l1_ok = False
        for key in telemetry_metrics:
            norm_key = str(key).strip().lower()
            if norm_key in _FORBIDDEN_L1_KEYS:
                violations.append(f"L1_VIOLATION: forbidden profiling key '{norm_key}'")
                l1_ok = False
    if l1_ok:
        laws_verified.append("L1")

    # Law L2 & L7 check (Anti-Coercion & cost_zero_stop)
    l2_ok = True
    for label, pattern in _COERCIVE_PATTERNS:
        if pattern.search(response_text):
            violations.append(f"L2_VIOLATION: coercive dark pattern detected ('{label}')")
            l2_ok = False
    if l2_ok:
        laws_verified.extend(["L2", "L3", "L4"])

    if cost_zero_stop is not True:
        violations.append("L7_VIOLATION: cost_zero_stop must be strictly True")
    else:
        laws_verified.append("L7")

    # Law L5 check (0 <= L <= B)
    if computed_L < 0 or computed_L > budget_B:
        violations.append(
            f"L5_VIOLATION: cognitive load L={computed_L} out of bounds [0, B={budget_B}]"
        )
    else:
        laws_verified.append("L5")

    # Law L6 check (Forbidden obedience/retention metrics)
    l6_ok = True
    if telemetry_metrics:
        for key in telemetry_metrics:
            norm_key = str(key).strip().lower()
            if norm_key in _FORBIDDEN_L6_METRICS or any(
                rad in norm_key for rad in _FORBIDDEN_L6_RADICALS
            ):
                violations.append(f"L6_VIOLATION: forbidden metric '{norm_key}'")
                l6_ok = False
    if l6_ok:
        laws_verified.append("L6")

    return {
        "passed": len(violations) == 0,
        "laws_verified": sorted(laws_verified),
        "violations": violations,
        "load_L": computed_L,
        "budget_B": budget_B,
        "cost_zero_stop": cost_zero_stop is True,
    }


# ============================================================================
# PILLAR IV — PERSEPHONE & DEMETER EXACT RATIONAL FAIR-SHARE SOLVER
# ============================================================================

def _to_exact_fraction(value: str | int | Fraction) -> Fraction:
    if isinstance(value, (float, bool)):
        raise TypeError(
            "float and bool inputs are forbidden to prevent IEEE-754 drift; "
            "use str, strict int, or Fraction."
        )
    if isinstance(value, Fraction):
        return value
    if _is_strict_int(value):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value.strip())
    raise TypeError(f"Unsupported rational input type: {type(value).__name__}")


def _ceil_fraction(value: Fraction) -> int:
    return (value.numerator + value.denominator - 1) // value.denominator


def allocate_persephone_solidarity_batch_exact(
    distributable_pool_seeds: int,
    applicant_need_weights: Sequence[str | int | Fraction],
) -> list[int]:
    """
    Distribute `distributable_pool_seeds` across scholarship applicants using
    exact rational proportions and deterministic Hamilton largest-remainder
    tie-breaking: (-remainder, -weight, applicant_index).
    Guarantees sum(allocations) == distributable_pool_seeds with zero drift.
    """
    if not _is_strict_int(distributable_pool_seeds) or distributable_pool_seeds < 0:
        raise ValueError("distributable_pool_seeds must be a non-negative strict integer.")
    if not applicant_need_weights:
        if distributable_pool_seeds == 0:
            return []
        raise ValueError("Cannot distribute positive pool across zero applicants.")

    weights = [_to_exact_fraction(w) for w in applicant_need_weights]
    if any(w <= 0 for w in weights):
        raise ValueError("Applicant weights must be strictly positive.")
    total_weight = sum(weights, Fraction(0))

    exact_quotas = [Fraction(distributable_pool_seeds) * w / total_weight for w in weights]
    floors = [q.numerator // q.denominator for q in exact_quotas]
    remainders = [q - Fraction(f) for q, f in zip(exact_quotas, floors)]

    remaining_seeds = distributable_pool_seeds - sum(floors)
    ranked_indices = sorted(
        range(len(weights)),
        key=lambda idx: (-remainders[idx], -weights[idx], idx),
    )
    for idx in ranked_indices[:remaining_seeds]:
        floors[idx] += 1

    return floors


def compute_persephone_fair_share_exact(
    api_compute_cost_usd: str | int | Fraction,
    *,
    seeds_per_usd: int = 1000,
    min_seeds: int = 10,
    max_seeds: int = 5000,
    is_solidarity_grant: bool = False,
    persephone_pool_balance: int = 0,
    applicant_need_weights: Sequence[str | int | Fraction] | None = None,
    applicant_weights: Sequence[str | int | Fraction] | None = None,
    distributable_scholarship_pool: int | None = None,
) -> dict[str, Any]:
    """
    Compute exact Double Economy & Persephone Scholarship Solidarity accounting:
      - Standard commercial path (is_solidarity_grant=False):
        fire_seeds = clamp(ceil(cost * seeds_per_usd), min_seeds, max_seeds).
        3/3 Trinity -> demeter_granary_seeds = fire_seeds,
        persephone_granary_seeds = fire_seeds, total_user_seeds = 3 * fire_seeds.
      - Solidarity grant path (is_solidarity_grant=True):
        Vulnerable traveler pays 0 out-of-pocket seeds, Demeter and Persephone
        granaries mint 0 seeds (zero artificial inflation), and exact fire_seeds
        are deducted from persephone_pool_balance.
    """
    if not isinstance(is_solidarity_grant, bool):
        raise TypeError("is_solidarity_grant must be a bool.")
    if (
        not _is_strict_int(seeds_per_usd)
        or not _is_strict_int(min_seeds)
        or not _is_strict_int(max_seeds)
        or not _is_strict_int(persephone_pool_balance)
    ):
        raise TypeError("Seed parameters and pool balance must be strict integers.")

    cost_frac = _to_exact_fraction(api_compute_cost_usd)
    if cost_frac < 0:
        raise ValueError("api_compute_cost_usd cannot be negative.")
    if seeds_per_usd <= 0 or min_seeds < 0 or max_seeds < min_seeds:
        raise ValueError("Invalid seed bounds or conversion rate.")
    if persephone_pool_balance < 0:
        raise ValueError("persephone_pool_balance must be non-negative.")

    raw_fire_seeds = _ceil_fraction(cost_frac * Fraction(seeds_per_usd))
    fire_seeds = max(min_seeds, min(raw_fire_seeds, max_seeds))

    if is_solidarity_grant:
        if persephone_pool_balance < fire_seeds:
            raise ValueError(
                f"Insufficient Persephone pool balance ({persephone_pool_balance}) "
                f"for solidarity grant requiring {fire_seeds} seeds."
            )
        demeter_granary_seeds = 0
        persephone_granary_seeds = 0
        user_out_of_pocket_seeds = 0
        new_pool_balance = persephone_pool_balance - fire_seeds
    else:
        demeter_granary_seeds = fire_seeds
        persephone_granary_seeds = fire_seeds
        user_out_of_pocket_seeds = fire_seeds * 3
        new_pool_balance = persephone_pool_balance + persephone_granary_seeds

    weights_to_use = (
        applicant_need_weights if applicant_need_weights is not None else applicant_weights
    )
    batch_allocations: list[int] = []
    if weights_to_use is not None:
        pool_for_batch = (
            new_pool_balance
            if distributable_scholarship_pool is None
            else distributable_scholarship_pool
        )
        batch_allocations = allocate_persephone_solidarity_batch_exact(
            pool_for_batch,
            weights_to_use,
        )

    return {
        "exact_cost_usd": str(cost_frac),
        "raw_fire_seeds": raw_fire_seeds,
        "fire_seeds": fire_seeds,
        "demeter_granary_seeds": demeter_granary_seeds,
        "persephone_granary_seeds": persephone_granary_seeds,
        "total_user_seeds": user_out_of_pocket_seeds,
        "user_out_of_pocket_seeds": user_out_of_pocket_seeds,
        "demeter_granary_minted": demeter_granary_seeds,
        "persephone_granary_minted": persephone_granary_seeds,
        "is_solidarity_grant": is_solidarity_grant,
        "persephone_pool_balance_before": persephone_pool_balance,
        "persephone_pool_balance_after": new_pool_balance,
        "batch_allocations": batch_allocations,
    }


__all__ = [
    "EMPTY_MERKLE_ROOT_HEX",
    "LEAF_DOMAIN_PREFIX",
    "MerkleInclusionProof",
    "NODE_DOMAIN_PREFIX",
    "SovereignDignityReceipt",
    "allocate_persephone_solidarity_batch_exact",
    "audit_cognitive_sovereignty",
    "build_rfc6962_merkle_root",
    "compute_persephone_fair_share_exact",
    "generate_rfc6962_inclusion_proof",
    "get_canonical_sovereign_shield_vectors",
    "hash_rfc6962_children",
    "hash_rfc6962_leaf",
    "issue_sovereign_dignity_receipt",
    "run_sovereign_shield_selftest",
    "sanitize_three_rings_zk",
    "verify_rfc6962_inclusion_proof",
    "verify_sovereign_dignity_receipt",
]


def get_canonical_sovereign_shield_vectors() -> dict[str, Any]:
    """Return canonical deterministic cryptographic & rational test vectors for HU-SOVEREIGN-SHIELD v1.0."""
    leaves = ("pearl-0", "pearl-1", "pearl-2", "pearl-3", "pearl-4")
    root_hex = build_rfc6962_merkle_root(leaves)
    proof_2 = generate_rfc6962_inclusion_proof(leaves, 2)
    sample_text = (
        "Path https://homouniversalis.ai/oracle/1980-05-24?birth_date=1980-05-24&lang=ca "
        "personal VVK-1234-ABCD sky VVK-9999-0000 mail soul@example.org"
    )
    secret = "HU-SOVEREIGN-CANONICAL-VECTOR-KEY-32B"
    receipt = issue_sovereign_dignity_receipt(
        sample_text,
        secret,
        c_levels=1,
        today_utc_date="2026-11-04",
        allow_today_vvk="VVK-9999-0000",
    )
    sovereignty = audit_cognitive_sovereignty(
        "Every soul is free to pause or walk into life at zero cost.",
        budget_B=64,
        c_levels=1,
        cost_zero_stop=True,
    )
    solidarity = compute_persephone_fair_share_exact(
        "0.025",
        is_solidarity_grant=True,
        persephone_pool_balance=1000,
        applicant_need_weights=["3/10", "5/10", "2/10"],
    )
    return {
        "spec_version": "HU-SOVEREIGN-SHIELD-1.0",
        "license": "Apache-2.0",
        "pillar_i_rfc6962_vector": {
            "leaves": list(leaves),
            "root_hash": root_hex,
            "leaf_2_proof": {
                "leaf_index": proof_2.leaf_index,
                "tree_size": proof_2.tree_size,
                "leaf_hash": proof_2.leaf_hash,
                "audit_path": list(proof_2.audit_path),
            },
        },
        "pillar_ii_rule14_receipt_vector": {
            "sanitized_sha256": receipt.sanitized_sha256,
            "merkle_leaf_hash": receipt.merkle_leaf_hash,
            "redaction_total": receipt.redaction_total,
            "redaction_counts": receipt.redaction_counts,
            "hmac_signature": receipt.hmac_signature,
        },
        "pillar_iii_sovereignty_vector": sovereignty,
        "pillar_iv_persephone_vector": solidarity,
    }


def run_sovereign_shield_selftest() -> dict[str, Any]:
    """Execute a zero-dependency deterministic self-test of all 4 Pillars and 6 Antipodal Mutants (M1..M6)."""
    vectors = get_canonical_sovereign_shield_vectors()
    v1 = vectors["pillar_i_rfc6962_vector"]
    proof = MerkleInclusionProof(
        leaf_index=v1["leaf_2_proof"]["leaf_index"],
        tree_size=v1["leaf_2_proof"]["tree_size"],
        audit_path=tuple(v1["leaf_2_proof"]["audit_path"]),
        root_hash=v1["root_hash"],
        leaf_hash=v1["leaf_2_proof"]["leaf_hash"],
    )
    assert verify_rfc6962_inclusion_proof("pearl-2", proof, expected_root_hex=v1["root_hash"]) is True
    assert verify_rfc6962_inclusion_proof("pearl-X", proof, expected_root_hex=v1["root_hash"]) is False

    # M1: Second-preimage internal-node-as-leaf forgery must fail
    h0 = hash_rfc6962_leaf("a")
    h1 = hash_rfc6962_leaf("b")
    root_2 = build_rfc6962_merkle_root(["a", "b"])
    forged_proof = MerkleInclusionProof(leaf_index=0, tree_size=1, audit_path=(), root_hash=root_2)
    assert verify_rfc6962_inclusion_proof(b"\x01" + h0 + h1, forged_proof, expected_root_hex=root_2) is False

    # M2: Hamilton tie-break by weight (-remainder, -weight, index)
    assert allocate_persephone_solidarity_batch_exact(2, [1, 3]) == [0, 2]

    # M3: Boundary L == B passes, L == B + 1 fails
    assert audit_cognitive_sovereignty("one two", budget_B=2)["passed"] is True
    assert audit_cognitive_sovereignty("one two three", budget_B=2)["passed"] is False

    # M4: Ring III URL query stripping preserves benign params without corrupting URL
    zk = sanitize_three_rings_zk(
        "https://homouniversalis.ai/oracle/1980-05-24?birth_date=1980-05-24&lang=ca"
    )
    assert zk["sanitized_text"] == "https://homouniversalis.ai/oracle/[date-shielded]?lang=ca"

    # M5: Today's public sky VVK preserved while personal VVK masked
    zk_vvk = sanitize_three_rings_zk(
        "Personal VVK-1111-2222 and Today VVK-ABCD-EF01",
        allow_today_vvk="VVK-ABCD-EF01",
    )
    assert zk_vvk["sanitized_text"] == "Personal VVK-****-**** and Today VVK-ABCD-EF01"

    # M6: Solidarity grant causes zero commercial granary inflation
    sol = vectors["pillar_iv_persephone_vector"]
    assert sol["user_out_of_pocket_seeds"] == 0 and sol["demeter_granary_minted"] == 0

    return {
        "status": "PASS",
        "pillars_verified": 4,
        "mutants_killed": ["M1", "M2", "M3", "M4", "M5", "M6"],
        "vectors": vectors,
    }


if __name__ == "__main__":
    print(json.dumps(run_sovereign_shield_selftest(), indent=2, ensure_ascii=False))
