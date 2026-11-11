# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
Shared JOSE ES256 (ECDSA P-256 + SHA-256) signing and verification helpers (`WO-12`).

Implements:
- Canonical low-S normalization (`s = n - s` whenever `s > n // 2`) before encoding
  64-byte JOSE `r || s` signatures, eliminating ECDSA `(r, n - s)` malleability so
  emitted signature bytes are canonical identifiers for caches, logs, and deduplication.
- Standard RFC 7515 / RFC 7518 JWS verification (`strict_low_s=False` by default,
  accepting all valid `1 <= s < n` signatures for external JWS interoperability)
  plus `strict_low_s=True` for internal callers that require canonical low-S bytes.
- Honest public `JOSE_ES256_STANDARD` descriptor (`RFC 8785 (JCS) + RFC 7515 (JWS) + RFC 7518 ES256`)
  without unobservable or KMS-incompatible RFC 6979 claims.
"""

from __future__ import annotations

from typing import Final

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)

SECP256R1_ORDER: Final[int] = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
SECP256R1_HALF_ORDER: Final[int] = SECP256R1_ORDER >> 1
JOSE_ES256_SIGNATURE_BYTES: Final[int] = 64
JOSE_ES256_STANDARD: Final[str] = "RFC 8785 (JCS) + RFC 7515 (JWS) + RFC 7518 ES256"


def normalize_es256_low_s(r_int: int, s_int: int) -> tuple[int, int]:
    """Validate `(r, s)` in `[1, n - 1]` and map `s` into canonical low-S `[1, n // 2]`."""
    if isinstance(r_int, bool) or isinstance(s_int, bool) or not isinstance(r_int, int) or not isinstance(s_int, int):
        raise TypeError("ECDSA (r, s) integers must be strict Python ints.")
    if not (1 <= r_int < SECP256R1_ORDER and 1 <= s_int < SECP256R1_ORDER):
        raise ValueError("ES256 signature integers (r, s) are out of [1, n - 1] range.")
    if s_int > SECP256R1_HALF_ORDER:
        s_int = SECP256R1_ORDER - s_int
    return r_int, s_int


def der_to_jose_es256_low_s(der_sig: bytes) -> bytes:
    """Convert an ASN.1 DER ECDSA P-256 signature into 64-byte JOSE `r || s` normalized to low-S."""
    if not isinstance(der_sig, (bytes, bytearray)):
        raise TypeError("der_sig must be bytes.")
    r_int, s_int = decode_dss_signature(bytes(der_sig))
    r_norm, s_norm = normalize_es256_low_s(r_int, s_int)
    return r_norm.to_bytes(32, "big") + s_norm.to_bytes(32, "big")


def sign_jose_es256_low_s(
    priv_key: ec.EllipticCurvePrivateKey,
    signing_input: bytes,
    *,
    deterministic_signing: bool = True,
) -> bytes:
    """
    Sign `signing_input` with ECDSA P-256 SHA-256 and return 64-byte low-S JOSE `r || s`.

    Both `deterministic_signing=True` and randomized `deterministic_signing=False`
    normalize `s` into `[1, n // 2]` before encoding `r || s`.
    """
    if not isinstance(signing_input, (bytes, bytearray)):
        raise TypeError("signing_input must be bytes.")
    der_sig = priv_key.sign(
        bytes(signing_input),
        ec.ECDSA(hashes.SHA256(), deterministic_signing=deterministic_signing),
    )
    return der_to_jose_es256_low_s(der_sig)


def verify_jose_es256_raw(
    pub_key: ec.EllipticCurvePublicKey,
    signing_input: bytes,
    raw_sig: bytes,
    *,
    strict_low_s: bool = False,
) -> tuple[int, int]:
    """
    Verify a 64-byte JOSE `ES256` (`r || s`) signature over `signing_input`.

    - Default (`strict_low_s=False`): accepts any valid `1 <= s < n` signature per
      standard RFC 7515 / RFC 7518 §3.4 JWS rules.
    - Strict (`strict_low_s=True`): rejects the malleable high-S twin (`s > n // 2`)
      when signature bytes are used as canonical identifiers.
    """
    if not isinstance(signing_input, (bytes, bytearray)):
        raise TypeError("signing_input must be bytes.")
    if not isinstance(raw_sig, (bytes, bytearray)):
        raise TypeError("raw_sig must be bytes.")
    sig_bytes = bytes(raw_sig)
    if len(sig_bytes) != JOSE_ES256_SIGNATURE_BYTES:
        raise ValueError("ES256 signature must be 64 bytes (r || s).")

    r_int = int.from_bytes(sig_bytes[:32], "big")
    s_int = int.from_bytes(sig_bytes[32:], "big")
    if not (1 <= r_int < SECP256R1_ORDER and 1 <= s_int < SECP256R1_ORDER):
        raise ValueError("ES256 signature integers (r, s) out of [1, n - 1] range.")
    if strict_low_s and s_int > SECP256R1_HALF_ORDER:
        raise ValueError("ES256 signature rejected: high-S malleability twin (strict_low_s=True).")

    try:
        pub_key.verify(
            encode_dss_signature(r_int, s_int),
            bytes(signing_input),
            ec.ECDSA(hashes.SHA256()),
        )
    except Exception as exc:
        raise ValueError(f"Invalid ES256 cryptographic signature: {exc}") from exc

    return r_int, s_int
