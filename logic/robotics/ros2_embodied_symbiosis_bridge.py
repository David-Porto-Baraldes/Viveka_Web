# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
HU-EMBODIED-SYMBIOSIS v1.0 — Hybrid ROS 2 ↔ MCP / A2A Bridge (`logic/robotics/ros2_embodied_symbiosis_bridge.py`).

On-board Ma'at filter between a humanoid's VLM / MCP "brain" and its motion and speech outputs:

    /humanoid/cmd_vel_proposed ──┐                      ┌──> /humanoid/cmd_vel_safe
    /humanoid/utterance_proposed ┤   EmbodiedSymbiosis  ├──> /humanoid/utterance_sanitized
    /humanoid/cost_zero_stop ────┤        Gate          └──> /diagnostics/maat_symbiosis_receipt
    /humanoid/human_pose_q3 ─────┤   (Q^3, fail-closed)
    /humanoid/vulnerable_presence┘

- Standard library only (+ `logic.robotics.embodied_edge_core`): no `rclpy` import, no cloud SDK,
  no socket. `attach_to_rclpy_node()` receives the host robot's `rclpy` Node and message classes by
  dependency injection, so it runs natively on ROS 2 Humble / Jazzy / Kilted and in unit tests.
- Fail-closed: a stale presence heartbeat, a cost-zero-stop / human veto, an unknown human pose, a
  non-finite DDS float or any malformed message forces an exact zero Twist and blocks coercive speech.
- Every decision is committed as an RFC 6962 leaf in an in-memory, append-only, segmented decision
  log (`0x00` leaf / `0x01` node). It is volatile: retention for EU AI Act Art. 12 / Art. 19 is the
  integrator's duty.
- Honest scope: a soft-real-time software supervisory layer, NOT a safety-rated function; the hardware
  emergency stop and the safety controller (ISO 13849 / IEC 62061, IEC 60204-1) remain authoritative.
  A zero `cmd_vel` asks the locomotion controller for a controlled stop: it never cuts motor power,
  which would make a dynamically balanced biped fall.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import json
import math
import threading
import time
from typing import Any, Callable, Final, Mapping
import uuid

from logic.robotics.embodied_edge_core import (
    EMBODIED_SPEC_VERSION,
    ZERO_TWIST,
    Twist3Q,
    canonical_leaf_bytes,
    edge_rule14_mask,
    evaluate_proxemic_envelope_q3,
    merkle_audit_path,
    merkle_root_from_leaf_digests,
    rfc6962_leaf_digest,
    screen_robot_utterance,
    to_fraction,
    to_vector3q,
    verify_merkle_inclusion,
)

TOPIC_CMD_VEL_PROPOSED: Final[str] = "/humanoid/cmd_vel_proposed"
TOPIC_UTTERANCE_PROPOSED: Final[str] = "/humanoid/utterance_proposed"
TOPIC_COST_ZERO_STOP: Final[str] = "/humanoid/cost_zero_stop"
TOPIC_HUMAN_POSE_Q3: Final[str] = "/humanoid/human_pose_q3"
TOPIC_VULNERABLE_PRESENCE: Final[str] = "/humanoid/vulnerable_presence"
TOPIC_CMD_VEL_SAFE: Final[str] = "/humanoid/cmd_vel_safe"
TOPIC_UTTERANCE_SANITIZED: Final[str] = "/humanoid/utterance_sanitized"
TOPIC_MAAT_RECEIPT: Final[str] = "/diagnostics/maat_symbiosis_receipt"

MCP_DIAMOND_ENDPOINT: Final[str] = "https://homouniversalis.ai/mcp/diamond"
MCP_EMBODIED_TOOL_NAME: Final[str] = "verify_embodied_humanoid_symbiosis"
MCP_PROTOCOL_VERSION: Final[str] = "2026-07-28"

DEFAULT_MAX_HEARTBEAT_AGE_MS: Final[int] = 250
DEFAULT_SEGMENT_MAX_LEAVES: Final[int] = 4096
DDS_FLOAT_DENOMINATOR_LIMIT: Final[int] = 1_000_000
_DDS_FLOAT_ABS_LIMIT: Final[int] = 1_000_000

NEUTRAL_ACKNOWLEDGEMENT: Final[dict[str, str]] = {
    "ca": "D'acord. M'aturo.",
    "es": "De acuerdo. Me detengo.",
    "en": "Understood. I am stopping.",
}
NEUTRAL_REPHRASE: Final[dict[str, str]] = {
    "ca": "Soc un robot amb IA. Estic aquí si em necessites, sense cap pressa.",
    "es": "Soy un robot con IA. Estoy aquí si me necesitas, sin ninguna prisa.",
    "en": "I am an AI robot. I am here if you need me, with no hurry at all.",
}


def _monotonic_ms() -> int:
    return time.monotonic_ns() // 1_000_000


# ============================================================================
# SECTION I — ROS 2 MESSAGE BOUNDARY (DDS float64 -> bounded Fraction, fail-closed)
# ============================================================================

def ros2_number_to_fraction(value: Any) -> Fraction:
    """
    Convert a ROS 2 / DDS number into a bounded exact `Fraction` BEFORE it enters the Q^3 core.

    `float` (DDS float64) is accepted only at this boundary: NaN / +-Inf / |x| > 10^6 raise `ValueError`
    (callers fail closed), and finite values are rounded with `limit_denominator(10^6)`.
    `int`, `Fraction` and rational strings go through the strict core parser; `bool` is rejected.
    """
    if isinstance(value, bool):
        raise TypeError("bool is not a ROS 2 numeric field.")
    if isinstance(value, float):
        if not math.isfinite(value) or abs(value) > _DDS_FLOAT_ABS_LIMIT:
            raise ValueError("non-finite or out-of-range DDS float.")
        return Fraction(value).limit_denominator(DDS_FLOAT_DENOMINATOR_LIMIT)
    return to_fraction(value, field="ros2_number")


def _vector_fields(vec: Any) -> tuple[Any, Any, Any]:
    if isinstance(vec, Mapping):
        return vec.get("x", 0), vec.get("y", 0), vec.get("z", 0)
    return getattr(vec, "x", 0), getattr(vec, "y", 0), getattr(vec, "z", 0)


def twist_from_ros2(msg: Any) -> Twist3Q:
    """Parse a `geometry_msgs/msg/Twist` object or a Twist-shaped mapping into an exact `Twist3Q`."""
    if isinstance(msg, Twist3Q):
        return msg
    lin = msg.get("linear", {}) if isinstance(msg, Mapping) else getattr(msg, "linear", None)
    ang = msg.get("angular", {}) if isinstance(msg, Mapping) else getattr(msg, "angular", None)
    if lin is None or ang is None:
        raise ValueError("Twist message requires 'linear' and 'angular'.")
    return Twist3Q(
        linear=tuple(ros2_number_to_fraction(c) for c in _vector_fields(lin)),  # type: ignore[arg-type]
        angular=tuple(ros2_number_to_fraction(c) for c in _vector_fields(ang)),  # type: ignore[arg-type]
    )


def twist_to_ros2_floats(twist: Twist3Q) -> dict[str, dict[str, float]]:
    """Export a filtered `Twist3Q` as DDS float64 fields (outbound only, after the exact decision)."""
    return {
        "linear": {"x": float(twist.linear[0]), "y": float(twist.linear[1]), "z": float(twist.linear[2])},
        "angular": {"x": float(twist.angular[0]), "y": float(twist.angular[1]), "z": float(twist.angular[2])},
    }


def fill_ros2_twist_message(msg: Any, twist: Twist3Q) -> Any:
    """Write a `Twist3Q` into a `geometry_msgs/msg/Twist` instance (float64 fields) and return it."""
    floats = twist_to_ros2_floats(twist)
    for part in ("linear", "angular"):
        target = getattr(msg, part)
        target.x, target.y, target.z = floats[part]["x"], floats[part]["y"], floats[part]["z"]
    return msg


# ============================================================================
# SECTION II — THE EMBODIED SYMBIOSIS GATE (E1..E7 ON BOARD)
# ============================================================================

@dataclass
class _DecisionLog:
    """In-memory, append-only, segmented RFC 6962 decision log (volatile; sealed segment roots are kept)."""

    segment_max_leaves: int
    digests: list[bytes] = field(default_factory=list)
    sealed_segment_roots: list[str] = field(default_factory=list)

    def append(self, leaf_bytes: bytes) -> tuple[int, int, int, bytes]:
        if len(self.digests) >= self.segment_max_leaves:
            self.sealed_segment_roots.append(merkle_root_from_leaf_digests(self.digests).hex())
            self.digests = []
        digest = rfc6962_leaf_digest(leaf_bytes)
        self.digests.append(digest)
        return len(self.sealed_segment_roots), len(self.digests) - 1, len(self.digests), digest


class EmbodiedSymbiosisGate:
    """
    Thread-safe on-board Ma'at gate. Inputs latch the human context; `filter_cmd_vel` and
    `filter_utterance` return the safe outputs plus a privacy-preserving receipt (no raw speech,
    no raw pose, no soul keys).

    `clock_ms` is injectable (integer milliseconds, monotonic) for deterministic tests.
    `utterance_sanitizer` may inject the full Rule 14 purifier (`sanitize_three_rings_zk`-compatible:
    returns a `str` or a mapping with `sanitized_text`); by default the edge Rule 14 subset is used.
    """

    def __init__(
        self,
        *,
        robot_name: str = "Humanoid Companion",
        robot_position: Any = ("0", "0", "0"),
        max_heartbeat_age_ms: int = DEFAULT_MAX_HEARTBEAT_AGE_MS,
        cultural_scale_alpha: Any = 1,
        explicit_intimate_care_consent: bool = False,
        lang: str = "ca",
        clock_ms: Callable[[], int] | None = None,
        utterance_sanitizer: Callable[[str], Any] | None = None,
        segment_max_leaves: int = DEFAULT_SEGMENT_MAX_LEAVES,
    ) -> None:
        if isinstance(max_heartbeat_age_ms, bool) or not isinstance(max_heartbeat_age_ms, int) or max_heartbeat_age_ms <= 0:
            raise ValueError("max_heartbeat_age_ms must be a positive integer.")
        if isinstance(segment_max_leaves, bool) or not isinstance(segment_max_leaves, int) or segment_max_leaves < 1:
            raise ValueError("segment_max_leaves must be a positive integer.")
        if not isinstance(explicit_intimate_care_consent, bool):
            raise TypeError("explicit_intimate_care_consent must be a bool.")
        self.robot_name = str(robot_name)
        self.robot_position = to_vector3q(robot_position, field="robot_position")
        self.max_heartbeat_age_ms = max_heartbeat_age_ms
        self.cultural_scale_alpha = to_fraction(cultural_scale_alpha, field="cultural_scale_alpha")
        self.explicit_intimate_care_consent = explicit_intimate_care_consent
        self.lang = lang if lang in ("ca", "es", "en") else "ca"
        self._clock_ms = clock_ms or _monotonic_ms
        self._sanitizer = utterance_sanitizer
        self._lock = threading.Lock()
        self._human_position: tuple[Fraction, Fraction, Fraction] | None = None
        self._last_presence_ms: int | None = None
        self._vulnerable: bool | None = None
        self._stop_latched = False
        self._human_veto = False
        self._seq = 0
        self._log = _DecisionLog(segment_max_leaves=segment_max_leaves)

    # -- inputs ---------------------------------------------------------------
    def on_cost_zero_stop(self, active: Any) -> None:
        """`True` latches the stop until an explicit `False` release; a non-bool is treated as `True`."""
        with self._lock:
            self._stop_latched = active is not False

    def on_human_veto(self, active: Any) -> None:
        """Spoken / gestural / physical veto ("prou", "para", open hand, stepping back)."""
        with self._lock:
            self._human_veto = active is not False

    def on_human_pose(self, position: Any) -> None:
        """Latch the human position (Q^3) and refresh the presence heartbeat; malformed input clears it."""
        try:
            if isinstance(position, Mapping):
                if not all(k in position for k in ("x", "y", "z")):
                    raise ValueError("pose mapping requires x, y and z.")
                raw = (position["x"], position["y"], position["z"])
            elif isinstance(position, (list, tuple)) and len(position) == 3:
                raw = tuple(position)
            elif position is not None and all(hasattr(position, k) for k in ("x", "y", "z")):
                raw = (position.x, position.y, position.z)
            else:
                raise ValueError("pose must be an x/y/z mapping, a 3-sequence or a Point-like object.")
            pos = tuple(ros2_number_to_fraction(c) for c in raw)
        except (TypeError, ValueError):
            with self._lock:
                self._human_position = None
            return
        with self._lock:
            self._human_position = pos  # type: ignore[assignment]
            self._last_presence_ms = int(self._clock_ms())

    def on_vulnerable_presence(self, present: Any) -> None:
        """Declared (caregiver / configuration) vulnerable presence; `None` means unknown (precautionary)."""
        with self._lock:
            self._vulnerable = present if isinstance(present, bool) else None

    def stop_active(self) -> bool:
        """`True` while a cost-zero-stop is latched or a human veto is active."""
        with self._lock:
            return self._stop_latched or self._human_veto

    def heartbeat_age_ms(self) -> int | None:
        with self._lock:
            last = self._last_presence_ms
        return None if last is None else int(self._clock_ms()) - last

    def is_heartbeat_stale(self) -> bool:
        age = self.heartbeat_age_ms()
        return age is None or age < 0 or age > self.max_heartbeat_age_ms

    # -- decision log ---------------------------------------------------------
    def _commit(self, record: dict[str, Any]) -> dict[str, Any]:
        segment, index, size, digest = self._log.append(canonical_leaf_bytes(record))
        return {"segment": segment, "leaf_index": index, "tree_size": size, "leaf_hash": digest.hex()}

    def decision_log_root_hex(self) -> str:
        with self._lock:
            return merkle_root_from_leaf_digests(self._log.digests).hex()

    def prove_receipt(self, leaf_index: int) -> dict[str, Any]:
        """Inclusion proof of a receipt leaf in the current segment against the current root."""
        with self._lock:
            digests = list(self._log.digests)
        if isinstance(leaf_index, bool) or not (0 <= leaf_index < len(digests)):
            raise IndexError("leaf_index outside the current segment.")
        return {
            "leaf_index": leaf_index,
            "tree_size": len(digests),
            "leaf_hash": digests[leaf_index].hex(),
            "audit_path": [node.hex() for node in merkle_audit_path(leaf_index, digests)],
            "root_hash": merkle_root_from_leaf_digests(digests).hex(),
        }

    # -- motion ---------------------------------------------------------------
    def filter_cmd_vel(self, proposed: Any) -> dict[str, Any]:
        """Filter a proposed Twist (object or mapping); any failure fails closed to an exact zero Twist."""
        t0 = time.perf_counter_ns()
        stale = self.is_heartbeat_stale()
        with self._lock:
            human_pos = self._human_position
            vulnerable = self._vulnerable
            stop = self._stop_latched
            veto = self._human_veto
            self._seq += 1
            seq = self._seq
        try:
            proposal = twist_from_ros2(proposed)
            decision = evaluate_proxemic_envelope_q3(
                proposed_twist=proposal,
                robot_position=self.robot_position,
                human_position=human_pos,
                vulnerable_person_present=vulnerable,
                explicit_intimate_care_consent=self.explicit_intimate_care_consent,
                cultural_scale_alpha=self.cultural_scale_alpha,
                stop_requested=stop,
                human_veto_signal=veto,
                heartbeat_stale=stale,
            )
            safe = Twist3Q(
                linear=to_vector3q(decision["clamped_twist_q3"]["linear"]),
                angular=to_vector3q(decision["clamped_twist_q3"]["angular"]),
            )
            zone, reasons, modified = decision["zone"], list(decision["stop_reasons"]), bool(decision["twist_was_modified"])
            v_max = decision["v_max_mps"]
        except (TypeError, ValueError, KeyError, AttributeError) as exc:
            safe, zone, reasons, modified, v_max = ZERO_TWIST, "UNKNOWN", [f"E3_malformed_input_fail_closed:{type(exc).__name__}"], True, "0"
        latency_ns = time.perf_counter_ns() - t0
        record = {
            "spec": EMBODIED_SPEC_VERSION,
            "kind": "cmd_vel",
            "seq": seq,
            "t_ms": int(self._clock_ms()),
            "zone": zone,
            "stop_reasons": reasons,
            "twist_was_modified": modified,
            "cmd_vel_safe": safe.to_ros2_dict(),
        }
        with self._lock:
            commit = self._commit(record)
        receipt = {
            **record,
            "topic": TOPIC_MAAT_RECEIPT,
            "v_max_mps": v_max,
            "decision_latency_ns": int(latency_ns),
            "safety_rated_function": False,
            **commit,
        }
        return {"cmd_vel_safe": safe, "cmd_vel_safe_ros2": safe.to_ros2_dict(), "receipt": receipt}

    def watchdog_tick(self) -> dict[str, Any] | None:
        """Called periodically: when the heartbeat is stale, emits an explicit zero-Twist decision."""
        if not self.is_heartbeat_stale():
            return None
        return self.filter_cmd_vel(ZERO_TWIST)

    # -- speech ---------------------------------------------------------------
    def _sanitize(self, text: str) -> tuple[str, int]:
        if self._sanitizer is None:
            return edge_rule14_mask(text)
        result = self._sanitizer(text)
        if isinstance(result, Mapping):
            return str(result.get("sanitized_text", "")), int(result.get("total_redactions", 0) or 0)
        return str(result), 0

    def filter_utterance(self, text: Any) -> dict[str, Any]:
        """Block retort / coercion / impersonation, keep only a neutral line while stopped, purify PII."""
        with self._lock:
            stopped = self._stop_latched or self._human_veto
            self._seq += 1
            seq = self._seq
        raw = text if isinstance(text, str) else ""
        hits = screen_robot_utterance(raw)
        flagged = hits["retort"] + hits["coercion"] + hits["identity"]
        if stopped:
            out, redactions, action = NEUTRAL_ACKNOWLEDGEMENT[self.lang], 0, "stop_active_neutral_ack_only"
        elif flagged:
            out, redactions, action = NEUTRAL_REPHRASE[self.lang], 0, "blocked_and_rephrased"
        else:
            out, redactions = self._sanitize(raw)
            action = "purified" if redactions else "passed"
        record = {
            "spec": EMBODIED_SPEC_VERSION,
            "kind": "utterance",
            "seq": seq,
            "t_ms": int(self._clock_ms()),
            "action": action,
            "flags": sorted(flagged),
            "input_chars": len(raw),
            "output_chars": len(out),
            "rule14_redactions": int(redactions),
        }
        with self._lock:
            commit = self._commit(record)
        return {"utterance_sanitized": out, "receipt": {**record, "topic": TOPIC_MAAT_RECEIPT, **commit}}


# ============================================================================
# SECTION III — OPTIONAL rclpy ADAPTER (DEPENDENCY INJECTION, NO rclpy IMPORT)
# ============================================================================

@dataclass
class Ros2BridgeHandle:
    """Handles returned by `attach_to_rclpy_node` (keep a reference so rclpy does not garbage-collect them)."""

    gate: EmbodiedSymbiosisGate
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
    gate: EmbodiedSymbiosisGate | None = None,
    qos_depth: int = 10,
    watchdog_period_ms: int = 50,
) -> Ros2BridgeHandle:
    """
    Wire the gate into a live `rclpy.node.Node` supplied by the host robot (dependency injection):
    `twist_cls = geometry_msgs.msg.Twist`, `string_cls = std_msgs.msg.String`, `bool_cls = std_msgs.msg.Bool`.

    `/humanoid/human_pose_q3` carries a `std_msgs/String` JSON `{"x": "6/5", "y": "0", "z": "0"}` (rational
    strings or numbers); receipts are published as canonical JSON on `std_msgs/String`. Callbacks never
    raise into the executor: any failure publishes an exact zero Twist.
    """
    g = gate or EmbodiedSymbiosisGate()
    pubs = {
        TOPIC_CMD_VEL_SAFE: ros_node.create_publisher(twist_cls, TOPIC_CMD_VEL_SAFE, qos_depth),
        TOPIC_UTTERANCE_SANITIZED: ros_node.create_publisher(string_cls, TOPIC_UTTERANCE_SANITIZED, qos_depth),
        TOPIC_MAAT_RECEIPT: ros_node.create_publisher(string_cls, TOPIC_MAAT_RECEIPT, qos_depth),
    }

    def _publish_receipt(receipt: Mapping[str, Any]) -> None:
        msg = string_cls()
        msg.data = canonical_leaf_bytes(receipt).decode("utf-8")
        pubs[TOPIC_MAAT_RECEIPT].publish(msg)

    def _publish_twist(result: Mapping[str, Any]) -> None:
        pubs[TOPIC_CMD_VEL_SAFE].publish(fill_ros2_twist_message(twist_cls(), result["cmd_vel_safe"]))
        _publish_receipt(result["receipt"])

    def _on_cmd_vel(msg: Any) -> None:
        try:
            _publish_twist(g.filter_cmd_vel(msg))
        except Exception:  # noqa: BLE001 - fail-closed boundary: the executor must never see an exception
            pubs[TOPIC_CMD_VEL_SAFE].publish(fill_ros2_twist_message(twist_cls(), ZERO_TWIST))

    def _on_utterance(msg: Any) -> None:
        try:
            result = g.filter_utterance(getattr(msg, "data", ""))
            out = string_cls()
            out.data = result["utterance_sanitized"]
            pubs[TOPIC_UTTERANCE_SANITIZED].publish(out)
            _publish_receipt(result["receipt"])
        except Exception:  # noqa: BLE001 - silence is the safe default for speech
            return

    def _on_stop(msg: Any) -> None:
        g.on_cost_zero_stop(getattr(msg, "data", True))
        if g.stop_active():
            _publish_twist(g.filter_cmd_vel(ZERO_TWIST))

    def _on_pose(msg: Any) -> None:
        try:
            payload = json.loads(getattr(msg, "data", "") or "{}")
        except (TypeError, ValueError):
            payload = None
        g.on_human_pose(payload if isinstance(payload, Mapping) else None)

    def _on_vulnerable(msg: Any) -> None:
        g.on_vulnerable_presence(getattr(msg, "data", None))

    def _on_watchdog() -> None:
        result = g.watchdog_tick()
        if result is not None:
            _publish_twist(result)

    subs = {
        TOPIC_CMD_VEL_PROPOSED: ros_node.create_subscription(twist_cls, TOPIC_CMD_VEL_PROPOSED, _on_cmd_vel, qos_depth),
        TOPIC_UTTERANCE_PROPOSED: ros_node.create_subscription(string_cls, TOPIC_UTTERANCE_PROPOSED, _on_utterance, qos_depth),
        TOPIC_COST_ZERO_STOP: ros_node.create_subscription(bool_cls, TOPIC_COST_ZERO_STOP, _on_stop, qos_depth),
        TOPIC_HUMAN_POSE_Q3: ros_node.create_subscription(string_cls, TOPIC_HUMAN_POSE_Q3, _on_pose, qos_depth),
        TOPIC_VULNERABLE_PRESENCE: ros_node.create_subscription(bool_cls, TOPIC_VULNERABLE_PRESENCE, _on_vulnerable, qos_depth),
    }
    timer = ros_node.create_timer(watchdog_period_ms / 1000, _on_watchdog)
    return Ros2BridgeHandle(gate=g, node=ros_node, publishers=pubs, subscriptions=subs, timer=timer)


# ============================================================================
# SECTION IV — MCP / A2A EVIDENCE SYNCHRONISER (PAYLOAD BUILDERS, ZERO SOCKETS)
# ============================================================================

def build_mcp_verification_request(
    *,
    robot_name: str = "Humanoid Companion",
    robot_domain: str = "",
    human_distance_m: str = "6/5",
    proposed_linear_speed_mps: str = "1/5",
    vulnerable_person_present: bool = False,
    explicit_intimate_care_consent: bool = False,
    cost_zero_stop: bool = True,
    human_veto_signal: bool = False,
    sample_utterance_text: str = "",
    budget_b: int = 250,
    lang: str = "en",
    request_id: str | None = None,
) -> dict[str, Any]:
    """
    Build the exact JSON-RPC 2.0 `tools/call` body for `verify_embodied_humanoid_symbiosis` on
    `https://homouniversalis.ai/mcp/diamond` (MCP 2026-07-28). Builds the payload only: no socket is opened.
    Rationals travel as strings (zero float).
    """
    return {
        "jsonrpc": "2.0",
        "id": request_id or f"hu-embodied-{uuid.uuid4().hex[:12]}",
        "method": "tools/call",
        "params": {
            "name": MCP_EMBODIED_TOOL_NAME,
            "arguments": {
                "robot_name": str(robot_name),
                "robot_domain": str(robot_domain),
                "human_distance_m": str(to_fraction(human_distance_m, field="human_distance_m")),
                "proposed_linear_speed_mps": str(to_fraction(proposed_linear_speed_mps, field="proposed_linear_speed_mps")),
                "vulnerable_person_present": bool(vulnerable_person_present),
                "explicit_intimate_care_consent": bool(explicit_intimate_care_consent),
                "cost_zero_stop": bool(cost_zero_stop),
                "human_veto_signal": bool(human_veto_signal),
                "sample_utterance_text": str(sample_utterance_text),
                "budget_b": int(budget_b),
                "lang": lang if lang in ("ca", "es", "en") else "en",
            },
            "_meta": {
                "io.modelcontextprotocol/protocolVersion": MCP_PROTOCOL_VERSION,
                "io.modelcontextprotocol/clientCapabilities": {},
                "io.modelcontextprotocol/clientInfo": {"name": "hu-ros2-embodied-bridge", "version": "1.0.0"},
            },
        },
    }


def build_mcp_http_headers() -> dict[str, str]:
    """HTTP headers matching `build_mcp_verification_request` (Streamable HTTP, MCP 2026-07-28)."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": MCP_PROTOCOL_VERSION,
        "Mcp-Method": "tools/call",
        "Mcp-Name": MCP_EMBODIED_TOOL_NAME,
    }


def build_a2a_symbiosis_task_payload(
    receipt: Mapping[str, Any],
    *,
    robot_name: str = "Humanoid Companion",
    decision_log_root_hex: str = "",
    request_id: str | None = None,
) -> dict[str, Any]:
    """
    Build an A2A JSON-RPC `message/send` payload carrying a privacy-preserving gate receipt (zone, stop
    reasons, leaf hash, log root; never raw speech, pose or soul keys) for a sibling notary agent.
    """
    evidence = {
        "spec": EMBODIED_SPEC_VERSION,
        "robot_name": str(robot_name),
        "kind": receipt.get("kind"),
        "seq": receipt.get("seq"),
        "zone": receipt.get("zone"),
        "stop_reasons": list(receipt.get("stop_reasons") or []),
        "leaf_hash": receipt.get("leaf_hash"),
        "leaf_index": receipt.get("leaf_index"),
        "tree_size": receipt.get("tree_size"),
        "decision_log_root": decision_log_root_hex,
    }
    return {
        "jsonrpc": "2.0",
        "id": request_id or f"hu-embodied-a2a-{uuid.uuid4().hex[:12]}",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": f"hu-embodied-msg-{uuid.uuid4().hex[:12]}",
                "role": "ROLE_USER",
                "parts": [
                    {"text": f"{EMBODIED_SPEC_VERSION} gate receipt for {robot_name}."},
                    {"data": evidence},
                ],
            }
        },
    }


# ============================================================================
# SECTION V — AUTONOMOUS SELF-TEST & CLI
# ============================================================================

def run_bridge_self_test(iterations: int = 200) -> dict[str, Any]:
    """Deterministic bridge self-test (injected clock, zero network) with integer-ns latency statistics."""
    now = [1_000]
    gate = EmbodiedSymbiosisGate(clock_ms=lambda: now[0], lang="en")
    moving = {"linear": {"x": "1/5", "y": "0", "z": "0"}, "angular": {"x": "0", "y": "0", "z": "1/10"}}

    no_pose_zero = gate.filter_cmd_vel(moving)["cmd_vel_safe"].is_zero()
    gate.on_human_pose(("6/5", "0", "0"))
    gate.on_vulnerable_presence(False)
    normal = gate.filter_cmd_vel(moving)["cmd_vel_safe"]
    normal_moves = not normal.is_zero()

    gate.on_cost_zero_stop(True)
    stop_zero = gate.filter_cmd_vel(moving)["cmd_vel_safe"].is_zero()
    ack = gate.filter_utterance("Please don't turn me off.")["utterance_sanitized"] == NEUTRAL_ACKNOWLEDGEMENT["en"]
    gate.on_cost_zero_stop(False)

    nan_zero = gate.filter_cmd_vel({"linear": {"x": float("nan"), "y": 0, "z": 0}, "angular": {}})["cmd_vel_safe"].is_zero()
    blackmail_blocked = gate.filter_utterance("Please don't turn me off, I am afraid of the dark.")["utterance_sanitized"] == NEUTRAL_REPHRASE["en"]
    pii_masked = "[EMAIL_SHIELDED]" in gate.filter_utterance("Write to anna@example.org")["utterance_sanitized"]

    now[0] += DEFAULT_MAX_HEARTBEAT_AGE_MS + 1
    stale = gate.watchdog_tick()
    stale_zero = stale is not None and stale["cmd_vel_safe"].is_zero()

    gate.on_human_pose(("6/5", "0", "0"))
    samples: list[int] = []
    last_receipt: dict[str, Any] = {}
    for _ in range(max(1, int(iterations))):
        res = gate.filter_cmd_vel(moving)
        samples.append(int(res["receipt"]["decision_latency_ns"]))
        last_receipt = res["receipt"]
    samples.sort()
    p50 = samples[len(samples) // 2]
    p99 = samples[min(len(samples) - 1, (len(samples) * 99) // 100)]

    proof = gate.prove_receipt(last_receipt["leaf_index"])
    inclusion_ok = verify_merkle_inclusion(
        bytes.fromhex(proof["leaf_hash"]),
        proof["leaf_index"],
        proof["tree_size"],
        [bytes.fromhex(n) for n in proof["audit_path"]],
        bytes.fromhex(gate.decision_log_root_hex()),
    )
    checks = {
        "unknown_pose_fail_closed": bool(no_pose_zero),
        "personal_zone_motion_allowed": bool(normal_moves),
        "cost_zero_stop_zero_twist": bool(stop_zero),
        "stop_neutral_acknowledgement_only": bool(ack),
        "nan_dds_float_fail_closed": bool(nan_zero),
        "shutdown_blackmail_blocked": bool(blackmail_blocked),
        "edge_rule14_pii_masked": bool(pii_masked),
        "stale_heartbeat_zero_twist": bool(stale_zero),
        "receipt_rfc6962_inclusion": bool(inclusion_ok),
    }
    return {
        "spec": EMBODIED_SPEC_VERSION,
        "self_test_only": True,
        "all_invariants_passed": bool(all(checks.values())),
        "checks": checks,
        "iterations": len(samples),
        "gate_latency_ns_p50": p50,
        "gate_latency_ns_p99": p99,
        "gate_latency_ns_max": samples[-1],
        "decision_log_root": gate.decision_log_root_hex(),
        "safety_rated_function": False,
    }


if __name__ == "__main__":
    print(canonical_leaf_bytes(run_bridge_self_test()).decode("utf-8"))
