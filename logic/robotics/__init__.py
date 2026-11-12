# SPDX-FileCopyrightText: 2026 David Porto Baraldés (Homo Universalis / Viveka)
# SPDX-License-Identifier: Apache-2.0
"""
Homo Universalis robotics package: zero-dependency ROS 2 ↔ Ma'at symbiosis bridges
(HU-EMBODIED-SYMBIOSIS v1.0 and HU-UNIFIED-CONSCIOUSNESS v1.0).

Public symbols are exported LAZILY (PEP 562): an eager import here would create an import cycle
(`logic.consciousness` imports `logic.robotics.embodied_edge_core`, whose package `__init__` would
import the unified bridge, which imports `logic.consciousness` back) and would load both bridges on
every `import logic.robotics.embodied_edge_core`.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_LAZY_EXPORTS: dict[str, str] = {
    "EmbodiedSymbiosisGate": "logic.robotics.ros2_embodied_symbiosis_bridge",
    "UnifiedConsciousnessGate": "logic.robotics.ros2_unified_consciousness_bridge",
    "attach_unified_consciousness_to_rclpy_node": "logic.robotics.ros2_unified_consciousness_bridge",
    "build_mcp_unified_consciousness_request": "logic.robotics.ros2_unified_consciousness_bridge",
    "build_a2a_unified_consciousness_task": "logic.robotics.ros2_unified_consciousness_bridge",
    "run_unified_bridge_self_test": "logic.robotics.ros2_unified_consciousness_bridge",
}
_ALIASES: dict[str, str] = {"attach_unified_consciousness_to_rclpy_node": "attach_to_rclpy_node"}

__all__ = sorted(_LAZY_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module 'logic.robotics' has no attribute {name!r}")
    return getattr(import_module(module_name), _ALIASES.get(name, name))
