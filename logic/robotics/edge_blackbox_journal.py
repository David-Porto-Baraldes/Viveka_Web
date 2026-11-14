# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
HU-ROBOTIC-REGULATORY-PASSPORT v1.0 — Crash-Safe On-Board Black-Box Decision Journal
(`logic/robotics/edge_blackbox_journal.py`).

Implements the persistent, append-only, tamper-evident on-board event logging required by:
  - EU AI Act (Regulation (EU) 2024/1689) Art. 12 (Record-keeping) & Art. 19(1) (>= 6 months /
    180 days statutory minimum log retention under the deployer's / manufacturer's control),
  - EU Machinery Regulation (EU) 2023/1230 Annex III §1.1.9 & §1.2.1 (protection against
    corruption or unlawful deletion of control/supervisory records),
  - GDPR Art. 5(1)(c), Art. 5(1)(e) & Art. 9 + HU Law E4 & Rule 14 (zero biometric templates,
    zero coercive emotion scores, and automatic key+value PII/BSUID masking BEFORE disk write).

Crystal-Audit Security Properties:
  1. Pure Python standard library (+ sibling pure-stdlib edge modules `embodied_edge_core` and
     `a2a_mcp_symbiotic_core`): zero third-party packages, zero network sockets, zero IEEE-754
     floats, and zero cloud dependencies (`python3 -I -m logic.robotics.edge_blackbox_journal`).
  2. Unbroken Cross-Segment Hash Chain + Signed Prune Horizon (`retention_horizon.json`):
     - Segment 0 starts at `GENESIS_PREV_HASH_HEX`; every subsequent segment `k > 0` starts its
       `prev_entry_sha256` from `segment-(k-1).sth.json["final_chain_sha256"]`.
     - Deleting a middle segment (`0, 2` with `1` missing) OR deleting `segment-000000` from disk
       without a verified `> 180d` signed `retention_horizon.json` raises `BlackBoxTamperError`.
  3. Symlink & `O_NOFOLLOW` protection (`CWE-59`): refuses symlinked directories or segment files.
  4. Honest scope (`WO-13`): software-layer supervisory audit journal; not a crash-hardened
     aviation flight data recorder (ED-112A) and not a hardware safety-rated PLC log.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import time
from typing import Any, Final, Mapping, Sequence

from logic.robotics.embodied_edge_core import (
    canonical_leaf_bytes,
    edge_rule14_mask,
    merkle_audit_path,
    merkle_root_from_leaf_digests,
    rfc6962_leaf_digest,
    scan_forbidden_telemetry,
    verify_merkle_inclusion,
)
from logic.symbiosis.a2a_mcp_symbiotic_core import (
    p256_derive_keypair,
    p256_derive_public_key,
    p256_sign_es256,
    p256_verify_es256,
)

BLACKBOX_SPEC_VERSION: Final[str] = "HU-EDGE-BLACKBOX-v1.0"
EU_AI_ACT_ART19_MIN_RETENTION_DAYS: Final[int] = 180
KOREA_AI_BASIC_ACT_AGENTIC_RETENTION_DAYS: Final[int] = 1_825
REGIONAL_RETENTION_PROFILES_DAYS: Final[dict[str, int]] = {
    "EU_AI_ACT_ART19_MIN_6M": EU_AI_ACT_ART19_MIN_RETENTION_DAYS,
    "KR_AI_BASIC_ACT_AGENTIC_5Y": KOREA_AI_BASIC_ACT_AGENTIC_RETENTION_DAYS,
}
SECONDS_PER_DAY: Final[int] = 86_400
DEFAULT_BLACKBOX_SEGMENT_MAX_LEAVES: Final[int] = 4096
DOMAIN_BLACKBOX_CHAIN: Final[bytes] = b"HU-BLACKBOX-CHAIN-v1\x00"
DOMAIN_BLACKBOX_STH: Final[bytes] = b"HU-BLACKBOX-STH-v1\x00"
DOMAIN_BLACKBOX_HORIZON: Final[bytes] = b"HU-BLACKBOX-RETENTION-HORIZON-v1\x00"
GENESIS_PREV_HASH_HEX: Final[str] = "0" * 64
RETENTION_HORIZON_FILENAME: Final[str] = "retention_horizon.json"

_O_NOFOLLOW_FLAG: Final[int] = getattr(os, "O_NOFOLLOW", 0)
_SEGMENT_JSONL_RE: Final[re.Pattern[str]] = re.compile(r"^segment-(\d{6})\.jsonl$")
_EDGE_BSUID_RE: Final[re.Pattern[str]] = re.compile(r"(?<![A-Za-z0-9])[A-Z]{2}\.[A-Za-z0-9._-]{8,}")


class BlackBoxError(Exception):
    """Base error for the on-board black-box decision journal."""


class BlackBoxBiometricViolationError(BlackBoxError):
    """Raised when Law E4 / GDPR Art. 9 forbidden biometric or coercive keys appear in a record."""


class BlackBoxTamperError(BlackBoxError):
    """Raised when disk journal verification detects tampering, deletion, symlink or corruption."""


class BlackBoxRetentionError(BlackBoxError):
    """Raised when a retention policy violates the EU AI Act Art. 19(1) 180-day statutory floor."""


def _now_epoch_s() -> int:
    return time.time_ns() // 1_000_000_000


def _reject_json_float(token: str) -> Any:
    raise BlackBoxTamperError(f"IEEE-754 float literal forbidden in canonical black-box journal: {token!r}")


def _strict_non_neg_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
    return value


def _mask_edge_string_and_bsuid(text: str) -> tuple[str, int]:
    bsuid_masked, bsuid_count = _EDGE_BSUID_RE.subn("[BSUID_SHIELDED]", text)
    masked, count = edge_rule14_mask(bsuid_masked)
    return masked, count + bsuid_count


def _sanitize_record_for_disk(node: Any, depth: int = 0) -> tuple[Any, int]:
    """Recursively apply Rule 14 + BSUID masking to keys & values while rejecting floats."""
    if depth > 24:
        raise ValueError("Black-box record exceeds maximum nesting depth (24).")
    if node is None or isinstance(node, bool):
        return node, 0
    if isinstance(node, int):
        return node, 0
    if isinstance(node, float):
        raise TypeError("IEEE-754 float is forbidden in black-box records; use int or rational str.")
    if isinstance(node, str):
        return _mask_edge_string_and_bsuid(node)
    if isinstance(node, Mapping):
        out_dict: dict[str, Any] = {}
        total_redactions = 0
        for raw_k, raw_v in node.items():
            if not isinstance(raw_k, str):
                raise TypeError("Black-box mapping keys must be strings.")
            clean_k, rk_count = _mask_edge_string_and_bsuid(raw_k)
            clean_v, rv_count = _sanitize_record_for_disk(raw_v, depth + 1)
            candidate_k = clean_k
            suffix = 2
            while candidate_k in out_dict:
                candidate_k = f"{clean_k}_{suffix}"
                suffix += 1
            out_dict[candidate_k] = clean_v
            total_redactions += rk_count + rv_count
        return out_dict, total_redactions
    if isinstance(node, (list, tuple)):
        out_list: list[Any] = []
        total_redactions = 0
        for item in node:
            clean_item, r_count = _sanitize_record_for_disk(item, depth + 1)
            out_list.append(clean_item)
            total_redactions += r_count
        return out_list, total_redactions
    raise TypeError(f"Unsupported type in black-box record: {type(node).__name__}")


def _compute_entry_chain_sha256(
    *,
    segment_index: int,
    leaf_index: int,
    epoch_s: int,
    prev_entry_sha256: str,
    leaf_hash_hex: str,
) -> str:
    header = f"{segment_index}:{leaf_index}:{epoch_s}:{prev_entry_sha256}:{leaf_hash_hex}".encode("ascii")
    return hashlib.sha256(DOMAIN_BLACKBOX_CHAIN + header).hexdigest()


def _fsync_directory(directory: Path) -> None:
    try:
        dir_fd = os.open(str(directory), os.O_RDONLY | _O_NOFOLLOW_FLAG)
    except OSError:
        return
    try:
        os.fsync(dir_fd)
    except OSError:
        pass
    finally:
        os.close(dir_fd)


def _atomic_write_json(target_path: Path, payload: Mapping[str, Any]) -> None:
    if target_path.is_symlink():
        raise BlackBoxTamperError(f"Refusing to write through symlink: {target_path.name}")
    raw = canonical_leaf_bytes(payload) + b"\n"
    tmp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    if tmp_path.is_symlink():
        raise BlackBoxTamperError(f"Refusing symlinked temporary file: {tmp_path.name}")
    fd = os.open(str(tmp_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC | _O_NOFOLLOW_FLAG, 0o600)
    try:
        os.write(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(str(tmp_path), str(target_path))
    _fsync_directory(target_path.parent)


class AppendOnlyDiskBlackBoxJournal:
    """
    Crash-safe, cross-segment hash-chained RFC 6962 disk journal for embodied AI decisions.

    - Enforces Law E4 (`scan_forbidden_telemetry`) and Rule 14 (`edge_rule14_mask` + BSUID) BEFORE disk write.
    - Enforces EU AI Act Art. 19(1) minimum retention floor (`min_retention_days >= 180`).
    - Chains every segment from the previous segment's `final_chain_sha256` and signs a tamper-evident
      `retention_horizon.json` upon lawful > 180-day pruning, catching both middle-segment and premature
      prefix-segment deletions.
    """

    def __init__(
        self,
        journal_dir: str | os.PathLike[str],
        *,
        segment_max_leaves: int = DEFAULT_BLACKBOX_SEGMENT_MAX_LEAVES,
        min_retention_days: int = EU_AI_ACT_ART19_MIN_RETENTION_DAYS,
        signing_private_key: int | None = None,
        verification_public_key_xy: tuple[int, int] | None = None,
        clock_epoch_s: Any | None = None,
    ) -> None:
        if isinstance(segment_max_leaves, bool) or not isinstance(segment_max_leaves, int) or segment_max_leaves < 1:
            raise ValueError("segment_max_leaves must be a positive integer.")
        if (
            isinstance(min_retention_days, bool)
            or not isinstance(min_retention_days, int)
            or min_retention_days < EU_AI_ACT_ART19_MIN_RETENTION_DAYS
        ):
            raise BlackBoxRetentionError(
                f"min_retention_days must be an integer >= {EU_AI_ACT_ART19_MIN_RETENTION_DAYS} (EU AI Act Art. 19(1))."
            )
        jdir = Path(journal_dir)
        if jdir.exists() and jdir.is_symlink():
            raise BlackBoxTamperError("journal_dir must not be a symbolic link.")
        jdir.mkdir(parents=True, exist_ok=True)
        self.journal_dir = jdir
        self.segment_max_leaves = segment_max_leaves
        self.min_retention_days = min_retention_days
        self._signing_private_key = signing_private_key
        if signing_private_key is not None and verification_public_key_xy is None:
            self._public_key_xy: tuple[int, int] | None = p256_derive_public_key(signing_private_key)
        else:
            self._public_key_xy = verification_public_key_xy
        self._clock_epoch_s = clock_epoch_s or _now_epoch_s
        self._lock = threading.Lock()

        self._active_segment_index = 0
        self._active_digests: list[bytes] = []
        self._active_prev_chain_hex: str = GENESIS_PREV_HASH_HEX
        self._active_first_epoch_s: int | None = None
        self._active_last_epoch_s: int | None = None
        self._sealed_segment_roots: dict[int, str] = {}
        self._sealed_segment_final_chains: dict[int, str] = {}
        self._horizon_next_segment: int = 0
        self._horizon_anchor_chain: str = GENESIS_PREV_HASH_HEX

        self.verify_and_recover()

    def _segment_jsonl_path(self, segment_index: int) -> Path:
        return self.journal_dir / f"segment-{segment_index:06d}.jsonl"

    def _segment_sth_path(self, segment_index: int) -> Path:
        return self.journal_dir / f"segment-{segment_index:06d}.sth.json"

    def _horizon_path(self) -> Path:
        return self.journal_dir / RETENTION_HORIZON_FILENAME

    def _signable_sth_core(
        self,
        *,
        segment_index: int,
        tree_size: int,
        root_hash_hex: str,
        first_epoch_s: int,
        last_epoch_s: int,
        segment_start_prev_sha256: str,
        final_chain_sha256: str,
    ) -> dict[str, Any]:
        return {
            "spec": BLACKBOX_SPEC_VERSION,
            "segment_index": segment_index,
            "tree_size": tree_size,
            "root_hash": root_hash_hex,
            "first_epoch_s": first_epoch_s,
            "last_epoch_s": last_epoch_s,
            "segment_start_prev_sha256": segment_start_prev_sha256,
            "final_chain_sha256": final_chain_sha256,
            "min_retention_days": self.min_retention_days,
        }

    def _signable_horizon_core(
        self,
        *,
        next_unpruned_segment_index: int,
        anchor_prev_chain_sha256: str,
        last_pruned_segment_last_epoch_s: int,
        pruned_at_epoch_s: int,
        min_retention_days: int,
    ) -> dict[str, Any]:
        return {
            "spec": BLACKBOX_SPEC_VERSION,
            "next_unpruned_segment_index": next_unpruned_segment_index,
            "anchor_prev_chain_sha256": anchor_prev_chain_sha256,
            "last_pruned_segment_last_epoch_s": last_pruned_segment_last_epoch_s,
            "pruned_at_epoch_s": pruned_at_epoch_s,
            "min_retention_days": min_retention_days,
        }

    def _attach_signature_if_configured(
        self,
        doc: dict[str, Any],
        domain_prefix: bytes,
        core: Mapping[str, Any],
    ) -> dict[str, Any]:
        if self._signing_private_key is not None and self._public_key_xy is not None:
            sig = p256_sign_es256(
                self._signing_private_key,
                domain_prefix + canonical_leaf_bytes(core),
            )
            doc["signature_alg"] = "ES256"
            doc["signature_hex"] = sig.hex()
            doc["public_key_xy_hex"] = [
                f"{self._public_key_xy[0]:064x}",
                f"{self._public_key_xy[1]:064x}",
            ]
        else:
            doc["signature_alg"] = "UNSIGNED_LOCAL_HASH_ONLY"
            doc["signature_hex"] = None
        return doc

    def _verify_signed_doc_if_applicable(
        self,
        doc: Mapping[str, Any],
        domain_prefix: bytes,
        core: Mapping[str, Any],
        label: str,
    ) -> None:
        sig_alg = doc.get("signature_alg")
        if self._public_key_xy is not None or sig_alg == "ES256":
            sig_hex = doc.get("signature_hex")
            if not isinstance(sig_hex, str) or len(sig_hex) != 128:
                raise BlackBoxTamperError(f"Missing or invalid ES256 signature on {label}")
            pub_xy = self._public_key_xy
            if pub_xy is None:
                raw_xy = doc.get("public_key_xy_hex")
                if not isinstance(raw_xy, list) or len(raw_xy) != 2:
                    raise BlackBoxTamperError(f"Missing public key coordinates on {label}")
                pub_xy = (int(raw_xy[0], 16), int(raw_xy[1], 16))
            if not p256_verify_es256(
                pub_xy,
                domain_prefix + canonical_leaf_bytes(core),
                bytes.fromhex(sig_hex),
            ):
                raise BlackBoxTamperError(f"ES256 signature verification failed on {label}")

    def _write_sth_locked(
        self,
        *,
        segment_index: int,
        digests: Sequence[bytes],
        first_epoch_s: int,
        last_epoch_s: int,
        segment_start_prev_sha256: str,
        final_chain_sha256: str,
    ) -> dict[str, Any]:
        root_hex = merkle_root_from_leaf_digests(digests).hex()
        core = self._signable_sth_core(
            segment_index=segment_index,
            tree_size=len(digests),
            root_hash_hex=root_hex,
            first_epoch_s=first_epoch_s,
            last_epoch_s=last_epoch_s,
            segment_start_prev_sha256=segment_start_prev_sha256,
            final_chain_sha256=final_chain_sha256,
        )
        sth_doc = self._attach_signature_if_configured(dict(core), DOMAIN_BLACKBOX_STH, core)
        _atomic_write_json(self._segment_sth_path(segment_index), sth_doc)
        self._sealed_segment_roots[segment_index] = root_hex
        self._sealed_segment_final_chains[segment_index] = final_chain_sha256
        return sth_doc

    def _verify_and_load_horizon_locked(self) -> tuple[int, str]:
        hpath = self._horizon_path()
        if not hpath.exists():
            return 0, GENESIS_PREV_HASH_HEX
        if hpath.is_symlink():
            raise BlackBoxTamperError("retention_horizon.json must not be a symbolic link.")
        try:
            hdoc = json.loads(hpath.read_text(encoding="utf-8"), parse_float=_reject_json_float)
        except BlackBoxTamperError:
            raise
        except Exception as exc:
            raise BlackBoxTamperError("Corrupted retention_horizon.json") from exc
        if not isinstance(hdoc, dict):
            raise BlackBoxTamperError("Invalid retention_horizon.json root type")
        next_seg = hdoc.get("next_unpruned_segment_index")
        anchor_hex = hdoc.get("anchor_prev_chain_sha256")
        last_seg_ts = hdoc.get("last_pruned_segment_last_epoch_s")
        pruned_at_ts = hdoc.get("pruned_at_epoch_s")
        decl_min_days = hdoc.get("min_retention_days")
        if (
            isinstance(next_seg, bool)
            or not isinstance(next_seg, int)
            or next_seg < 1
            or not isinstance(anchor_hex, str)
            or len(anchor_hex) != 64
            or isinstance(last_seg_ts, bool)
            or not isinstance(last_seg_ts, int)
            or isinstance(pruned_at_ts, bool)
            or not isinstance(pruned_at_ts, int)
            or isinstance(decl_min_days, bool)
            or not isinstance(decl_min_days, int)
            or decl_min_days < EU_AI_ACT_ART19_MIN_RETENTION_DAYS
        ):
            raise BlackBoxTamperError("Malformed fields in retention_horizon.json")
        if (pruned_at_ts - last_seg_ts) <= decl_min_days * SECONDS_PER_DAY:
            raise BlackBoxTamperError("Unlawful premature retention_horizon.json age delta")
        core = self._signable_horizon_core(
            next_unpruned_segment_index=next_seg,
            anchor_prev_chain_sha256=anchor_hex,
            last_pruned_segment_last_epoch_s=last_seg_ts,
            pruned_at_epoch_s=pruned_at_ts,
            min_retention_days=decl_min_days,
        )
        self._verify_signed_doc_if_applicable(hdoc, DOMAIN_BLACKBOX_HORIZON, core, RETENTION_HORIZON_FILENAME)
        return next_seg, anchor_hex

    def verify_and_recover(self) -> dict[str, Any]:
        """
        Verify symlink absence, retention horizon, contiguous segment indices, cross-segment hash
        continuity, RFC 6962 leaf/root digests and ES256 STH signatures. Fail-closed on tamper.
        """
        with self._lock:
            if self.journal_dir.is_symlink():
                raise BlackBoxTamperError("journal_dir must not be a symbolic link.")
            for entry in sorted(self.journal_dir.iterdir()):
                if entry.is_symlink():
                    raise BlackBoxTamperError(f"Symbolic link forbidden inside black-box directory: {entry.name}")

            base_seg_idx, base_anchor_chain = self._verify_and_load_horizon_locked()

            seg_files: list[tuple[int, Path]] = []
            for entry in sorted(self.journal_dir.iterdir()):
                m = _SEGMENT_JSONL_RE.match(entry.name)
                if m and entry.is_file():
                    seg_files.append((int(m.group(1)), entry))

            for entry in sorted(self.journal_dir.iterdir()):
                if entry.name.endswith(".sth.json") and entry.name.startswith("segment-"):
                    idx_part = entry.name[len("segment-") : len("segment-") + 6]
                    if idx_part.isdigit():
                        seg_idx = int(idx_part)
                        if not self._segment_jsonl_path(seg_idx).exists():
                            raise BlackBoxTamperError(f"Orphan STH without segment data: {entry.name}")

            if seg_files:
                actual_indices = [idx for idx, _ in seg_files]
                expected_indices = list(range(base_seg_idx, base_seg_idx + len(seg_files)))
                if actual_indices != expected_indices:
                    raise BlackBoxTamperError(
                        f"Missing or out-of-order segment files: got {actual_indices}, expected {expected_indices}"
                    )

            sealed_roots: dict[int, str] = {}
            sealed_final_chains: dict[int, str] = {}
            total_verified_leaves = 0
            unsealed_indices: list[int] = []

            running_cross_segment_prev = base_anchor_chain
            active_idx = base_seg_idx
            active_digests: list[bytes] = []
            active_prev_chain = base_anchor_chain
            active_first_ts: int | None = None
            active_last_ts: int | None = None

            for seg_idx, jsonl_path in seg_files:
                raw_text = jsonl_path.read_text(encoding="utf-8")
                lines = [ln for ln in raw_text.splitlines() if ln.strip()]
                if not lines:
                    raise BlackBoxTamperError(f"Empty segment file detected: {jsonl_path.name}")

                seg_start_prev = running_cross_segment_prev
                prev_chain = seg_start_prev
                seg_digests: list[bytes] = []
                first_ts: int | None = None
                last_ts: int | None = None

                for expected_leaf_idx, line in enumerate(lines):
                    try:
                        obj = json.loads(line, parse_float=_reject_json_float)
                    except BlackBoxTamperError:
                        raise
                    except Exception as exc:
                        raise BlackBoxTamperError(
                            f"Corrupted JSONL in {jsonl_path.name}:{expected_leaf_idx + 1}: {type(exc).__name__}"
                        ) from exc
                    if not isinstance(obj, dict):
                        raise BlackBoxTamperError(f"Non-object entry in {jsonl_path.name}:{expected_leaf_idx + 1}")

                    rec = obj.get("record")
                    if not isinstance(rec, dict):
                        raise BlackBoxTamperError(f"Missing record object in {jsonl_path.name}:{expected_leaf_idx + 1}")
                    if scan_forbidden_telemetry(rec):
                        raise BlackBoxTamperError(f"Forbidden biometric key found on disk in {jsonl_path.name}")

                    decl_seg = obj.get("segment_index")
                    decl_leaf = obj.get("leaf_index")
                    decl_epoch = obj.get("epoch_s")
                    decl_prev = obj.get("prev_entry_sha256")
                    decl_leaf_hex = obj.get("leaf_hash")
                    decl_chain_hex = obj.get("entry_sha256")

                    if decl_seg != seg_idx or decl_leaf != expected_leaf_idx:
                        raise BlackBoxTamperError(
                            f"Index discontinuity in {jsonl_path.name}: got ({decl_seg}, {decl_leaf}), "
                            f"expected ({seg_idx}, {expected_leaf_idx})"
                        )
                    if isinstance(decl_epoch, bool) or not isinstance(decl_epoch, int) or decl_epoch < 0:
                        raise BlackBoxTamperError(f"Invalid epoch_s in {jsonl_path.name}:{expected_leaf_idx + 1}")
                    if not isinstance(decl_prev, str) or not hmac.compare_digest(decl_prev, prev_chain):
                        raise BlackBoxTamperError(f"Broken hash chain in {jsonl_path.name}:{expected_leaf_idx + 1}")

                    recomputed_digest = rfc6962_leaf_digest(canonical_leaf_bytes(rec))
                    recomputed_leaf_hex = recomputed_digest.hex()
                    if not isinstance(decl_leaf_hex, str) or not hmac.compare_digest(
                        decl_leaf_hex, recomputed_leaf_hex
                    ):
                        raise BlackBoxTamperError(f"Leaf digest mismatch in {jsonl_path.name}:{expected_leaf_idx + 1}")

                    recomputed_chain = _compute_entry_chain_sha256(
                        segment_index=seg_idx,
                        leaf_index=expected_leaf_idx,
                        epoch_s=decl_epoch,
                        prev_entry_sha256=prev_chain,
                        leaf_hash_hex=recomputed_leaf_hex,
                    )
                    if not isinstance(decl_chain_hex, str) or not hmac.compare_digest(
                        decl_chain_hex, recomputed_chain
                    ):
                        raise BlackBoxTamperError(f"Entry chain MAC mismatch in {jsonl_path.name}:{expected_leaf_idx + 1}")

                    seg_digests.append(recomputed_digest)
                    prev_chain = recomputed_chain
                    if first_ts is None or decl_epoch < first_ts:
                        first_ts = decl_epoch
                    if last_ts is None or decl_epoch > last_ts:
                        last_ts = decl_epoch
                    total_verified_leaves += 1

                sth_path = self._segment_sth_path(seg_idx)
                if sth_path.exists():
                    try:
                        sth_obj = json.loads(
                            sth_path.read_text(encoding="utf-8"),
                            parse_float=_reject_json_float,
                        )
                    except BlackBoxTamperError:
                        raise
                    except Exception as exc:
                        raise BlackBoxTamperError(f"Corrupted STH {sth_path.name}") from exc
                    expected_root_hex = merkle_root_from_leaf_digests(seg_digests).hex()
                    if (
                        sth_obj.get("segment_index") != seg_idx
                        or sth_obj.get("tree_size") != len(seg_digests)
                        or not isinstance(sth_obj.get("root_hash"), str)
                        or not hmac.compare_digest(sth_obj["root_hash"], expected_root_hex)
                        or not isinstance(sth_obj.get("segment_start_prev_sha256"), str)
                        or not hmac.compare_digest(sth_obj["segment_start_prev_sha256"], seg_start_prev)
                        or not isinstance(sth_obj.get("final_chain_sha256"), str)
                        or not hmac.compare_digest(sth_obj["final_chain_sha256"], prev_chain)
                    ):
                        raise BlackBoxTamperError(f"Sealed STH mismatch in {sth_path.name}")

                    core = self._signable_sth_core(
                        segment_index=seg_idx,
                        tree_size=len(seg_digests),
                        root_hash_hex=expected_root_hex,
                        first_epoch_s=int(sth_obj["first_epoch_s"]),
                        last_epoch_s=int(sth_obj["last_epoch_s"]),
                        segment_start_prev_sha256=seg_start_prev,
                        final_chain_sha256=prev_chain,
                    )
                    self._verify_signed_doc_if_applicable(sth_obj, DOMAIN_BLACKBOX_STH, core, sth_path.name)
                    sealed_roots[seg_idx] = expected_root_hex
                    sealed_final_chains[seg_idx] = prev_chain
                    running_cross_segment_prev = prev_chain
                else:
                    unsealed_indices.append(seg_idx)
                    active_idx = seg_idx
                    active_digests = seg_digests
                    active_prev_chain = prev_chain
                    active_first_ts = first_ts
                    active_last_ts = last_ts

            if len(unsealed_indices) > 1:
                raise BlackBoxTamperError(f"Multiple unsealed segments detected: {unsealed_indices}")
            if unsealed_indices and sealed_roots and unsealed_indices[0] <= max(sealed_roots):
                raise BlackBoxTamperError("Unsealed segment precedes a sealed segment.")

            if not unsealed_indices:
                next_idx = (max(sealed_roots) + 1) if sealed_roots else base_seg_idx
                self._active_segment_index = next_idx
                self._active_digests = []
                self._active_prev_chain_hex = running_cross_segment_prev
                self._active_first_epoch_s = None
                self._active_last_epoch_s = None
            else:
                self._active_segment_index = active_idx
                self._active_digests = active_digests
                self._active_prev_chain_hex = active_prev_chain
                self._active_first_epoch_s = active_first_ts
                self._active_last_epoch_s = active_last_ts

            self._sealed_segment_roots = sealed_roots
            self._sealed_segment_final_chains = sealed_final_chains
            self._horizon_next_segment = base_seg_idx
            self._horizon_anchor_chain = base_anchor_chain
            integrity_ok = len(unsealed_indices) <= 1
            return {
                "spec": BLACKBOX_SPEC_VERSION,
                "integrity_verified": integrity_ok,
                "horizon_base_segment": base_seg_idx,
                "sealed_segments_count": len(sealed_roots),
                "active_segment_index": self._active_segment_index,
                "active_segment_leaves": len(self._active_digests),
                "total_verified_leaves": total_verified_leaves,
                "min_retention_days": self.min_retention_days,
            }

    def _current_segment_start_prev_locked(self, seg_idx: int) -> str:
        if seg_idx == self._horizon_next_segment:
            return self._horizon_anchor_chain
        return self._sealed_segment_final_chains[seg_idx - 1]

    def append_record(self, record: Mapping[str, Any], *, epoch_s: int | None = None) -> dict[str, Any]:
        """
        Validate (E4), mask (Rule 14 + BSUID on keys & values), cross-segment hash-chain and fsync
        a canonical decision record to disk. Seals automatically at `segment_max_leaves`.
        """
        if not isinstance(record, Mapping):
            raise TypeError("record must be a mapping.")
        forbidden = scan_forbidden_telemetry(record)
        if forbidden:
            raise BlackBoxBiometricViolationError(
                f"Law E4 / GDPR Art. 9 violation: forbidden telemetry keys {forbidden} refused before disk write."
            )
        sanitized_record, redactions = _sanitize_record_for_disk(record)
        ts = _strict_non_neg_int(
            self._clock_epoch_s() if epoch_s is None else epoch_s,
            "epoch_s",
        )
        leaf_bytes = canonical_leaf_bytes(sanitized_record)
        digest = rfc6962_leaf_digest(leaf_bytes)
        leaf_hex = digest.hex()

        with self._lock:
            seg_idx = self._active_segment_index
            leaf_idx = len(self._active_digests)
            prev_chain = self._active_prev_chain_hex
            entry_chain = _compute_entry_chain_sha256(
                segment_index=seg_idx,
                leaf_index=leaf_idx,
                epoch_s=ts,
                prev_entry_sha256=prev_chain,
                leaf_hash_hex=leaf_hex,
            )
            envelope = {
                "segment_index": seg_idx,
                "leaf_index": leaf_idx,
                "epoch_s": ts,
                "prev_entry_sha256": prev_chain,
                "leaf_hash": leaf_hex,
                "entry_sha256": entry_chain,
                "rule14_redactions": int(redactions),
                "record": sanitized_record,
            }
            line_bytes = canonical_leaf_bytes(envelope) + b"\n"
            seg_path = self._segment_jsonl_path(seg_idx)
            if seg_path.is_symlink():
                raise BlackBoxTamperError(f"Refusing to append to symlink: {seg_path.name}")
            fd = os.open(str(seg_path), os.O_WRONLY | os.O_CREAT | os.O_APPEND | _O_NOFOLLOW_FLAG, 0o600)
            try:
                os.write(fd, line_bytes)
                os.fsync(fd)
            finally:
                os.close(fd)
            if leaf_idx == 0:
                _fsync_directory(self.journal_dir)

            self._active_digests.append(digest)
            self._active_prev_chain_hex = entry_chain
            if self._active_first_epoch_s is None or ts < self._active_first_epoch_s:
                self._active_first_epoch_s = ts
            if self._active_last_epoch_s is None or ts > self._active_last_epoch_s:
                self._active_last_epoch_s = ts

            tree_size_now = len(self._active_digests)
            sealed_sth: dict[str, Any] | None = None
            if tree_size_now >= self.segment_max_leaves:
                seg_start_prev = self._current_segment_start_prev_locked(seg_idx)
                sealed_sth = self._write_sth_locked(
                    segment_index=seg_idx,
                    digests=self._active_digests,
                    first_epoch_s=int(self._active_first_epoch_s),
                    last_epoch_s=int(self._active_last_epoch_s),
                    segment_start_prev_sha256=seg_start_prev,
                    final_chain_sha256=self._active_prev_chain_hex,
                )
                self._active_segment_index = seg_idx + 1
                self._active_digests = []
                self._active_first_epoch_s = None
                self._active_last_epoch_s = None

            return {
                "segment": seg_idx,
                "leaf_index": leaf_idx,
                "tree_size": tree_size_now,
                "leaf_hash": leaf_hex,
                "entry_sha256": entry_chain,
                "segment_sealed": sealed_sth is not None,
            }

    def seal_active_segment(self) -> dict[str, Any] | None:
        """Explicitly seal the active segment (e.g. on clean robot shutdown) if non-empty."""
        with self._lock:
            if not self._active_digests:
                return None
            seg_idx = self._active_segment_index
            seg_start_prev = self._current_segment_start_prev_locked(seg_idx)
            sth = self._write_sth_locked(
                segment_index=seg_idx,
                digests=self._active_digests,
                first_epoch_s=int(self._active_first_epoch_s or 0),
                last_epoch_s=int(self._active_last_epoch_s or 0),
                segment_start_prev_sha256=seg_start_prev,
                final_chain_sha256=self._active_prev_chain_hex,
            )
            self._active_segment_index = seg_idx + 1
            self._active_digests = []
            self._active_first_epoch_s = None
            self._active_last_epoch_s = None
            return sth

    def current_root_hex(self) -> str:
        """Return the RFC 6962 Merkle root of the active segment (or most recently sealed segment if empty)."""
        with self._lock:
            if self._active_digests:
                return merkle_root_from_leaf_digests(self._active_digests).hex()
            if self._sealed_segment_roots:
                latest = max(self._sealed_segment_roots)
                return self._sealed_segment_roots[latest]
            return merkle_root_from_leaf_digests([]).hex()

    def prove_receipt(self, leaf_index: int, *, segment_index: int | None = None) -> dict[str, Any]:
        """Generate an RFC 6962 inclusion proof for `leaf_index` in `segment_index` (defaults to current/latest)."""
        if isinstance(leaf_index, bool) or not isinstance(leaf_index, int) or leaf_index < 0:
            raise IndexError("leaf_index must be a non-negative integer.")
        with self._lock:
            if segment_index is None:
                if self._active_digests:
                    target_seg = self._active_segment_index
                    digests = list(self._active_digests)
                elif self._sealed_segment_roots:
                    target_seg = max(self._sealed_segment_roots)
                    digests = self._load_segment_digests_unlocked(target_seg)
                else:
                    raise IndexError("Black-box journal is empty.")
            elif segment_index == self._active_segment_index and self._active_digests:
                target_seg = segment_index
                digests = list(self._active_digests)
            else:
                target_seg = segment_index
                digests = self._load_segment_digests_unlocked(target_seg)

        if leaf_index >= len(digests):
            raise IndexError("leaf_index outside segment bounds.")
        root_bytes = merkle_root_from_leaf_digests(digests)
        path_nodes = merkle_audit_path(leaf_index, digests)
        proof_valid = verify_merkle_inclusion(digests[leaf_index], leaf_index, len(digests), path_nodes, root_bytes)
        return {
            "segment": target_seg,
            "leaf_index": leaf_index,
            "tree_size": len(digests),
            "leaf_hash": digests[leaf_index].hex(),
            "audit_path": [node.hex() for node in path_nodes],
            "root_hash": root_bytes.hex(),
            "inclusion_verified": proof_valid,
        }

    def _load_segment_digests_unlocked(self, segment_index: int) -> list[bytes]:
        seg_path = self._segment_jsonl_path(segment_index)
        if not seg_path.exists():
            raise IndexError(f"Segment {segment_index} does not exist on disk.")
        out: list[bytes] = []
        for line in seg_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                obj = json.loads(line, parse_float=_reject_json_float)
                out.append(bytes.fromhex(obj["leaf_hash"]))
        return out

    def prune_expired_segments(self, *, now_epoch_s: int | None = None) -> dict[str, Any]:
        """
        Purge ONLY contiguous oldest sealed prefix segments whose `last_epoch_s` is strictly older
        than `min_retention_days * 86400` seconds, writing a signed `retention_horizon.json` anchor
        before unlinking so cross-segment chain integrity remains unbroken across reboots.
        """
        now_ts = _strict_non_neg_int(
            self._clock_epoch_s() if now_epoch_s is None else now_epoch_s,
            "now_epoch_s",
        )
        min_age_s = self.min_retention_days * SECONDS_PER_DAY
        purged: list[int] = []
        retained: list[int] = []

        with self._lock:
            for seg_idx in sorted(list(self._sealed_segment_roots.keys())):
                sth_path = self._segment_sth_path(seg_idx)
                jsonl_path = self._segment_jsonl_path(seg_idx)
                if not sth_path.exists():
                    continue
                sth_obj = json.loads(sth_path.read_text(encoding="utf-8"), parse_float=_reject_json_float)
                last_ts = int(sth_obj["last_epoch_s"])
                if seg_idx == self._horizon_next_segment and now_ts > last_ts and (now_ts - last_ts) > min_age_s:
                    if (self._public_key_xy is not None or sth_obj.get("signature_alg") == "ES256") and self._signing_private_key is None:
                        raise BlackBoxTamperError(
                            "Refusing signature-downgrade prune: ES256-protected black-box requires signing_private_key."
                        )
                    final_chain = str(sth_obj["final_chain_sha256"])
                    h_core = self._signable_horizon_core(
                        next_unpruned_segment_index=seg_idx + 1,
                        anchor_prev_chain_sha256=final_chain,
                        last_pruned_segment_last_epoch_s=last_ts,
                        pruned_at_epoch_s=now_ts,
                        min_retention_days=self.min_retention_days,
                    )
                    h_doc = self._attach_signature_if_configured(dict(h_core), DOMAIN_BLACKBOX_HORIZON, h_core)
                    _atomic_write_json(self._horizon_path(), h_doc)
                    if jsonl_path.exists():
                        jsonl_path.unlink()
                    sth_path.unlink()
                    del self._sealed_segment_roots[seg_idx]
                    del self._sealed_segment_final_chains[seg_idx]
                    self._horizon_next_segment = seg_idx + 1
                    self._horizon_anchor_chain = final_chain
                    purged.append(seg_idx)
                else:
                    retained.append(seg_idx)
            if purged:
                _fsync_directory(self.journal_dir)

        return {
            "min_retention_days": self.min_retention_days,
            "purged_segments": purged,
            "retained_sealed_segments": retained,
            "horizon_base_segment": self._horizon_next_segment,
        }


def run_blackbox_self_test() -> dict[str, Any]:
    """
    Deterministic self-test exercising 8 adversarial failure/tamper mutants in an isolated tmpdir:
      M1 — Biometric key injection refused before disk write (`E4` / GDPR Art. 9).
      M2 — Retention floor `< 180` days rejected (`EU AI Act Art. 19(1)`).
      M3 — Premature purge at day 179 refused; lawful purge at day 181 writes signed horizon & recovers cleanly.
      M4 — Record payload tampering on disk caught by `verify_and_recover()`.
      M5 — Intra-segment line deletion / chain break caught by `verify_and_recover()`.
      M6 — Sealed ES256 STH signature forgery caught by `verify_and_recover()`.
      M7 — Middle-segment deletion (`segment-000001` removed between `0` and `2`) caught by cross-segment chain.
      M8 — Unlawful raw file deletion of `segment-000000` without signed > 180d horizon caught on reboot.
    """
    priv_d, pub_xy = p256_derive_keypair(b"hu-edge-blackbox-selftest-seed-2026")
    killed: list[str] = []
    base_ts = 1_794_600_000

    # M1: Biometric vector rejected before disk write
    with tempfile.TemporaryDirectory() as tmp1:
        j1 = AppendOnlyDiskBlackBoxJournal(tmp1, segment_max_leaves=2, signing_private_key=priv_d)
        try:
            j1.append_record({"kind": "cmd_vel", "face_embedding_vector": [1, 2, 3]}, epoch_s=base_ts)
        except BlackBoxBiometricViolationError:
            if not list(Path(tmp1).glob("segment-*.jsonl")):
                killed.append("M1_biometric_vector_blocked_before_disk")

    # M2: Sub-180-day retention rejected
    with tempfile.TemporaryDirectory() as tmp2:
        try:
            AppendOnlyDiskBlackBoxJournal(tmp2, min_retention_days=179)
        except BlackBoxRetentionError:
            killed.append("M2_sub_180d_retention_rejected")

    # M3: Premature purge at 179d blocked; purge at 181d writes signed horizon & reboot verifies segment 1!
    with tempfile.TemporaryDirectory() as tmp3:
        j3 = AppendOnlyDiskBlackBoxJournal(
            tmp3,
            segment_max_leaves=2,
            signing_private_key=priv_d,
            verification_public_key_xy=pub_xy,
        )
        j3.append_record(
            {"kind": "utterance", "CO.13491283912": "Reach test@example.com or VVK-ABCD-1234"},
            epoch_s=base_ts,
        )
        r_seal = j3.append_record({"kind": "cmd_vel", "zone": "SOCIAL"}, epoch_s=base_ts + 10)
        j3.append_record({"kind": "cmd_vel", "zone": "PUBLIC"}, epoch_s=base_ts + 20)
        raw_disk = (Path(tmp3) / "segment-000000.jsonl").read_text(encoding="utf-8")
        pii_scrubbed = (
            ("test@example.com" not in raw_disk)
            and ("VVK-ABCD-1234" not in raw_disk)
            and ("CO.13491283912" not in raw_disk)
        )
        p_early = j3.prune_expired_segments(now_epoch_s=base_ts + 10 + 179 * SECONDS_PER_DAY)
        p_late = j3.prune_expired_segments(now_epoch_s=base_ts + 10 + 181 * SECONDS_PER_DAY)
        j3_reboot = AppendOnlyDiskBlackBoxJournal(tmp3, verification_public_key_xy=pub_xy)
        rec3 = j3_reboot.verify_and_recover()
        if (
            r_seal["segment_sealed"]
            and pii_scrubbed
            and p_early["purged_segments"] == []
            and p_late["purged_segments"] == [0]
            and rec3["horizon_base_segment"] == 1
            and rec3["total_verified_leaves"] == 1
        ):
            killed.append("M3_art19_180d_signed_horizon_and_key_value_rule14_enforced")

    # M4: Disk payload tampering caught on reboot
    with tempfile.TemporaryDirectory() as tmp4:
        j4 = AppendOnlyDiskBlackBoxJournal(tmp4, segment_max_leaves=4, signing_private_key=priv_d)
        j4.append_record({"kind": "cmd_vel", "zone": "PERSONAL"}, epoch_s=base_ts)
        seg_file = Path(tmp4) / "segment-000000.jsonl"
        seg_file.write_text(seg_file.read_text(encoding="utf-8").replace("PERSONAL", "PUBLIC"), encoding="utf-8")
        try:
            AppendOnlyDiskBlackBoxJournal(tmp4, verification_public_key_xy=pub_xy)
        except BlackBoxTamperError:
            killed.append("M4_payload_tamper_detected")

    # M5: Line deletion / chain break caught on reboot
    with tempfile.TemporaryDirectory() as tmp5:
        j5 = AppendOnlyDiskBlackBoxJournal(tmp5, segment_max_leaves=4, signing_private_key=priv_d)
        j5.append_record({"kind": "cmd_vel", "seq": 1}, epoch_s=base_ts)
        j5.append_record({"kind": "cmd_vel", "seq": 2}, epoch_s=base_ts + 1)
        seg_file5 = Path(tmp5) / "segment-000000.jsonl"
        lines5 = seg_file5.read_text(encoding="utf-8").splitlines()
        seg_file5.write_text(lines5[1] + "\n", encoding="utf-8")
        try:
            AppendOnlyDiskBlackBoxJournal(tmp5, verification_public_key_xy=pub_xy)
        except BlackBoxTamperError:
            killed.append("M5_chain_truncation_detected")

    # M6: Sealed STH ES256 signature forgery caught on reboot
    with tempfile.TemporaryDirectory() as tmp6:
        j6 = AppendOnlyDiskBlackBoxJournal(tmp6, segment_max_leaves=1, signing_private_key=priv_d)
        j6.append_record({"kind": "cmd_vel", "seq": 1}, epoch_s=base_ts)
        sth_file6 = Path(tmp6) / "segment-000000.sth.json"
        sth_obj6 = json.loads(sth_file6.read_text(encoding="utf-8"))
        bad_sig = ("00" if not sth_obj6["signature_hex"].startswith("00") else "ff") + sth_obj6["signature_hex"][2:]
        sth_obj6["signature_hex"] = bad_sig
        sth_file6.write_text(json.dumps(sth_obj6), encoding="utf-8")
        try:
            AppendOnlyDiskBlackBoxJournal(tmp6, verification_public_key_xy=pub_xy)
        except BlackBoxTamperError:
            killed.append("M6_sth_es256_forgery_detected")

    # M7: Middle-segment deletion (`segment-000001.*` deleted while `0` and `2` remain) caught!
    with tempfile.TemporaryDirectory() as tmp7:
        j7 = AppendOnlyDiskBlackBoxJournal(tmp7, segment_max_leaves=1, signing_private_key=priv_d)
        j7.append_record({"kind": "cmd_vel", "seq": 1}, epoch_s=base_ts)
        j7.append_record({"kind": "cmd_vel", "seq": 2}, epoch_s=base_ts + 1)
        j7.append_record({"kind": "cmd_vel", "seq": 3}, epoch_s=base_ts + 2)
        (Path(tmp7) / "segment-000001.jsonl").unlink()
        (Path(tmp7) / "segment-000001.sth.json").unlink()
        try:
            AppendOnlyDiskBlackBoxJournal(tmp7, verification_public_key_xy=pub_xy)
        except BlackBoxTamperError:
            killed.append("M7_middle_segment_deletion_detected")

    # M8: Raw premature deletion of `segment-000000.*` without signed > 180d horizon caught!
    with tempfile.TemporaryDirectory() as tmp8:
        j8 = AppendOnlyDiskBlackBoxJournal(tmp8, segment_max_leaves=1, signing_private_key=priv_d)
        j8.append_record({"kind": "cmd_vel", "seq": 1}, epoch_s=base_ts)
        j8.append_record({"kind": "cmd_vel", "seq": 2}, epoch_s=base_ts + 1)
        (Path(tmp8) / "segment-000000.jsonl").unlink()
        (Path(tmp8) / "segment-000000.sth.json").unlink()
        try:
            AppendOnlyDiskBlackBoxJournal(tmp8, verification_public_key_xy=pub_xy)
        except BlackBoxTamperError:
            killed.append("M8_premature_segment0_file_deletion_detected")

    expected_total = 8
    return {
        "spec": BLACKBOX_SPEC_VERSION,
        "self_test_only": True,
        "mutants_tested": expected_total,
        "mutants_killed": len(killed),
        "all_mutants_killed": len(killed) == expected_total,
        "killed_ids": killed,
        "min_retention_days": EU_AI_ACT_ART19_MIN_RETENTION_DAYS,
        "regional_retention_profiles_days": dict(REGIONAL_RETENTION_PROFILES_DAYS),
    }


if __name__ == "__main__":
    report = run_blackbox_self_test()
    print(json.dumps(report, indent=2))
    if not report["all_mutants_killed"]:
        raise SystemExit(1)
