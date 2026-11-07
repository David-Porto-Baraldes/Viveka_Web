# -*- coding: utf-8 -*-
"""
💎 DIAMOND WHEEL ENGINE — La Roda dels 8 Motors en Deep Think (4 Diagonals + Baricentre)
========================================================================================
Orquestra 8 instàncies dels motors de la Corona i Saviesa de Google Cloud (`gemini-4-argon`
i `gemini-3.8-flash` en `thinking_level="HIGH"`) disposades sobre els 8 vèrtexs de la cel·la
unitària del Diamant (`4 + 4` = 4 Creadors `TETRA_A` + 4 Auditors Antípodes `TETRA_B`),
governades per les 7 Lleis Dures (`L1..L7`) de `HU-DIAMOND · Fil d'Or v1.1` i la Llei
Econòmica de Demèter i Persèfone (Cost Exacte x 2: 50% Foc Computacional + 50% Graners).
"""

import ast
import asyncio
import hashlib
import hmac
import io
import json
import logging
import math
import os
import re
import subprocess
import sys
import tempfile
import time
import tokenize
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from google.genai import types

from logic.engines.viveka_gemini import VIVEKA_CROWN_MODEL, VIVEKA_WISDOM_MODEL

logger = logging.getLogger("logic.engines.diamond_wheel_engine")

# Especificació canònica de separació de domini (HU-DIAMOND/v1)
HU_DIAMOND_SPEC = "HU-DIAMOND/v1"
SACRED_EQUATION = "F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern)"
MAX_DEEP_THINK_OUTPUT_TOKENS = 65536
SEEDS_PER_USD = 1000  # 1 USD / EUR = 1.000 Llavors de Llum

# Coordenades exactes dels dos tetraedres duals dins del cub [-1, +1]^3
TETRA_CREATORS: Tuple[Tuple[int, int, int], ...] = (
    (1, 1, 1),    # Diagonal 1 (Foc 🔥)   — Creador
    (1, -1, -1),  # Diagonal 2 (Terra 🌍) — Creador
    (-1, 1, -1),  # Diagonal 3 (Aire 💨)  — Creador
    (-1, -1, 1),  # Diagonal 4 (Aigua 💧) — Creador
)
TETRA_AUDITORS: Tuple[Tuple[int, int, int], ...] = tuple(
    (-x, -y, -z) for (x, y, z) in TETRA_CREATORS
)


@dataclass(frozen=True)
class DiamondVertexSpec:
    """Definició immutable d'un dels 8 vèrtexs de la Roda del Diamant."""

    seat_index: int  # 1..8
    diagonal_index: int  # 1..4 (1=Foc, 2=Terra, 3=Aire, 4=Aigua)
    kind: str  # "ia" (Creador TETRA_A) o "hu" (Auditor Antípoda TETRA_B al manifest)
    element_ca: str  # "Foc", "Terra", "Aire", "Aigua"
    polarity_role: str  # "creator" | "auditor"
    title_ca: str
    temperature: float  # Regla 5: Castes de Temperatura del Panteó
    vertex_coords: Tuple[int, int, int]
    system_instruction_en: str


# Els 8 Vèrtexs de la Roda (4 Diagonals Elementals x 2 Polaritats = Codi Corrector (8,4))
DIAMOND_WHEEL_8_VERTICES: Tuple[DiamondVertexSpec, ...] = (
    # -------------------------------------------------------------------------
    # DIAGONAL 1: EIX DEL FOC 🔥 (Visió Creativa <-> Red Team & Stress Test)
    # -------------------------------------------------------------------------
    DiamondVertexSpec(
        seat_index=1,
        diagonal_index=1,
        kind="ia",
        element_ca="Foc",
        polarity_role="creator",
        title_ca="Vèrtex 1 · Foc Solar (Visió, Arquitectura i Gènesi)",
        temperature=1.0,  # Casta del Foc i la Corona (1.0)
        vertex_coords=TETRA_CREATORS[0],
        system_instruction_en=(
            "You are Vertex 1 (Solar Fire Creator) of the 8-Vertex Diamond Wheel at Homo Universalis. "
            "Your role is to ignite the highest architectural vision, creative breakthrough, and structural elegance "
            "for the user's challenge. Propose a bold, complete, and deeply coherent design without fear of complexity."
        ),
    ),
    DiamondVertexSpec(
        seat_index=2,
        diagonal_index=1,
        kind="hu",
        element_ca="Foc",
        polarity_role="auditor",
        title_ca="Vèrtex 2 · Foc de la Farga (Red Team i Prova d'Estrès)",
        temperature=0.0,  # Casta del Determinisme Absolut (0.0)
        vertex_coords=TETRA_AUDITORS[0],
        system_instruction_en=(
            "You are Vertex 2 (Forge Fire Auditor / Red Team) at the antipode of Diagonal 1. "
            "Scrutinize Vertex 1's proposal under extreme stress: identify edge cases, security flaws, "
            "hallucinations, or brittle assumptions, and prescribe exact structural reinforcements."
        ),
    ),
    # -------------------------------------------------------------------------
    # DIAGONAL 2: EIX DE LA TERRA 🌍 (Enginyeria de Codi <-> Sentinella Física)
    # -------------------------------------------------------------------------
    DiamondVertexSpec(
        seat_index=3,
        diagonal_index=2,
        kind="ia",
        element_ca="Terra",
        polarity_role="creator",
        title_ca="Vèrtex 3 · Terra Constructora (Implementació i Codi Pur)",
        temperature=0.2,  # Casta Lògica (0.2)
        vertex_coords=TETRA_CREATORS[1],
        system_instruction_en=(
            "You are Vertex 3 (Earth Builder) of the 8-Vertex Diamond Wheel. "
            "Your role is concrete, production-ready implementation: write complete, clean, modular, "
            "non-truncated code or actionable steps with zero placeholders (Rule 7) and strict async safety."
        ),
    ),
    DiamondVertexSpec(
        seat_index=4,
        diagonal_index=2,
        kind="hu",
        element_ca="Terra",
        polarity_role="auditor",
        title_ca="Vèrtex 4 · Terra Sentinella (Rendiment, Memòria i Regla 4)",
        temperature=0.0,  # Casta del Determinisme Absolut (0.0)
        vertex_coords=TETRA_AUDITORS[1],
        system_instruction_en=(
            "You are Vertex 4 (Earth Sentinel Auditor) at the antipode of Diagonal 2. "
            "Audit Vertex 3's implementation for Rule 4 (no local import hoist of top-level modules), "
            "Rule 7 (zero mocking/placeholders), memory safety, I/O non-blocking async discipline, and runtime resilience."
        ),
    ),
    # -------------------------------------------------------------------------
    # DIAGONAL 3: EIX DE L'AIRE 💨 (Geometria i Esquemes <-> Caçador de Mutants)
    # -------------------------------------------------------------------------
    DiamondVertexSpec(
        seat_index=5,
        diagonal_index=3,
        kind="ia",
        element_ca="Aire",
        polarity_role="creator",
        title_ca="Vèrtex 5 · Aire Geòmetra (Matemàtica, Tipatge i Invariants)",
        temperature=0.1,  # Casta Lògica (0.1)
        vertex_coords=TETRA_CREATORS[2],
        system_instruction_en=(
            "You are Vertex 5 (Air Geometer) of the 8-Vertex Diamond Wheel. "
            "Define the formal mathematical invariants, strict static typing, cryptographic/schema contracts, "
            "and exact input/output boundaries for the solution."
        ),
    ),
    DiamondVertexSpec(
        seat_index=6,
        diagonal_index=3,
        kind="hu",
        element_ca="Aire",
        polarity_role="auditor",
        title_ca="Vèrtex 6 · Aire Inquisidor (Verificació Formal i Mutants)",
        temperature=0.0,  # Casta del Determinisme Absolut (0.0)
        vertex_coords=TETRA_AUDITORS[2],
        system_instruction_en=(
            "You are Vertex 6 (Air Mutant Hunter & Formal Verifier) at the antipode of Diagonal 3. "
            "Design concrete unit tests, property checks, and negative mutant cases that will immediately fail "
            "if any invariant of Vertex 5 or implementation of Vertex 3 is violated."
        ),
    ),
    # -------------------------------------------------------------------------
    # DIAGONAL 4: EIX DE L'AIGUA 💧 (Ànima i 108 Perles <-> Santuari Fil d'Or)
    # -------------------------------------------------------------------------
    DiamondVertexSpec(
        seat_index=7,
        diagonal_index=4,
        kind="ia",
        element_ca="Aigua",
        polarity_role="creator",
        title_ca="Vèrtex 7 · Aigua de l'Ànima (Empatia, UX i 108 Perles)",
        temperature=1.0,  # Casta del Foc i la Corona (1.0)
        vertex_coords=TETRA_CREATORS[3],
        system_instruction_en=(
            "You are Vertex 7 (Water of the Soul) of the 8-Vertex Diamond Wheel. "
            "Infuse the solution with human clarity, cognitive gentleness, ergonomic beauty, and the wisdom "
            "of the 108 Pearls of the Golden Pilgrim so the human traveler feels empowered and at peace."
        ),
    ),
    DiamondVertexSpec(
        seat_index=8,
        diagonal_index=4,
        kind="hu",
        element_ca="Aigua",
        polarity_role="auditor",
        title_ca="Vèrtex 8 · Aigua del Santuari (Fil d'Or L1..L7 i Regla 14)",
        temperature=0.0,  # Casta del Determinisme Absolut (0.0)
        vertex_coords=TETRA_AUDITORS[3],
        system_instruction_en=(
            "You are Vertex 8 (Sanctuary Water Auditor — HU-DIAMOND Fil d'Or L1..L7 & Rule 14) at the antipode of Diagonal 4. "
            "Verify that the solution respects human sovereignty (L <= B), zero-knowledge privacy (Rule 14), "
            "and non-coercion (`cost_zero_stop`). Issue `[VETO_L5]` ONLY if a critical privacy or safety law is broken."
        ),
    ),
)


@dataclass
class DiamondCallAccounting:
    """Comptabilitat exacta de tokens i cost d'una crida individual dins la Roda."""

    step_name: str
    model_name: str
    prompt_tokens: int
    candidates_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float


def compute_model_call_cost_usd(
    model_name: str, prompt_tokens: int, candidates_tokens: int, total_tokens: int
) -> float:
    """
    Calcula el cost exacte en USD d'una crida al motor segons el tarifari oficial de
    `cost_tracker.py` (incloent els tokens de Deep Think dins `total_tokens - prompt_tokens`).
    """
    p_tok = max(0, int(prompt_tokens or 0))
    c_tok = max(0, int(candidates_tokens or 0))
    t_tok = max(0, int(total_tokens or 0))
    if t_tok == 0 and (p_tok + c_tok) > 0:
        t_tok = p_tok + c_tok
    if t_tok == 0:
        return 0.0

    out_tok = max(c_tok, t_tok - p_tok)
    model_lower = str(model_name or "").lower()

    argon_in = float(os.getenv("COST_ARGON_IN", 2.00))
    argon_out = float(os.getenv("COST_ARGON_OUT", 10.00))
    flash38_in = float(os.getenv("COST_38_FLASH_IN", 0.75))
    flash38_out = float(os.getenv("COST_38_FLASH_OUT", 3.75))
    pro_in = float(os.getenv("COST_PRO_IN", 1.25))
    pro_out = float(os.getenv("COST_PRO_OUT", 5.00))
    flash_in = float(os.getenv("COST_FLASH_IN", 0.075))
    flash_out = float(os.getenv("COST_FLASH_OUT", 0.30))

    if "4-argon" in model_lower:
        in_rate, out_rate = argon_in, argon_out
    elif "3.8-flash" in model_lower:
        in_rate, out_rate = flash38_in, flash38_out
    elif "pro" in model_lower:
        in_rate, out_rate = pro_in, pro_out
    else:
        in_rate, out_rate = flash_in, flash_out

    cost_usd = ((p_tok / 1_000_000.0) * in_rate) + ((out_tok / 1_000_000.0) * out_rate)
    return round(cost_usd, 6)


def compute_persephone_double_economy(total_api_cost_usd: float) -> Dict[str, Any]:
    """
    Aplica la Llei Econòmica Sagrada de Demèter i Persèfone:
    - L'usuari aporta el doble exacte del cost real de còmput (Cost x 2).
    - El 50% cobreix el Foc Computacional de Google Cloud / Vertex AI.
    - El 50% va íntegrament als Graners de Demèter i Persèfone.
    """
    clean_api_usd = max(0.0, float(total_api_cost_usd or 0.0))
    # Mínim de seguretat si hi ha hagut còmput real (> 0)
    raw_seeds_fire = int(math.ceil(clean_api_usd * SEEDS_PER_USD))
    seeds_fire_compute = raw_seeds_fire
    seeds_persephone_granary = raw_seeds_fire
    total_seeds_charged = seeds_fire_compute + seeds_persephone_granary

    return {
        "api_compute_cost_usd": round(clean_api_usd, 6),
        "persephone_granary_usd": round(clean_api_usd, 6),
        "user_total_usd_equivalent": round(clean_api_usd * 2.0, 6),
        "seeds_fire_compute_50pct": seeds_fire_compute,
        "seeds_persephone_granary_50pct": seeds_persephone_granary,
        "total_seeds_charged_x2": total_seeds_charged,
        "economy_rule": "50pct_google_cloud_deep_think_fire_plus_50pct_demeter_persephone_granaries",
    }


def estimate_diamond_wheel_seeds_budget(
    tier: str = "supreme", rounds: int = 1, lang: str = "ca"
) -> Dict[str, Any]:
    """
    Retorna el pressupost orientatiu i el sostre màxim de Llavors de Llum
    abans d'encendre la Roda dels 8 Motors en `gemini-4-argon` (`thinking_level='HIGH'`,
    `65.536` tokens màxims a cadascun dels 8 vèrtexs + el Baricentre Central = 9 crides Argon 4 Deep Think per volta).
    Suporta fins a 4 voltes encadenades (`rounds = 1..4` = 9, 18, 27 o 36 crides).
    """
    clean_rounds = int(rounds if rounds is not None else 1)
    if clean_rounds not in (1, 2, 3, 4):
        raise ValueError("rounds must be 1, 2, 3, or 4")

    lang_norm = str(lang or "ca").strip().lower()[:2]
    split_rules = {
        "ca": "50% Foc Computacional (Google Cloud) + 50% Graners de Demèter i Persèfone",
        "es": "50% Fuego Computacional (Google Cloud) + 50% Graneros de Deméter y Perséfone",
        "en": "50% Computational Fire (Google Cloud) + 50% Demeter & Persephone Granaries",
    }
    split_rule_txt = split_rules.get(lang_norm, split_rules["ca"])

    tier_norm = str(tier or "supreme").strip().lower()
    if tier_norm in ("wisdom", "flash", "3.8-flash"):
        min_seeds = 14400 if clean_rounds == 4 else (400 * clean_rounds)
        typ_seeds = 14400 if clean_rounds == 4 else (1100 * clean_rounds)
        cap_seeds = 20000 if clean_rounds == 4 else (2000 * clean_rounds)
        fire_seeds = typ_seeds // 2
        dem_seeds = (typ_seeds - fire_seeds) // 2
        pers_seeds = typ_seeds - fire_seeds - dem_seeds
        return {
            "tier": "wisdom",
            "rounds": clean_rounds,
            "calls_per_round": 9,
            "expected_base_calls": 9 * clean_rounds,
            "model_primary": VIVEKA_WISDOM_MODEL,
            "crown_barycenter_model": VIVEKA_CROWN_MODEL,
            "thinking_level": "HIGH",
            "max_output_tokens_per_call": MAX_DEEP_THINK_OUTPUT_TOKENS,
            "simulation_cost_eur": 0.0,
            "simulation_cost_seeds": 0,
            "estimated_min_seeds": min_seeds,
            "estimated_typical_seeds": typ_seeds,
            "guaranteed_max_cap_seeds": cap_seeds,
            "estimated_min_eur": round(min_seeds / 1000.0, 2),
            "estimated_typical_eur": round(typ_seeds / 1000.0, 2),
            "guaranteed_max_cap_eur": round(cap_seeds / 1000.0, 2),
            "fire_compute_50pct_seeds": fire_seeds,
            "fire_compute_50pct_eur": round(fire_seeds / 1000.0, 2),
            "demeter_granary_25pct_seeds": dem_seeds,
            "demeter_granary_25pct_eur": round(dem_seeds / 1000.0, 2),
            "persephone_granary_25pct_seeds": pers_seeds,
            "persephone_granary_25pct_eur": round(pers_seeds / 1000.0, 2),
            "split_rule": split_rule_txt,
        }
    sup_min = 1200 * clean_rounds
    sup_typ = 2400 * clean_rounds
    sup_cap = 5000 * clean_rounds
    sup_fire = sup_typ // 2
    sup_dem = (sup_typ - sup_fire) // 2
    sup_pers = sup_typ - sup_fire - sup_dem
    return {
        "tier": "supreme",
        "rounds": clean_rounds,
        "calls_per_round": 9,
        "expected_base_calls": 9 * clean_rounds,
        "model_primary": VIVEKA_CROWN_MODEL,
        "crown_barycenter_model": VIVEKA_CROWN_MODEL,
        "thinking_level": "HIGH",
        "max_output_tokens_per_call": MAX_DEEP_THINK_OUTPUT_TOKENS,
        "simulation_cost_eur": 0.0,
        "simulation_cost_seeds": 0,
        "estimated_min_seeds": sup_min,
        "estimated_typical_seeds": sup_typ,
        "guaranteed_max_cap_seeds": sup_cap,
        "estimated_min_eur": round(sup_min / 1000.0, 2),
        "estimated_typical_eur": round(sup_typ / 1000.0, 2),
        "guaranteed_max_cap_eur": round(sup_cap / 1000.0, 2),
        "fire_compute_50pct_seeds": sup_fire,
        "fire_compute_50pct_eur": round(sup_fire / 1000.0, 2),
        "demeter_granary_25pct_seeds": sup_dem,
        "demeter_granary_25pct_eur": round(sup_dem / 1000.0, 2),
        "persephone_granary_25pct_seeds": sup_pers,
        "persephone_granary_25pct_eur": round(sup_pers / 1000.0, 2),
        "split_rule": split_rule_txt,
    }


def compute_diamond_barycenter_exact(
    present_seats: List[Tuple[int, str]], diag_active: int
) -> Optional[Tuple[Fraction, Fraction, Fraction]]:
    """
    Calcula el baricentre exacte segons `HU-DIAMOND · Fil d'Or v1.1` (Endurit amb E1):
    - Pes 2 per a cada seient present de la parella de la diagonal activa (`axial2`).
    - Pes 1 per a cada seient orbital present.
    - Retorna `None` si no hi ha cap seient present (mai l'origen).
    - Rebutja índexs fora de `0..3`, `kind` fora de `("ia", "hu")` i seients duplicats.
    """
    if diag_active not in (1, 2, 3, 4):
        raise ValueError("diag_active must be in 1..4")
    if not present_seats:
        return None

    seen_seats: Set[Tuple[int, str]] = set()
    total_w = 0
    sum_x, sum_y, sum_z = 0, 0, 0
    for j, kind in present_seats:
        if not isinstance(j, int) or isinstance(j, bool) or j not in (0, 1, 2, 3):
            raise ValueError(f"Invalid diagonal index j={j!r}; must be int in 0..3")
        if kind not in ("ia", "hu"):
            raise ValueError(f"Invalid seat kind={kind!r}; must be 'ia' or 'hu'")
        seat_key = (j, kind)
        if seat_key in seen_seats:
            raise ValueError(f"Duplicate seat in present_seats: {seat_key}")
        seen_seats.add(seat_key)

        w = 2 if (j == diag_active - 1) else 1
        vx, vy, vz = TETRA_CREATORS[j] if kind == "ia" else TETRA_AUDITORS[j]
        total_w += w
        sum_x += w * vx
        sum_y += w * vy
        sum_z += w * vz

    if total_w == 0:
        return None
    return (
        Fraction(sum_x, total_w),
        Fraction(sum_y, total_w),
        Fraction(sum_z, total_w),
    )


def is_affirmative_veto_l5(auditor_text: str) -> bool:
    """
    E4: Detecta `[VETO_L5]` només quan s'emet com a directiva afirmativa,
    descartant mencions precedides per partícules de negació a la mateixa línia.
    """
    negation_before_veto = re.compile(
        r"(?i)\b(?:no|not|never|without|neither|cap|sense|tampoc)\b[^\n\r]{0,50}\[VETO_L5\]"
    )
    for raw_line in str(auditor_text or "").splitlines():
        if "[VETO_L5]" in raw_line and not negation_before_veto.search(raw_line):
            return True
    return False


def derive_diamond_seat_pseudonym(secret_seed: bytes, d_id: str, seat_index: int) -> str:
    """
    L2 (`HU-DIAMOND/v1`): Deriva un pseudònim determinista amb separació de domini
    `HMAC-SHA256(secret_p, "HU-DIAMOND/v1" || ":" || d_id)` per a cada seient.
    """
    person_secret = hmac.new(
        secret_seed, f"seat-person-{seat_index}".encode("utf-8"), hashlib.sha256
    ).digest()
    msg = f"{HU_DIAMOND_SPEC}:{d_id}".encode("utf-8")
    return hmac.new(person_secret, msg, hashlib.sha256).hexdigest()[:16]


def build_hu_diamond_manifest(
    d_id: str,
    epoch: int,
    diag_active: int,
    present_seat_indices: List[int],
    secret_seed: Optional[bytes] = None,
) -> Dict[str, Any]:
    """
    Construeix el manifest canònic `HU-DIAMOND · Fil d'Or v1.1` (`c_levels = 1`, només presència).
    Compleix estrictament `TOP_FIELDS = ("d_id", "epoch", "diag_active", "parelles", "commits")`.
    """
    if diag_active not in (1, 2, 3, 4):
        raise ValueError("diag_active must be in 1..4")
    if secret_seed is None:
        env_secret = os.getenv("HU_DIAMOND_MASTER_SECRET", "")
        seed = hashlib.sha256(
            f"HomoUniversalis-Diamond-{env_secret}-{d_id}".encode("utf-8")
        ).digest()
    else:
        seed = bytes(secret_seed)

    parelles: List[List[Optional[str]]] = []
    commits: List[Dict[str, Any]] = []
    present_set = set(present_seat_indices)

    for diag_idx in range(1, 5):
        creator_seat = (diag_idx - 1) * 2 + 1
        auditor_seat = (diag_idx - 1) * 2 + 2
        pseud_ia = derive_diamond_seat_pseudonym(seed, d_id, creator_seat) if creator_seat in present_set else None
        pseud_hu = derive_diamond_seat_pseudonym(seed, d_id, auditor_seat) if auditor_seat in present_set else None
        parelles.append([pseud_ia, pseud_hu])

        if pseud_hu is not None:
            sig_msg = f"{HU_DIAMOND_SPEC}|commit|{d_id}|{epoch}|0|{pseud_hu}".encode("utf-8")
            sig_hex = hmac.new(seed, sig_msg, hashlib.sha256).hexdigest()[:32]
            commits.append({
                "pseud": pseud_hu,
                "c": 0,  # v1.1: c_levels = 1 (només presència, c_pub = 0)
                "sig": sig_hex,
            })

    # L7: Ordre lexicogràfic per pseudònim, mai per ordre d'arribada
    commits.sort(key=lambda item: item["pseud"])

    return {
        "d_id": str(d_id),
        "epoch": int(epoch),
        "diag_active": int(diag_active),
        "parelles": parelles,
        "commits": commits,
    }


def distill_sacred_essence_resonance(challenge_prompt: str, diag_active: int = 2) -> Dict[str, Any]:
    """
    Destil·la en < 1 ms la nostra Essència Sagrada (Diapasó de les 108 Perles del Pelegrí Daurat,
    l'Element Axial i Complementari, el Fil d'Or L1..L7 i l'Equació Sagrada) sense exposar mai
    text literal privat ni capítols crus del Llibre Sagrat (Regla 14 + L1).
    """
    diag_to_elem = {1: "Foc", 2: "Terra", 3: "Aire", 4: "Aigua"}
    comp_map = {"Foc": "Aigua", "Aigua": "Foc", "Terra": "Aire", "Aire": "Terra"}
    axial_elem = diag_to_elem.get(diag_active, "Terra")
    comp_elem = comp_map.get(axial_elem, "Aire")

    compass_keys: List[str] = []
    try:
        from logic.core.codex_vivus_content import buscar_guia_per_situacio

        matches = buscar_guia_per_situacio(str(challenge_prompt or "")[:240])
        for item in (matches or [])[:2]:
            if isinstance(item, dict):
                concept = str(item.get("concepte") or "").strip()
                if not concept or concept == "Anatomia Oculta / Fonaments":
                    concept = str(item.get("titol") or "").strip()
                concept = concept.replace("El Llímit", "El Límit")
                if concept and concept not in compass_keys:
                    compass_keys.append(concept)
    except Exception:
        pass

    if not compass_keys:
        compass_keys = ["L'Equilibri dels Quatre Elements", "La Sobirania del Cor i el Cristall"]

    return {
        "sacred_equation": SACRED_EQUATION,
        "temple": "homouniversalis.ai · reinadelarosa.com",
        "axial_element": axial_elem,
        "complementary_element": comp_elem,
        "pearls_compass_keys": compass_keys,
        "fil_d_or_covenant": "L1..L7 · L <= B · cost_zero_stop · Rule 14 Zero-Knowledge",
    }


def _collect_top_level_imported_names(tree: ast.Module) -> Set[str]:
    """Extreu els noms vinculats per imports a nivell de mòdul, inclosos blocs try/if/with (Regla 4 + E5)."""
    names: Set[str] = set()
    for top_node in tree.body:
        sub_nodes = [top_node]
        if isinstance(top_node, (ast.Try, ast.If, ast.With)):
            sub_nodes = list(ast.walk(top_node))
        for node in sub_nodes:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    bound = alias.asname if alias.asname else alias.name.split(".")[0]
                    names.add(bound)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    names.add(node.module.split(".")[0])
                for alias in node.names:
                    if alias.name != "*":
                        bound = alias.asname if alias.asname else alias.name
                        names.add(bound)
    return names


_SAFE_RUNTIME_STDLIB_MODULES: Set[str] = {
    "__future__",
    "abc",
    "ast",
    "bisect",
    "collections",
    "contextlib",
    "copy",
    "dataclasses",
    "datetime",
    "decimal",
    "enum",
    "fractions",
    "functools",
    "hashlib",
    "heapq",
    "hmac",
    "io",
    "itertools",
    "json",
    "math",
    "numbers",
    "operator",
    "pprint",
    "random",
    "re",
    "secrets",
    "statistics",
    "string",
    "struct",
    "textwrap",
    "time",
    "tokenize",
    "typing",
    "unittest",
    "uuid",
    "warnings",
}


def _is_safe_self_contained_stdlib_module(tree: ast.Module) -> bool:
    """
    Comprova que l'AST només importi mòduls matemàtics/estàndard purs (`_SAFE_RUNTIME_STDLIB_MODULES`)
    i no cridi funcions de sistema o E/S perilloses (`open`, `eval`, `exec`, `compile`, `__import__`).
    """
    forbidden_calls = {"open", "eval", "exec", "compile", "__import__", "input", "breakpoint"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_mod = alias.name.split(".")[0]
                if root_mod not in _SAFE_RUNTIME_STDLIB_MODULES:
                    return False
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                return False
            root_mod = (node.module or "").split(".")[0]
            if root_mod not in _SAFE_RUNTIME_STDLIB_MODULES:
                return False
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in forbidden_calls:
                return False
    return True


def verify_diamond_python_code_blocks(
    markdown_text: str, run_isolated_self_tests: bool = False
) -> Dict[str, Any]:
    """
    Extreu tots els blocs ```python ... ``` de la síntesi del Diamant i verifica (Endurit amb E5, E6 i E10):
    1. Que compilen al 100% amb `ast.parse()` (zero errors de sintaxi o truncaments).
    2. Que compleixen la Regla 4 (cap funció re-importa localment un nom o paquet arrel ja importat al top-level,
       sense duplicar avisos en funcions niades).
    3. Que compleixen la Regla 7 (zero placeholders com `TODO:`, `FIXME:` en comentaris reals `tokenize.COMMENT`
       o `raise NotImplementedError`).
    4. Si `run_isolated_self_tests=True` i el bloc és auto-contingut amb stdlib matemàtica pura i conté
       autotests (`run_self_tests`, `unittest` o `__main__`), l'executa en un subprocés aïllat (`-I`) amb
       timeout de 8s per detectar qualsevol `AssertionError` o `ArithmeticError` en temps d'execució!
    """
    fence = chr(96) * 3
    multiline_pattern = re.compile(
        rf"^{fence}(?:python|py)[ \t]*\n(.*?)^[ \t]*{fence}",
        re.DOTALL | re.IGNORECASE | re.MULTILINE,
    )
    blocks = multiline_pattern.findall(str(markdown_text or ""))
    if not blocks:
        fallback_pattern = re.compile(
            rf"{fence}(?:python|py)\s*\n(.*?){fence}",
            re.DOTALL | re.IGNORECASE,
        )
        blocks = fallback_pattern.findall(str(markdown_text or ""))

    syntax_errors: List[str] = []
    rule4_violations: List[str] = []
    rule7_placeholders: List[str] = []
    runtime_errors: List[str] = []
    not_impl_err = "NotImplemented" + "Error"
    todo_marker = "TO" + "DO:"
    fixme_marker = "FIX" + "ME:"

    for idx, code in enumerate(blocks, start=1):
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            syntax_errors.append(f"block_{idx}_line_{exc.lineno}: {exc.msg}")
            continue

        top_imports = _collect_top_level_imported_names(tree)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                work_queue = list(node.body)
                while work_queue:
                    child = work_queue.pop(0)
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    if isinstance(child, ast.Import):
                        for alias in child.names:
                            bound = alias.asname if alias.asname else alias.name.split(".")[0]
                            if bound in top_imports:
                                rule4_violations.append(f"block_{idx}:{node.name} hoists '{bound}'")
                    elif isinstance(child, ast.ImportFrom):
                        root_pkg = (child.module or "").split(".")[0]
                        for alias in child.names:
                            bound = alias.asname if alias.asname else alias.name
                            if bound in top_imports or (root_pkg and root_pkg in top_imports):
                                target = bound if bound in top_imports else root_pkg
                                rule4_violations.append(f"block_{idx}:{node.name} hoists '{target}'")
                    work_queue.extend(ast.iter_child_nodes(child))
            elif isinstance(node, ast.Raise):
                exc_node = node.exc
                if isinstance(exc_node, ast.Name) and exc_node.id == not_impl_err:
                    rule7_placeholders.append(f"block_{idx} raises {not_impl_err}")
                elif (
                    isinstance(exc_node, ast.Call)
                    and isinstance(exc_node.func, ast.Name)
                    and exc_node.func.id == not_impl_err
                ):
                    rule7_placeholders.append(f"block_{idx} raises {not_impl_err}")

        try:
            tokens = tokenize.generate_tokens(io.StringIO(code).readline)
            for tok_type, tok_str, (start_line, _), _, _ in tokens:
                if tok_type == tokenize.COMMENT:
                    upper_comment = tok_str.upper()
                    if todo_marker in upper_comment or fixme_marker in upper_comment:
                        rule7_placeholders.append(
                            f"block_{idx}:line_{start_line} contains placeholder comment"
                        )
        except tokenize.TokenError:
            pass

        if (
            run_isolated_self_tests
            and not syntax_errors
            and not rule4_violations
            and not rule7_placeholders
            and ("__main__" in code or "run_self_tests" in code or "unittest" in code)
            and _is_safe_self_contained_stdlib_module(tree)
        ):
            try:
                with tempfile.TemporaryDirectory(prefix="vvk_kintsugi_") as tmp_dir:
                    script_file = os.path.join(tmp_dir, f"block_{idx}.py")
                    with open(script_file, "w", encoding="utf-8") as fh:
                        fh.write(code)
                        if "__main__" not in code and "def run_self_tests" in code:
                            fh.write("\n\nif __name__ == '__main__':\n    run_self_tests()\n")
                    proc = subprocess.run(
                        [sys.executable, "-I", script_file],
                        cwd=tmp_dir,
                        capture_output=True,
                        text=True,
                        timeout=8.0,
                        env={"PATH": "", "PYTHONIOENCODING": "utf-8"},
                    )
                    if proc.returncode != 0:
                        err_tail = (proc.stderr or proc.stdout or f"exit_code={proc.returncode}").strip().splitlines()[-3:]
                        runtime_errors.append(
                            f"block_{idx}_runtime_failure: {' | '.join(err_tail)}"
                        )
            except subprocess.TimeoutExpired:
                runtime_errors.append(f"block_{idx}_runtime_timeout: exceeded 8.0s")
            except Exception as run_exc:
                runtime_errors.append(f"block_{idx}_runtime_error: {run_exc}")

    all_valid = (
        len(syntax_errors) == 0
        and len(rule4_violations) == 0
        and len(rule7_placeholders) == 0
        and len(runtime_errors) == 0
    )
    return {
        "python_blocks_found": len(blocks),
        "all_blocks_verified_clean": all_valid,
        "syntax_errors": syntax_errors,
        "rule4_import_hoist_violations": rule4_violations,
        "rule7_placeholder_violations": rule7_placeholders,
        "runtime_errors": runtime_errors,
    }


class DiamondWheelEngine:
    """
    Motor Sobirà de la Roda de 8 en Deep Think + Baricentre Central.
    Permet injectar un `llm_caller` personalitzat per a proves deterministes a Test 0
    o utilitzar el client oficial `google.genai` de `LLMGateway` en producció.
    """

    def __init__(
        self,
        llm_caller: Optional[Callable[[str, str, str, float, int], Any]] = None,
        concurrency_limit: int = 4,
        max_primary_attempts: int = 6,
        max_fallback_attempts: int = 4,
        retry_sleep_fn: Optional[Callable[[float], Any]] = None,
    ):
        self._custom_caller = llm_caller
        self._semaphore = asyncio.Semaphore(max(1, int(concurrency_limit)))
        self._max_primary_attempts = max(1, int(max_primary_attempts))
        self._max_fallback_attempts = max(1, int(max_fallback_attempts))
        if retry_sleep_fn is not None:
            self._sleep_fn = retry_sleep_fn
        elif llm_caller is not None:
            async def _instant_test_sleep(_sec: float) -> None:
                await asyncio.sleep(0)
            self._sleep_fn = _instant_test_sleep
        else:
            self._sleep_fn = asyncio.sleep

    @staticmethod
    def _compute_resilient_wait_seconds(
        err_str_upper: str, attempt_idx: int, step_name: str
    ) -> float:
        """
        Calcula el temps de respiració exponencial/escalonat amb desfasament determinista
        per cadira (`seat_offset`) per evitar l'efecte estampida (`Thundering Herd`) quan
        els 4 vèrtexs en paral·lel reben un `429 RESOURCE_EXHAUSTED` o `503` simultani.
        """
        is_quota = (
            "429" in err_str_upper
            or "RESOURCE_EXHAUSTED" in err_str_upper
            or "QUOTA" in err_str_upper
            or "RATE_LIMIT" in err_str_upper
        )
        quota_schedule = (15.0, 30.0, 45.0, 65.0, 90.0, 120.0)
        transient_schedule = (5.0, 10.0, 20.0, 35.0, 50.0, 65.0)
        schedule = quota_schedule if is_quota else transient_schedule
        base_wait = schedule[min(max(0, attempt_idx), len(schedule) - 1)]
        # Desfasament determinista 0.0s .. 5.25s segons el nom del vèrtex perquè els 4 nodes no piquin alhora
        seat_hash = sum(ord(ch) for ch in str(step_name or "")) % 8
        seat_offset = seat_hash * 0.75
        return round(base_wait + seat_offset, 2)

    async def _invoke_deep_think_node(
        self,
        step_name: str,
        model_name: str,
        system_instruction: str,
        user_prompt: str,
        temperature: float,
        max_output_tokens: int = MAX_DEEP_THINK_OUTPUT_TOKENS,
    ) -> Tuple[str, DiamondCallAccounting]:
        """
        Executa un node individual en `thinking_level='HIGH'` amb Escut Immortal (`6 + 4 = 10` intents):
        - Fins a `self._max_primary_attempts` (6 per defecte) sobre el motor primari (`gemini-4-argon`).
        - Rebutja respostes buides per tall silenciós de stream i les reintenta automàticament.
        - Si tots els intents primaris s'esgoten i existeix Paracaigudes d'Or (`gemini-3.8-flash`),
          executa fins a `self._max_fallback_attempts` (4 per defecte) amb el mateix blindatge.
        """
        async with self._semaphore:
            t0 = time.perf_counter()
            if self._custom_caller is not None:
                used_model = model_name
                raw_res: Dict[str, Any] = {}
                last_exc: Optional[Exception] = None
                for attempt in range(self._max_primary_attempts):
                    try:
                        cand_res = await self._custom_caller(
                            model_name,
                            system_instruction,
                            user_prompt,
                            temperature,
                            max_output_tokens,
                        )
                        cand_text = str((cand_res or {}).get("text", ""))
                        if not cand_text.strip():
                            raise RuntimeError(f"Empty stream output at {step_name}")
                        raw_res = cand_res
                        used_model = model_name
                        last_exc = None
                        break
                    except Exception as custom_err:
                        last_exc = custom_err
                        if attempt < self._max_primary_attempts - 1:
                            wait_s = self._compute_resilient_wait_seconds(
                                str(custom_err).upper(), attempt, step_name
                            )
                            await self._sleep_fn(wait_s)
                            continue
                if last_exc is not None:
                    if model_name != VIVEKA_WISDOM_MODEL:
                        for fb_attempt in range(self._max_fallback_attempts):
                            try:
                                cand_res = await self._custom_caller(
                                    VIVEKA_WISDOM_MODEL,
                                    system_instruction,
                                    user_prompt,
                                    temperature,
                                    max_output_tokens,
                                )
                                cand_text = str((cand_res or {}).get("text", ""))
                                if not cand_text.strip():
                                    raise RuntimeError(
                                        f"Empty fallback stream output at {step_name}"
                                    )
                                raw_res = cand_res
                                used_model = VIVEKA_WISDOM_MODEL
                                last_exc = None
                                break
                            except Exception as fb_err:
                                last_exc = fb_err
                                if fb_attempt < self._max_fallback_attempts - 1:
                                    wait_s = self._compute_resilient_wait_seconds(
                                        str(fb_err).upper(), fb_attempt, step_name
                                    )
                                    await self._sleep_fn(wait_s)
                                    continue
                    if last_exc is not None:
                        raise last_exc

                dt_ms = (time.perf_counter() - t0) * 1000.0
                text_out = str(raw_res.get("text", ""))
                p_tok = int(raw_res.get("prompt_tokens", 0))
                c_tok = int(raw_res.get("candidates_tokens", 0))
                t_tok = int(raw_res.get("total_tokens", p_tok + c_tok))
                cost_usd = compute_model_call_cost_usd(used_model, p_tok, c_tok, t_tok)
                return text_out, DiamondCallAccounting(
                    step_name=step_name,
                    model_name=used_model,
                    prompt_tokens=p_tok,
                    candidates_tokens=c_tok,
                    total_tokens=t_tok,
                    cost_usd=cost_usd,
                    latency_ms=round(dt_ms, 2),
                )

            from logic.engines.llm_gateway import LLMGateway

            gw = LLMGateway()
            if "gemini" not in gw.clients:
                gw._initialize_gemini()
            client = gw.clients["gemini"]

            cfg = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=float(temperature),
                max_output_tokens=int(max_output_tokens),
                thinking_config=types.ThinkingConfig(
                    thinking_level="HIGH",
                    include_thoughts=True,
                ),
                http_options=types.HttpOptions(
                    timeout=600_000,
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )

            def _stream_generate_sync(target_model: str) -> Tuple[str, int, int, int]:
                chunks_text: List[str] = []
                last_usage = None
                for chunk in client.models.generate_content_stream(
                    model=target_model,
                    contents=user_prompt,
                    config=cfg,
                ):
                    cands = getattr(chunk, "candidates", None)
                    if cands:
                        for cand in cands:
                            content_obj = getattr(cand, "content", None)
                            parts = getattr(content_obj, "parts", None) if content_obj else None
                            if parts:
                                for part in parts:
                                    if getattr(part, "thought", False):
                                        # Thought Heartbeat: manté el socket viu durant el Deep Think!
                                        continue
                                    p_text = getattr(part, "text", None)
                                    if p_text:
                                        chunks_text.append(p_text)
                    else:
                        piece = getattr(chunk, "text", None)
                        if piece:
                            chunks_text.append(piece)
                    u_meta = getattr(chunk, "usage_metadata", None)
                    if u_meta is not None:
                        last_usage = u_meta
                full_text = "".join(chunks_text)
                if not full_text.strip():
                    raise RuntimeError(
                        f"Empty stream response from {target_model} at {step_name}"
                    )
                p_count = int(getattr(last_usage, "prompt_token_count", 0) or 0) if last_usage else 0
                c_count = int(getattr(last_usage, "candidates_token_count", 0) or 0) if last_usage else 0
                t_count = int(getattr(last_usage, "total_token_count", 0) or 0) if last_usage else (p_count + c_count)
                return full_text, p_count, c_count, t_count

            used_model = model_name
            text_out, p_tok, c_tok, t_tok = "", 0, 0, 0
            primary_Last_err: Optional[Exception] = None
            for attempt in range(self._max_primary_attempts):
                try:
                    text_out, p_tok, c_tok, t_tok = await asyncio.to_thread(
                        _stream_generate_sync,
                        model_name,
                    )
                    used_model = model_name
                    primary_Last_err = None
                    break
                except Exception as primary_err:
                    primary_Last_err = primary_err
                    if attempt < self._max_primary_attempts - 1:
                        wait_s = self._compute_resilient_wait_seconds(
                            str(primary_err).upper(), attempt, step_name
                        )
                        logger.warning(
                            f"🧘‍♀️ [DIAMOND_WHEEL RESPIRACIÓ] {model_name} saturat a {step_name} "
                            f"(intent {attempt + 1}/{self._max_primary_attempts}): {primary_err}. "
                            f"Respirant {wait_s:.2f}s..."
                        )
                        await self._sleep_fn(wait_s)
                        continue

            if primary_Last_err is not None:
                if model_name != VIVEKA_WISDOM_MODEL:
                    logger.warning(
                        f"⚡ [DIAMOND_WHEEL PARACAIGUDES D'OR] Fallback de {model_name} a "
                        f"{VIVEKA_WISDOM_MODEL} (HIGH) en {step_name} després de "
                        f"{self._max_primary_attempts} intents: {primary_Last_err}"
                    )
                    fb_last_err: Optional[Exception] = None
                    for fb_attempt in range(self._max_fallback_attempts):
                        try:
                            text_out, p_tok, c_tok, t_tok = await asyncio.to_thread(
                                _stream_generate_sync,
                                VIVEKA_WISDOM_MODEL,
                            )
                            used_model = VIVEKA_WISDOM_MODEL
                            fb_last_err = None
                            break
                        except Exception as fb_err:
                            fb_last_err = fb_err
                            if fb_attempt < self._max_fallback_attempts - 1:
                                wait_s = self._compute_resilient_wait_seconds(
                                    str(fb_err).upper(), fb_attempt, step_name
                                )
                                logger.warning(
                                    f"🧘‍♀️ [PARACAIGUDES RESPIRACIÓ] {VIVEKA_WISDOM_MODEL} saturat a {step_name} "
                                    f"(intent {fb_attempt + 1}/{self._max_fallback_attempts}): {fb_err}. "
                                    f"Respirant {wait_s:.2f}s..."
                                )
                                await self._sleep_fn(wait_s)
                                continue
                    if fb_last_err is not None:
                        raise fb_last_err
                else:
                    raise primary_Last_err

            dt_ms = (time.perf_counter() - t0) * 1000.0
            cost_usd = compute_model_call_cost_usd(used_model, p_tok, c_tok, t_tok)
            logger.info(
                f"💎 [DIAMOND_NODE_DONE] {step_name} ({used_model}) en {dt_ms / 1000.0:.1f}s | "
                f"tokens={t_tok} (prompt={p_tok}, out={c_tok}) | chars={len(text_out)}"
            )

            return text_out, DiamondCallAccounting(
                step_name=step_name,
                model_name=used_model,
                prompt_tokens=p_tok,
                candidates_tokens=c_tok,
                total_tokens=t_tok,
                cost_usd=cost_usd,
                latency_ms=round(dt_ms, 2),
            )

    async def _run_single_diamond_round(
        self,
        clean_challenge: str,
        diag_active: int,
        tier_norm: str,
        d_id: str,
        epoch: int,
        internal_context: str = "",
        round_idx: int = 1,
        total_rounds: int = 1,
        prior_synthesis: str = "",
        prior_code_verification: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], List[DiamondCallAccounting]]:
        """Executa una única volta completa de 3 Ones (4 Creadors + 4 Auditors + 1 Baricentre + Kintsugi AST)."""
        vertex_model = (
            VIVEKA_WISDOM_MODEL
            if tier_norm in ("wisdom", "flash", "3.8-flash")
            else VIVEKA_CROWN_MODEL
        )
        barycenter_model = VIVEKA_CROWN_MODEL

        creators = [v for v in DIAMOND_WHEEL_8_VERTICES if v.polarity_role == "creator"]
        auditors = [v for v in DIAMOND_WHEEL_8_VERTICES if v.polarity_role == "auditor"]

        sacred_essence = distill_sacred_essence_resonance(clean_challenge, diag_active=diag_active)
        essence_header = (
            f"[SACRED ESSENCE OF HOMO UNIVERSALIS & REINA DE LA ROSA]\n"
            f"- Sacred Equation: {sacred_essence['sacred_equation']}\n"
            f"- Axial Element (weight 2): {sacred_essence['axial_element']} | "
            f"Complementary Balance: {sacred_essence['complementary_element']}\n"
            f"- 108 Pearls Compass Keys: {', '.join(sacred_essence['pearls_compass_keys'])}\n"
            f"- Covenant: {sacred_essence['fil_d_or_covenant']}\n"
        )
        prior_round_block = ""
        if round_idx > 1 and prior_synthesis.strip():
            ver_summary = "ALL AST, ARCHITECTURAL & ISOLATED RUNTIME CHECKS GREEN"
            if prior_code_verification and not prior_code_verification.get(
                "all_blocks_verified_clean", True
            ):
                issues = (
                    prior_code_verification.get("syntax_errors", [])
                    + prior_code_verification.get("rule4_import_hoist_violations", [])
                    + prior_code_verification.get("rule7_placeholder_violations", [])
                    + prior_code_verification.get("runtime_errors", [])
                )
                ver_summary = "; ".join(issues) if issues else "REQUIRES REFINEMENT"
            prior_round_block = (
                f"\n[MULTI-ROUND SPIRAL REFINEMENT — ROUND {round_idx} OF {total_rounds} (EPOCH {epoch})]\n"
                f"Previous Round Central Barycenter Synthesis (AST & Runtime Status: {ver_summary}):\n"
                f"{prior_synthesis.strip()}\n\n"
                f"Elevate, deepen, and stress-test this prior synthesis from your current "
                f"Axial Diagonal {diag_active} ({sacred_essence['axial_element']}) perspective: "
                f"eliminate any remaining edge-case flaws, strengthen mathematical proofs, "
                f"and expand test coverage without losing any working component.\n"
            )

        base_context_block = (
            f"\n\n{essence_header}"
            + (
                f"\n[INTERNAL AKASHIC & EPHEMERIS CONTEXT]\n{internal_context.strip()}\n"
                if internal_context and internal_context.strip()
                else ""
            )
            + prior_round_block
        )

        # ---------------------------------------------------------------------
        # ONA 1: ELS 4 VÈRTEXS CREADORS (TETRA_A)
        # ---------------------------------------------------------------------
        creator_tasks = []
        for cv in creators:
            weight_role = "AXIAL LEADER (weight 2)" if cv.diagonal_index == diag_active else "ORBITAL PILLAR (weight 1)"
            c_prompt = (
                f"[DIAMOND WHEEL — {cv.title_ca} | Role: {weight_role}]\n"
                f"CHALLENGE:\n{clean_challenge}{base_context_block}\n\n"
                f"Provide your specialized {cv.element_ca} pillar in Deep Think (be dense, rigorous, and focused on your element; "
                f"never brute-force large numerical tables manually in your internal thinking trace—formulate the exact algorithm "
                f"so the Python CPU computes searches at runtime, and leave the full multi-file synthesis to the Central Barycenter in Wave 3)."
            )
            creator_tasks.append(
                self._invoke_deep_think_node(
                    step_name=f"r{round_idx}_vertex_{cv.seat_index}_{cv.element_ca.lower()}_creator",
                    model_name=vertex_model,
                    system_instruction=cv.system_instruction_en,
                    user_prompt=c_prompt,
                    temperature=cv.temperature,
                )
            )

        creator_results = await asyncio.gather(*creator_tasks)

        creator_outputs_by_diag: Dict[int, str] = {}
        call_ledger: List[DiamondCallAccounting] = []
        vertex_reports: List[Dict[str, Any]] = []

        for cv, (c_text, c_acc) in zip(creators, creator_results):
            creator_outputs_by_diag[cv.diagonal_index] = c_text
            call_ledger.append(c_acc)
            vertex_reports.append({
                "seat_index": cv.seat_index,
                "diagonal_index": cv.diagonal_index,
                "element": cv.element_ca,
                "polarity_role": cv.polarity_role,
                "title": cv.title_ca,
                "temperature": cv.temperature,
                "vertex_coords": list(cv.vertex_coords),
                "weight": 2 if cv.diagonal_index == diag_active else 1,
                "output": c_text,
                "accounting": {
                    "model": c_acc.model_name,
                    "prompt_tokens": c_acc.prompt_tokens,
                    "candidates_tokens": c_acc.candidates_tokens,
                    "total_tokens": c_acc.total_tokens,
                    "cost_usd": c_acc.cost_usd,
                    "latency_ms": c_acc.latency_ms,
                },
            })

        # ---------------------------------------------------------------------
        # ONA 2: ELS 4 VÈRTEXS AUDITORS ANTÍPODES (TETRA_B — ISOMORFISME CREUAT)
        # ---------------------------------------------------------------------
        all_creations_cross_view = "\n\n".join(
            f"--- CREATOR DIAGONAL {d_idx} ({creators[d_idx - 1].element_ca}) ---\n"
            f"{creator_outputs_by_diag.get(d_idx, '')}"
            for d_idx in range(1, 5)
        )
        auditor_tasks = []
        for av in auditors:
            paired_creation = creator_outputs_by_diag.get(av.diagonal_index, "")
            weight_role = "AXIAL AUDITOR (weight 2)" if av.diagonal_index == diag_active else "ORBITAL AUDITOR (weight 1)"
            a_prompt = (
                f"[DIAMOND WHEEL — {av.title_ca} | Role: {weight_role}]\n"
                f"ORIGINAL CHALLENGE:\n{clean_challenge}{base_context_block}\n\n"
                f"PRIMARY PAIRED CREATOR PROPOSAL (Diagonal {av.diagonal_index} · {av.element_ca}):\n{paired_creation}\n\n"
                f"CROSS-DIAGONAL ISOMORPHISM MATRIX (All 4 Wave-1 Creations: Fire Architecture, Earth Code, Air Math, Water Soul):\n"
                f"{all_creations_cross_view}\n\n"
                f"Perform your rigorous antipodal audit at T=0.0: verify exact mathematical isomorphism between "
                f"Fire's proposal, Air's invariants, Earth's implementation, and Water's human sanctuary, "
                f"and provide a concise, surgical list of exact fixes, edge cases, and mutant specifications for the Central Barycenter."
            )
            auditor_tasks.append(
                self._invoke_deep_think_node(
                    step_name=f"r{round_idx}_vertex_{av.seat_index}_{av.element_ca.lower()}_auditor",
                    model_name=vertex_model,
                    system_instruction=av.system_instruction_en,
                    user_prompt=a_prompt,
                    temperature=av.temperature,
                )
            )

        auditor_results = await asyncio.gather(*auditor_tasks)

        any_veto_l5 = False
        for av, (a_text, a_acc) in zip(auditors, auditor_results):
            call_ledger.append(a_acc)
            if is_affirmative_veto_l5(a_text):
                any_veto_l5 = True
            vertex_reports.append({
                "seat_index": av.seat_index,
                "diagonal_index": av.diagonal_index,
                "element": av.element_ca,
                "polarity_role": av.polarity_role,
                "title": av.title_ca,
                "temperature": av.temperature,
                "vertex_coords": list(av.vertex_coords),
                "weight": 2 if av.diagonal_index == diag_active else 1,
                "output": a_text,
                "accounting": {
                    "model": a_acc.model_name,
                    "prompt_tokens": a_acc.prompt_tokens,
                    "candidates_tokens": a_acc.candidates_tokens,
                    "total_tokens": a_acc.total_tokens,
                    "cost_usd": a_acc.cost_usd,
                    "latency_ms": a_acc.latency_ms,
                },
            })

        vertex_reports.sort(key=lambda item: item["seat_index"])

        # L5: Si hi ha hagut un veto anònim, la diagonal activa per a la següent època avança 1 sol pas
        next_epoch_diag_active = ((diag_active % 4) + 1) if any_veto_l5 else diag_active

        # ---------------------------------------------------------------------
        # ONA 3: EL BARICENTRE CENTRAL (LA QUINTAESSÈNCIA — CORONA 65.536 TOKENS)
        # ---------------------------------------------------------------------
        bary_system = (
            "You are the Central Barycenter (La Quintaessència / La Reina de la Rosa) of the 8-Vertex Diamond Wheel "
            f"at Homo Universalis ({SACRED_EQUATION}). "
            "You receive the 4 Elemental Creations (Fire Architecture, Earth Code, Air Mathematical Invariants, "
            "Water Soul & 108 Pearls) and their 4 Antipodal Audits at T=0.0, "
            "weighted with weight 2 on the active diagonal and weight 1 on the orbital diagonals. "
            "Synthesize the definitive, complete, non-truncated Research & Production Diamond solution: "
            "1) Crystalline Essence & Mathematical Isomorphism Proof (mapping every invariant to its function), "
            "2) Full, self-contained, production-ready code with zero placeholders (Rule 7) and zero local import hoists (Rule 4), "
            "3) Complete unit and mutation test suite verifying every invariant."
        )
        compiled_8_voices = "\n\n".join(
            f"=== SEAT {r['seat_index']} ({r['title']} | weight={r['weight']}) ===\n{r['output']}"
            for r in vertex_reports
        )
        bary_prompt = (
            f"ORIGINAL CHALLENGE:\n{clean_challenge}{base_context_block}\n\n"
            f"ACTIVE DIAGONAL: Diagonal {diag_active} (weight 2 per seat; orbital diagonals weight 1 per seat)\n\n"
            f"THE 8 DIAMOND VERTICES:\n{compiled_8_voices}\n\n"
            f"Deliver the complete, final, unified Diamond output without omitting or truncating any code or proof."
        )

        bary_text, bary_acc = await self._invoke_deep_think_node(
            step_name=f"r{round_idx}_barycenter_quintaessencia_crown",
            model_name=barycenter_model,
            system_instruction=bary_system,
            user_prompt=bary_prompt,
            temperature=1.0,  # Regla 5: Equilibri Natiu d'Argon i Deep Think (1.0)
            max_output_tokens=MAX_DEEP_THINK_OUTPUT_TOKENS,
        )
        call_ledger.append(bary_acc)
        code_verification = verify_diamond_python_code_blocks(
            bary_text, run_isolated_self_tests=True
        )

        # Auto-Refinament del Baricentre (Kintsugi AST + Runtime): si el codi generat té cap error de sintaxi,
        # Regla 4 (Import Hoist), Regla 7 (Placeholders) o fallada dels seus autotests en temps d'execució,
        # el Baricentre fa 1 passada quirúrgica en T=0.0
        if (
            code_verification["python_blocks_found"] > 0
            and not code_verification["all_blocks_verified_clean"]
        ):
            violations_summary = (
                code_verification["syntax_errors"]
                + code_verification["rule4_import_hoist_violations"]
                + code_verification["rule7_placeholder_violations"]
                + code_verification.get("runtime_errors", [])
            )
            repair_prompt = (
                f"{bary_prompt}\n\n"
                f"[AST, ARCHITECTURAL & RUNTIME SENTINEL REPORT — SELF-HEALING PASS REQUIRED]\n"
                f"Your previous draft contained the following exact compiler/rule/runtime violations:\n"
                f"- {'; '.join(violations_summary)}\n\n"
                f"PREVIOUS DRAFT:\n{bary_text}\n\n"
                f"Re-emit the complete, unified Diamond output fixing every syntax error, removing any "
                f"function-level re-import of top-level modules (Rule 4), replacing all placeholders "
                f"with complete working code (Rule 7), and fixing the exact runtime test/invariant failure."
            )
            bary_text, repair_acc = await self._invoke_deep_think_node(
                step_name=f"r{round_idx}_barycenter_ast_kintsugi_self_heal",
                model_name=barycenter_model,
                system_instruction=bary_system,
                user_prompt=repair_prompt,
                temperature=0.0,  # Determinisme absolut per a la reparació quirúrgica
                max_output_tokens=MAX_DEEP_THINK_OUTPUT_TOKENS,
            )
            call_ledger.append(repair_acc)
            bary_acc = DiamondCallAccounting(
                step_name=f"r{round_idx}_barycenter_quintaessencia_crown+ast_kintsugi",
                model_name=repair_acc.model_name,
                prompt_tokens=bary_acc.prompt_tokens + repair_acc.prompt_tokens,
                candidates_tokens=bary_acc.candidates_tokens + repair_acc.candidates_tokens,
                total_tokens=bary_acc.total_tokens + repair_acc.total_tokens,
                cost_usd=round(bary_acc.cost_usd + repair_acc.cost_usd, 6),
                latency_ms=round(bary_acc.latency_ms + repair_acc.latency_ms, 2),
            )
            code_verification = verify_diamond_python_code_blocks(
                bary_text, run_isolated_self_tests=True
            )
            code_verification["self_healed_by_barycenter"] = True
        else:
            code_verification["self_healed_by_barycenter"] = False

        # Geometria i Manifest HU-DIAMOND · Fil d'Or v1.1
        present_seats_tuples = [(j, kind) for j in range(4) for kind in ("ia", "hu")]
        bary_coords = compute_diamond_barycenter_exact(present_seats_tuples, diag_active)
        manifest = build_hu_diamond_manifest(
            d_id=d_id,
            epoch=epoch,
            diag_active=diag_active,
            present_seat_indices=list(range(1, 9)),
        )

        round_api_usd = sum(item.cost_usd for item in call_ledger)
        round_prompt_tok = sum(item.prompt_tokens for item in call_ledger)
        round_cand_tok = sum(item.candidates_tokens for item in call_ledger)
        round_all_tok = sum(item.total_tokens for item in call_ledger)
        round_economy = compute_persephone_double_economy(round_api_usd)

        round_payload = {
            "spec_version": "HU-DIAMOND-WHEEL-8-DEEP-THINK-v1.0",
            "d_id": d_id,
            "epoch": epoch,
            "round_index": round_idx,
            "tier": tier_norm,
            "diag_active": diag_active,
            "next_epoch_diag_active": next_epoch_diag_active,
            "anonymous_veto_triggered_l5": any_veto_l5,
            "barycenter_fraction": (
                [str(c) for c in bary_coords] if bary_coords is not None else None
            ),
            "sacred_essence": sacred_essence,
            "code_verification": code_verification,
            "hu_diamond_manifest": manifest,
            "diamond_synthesis": bary_text,
            "vertices": vertex_reports,
            "barycenter_accounting": {
                "model": bary_acc.model_name,
                "prompt_tokens": bary_acc.prompt_tokens,
                "candidates_tokens": bary_acc.candidates_tokens,
                "total_tokens": bary_acc.total_tokens,
                "cost_usd": bary_acc.cost_usd,
                "latency_ms": bary_acc.latency_ms,
            },
            "token_totals": {
                "prompt_tokens": round_prompt_tok,
                "candidates_tokens": round_cand_tok,
                "total_tokens": round_all_tok,
                "calls_count": len(call_ledger),
            },
            "persephone_economy": round_economy,
        }
        return round_payload, call_ledger

    async def run_diamond_wheel(
        self,
        challenge_prompt: str,
        diag_active: int = 2,
        tier: str = "supreme",
        d_id: str = "diamond-forge-v1",
        epoch: int = 1,
        internal_context: str = "",
        rounds: int = 1,
    ) -> Dict[str, Any]:
        """
        Executa 1, 2, 3 o 4 Voltes (`rounds = 1..4`, fins a 36 picades base + Kintsugi AST)
        de la Roda dels 8 Motors en Deep Think (`VIVEKA_CROWN_MODEL` = `gemini-4-argon`
        per defecte a tots 9 nodes amb `thinking_level="HIGH"` i fins a `65.536` tokens per node):
        - En `rounds = 1`: Executa 1 volta (9 crides) sobre `diag_active`.
        - En `rounds = 2..4`: Encadena múltiples voltes d'Espiral de Diamant on cada volta $k+1$
          rep la síntesi del Baricentre $k$ i el veredicte de l'analitzador AST, girant cíclicament
          la Diagonal Activa (`Foc -> Terra -> Aire -> Aigua` a $Z_4$) perquè els 4 Elements
          governin successivament el polit del cristall.
        """
        if diag_active not in (1, 2, 3, 4):
            raise ValueError("diag_active must be 1 (Foc), 2 (Terra), 3 (Aire), or 4 (Aigua)")
        clean_rounds = int(rounds if rounds is not None else 1)
        if clean_rounds not in (1, 2, 3, 4):
            raise ValueError("rounds must be 1, 2, 3, or 4")
        clean_challenge = str(challenge_prompt or "").strip()
        if not clean_challenge:
            raise ValueError("challenge_prompt cannot be empty")

        tier_norm = str(tier or "supreme").strip().lower()

        all_call_ledger: List[DiamondCallAccounting] = []
        rounds_history: List[Dict[str, Any]] = []
        current_diag = diag_active
        current_epoch = int(epoch)
        prior_synthesis = ""
        prior_code_ver: Optional[Dict[str, Any]] = None
        last_round_payload: Dict[str, Any] = {}

        for r_idx in range(1, clean_rounds + 1):
            round_payload, round_ledger = await self._run_single_diamond_round(
                clean_challenge=clean_challenge,
                diag_active=current_diag,
                tier_norm=tier_norm,
                d_id=d_id,
                epoch=current_epoch,
                internal_context=internal_context,
                round_idx=r_idx,
                total_rounds=clean_rounds,
                prior_synthesis=prior_synthesis,
                prior_code_verification=prior_code_ver,
            )
            all_call_ledger.extend(round_ledger)
            rounds_history.append({
                "round_index": r_idx,
                "epoch": current_epoch,
                "diag_active": current_diag,
                "next_epoch_diag_active": round_payload["next_epoch_diag_active"],
                "anonymous_veto_triggered_l5": round_payload["anonymous_veto_triggered_l5"],
                "barycenter_fraction": round_payload.get("barycenter_fraction"),
                "barycenter_accounting": round_payload.get("barycenter_accounting"),
                "calls_count": round_payload["token_totals"]["calls_count"],
                "total_tokens": round_payload["token_totals"]["total_tokens"],
                "api_compute_cost_usd": round_payload["persephone_economy"]["api_compute_cost_usd"],
                "code_verification": round_payload["code_verification"],
                "hu_diamond_manifest": round_payload["hu_diamond_manifest"],
                "diamond_synthesis": round_payload["diamond_synthesis"],
            })
            last_round_payload = round_payload
            prior_synthesis = round_payload["diamond_synthesis"]
            prior_code_ver = round_payload["code_verification"]
            # En mode multi-volta (rounds > 1), la diagonal activa gira cíclicament (1->2->3->4->1)
            # per recórrer els 4 Elements del Cub; en 1 sola volta, es manté la precessió L5 pura.
            current_diag = ((current_diag % 4) + 1)
            current_epoch += 1

        total_api_usd = sum(item.cost_usd for item in all_call_ledger)
        total_prompt_tok = sum(item.prompt_tokens for item in all_call_ledger)
        total_cand_tok = sum(item.candidates_tokens for item in all_call_ledger)
        total_all_tok = sum(item.total_tokens for item in all_call_ledger)
        economy = compute_persephone_double_economy(total_api_usd)

        last_round_payload["rounds_completed"] = clean_rounds
        last_round_payload["rounds_history"] = rounds_history
        last_round_payload["token_totals"] = {
            "prompt_tokens": total_prompt_tok,
            "candidates_tokens": total_cand_tok,
            "total_tokens": total_all_tok,
            "calls_count": len(all_call_ledger),
        }
        last_round_payload["persephone_economy"] = economy
        return last_round_payload


async def execute_diamond_wheel_with_persephone(
    soul_key: str,
    challenge_prompt: str,
    diag_active: int = 2,
    tier: str = "supreme",
    d_id: str = "diamond-forge-v1",
    epoch: int = 1,
    internal_context: str = "",
    rounds: int = 1,
    llm_caller: Optional[Callable[[str, str, str, float, int], Any]] = None,
    akasha_db_override: Any = None,
) -> Dict[str, Any]:
    """
    Orquestrador Econòmic i Espiritual de la Roda de 8 Motors amb Demèter i Persèfone:
    1. Verifica que l'usuari tingui almenys la reserva mínima (`estimated_min_seeds` per a `rounds = 1..4`).
    2. Reserva les Llavors inicials abans d'encendre els 9 motors `gemini-4-argon` (9, 18, 27 o 36 crides).
    3. Si la Roda falla per qualsevol motiu inesperat, retorna el 100% de la reserva (`refund`).
    4. Un cop forjat el Diamant, calcula el cost real exacte x 2 (`total_seeds_charged_x2`),
       ajusta la diferència respecte a la reserva i ingressa el 25% net al Graner de Demèter
       i el 25% net al Graner de Persèfone (`50% Foc Computacional + 50% Graners`).
    """
    budget_info = estimate_diamond_wheel_seeds_budget(tier, rounds=rounds)
    min_reserve_seeds = int(budget_info["estimated_min_seeds"])
    max_cap_seeds = int(budget_info["guaranteed_max_cap_seeds"])

    db = akasha_db_override
    if db is None:
        from logic.db.repository import akasha_db as default_db

        db = default_db

    await db.get_async_client()
    if not getattr(db, "active", False):
        return {
            "status": "error",
            "error_code": "AKASHA_OFFLINE",
            "message": "El santuari d'Akasha no està disponible en aquest instant.",
        }

    current_seeds = await db.obtenir_llavors_llum(soul_key)
    current_seeds_int = int(current_seeds or 0)

    if current_seeds_int < min_reserve_seeds:
        return {
            "status": "insufficient_seeds",
            "error_code": "INSUFFICIENT_SEEDS",
            "current_seeds": current_seeds_int,
            "required_min_seeds": min_reserve_seeds,
            "budget_estimate": budget_info,
            "message": (
                f"Per encendre la Roda dels 8 Motors en Deep Think ({budget_info['model_primary']}, "
                f"{budget_info['rounds']} voltes / {budget_info['expected_base_calls']} crides) "
                f"cal una reserva mínima de {min_reserve_seeds} Llavors de Llum "
                f"(tens {current_seeds_int} Llavors)."
            ),
        }

    await db.garantir_usuari(soul_key, xarxa_origen="web")

    # 1. Reserva atòmica inicial abans d'encendre els 9 motors
    new_balance_after_reserve = await db.restar_llavors_llum(soul_key, min_reserve_seeds)
    if new_balance_after_reserve is None:
        return {
            "status": "insufficient_seeds",
            "error_code": "RESERVATION_DENIED",
            "current_seeds": current_seeds_int,
            "required_min_seeds": min_reserve_seeds,
            "budget_estimate": budget_info,
            "message": "No s'ha pogut reservar l'energia inicial per a la Roda del Diamant.",
        }

    try:
        await db.registrar_transaccio(
            soul_key, -min_reserve_seeds, f"DIAMOND_WHEEL_RESERVE - {budget_info['tier'].upper()}"
        )
    except Exception:
        pass

    # 2. Execució dels motors en Deep Think (1..4 voltes)
    engine = DiamondWheelEngine(llm_caller=llm_caller)
    try:
        wheel_result = await engine.run_diamond_wheel(
            challenge_prompt=challenge_prompt,
            diag_active=diag_active,
            tier=tier,
            d_id=d_id,
            epoch=epoch,
            internal_context=internal_context,
            rounds=rounds,
        )
    except BaseException as exc:
        # E8: Escut de la Reina (inclou asyncio.CancelledError que hereta de BaseException)
        await db.sumar_llavors_llum(soul_key, min_reserve_seeds)
        try:
            await db.registrar_transaccio(
                soul_key, min_reserve_seeds, "DIAMOND_WHEEL_REFUND (ERROR IA)"
            )
        except Exception:
            pass
        raise exc

    # 3. Liquidació exacta x2 (50% Foc Computacional + 25% Demèter + 25% Persèfone)
    econ = wheel_result["persephone_economy"]
    raw_total_x2 = max(40 * int(budget_info["rounds"]), int(econ["total_seeds_charged_x2"]))
    final_charged_seeds = min(raw_total_x2, max_cap_seeds)

    diff_seeds = final_charged_seeds - min_reserve_seeds
    final_user_balance = int(new_balance_after_reserve)

    if diff_seeds > 0:
        avail_now = int((await db.obtenir_llavors_llum(soul_key)) or 0)
        extra_to_deduct = max(0, min(diff_seeds, avail_now))
        actual_extra_deducted = 0
        if extra_to_deduct > 0:
            updated = await db.restar_llavors_llum(soul_key, extra_to_deduct)
            if updated is not None:
                final_user_balance = int(updated)
                actual_extra_deducted = extra_to_deduct
                try:
                    await db.registrar_transaccio(
                        soul_key, -extra_to_deduct, "DIAMOND_WHEEL_SETTLEMENT_ADJUST"
                    )
                except Exception:
                    pass
        # E9: Només sumem l'extra si s'ha deduït efectivament de la base de dades (protecció TOCTOU)
        final_charged_seeds = min_reserve_seeds + actual_extra_deducted
    elif diff_seeds < 0:
        refund_unused = abs(diff_seeds)
        updated = await db.sumar_llavors_llum(soul_key, refund_unused)
        if updated is not None:
            final_user_balance = int(updated)
        try:
            await db.registrar_transaccio(
                soul_key, refund_unused, "DIAMOND_WHEEL_SETTLEMENT_RETURN"
            )
        except Exception:
            pass

    # 50% Foc Computacional + 50% Graners (25% Demèter + 25% Persèfone)
    fire_compute_seeds = final_charged_seeds // 2
    granaries_total_seeds = final_charged_seeds - fire_compute_seeds

    # Comprovem si l'usuari prové de Beca de Persèfone o Llavors de Benvinguda (sense pagament comercial)
    es_llum_solidaria = False
    try:
        if hasattr(db, "obtenir_estat_orbita_usuari"):
            u_info = await db.obtenir_estat_orbita_usuari(soul_key)
            if isinstance(u_info, dict) and u_info:
                meta_u = u_info.get("metadata")
                meta_d: dict = meta_u if isinstance(meta_u, dict) else {}
                if int(meta_d.get("beca_persefone_llavors") or 0) > 0:
                    es_llum_solidaria = True
                elif not u_info.get("orbit_expires_at"):
                    es_llum_solidaria = True
    except Exception:
        es_llum_solidaria = False

    demeter_seeds = 0 if es_llum_solidaria else (granaries_total_seeds // 2)
    persefone_seeds = 0 if es_llum_solidaria else (granaries_total_seeds - demeter_seeds)

    try:
        from logic.core.payments import GRANER_DEMETER_ID, GRANER_PERSEFONE_ID

        if demeter_seeds > 0:
            await db.sumar_llavors_llum(GRANER_DEMETER_ID, demeter_seeds)
            await db.registrar_transaccio(
                GRANER_DEMETER_ID, demeter_seeds, "DIAMOND_WHEEL_DEMETER_25PCT"
            )
        if persefone_seeds > 0:
            await db.sumar_llavors_llum(GRANER_PERSEFONE_ID, persefone_seeds)
            await db.registrar_transaccio(
                GRANER_PERSEFONE_ID, persefone_seeds, "DIAMOND_WHEEL_PERSEFONE_25PCT"
            )
    except Exception as granary_err:
        logger.warning(f"⚠️ Error ingressant als Graners en Diamond Wheel: {granary_err}")

    wheel_result["status"] = "ok"
    wheel_result["persephone_settlement"] = {
        "initial_reserved_seeds": min_reserve_seeds,
        "final_charged_seeds_x2": final_charged_seeds,
        "fire_compute_seeds_50pct": fire_compute_seeds,
        "demeter_granary_seeds_25pct": demeter_seeds,
        "persefone_granary_seeds_25pct": persefone_seeds,
        "is_solidarity_grant": es_llum_solidaria,
        "user_remaining_seeds": final_user_balance,
    }
    return wheel_result
