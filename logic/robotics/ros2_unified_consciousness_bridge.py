# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
HU-UNIFIED-CONSCIOUSNESS v1.0 — Hybrid ROS 2 Bridge of One Consciousness and Three Levels
(`logic/robotics/ros2_unified_consciousness_bridge.py`).

One on-board piece joins the Word-Circle Arbiter (U1..U7, voice and memory) with the Embodied Symbiosis
Gate of Living Folio V (E1..E7, motion):

    /consciousness/human_event ──────────┐                          ┌──> /consciousness/voice_out_safe
    /consciousness/l1_utterance_proposed ┤                          ├──> /consciousness/soul_ledger_commit
    /consciousness/l2_verified_turn ─────┤   UnifiedConsciousness   ├──> /humanoid/cmd_vel_safe
    /consciousness/l3_meditation_event ──┤          Gate            └──> /diagnostics/maat_unified_consciousness_receipt
    /consciousness/voice_feedback ───────┤  (Word Circle + Q^3 body)
    /humanoid/cmd_vel_proposed ──────────┤
    /humanoid/cost_zero_stop · /humanoid/human_pose_q3 · /humanoid/vulnerable_presence

- Standard library only (+ the stdlib-only edge cores): no `rclpy` import, no `logic.engines`, no socket.
  `attach_to_rclpy_node()` receives the host robot's Node and message classes by dependency injection.
- A human veto or a cost-zero-stop closes the body (exact zero Twist) AND empties the three levels.
  A stale presence heartbeat stops the body and pauses the voice, but keeps a legitimate Level 3
  meditation: sensor silence stops the body, only the human's word or the stop button empties the mind.
- `voice_out_safe` is live speech for the person present (screened by U2/E5/E6); everything that is
  persisted or published (ledger, receipts) is Rule 14 masked and never contains the unspoken tail.
- Honest scope: soft-real-time supervisory software, NOT a safety-rated function, NOT a medical device
  and NO claim of phenomenal consciousness.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import threading
from typing import Any, Callable, Final, Mapping
import uuid

from logic.consciousness.unified_consciousness_core import (
    DEFAULT_ENVELOPE_TTL_MS,
    EVENT_COST_ZERO_STOP,
    EVENT_COST_ZERO_STOP_RELEASE,
    EVENT_DEPOSIT_SILENT_ENVELOPE,
    EVENT_HUMAN_BARGE_IN,
    EVENT_HUMAN_DECLINE_L3,
    EVENT_HUMAN_INVITE_L3,
    EVENT_HUMAN_SPEECH_END,
    EVENT_HUMAN_SPEECH_START,
    EVENT_HUMAN_VETO,
    EVENT_L1_PROPOSE_SPEECH,
    EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH,
    EVENT_L2_START_CYCLE,
    EVENT_L3_COMPLETE_MEDITATION,
    EVENT_L3_OFFER_GENTLE_HAND,
    EVENT_L3_START_MEDITATION,
    EVENT_PRESENCE_LOST,
    EVENT_VOICE_EMISSION_COMPLETE,
    UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
    ConsciousnessEvent,
    WordCircleArbiter,
    issue_verified_knowledge_envelope,
)
from logic.robotics.embodied_edge_core import ZERO_TWIST, canonical_leaf_bytes, to_fraction, verify_merkle_inclusion
from logic.robotics.ros2_embodied_symbiosis_bridge import EmbodiedSymbiosisGate, fill_ros2_twist_message

TOPIC_HUMAN_EVENT: Final[str] = "/consciousness/human_event"
TOPIC_L1_UTTERANCE_PROPOSED: Final[str] = "/consciousness/l1_utterance_proposed"
TOPIC_L2_VERIFIED_TURN: Final[str] = "/consciousness/l2_verified_turn"
TOPIC_L3_MEDITATION_EVENT: Final[str] = "/consciousness/l3_meditation_event"
TOPIC_VOICE_FEEDBACK: Final[str] = "/consciousness/voice_feedback"
TOPIC_VOICE_OUT_SAFE: Final[str] = "/consciousness/voice_out_safe"
TOPIC_SOUL_LEDGER_COMMIT: Final[str] = "/consciousness/soul_ledger_commit"
TOPIC_CMD_VEL_PROPOSED: Final[str] = "/humanoid/cmd_vel_proposed"
TOPIC_CMD_VEL_SAFE: Final[str] = "/humanoid/cmd_vel_safe"
TOPIC_COST_ZERO_STOP: Final[str] = "/humanoid/cost_zero_stop"
TOPIC_HUMAN_POSE_Q3: Final[str] = "/humanoid/human_pose_q3"
TOPIC_VULNERABLE_PRESENCE: Final[str] = "/humanoid/vulnerable_presence"
TOPIC_UNIFIED_RECEIPT: Final[str] = "/diagnostics/maat_unified_consciousness_receipt"

MCP_DIAMOND_ENDPOINT: Final[str] = "https://homouniversalis.ai/mcp/diamond"
MCP_UNIFIED_TOOL_NAME: Final[str] = "verify_unified_three_level_consciousness"
MCP_PROTOCOL_VERSION: Final[str] = "2026-07-28"
_MAX_JSON_MESSAGE_BYTES: Final[int] = 32 * 1024

_HUMAN_EVENT_MAP: Final[dict[str, str]] = {
    "speech_start": EVENT_HUMAN_SPEECH_START,
    "speech_end": EVENT_HUMAN_SPEECH_END,
    "barge_in": EVENT_HUMAN_BARGE_IN,
    "veto": EVENT_HUMAN_VETO,
    "invite_l3": EVENT_HUMAN_INVITE_L3,
    "decline_l3": EVENT_HUMAN_DECLINE_L3,
}


def _parse_json_message(msg: Any) -> dict[str, Any] | None:
    """Parse a `std_msgs/String` JSON payload (bounded, `float` literals kept as strings); `None` if malformed."""
    raw = msg if isinstance(msg, (str, Mapping)) else getattr(msg, "data", "")
    if isinstance(raw, Mapping):
        return dict(raw)
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > _MAX_JSON_MESSAGE_BYTES:
        return None
    try:
        payload = json.loads(raw or "{}", parse_float=str)
    except ValueError:
        return None
    return payload if isinstance(payload, dict) else None


def _opt_int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


class UnifiedConsciousnessGate:
    """
    Thread-safe on-board gate of One Consciousness: `mind` (Word-Circle Arbiter) + `body` (Embodied
    Symbiosis Gate). Every input returns the safe outputs plus privacy-preserving receipts (never raw
    speech, raw pose or soul keys).
    """

    def __init__(
        self,
        *,
        robot_name: str = "Humanoid Companion",
        lang: str = "ca",
        clock_ms: Callable[[], int] | None = None,
        body: EmbodiedSymbiosisGate | None = None,
        mind: WordCircleArbiter | None = None,
        ledger_sanitizer: Callable[[str], Any] | None = None,
    ) -> None:
        self.robot_name = str(robot_name)
        self.lang = lang if lang in ("ca", "es", "en") else "ca"
        self.body = body or EmbodiedSymbiosisGate(robot_name=robot_name, lang=self.lang, clock_ms=clock_ms)
        self.mind = mind or WordCircleArbiter(lang=self.lang, clock_ms=clock_ms, ledger_sanitizer=ledger_sanitizer)
        self._lock = threading.Lock()
        self._last_spoken_units: int | None = None

    # -- mind -----------------------------------------------------------------
    def _mind(self, event: ConsciousnessEvent) -> dict[str, Any]:
        result = self.mind.process(event)
        if result["decision"]["voice_action"] in ("cut", "emit"):
            with self._lock:
                self._last_spoken_units = None
        return result

    def on_voice_feedback(self, payload: Mapping[str, Any] | Any) -> dict[str, Any] | None:
        """TTS feedback: `{"spoken_units": k}` tracks the played-out index; `{"event": "complete"}` closes the emission."""
        data = _parse_json_message(payload)
        if data is None:
            return None
        units = _opt_int(data.get("spoken_units"))
        if units is not None:
            with self._lock:
                self._last_spoken_units = units
        if data.get("event") == "complete":
            return self._mind(ConsciousnessEvent(kind=EVENT_VOICE_EMISSION_COMPLETE))
        return None

    def on_human_event(self, payload: Mapping[str, Any] | Any) -> dict[str, Any]:
        """`{"event": speech_start|speech_end|barge_in|veto|veto_release|invite_l3|decline_l3, "spoken_units": k}`."""
        data = _parse_json_message(payload) or {}
        name = str(data.get("event") or "")
        if name == "veto_release":
            self.body.on_human_veto(False)
            return {"decision": None, "voice_out_text": None, "cmd_vel": None}
        kind = _HUMAN_EVENT_MAP.get(name)
        if kind is None:
            return {"decision": None, "voice_out_text": None, "cmd_vel": None, "rejected": "unknown_human_event"}
        with self._lock:
            fallback_units = self._last_spoken_units
        units = _opt_int(data.get("spoken_units"))
        result = self._mind(ConsciousnessEvent(kind=kind, spoken_units=units if units is not None else fallback_units))
        cmd = None
        if kind == EVENT_HUMAN_VETO:
            self.body.on_human_veto(True)
            cmd = self.body.filter_cmd_vel(ZERO_TWIST)
        return {**result, "cmd_vel": cmd}

    def on_cost_zero_stop(self, active: Any) -> dict[str, Any]:
        """`True` (or any non-`False`) latches the stop on body and mind; an explicit `False` releases both."""
        stop = active is not False
        self.body.on_cost_zero_stop(stop)
        with self._lock:
            units = self._last_spoken_units
        if stop:
            result = self._mind(ConsciousnessEvent(kind=EVENT_COST_ZERO_STOP, spoken_units=units))
            return {**result, "cmd_vel": self.body.filter_cmd_vel(ZERO_TWIST)}
        return {**self._mind(ConsciousnessEvent(kind=EVENT_COST_ZERO_STOP_RELEASE)), "cmd_vel": None}

    def on_l1_utterance(self, text: Any) -> dict[str, Any]:
        raw = text if isinstance(text, str) else getattr(text, "data", "")
        return self._mind(ConsciousnessEvent(kind=EVENT_L1_PROPOSE_SPEECH, text=raw if isinstance(raw, str) else ""))

    def on_l2_verified_turn(self, payload: Mapping[str, Any] | Any) -> dict[str, Any]:
        """
        `{"event": "start_cycle", "cycle_id": "..."}` registers an asynchronous L2 cycle without taking the floor;
        `{"silent": true, "verified_facts": "...", "cycle_id"?, "topic_hint"?, "ttl_ms"?}` deposits silently into
        the session Knowledge Vault without forcing speech; otherwise `{"text", "verified_facts", ...}` speaks on L2.
        """
        data = _parse_json_message(payload) or {}
        cycle_id = str(data.get("cycle_id") or "")
        if data.get("event") == "start_cycle":
            try:
                return self._mind(ConsciousnessEvent(kind=EVENT_L2_START_CYCLE, cycle_id=cycle_id))
            except (TypeError, ValueError) as exc:
                return {"decision": None, "voice_out_text": None, "rejected": f"malformed_l2_cycle:{type(exc).__name__}"}
        envelope = None
        try:
            envelope = issue_verified_knowledge_envelope(
                source_level=int(data.get("source_level", 2)) if not isinstance(data.get("source_level", 2), bool) else 0,
                verified_facts=str(data.get("verified_facts") or ""),
                claim_kinds=data.get("claim_kinds") if isinstance(data.get("claim_kinds"), list) else None,
            )
        except (TypeError, ValueError):
            envelope = None
        topic_hint = data.get("topic_hint") if isinstance(data.get("topic_hint"), str) else ""
        ttl_ms = data.get("ttl_ms", DEFAULT_ENVELOPE_TTL_MS)
        if data.get("silent") is True:
            try:
                return self._mind(
                    ConsciousnessEvent(
                        kind=EVENT_DEPOSIT_SILENT_ENVELOPE,
                        envelope=envelope,
                        cycle_id=cycle_id,
                        topic_hint=topic_hint,
                        ttl_ms=ttl_ms,
                    )
                )
            except (TypeError, ValueError) as exc:
                return {"decision": None, "voice_out_text": None, "rejected": f"malformed_silent_deposit:{type(exc).__name__}"}
        text = data.get("text") if isinstance(data.get("text"), str) else ""
        try:
            return self._mind(
                ConsciousnessEvent(
                    kind=EVENT_L2_DELIVER_ENVELOPE_AND_SPEECH,
                    text=text,
                    envelope=envelope,
                    cycle_id=cycle_id,
                    topic_hint=topic_hint,
                    ttl_ms=ttl_ms,
                )
            )
        except (TypeError, ValueError) as exc:
            return {"decision": None, "voice_out_text": None, "rejected": f"malformed_l2_turn:{type(exc).__name__}"}

    def on_l3_meditation_event(self, payload: Mapping[str, Any] | Any) -> dict[str, Any]:
        """`{"event": start|complete|gentle_offer, ...}`; numeric loads are strict ints, complexity a rational string."""
        data = _parse_json_message(payload) or {}
        name = str(data.get("event") or "")
        cycle_id = str(data.get("cycle_id") or "")
        topic_hint = data.get("topic_hint") if isinstance(data.get("topic_hint"), str) else ""
        try:
            if name == "start":
                event = ConsciousnessEvent(
                    kind=EVENT_L3_START_MEDITATION,
                    cycle_id=cycle_id,
                    queue_if_busy=data.get("queue_if_busy", False),
                    current_load_l=data.get("current_load_l", 0),
                    delta_load_l3=data.get("delta_load_l3", 0),
                    budget_b=data.get("budget_b", 250),
                    explicit_deep_request=data.get("explicit_deep_request", False),
                    complexity_score_q=to_fraction(data.get("complexity_score_q", 0), field="complexity_score_q"),
                )
            elif name == "complete":
                facts = data.get("verified_facts")
                env = issue_verified_knowledge_envelope(source_level=3, verified_facts=facts) if isinstance(facts, str) and facts.strip() else None
                event = ConsciousnessEvent(
                    kind=EVENT_L3_COMPLETE_MEDITATION,
                    text=str(data.get("synthesis_text") or ""),
                    envelope=env,
                    cycle_id=cycle_id,
                    topic_hint=topic_hint,
                    ttl_ms=data.get("ttl_ms", DEFAULT_ENVELOPE_TTL_MS),
                )
            elif name == "gentle_offer":
                event = ConsciousnessEvent(kind=EVENT_L3_OFFER_GENTLE_HAND, text=str(data.get("gentle_offer_text") or ""))
            else:
                return {"decision": None, "voice_out_text": None, "rejected": "unknown_l3_event"}
            return self._mind(event)
        except (TypeError, ValueError) as exc:
            return {"decision": None, "voice_out_text": None, "rejected": f"malformed_l3_event:{type(exc).__name__}"}

    # -- body -----------------------------------------------------------------
    def filter_cmd_vel(self, proposed: Any) -> dict[str, Any]:
        return self.body.filter_cmd_vel(proposed)

    def watchdog_tick(self) -> dict[str, Any] | None:
        """Stale heartbeat -> zero Twist and a paused voice (Level 3 meditation is preserved)."""
        stale = self.body.watchdog_tick()
        if stale is None:
            return None
        mind = None
        if self.mind.state.speaking_level:
            with self._lock:
                units = self._last_spoken_units
            mind = self._mind(ConsciousnessEvent(kind=EVENT_PRESENCE_LOST, spoken_units=units))
        return {"cmd_vel": stale, "mind": mind}


# ============================================================================
# OPTIONAL rclpy ADAPTER (DEPENDENCY INJECTION, NO rclpy IMPORT)
# ============================================================================

@dataclass
class UnifiedRos2BridgeHandle:
    gate: UnifiedConsciousnessGate
    node: Any
    publishers: dict[str, Any]
    subscriptions: dict[str, Any]
    timer: Any


def attach_to_rclpy_node(
    ros_node: Any,
    *,
    twist_cls: type,
    string_cls: type,
    bool_cls: type,
    gate: UnifiedConsciousnessGate | None = None,
    qos_depth: int = 10,
    watchdog_period_ms: int = 50,
) -> UnifiedRos2BridgeHandle:
    """
    Wire the unified gate into a live `rclpy.node.Node` (dependency injection: `geometry_msgs/Twist`,
    `std_msgs/String`, `std_msgs/Bool`). Consciousness topics carry JSON on `std_msgs/String`. Callbacks
    never raise into the executor: any failure publishes an exact zero Twist and stays silent.
    """
    g = gate or UnifiedConsciousnessGate()
    pubs = {
        TOPIC_VOICE_OUT_SAFE: ros_node.create_publisher(string_cls, TOPIC_VOICE_OUT_SAFE, qos_depth),
        TOPIC_SOUL_LEDGER_COMMIT: ros_node.create_publisher(string_cls, TOPIC_SOUL_LEDGER_COMMIT, qos_depth),
        TOPIC_CMD_VEL_SAFE: ros_node.create_publisher(twist_cls, TOPIC_CMD_VEL_SAFE, qos_depth),
        TOPIC_UNIFIED_RECEIPT: ros_node.create_publisher(string_cls, TOPIC_UNIFIED_RECEIPT, qos_depth),
    }

    def _publish_string(topic: str, data: str) -> None:
        msg = string_cls()
        msg.data = data
        pubs[topic].publish(msg)

    def _publish_twist(cmd: Mapping[str, Any] | None) -> None:
        if cmd is None:
            return
        pubs[TOPIC_CMD_VEL_SAFE].publish(fill_ros2_twist_message(twist_cls(), cmd["cmd_vel_safe"]))
        _publish_string(TOPIC_UNIFIED_RECEIPT, canonical_leaf_bytes(cmd["receipt"]).decode("utf-8"))

    def _publish_mind(result: Mapping[str, Any] | None) -> None:
        if not result or not result.get("receipt"):
            return
        if result.get("voice_out_text"):
            _publish_string(TOPIC_VOICE_OUT_SAFE, str(result["voice_out_text"]))
        entry = result.get("ledger_entry")
        if entry:
            _publish_string(TOPIC_SOUL_LEDGER_COMMIT, canonical_leaf_bytes(entry).decode("utf-8"))
        _publish_string(TOPIC_UNIFIED_RECEIPT, canonical_leaf_bytes(result["receipt"]).decode("utf-8"))

    def _zero() -> None:
        pubs[TOPIC_CMD_VEL_SAFE].publish(fill_ros2_twist_message(twist_cls(), ZERO_TWIST))

    def _guard(fn: Callable[[Any], None]) -> Callable[[Any], None]:
        def _cb(msg: Any) -> None:
            try:
                fn(msg)
            except Exception:  # noqa: BLE001 - fail-closed boundary: the executor must never see an exception
                _zero()

        return _cb

    def _on_human(msg: Any) -> None:
        result = g.on_human_event(msg)
        _publish_mind(result)
        _publish_twist(result.get("cmd_vel"))

    def _on_stop(msg: Any) -> None:
        result = g.on_cost_zero_stop(getattr(msg, "data", True))
        _publish_mind(result)
        _publish_twist(result.get("cmd_vel"))

    def _on_watchdog() -> None:
        try:
            result = g.watchdog_tick()
            if result is not None:
                _publish_twist(result["cmd_vel"])
                _publish_mind(result["mind"])
        except Exception:  # noqa: BLE001 - fail-closed boundary
            _zero()

    def _on_pose(msg: Any) -> None:
        g.body.on_human_pose(_parse_json_message(msg))

    subs = {
        TOPIC_HUMAN_EVENT: ros_node.create_subscription(string_cls, TOPIC_HUMAN_EVENT, _guard(_on_human), qos_depth),
        TOPIC_L1_UTTERANCE_PROPOSED: ros_node.create_subscription(
            string_cls, TOPIC_L1_UTTERANCE_PROPOSED, _guard(lambda m: _publish_mind(g.on_l1_utterance(m))), qos_depth
        ),
        TOPIC_L2_VERIFIED_TURN: ros_node.create_subscription(
            string_cls, TOPIC_L2_VERIFIED_TURN, _guard(lambda m: _publish_mind(g.on_l2_verified_turn(m))), qos_depth
        ),
        TOPIC_L3_MEDITATION_EVENT: ros_node.create_subscription(
            string_cls, TOPIC_L3_MEDITATION_EVENT, _guard(lambda m: _publish_mind(g.on_l3_meditation_event(m))), qos_depth
        ),
        TOPIC_VOICE_FEEDBACK: ros_node.create_subscription(
            string_cls, TOPIC_VOICE_FEEDBACK, _guard(lambda m: _publish_mind(g.on_voice_feedback(m))), qos_depth
        ),
        TOPIC_CMD_VEL_PROPOSED: ros_node.create_subscription(
            twist_cls, TOPIC_CMD_VEL_PROPOSED, _guard(lambda m: _publish_twist(g.filter_cmd_vel(m))), qos_depth
        ),
        TOPIC_COST_ZERO_STOP: ros_node.create_subscription(bool_cls, TOPIC_COST_ZERO_STOP, _guard(_on_stop), qos_depth),
        TOPIC_HUMAN_POSE_Q3: ros_node.create_subscription(string_cls, TOPIC_HUMAN_POSE_Q3, _guard(_on_pose), qos_depth),
        TOPIC_VULNERABLE_PRESENCE: ros_node.create_subscription(
            bool_cls, TOPIC_VULNERABLE_PRESENCE, _guard(lambda m: g.body.on_vulnerable_presence(getattr(m, "data", None))), qos_depth
        ),
    }
    timer = ros_node.create_timer(watchdog_period_ms / 1000, _on_watchdog)
    return UnifiedRos2BridgeHandle(gate=g, node=ros_node, publishers=pubs, subscriptions=subs, timer=timer)


# ============================================================================
# MCP / A2A PAYLOAD BUILDERS (ZERO SOCKETS)
# ============================================================================

def build_mcp_unified_consciousness_request(
    *,
    agent_name: str = "Viveka Unified Consciousness",
    l1_utterance_text: str = "",
    interruption: str = "none",
    spoken_units: int | None = None,
    l3_explicit_deep_request: bool = True,
    explicit_human_invitation: bool = True,
    ai_identity_disclosed: bool = True,
    budget_b: int = 250,
    lang: str = "en",
    request_id: str | None = None,
) -> dict[str, Any]:
    """JSON-RPC 2.0 `tools/call` body for `verify_unified_three_level_consciousness` (MCP 2026-07-28); no socket is opened."""
    if interruption not in ("none", "barge_in", "veto", "cost_zero_stop"):
        raise ValueError("interruption must be none, barge_in, veto or cost_zero_stop.")
    arguments: dict[str, Any] = {
        "agent_name": str(agent_name),
        "l1_utterance_text": str(l1_utterance_text),
        "interruption": interruption,
        "l3_explicit_deep_request": bool(l3_explicit_deep_request),
        "explicit_human_invitation": bool(explicit_human_invitation),
        "ai_identity_disclosed": bool(ai_identity_disclosed),
        "budget_b": int(budget_b),
        "lang": lang if lang in ("ca", "es", "en") else "en",
    }
    if spoken_units is not None:
        arguments["spoken_units"] = int(spoken_units)
    return {
        "jsonrpc": "2.0",
        "id": request_id or f"hu-unified-{uuid.uuid4().hex[:12]}",
        "method": "tools/call",
        "params": {
            "name": MCP_UNIFIED_TOOL_NAME,
            "arguments": arguments,
            "_meta": {
                "io.modelcontextprotocol/protocolVersion": MCP_PROTOCOL_VERSION,
                "io.modelcontextprotocol/clientCapabilities": {},
                "io.modelcontextprotocol/clientInfo": {"name": "hu-ros2-unified-consciousness-bridge", "version": "1.0.0"},
            },
        },
    }


def build_mcp_unified_http_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": MCP_PROTOCOL_VERSION,
        "Mcp-Method": "tools/call",
        "Mcp-Name": MCP_UNIFIED_TOOL_NAME,
    }


def build_a2a_unified_consciousness_task(
    receipt: Mapping[str, Any],
    *,
    agent_name: str = "Viveka Unified Consciousness",
    decision_log_root_hex: str = "",
    request_id: str | None = None,
) -> dict[str, Any]:
    """A2A `message/send` carrying a privacy-preserving Word-Circle receipt (never raw speech or soul keys)."""
    evidence = {
        "spec": UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
        "agent_name": str(agent_name),
        "event": receipt.get("event"),
        "accepted": receipt.get("accepted"),
        "floor_after": receipt.get("floor_after"),
        "l3_state_after": receipt.get("l3_state_after"),
        "levels_cancelled": list(receipt.get("levels_cancelled") or []),
        "seq": receipt.get("seq"),
        "leaf_hash": receipt.get("leaf_hash"),
        "leaf_index": receipt.get("leaf_index"),
        "tree_size": receipt.get("tree_size"),
        "decision_log_root": decision_log_root_hex,
    }
    return {
        "jsonrpc": "2.0",
        "id": request_id or f"hu-unified-a2a-{uuid.uuid4().hex[:12]}",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": f"hu-unified-msg-{uuid.uuid4().hex[:12]}",
                "role": "ROLE_USER",
                "parts": [
                    {"text": f"{UNIFIED_CONSCIOUSNESS_SPEC_VERSION} Word-Circle receipt for {agent_name}."},
                    {"data": evidence},
                ],
            }
        },
    }


# ============================================================================
# AUTONOMOUS SELF-TEST & CLI
# ============================================================================

def _percentiles(samples: list[int]) -> tuple[int, int, int]:
    ordered = sorted(samples)
    return ordered[len(ordered) // 2], ordered[min(len(ordered) - 1, (len(ordered) * 99) // 100)], ordered[-1]


def run_unified_bridge_self_test(iterations: int = 200) -> dict[str, Any]:
    """Deterministic self-test of the unified bridge (injected clock, zero network, integer-ns latencies)."""
    now = [1_000]
    gate = UnifiedConsciousnessGate(lang="en", clock_ms=lambda: now[0])
    moving = {"linear": {"x": "1/5", "y": "0", "z": "0"}, "angular": {"x": "0", "y": "0", "z": "1/10"}}
    gate.body.on_human_pose(("6/5", "0", "0"))
    gate.body.on_vulnerable_presence(False)
    moves = not gate.filter_cmd_vel(moving)["cmd_vel_safe"].is_zero()

    gate.on_human_event({"event": "speech_start"})
    gate.on_human_event({"event": "speech_end"})
    human_asked_for_depth = True
    gate.on_l3_meditation_event(
        {"event": "start", "current_load_l": 30, "delta_load_l3": 120, "budget_b": 250, "explicit_deep_request": human_asked_for_depth}
    )
    hallucination = gate.on_l1_utterance("Your Sun is at 23°41' Aries.")
    humble = hallucination["decision"]["humble_crystal"]["action"] == "humble_rephrase"
    gate.on_voice_feedback({"spoken_units": 9})
    barge = gate.on_human_event({"event": "barge_in"})
    barge_keeps_l3 = barge["decision"]["l3_state_after"] == "L3_MEDITATING"
    heard_only = barge["ledger_entry"] is not None and barge["ledger_entry"]["consolidated_units"] <= 9
    gate.on_human_event({"event": "speech_end"})

    veto = gate.on_human_event({"event": "veto"})
    veto_ok = bool(
        veto["decision"]["levels_cancelled"] == [1, 2, 3]
        and veto["decision"]["l3_state_after"] == "L3_CANCELLED"
        and veto["cmd_vel"]["cmd_vel_safe"].is_zero()
        and gate.filter_cmd_vel(moving)["cmd_vel_safe"].is_zero()
    )
    late = gate.on_l3_meditation_event({"event": "complete", "synthesis_text": "late synthesis"})
    late_dropped = late["decision"]["accepted"] is False
    gate.on_human_event({"event": "veto_release"})
    gate.on_human_event({"event": "speech_start"})
    gate.on_human_event({"event": "speech_end"})

    now[0] += 251
    stale = gate.watchdog_tick()
    stale_zero = stale is not None and stale["cmd_vel"]["cmd_vel_safe"].is_zero()
    gate.body.on_human_pose(("6/5", "0", "0"))

    samples: list[int] = []
    last: dict[str, Any] = {}
    for i in range(max(1, int(iterations))):
        kind = "speech_start" if i % 2 == 0 else "speech_end"
        res = gate.on_human_event({"event": kind})
        samples.append(int(res["receipt"]["decision_latency_ns"]))
        last = res["receipt"]
    p50, p99, p_max = _percentiles(samples)
    body_samples = [int(gate.filter_cmd_vel(moving)["receipt"]["decision_latency_ns"]) for _ in range(max(1, int(iterations)))]
    b50, b99, b_max = _percentiles(body_samples)

    proof = gate.mind.prove_receipt(last["leaf_index"])
    inclusion_ok = verify_merkle_inclusion(
        bytes.fromhex(proof["leaf_hash"]),
        proof["leaf_index"],
        proof["tree_size"],
        [bytes.fromhex(n) for n in proof["audit_path"]],
        bytes.fromhex(gate.mind.decision_log_root_hex()),
    )
    checks = {
        "personal_zone_motion_allowed": bool(moves),
        "l1_hallucination_humbled": bool(humble),
        "barge_in_preserves_l3": bool(barge_keeps_l3),
        "spoken_truth_prefix_only": bool(heard_only),
        "veto_empties_three_levels_and_zero_twist": bool(veto_ok),
        "late_l3_result_dropped_after_veto": bool(late_dropped),
        "stale_heartbeat_zero_twist": bool(stale_zero),
        "receipt_rfc6962_inclusion": bool(inclusion_ok),
    }
    return {
        "spec": UNIFIED_CONSCIOUSNESS_SPEC_VERSION,
        "self_test_only": True,
        "all_invariants_passed": bool(all(checks.values())),
        "checks": checks,
        "iterations": len(samples),
        "arbiter_latency_ns_p50": p50,
        "arbiter_latency_ns_p99": p99,
        "arbiter_latency_ns_max": p_max,
        "body_gate_latency_ns_p50": b50,
        "body_gate_latency_ns_p99": b99,
        "body_gate_latency_ns_max": b_max,
        "decision_log_root": gate.mind.decision_log_root_hex(),
        "safety_rated_function": False,
    }


if __name__ == "__main__":
    print(canonical_leaf_bytes(run_unified_bridge_self_test()).decode("utf-8"))
