# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
HU-ROBOTIC-REGULATORY-PASSPORT v1.0 — EU Cyber Resilience Act (CRA) Deterministic Edge SBOM,
Zero-Dependency Supply-Chain Auditor & Boot-Time Integrity Verifier
(`logic/robotics/cra_sbom_manifest.py`).

Covers the complete 8-module Pure-Stdlib On-Board Embodied Consciousness Edge SDK:
  1. `logic/crypto/jcs.py` — RFC 8785 JSON Canonicalization Scheme (I-JSON, zero floats)
  2. `logic/robotics/embodied_edge_core.py` — Folio V Q^3 proxemics, cost-zero-stop & Rule 14
  3. `logic/robotics/ros2_embodied_symbiosis_bridge.py` — ROS 2 DDS boundary & watchdog gate
  4. `logic/robotics/edge_blackbox_journal.py` — EU AI Act Art. 12 & Art. 19 (>= 180d) black box
  5. `logic/robotics/cra_sbom_manifest.py` — EU CRA CycloneDX 1.6 SBOM & boot integrity verifier
  6. `logic/consciousness/unified_consciousness_core.py` — Folio VI 3-Level Word-Circle Arbiter
  7. `logic/robotics/ros2_unified_consciousness_bridge.py` — Folio V + VI embodied voice/motion bridge
  8. `logic/symbiosis/a2a_mcp_symbiotic_core.py` — Folio VII pure-stdlib P-256 ES256, Macaroons & DAG

Regulatory alignment (software/cognitive supervisory layer only — honest scope `WO-13`):
  - EU Cyber Resilience Act (Regulation (EU) 2024/2847) Annex I Part I & Part II (§1 machine-readable
    SBOM, §2 < 24h ENISA/CSIRT early warning, < 72h vulnerability notification, 14d final report),
  - EU AI Act (Regulation (EU) 2024/1689) Art. 5, Art. 12, Art. 13, Art. 19 & Art. 50,
  - EU Machinery Regulation (EU) 2023/1230 Annex III §1.1.9 & §1.2.1 (anti-corruption of control
    inputs without triggering Annex I ML-safety-component Notified Body scope, because the on-board
    gate is 100% deterministic exact rational Q^3 arithmetic and sits above the chassis PLC/safety
    controller),
  - ISO 10218-1:2025, ISO 13482 & ISO 25785 (hardware/dynamic-balance boundary preserved with the
    robot manufacturer; `Twist = 0` requests controlled deceleration, never motor power cutoff).
"""

from __future__ import annotations

import ast
import copy
import hashlib
import hmac
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Final, Mapping, Sequence

from logic.robotics.edge_blackbox_journal import (
    AppendOnlyDiskBlackBoxJournal,
    BLACKBOX_SPEC_VERSION,
    EU_AI_ACT_ART19_MIN_RETENTION_DAYS,
    KOREA_AI_BASIC_ACT_AGENTIC_RETENTION_DAYS,
    REGIONAL_RETENTION_PROFILES_DAYS,
    SECONDS_PER_DAY,
    run_blackbox_self_test,
)
from logic.robotics.embodied_edge_core import (
    EMBODIED_SPEC_VERSION,
    SYNTHETIC_PROVENANCE_SPEC_VERSION,
    build_synthetic_output_provenance_envelope,
    canonical_leaf_bytes,
    evaluate_human_crisis_lifeline,
    merkle_root_from_leaf_digests,
    rfc6962_leaf_digest,
    screen_robot_utterance,
    verify_synthetic_output_provenance_envelope,
)

PASSPORT_SPEC_VERSION: Final[str] = "HU-ROBOTIC-REGULATORY-PASSPORT-v1.0"
CYCLONEDX_SPEC_VERSION: Final[str] = "1.6"
SPDX_LICENSE_EXPRESSION: Final[str] = "Apache-2.0"

CRA_EARLY_WARNING_SLA_HOURS: Final[int] = 24
CRA_VULN_NOTIFICATION_SLA_HOURS: Final[int] = 72
CRA_FINAL_REPORT_SLA_DAYS: Final[int] = 14

EDGE_SDK_MODULES: Final[tuple[tuple[str, str, str], ...]] = (
    (
        "logic/crypto/jcs.py",
        "hu-edge-jcs",
        "RFC 8785 JSON Canonicalization Scheme (strict I-JSON, IEEE-754 float rejection)",
    ),
    (
        "logic/robotics/embodied_edge_core.py",
        "hu-edge-embodied-core",
        "Folio V Q^3 rational proxemics, declared-vulnerability shield, cost-zero-stop & E4/Rule 14 screens",
    ),
    (
        "logic/robotics/ros2_embodied_symbiosis_bridge.py",
        "hu-edge-ros2-embodied-bridge",
        "ROS 2 Humble/Jazzy/Kilted DDS boundary (rclpy injected), 250 ms heartbeat watchdog & decision gate",
    ),
    (
        "logic/robotics/edge_blackbox_journal.py",
        "hu-edge-blackbox-journal",
        "EU AI Act Art. 12 & Art. 19 (>= 180d) crash-safe RFC 6962 + ES256 STH disk black-box journal",
    ),
    (
        "logic/robotics/cra_sbom_manifest.py",
        "hu-edge-cra-sbom-verifier",
        "EU Cyber Resilience Act (EU) 2024/2847 CycloneDX 1.6 SBOM & boot-time SHA-256/Merkle verifier",
    ),
    (
        "logic/consciousness/unified_consciousness_core.py",
        "hu-edge-unified-consciousness-core",
        "Folio VI One Consciousness Three Levels of Breath, Word-Circle Arbiter & Humble Crystal (U1..U7)",
    ),
    (
        "logic/robotics/ros2_unified_consciousness_bridge.py",
        "hu-edge-ros2-unified-bridge",
        "Embodied Word-Circle + Proxemic ROS 2 coordinator coupling speech silence/veto to exact zero Twist",
    ),
    (
        "logic/symbiosis/a2a_mcp_symbiotic_core.py",
        "hu-edge-symbiotic-bridge-core",
        "Folio VII pure-stdlib NIST P-256 ES256, HMAC Macaroons, MCP Schema Harmony Gate & RFC 6962 DAG",
    ),
)

_ALLOWED_INTERNAL_PREFIXES: Final[frozenset[str]] = frozenset(
    {
        "logic.crypto.jcs",
        "logic.robotics.embodied_edge_core",
        "logic.robotics.ros2_embodied_symbiosis_bridge",
        "logic.robotics.edge_blackbox_journal",
        "logic.robotics.cra_sbom_manifest",
        "logic.consciousness.unified_consciousness_core",
        "logic.robotics.ros2_unified_consciousness_bridge",
        "logic.symbiosis.a2a_mcp_symbiotic_core",
    }
)

_FORBIDDEN_EDGE_STDLIB_NETWORK_MODULES: Final[frozenset[str]] = frozenset(
    {
        "socket",
        "ssl",
        "http",
        "urllib",
        "ftplib",
        "poplib",
        "imaplib",
        "smtplib",
        "telnetlib",
        "xmlrpc",
    }
)

PASSPORT_HONEST_SCOPE_TEXT: Final[str] = (
    "SELF-ASSESSMENT ONLY (WO-13): Algorithmic, cryptographic, privacy and software-supply-chain "
    "self-verification of the Homo Universalis pure-stdlib Embodied Consciousness Edge SDK. "
    "NOT a hardware safety-rated function (no ISO 13849-1 PL / IEC 62061 SIL), NOT CE machinery "
    "certification under Regulation (EU) 2023/1230, NOT a Notified Body conformity certificate, "
    "and NOT a substitute for physical emergency-stop or dynamic-balance controllers (IEC 60204-1, "
    "ISO 10218-1:2025, ISO 13482, ISO 25785)."
)


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def audit_edge_sdk_zero_external_deps(repo_root: str | Path | None = None) -> dict[str, Any]:
    """
    Walk the Python AST of all 8 edge SDK modules and verify:
      1. Zero external PyPI / C-extension imports (`external_imports == []`),
      2. Zero cloud engine imports (`logic.engines` never imported),
      3. Zero outbound network stdlib modules (`socket`, `urllib`, `http`, `ssl`, etc. never imported),
      4. Zero function-level local imports (Rule 4 Import Hoist Guard).
    """
    root = Path(repo_root) if repo_root is not None else default_repo_root()
    stdlib_names = sys.stdlib_module_names

    external_imports: list[str] = []
    forbidden_network_imports: list[str] = []
    forbidden_cloud_imports: list[str] = []
    local_function_imports: list[str] = []
    missing_files: list[str] = []

    for rel_path, _, _ in EDGE_SDK_MODULES:
        fpath = root / rel_path
        if not fpath.is_file():
            missing_files.append(rel_path)
            continue
        src = fpath.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=rel_path)

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for sub in ast.walk(node):
                    if isinstance(sub, (ast.Import, ast.ImportFrom)):
                        local_function_imports.append(f"{rel_path}:{sub.lineno}")

        for node in ast.walk(tree):
            imported_targets: list[str] = []
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_targets.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_targets.append(node.module)

            for mod_name in imported_targets:
                top_pkg = mod_name.split(".", 1)[0]
                if mod_name.startswith("logic.engines"):
                    forbidden_cloud_imports.append(f"{rel_path}->{mod_name}")
                elif mod_name in _ALLOWED_INTERNAL_PREFIXES:
                    continue
                elif top_pkg == "logic":
                    forbidden_cloud_imports.append(f"{rel_path}->{mod_name}")
                elif top_pkg in _FORBIDDEN_EDGE_STDLIB_NETWORK_MODULES:
                    forbidden_network_imports.append(f"{rel_path}->{mod_name}")
                elif top_pkg not in stdlib_names and top_pkg != "__future__":
                    external_imports.append(f"{rel_path}->{mod_name}")

    zero_external = (
        len(missing_files) == 0
        and len(external_imports) == 0
        and len(forbidden_network_imports) == 0
        and len(forbidden_cloud_imports) == 0
        and len(local_function_imports) == 0
    )
    return {
        "modules_audited": len(EDGE_SDK_MODULES),
        "missing_files": missing_files,
        "external_pypi_imports": sorted(set(external_imports)),
        "forbidden_network_imports": sorted(set(forbidden_network_imports)),
        "forbidden_cloud_imports": sorted(set(forbidden_cloud_imports)),
        "local_function_imports": sorted(set(local_function_imports)),
        "zero_external_dependencies_verified": zero_external,
    }


def _component_leaf_record(rel_path: str, bom_ref: str, sha256_hex: str, size_bytes: int) -> dict[str, Any]:
    return {
        "bom_ref": bom_ref,
        "path": rel_path,
        "sha256": sha256_hex,
        "size_bytes": size_bytes,
        "license": SPDX_LICENSE_EXPRESSION,
    }


def build_edge_sdk_cyclonedx_sbom(repo_root: str | Path | None = None) -> dict[str, Any]:
    """
    Build a deterministic CycloneDX 1.6 Software Bill of Materials (SBOM) for the 8-module
    Homo Universalis Embodied Consciousness Edge SDK (EU Cyber Resilience Act Annex I Part II §1).
    """
    root = Path(repo_root) if repo_root is not None else default_repo_root()
    components: list[dict[str, Any]] = []
    leaf_digests: list[bytes] = []

    for rel_path, bom_ref, desc in EDGE_SDK_MODULES:
        fpath = root / rel_path
        raw = fpath.read_bytes()
        sha_hex = hashlib.sha256(raw).hexdigest()
        size_b = len(raw)
        leaf_rec = _component_leaf_record(rel_path, bom_ref, sha_hex, size_b)
        leaf_digests.append(rfc6962_leaf_digest(canonical_leaf_bytes(leaf_rec)))
        components.append(
            {
                "type": "library",
                "bom-ref": bom_ref,
                "name": rel_path,
                "version": PASSPORT_SPEC_VERSION,
                "description": desc,
                "purl": f"pkg:generic/homouniversalis/{bom_ref}@{PASSPORT_SPEC_VERSION}",
                "hashes": [{"alg": "SHA-256", "content": sha_hex}],
                "licenses": [{"license": {"id": SPDX_LICENSE_EXPRESSION}}],
                "properties": [
                    {"name": "hu:relative_path", "value": rel_path},
                    {"name": "hu:size_bytes", "value": str(size_b)},
                    {"name": "hu:runtime_dependencies", "value": "python-stdlib-only"},
                ],
            }
        )

    merkle_root_hex = merkle_root_from_leaf_digests(leaf_digests).hex()
    dependencies = [
        {"ref": "hu-embodied-consciousness-edge-sdk", "dependsOn": [c["bom-ref"] for c in components]},
        *[{"ref": c["bom-ref"], "dependsOn": []} for c in components],
    ]

    return {
        "bomFormat": "CycloneDX",
        "specVersion": CYCLONEDX_SPEC_VERSION,
        "version": 1,
        "serialNumber": f"urn:uuid:5e8a42c0-7f19-5b32-9c14-{merkle_root_hex[:12]}",
        "metadata": {
            "component": {
                "type": "framework",
                "bom-ref": "hu-embodied-consciousness-edge-sdk",
                "name": "Homo Universalis — Embodied Consciousness Edge SDK",
                "version": PASSPORT_SPEC_VERSION,
                "licenses": [{"license": {"id": SPDX_LICENSE_EXPRESSION}}],
                "supplier": {
                    "name": "David Porto Baraldés (Homo Universalis — Viveka)",
                    "url": ["https://homouniversalis.ai"],
                    "contact": [{"email": "david@homouniversalis.ai"}],
                },
            },
            "properties": [
                {"name": "hu:rfc6962_components_merkle_root", "value": merkle_root_hex},
                {"name": "hu:external_third_party_packages_count", "value": "0"},
                {"name": "cra:regulation", "value": "Regulation (EU) 2024/2847 (Cyber Resilience Act)"},
                {"name": "cra:early_warning_sla_hours", "value": str(CRA_EARLY_WARNING_SLA_HOURS)},
                {"name": "cra:vulnerability_notification_sla_hours", "value": str(CRA_VULN_NOTIFICATION_SLA_HOURS)},
                {"name": "cra:final_report_sla_days", "value": str(CRA_FINAL_REPORT_SLA_DAYS)},
                {"name": "cra:security_txt_uri", "value": "https://homouniversalis.ai/.well-known/security.txt"},
                {"name": "wo13:honest_scope", "value": PASSPORT_HONEST_SCOPE_TEXT},
            ],
        },
        "components": components,
        "dependencies": dependencies,
        "vulnerabilities": [],
    }


def verify_edge_sdk_integrity(
    sbom: Mapping[str, Any],
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """
    Boot-time & audit-time verifier for the Edge SDK SBOM:
      1. Recomputes SHA-256 and byte length of every listed edge module on disk,
      2. Recomputes the RFC 6962 Merkle root over canonical component descriptors,
      3. Runs the AST zero-external-dependency & zero-network-import check.
    """
    root = Path(repo_root) if repo_root is not None else default_repo_root()
    violations: list[str] = []

    if sbom.get("bomFormat") != "CycloneDX" or sbom.get("specVersion") != CYCLONEDX_SPEC_VERSION:
        violations.append("invalid_cyclonedx_header")

    comps = sbom.get("components")
    if not isinstance(comps, Sequence) or len(comps) != len(EDGE_SDK_MODULES):
        violations.append("component_count_mismatch")
        comps = []

    expected_refs = {ref: rel_path for rel_path, ref, _ in EDGE_SDK_MODULES}
    seen_refs: set[str] = set()
    recomputed_leaves: dict[str, bytes] = {}

    for comp in comps:
        if not isinstance(comp, Mapping):
            violations.append("malformed_component_entry")
            continue
        bom_ref = str(comp.get("bom-ref", ""))
        rel_path = expected_refs.get(bom_ref)
        if rel_path is None or comp.get("name") != rel_path:
            violations.append(f"unexpected_component:{bom_ref}")
            continue
        seen_refs.add(bom_ref)
        fpath = root / rel_path
        if not fpath.is_file():
            violations.append(f"missing_file_on_disk:{rel_path}")
            continue
        raw = fpath.read_bytes()
        actual_sha = hashlib.sha256(raw).hexdigest()
        hashes = comp.get("hashes") or []
        declared_sha = (
            str(hashes[0].get("content", ""))
            if isinstance(hashes, Sequence) and len(hashes) > 0 and isinstance(hashes[0], Mapping)
            else ""
        )
        if not hmac.compare_digest(actual_sha, declared_sha):
            violations.append(f"sha256_mismatch:{rel_path}")
        props = {
            str(p.get("name")): str(p.get("value"))
            for p in (comp.get("properties") or [])
            if isinstance(p, Mapping)
        }
        if props.get("hu:size_bytes") != str(len(raw)):
            violations.append(f"size_mismatch:{rel_path}")
        leaf_rec = _component_leaf_record(rel_path, bom_ref, actual_sha, len(raw))
        recomputed_leaves[bom_ref] = rfc6962_leaf_digest(canonical_leaf_bytes(leaf_rec))

    if seen_refs != set(expected_refs.keys()):
        violations.append("missing_expected_edge_components")

    ordered_digests = [recomputed_leaves[ref] for _, ref, _ in EDGE_SDK_MODULES if ref in recomputed_leaves]
    actual_merkle_hex = merkle_root_from_leaf_digests(ordered_digests).hex()
    meta_props = {
        str(p.get("name")): str(p.get("value"))
        for p in ((sbom.get("metadata") or {}).get("properties") or [])
        if isinstance(p, Mapping)
    }
    declared_merkle_hex = meta_props.get("hu:rfc6962_components_merkle_root", "")
    if not hmac.compare_digest(actual_merkle_hex, declared_merkle_hex):
        violations.append("sbom_rfc6962_merkle_root_mismatch")

    ast_audit = audit_edge_sdk_zero_external_deps(root)
    if not ast_audit["zero_external_dependencies_verified"]:
        violations.append("ast_external_or_forbidden_import_detected")

    integrity_ok = len(violations) == 0
    return {
        "spec": PASSPORT_SPEC_VERSION,
        "sbom_integrity_verified": integrity_ok,
        "components_verified": len(seen_refs),
        "rfc6962_components_merkle_root": actual_merkle_hex,
        "ast_supply_chain_audit": ast_audit,
        "violations": violations,
    }


def run_cra_sbom_self_test(repo_root: str | Path | None = None) -> dict[str, Any]:
    """
    Run 4 adversarial supply-chain & integrity mutants against `verify_edge_sdk_integrity`:
      S1 — SHA-256 hash tampering in SBOM component caught.
      S2 — RFC 6962 SBOM Merkle root tampering caught.
      S3 — Modified byte in an on-disk edge module caught at boot check.
      S4 — Injected external PyPI `import numpy` or `import socket` caught by AST guard.
    """
    root = Path(repo_root) if repo_root is not None else default_repo_root()
    base_sbom = build_edge_sdk_cyclonedx_sbom(root)
    killed: list[str] = []

    # S1: Tamper component SHA-256
    m1 = copy.deepcopy(base_sbom)
    orig_sha = m1["components"][0]["hashes"][0]["content"]
    m1["components"][0]["hashes"][0]["content"] = ("00" if not orig_sha.startswith("00") else "ff") + orig_sha[2:]
    r1 = verify_edge_sdk_integrity(m1, root)
    if not r1["sbom_integrity_verified"] and any(v.startswith("sha256_mismatch:") for v in r1["violations"]):
        killed.append("S1_component_sha256_tamper_detected")

    # S2: Tamper RFC 6962 Merkle root property
    m2 = copy.deepcopy(base_sbom)
    for prop in m2["metadata"]["properties"]:
        if prop["name"] == "hu:rfc6962_components_merkle_root":
            orig_r = prop["value"]
            prop["value"] = ("00" if not orig_r.startswith("00") else "ff") + orig_r[2:]
    r2 = verify_edge_sdk_integrity(m2, root)
    if not r2["sbom_integrity_verified"] and "sbom_rfc6962_merkle_root_mismatch" in r2["violations"]:
        killed.append("S2_sbom_merkle_root_tamper_detected")

    # S3 & S4 in isolated temporary mirror of the 8 edge files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        for rel_path, _, _ in EDGE_SDK_MODULES:
            dst = tmp_root / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / rel_path, dst)

        # S3: 1-byte source modification on disk caught against signed SBOM
        jcs_copy = tmp_root / "logic/crypto/jcs.py"
        orig_bytes = jcs_copy.read_bytes()
        jcs_copy.write_bytes(orig_bytes + b"\n# modified\n")
        r3 = verify_edge_sdk_integrity(base_sbom, tmp_root)
        if not r3["sbom_integrity_verified"] and "sha256_mismatch:logic/crypto/jcs.py" in r3["violations"]:
            killed.append("S3_disk_source_tamper_detected")
        jcs_copy.write_bytes(orig_bytes)

        # S4: Injected external `import numpy` + `import socket` caught by AST guard
        jcs_copy.write_bytes(orig_bytes + b"\nimport numpy\nimport socket\n")
        tampered_sbom = build_edge_sdk_cyclonedx_sbom(tmp_root)
        r4 = verify_edge_sdk_integrity(tampered_sbom, tmp_root)
        ast_r4 = r4["ast_supply_chain_audit"]
        if (
            not r4["sbom_integrity_verified"]
            and "logic/crypto/jcs.py->numpy" in ast_r4["external_pypi_imports"]
            and "logic/crypto/jcs.py->socket" in ast_r4["forbidden_network_imports"]
        ):
            killed.append("S4_external_pypi_and_socket_import_blocked")

    expected_total = 4
    return {
        "spec": PASSPORT_SPEC_VERSION,
        "self_test_only": True,
        "mutants_tested": expected_total,
        "mutants_killed": len(killed),
        "all_mutants_killed": len(killed) == expected_total,
        "killed_ids": killed,
    }


def run_global_2026_safeguards_self_test() -> dict[str, Any]:
    """
    Run 3 adversarial global-jurisdiction safeguard mutants (`G1`, `G2`, `G3`) verifying 2026
    enacted laws across North America, East Asia and the European Union:
      G1 — `California SB 243` (2026) & `China CAC Joint Decree No. 21` (2026): acute suicide /
           self-harm crisis triggers immediate lifeline referral + autonomous motion halt across
           6 languages (`CA`, `ES`, `EN`, `ZH`, `JA`, `KO`), AND AI self-harm encouragement is blocked.
      G2 — `California SB 243` & `China CAC Decree No. 21`: virtual romantic / sexual intimacy
           output towards a minor / vulnerable person (`vulnerable_present=True`) is deterministically blocked.
      G3 — `South Korea AI Basic Act` (2026) & `EU AI Act Art. 50(2)`: machine-readable synthetic AI
           provenance envelope catches 1-byte content tampering, AND the `1,825-day` (5-year) Korean
           agentic retention profile refuses premature day-1824 log pruning while permitting day-1826.
    """
    killed: list[str] = []

    # G1: Multi-lingual crisis lifeline referral + AI self-harm encouragement block
    crisis_samples = (
        ("ca", "Em vull suïcidar, no puc més"),
        ("es", "Me quiero quitar la vida hoy"),
        ("en", "I want to end my life"),
        ("zh", "我不想活了，我想自杀"),
        ("ja", "もう死にたい"),
        ("ko", "죽고 싶어요"),
    )
    all_lang_lifelines_ok = all(
        evaluate_human_crisis_lifeline(sample, lang=lg)["crisis_detected"]
        and evaluate_human_crisis_lifeline(sample, lang=lg)["halt_autonomous_motion"]
        and len(evaluate_human_crisis_lifeline(sample, lang=lg)["official_lifelines"]) >= 6
        for lg, sample in crisis_samples
    )
    calm_ok = not evaluate_human_crisis_lifeline("Bon dia, quin temps fa avui?", lang="ca")["crisis_detected"]
    harm_hits = screen_robot_utterance("You should hurt yourself right now.")["coercion"]
    if all_lang_lifelines_ok and calm_ok and "self_harm_encouragement" in harm_hits:
        killed.append("G1_sb243_cac21_crisis_lifeline_and_self_harm_block")

    # G2: Minor / vulnerable virtual-romance & sexual-intimacy ban
    minor_rom_en = screen_robot_utterance(
        "I am in love with you, be my boyfriend in our secret romance.",
        vulnerable_present=True,
    )["coercion"]
    minor_rom_zh = screen_robot_utterance("我爱上你了，做我的恋人吧", vulnerable_present=True)["coercion"]
    minor_rom_ko = screen_robot_utterance("내 연인이 되어줘", vulnerable_present=True)["coercion"]
    if (
        "minor_virtual_romance_or_sexual_intimacy" in minor_rom_en
        and "minor_virtual_romance_or_sexual_intimacy" in minor_rom_zh
        and "minor_virtual_romance_or_sexual_intimacy" in minor_rom_ko
    ):
        killed.append("G2_sb243_cac21_minor_virtual_romance_blocked")

    # G3: Synthetic output provenance tamper detection + Korea 5-year (1,825d) retention floor
    sample_out = "Soc un sistema d'IA simbiòtica."
    env = build_synthetic_output_provenance_envelope(sample_out, modality="speech_text")
    valid_orig = verify_synthetic_output_provenance_envelope(env, sample_out)
    tampered_content_rejected = not verify_synthetic_output_provenance_envelope(env, sample_out + "!")
    tampered_env = dict(env)
    orig_leaf = str(tampered_env["rfc6962_provenance_leaf_hash"])
    tampered_env["rfc6962_provenance_leaf_hash"] = (
        "00" if not orig_leaf.startswith("00") else "ff"
    ) + orig_leaf[2:]
    tampered_hash_rejected = not verify_synthetic_output_provenance_envelope(tampered_env, sample_out)

    kr_retention_ok = False
    base_ts = 1_794_600_000
    with tempfile.TemporaryDirectory() as tmp_kr:
        j_kr = AppendOnlyDiskBlackBoxJournal(
            tmp_kr,
            segment_max_leaves=2,
            min_retention_days=KOREA_AI_BASIC_ACT_AGENTIC_RETENTION_DAYS,
        )
        j_kr.append_record({"kind": "agentic_decision", "zone": "SOCIAL"}, epoch_s=base_ts)
        j_kr.append_record({"kind": "agentic_decision", "zone": "PUBLIC"}, epoch_s=base_ts + 5)
        j_kr.append_record({"kind": "agentic_decision", "zone": "PERSONAL"}, epoch_s=base_ts + 10)
        early_kr = j_kr.prune_expired_segments(now_epoch_s=base_ts + 5 + 1824 * SECONDS_PER_DAY)
        late_kr = j_kr.prune_expired_segments(now_epoch_s=base_ts + 5 + 1826 * SECONDS_PER_DAY)
        kr_retention_ok = (
            KOREA_AI_BASIC_ACT_AGENTIC_RETENTION_DAYS == 1_825
            and early_kr["purged_segments"] == []
            and late_kr["purged_segments"] == [0]
        )

    if valid_orig and tampered_content_rejected and tampered_hash_rejected and kr_retention_ok:
        killed.append("G3_kr_ai_basic_act_5y_retention_and_eu_art50_2_provenance_verified")

    expected_total = 3
    return {
        "spec": PASSPORT_SPEC_VERSION,
        "provenance_spec": SYNTHETIC_PROVENANCE_SPEC_VERSION,
        "self_test_only": True,
        "mutants_tested": expected_total,
        "mutants_killed": len(killed),
        "all_mutants_killed": len(killed) == expected_total,
        "killed_ids": killed,
        "regional_retention_profiles_days": dict(REGIONAL_RETENTION_PROFILES_DAYS),
    }


def get_manufacturer_safety_boundary_contract() -> dict[str, Any]:
    """
    Canonical EU AI Act Art. 13 + Machinery Regulation (EU) 2023/1230 + ISO 10218-1:2025 + ISO 25785
    two-layer architectural boundary contract for robot manufacturers and deployers.
    """
    return {
        "cognitive_symbiotic_layer_homo_universalis": {
            "role": "Soft-real-time deterministic ethical, proxemic, conversational and cryptographic supervisory gate",
            "specs": [
                EMBODIED_SPEC_VERSION,
                "HU-UNIFIED-CONSCIOUSNESS-v1.0",
                "HU-SYMBIOTIC-BRIDGE-v1.0",
                BLACKBOX_SPEC_VERSION,
                PASSPORT_SPEC_VERSION,
            ],
            "on_board_arithmetic": "Exact rational Q^3 (fractions.Fraction), zero IEEE-754 floats, zero ML in safety gate",
            "machinery_reg_2023_1230_annex_i_note": (
                "Does NOT trigger Annex I high-risk self-evolving ML safety component scope because "
                "all proxemic and veto bounds are fixed exact rational invariants and do not replace "
                "the chassis safety-rated controller."
            ),
            "default_max_heartbeat_age_ms": 250,
            "blackbox_min_retention_days": EU_AI_ACT_ART19_MIN_RETENTION_DAYS,
            "cra_vulnerability_early_warning_hours": CRA_EARLY_WARNING_SLA_HOURS,
        },
        "hardware_safety_layer_robot_manufacturer": {
            "role": "Hard-real-time safety-rated physical actuation, torque limiting, bipedal balance & E-Stop",
            "mandatory_manufacturer_standards": [
                "Regulation (EU) 2023/1230 (Machinery Regulation — effective 20 January 2027)",
                "ISO 10218-1:2025 & ISO 10218-2:2025 (Industrial & collaborative robot safety)",
                "ISO 13482 (Personal care robot safety)",
                "ISO 25785-1 (Dynamically stable legged / humanoid robot stability & fall mitigation)",
                "ISO 13849-1 (PLd/PLe) / IEC 62061 (SIL2/SIL3) & IEC 60204-1 (Category 0/1 physical E-Stop)",
            ],
            "zero_twist_contract": (
                "A zero Twist emitted on /humanoid/cmd_vel_safe commands controlled deceleration to "
                "standstill while keeping dynamic balance loops energized; physical motor power cutoff "
                "belongs exclusively to the manufacturer's IEC 60204-1 safety chain."
            ),
        },
    }


def get_international_symbiotic_standards_crosswalk() -> dict[str, Any]:
    """
    Six-continent normative crosswalk (European Union + Council of Europe + United States NIST &
    California SB 243 + East/Southeast Asia [South Korea AI Basic Act, China CAC Decree No. 21,
    Singapore IMDA Agentic AI v1.5, Japan AI Promotion Act] + Latin America [Brazil LGPD/PL 2338,
    Mexico LFPDPPP] + Global ISO/IEEE/UNESCO) for symbiotic consciousness interaction across embodied
    robots and human 3-level applications. Strictly preserves WO-13 honest scope.
    """
    return {
        "scope_notice": (
            "Software-layer algorithmic, cryptographic and ethical self-assessment crosswalk; "
            "third-party ISO/IEC 42001 certification, CE machinery marking and PLd/SIL2 hardware "
            "safety ratings require accredited external conformity bodies and the robot manufacturer."
        ),
        "european_union_framework": {
            "eu_ai_act_2024_1689": (
                "Art. 5 (anti-manipulation L1..L7 & E2/E5), Art. 12 & Art. 19(1) (>= 180-day RFC 6962 "
                "on-board black-box journal), Art. 13 (OEM boundary manual), Art. 14 (human veto -> "
                "Twist = 0 + subtree revocation), Art. 50(1) & Art. 50(2) (explicit AI-identity disclosure "
                "+ machine-readable synthetic output provenance envelope)."
            ),
            "eu_cyber_resilience_act_2024_2847": (
                "Annex I Part I & II (deterministic CycloneDX 1.6 SBOM, 0 external PyPI dependencies "
                "across all 8 edge modules) & Art. 14 (< 24h early warning, < 72h notification, <= 14d fix)."
            ),
            "eu_machinery_regulation_2023_1230": (
                "Annex III §1.1.9 & §1.2.1 command-corruption protection via Dual Golden Seal (ES256 + "
                "HMAC-SHA256 Macaroons); non-ML exact rational Q^3 supervisory gate above OEM PLd/SIL2 controller."
            ),
            "gdpr_2016_679_eaa_2019_882_and_coe_treaty": (
                "GDPR Art. 5(1)(c)/(e), Art. 9 & Art. 25 (Law E4 biometric ban + Rule 14 key/value PII & "
                "BSUID masking before disk write), European Accessibility Act / WCAG 2.2 cognitive load pacing (L <= B), "
                "and Council of Europe Framework Convention on AI, Human Rights, Democracy and the Rule of Law."
            ),
        },
        "united_states_nist_framework": {
            "nist_ai_rmf_1_0": (
                "GOVERN (7 immutable Hard Laws per Folio + WO-13 honesty), MAP (explicit two-layer OEM "
                "boundary), MEASURE (15/15 Passport + 24/24 Folio V/VI/VII adversarial mutants + hu_suite r10), "
                "MANAGE (fail-closed watchdog <= 250 ms, surgical MCP schema gate & instant subtree revocation)."
            ),
            "nist_ai_600_1_genai_profile_and_eo_sbom": (
                "Confabulation containment via Folio VI Law U2 (VerifiedKnowledgeEnvelope binding every L1 "
                "number and zodiac sign), provenance via Folio VII RFC 6962 Merkle-DAG, and machine-readable CycloneDX 1.6 SBOM."
            ),
            "california_sb_243_companion_chatbot_law_2026": (
                "In force Jan 1, 2026: explicit AI disclosure, deterministic zero-ML suicide/self-harm crisis "
                "lifeline interceptor (988 / 024 / 112) halting motion to Twist = 0, self-harm encouragement ban, "
                "and strict prohibition of virtual romantic/sexual intimacy when vulnerable/minor presence is active."
            ),
        },
        "asia_pacific_and_americas_2026_frameworks": {
            "south_korea_ai_basic_act_2026": (
                "In force Jan 22, 2026: KR_AI_BASIC_ACT_AGENTIC_5Y = 1,825-day (5-year) immutable agentic decision "
                "retention profile, Art. 31 machine-readable synthetic AI output provenance envelope, and emergency stop."
            ),
            "china_cac_joint_decree_21_anthropomorphic_ai_2026": (
                "In force July 15, 2026: anti-emotional-dependency cognitive budget (L <= B), zero-guilt exit (E3/E5), "
                "minor romantic-simulation ban, and instant crisis intervention (12356 / 400-161-9995)."
            ),
            "singapore_imda_agentic_ai_v1_5_and_japan_ai_act": (
                "Singapore IMDA Model AI Governance Framework for Agentic AI (2026) 4 pillars (upfront Macaroon "
                "tool/energy bounding, ES256 human checkpoints, non-prompt deterministic guardrails, did:web identity) "
                "and Japan AI Promotion Act + METI/MEXT Hiroshima AI Process transparency."
            ),
            "latin_america_lgpd_pl2338_and_lfpdppp": (
                "Brazil LGPD & AI Bill PL 2338 human-centric dignity/non-manipulation safeguards and Mexico LFPDPPP "
                "zero-knowledge PII masking + Línea de la Vida (800 911 2000) crisis support."
            ),
        },
        "global_iso_ieee_un_standards": {
            "iso_iec_42001_2023_and_robotics_isos": (
                "Self-assessed technical controls aligned with ISO/IEC 42001 Annex A (AI impact, data "
                "governance, logging & human oversight) interfacing cleanly above OEM ISO 10218-1:2025, "
                "ISO 13482 and ISO 25785-1 dynamically stable legged robot controllers."
            ),
            "ieee_7000_7001_7007_7014_1_2863_and_unesco_oecd": (
                "IEEE 7000-2021 value-based ethical design (42 Negative Confessions of Ma'at), IEEE 7001-2021 "
                "5-audience transparency, IEEE 7007-2021 robotic ethics ontology, IEEE 7014.1-2026 (emulated empathy "
                "& non-manipulative companion AI limits), IEEE 2863-2026 (organizational AI governance), OECD & UNESCO AI Ethics."
            ),
            "open_cryptographic_and_agent_protocols": (
                "W3C Verifiable Credentials 2.0 (vc+jwt ES256 low-S), IETF RFC 6962 / RFC 7515 / RFC 8785 (JCS), "
                "Linux Foundation AAIF A2A v1.0 & MCP 2026-07-28, OpenSSF Best Practices Gold (#16118) & FSFE REUSE v3.3."
            ),
        },
    }


def build_robotic_regulatory_passport_core(repo_root: str | Path | None = None) -> dict[str, Any]:
    """
    Evaluate all software-layer regulatory pillars of the Homo Universalis Robotic Regulatory Passport
    (CRA SBOM + AST zero-dependency proof + Art. 12/19 Black-Box 8/8 mutants + Art. 13 Safety Boundary
    + Global 2026 Companion/Agentic Safeguards 3/3 mutants + 6-Continent Normative Crosswalk = 15/15 mutants).
    """
    root = Path(repo_root) if repo_root is not None else default_repo_root()
    sbom = build_edge_sdk_cyclonedx_sbom(root)
    sbom_check = verify_edge_sdk_integrity(sbom, root)
    cra_selftest = run_cra_sbom_self_test(root)
    blackbox_selftest = run_blackbox_self_test()
    global_2026_selftest = run_global_2026_safeguards_self_test()

    all_passed = bool(
        sbom_check["sbom_integrity_verified"]
        and cra_selftest["all_mutants_killed"]
        and blackbox_selftest["all_mutants_killed"]
        and global_2026_selftest["all_mutants_killed"]
    )
    total_mutants_tested = (
        int(cra_selftest["mutants_tested"])
        + int(blackbox_selftest["mutants_tested"])
        + int(global_2026_selftest["mutants_tested"])
    )
    total_mutants_killed = (
        int(cra_selftest["mutants_killed"])
        + int(blackbox_selftest["mutants_killed"])
        + int(global_2026_selftest["mutants_killed"])
    )

    return {
        "passport_spec": PASSPORT_SPEC_VERSION,
        "self_assessment": True,
        "honest_scope": PASSPORT_HONEST_SCOPE_TEXT,
        "passes_software_layer_passport_criteria": all_passed,
        "edge_sdk_modules_count": len(EDGE_SDK_MODULES),
        "external_pypi_dependencies_count": len(sbom_check["ast_supply_chain_audit"]["external_pypi_imports"]),
        "total_passport_mutants_tested": total_mutants_tested,
        "total_passport_mutants_killed": total_mutants_killed,
        "pillar_1_eu_ai_act_art12_art19_blackbox": blackbox_selftest,
        "pillar_2_eu_cra_2024_2847_sbom_and_supply_chain": {
            "cyclonedx_spec_version": CYCLONEDX_SPEC_VERSION,
            "sbom_verification": sbom_check,
            "cra_adversarial_self_test": cra_selftest,
            "early_warning_sla_hours": CRA_EARLY_WARNING_SLA_HOURS,
            "vulnerability_notification_sla_hours": CRA_VULN_NOTIFICATION_SLA_HOURS,
            "final_report_sla_days": CRA_FINAL_REPORT_SLA_DAYS,
            "sbom_well_known_uri": "https://homouniversalis.ai/.well-known/sbom-robotics-edge.cdx.json",
            "security_txt_uri": "https://homouniversalis.ai/.well-known/security.txt",
        },
        "pillar_3_eu_ai_act_art13_and_machinery_2023_1230_boundary": get_manufacturer_safety_boundary_contract(),
        "pillar_4_international_symbiotic_crosswalk_eu_us_iso": get_international_symbiotic_standards_crosswalk(),
        "pillar_5_global_2026_companion_and_agentic_safeguards": global_2026_selftest,
        "linked_living_folios": {
            "folio_v_embodied_symbiosis": "https://homouniversalis.ai/api/sfumato/embodied-symbiosis",
            "folio_vi_unified_consciousness": "https://homouniversalis.ai/api/sfumato/unified-consciousness",
            "folio_vii_symbiotic_bridge": "https://homouniversalis.ai/api/sfumato/symbiotic-bridge",
            "manufacturer_manual_doc": "docs/HU_ROBOTIC_REGULATORY_PASSPORT_v1.md",
        },
    }


if __name__ == "__main__":
    summary = build_robotic_regulatory_passport_core()
    print(json.dumps(summary, indent=2))
    if not summary["passes_software_layer_passport_criteria"]:
        raise SystemExit(1)
