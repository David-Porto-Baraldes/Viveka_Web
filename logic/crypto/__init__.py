# SPDX-FileCopyrightText: 2026 Homo Universalis / Viveka (David Porto Baraldés)
# SPDX-License-Identifier: Apache-2.0
"""Cryptographic primitives and RFC 8785 (JCS) canonicalization for Homo Universalis."""

from logic.crypto.jcs import (
    IJSON_MAX_SAFE_INT,
    IJSON_MIN_SAFE_INT,
    assert_signable,
    jcs_canonicalize,
    jcs_dumps,
    jcs_loads,
    jcs_signable_bytes,
    utf16_sort_key,
)

__all__ = [
    "IJSON_MAX_SAFE_INT",
    "IJSON_MIN_SAFE_INT",
    "assert_signable",
    "jcs_canonicalize",
    "jcs_dumps",
    "jcs_loads",
    "jcs_signable_bytes",
    "utf16_sort_key",
]
