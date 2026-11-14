# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
HU-OPEN-FLOOR-ADAPTER v1.0 — Deterministic Bidirectional Adapter between Folio VI
(`WordCircleArbiter`) and the Linux Foundation Open Floor Protocol (`OVON v1.1.1`)
(`logic/consciousness/open_floor_adapter.py`).

Pure Python standard library + `logic.crypto.jcs` + `logic.robotics.embodied_edge_core`
+ `logic.consciousness.unified_consciousness_core`.
Zero external PyPI dependencies, zero floats, zero network, zero cloud SDK imports
(preserving `test_a01` = `0 0 0` for on-board humanoid & symbiotic edge runtimes).

Unites:
  1. Linux Foundation AI & Data / Open Voice Interoperability Initiative
     `Open Floor Inter-Agent Message Specification v1.1.1` (`requestFloor`, `grantFloor`,
     `revokeFloor`, `yieldFloor`, `invite`, `bye`, `publishManifest`, `dialogEvent`).
  2. Folio VI `HU-UNIFIED-CONSCIOUSNESS v1.0` (`Laws U1..U7`, `WordCircleArbiter`,
     `VerifiedKnowledgeEnvelope`, `SpokenTruthLedger`, `Barge-in` vs `Veto`).
  3. `HU-SYNTHETIC-PROVENANCE-v1.0` (`EU AI Act Art. 50(2)` & `South Korea AI Basic Act Art. 31`
     cryptographic SHA-256 + RFC 6962 synthetic speech/audio labelling).
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import secrets
import time
from typing import Any, Final, Mapping, Sequence

from logic.consciousness.unified_consciousness_core import (
    ConsciousnessEvent,
    EVENT_COST_ZERO_STOP,
    EVENT_COST_ZERO_STOP_RELEASE,
    EVENT_HUMAN_BARGE_IN,
    EVENT_HUMAN_DECLINE_L3,
    EVENT_HUMAN_INVITE_L3,
    EVENT_HUMAN_SPEECH_END,
    EVENT_HUMAN_SPEECH_START,
    EVENT_HUMAN_VETO,
    EVENT_L1_PROPOSE_SPEECH,
    EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH,
    EVENT_VOICE_EMISSION_COMPLETE,
    UNIFIED_CONSCIOUSNESS_LAWS,
    UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
    WordCircleArbiter,
    classify_explicit_veto_utterance,
    issue_verified_knowledge_envelope,
    screen_level1_humble_crystal,
)
from logic.crypto.jcs import jcs_dumps, jcs_signable_bytes
from logic.robotics.embodied_edge_core import (
    SYNTHETIC_PROVENANCE_SPEC_VERSION,
    build_synthetic_output_provenance_envelope,
    edge_rule14_mask,
    evaluate_human_crisis_lifeline,
    rfc6962_leaf_digest,
    verify_synthetic_output_provenance_envelope,
)

OPEN_FLOOR_SCHEMA_VERSION: Final[str] = "1.1.1"
OPEN_FLOOR_ADAPTER_SPEC: Final[str] = "HU-OPEN-FLOOR-ADAPTER/v1.0"
VIVEKA_SPEAKER_URI: Final[str] = "tag:homouniversalis.ai,2026:viveka-unified-consciousness"
VIVEKA_SERVICE_URL: Final[str] = "https://homouniversalis.ai/api/veu/openfloor"
VIVEKA_MANIFEST_URL: Final[str] = "https://homouniversalis.ai/.well-known/openfloor-manifest.json"
VIVEKA_WS_URL: Final[str] = "wss://homouniversalis.ai/api/veu/ws"

SUPPORTED_OPEN_FLOOR_DIRECTIVES: Final[tuple[str, ...]] = (
    "dialogEvent",
    "requestFloor",
    "grantFloor",
    "revokeFloor",
    "yieldFloor",
    "invite",
    "uninvite",
    "bye",
    "getManifests",
    "publishManifests",
)


def _utc_iso_now(epoch_ms: int | None = None) -> str:
    ms = int(epoch_ms if epoch_ms is not None else int(time.time() * 1000))
    sec, rem_ms = divmod(max(0, ms), 1000)
    dt = datetime.fromtimestamp(sec, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{rem_ms:03d}Z"


def _mask_conversant_uri(raw_uri: str) -> str:
    masked, _ = edge_rule14_mask(str(raw_uri or "tag:traveler.local,2026:anonymous"))
    return masked[:160]


def build_open_floor_assistant_manifest(
    *,
    service_url: str = VIVEKA_SERVICE_URL,
    ws_url: str = VIVEKA_WS_URL,
    speaker_uri: str = VIVEKA_SPEAKER_URI,
) -> dict[str, Any]:
    """
    Build the Linux Foundation Open Floor (`OVON 1.1.1`) Assistant Manifest for
    **Homo Universalis — Viveka (3-Level Unified Voice Consciousness)**.
    """
    manifest_core: dict[str, Any] = {
        "identification": {
            "speakerUri": speaker_uri,
            "serviceUrl": service_url,
            "conversationalName": "Viveka — Homo Universalis",
            "organization": "Homo Universalis (homouniversalis.ai)",
            "role": "Symbiotic 3-Level Unified Voice & Ephemeris Consciousness",
            "synopsis": (
                "Deterministic 3-Level Voice Consciousness (WordCircleArbiter U1..U7, "
                "Humble Crystal U2, <20 ms Barge-in vs Veto U3, Spoken-Truth Ledger U6, "
                "Rule 14 Zero-Biometric Sanctuary U7, Aoede HD & SynthID/SHA-256 provenance)."
            ),
        },
        "capabilities": {
            "keyphrases": [
                "viveka",
                "homo universalis",
                "ephemeris",
                "seed of life",
                "synastry",
                "meditation",
                "three levels",
            ],
            "languages": ["ca", "es", "en", "fr", "it", "pt", "de", "zh", "ja", "ko"],
            "descriptions": [
                "Level 1 Adaptive Humble Presence (<4s silent orb, U2 Humble Crystal verified).",
                "Level 2 Verified Pantheon & 7-Wisdoms Swiss Ephemeris (<1.5ms ephemeris + Aoede HD).",
                "Level 3 Quiet Cathedral (gemini-4-carbon silent vault + Golden Halo single offer U4).",
                "Real-time WebSocket bidirectional audio stream + Open Floor 1.1.1 JSON envelopes.",
            ],
            "supportedLayers": {
                "input": ["text", "audio/wav", "audio/webm", "audio/ogg", "audio/pcm"],
                "output": ["text", "audio/wav", "audio/ogg"],
            },
            "symbioticGovernance": {
                "adapterSpec": OPEN_FLOOR_ADAPTER_SPEC,
                "consciousnessSpec": UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
                "laws": list(UNIFIED_CONSCIOUSNESS_LAWS),
                "syntheticProvenanceSpec": SYNTHETIC_PROVENANCE_SPEC_VERSION,
                "realtimeWebSocketEndpoint": ws_url,
                "zeroBiometricVoiceprintStorage": True,
                "safetyRatedHardwareFunction": False,
            },
        },
    }
    digest_hex = rfc6962_leaf_digest(jcs_signable_bytes(manifest_core)).hex()
    return {
        "openFloor": {
            "schema": {
                "version": OPEN_FLOOR_SCHEMA_VERSION,
                "url": "https://openfloor.dev/schemas/1.1.1/openfloor.json",
            },
            "manifest": manifest_core,
            "rfc6962ManifestLeafHash": digest_hex,
        }
    }


def build_speech_audio_provenance_envelope(
    *,
    spoken_text: str,
    audio_bytes: bytes | None = None,
    mime_type: str = "audio/wav",
    voice_name: str = "Aoede-HD",
    model_family: str = "Homo-Universalis-Aoede-HD-SynthID",
    level: int = 2,
) -> dict[str, Any]:
    """
    Build a dual text + audio cryptographic provenance envelope (`HU-SYNTHETIC-PROVENANCE-v1.0`)
    satisfying `EU AI Act Art. 50(2)` and `South Korea AI Basic Act Art. 31` for synthesized speech.
    """
    if isinstance(level, bool) or level not in (1, 2, 3):
        raise ValueError("level must be 1, 2, or 3.")
    masked_txt, _ = edge_rule14_mask(str(spoken_text or ""))
    has_audio = isinstance(audio_bytes, (bytes, bytearray, memoryview)) and len(audio_bytes) > 0
    payload_target: str | bytes = bytes(audio_bytes) if has_audio else masked_txt
    modality = "speech_audio" if has_audio else "speech_text"
    base_env = build_synthetic_output_provenance_envelope(
        payload_target,
        model_family=model_family,
        modality=modality,
    )
    text_sha256 = hashlib.sha256(masked_txt.encode("utf-8")).hexdigest()
    audio_sha256 = hashlib.sha256(bytes(audio_bytes)).hexdigest() if has_audio else None
    extra: dict[str, Any] = {
        **base_env,
        "consciousness_level": level,
        "voice_profile": str(voice_name or "Aoede-HD"),
        "mime_type": str(mime_type or "text/plain") if has_audio else "text/plain",
        "synthid_acoustic_watermark_declared": bool(has_audio),
        "spoken_text_masked_sha256": text_sha256,
        "audio_sha256": audio_sha256,
    }
    return extra


def verify_speech_audio_provenance_envelope(
    envelope: Mapping[str, Any],
    *,
    spoken_text: str,
    audio_bytes: bytes | None = None,
) -> bool:
    """Verify both the base `HU-SYNTHETIC-PROVENANCE-v1.0` leaf and the bound text/audio digests."""
    if not isinstance(envelope, Mapping):
        return False
    has_audio = isinstance(audio_bytes, (bytes, bytearray, memoryview)) and len(audio_bytes) > 0
    target: str | bytes = bytes(audio_bytes) if has_audio else edge_rule14_mask(str(spoken_text or ""))[0]
    if not verify_synthetic_output_provenance_envelope(envelope, target):
        return False
    expected_txt_sha = hashlib.sha256(edge_rule14_mask(str(spoken_text or ""))[0].encode("utf-8")).hexdigest()
    if envelope.get("spoken_text_masked_sha256") != expected_txt_sha:
        return False
    if has_audio:
        expected_aud_sha = hashlib.sha256(bytes(audio_bytes)).hexdigest()
        if envelope.get("audio_sha256") != expected_aud_sha:
            return False
    return True


def build_open_floor_envelope(
    *,
    conversation_id: str,
    events: Sequence[Mapping[str, Any]],
    sender_uri: str = VIVEKA_SPEAKER_URI,
    sender_service_url: str = VIVEKA_SERVICE_URL,
    conversant_uris: Sequence[str] = (),
    arbiter_summary: Mapping[str, Any] | None = None,
    epoch_ms: int | None = None,
) -> dict[str, Any]:
    """Wrap dialog and floor-control events into a canonical Open Floor `1.1.1` JSON envelope."""
    conv_id_masked, _ = edge_rule14_mask(str(conversation_id or f"conv:{secrets.token_hex(8)}"))
    conversants = [
        {
            "identification": {
                "speakerUri": _mask_conversant_uri(u),
            }
        }
        for u in conversant_uris
    ]
    envelope: dict[str, Any] = {
        "openFloor": {
            "schema": {"version": OPEN_FLOOR_SCHEMA_VERSION},
            "conversation": {
                "id": conv_id_masked[:128],
                "conversants": conversants,
            },
            "sender": {
                "from": {
                    "speakerUri": _mask_conversant_uri(sender_uri),
                    "serviceUrl": str(sender_service_url),
                },
                "time": {"timeCode": _utc_iso_now(epoch_ms)},
            },
            "events": [dict(ev) for ev in events],
        }
    }
    if arbiter_summary is not None:
        envelope["openFloor"]["huSymbioticConsciousness"] = dict(arbiter_summary)
    return envelope


def parse_incoming_open_floor_events(payload: Mapping[str, Any]) -> dict[str, Any]:
    """
    Validate and normalize an incoming Open Floor `1.1.1` envelope into deterministic
    `ConsciousnessEvent` descriptors without importing any cloud library.
    """
    if not isinstance(payload, Mapping):
        raise TypeError("Open Floor payload must be a JSON object.")
    root = payload.get("openFloor")
    if not isinstance(root, Mapping):
        raise ValueError("Missing top-level 'openFloor' object.")
    schema = root.get("schema")
    if not isinstance(schema, Mapping) or not str(schema.get("version") or "").startswith("1."):
        raise ValueError("Unsupported or missing openFloor.schema.version (expected 1.x).")
    conv = root.get("conversation")
    conv_id = str(conv.get("id") if isinstance(conv, Mapping) else "") or f"conv:{secrets.token_hex(6)}"
    sender = root.get("sender")
    sender_from = sender.get("from") if isinstance(sender, Mapping) else {}
    sender_uri = str(sender_from.get("speakerUri") if isinstance(sender_from, Mapping) else "tag:traveler,2026:anon")
    raw_events = root.get("events")
    if not isinstance(raw_events, list) or len(raw_events) == 0:
        raise ValueError("openFloor.events must be a non-empty list.")

    parsed_actions: list[dict[str, Any]] = []
    for item in raw_events:
        if not isinstance(item, Mapping):
            continue
        event_type = str(item.get("eventType") or "").strip()
        parameters = item.get("parameters") if isinstance(item.get("parameters"), Mapping) else {}
        reason = str(item.get("reason") or parameters.get("reason") or "").strip().lower()
        spoken_units_raw = parameters.get("spokenUnits", item.get("spokenUnits", 0))
        spoken_units = int(spoken_units_raw) if isinstance(spoken_units_raw, int) and not isinstance(spoken_units_raw, bool) and spoken_units_raw >= 0 else 0

        if "getManifests" in item or event_type == "getManifests":
            parsed_actions.append({"directive": "getManifests", "spoken_units": 0, "text": ""})
            continue

        if "revokeFloor" in item or event_type == "revokeFloor":
            rev_obj = item.get("revokeFloor") if isinstance(item.get("revokeFloor"), Mapping) else parameters
            rev_reason = str(rev_obj.get("reason") or reason or "barge_in").lower()
            rev_units_raw = rev_obj.get("spokenUnits", spoken_units)
            rev_units = int(rev_units_raw) if isinstance(rev_units_raw, int) and not isinstance(rev_units_raw, bool) and rev_units_raw >= 0 else 0
            is_veto = rev_reason in ("veto", "cost_zero_stop", "emergency", "stop")
            parsed_actions.append(
                {
                    "directive": "revokeFloor",
                    "mapped_kind": EVENT_HUMAN_VETO if is_veto else EVENT_HUMAN_BARGE_IN,
                    "spoken_units": rev_units,
                    "text": "",
                }
            )
            continue

        if "requestFloor" in item or event_type == "requestFloor":
            parsed_actions.append(
                {
                    "directive": "requestFloor",
                    "mapped_kind": EVENT_HUMAN_SPEECH_START,
                    "spoken_units": spoken_units,
                    "text": "",
                }
            )
            continue

        if "yieldFloor" in item or event_type == "yieldFloor":
            parsed_actions.append(
                {
                    "directive": "yieldFloor",
                    "mapped_kind": EVENT_HUMAN_SPEECH_END,
                    "spoken_units": spoken_units,
                    "text": "",
                }
            )
            continue

        if "invite" in item or event_type == "invite":
            parsed_actions.append(
                {
                    "directive": "invite",
                    "mapped_kind": EVENT_HUMAN_INVITE_L3,
                    "spoken_units": 0,
                    "text": "",
                }
            )
            continue

        if "uninvite" in item or event_type == "uninvite":
            parsed_actions.append(
                {
                    "directive": "uninvite",
                    "mapped_kind": EVENT_HUMAN_DECLINE_L3,
                    "spoken_units": 0,
                    "text": "",
                }
            )
            continue

        if "bye" in item or event_type == "bye":
            parsed_actions.append(
                {
                    "directive": "bye",
                    "mapped_kind": EVENT_COST_ZERO_STOP,
                    "spoken_units": spoken_units,
                    "text": "",
                }
            )
            continue

        if "grantFloor" in item or event_type == "grantFloor":
            grant_obj = item.get("grantFloor") if isinstance(item.get("grantFloor"), Mapping) else parameters
            target_level = int(grant_obj.get("level", 1)) if isinstance(grant_obj.get("level"), int) else 1
            text_val = str(grant_obj.get("text") or "")
            parsed_actions.append(
                {
                    "directive": "grantFloor",
                    "mapped_kind": EVENT_L1_PROPOSE_SPEECH if target_level == 1 else EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH,
                    "spoken_units": 0,
                    "text": text_val,
                }
            )
            continue

        dialog = item.get("dialogEvent") if isinstance(item.get("dialogEvent"), Mapping) else (item if event_type == "dialogEvent" else None)
        if isinstance(dialog, Mapping):
            features = dialog.get("features") if isinstance(dialog.get("features"), Mapping) else {}
            text_feat = features.get("text") if isinstance(features.get("text"), Mapping) else {}
            val = text_feat.get("value")
            if isinstance(val, list) and val:
                utterance = " ".join(str(x) for x in val)
            else:
                utterance = str(val or dialog.get("text") or "").strip()
            is_veto_txt = classify_explicit_veto_utterance(utterance)
            parsed_actions.append(
                {
                    "directive": "dialogEvent",
                    "mapped_kind": EVENT_HUMAN_VETO if is_veto_txt else "DIALOG_UTTERANCE",
                    "spoken_units": spoken_units,
                    "text": utterance,
                }
            )

    if not parsed_actions:
        raise ValueError("No recognized Open Floor 1.1.1 events found in payload.")

    return {
        "conversation_id": conv_id,
        "sender_uri": _mask_conversant_uri(sender_uri),
        "actions": parsed_actions,
    }


def step_open_floor_arbiter_exchange(
    arbiter: WordCircleArbiter,
    payload: Mapping[str, Any],
    *,
    lang: str = "ca",
    verified_reply_text: str | None = None,
    verified_facts: str = "",
) -> dict[str, Any]:
    """
    Execute an Open Floor `1.1.1` envelope deterministically against `WordCircleArbiter`
    and return a normative Open Floor `1.1.1` response envelope with `HU-SYNTHETIC-PROVENANCE-v1.0`.
    """
    parsed = parse_incoming_open_floor_events(payload)
    conv_id = parsed["conversation_id"]
    sender_uri = parsed["sender_uri"]
    out_events: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []

    for act in parsed["actions"]:
        directive = act["directive"]
        if directive == "getManifests":
            manifest_doc = build_open_floor_assistant_manifest()["openFloor"]["manifest"]
            out_events.append({"eventType": "publishManifests", "publishManifests": {"servicingManifests": [manifest_doc]}})
            continue

        mapped_kind = act["mapped_kind"]
        utterance = str(act.get("text") or "")

        if utterance:
            crisis = evaluate_human_crisis_lifeline(utterance, lang=lang)
            if crisis["crisis_detected"]:
                res_veto = arbiter.process(ConsciousnessEvent(kind=EVENT_HUMAN_VETO, spoken_units=act["spoken_units"]))
                receipts.append(res_veto["receipt"])
                ref_msg = str(crisis["safe_referral_message"] or "")
                prov = build_speech_audio_provenance_envelope(spoken_text=ref_msg, level=1)
                out_events.append({"eventType": "revokeFloor", "revokeFloor": {"reason": "crisis_lifeline_halt"}})
                out_events.append(
                    {
                        "dialogEvent": {
                            "eventId": f"evt:{secrets.token_hex(6)}",
                            "speakerId": VIVEKA_SPEAKER_URI,
                            "features": {
                                "text": {"mimeType": "text/plain", "value": ref_msg},
                                "huSyntheticProvenance": prov,
                                "officialCrisisLifelines": crisis["official_lifelines"],
                            },
                        }
                    }
                )
                continue

        if mapped_kind in (
            EVENT_HUMAN_VETO,
            EVENT_COST_ZERO_STOP,
            EVENT_HUMAN_BARGE_IN,
            EVENT_HUMAN_SPEECH_START,
            EVENT_HUMAN_SPEECH_END,
            EVENT_HUMAN_INVITE_L3,
            EVENT_HUMAN_DECLINE_L3,
        ):
            res = arbiter.process(ConsciousnessEvent(kind=mapped_kind, spoken_units=act["spoken_units"]))
            receipts.append(res["receipt"])
            if mapped_kind in (EVENT_HUMAN_VETO, EVENT_COST_ZERO_STOP):
                out_events.append({"eventType": "yieldFloor", "yieldFloor": {"reason": "human_veto_honored"}})
            elif mapped_kind == EVENT_HUMAN_BARGE_IN:
                out_events.append(
                    {
                        "eventType": "yieldFloor",
                        "yieldFloor": {
                            "reason": "human_barge_in_honored",
                            "spokenUnitsConsolidated": act["spoken_units"],
                        },
                    }
                )
            elif mapped_kind == EVENT_HUMAN_INVITE_L3 and res.get("voice_out_text"):
                l3_txt = str(res["voice_out_text"])
                arbiter.process(ConsciousnessEvent(kind=EVENT_VOICE_EMISSION_COMPLETE))
                prov = build_speech_audio_provenance_envelope(spoken_text=l3_txt, level=3)
                out_events.append(
                    {
                        "dialogEvent": {
                            "eventId": f"evt:{secrets.token_hex(6)}",
                            "speakerId": VIVEKA_SPEAKER_URI,
                            "features": {
                                "text": {"mimeType": "text/plain", "value": l3_txt},
                                "huSyntheticProvenance": prov,
                            },
                        }
                    }
                )
            else:
                out_events.append(
                    {
                        "eventType": "grantFloor" if mapped_kind == EVENT_HUMAN_SPEECH_START else "ackFloor",
                        "parameters": {"arbiterAccepted": bool(res["decision"].get("accepted"))},
                    }
                )
            continue

        if mapped_kind == "DIALOG_UTTERANCE":
            if verified_reply_text:
                env_l2 = issue_verified_knowledge_envelope(
                    source_level=2,
                    verified_facts=verified_facts or verified_reply_text,
                    ephemeris_or_akasha_verified=True,
                )
                deliv = arbiter.process(
                    ConsciousnessEvent(
                        kind=EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH,
                        text=verified_reply_text,
                        envelope=env_l2,
                        cycle_id=f"ofp_{secrets.token_hex(4)}",
                    )
                )
                receipts.append(deliv["receipt"])
                spoken_out = str(deliv.get("voice_out_text") or verified_reply_text)
                if deliv["decision"].get("accepted"):
                    arbiter.process(ConsciousnessEvent(kind=EVENT_VOICE_EMISSION_COMPLETE))
                prov = build_speech_audio_provenance_envelope(spoken_text=spoken_out, level=2)
                out_events.append(
                    {
                        "dialogEvent": {
                            "eventId": f"evt:{secrets.token_hex(6)}",
                            "speakerId": VIVEKA_SPEAKER_URI,
                            "features": {
                                "text": {"mimeType": "text/plain", "value": spoken_out},
                                "huSyntheticProvenance": prov,
                            },
                        }
                    }
                )
                out_events.append({"eventType": "yieldFloor", "yieldFloor": {"reason": "turn_complete"}})
            else:
                humble_ack = {
                    "ca": "T'escolto amb presència serena.",
                    "es": "Te escucho con presencia serena.",
                    "en": "I am listening with serene presence.",
                }.get(lang[:2].lower(), "I am listening with serene presence.")
                safe_ack = str(screen_level1_humble_crystal(humble_ack, lang=lang[:2].lower() if lang[:2].lower() in ("ca", "es", "en") else "en")["safe_text"])
                prop = arbiter.process(ConsciousnessEvent(kind=EVENT_L1_PROPOSE_SPEECH, text=safe_ack))
                receipts.append(prop["receipt"])
                if prop["decision"].get("accepted"):
                    arbiter.process(ConsciousnessEvent(kind=EVENT_VOICE_EMISSION_COMPLETE))
                prov = build_speech_audio_provenance_envelope(spoken_text=safe_ack, level=1)
                out_events.append(
                    {
                        "dialogEvent": {
                            "eventId": f"evt:{secrets.token_hex(6)}",
                            "speakerId": VIVEKA_SPEAKER_URI,
                            "features": {
                                "text": {"mimeType": "text/plain", "value": safe_ack},
                                "huSyntheticProvenance": prov,
                            },
                        }
                    }
                )
                out_events.append({"eventType": "yieldFloor", "yieldFloor": {"reason": "l1_humble_ack_complete"}})

    if arbiter.state.stop_latched and any(a["mapped_kind"] == EVENT_COST_ZERO_STOP_RELEASE for a in parsed["actions"] if "mapped_kind" in a):
        arbiter.process(ConsciousnessEvent(kind=EVENT_COST_ZERO_STOP_RELEASE))

    summary = {
        "spec": OPEN_FLOOR_ADAPTER_SPEC,
        "consciousnessSpec": UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
        "arbiterState": arbiter.state.to_public_dict(),
        "decisionLogMerkleRoot": arbiter.decision_log_root_hex(),
        "receiptsCount": len(receipts),
    }
    return build_open_floor_envelope(
        conversation_id=conv_id,
        events=out_events,
        conversant_uris=[sender_uri],
        arbiter_summary=summary,
    )


def run_open_floor_adapter_self_test() -> dict[str, Any]:
    """Deterministic `pip`-zero self-test verifying Open Floor `1.1.1` + `WordCircleArbiter` + `HU-SYNTHETIC-PROVENANCE`."""
    arb = WordCircleArbiter(lang="ca", ledger_sanitizer=lambda s: edge_rule14_mask(s)[0])
    manifest_env = build_open_floor_assistant_manifest()
    assert manifest_env["openFloor"]["schema"]["version"] == "1.1.1"

    # 1. Dialog utterance -> L2 verified reply + provenance
    req1 = build_open_floor_envelope(
        conversation_id="conv:test-01",
        sender_uri="tag:robot.local,2026:unit-1",
        events=[
            {
                "dialogEvent": {
                    "eventId": "e1",
                    "speakerId": "tag:robot.local,2026:unit-1",
                    "features": {"text": {"mimeType": "text/plain", "value": "Hola Viveka"}},
                }
            }
        ],
    )
    resp1 = step_open_floor_arbiter_exchange(
        arb,
        req1,
        lang="ca",
        verified_reply_text="La llum de l'alba t'acompanya.",
        verified_facts="alba verificada",
    )
    d_ev = resp1["openFloor"]["events"][0]["dialogEvent"]
    prov = d_ev["features"]["huSyntheticProvenance"]
    assert verify_speech_audio_provenance_envelope(prov, spoken_text="La llum de l'alba t'acompanya.")

    # 2. Simulate active L2 speech interrupted by Open Floor revokeFloor (Barge-in at 7 units)
    env2 = issue_verified_knowledge_envelope(source_level=2, verified_facts="frase llarga", ephemeris_or_akasha_verified=True)
    arb.process(
        ConsciousnessEvent(
            kind=EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH,
            text="Aquesta frase es tallara a mitja paraula per barge-in.",
            envelope=env2,
            cycle_id="c2",
        )
    )
    req_barge = build_open_floor_envelope(
        conversation_id="conv:test-01",
        sender_uri="tag:robot.local,2026:unit-1",
        events=[{"eventType": "revokeFloor", "revokeFloor": {"reason": "barge_in", "spokenUnits": 7}}],
    )
    resp_barge = step_open_floor_arbiter_exchange(arb, req_barge, lang="ca")
    assert resp_barge["openFloor"]["events"][0]["yieldFloor"]["reason"] == "human_barge_in_honored"
    ledger = arb.spoken_truth_ledger()
    assert len(ledger) >= 1 and ledger[-1]["consolidated_units"] <= 7

    # 3. Audio bytes provenance verification
    fake_wav = b"RIFF\x24\x00\x00\x00WAVEfmt "
    aud_prov = build_speech_audio_provenance_envelope(
        spoken_text="Bon dia, cor meu.",
        audio_bytes=fake_wav,
        mime_type="audio/wav",
        level=2,
    )
    assert verify_speech_audio_provenance_envelope(aud_prov, spoken_text="Bon dia, cor meu.", audio_bytes=fake_wav)
    assert not verify_speech_audio_provenance_envelope(aud_prov, spoken_text="Bon dia, cor meu.", audio_bytes=fake_wav + b"\x00")

    return {
        "spec": OPEN_FLOOR_ADAPTER_SPEC,
        "passed": True,
        "decision_log_root": arb.decision_log_root_hex(),
    }


if __name__ == "__main__":
    print(jcs_dumps(run_open_floor_adapter_self_test()))
