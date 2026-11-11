# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
Living Folio IV of Leonardo da Vinci (`logic/engines/maat_w3c_vc_notary_crucible.py` · 46-Facet Diamond Edition):
  1. W3C Verifiable Credentials Data Model v2.0 (`MaatHumanDignityCredential`) secured as a
     W3C VC-JOSE-COSE Compact JWS (`application/vc+jwt`, asymmetric `ES256` ECDSA P-256) over
     RFC 8785 (JCS) canonical bytes with strict float rejection (`WO-01` & `WO-08`).
  2. RFC 6962 §2.1.1 & §2.1.2 Binary Merkle Tree & Append-Only Consistency Subproofs
     (`SUBPROOF(m, D[n], b)`) proving that the Golden Book of Ma'at is strictly append-only
     between any tree sizes `1 <= m <= n` with zero-slice `O(log n)` windowing.
  3. Constant-Depth Sparse Merkle Revocation & Non-Membership Tree (`O(H)` cryptographic proof
     that a certificate serial is `ACTIVE`, `REVOKED`, or `EMPTY`, binding `slot_index` to
     `SHA-256(serial_id)` to prevent cross-slot replay).
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
import hmac
import json
import os
import re
import threading
import time
from typing import Any, Callable, Final, Literal, Mapping, Protocol, Sequence, runtime_checkable
import uuid

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)

from logic.crypto.es256 import (
    der_to_jose_es256_low_s as _shared_der_to_jose_es256_low_s,
    sign_jose_es256_low_s as _shared_sign_jose_es256_low_s,
    verify_jose_es256_raw as _shared_verify_jose_es256_raw,
)
from logic.crypto.jcs import (
    assert_signable as _jcs_assert_signable,
    jcs_loads as _jcs_loads,
    jcs_signable_bytes as _jcs_signable_bytes,
)

FOLIO_IV_ID: Final[str] = "folio-IV-maat-w3c-vc-and-rfc6962-notary"
MAAT_VC_DEFAULT_KID: Final[str] = "maat-vc-es256-2026-1"
MAAT_VC_MEDIA_TYPE: Final[str] = "vc+jwt"
MAAT_DIGNITY_JSONLD_CONTEXT_URL: Final[str] = "https://homouniversalis.ai/codex/schemas/maat-dignity-v1.jsonld"
_URN_UUID_V4_RE: Final[re.Pattern[str]] = re.compile(
    r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
LOG_STH_DEFAULT_KID: Final[str] = "hu-log-sth-es256-2026-1"
LOG_STH_MEDIA_TYPE: Final[str] = "sth+jwt"
SMT_DEFAULT_DEPTH: Final[int] = 16
SMT_COLLISION_FREE_DEPTH: Final[int] = 256
MAAT_VC_DEFAULT_MAX_LIFETIME_DAYS: Final[int] = 365
MAAT_STATUS_STH_FRESHNESS_WINDOW_SECONDS: Final[int] = 86_400
MAAT_GOLDEN_BOOK_LOG_ID: Final[str] = "hu-maat-golden-book-2026"
MAAT_SMT_REVOCATION_LOG_ID: Final[str] = "hu-maat-smt-2026"
SOVEREIGN_SHIELD_LOG_ID: Final[str] = "hu-sovereign-shield-log-2026"
SmtStatusLiteral = Literal["ACTIVE", "REVOKED", "EMPTY"]
LogKindLiteral = Literal["rfc6962", "smt-256"]


class CredentialErrorCode(str, Enum):
    """Typed verification failure codes for W3C Ma'at Verifiable Credentials (`WO-03` §2.6)."""

    INVALID_JWS_FORMAT = "INVALID_JWS_FORMAT"
    INVALID_HEADER = "INVALID_HEADER"
    FORBIDDEN_EMBEDDED_KEY = "FORBIDDEN_EMBEDDED_KEY"
    UNSUPPORTED_ALG = "UNSUPPORTED_ALG"
    INVALID_TYP = "INVALID_TYP"
    MISSING_KID = "MISSING_KID"
    UNTRUSTED_KID = "UNTRUSTED_KID"
    SIGNATURE_INVALID = "SIGNATURE_INVALID"
    PAYLOAD_NOT_CANONICAL_JCS = "PAYLOAD_NOT_CANONICAL_JCS"
    PAYLOAD_TAMPERED = "PAYLOAD_TAMPERED"
    INVALID_CREDENTIAL_ID = "INVALID_CREDENTIAL_ID"
    LEGACY_PROOF_FORBIDDEN = "LEGACY_PROOF_FORBIDDEN"
    INVALID_CONTEXT = "INVALID_CONTEXT"
    INVALID_CREDENTIAL_TYPE = "INVALID_CREDENTIAL_TYPE"
    UNTRUSTED_ISSUER = "UNTRUSTED_ISSUER"
    MISSING_VALID_FROM = "MISSING_VALID_FROM"
    MISSING_VALID_UNTIL = "MISSING_VALID_UNTIL"
    INVALID_TIMESTAMP_FORMAT = "INVALID_TIMESTAMP_FORMAT"
    INVALID_VALIDITY_WINDOW = "INVALID_VALIDITY_WINDOW"
    EXCEEDS_MAX_LIFETIME = "EXCEEDS_MAX_LIFETIME"
    MISSING_VERIFICATION_TIME = "MISSING_VERIFICATION_TIME"
    NOT_YET_VALID = "NOT_YET_VALID"
    CREDENTIAL_EXPIRED = "CREDENTIAL_EXPIRED"
    MISSING_CREDENTIAL_STATUS = "MISSING_CREDENTIAL_STATUS"
    INVALID_CREDENTIAL_STATUS = "INVALID_CREDENTIAL_STATUS"
    MISSING_STATUS_STH = "MISSING_STATUS_STH"
    UNTRUSTED_STH_KEY = "UNTRUSTED_STH_KEY"
    INVALID_STATUS_STH = "INVALID_STATUS_STH"
    STALE_STATUS_STH = "STALE_STATUS_STH"
    FUTURE_STATUS_STH = "FUTURE_STATUS_STH"
    MISSING_STATUS_PROOF = "MISSING_STATUS_PROOF"
    INVALID_STATUS_PROOF = "INVALID_STATUS_PROOF"
    CREDENTIAL_REVOKED = "CREDENTIAL_REVOKED"
    CREDENTIAL_STATUS_NOT_ACTIVE = "CREDENTIAL_STATUS_NOT_ACTIVE"
    MISSING_SUBJECT_ID = "MISSING_SUBJECT_ID"
    DOMAIN_INVARIANT_VIOLATION = "DOMAIN_INVARIANT_VIOLATION"


class MaatCredentialVerificationError(ValueError):
    """Typed exception carrying a distinct `CredentialErrorCode` (`WO-03` §2.6)."""

    def __init__(self, code: CredentialErrorCode, message: str) -> None:
        super().__init__(f"[{code.value}] {message}")
        self.code: CredentialErrorCode = code
        self.reason: str = message


class SmtSlotCollisionError(ValueError):
    """Raised when two distinct `serial_id` values map to the same SMT slot (`F-04` guard)."""

_SECP256R1_ORDER: Final[int] = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
_EMPTY_TREE_HASH: Final[bytes] = hashlib.sha256(b"").digest()
_LEAF_PREFIX: Final[bytes] = b"\x00"
_NODE_PREFIX: Final[bytes] = b"\x01"
_SHA256_BYTES: Final[int] = 32


# ============================================================================
# SECTION I — RFC 8785 JSON CANONICALIZATION SCHEME (JCS) & BASE64URL
# ============================================================================

def _assert_no_floats_recursive(value: Any, path: str = "$") -> None:
    """Recursively reject IEEE-754 floats at any depth inside a notary proof structure."""
    _jcs_assert_signable(value, path)


def jcs_canonical_bytes(value: Any) -> bytes:
    """Serialize any JSON-compatible structure into deterministic RFC 8785 UTF-8 bytes."""
    return _jcs_signable_bytes(value)


def b64url_encode(data: bytes) -> str:
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("b64url_encode requires bytes.")
    return base64.urlsafe_b64encode(bytes(data)).rstrip(b"=").decode("ascii")


def b64url_decode(token: str) -> bytes:
    if not isinstance(token, str) or not token:
        raise ValueError("b64url token must be a non-empty string.")
    if "=" in token or any(ch not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for ch in token):
        raise ValueError("b64url token must use unpadded URL-safe alphabet.")
    rem = len(token) % 4
    if rem == 1:
        raise ValueError("Invalid base64url token length (mod 4 == 1).")
    pad = "=" * ((4 - rem) % 4)
    decoded = base64.urlsafe_b64decode((token + pad).encode("ascii"))
    if b64url_encode(decoded) != token:
        raise ValueError("Non-canonical base64url padding bits rejected.")
    return decoded


# ============================================================================
# SECTION II — RFC 6962 §2.1.1 & §2.1.2 APPEND-ONLY MERKLE CONSISTENCY ENGINE
# ============================================================================

def _largest_power_of_two_less_than(n: int) -> int:
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer.")
    if n <= 1:
        return 0
    return 1 << ((n - 1).bit_length() - 1)


def rfc6962_leaf_hash(data: bytes | str) -> bytes:
    if isinstance(data, str):
        raw = data.encode("utf-8")
    elif isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
    else:
        raise TypeError(f"Leaf data must be bytes or str, got {type(data).__name__}.")
    return hashlib.sha256(_LEAF_PREFIX + raw).digest()


def rfc6962_node_hash(left: bytes, right: bytes) -> bytes:
    if not isinstance(left, bytes) or not isinstance(right, bytes) or len(left) != _SHA256_BYTES or len(right) != _SHA256_BYTES:
        raise ValueError("Internal Merkle node children must be 32-byte SHA-256 digests.")
    return hashlib.sha256(_NODE_PREFIX + left + right).digest()


def _mth_window(leaves: Sequence[bytes | str], lo: int, hi: int) -> bytes:
    """Zero-slice O(n) window computation of RFC 6962 §2.1 MTH(D[lo:hi])."""
    n = hi - lo
    if n == 0:
        return _EMPTY_TREE_HASH
    if n == 1:
        return rfc6962_leaf_hash(leaves[lo])
    k = _largest_power_of_two_less_than(n)
    left = _mth_window(leaves, lo, lo + k)
    right = _mth_window(leaves, lo + k, hi)
    return rfc6962_node_hash(left, right)


def rfc6962_merkle_tree_hash(leaves: Sequence[bytes | str]) -> bytes:
    """Compute RFC 6962 §2.1 MTH(D[n])."""
    if isinstance(leaves, (str, bytes)) or not isinstance(leaves, Sequence):
        raise TypeError("leaves must be a sequence of bytes or str.")
    return _mth_window(leaves, 0, len(leaves))


def _subproof_window(m: int, leaves: Sequence[bytes | str], lo: int, hi: int, b: bool) -> list[bytes]:
    """Zero-slice RFC 6962 §2.1.2 SUBPROOF(m, D[lo:hi], b)."""
    n = hi - lo
    if m == n:
        if b:
            return []
        return [_mth_window(leaves, lo, hi)]
    k = _largest_power_of_two_less_than(n)
    if m <= k:
        sub = _subproof_window(m, leaves, lo, lo + k, b)
        sub.append(_mth_window(leaves, lo + k, hi))
        return sub
    sub = _subproof_window(m - k, leaves, lo + k, hi, False)
    sub.append(_mth_window(leaves, lo, lo + k))
    return sub


def _coerce_sha256_root_bytes(root: bytes | str, label: str = "trusted_root") -> bytes:
    """Validate and convert a 32-byte raw digest or 64-char hex string into 32-byte SHA-256 bytes."""
    if isinstance(root, (bytes, bytearray)):
        raw = bytes(root)
        if len(raw) != _SHA256_BYTES:
            raise ValueError(f"{label} must be exactly 32 bytes (got {len(raw)} bytes).")
        return raw
    if isinstance(root, str):
        s = root.strip()
        if len(s) != 64:
            raise ValueError(f"{label} hex string must be 64 characters (got {len(s)}).")
        try:
            return bytes.fromhex(s)
        except ValueError as exc:
            raise ValueError(f"{label} is not valid hexadecimal: {exc}") from exc
    raise TypeError(f"{label} must be 32-byte bytes or 64-char hex str, got {type(root).__name__}.")


@dataclass(frozen=True)
class MerkleConsistencyProof:
    """
    RFC 6962 §2.1.2 append-only consistency proof between `old_size` m and `new_size` n.

    `claimed_old_root` and `claimed_new_root` are informational generator outputs only;
    verification (`verify_consistency`) never reads roots from the proof object (`WO-02`).
    """

    old_size: int
    new_size: int
    consistency_path_hex: tuple[str, ...]
    claimed_old_root: str = ""
    claimed_new_root: str = ""

    @property
    def old_root_hex(self) -> str:
        return self.claimed_old_root

    @property
    def new_root_hex(self) -> str:
        return self.claimed_new_root


def generate_rfc6962_consistency_proof(
    leaves: Sequence[bytes | str],
    old_size: int,
) -> MerkleConsistencyProof:
    """Prove that the first `old_size` leaves form an immutable prefix of `leaves` (`new_size`)."""
    if isinstance(leaves, (str, bytes)) or not isinstance(leaves, Sequence):
        raise TypeError("leaves must be a sequence of bytes or str.")
    n = len(leaves)
    if not isinstance(old_size, int) or isinstance(old_size, bool) or old_size < 1 or old_size > n:
        raise ValueError(f"old_size must satisfy 1 <= old_size <= {n}.")
    old_root = _mth_window(leaves, 0, old_size).hex()
    new_root = _mth_window(leaves, 0, n).hex()
    path = tuple(h.hex() for h in _subproof_window(old_size, leaves, 0, n, True))
    return MerkleConsistencyProof(
        old_size=old_size,
        new_size=n,
        consistency_path_hex=path,
        claimed_old_root=old_root,
        claimed_new_root=new_root,
    )


def verify_consistency(
    old_size: int,
    new_size: int,
    old_root: bytes | str,
    new_root: bytes | str,
    path: Sequence[bytes | str],
) -> bool:
    """
    Verify an RFC 6962 §2.1.2 / RFC 9162 §2.1.4.2 consistency proof in O(log n) (`WO-02`).

    Both `old_root` and `new_root` MUST come from Signed Tree Heads (STHs) that the
    verifier already trusts, never from the untrusted proof blob.
    When `old_size == new_size`, returns True iff `path` is empty and `old_root == new_root`.
    """
    if isinstance(old_size, bool) or isinstance(new_size, bool) or not isinstance(old_size, int) or not isinstance(new_size, int):
        return False
    if old_size < 1 or new_size < old_size:
        return False
    if isinstance(path, (str, bytes)) or not isinstance(path, Sequence):
        return False
    try:
        old_root_bytes = _coerce_sha256_root_bytes(old_root, "old_root")
        new_root_bytes = _coerce_sha256_root_bytes(new_root, "new_root")
        path_bytes = [_coerce_sha256_root_bytes(node, "path_node") for node in path]
    except (TypeError, ValueError):
        return False

    if old_size == new_size:
        return len(path_bytes) == 0 and hmac.compare_digest(old_root_bytes, new_root_bytes)

    if (old_size & (old_size - 1)) == 0:
        path_bytes = [old_root_bytes] + path_bytes

    if not path_bytes:
        return False

    fn = old_size - 1
    sn = new_size - 1
    while (fn & 1) == 1:
        fn >>= 1
        sn >>= 1

    fr = path_bytes[0]
    sr = path_bytes[0]
    for c in path_bytes[1:]:
        if sn == 0:
            return False
        if (fn & 1) == 1 or fn == sn:
            fr = rfc6962_node_hash(c, fr)
            sr = rfc6962_node_hash(c, sr)
            while (fn & 1) == 0 and fn != 0:
                fn >>= 1
                sn >>= 1
        else:
            sr = rfc6962_node_hash(sr, c)
        fn >>= 1
        sn >>= 1

    return sn == 0 and hmac.compare_digest(fr, old_root_bytes) and hmac.compare_digest(sr, new_root_bytes)


def verify_rfc6962_consistency_proof(
    proof: MerkleConsistencyProof,
    *,
    trusted_old_root: bytes | str,
    trusted_new_root: bytes | str,
) -> bool:
    """
    Verify an RFC 6962 consistency proof against caller-supplied `trusted_old_root` and `trusted_new_root` (`WO-02`).

    Never reads roots from `proof`.
    """
    if not isinstance(proof, MerkleConsistencyProof):
        return False
    return verify_consistency(
        proof.old_size,
        proof.new_size,
        trusted_old_root,
        trusted_new_root,
        proof.consistency_path_hex,
    )


def verify_inclusion(
    leaf_hash: bytes | str,
    index: int,
    tree_size: int,
    path: Sequence[bytes | str],
    *,
    trusted_root: bytes | str,
) -> bool:
    """
    Verify an RFC 9162 §2.1.3.2 / RFC 6962 §2.1.1 Merkle inclusion proof against a mandatory `trusted_root` (`WO-02`).

    `leaf_hash` is the 32-byte (or 64-hex) `MTH({d(index)}) = SHA-256(0x00 || leaf)`.
    `trusted_root` must be obtained from a verified Signed Tree Head (STH).
    """
    if isinstance(index, bool) or isinstance(tree_size, bool) or not isinstance(index, int) or not isinstance(tree_size, int):
        return False
    if tree_size < 1 or index < 0 or index >= tree_size:
        return False
    if isinstance(path, (str, bytes)) or not isinstance(path, Sequence):
        return False
    try:
        curr = _coerce_sha256_root_bytes(leaf_hash, "leaf_hash")
        root_bytes = _coerce_sha256_root_bytes(trusted_root, "trusted_root")
        path_bytes = [_coerce_sha256_root_bytes(node, "path_node") for node in path]
    except (TypeError, ValueError):
        return False

    fn = index
    sn = tree_size - 1
    for p_node in path_bytes:
        if sn == 0:
            return False
        if (fn & 1) == 1 or fn == sn:
            curr = rfc6962_node_hash(p_node, curr)
            while (fn & 1) == 0 and fn != 0:
                fn >>= 1
                sn >>= 1
        else:
            curr = rfc6962_node_hash(curr, p_node)
        fn >>= 1
        sn >>= 1

    return sn == 0 and hmac.compare_digest(curr, root_bytes)


# ============================================================================
# SECTION III — SPARSE MERKLE REVOCATION TREE (CONSTANT DEPTH H = 16)
# ============================================================================

@dataclass(frozen=True)
class VerifiedSmtStatus:
    """Typed result returned by `SparseMerkleRevocationTree.verify_status_proof` (`WO-02`)."""

    serial_id: str
    slot_index: int
    depth: int
    status: SmtStatusLiteral
    trusted_root_hex: str


class SparseMerkleRevocationTree:
    """
    Deterministic Sparse Merkle Tree of depth H (`4 <= H <= 256`, default `SMT_DEFAULT_DEPTH = 16`,
    or `SMT_COLLISION_FREE_DEPTH = 256` for full 256-bit SHA-256 addressing) proving in O(H) whether
    a Ma'at Notary Certificate Serial is ACTIVE, REVOKED, or EMPTY (`WO-02` & `F-04` collision guard).
    """

    def __init__(self, depth: int = SMT_DEFAULT_DEPTH) -> None:
        if not isinstance(depth, int) or isinstance(depth, bool) or not (4 <= depth <= 256):
            raise ValueError("depth must be an integer in [4, 256].")
        self.depth = depth
        self._default_hashes: list[bytes] = [rfc6962_leaf_hash(b"EMPTY:0")]
        for _ in range(depth):
            prev = self._default_hashes[-1]
            self._default_hashes.append(rfc6962_node_hash(prev, prev))
        self._nodes: dict[tuple[int, int], bytes] = {}
        self._statuses: dict[int, tuple[str, str]] = {}

    @staticmethod
    def compute_slot_index(serial_id: str, depth: int) -> int:
        if not isinstance(serial_id, str) or not serial_id.strip():
            raise ValueError("serial_id must be a non-empty string.")
        if isinstance(depth, bool) or not isinstance(depth, int) or not (4 <= depth <= 256):
            raise ValueError("depth must be an integer in [4, 256].")
        digest = hashlib.sha256(serial_id.encode("utf-8")).digest()
        if depth <= 32:
            val = int.from_bytes(digest[:4], "big")
            return val & ((1 << depth) - 1)
        full_val = int.from_bytes(digest, "big")
        return full_val & ((1 << depth) - 1)

    def _slot_index(self, serial_id: str) -> int:
        return self.compute_slot_index(serial_id, self.depth)

    def set_status(self, serial_id: str, status: str = "ACTIVE") -> int:
        if status not in ("ACTIVE", "REVOKED"):
            raise ValueError("status must be 'ACTIVE' or 'REVOKED'.")
        idx = self._slot_index(serial_id)
        existing = self._statuses.get(idx)
        if existing is not None and existing[0] != serial_id:
            raise SmtSlotCollisionError(
                f"SMT slot collision at index {idx} (depth={self.depth}): slot is already bound to "
                f"{existing[0]!r} ({existing[1]}) and cannot be overwritten by {serial_id!r}."
            )
        self._statuses[idx] = (serial_id, status)
        leaf_val = f"{status}:{serial_id}".encode("utf-8")
        curr_hash = rfc6962_leaf_hash(leaf_val)
        self._nodes[(0, idx)] = curr_hash
        curr_idx = idx
        for lvl in range(self.depth):
            sibling_idx = curr_idx ^ 1
            sibling_hash = self._nodes.get((lvl, sibling_idx), self._default_hashes[lvl])
            parent_idx = curr_idx >> 1
            if (curr_idx & 1) == 0:
                curr_hash = rfc6962_node_hash(curr_hash, sibling_hash)
            else:
                curr_hash = rfc6962_node_hash(sibling_hash, curr_hash)
            self._nodes[(lvl + 1, parent_idx)] = curr_hash
            curr_idx = parent_idx
        return idx

    @property
    def root_hex(self) -> str:
        return self._nodes.get((self.depth, 0), self._default_hashes[self.depth]).hex()

    @property
    def root_bytes(self) -> bytes:
        return self._nodes.get((self.depth, 0), self._default_hashes[self.depth])

    def prove_status(self, serial_id: str) -> dict[str, Any]:
        idx = self._slot_index(serial_id)
        entry = self._statuses.get(idx)
        if entry is not None and entry[0] != serial_id:
            raise SmtSlotCollisionError(
                f"Cannot prove status for {serial_id!r}: slot {idx} (depth={self.depth}) is occupied by {entry[0]!r}."
            )
        status = entry[1] if (entry is not None and entry[0] == serial_id) else "EMPTY"
        siblings: list[str] = []
        curr_idx = idx
        for lvl in range(self.depth):
            sib_idx = curr_idx ^ 1
            sib_hash = self._nodes.get((lvl, sib_idx), self._default_hashes[lvl])
            siblings.append(sib_hash.hex())
            curr_idx >>= 1
        return {
            "serial_id": serial_id,
            "slot_index": idx,
            "depth": self.depth,
            "status": status,
            "siblings_hex": siblings,
            "claimed_root": self.root_hex,
        }

    @staticmethod
    def verify_status_proof(
        proof: Mapping[str, Any],
        *,
        trusted_root: bytes | str,
        depth: int = SMT_DEFAULT_DEPTH,
    ) -> VerifiedSmtStatus:
        """
        Verify a Sparse Merkle Tree status proof against a mandatory `trusted_root` and fixed `depth` (`WO-02`).

        - Never reads any root or depth from `proof` to decide the tree geometry or target root;
          if `proof` includes `"depth"`, it must equal the verifier's `depth`.
        - Raises `ValueError` on any structural, slot, or cryptographic mismatch.
        - Returns a typed `VerifiedSmtStatus` instead of a bare `bool`.
        """
        if not isinstance(proof, Mapping):
            raise TypeError("proof must be a mapping.")
        if isinstance(depth, bool) or not isinstance(depth, int) or not (4 <= depth <= 256):
            raise ValueError("depth must be an integer in [4, 256].")
        expected_root = _coerce_sha256_root_bytes(trusted_root, "trusted_root")

        if "depth" in proof:
            proof_depth = proof["depth"]
            if isinstance(proof_depth, bool) or not isinstance(proof_depth, int) or proof_depth != depth:
                raise ValueError(f"Proof depth {proof_depth!r} does not match verifier's pinned depth {depth}.")

        serial_id_raw = proof.get("serial_id")
        if not isinstance(serial_id_raw, str) or not serial_id_raw.strip():
            raise ValueError("proof['serial_id'] must be a non-empty string.")
        serial_id = serial_id_raw
        raw_idx = proof.get("slot_index")
        raw_hex = proof.get("slot_index_hex")
        if type(raw_idx) is int:
            idx = raw_idx
        elif isinstance(raw_hex, str) and raw_hex.strip():
            idx = int(raw_hex.strip(), 16)
        else:
            raise ValueError("proof['slot_index'] must be an integer or hex string.")
        expected_idx = SparseMerkleRevocationTree.compute_slot_index(serial_id, depth)
        if idx != expected_idx:
            raise ValueError(f"SMT slot_index mismatch: got {idx}, expected {expected_idx} for {serial_id!r}.")

        status_raw = proof.get("status")
        if status_raw not in ("ACTIVE", "REVOKED", "EMPTY"):
            raise ValueError(f"Invalid SMT status {status_raw!r}; must be 'ACTIVE', 'REVOKED', or 'EMPTY'.")
        status_typed: SmtStatusLiteral = status_raw  # type: ignore[assignment]

        raw_siblings = proof.get("siblings_hex")
        if isinstance(raw_siblings, (str, bytes)) or not isinstance(raw_siblings, Sequence):
            raise ValueError("proof['siblings_hex'] must be a sequence of hex strings.")
        if len(raw_siblings) != depth:
            raise ValueError(f"SMT siblings_hex length {len(raw_siblings)} does not match pinned depth {depth}.")
        siblings = [_coerce_sha256_root_bytes(s, "sibling") for s in raw_siblings]

        if status_typed == "EMPTY":
            curr = rfc6962_leaf_hash(b"EMPTY:0")
        else:
            curr = rfc6962_leaf_hash(f"{status_typed}:{serial_id}".encode("utf-8"))
        curr_idx = idx
        for lvl in range(depth):
            sib = siblings[lvl]
            if (curr_idx & 1) == 0:
                curr = rfc6962_node_hash(curr, sib)
            else:
                curr = rfc6962_node_hash(sib, curr)
            curr_idx >>= 1
        if not hmac.compare_digest(curr, expected_root):
            raise ValueError("SMT status proof root mismatch against trusted_root.")

        return VerifiedSmtStatus(
            serial_id=serial_id,
            slot_index=idx,
            depth=depth,
            status=status_typed,
            trusted_root_hex=expected_root.hex(),
        )


def verify_status_proof(
    proof: Mapping[str, Any],
    *,
    trusted_root: bytes | str,
    depth: int = SMT_DEFAULT_DEPTH,
) -> VerifiedSmtStatus:
    """Module-level alias for `SparseMerkleRevocationTree.verify_status_proof` (`WO-02` §2.1)."""
    return SparseMerkleRevocationTree.verify_status_proof(
        proof,
        trusted_root=trusted_root,
        depth=depth,
    )


# ============================================================================
# SECTION IV — ASYMMETRIC ES256 (P-256) CREDENTIAL SIGNER PROTOCOL & W3C VC 2.0
# ============================================================================

def _der_ecdsa_to_jose_low_s(der_sig: bytes) -> bytes:
    """Convert an ASN.1 DER ECDSA P-256 signature into 64-byte JOSE `r || s` with low-S normalization (`WO-12`)."""
    return _shared_der_to_jose_es256_low_s(der_sig)


@runtime_checkable
class CredentialSigner(Protocol):
    """Protocol for asymmetric ES256 (ECDSA P-256) W3C VC-JOSE-COSE signers (`WO-01`)."""

    kid: str

    def sign(self, signing_input: bytes) -> bytes:
        """Sign `signing_input` (`ASCII(b64u(header) + '.' + b64u(payload))`) and return 64-byte `r || s`."""
        ...

    def public_jwk(self) -> dict[str, str]:
        """Return the public RFC 7517 JWK dictionary for this signer."""
        ...


class LocalEphemeralSigner:
    """
    Ephemeral in-memory ECDSA P-256 (`ES256`) signer for unit tests and self-tests (`WO-01`).

    Generates a fresh random P-256 private key at instantiation time unless an explicit
    `ec.EllipticCurvePrivateKey` is injected by a test. No secret seed or static private key
    ever resides in source code.
    """

    def __init__(
        self,
        *,
        kid: str = MAAT_VC_DEFAULT_KID,
        private_key: ec.EllipticCurvePrivateKey | None = None,
    ) -> None:
        if not isinstance(kid, str) or not kid.strip():
            raise ValueError("kid must be a non-empty string.")
        self.kid: str = kid.strip()
        self._private_key: ec.EllipticCurvePrivateKey = (
            private_key if private_key is not None else ec.generate_private_key(ec.SECP256R1())
        )

    def sign(self, signing_input: bytes) -> bytes:
        if not isinstance(signing_input, (bytes, bytearray)):
            raise TypeError("signing_input must be bytes.")
        return _shared_sign_jose_es256_low_s(self._private_key, bytes(signing_input))

    def public_jwk(self) -> dict[str, str]:
        nums = self._private_key.public_key().public_numbers()
        return {
            "kty": "EC",
            "crv": "P-256",
            "use": "sig",
            "alg": "ES256",
            "kid": self.kid,
            "x": b64url_encode(nums.x.to_bytes(32, "big")),
            "y": b64url_encode(nums.y.to_bytes(32, "big")),
        }

    def trusted_jwks(self) -> dict[str, list[dict[str, str]]]:
        return {"keys": [self.public_jwk()]}


class KmsOrEnvCredentialSigner:
    """
    Production adapter for Google Cloud KMS (`EC_SIGN_P256_SHA256`) or Secret Manager PEM (`WO-01`).

    The human provisions the production key in Cloud KMS or Secret Manager.
    - When `kms_sign_callback` is provided (or `MAAT_VC_KMS_KEY_NAME` is configured with a KMS client),
      `sign()` hashes `signing_input` with SHA-256, invokes KMS `asymmetric_sign`, and converts the
      returned ASN.1 DER ECDSA signature to 64-byte JOSE `r || s` (with low-S normalization).
    - Alternatively, loads an unencrypted PKCS#8 / EC PEM private key from the environment variable
      named in `pem_env_var` (default `MAAT_VC_ES256_PRIVATE_KEY_PEM`).
    """

    def __init__(
        self,
        *,
        kid: str = MAAT_VC_DEFAULT_KID,
        kms_key_name: str | None = None,
        kms_sign_callback: Callable[[bytes], bytes] | None = None,
        public_key_pem: str | bytes | None = None,
        pem_env_var: str = "MAAT_VC_ES256_PRIVATE_KEY_PEM",
    ) -> None:
        if not isinstance(kid, str) or not kid.strip():
            raise ValueError("kid must be a non-empty string.")
        self.kid: str = kid.strip()
        self.kms_key_name: str | None = kms_key_name or os.getenv("MAAT_VC_KMS_KEY_NAME")
        self._kms_sign_callback = kms_sign_callback
        self._private_key: ec.EllipticCurvePrivateKey | None = None
        self._public_key: ec.EllipticCurvePublicKey | None = None

        pem_raw = os.getenv(pem_env_var)
        if pem_raw:
            loaded = serialization.load_pem_private_key(pem_raw.encode("utf-8"), password=None)
            if not isinstance(loaded, ec.EllipticCurvePrivateKey):
                raise TypeError("Configured PEM private key is not an EllipticCurvePrivateKey.")
            self._private_key = loaded
            self._public_key = loaded.public_key()
        elif public_key_pem is not None:
            raw_pub = public_key_pem.encode("utf-8") if isinstance(public_key_pem, str) else bytes(public_key_pem)
            loaded_pub = serialization.load_pem_public_key(raw_pub)
            if not isinstance(loaded_pub, ec.EllipticCurvePublicKey):
                raise TypeError("Provided public_key_pem is not an EllipticCurvePublicKey.")
            self._public_key = loaded_pub

    def sign(self, signing_input: bytes) -> bytes:
        if not isinstance(signing_input, (bytes, bytearray)):
            raise TypeError("signing_input must be bytes.")
        if self._kms_sign_callback is not None:
            der_sig = self._kms_sign_callback(bytes(signing_input))
            return _der_ecdsa_to_jose_low_s(der_sig)
        if self._private_key is not None:
            return _shared_sign_jose_es256_low_s(self._private_key, bytes(signing_input))
        raise RuntimeError(
            "Production Ma'at VC signer requires either a configured Cloud KMS callback "
            "(MAAT_VC_KMS_KEY_NAME) or MAAT_VC_ES256_PRIVATE_KEY_PEM from Secret Manager."
        )

    def public_jwk(self) -> dict[str, str]:
        if self._public_key is None:
            raise RuntimeError("No public key loaded for KmsOrEnvCredentialSigner.")
        nums = self._public_key.public_numbers()
        return {
            "kty": "EC",
            "crv": "P-256",
            "use": "sig",
            "alg": "ES256",
            "kid": self.kid,
            "x": b64url_encode(nums.x.to_bytes(32, "big")),
            "y": b64url_encode(nums.y.to_bytes(32, "big")),
        }


@dataclass(frozen=True)
class VerifiedCredential:
    """Verified W3C VC 2.0 (`application/vc+jwt`) result returned after strict ES256 verification."""

    kid: str
    alg: str
    typ: str
    header: dict[str, Any]
    claims: dict[str, Any]
    payload_jcs_sha256: str
    compact_jws: str


def _parse_rfc3339_utc(ts_str: str) -> datetime:
    if not isinstance(ts_str, str) or not ts_str.strip():
        raise ValueError("Timestamp must be a non-empty RFC 3339 string.")
    s = ts_str.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        raise ValueError("Timestamp must include an explicit timezone offset or 'Z'.")
    return dt.astimezone(timezone.utc)


def _format_rfc3339_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def issue_w3c_maat_dignity_credential(
    *,
    subject_id: str,
    subject_name: str,
    dignity_score_100: int,
    merkle_root_hex: str,
    revocation_root_hex: str,
    signer: CredentialSigner,
    issuance_date_utc: str | None = None,
    valid_until_utc: str | None = None,
    serial_id: str | None = None,
    credential_uuid: str | None = None,
    max_lifetime_days: int = MAAT_VC_DEFAULT_MAX_LIFETIME_DAYS,
    cost_zero_stop: bool = True,
    eu_ai_act_art50_compliant: bool = True,
    rule14_zero_knowledge: bool = True,
    laws_verified: Sequence[str] = ("L1", "L2", "L3", "L4", "L5", "L6", "L7"),
) -> dict[str, Any]:
    """
    Issue a W3C Verifiable Credential v2.0 (`MaatHumanDignityCredential`) secured as an
    asymmetric `ES256` (`ECDSA P-256`) W3C VC-JOSE-COSE Compact JWS (`typ: "vc+jwt"`).
    """
    if not isinstance(dignity_score_100, int) or isinstance(dignity_score_100, bool) or not (0 <= dignity_score_100 <= 100):
        raise ValueError("dignity_score_100 must be an integer in [0, 100].")
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise ValueError("subject_id must be a non-empty string.")
    if not isinstance(subject_name, str) or not subject_name.strip():
        raise ValueError("subject_name must be a non-empty string.")
    if serial_id is not None and (not isinstance(serial_id, str) or not serial_id.strip()):
        raise ValueError("serial_id must be None or a non-empty string.")
    if not isinstance(signer, CredentialSigner):
        raise TypeError("signer must implement the CredentialSigner protocol (asymmetric ES256).")
    if not isinstance(signer.kid, str) or not signer.kid.strip():
        raise ValueError("signer.kid must be a non-empty string.")
    if isinstance(max_lifetime_days, bool) or not isinstance(max_lifetime_days, int) or max_lifetime_days <= 0:
        raise ValueError("max_lifetime_days must be a positive integer.")
    if not isinstance(cost_zero_stop, bool):
        raise TypeError("cost_zero_stop must be a bool.")
    if not isinstance(eu_ai_act_art50_compliant, bool):
        raise TypeError("eu_ai_act_art50_compliant must be a bool.")
    if not isinstance(rule14_zero_knowledge, bool):
        raise TypeError("rule14_zero_knowledge must be a bool.")
    laws_verified_list = [str(law) for law in laws_verified]

    try:
        m_bytes = bytes.fromhex(merkle_root_hex)
        r_bytes = bytes.fromhex(revocation_root_hex)
    except Exception as exc:
        raise ValueError(f"merkle_root_hex and revocation_root_hex must be valid hex strings: {exc}") from exc
    if len(m_bytes) != _SHA256_BYTES or len(r_bytes) != _SHA256_BYTES:
        raise ValueError("merkle_root_hex and revocation_root_hex must be 32-byte (64-hex-char) SHA-256 roots.")

    now_dt = datetime.now(timezone.utc).replace(microsecond=0)
    valid_from_dt = _parse_rfc3339_utc(issuance_date_utc) if issuance_date_utc is not None else now_dt
    valid_until_dt = (
        _parse_rfc3339_utc(valid_until_utc)
        if valid_until_utc is not None
        else (valid_from_dt + timedelta(days=max_lifetime_days))
    )
    if valid_until_dt <= valid_from_dt:
        raise ValueError("validUntil must be strictly later than validFrom.")
    if valid_until_dt - valid_from_dt > timedelta(days=max_lifetime_days):
        raise ValueError(
            f"Credential lifetime ({valid_until_dt - valid_from_dt}) exceeds maximum allowed {max_lifetime_days} days."
        )

    if credential_uuid is not None:
        vc_uuid_obj = uuid.UUID(str(credential_uuid))
        if vc_uuid_obj.version != 4:
            raise ValueError("credential_uuid must be a valid RFC 9562 UUIDv4.")
    else:
        vc_uuid_obj = uuid.uuid4()
    vc_urn = f"urn:uuid:{vc_uuid_obj}"
    effective_serial = serial_id.strip() if serial_id is not None else f"MAAT-VC-{vc_uuid_obj.hex[:12].upper()}"

    vc_claims: dict[str, Any] = {
        "@context": [
            "https://www.w3.org/ns/credentials/v2",
            MAAT_DIGNITY_JSONLD_CONTEXT_URL,
        ],
        "id": vc_urn,
        "serialNumber": effective_serial,
        "type": ["VerifiableCredential", "MaatHumanDignityCredential"],
        "issuer": {
            "id": "did:web:homouniversalis.ai",
            "name": "Homo Universalis — Viveka (Ma'at Sovereign Notary)",
            "notaryFolio": "https://homouniversalis.ai/oracle/notary",
        },
        "validFrom": _format_rfc3339_utc(valid_from_dt),
        "validUntil": _format_rfc3339_utc(valid_until_dt),
        "credentialStatus": {
            "id": f"https://homouniversalis.ai/oracle/notary#status-{effective_serial}",
            "type": "HUSparseMerkleStatus2026",
            "statusLog": "hu-maat-smt-2026",
            "serialId": effective_serial,
        },
        "credentialSubject": {
            "id": subject_id.strip(),
            "name": subject_name.strip(),
            "dignityScore100": dignity_score_100,
            "c_levels": 1,
            "cost_zero_stop": bool(cost_zero_stop),
            "lawsVerified": laws_verified_list,
            "euAiActArt50Compliant": bool(eu_ai_act_art50_compliant),
            "rule14ZeroKnowledge": bool(rule14_zero_knowledge),
            "rfc6962MerkleRoot": merkle_root_hex.lower(),
            "issuanceTimeRevocationRoot": revocation_root_hex.lower(),
        },
    }

    protected_header: dict[str, str] = {
        "alg": "ES256",
        "kid": signer.kid,
        "typ": MAAT_VC_MEDIA_TYPE,
    }
    header_bytes = jcs_canonical_bytes(protected_header)
    payload_bytes = jcs_canonical_bytes(vc_claims)
    payload_sha256 = hashlib.sha256(payload_bytes).hexdigest()

    header_b64 = b64url_encode(header_bytes)
    payload_b64 = b64url_encode(payload_bytes)
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    raw_sig = signer.sign(signing_input)
    if not isinstance(raw_sig, (bytes, bytearray)) or len(raw_sig) != 64:
        raise ValueError("CredentialSigner.sign() must return a 64-byte JOSE (r || s) ES256 signature.")
    sig_b64 = b64url_encode(bytes(raw_sig))
    compact_jws = f"{header_b64}.{payload_b64}.{sig_b64}"

    return {
        **vc_claims,
        "media_type": f"application/{MAAT_VC_MEDIA_TYPE}",
        "alg": "ES256",
        "kid": signer.kid,
        "typ": MAAT_VC_MEDIA_TYPE,
        "payload_jcs_sha256": payload_sha256,
        "compact_jws": compact_jws,
        "vc": dict(vc_claims),
    }


def _extract_trusted_ec_p256_public_key(
    trusted_jwks: Mapping[str, Any],
    kid: str,
) -> ec.EllipticCurvePublicKey:
    if not isinstance(trusted_jwks, Mapping):
        raise ValueError("trusted_jwks must be a mapping containing a 'keys' list.")
    keys = trusted_jwks.get("keys")
    if not isinstance(keys, list):
        raise ValueError("trusted_jwks['keys'] must be a list.")

    matched: Mapping[str, Any] | None = None
    for entry in keys:
        if isinstance(entry, Mapping) and entry.get("kid") == kid:
            matched = entry
            break
    if matched is None:
        raise ValueError(f"Unknown or untrusted kid {kid!r}: not present in trusted_jwks.")

    if matched.get("kty") != "EC" or matched.get("crv") != "P-256":
        raise ValueError(f"Key {kid!r} in trusted_jwks is not an EC P-256 JWK.")
    if matched.get("alg") not in (None, "ES256"):
        raise ValueError(f"Key {kid!r} in trusted_jwks does not permit ES256.")
    if matched.get("use") not in (None, "sig"):
        raise ValueError(f"Key {kid!r} in trusted_jwks is not marked for signature use ('sig').")

    x_bytes = b64url_decode(str(matched.get("x", "")))
    y_bytes = b64url_decode(str(matched.get("y", "")))
    if len(x_bytes) != 32 or len(y_bytes) != 32:
        raise ValueError(f"Key {kid!r} coordinates (x, y) must be 32 bytes each.")

    pub_nums = ec.EllipticCurvePublicNumbers(
        int.from_bytes(x_bytes, "big"),
        int.from_bytes(y_bytes, "big"),
        ec.SECP256R1(),
    )
    return pub_nums.public_key()


def _vc_err(code: CredentialErrorCode, msg: str) -> MaatCredentialVerificationError:
    return MaatCredentialVerificationError(code, msg)


def verify(
    credential_jws: str | Mapping[str, Any],
    trusted_jwks: Mapping[str, Any],
    *,
    now: datetime | str | None = None,
    expected_issuer: str = "did:web:homouniversalis.ai",
    max_lifetime_days: int = MAAT_VC_DEFAULT_MAX_LIFETIME_DAYS,
    trusted_status_sth: str | Mapping[str, Any] | SignedTreeHead | None = None,
    status_proof: Mapping[str, Any] | None = None,
    status_freshness_window_seconds: int = MAAT_STATUS_STH_FRESHNESS_WINDOW_SECONDS,
    smt_depth: int = SMT_DEFAULT_DEPTH,
    require_status_sth: bool = False,
    strict_low_s: bool = False,
) -> VerifiedCredential:
    """Strictly verify a W3C VC 2.0 (`application/vc+jwt`) compact JWS (`WO-01` & `WO-03`)."""
    embedded_status_proof: Mapping[str, Any] | None = None
    if isinstance(credential_jws, Mapping):
        if "proof" in credential_jws:
            raise _vc_err(
                CredentialErrorCode.LEGACY_PROOF_FORBIDDEN,
                "Embedded 'proof' (DataIntegrityProof / hybrid JSON proof) is forbidden; use pure VC-JOSE-COSE 'compact_jws'.",
            )
        raw_token = credential_jws.get("compact_jws")
        if not isinstance(raw_token, str) or not raw_token:
            raise _vc_err(CredentialErrorCode.INVALID_JWS_FORMAT, "Missing compact_jws string.")
        if isinstance(credential_jws.get("status_proof"), Mapping):
            embedded_status_proof = credential_jws["status_proof"]
        if "credentialSubject" in credential_jws:
            _env = {"media_type", "alg", "kid", "typ", "payload_jcs_sha256", "compact_jws", "vc", "status_proof"}
            embedded_vc: Mapping[str, Any] | None = {k: v for k, v in credential_jws.items() if k not in _env}
        else:
            embedded_vc = credential_jws.get("vc") if isinstance(credential_jws.get("vc"), Mapping) else None
    elif isinstance(credential_jws, str):
        raw_token = credential_jws
        embedded_vc = None
    else:
        raise TypeError("credential_jws must be a compact JWS string or an issued credential mapping.")

    parts = raw_token.split(".")
    if len(parts) != 3 or not all(parts):
        raise _vc_err(CredentialErrorCode.INVALID_JWS_FORMAT, "Expected three non-empty base64url segments.")
    header_b64, payload_b64, sig_b64 = parts

    try:
        header_obj = _jcs_loads(b64url_decode(header_b64))
    except Exception as exc:
        raise _vc_err(CredentialErrorCode.INVALID_HEADER, f"Malformed JWS header: {exc}") from exc
    if not isinstance(header_obj, Mapping):
        raise _vc_err(CredentialErrorCode.INVALID_HEADER, "JWS header must be a JSON object.")
    if "jwk" in header_obj:
        raise _vc_err(CredentialErrorCode.FORBIDDEN_EMBEDDED_KEY, "Embedded 'jwk' in JWS header is forbidden.")
    if header_obj.get("alg") != "ES256":
        raise _vc_err(CredentialErrorCode.UNSUPPORTED_ALG, f"Unsupported or forbidden JWS alg {header_obj.get('alg')!r}.")
    if header_obj.get("typ") != MAAT_VC_MEDIA_TYPE:
        raise _vc_err(CredentialErrorCode.INVALID_TYP, f"Invalid typ {header_obj.get('typ')!r}.")
    kid = header_obj.get("kid")
    if not isinstance(kid, str) or not kid.strip():
        raise _vc_err(CredentialErrorCode.MISSING_KID, "Missing 'kid' in JWS header.")

    try:
        pub_key = _extract_trusted_ec_p256_public_key(trusted_jwks, kid)
    except Exception as exc:
        raise _vc_err(CredentialErrorCode.UNTRUSTED_KID, str(exc)) from exc

    try:
        sig_bytes = b64url_decode(sig_b64)
    except Exception as exc:
        raise _vc_err(CredentialErrorCode.SIGNATURE_INVALID, str(exc)) from exc
    try:
        _shared_verify_jose_es256_raw(
            pub_key,
            f"{header_b64}.{payload_b64}".encode("ascii"),
            sig_bytes,
            strict_low_s=strict_low_s,
        )
    except Exception as exc:
        raise _vc_err(CredentialErrorCode.SIGNATURE_INVALID, f"ES256 signature verification failed: {exc}") from exc

    try:
        payload_bytes = b64url_decode(payload_b64)
        claims = _jcs_loads(payload_bytes)
        if not isinstance(claims, dict) or jcs_canonical_bytes(claims) != payload_bytes:
            raise ValueError("Payload is not a canonical RFC 8785 JSON object.")
    except Exception as exc:
        raise _vc_err(CredentialErrorCode.PAYLOAD_NOT_CANONICAL_JCS, str(exc)) from exc

    if embedded_vc is not None and embedded_vc != claims:
        raise _vc_err(CredentialErrorCode.PAYLOAD_TAMPERED, "Wrapper 'vc' does not match signed payload.")

    if "proof" in claims:
        raise _vc_err(
            CredentialErrorCode.LEGACY_PROOF_FORBIDDEN,
            "VC-JOSE-COSE payload must not contain an embedded 'proof' property.",
        )

    cred_id = claims.get("id")
    if not isinstance(cred_id, str) or not _URN_UUID_V4_RE.match(cred_id):
        raise _vc_err(
            CredentialErrorCode.INVALID_CREDENTIAL_ID,
            f"Credential 'id' {cred_id!r} must be a lowercase RFC 9562 UUIDv4 URN ('urn:uuid:<uuid4>').",
        )

    ctx, vtypes = claims.get("@context"), claims.get("type")
    if not isinstance(ctx, list) or "https://www.w3.org/ns/credentials/v2" not in ctx:
        raise _vc_err(CredentialErrorCode.INVALID_CONTEXT, "Missing W3C VC v2.0 '@context'.")
    if not isinstance(vtypes, list) or "VerifiableCredential" not in vtypes or "MaatHumanDignityCredential" not in vtypes:
        raise _vc_err(CredentialErrorCode.INVALID_CREDENTIAL_TYPE, "Missing required VC types.")

    issuer = claims.get("issuer")
    issuer_id = issuer.get("id") if isinstance(issuer, Mapping) else issuer
    if issuer_id != expected_issuer:
        raise _vc_err(CredentialErrorCode.UNTRUSTED_ISSUER, f"Untrusted issuer {issuer_id!r}.")

    valid_from_str, valid_until_str = claims.get("validFrom"), claims.get("validUntil")
    if not isinstance(valid_from_str, str) or not valid_from_str.strip():
        raise _vc_err(CredentialErrorCode.MISSING_VALID_FROM, "Missing validFrom.")
    if not isinstance(valid_until_str, str) or not valid_until_str.strip():
        raise _vc_err(CredentialErrorCode.MISSING_VALID_UNTIL, "Missing validUntil.")
    try:
        vf_dt, vu_dt = _parse_rfc3339_utc(valid_from_str), _parse_rfc3339_utc(valid_until_str)
    except Exception as exc:
        raise _vc_err(CredentialErrorCode.INVALID_TIMESTAMP_FORMAT, str(exc)) from exc
    if vu_dt <= vf_dt:
        raise _vc_err(CredentialErrorCode.INVALID_VALIDITY_WINDOW, "validUntil must be > validFrom.")
    if vu_dt - vf_dt > timedelta(days=max_lifetime_days):
        raise _vc_err(CredentialErrorCode.EXCEEDS_MAX_LIFETIME, f"Lifetime exceeds {max_lifetime_days} days.")

    now_dt: datetime | None = None
    if now is not None:
        try:
            now_dt = _parse_rfc3339_utc(now) if isinstance(now, str) else now.astimezone(timezone.utc)
        except Exception as exc:
            raise _vc_err(CredentialErrorCode.INVALID_TIMESTAMP_FORMAT, str(exc)) from exc
        if now_dt < vf_dt:
            raise _vc_err(CredentialErrorCode.NOT_YET_VALID, "Credential is not yet valid.")
        if now_dt >= vu_dt:
            raise _vc_err(CredentialErrorCode.CREDENTIAL_EXPIRED, "Credential has expired.")
    elif require_status_sth:
        raise _vc_err(CredentialErrorCode.MISSING_VERIFICATION_TIME, "Explicit 'now' is required.")

    cred_status = claims.get("credentialStatus")
    if not isinstance(cred_status, Mapping):
        raise _vc_err(CredentialErrorCode.MISSING_CREDENTIAL_STATUS, "Missing 'credentialStatus'.")
    status_log, status_serial = cred_status.get("statusLog"), cred_status.get("serialId")
    if (
        cred_status.get("type") != "HUSparseMerkleStatus2026"
        or not isinstance(status_log, str)
        or not status_log.strip()
        or not isinstance(status_serial, str)
        or not status_serial.strip()
        or ("serialNumber" in claims and claims["serialNumber"] != status_serial)
    ):
        raise _vc_err(CredentialErrorCode.INVALID_CREDENTIAL_STATUS, "Invalid credentialStatus fields.")

    if require_status_sth or trusted_status_sth is not None:
        if trusted_status_sth is None:
            raise _vc_err(CredentialErrorCode.MISSING_STATUS_STH, "Missing trusted_status_sth.")
        try:
            verified_sth = verify_signed_tree_head(
                trusted_status_sth,
                trusted_jwks,
                expected_log_id=status_log,
                expected_kind="smt-256",
                strict_low_s=strict_low_s,
            )
        except Exception as exc:
            code = (
                CredentialErrorCode.UNTRUSTED_STH_KEY
                if ("not present in trusted_jwks" in str(exc) or "signature" in str(exc))
                else CredentialErrorCode.INVALID_STATUS_STH
            )
            raise _vc_err(code, str(exc)) from exc

        if now_dt is not None:
            age_ms = int(now_dt.timestamp() * 1000) - verified_sth.timestamp_ms
            if age_ms < 0:
                raise _vc_err(CredentialErrorCode.FUTURE_STATUS_STH, "Status STH is in the future.")
            if age_ms > status_freshness_window_seconds * 1000:
                raise _vc_err(CredentialErrorCode.STALE_STATUS_STH, "Status STH is stale.")

        eff_proof = status_proof or embedded_status_proof
        if eff_proof is None and isinstance(trusted_status_sth, Mapping) and isinstance(trusted_status_sth.get("status_proof"), Mapping):
            eff_proof = trusted_status_sth["status_proof"]
        if eff_proof is None:
            raise _vc_err(CredentialErrorCode.MISSING_STATUS_PROOF, "Missing status_proof.")
        if eff_proof.get("serial_id") != status_serial:
            raise _vc_err(CredentialErrorCode.INVALID_STATUS_PROOF, "status_proof serial_id mismatch.")
        try:
            verified_status = SparseMerkleRevocationTree.verify_status_proof(
                eff_proof, trusted_root=verified_sth.root_bytes, depth=smt_depth
            )
        except Exception as exc:
            raise _vc_err(CredentialErrorCode.INVALID_STATUS_PROOF, str(exc)) from exc
        if verified_status.status == "REVOKED":
            raise _vc_err(CredentialErrorCode.CREDENTIAL_REVOKED, f"Credential {status_serial!r} is REVOKED.")
        if verified_status.status != "ACTIVE":
            raise _vc_err(CredentialErrorCode.CREDENTIAL_STATUS_NOT_ACTIVE, f"Status is {verified_status.status!r}.")

    subj = claims.get("credentialSubject")
    if not isinstance(subj, Mapping) or not isinstance(subj.get("id"), str) or not subj["id"].strip():
        raise _vc_err(CredentialErrorCode.MISSING_SUBJECT_ID, "Missing credentialSubject.id.")
    c_lvl = subj.get("c_levels")
    if isinstance(c_lvl, bool) or c_lvl != 1 or subj.get("cost_zero_stop") is not True:
        raise _vc_err(CredentialErrorCode.DOMAIN_INVARIANT_VIOLATION, "Law L1/L2 violation in credentialSubject.")

    return VerifiedCredential(
        kid=kid,
        alg="ES256",
        typ=MAAT_VC_MEDIA_TYPE,
        header=dict(header_obj),
        claims=claims,
        payload_jcs_sha256=hashlib.sha256(payload_bytes).hexdigest(),
        compact_jws=raw_token,
    )


def verify_maat_credential(
    jws: str | Mapping[str, Any],
    *,
    trusted_jwks: Mapping[str, Any],
    trusted_status_sth: str | Mapping[str, Any] | SignedTreeHead,
    now: datetime | str,
    status_proof: Mapping[str, Any] | None = None,
    expected_issuer: str = "did:web:homouniversalis.ai",
    max_lifetime_days: int = MAAT_VC_DEFAULT_MAX_LIFETIME_DAYS,
    status_freshness_window_seconds: int = MAAT_STATUS_STH_FRESHNESS_WINDOW_SECONDS,
    smt_depth: int = SMT_DEFAULT_DEPTH,
    strict_low_s: bool = False,
) -> VerifiedCredential:
    """
    Canonical W3C Ma'at Verifiable Credential policy verifier (`WO-03` §2 & `WO-12` §2.2).

    Requires and enforces:
      1. Compact JWS signature & protected header (`alg == "ES256"`, `kid` in `trusted_jwks`, `typ == "vc+jwt"`).
      2. `issuer == expected_issuer`.
      3. `validFrom <= now < validUntil` (strict UTC RFC 3339, mandatory `validUntil`, max lifetime `365` days).
      4. `credentialStatus` (`HUSparseMerkleStatus2026`) verified against a signed `trusted_status_sth`
         no older than `status_freshness_window_seconds` (`24 h` default) and a valid `status_proof`
         proving `status == "ACTIVE"`. Never uses embedded `sparseRevocationRoot` or `issuanceTimeRevocationRoot`.
      5. `credentialSubject.id` present, `c_levels == 1`, `cost_zero_stop is True`.
      6. Raises `MaatCredentialVerificationError` with a distinct `CredentialErrorCode` on any failure.
    """
    return verify(
        jws,
        trusted_jwks,
        now=now,
        expected_issuer=expected_issuer,
        max_lifetime_days=max_lifetime_days,
        trusted_status_sth=trusted_status_sth,
        status_proof=status_proof,
        status_freshness_window_seconds=status_freshness_window_seconds,
        smt_depth=smt_depth,
        require_status_sth=True,
        strict_low_s=strict_low_s,
    )


def verify_w3c_maat_dignity_credential(
    credential_or_jws: str | Mapping[str, Any],
    trusted_jwks: Mapping[str, Any],
    *,
    now: datetime | str | None = None,
    expected_issuer: str = "did:web:homouniversalis.ai",
    trusted_status_sth: str | Mapping[str, Any] | SignedTreeHead | None = None,
    status_proof: Mapping[str, Any] | None = None,
    strict_low_s: bool = False,
) -> bool:
    """Boolean wrapper around `verify()` returning True iff the ES256 W3C VC-JOSE-COSE credential is valid."""
    try:
        verify(
            credential_or_jws,
            trusted_jwks,
            now=now,
            expected_issuer=expected_issuer,
            trusted_status_sth=trusted_status_sth,
            status_proof=status_proof,
            strict_low_s=strict_low_s,
        )
        return True
    except Exception:
        return False


# ============================================================================
# SECTION V — SIGNED TREE HEADS (STH) & TRUSTED LOG STATE ANCHOR (WO-02)
# ============================================================================

@dataclass(frozen=True)
class SignedTreeHead:
    """
    Verified Signed Tree Head (STH) for an RFC 6962 or Sparse Merkle log (`WO-02` §2.2).

    Canonical JCS payload fields:
      `{"kind": "rfc6962" | "smt-256", "log_id": str, "root_hash": hex, "timestamp_ms": int, "tree_size": int}`
    Signed as an `ES256` Compact JWS (`typ: "sth+jwt"`) with a log-specific `kid`.
    """

    log_id: str
    tree_size: int
    root_hash: str
    timestamp_ms: int
    kind: LogKindLiteral
    kid: str
    compact_jws: str
    payload_jcs_sha256: str

    @property
    def root_bytes(self) -> bytes:
        return bytes.fromhex(self.root_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "log_id": self.log_id,
            "tree_size": self.tree_size,
            "root_hash": self.root_hash,
            "timestamp_ms": self.timestamp_ms,
            "kind": self.kind,
            "kid": self.kid,
            "alg": "ES256",
            "typ": LOG_STH_MEDIA_TYPE,
            "payload_jcs_sha256": self.payload_jcs_sha256,
            "compact_jws": self.compact_jws,
        }


def issue_signed_tree_head(
    *,
    log_id: str,
    tree_size: int,
    root_hash: bytes | str,
    timestamp_ms: int,
    kind: LogKindLiteral,
    signer: CredentialSigner,
) -> SignedTreeHead:
    """
    Issue a canonical RFC 8785 (JCS) + ES256 Signed Tree Head (`SignedTreeHead`) (`WO-02` §2.2).
    """
    if not isinstance(log_id, str) or not log_id.strip():
        raise ValueError("log_id must be a non-empty string.")
    if isinstance(tree_size, bool) or not isinstance(tree_size, int) or tree_size < 0:
        raise ValueError("tree_size must be a non-negative integer.")
    if isinstance(timestamp_ms, bool) or not isinstance(timestamp_ms, int) or timestamp_ms <= 0:
        raise ValueError("timestamp_ms must be a positive integer.")
    if kind not in ("rfc6962", "smt-256"):
        raise ValueError("kind must be 'rfc6962' or 'smt-256'.")
    if not isinstance(signer, CredentialSigner):
        raise TypeError("signer must implement CredentialSigner.")

    root_bytes = _coerce_sha256_root_bytes(root_hash, "root_hash")
    root_hex = root_bytes.hex()

    sth_payload: dict[str, Any] = {
        "kind": kind,
        "log_id": log_id.strip(),
        "root_hash": root_hex,
        "timestamp_ms": timestamp_ms,
        "tree_size": tree_size,
    }
    protected_header: dict[str, str] = {
        "alg": "ES256",
        "kid": signer.kid,
        "typ": LOG_STH_MEDIA_TYPE,
    }
    header_bytes = jcs_canonical_bytes(protected_header)
    payload_bytes = jcs_canonical_bytes(sth_payload)
    payload_sha256 = hashlib.sha256(payload_bytes).hexdigest()

    header_b64 = b64url_encode(header_bytes)
    payload_b64 = b64url_encode(payload_bytes)
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    raw_sig = signer.sign(signing_input)
    if not isinstance(raw_sig, (bytes, bytearray)) or len(raw_sig) != 64:
        raise ValueError("CredentialSigner.sign() must return 64-byte JOSE (r || s) ES256 signature.")
    sig_b64 = b64url_encode(bytes(raw_sig))
    compact_jws = f"{header_b64}.{payload_b64}.{sig_b64}"

    return SignedTreeHead(
        log_id=log_id.strip(),
        tree_size=tree_size,
        root_hash=root_hex,
        timestamp_ms=timestamp_ms,
        kind=kind,
        kid=signer.kid,
        compact_jws=compact_jws,
        payload_jcs_sha256=payload_sha256,
    )


def verify_signed_tree_head(
    sth_or_jws: str | Mapping[str, Any] | SignedTreeHead,
    trusted_jwks: Mapping[str, Any],
    *,
    expected_log_id: str | None = None,
    expected_kind: LogKindLiteral | None = None,
    strict_low_s: bool = False,
) -> SignedTreeHead:
    """Strictly verify a Signed Tree Head (STH) compact JWS against `trusted_jwks` (`WO-02` §2.2 & §2.4)."""
    wrapper_obj: Mapping[str, Any] | None = None
    if isinstance(sth_or_jws, SignedTreeHead):
        raw_token, wrapper_obj = sth_or_jws.compact_jws, sth_or_jws.to_dict()
    elif isinstance(sth_or_jws, Mapping):
        tok = sth_or_jws.get("compact_jws")
        if not isinstance(tok, str) or not tok:
            raise ValueError("STH mapping is missing 'compact_jws'.")
        raw_token, wrapper_obj = tok, sth_or_jws
    elif isinstance(sth_or_jws, str):
        raw_token = sth_or_jws
    else:
        raise TypeError("sth_or_jws must be a compact JWS string, mapping, or SignedTreeHead.")

    parts = raw_token.split(".")
    if len(parts) != 3 or not all(parts):
        raise ValueError("Invalid STH compact JWS format.")
    header_b64, payload_b64, sig_b64 = parts
    header_obj = _jcs_loads(b64url_decode(header_b64))
    if not isinstance(header_obj, Mapping) or "jwk" in header_obj:
        raise ValueError("Invalid STH JWS header or forbidden embedded 'jwk'.")
    if header_obj.get("alg") != "ES256" or header_obj.get("typ") != LOG_STH_MEDIA_TYPE:
        raise ValueError("Unsupported STH JWS alg or typ.")
    kid = header_obj.get("kid")
    if not isinstance(kid, str) or not kid.strip():
        raise ValueError("STH JWS header is missing a valid 'kid'.")

    pub_key = _extract_trusted_ec_p256_public_key(trusted_jwks, kid)
    sig_bytes = b64url_decode(sig_b64)
    try:
        _shared_verify_jose_es256_raw(
            pub_key,
            f"{header_b64}.{payload_b64}".encode("ascii"),
            sig_bytes,
            strict_low_s=strict_low_s,
        )
    except Exception as exc:
        raise ValueError(f"STH ES256 signature verification failed: {exc}") from exc

    payload_bytes = b64url_decode(payload_b64)
    payload_obj = _jcs_loads(payload_bytes)
    if not isinstance(payload_obj, dict):
        raise ValueError("STH payload must be a JSON object.")
    if jcs_canonical_bytes(payload_obj) != payload_bytes:
        raise ValueError("STH payload bytes are not in canonical RFC 8785 (JCS) form.")

    if set(payload_obj.keys()) != {"kind", "log_id", "root_hash", "timestamp_ms", "tree_size"}:
        raise ValueError(f"Unexpected keys in STH payload: {sorted(payload_obj.keys())}.")

    log_id = payload_obj["log_id"]
    tree_size = payload_obj["tree_size"]
    timestamp_ms = payload_obj["timestamp_ms"]
    kind = payload_obj["kind"]
    if not isinstance(log_id, str) or not log_id.strip():
        raise ValueError("STH log_id must be a non-empty string.")
    if isinstance(tree_size, bool) or not isinstance(tree_size, int) or tree_size < 0:
        raise ValueError("STH tree_size must be a non-negative integer.")
    if isinstance(timestamp_ms, bool) or not isinstance(timestamp_ms, int) or timestamp_ms <= 0:
        raise ValueError("STH timestamp_ms must be a positive integer.")
    if kind not in ("rfc6962", "smt-256"):
        raise ValueError("STH kind must be 'rfc6962' or 'smt-256'.")
    root_hex = _coerce_sha256_root_bytes(payload_obj["root_hash"], "STH root_hash").hex()
    if expected_log_id is not None and log_id != expected_log_id:
        raise ValueError(f"STH log_id {log_id!r} != {expected_log_id!r}.")
    if expected_kind is not None and kind != expected_kind:
        raise ValueError(f"STH kind {kind!r} != {expected_kind!r}.")
    if wrapper_obj is not None:
        for k, v in (("log_id", log_id), ("tree_size", tree_size), ("root_hash", root_hex), ("timestamp_ms", timestamp_ms), ("kind", kind)):
            if k in wrapper_obj and wrapper_obj[k] != v:
                raise ValueError(f"STH wrapper field {k!r} was tampered.")

    return SignedTreeHead(
        log_id=log_id,
        tree_size=tree_size,
        root_hash=root_hex,
        timestamp_ms=timestamp_ms,
        kind=kind,  # type: ignore[arg-type]
        kid=kid,
        compact_jws=raw_token,
        payload_jcs_sha256=hashlib.sha256(payload_bytes).hexdigest(),
    )


class TrustedLogState:
    """
    Stateful verifier anchor tracking the latest verified `SignedTreeHead` per `log_id` (`WO-02` §3).

    Enforces:
    1. Every STH is cryptographically verified against `trusted_jwks`.
    2. Monotonic `tree_size` (`new.tree_size >= old.tree_size`) and monotonic `timestamp_ms`.
    3. For `"rfc6962"` append-only logs:
       - If `old.tree_size == new.tree_size`, requires `old.root_hash == new.root_hash` and an empty consistency path.
       - If `new.tree_size > old.tree_size` (and `old.tree_size >= 1`), requires a valid RFC 6962 consistency
         proof linking `old.root_bytes` to `new.root_bytes` before advancing the state.
    """

    def __init__(self, trusted_jwks: Mapping[str, Any]) -> None:
        if not isinstance(trusted_jwks, Mapping):
            raise TypeError("trusted_jwks must be a mapping.")
        self._trusted_jwks = trusted_jwks
        self._heads: dict[str, SignedTreeHead] = {}

    def get_sth(self, log_id: str) -> SignedTreeHead:
        if log_id not in self._heads:
            raise KeyError(f"No verified SignedTreeHead anchored for log_id {log_id!r}.")
        return self._heads[log_id]

    def trusted_root_bytes(self, log_id: str) -> bytes:
        return self.get_sth(log_id).root_bytes

    def update(
        self,
        candidate_sth: str | Mapping[str, Any] | SignedTreeHead,
        *,
        consistency_path: Sequence[bytes | str] | None = None,
    ) -> SignedTreeHead:
        verified_new = verify_signed_tree_head(candidate_sth, self._trusted_jwks)
        old = self._heads.get(verified_new.log_id)
        if old is None:
            self._heads[verified_new.log_id] = verified_new
            return verified_new

        if verified_new.kind != old.kind or verified_new.tree_size < old.tree_size or verified_new.timestamp_ms < old.timestamp_ms:
            raise ValueError(f"Rollback detected or Timestamp rollback detected on log {verified_new.log_id!r}.")
        if verified_new.kind == "rfc6962" and old.tree_size >= 1:
            if not verify_consistency(
                old.tree_size, verified_new.tree_size, old.root_bytes, verified_new.root_bytes, consistency_path or ()
            ):
                raise ValueError(f"RFC 6962 consistency proof failed for log {verified_new.log_id!r}.")

        self._heads[verified_new.log_id] = verified_new
        return verified_new


def _audit_path_window(index: int, leaves: Sequence[bytes | str], lo: int, hi: int) -> list[bytes]:
    """Zero-slice RFC 6962 §2.1.1 PATH(index, D[lo:hi]) audit inclusion path."""
    n = hi - lo
    if n <= 1:
        return []
    k = _largest_power_of_two_less_than(n)
    if index < k:
        sub = _audit_path_window(index, leaves, lo, lo + k)
        sub.append(_mth_window(leaves, lo + k, hi))
        return sub
    sub = _audit_path_window(index - k, leaves, lo + k, hi)
    sub.append(_mth_window(leaves, lo, lo + k))
    return sub


class AppendOnlyMerkleTransparencyLog:
    """
    Thread-safe RFC 6962 append-only transparency log anchored by ES256 Signed Tree Heads (`WO-13` §2.3 & §5).

    Guarantees:
    - Strictly append-only: leaves keep their `leaf_index` (`0 .. tree_size - 1`) forever; leaves are never deleted or overwritten.
    - Monotonic `tree_size` (`n -> n + 1`) and strictly monotonic `timestamp_ms`.
    - Stores signed `SignedTreeHead` snapshots by `tree_size` so any auditor can fetch earlier STHs
      and verify `verify_consistency(old_size, new_size, old_sth.root_bytes, new_sth.root_bytes, path)`.
    - Bounded memory capacity (`max_leaves`, default `4096`): refuses further appends with `OverflowError`
      rather than evicting historical leaves (which would violate append-only transparency).
    """

    def __init__(
        self,
        *,
        log_id: str = SOVEREIGN_SHIELD_LOG_ID,
        founding_leaves: Sequence[bytes | str],
        signer: CredentialSigner,
        max_leaves: int = 4096,
    ) -> None:
        if not isinstance(log_id, str) or not log_id.strip():
            raise ValueError("log_id must be a non-empty string.")
        if isinstance(founding_leaves, (str, bytes)) or not isinstance(founding_leaves, Sequence) or len(founding_leaves) < 1:
            raise ValueError("founding_leaves must be a non-empty sequence of bytes or str.")
        if not isinstance(signer, CredentialSigner):
            raise TypeError("signer must implement CredentialSigner.")
        if isinstance(max_leaves, bool) or not isinstance(max_leaves, int) or max_leaves < len(founding_leaves):
            raise ValueError("max_leaves must be an integer >= len(founding_leaves).")

        self._lock = threading.Lock()
        self.log_id: str = log_id.strip()
        self._signer: CredentialSigner = signer
        self.max_leaves: int = max_leaves
        self._leaves: list[bytes] = [
            leaf.encode("utf-8") if isinstance(leaf, str) else bytes(leaf)
            for leaf in founding_leaves
        ]
        now_ms = max(1, int(time.time() * 1000))
        self._last_ts_ms: int = now_ms
        initial_root = _mth_window(self._leaves, 0, len(self._leaves))
        initial_sth = issue_signed_tree_head(
            log_id=self.log_id,
            tree_size=len(self._leaves),
            root_hash=initial_root,
            timestamp_ms=now_ms,
            kind="rfc6962",
            signer=self._signer,
        )
        self._sths_by_size: dict[int, SignedTreeHead] = {len(self._leaves): initial_sth}

    @property
    def signer_kid(self) -> str:
        return self._signer.kid

    def public_jwk(self) -> dict[str, str]:
        return self._signer.public_jwk()

    @property
    def current_tree_size(self) -> int:
        with self._lock:
            return len(self._leaves)

    def current_sth(self) -> SignedTreeHead:
        with self._lock:
            return self._sths_by_size[len(self._leaves)]

    def available_sizes(self) -> list[int]:
        with self._lock:
            return sorted(self._sths_by_size.keys())

    def _ensure_sth_locked(self, size: int) -> SignedTreeHead:
        if size < 1 or size > len(self._leaves):
            raise ValueError(f"Requested tree_size {size} out of range [1, {len(self._leaves)}].")
        existing = self._sths_by_size.get(size)
        if existing is not None:
            return existing
        # Deterministic historical prefix root signed at monotonic timestamp if an intermediate prefix was never checkpointed
        prefix_root = _mth_window(self._leaves, 0, size)
        now_ms = max(self._last_ts_ms + 1, int(time.time() * 1000))
        self._last_ts_ms = now_ms
        minted = issue_signed_tree_head(
            log_id=self.log_id,
            tree_size=size,
            root_hash=prefix_root,
            timestamp_ms=now_ms,
            kind="rfc6962",
            signer=self._signer,
        )
        self._sths_by_size[size] = minted
        return minted

    def get_sth(self, tree_size: int | None = None) -> SignedTreeHead:
        with self._lock:
            target = len(self._leaves) if tree_size is None else tree_size
            if isinstance(target, bool) or not isinstance(target, int):
                raise ValueError("tree_size must be an integer.")
            return self._ensure_sth_locked(target)

    def prove_inclusion_at(self, leaf_index: int | None = None, tree_size: int | None = None) -> dict[str, Any]:
        """Read-only inclusion proof against the signed STH at `tree_size` (never mutates log state)."""
        with self._lock:
            eff_size = len(self._leaves) if tree_size is None else tree_size
            if isinstance(eff_size, bool) or not isinstance(eff_size, int) or eff_size < 1 or eff_size > len(self._leaves):
                raise ValueError(f"tree_size must be in [1, {len(self._leaves)}].")
            eff_idx = (eff_size - 1) if leaf_index is None else leaf_index
            if isinstance(eff_idx, bool) or not isinstance(eff_idx, int) or eff_idx < 0 or eff_idx >= eff_size:
                raise ValueError(f"leaf_index must be in [0, {eff_size - 1}].")
            sth = self._ensure_sth_locked(eff_size)
            leaf_bytes = self._leaves[eff_idx]
            leaf_hash_hex = rfc6962_leaf_hash(leaf_bytes).hex()
            audit_path_hex = [h.hex() for h in _audit_path_window(eff_idx, self._leaves, 0, eff_size)]
            self_check = verify_inclusion(
                leaf_hash_hex,
                eff_idx,
                eff_size,
                audit_path_hex,
                trusted_root=sth.root_bytes,
            )
            return {
                "log_id": self.log_id,
                "leaf_bytes": leaf_bytes,
                "leaf_hash": leaf_hash_hex,
                "leaf_index": eff_idx,
                "tree_size": eff_size,
                "root_hash": sth.root_hash,
                "audit_path": audit_path_hex,
                "signed_tree_head": sth.to_dict(),
                "inclusion_self_check_passed": self_check,
            }

    def prove_consistency_between(self, old_size: int, new_size: int | None = None) -> dict[str, Any]:
        """Read-only RFC 6962 §2.1.2 consistency proof between two signed STHs (`1 <= old_size <= new_size`)."""
        with self._lock:
            eff_new = len(self._leaves) if new_size is None else new_size
            if (
                isinstance(old_size, bool)
                or isinstance(eff_new, bool)
                or not isinstance(old_size, int)
                or not isinstance(eff_new, int)
            ):
                raise ValueError("old_size and new_size must be integers.")
            if old_size < 1 or eff_new < old_size or eff_new > len(self._leaves):
                raise ValueError(f"Require 1 <= old_size <= new_size <= {len(self._leaves)}.")
            old_sth = self._ensure_sth_locked(old_size)
            new_sth = self._ensure_sth_locked(eff_new)
            c_proof = generate_rfc6962_consistency_proof(self._leaves[:eff_new], old_size=old_size)
            c_ok = verify_consistency(
                old_size,
                eff_new,
                old_sth.root_bytes,
                new_sth.root_bytes,
                c_proof.consistency_path_hex,
            )
            return {
                "log_id": self.log_id,
                "old_size": old_size,
                "new_size": eff_new,
                "consistency_path_hex": list(c_proof.consistency_path_hex),
                "old_signed_tree_head": old_sth.to_dict(),
                "new_signed_tree_head": new_sth.to_dict(),
                "consistency_self_check_passed": c_ok,
            }

    def append_leaf(self, data: bytes | str) -> dict[str, Any]:
        """
        Append one leaf monotonically (`n -> n + 1`), mint a new `SignedTreeHead`, and return both
        the RFC 6962 inclusion proof at index `n` and the consistency proof from `n` to `n + 1`.
        """
        raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
        with self._lock:
            if len(self._leaves) >= self.max_leaves:
                raise OverflowError(
                    f"Append-only log {self.log_id!r} reached in-memory capacity ({self.max_leaves} leaves)."
                )
            prev_size = len(self._leaves)
            prev_sth = self._ensure_sth_locked(prev_size)
            self._leaves.append(raw)
            new_size = len(self._leaves)
            leaf_idx = new_size - 1
            new_root = _mth_window(self._leaves, 0, new_size)
            now_ms = max(self._last_ts_ms + 1, int(time.time() * 1000))
            self._last_ts_ms = now_ms
            new_sth = issue_signed_tree_head(
                log_id=self.log_id,
                tree_size=new_size,
                root_hash=new_root,
                timestamp_ms=now_ms,
                kind="rfc6962",
                signer=self._signer,
            )
            self._sths_by_size[new_size] = new_sth
            leaf_hash_hex = rfc6962_leaf_hash(raw).hex()
            audit_path_hex = [h.hex() for h in _audit_path_window(leaf_idx, self._leaves, 0, new_size)]
            inc_ok = verify_inclusion(
                leaf_hash_hex,
                leaf_idx,
                new_size,
                audit_path_hex,
                trusted_root=new_sth.root_bytes,
            )
            c_proof = generate_rfc6962_consistency_proof(self._leaves, old_size=prev_size)
            cons_ok = verify_consistency(
                prev_size,
                new_size,
                prev_sth.root_bytes,
                new_sth.root_bytes,
                c_proof.consistency_path_hex,
            )
            return {
                "log_id": self.log_id,
                "leaf_hash": leaf_hash_hex,
                "leaf_index": leaf_idx,
                "tree_size": new_size,
                "root_hash": new_sth.root_hash,
                "audit_path": audit_path_hex,
                "signed_tree_head": new_sth.to_dict(),
                "previous_signed_tree_head": prev_sth.to_dict(),
                "consistency_proof": {
                    "log_id": self.log_id,
                    "old_size": prev_size,
                    "new_size": new_size,
                    "consistency_path_hex": list(c_proof.consistency_path_hex),
                    "consistency_self_check_passed": cons_ok,
                },
                "inclusion_self_check_passed": inc_ok,
            }


def run_folio_iv_self_test() -> dict[str, Any]:
    """
    Ephemeral self-test for Living Folio IV (< 2 ms, 0 network calls).

    Uses fresh random P-256 `LocalEphemeralSigner` instances on every invocation so no static key
    lives in source code, and anchors all Merkle/SMT verifications to signed STHs via `TrustedLogState` (`WO-02`).
    """
    ephemeral_vc_signer = LocalEphemeralSigner(kid="maat-vc-es256-selftest-ephemeral")
    ephemeral_sth_signer = LocalEphemeralSigner(kid="hu-log-sth-es256-selftest-ephemeral")
    combined_jwks = {"keys": [ephemeral_vc_signer.public_jwk(), ephemeral_sth_signer.public_jwk()]}
    log_state = TrustedLogState(combined_jwks)
    selftest_now_dt = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc)
    selftest_now_ms = int(selftest_now_dt.timestamp() * 1000)

    leaves = [f"MAAT-LEAF-{i}" for i in range(1, 10)]
    sth_old = issue_signed_tree_head(
        log_id=MAAT_GOLDEN_BOOK_LOG_ID,
        tree_size=5,
        root_hash=rfc6962_merkle_tree_hash(leaves[:5]),
        timestamp_ms=selftest_now_ms - 2000,
        kind="rfc6962",
        signer=ephemeral_sth_signer,
    )
    sth_new = issue_signed_tree_head(
        log_id=MAAT_GOLDEN_BOOK_LOG_ID,
        tree_size=9,
        root_hash=rfc6962_merkle_tree_hash(leaves),
        timestamp_ms=selftest_now_ms - 1000,
        kind="rfc6962",
        signer=ephemeral_sth_signer,
    )
    c_proof = generate_rfc6962_consistency_proof(leaves, old_size=5)
    log_state.update(sth_old)
    log_state.update(sth_new, consistency_path=c_proof.consistency_path_hex)
    c_ok = verify_consistency(
        5,
        9,
        sth_old.root_bytes,
        log_state.trusted_root_bytes(MAAT_GOLDEN_BOOK_LOG_ID),
        c_proof.consistency_path_hex,
    )

    smt = SparseMerkleRevocationTree(depth=SMT_DEFAULT_DEPTH)
    smt.set_status("MAAT-VC-2026-0001", "ACTIVE")
    smt.set_status("MAAT-VC-2026-0002", "REVOKED")
    sth_smt = issue_signed_tree_head(
        log_id=MAAT_SMT_REVOCATION_LOG_ID,
        tree_size=2,
        root_hash=smt.root_bytes,
        timestamp_ms=selftest_now_ms - 1000,
        kind="smt-256",
        signer=ephemeral_sth_signer,
    )
    log_state.update(sth_smt)
    trusted_smt_root = log_state.trusted_root_bytes(MAAT_SMT_REVOCATION_LOG_ID)

    p_active = smt.prove_status("MAAT-VC-2026-0001")
    smt_ok = (
        SparseMerkleRevocationTree.verify_status_proof(p_active, trusted_root=trusted_smt_root).status == "ACTIVE"
        and SparseMerkleRevocationTree.verify_status_proof(
            smt.prove_status("MAAT-VC-2026-0002"), trusted_root=trusted_smt_root
        ).status
        == "REVOKED"
    )

    vc = issue_w3c_maat_dignity_credential(
        subject_id="https://homouniversalis.ai",
        subject_name="Homo Universalis — Viveka",
        dignity_score_100=100,
        merkle_root_hex=sth_new.root_hash,
        revocation_root_hex=sth_smt.root_hash,
        signer=ephemeral_vc_signer,
        issuance_date_utc="2026-11-10T00:00:00Z",
        valid_until_utc="2027-11-10T00:00:00Z",
        serial_id="MAAT-VC-2026-0001",
    )
    vc_ok = (
        verify_maat_credential(
            vc,
            trusted_jwks=combined_jwks,
            trusted_status_sth=sth_smt,
            status_proof=p_active,
            now=selftest_now_dt,
        ).alg
        == "ES256"
    )

    return {
        "folio_id": FOLIO_IV_ID,
        "self_test_only": True,
        "note": (
            "In-memory invariant self-test executed with a fresh per-run random P-256 ephemeral key "
            "(not a production credential)."
        ),
        "all_invariants_passed": bool(c_ok and smt_ok and vc_ok),
        "rfc6962_consistency_verified": c_ok,
        "sparse_merkle_revocation_verified": smt_ok,
        "w3c_vc_verified": vc_ok,
        "vc_alg": "ES256",
        "vc_typ": MAAT_VC_MEDIA_TYPE,
        "ephemeral_kid": ephemeral_vc_signer.kid,
        "ephemeral_public_jwk_x": ephemeral_vc_signer.public_jwk()["x"],
        "ephemeral_sth_kid": ephemeral_sth_signer.kid,
        "merkle_root_hex": sth_new.root_hash,
        "revocation_root_hex": sth_smt.root_hash,
    }
