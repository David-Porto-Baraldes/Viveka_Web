# SPDX-FileCopyrightText: 2026 Homo Universalis / Viveka (David Porto Baraldés)
# SPDX-License-Identifier: Apache-2.0
"""
RFC 8785 JSON Canonicalization Scheme (JCS) & Strict Signable-Payload Guard.

Implements:
- RFC 8785 §3.2.2.2 minimal string escaping and lone surrogate rejection.
- RFC 8785 §3.2.2.3 ECMAScript number serialization (IEEE-754 NumberToString)
  with I-JSON safe integer bounds [-(2^53 - 1), +(2^53 - 1)].
- RFC 8785 §3.2.3 UTF-16 code-unit key sorting (surrogate decomposition for U+10000..U+10FFFF).
- `assert_signable(obj)`: strict recursive guard rejecting floats anywhere in a
  payload intended for cryptographic signing.
- `jcs_loads(raw)`: strict JSON parser rejecting duplicate object keys, NaN/Infinity,
  and lone UTF-16 surrogates.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
import json
import math
from typing import Any

IJSON_MAX_SAFE_INT: int = (1 << 53) - 1  # +9007199254740991
IJSON_MIN_SAFE_INT: int = -((1 << 53) - 1)  # -9007199254740991


def _assert_no_lone_surrogates(text: str, path: str = "$") -> None:
    """Reject lone UTF-16 surrogates (U+D800..U+DFFF) per RFC 8785 / I-JSON."""
    for ch in text:
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            raise ValueError(f"Lone UTF-16 surrogate U+{cp:04X} is forbidden in JCS at {path}.")


def utf16_sort_key(key: str) -> bytes:
    """
    Return the big-endian UTF-16 code-unit sequence for an object member name.

    Per RFC 8785 §3.2.3, object properties are sorted lexicographically by their
    UTF-16 code units. Supplemental code points (U+10000..U+10FFFF) decompose into
    a high surrogate (0xD800..0xDBFF) followed by a low surrogate (0xDC00..0xDFFF),
    sorting before BMP private-use / compatibility characters U+E000..U+FFFF.
    """
    if not isinstance(key, str):
        raise TypeError(f"JCS object key must be str, got {type(key).__name__}.")
    _assert_no_lone_surrogates(key)
    return key.encode("utf-16-be")


def _escape_jcs_string(value: str, path: str = "$") -> str:
    """Serialize a JSON string per RFC 8785 §3.2.2.2."""
    _assert_no_lone_surrogates(value, path)
    out: list[str] = ['"']
    for ch in value:
        cp = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif cp == 0x08:
            out.append("\\b")
        elif cp == 0x09:
            out.append("\\t")
        elif cp == 0x0A:
            out.append("\\n")
        elif cp == 0x0C:
            out.append("\\f")
        elif cp == 0x0D:
            out.append("\\r")
        elif cp < 0x20:
            out.append(f"\\u{cp:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _format_ecmascript_float(value: float, path: str = "$") -> str:
    """
    Serialize an IEEE-754 double according to ECMAScript Number::toString (RFC 8785 §3.2.2.3).

    Uses Python's shortest round-trip `repr(float)` (David Gay / Ryū shortest significand)
    combined with exact `Decimal` exponent positioning:
    - `-0.0` and `+0.0` -> `"0"`
    - `NaN` / `Infinity` -> raises `ValueError`
    - Exponent `n` (where `10^(n-1) <= |v| < 10^n`) in `-5 <= n <= 21` uses fixed-point notation:
      - If `k <= n`: integer digits padded with `n - k` trailing zeros (e.g. `100.0` -> `"100"`, `1e20` -> `"100000000000000000000"`).
      - If `0 < n < k`: decimal point after `n` digits (e.g. `12.5` -> `"12.5"`).
      - If `-5 <= n <= 0`: `"0."` followed by `-n` zeros and the `k` significand digits (e.g. `1e-6` -> `"0.000001"`).
    - Otherwise scientific notation `<d>[.<digits>]e<+|-><exp>` with no leading zero on the exponent
      (e.g. `1e-7` -> `"1e-7"`, `1e21` -> `"1e+21"`).
    """
    if not math.isfinite(value):
        raise ValueError(f"JCS forbids non-finite IEEE-754 numbers ({value!r}) at {path}.")
    if value == 0.0:
        return "0"

    neg = value < 0.0
    abs_val = -value if neg else value
    # Python 3's repr(float) produces the shortest decimal that round-trips to the exact IEEE-754 double.
    d = Decimal(repr(abs_val)).normalize()
    sign_prefix = "-" if neg else ""

    _, digit_tuple, exp = d.as_tuple()
    digits = "".join(str(x) for x in digit_tuple)
    # Strip any trailing zeros that normalize() might leave on zero-exponent integers
    while len(digits) > 1 and digits.endswith("0"):
        digits = digits[:-1]
        exp += 1

    k = len(digits)  # number of significant digits (k >= 1)
    n = k + int(exp)  # decimal exponent position such that value = (0.digits) * 10^n

    if k <= n <= 21:
        body = digits + ("0" * (n - k))
    elif 0 < n < k:
        body = digits[:n] + "." + digits[n:]
    elif -5 <= n <= 0:
        body = "0." + ("0" * (-n)) + digits
    else:
        mantissa = digits if k == 1 else (digits[0] + "." + digits[1:])
        exp_val = n - 1
        exp_sign = "+" if exp_val > 0 else "-"
        body = f"{mantissa}e{exp_sign}{abs(exp_val)}"

    return sign_prefix + body


def _format_jcs_number(value: int | float, path: str = "$") -> str:
    """Serialize an integer or float per RFC 8785 §3.2.2.3 and I-JSON bounds."""
    if isinstance(value, bool):
        raise TypeError(f"Boolean is not a number at {path}.")
    if isinstance(value, int):
        if value < IJSON_MIN_SAFE_INT or value > IJSON_MAX_SAFE_INT:
            raise ValueError(
                f"Integer {value} at {path} exceeds I-JSON / IEEE-754 safe range "
                f"[{IJSON_MIN_SAFE_INT}, {IJSON_MAX_SAFE_INT}]."
            )
        return str(value)
    if isinstance(value, float):
        return _format_ecmascript_float(value, path)
    raise TypeError(f"Unsupported numeric type {type(value).__name__} at {path}.")


def assert_signable(obj: Any, path: str = "$") -> None:
    """
    Strictly validate that `obj` is safe for cryptographic signing (WO-08).

    Rejects:
    - Any `float` at any nesting depth (`TypeError`).
    - Any `int` outside I-JSON safe bounds `[-(2^53 - 1), +(2^53 - 1)]` (`ValueError`).
    - Any non-string dict key (`TypeError`).
    - Any lone UTF-16 surrogate in strings or keys (`ValueError`).
    - Any unsupported Python object type (`TypeError`).
    """
    if obj is None or isinstance(obj, bool):
        return
    if isinstance(obj, float):
        raise TypeError(
            f"Floating-point numbers are forbidden in signed payloads at {path} (got {obj!r}); "
            "use exact integer, string, or rational string representation."
        )
    if isinstance(obj, int):
        if obj < IJSON_MIN_SAFE_INT or obj > IJSON_MAX_SAFE_INT:
            raise ValueError(
                f"Integer {obj} at {path} exceeds I-JSON safe range "
                f"[{IJSON_MIN_SAFE_INT}, {IJSON_MAX_SAFE_INT}]."
            )
        return
    if isinstance(obj, str):
        _assert_no_lone_surrogates(obj, path)
        return
    if isinstance(obj, (list, tuple)):
        for idx, item in enumerate(obj):
            assert_signable(item, f"{path}[{idx}]")
        return
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise TypeError(f"JSON object keys must be strings at {path}, got {type(k).__name__}.")
            _assert_no_lone_surrogates(k, f"{path}.<key>")
            assert_signable(v, f"{path}.{k}")
        return
    raise TypeError(f"Unsupported type {type(obj).__name__} in signed payload at {path}.")


def jcs_dumps(obj: Any, *, _path: str = "$") -> str:
    """Serialize any JSON-compatible value into its canonical RFC 8785 string."""
    if obj is None:
        return "null"
    if obj is True:
        return "true"
    if obj is False:
        return "false"
    if isinstance(obj, (int, float)):
        return _format_jcs_number(obj, _path)
    if isinstance(obj, str):
        return _escape_jcs_string(obj, _path)
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(jcs_dumps(item, _path=f"{_path}[{idx}]") for idx, item in enumerate(obj)) + "]"
    if isinstance(obj, Mapping):
        for k in obj.keys():
            if not isinstance(k, str):
                raise TypeError(f"JSON object keys must be strings at {_path}, got {type(k).__name__}.")
        sorted_keys = sorted(obj.keys(), key=utf16_sort_key)
        members = [
            f"{_escape_jcs_string(k, f'{_path}.<key>')}:{jcs_dumps(obj[k], _path=f'{_path}.{k}')}"
            for k in sorted_keys
        ]
        return "{" + ",".join(members) + "}"
    raise TypeError(f"Unsupported type {type(obj).__name__} in JCS serialization at {_path}.")


def jcs_canonicalize(obj: Any) -> bytes:
    """Serialize any JSON-compatible value into canonical RFC 8785 UTF-8 bytes."""
    return jcs_dumps(obj).encode("utf-8")


def jcs_signable_bytes(obj: Any) -> bytes:
    """
    Validate `assert_signable(obj)` (rejecting floats) and return RFC 8785 UTF-8 bytes.

    Every cryptographic signer and verifier in the repository must use this function.
    """
    assert_signable(obj)
    return jcs_canonicalize(obj)


def _reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        _assert_no_lone_surrogates(k)
        if isinstance(v, str):
            _assert_no_lone_surrogates(v)
        if k in out:
            raise ValueError(f"Duplicate JSON object key {k!r} is forbidden in RFC 8785 / I-JSON.")
        out[k] = v
    return out


def _reject_non_finite_constant(constant: str) -> Any:
    raise ValueError(f"Non-finite JSON constant {constant!r} is forbidden in RFC 8785.")


def jcs_loads(raw: str | bytes) -> Any:
    """
    Parse JSON strictly per RFC 8785 / I-JSON:
    - Rejects duplicate object keys.
    - Rejects NaN, Infinity, -Infinity.
    - Rejects lone UTF-16 surrogates in strings or keys.
    """
    if isinstance(raw, (bytes, bytearray)):
        text = bytes(raw).decode("utf-8")
    elif isinstance(raw, str):
        text = raw
    else:
        raise TypeError(f"jcs_loads expects str or bytes, got {type(raw).__name__}.")
    parsed = json.loads(
        text,
        object_pairs_hook=_reject_duplicate_object_pairs,
        parse_constant=_reject_non_finite_constant,
    )
    if isinstance(parsed, str):
        _assert_no_lone_surrogates(parsed)
    return parsed
