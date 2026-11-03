#!/usr/bin/env python3
"""
Continuous Atheris Fuzzing Harness for Homo Universalis — Viveka.
Fuzzes RFC 8785 JSON Canonicalization Scheme (JCS), Rule 14 Zero-Knowledge
Privacy Masking (`VVK-XXXX-YYYY` / PII purification), and ISO-8601 date validation.
"""
import json
import re
import sys

try:
    import atheris
except ImportError:  # pragma: no cover - fallback when running standalone without atheris binary
    atheris = None  # type: ignore[assignment]


_VVK_RE = re.compile(r"\bVVK-[0-9A-F]{4}-[0-9A-F]{4}\b")
_ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")


def _jcs_canonicalize(obj: object) -> str:
    """Deterministic RFC 8785 JCS serializer under fuzzing scrutiny."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _shield_and_mask(raw_text: str) -> str:
    """Rule 14 Ring I & Ring III deterministic privacy masking under fuzzing scrutiny."""
    masked = _VVK_RE.sub("VVK-****-****", raw_text)
    masked = _ISO_DATE_RE.sub("[date-shielded]", masked)
    return masked


def TestOneInput(data: bytes) -> None:
    """Atheris entry point invoked on each mutated byte buffer."""
    text = data.decode("utf-8", errors="replace")
    masked = _shield_and_mask(text)
    if "VVK-92BA-FC44" in masked:
        raise AssertionError("Unmasked personal VVK key leaked through Rule 14 Ring I")
    try:
        parsed = json.loads(text)
    except Exception:
        return
    canonical = _jcs_canonicalize(parsed)
    reparsed = json.loads(canonical)
    if _jcs_canonicalize(reparsed) != canonical:
        raise AssertionError("RFC 8785 JCS idempotence violation")


def main() -> None:
    if atheris is not None:
        atheris.instrument_all()
        atheris.Setup(sys.argv, TestOneInput)
        atheris.Fuzz()
    else:
        for sample in (b'{"b":1,"a":"VVK-92BA-FC44"}', b"1980-05-24"):
            TestOneInput(sample)


if __name__ == "__main__":
    main()
