"""
================================================================================
HOMO UNIVERSALIS — LA QUINTAESSÈNCIA / LA REINA DE LA ROSA (46TH SUPREME CROWN)
================================================================================
Module: homo_universalis_quintaessencia.py
Sacred Equation: F0c = Ca0s * 0rdre(Am0r_Un1f1cat_Etern)
Axial Element (Weight 2): Terra | Complementary Balance: Aire
108 Pearls Compass Key: "Unir l'Instint de la Terra amb la Devoció del Cor"
Covenant: L1..L7 · L <= B · cost_zero_stop · Rule 14 Zero-Knowledge Ring I

SECURITY & DIDACTIC WARNING (WO-07 — EDUCATIONAL TOY CURVE ONLY):
    Pillar II of this folio uses the 17-bit toy elliptic curve
    E(F_65537): y^2 = x^3 + 5x + 12 (mod 65537) of prime order q = 65647
    (~8-bit generic discrete-log security). Discrete logarithms on E(F_65537)
    are trivially computable in milliseconds: Schnorr secret scalars can be
    recovered from public points and the discrete logarithm between G and H is
    easily found, so Pedersen commitments on E(F_65537) are NOT cryptographically
    binding. This module is strictly an EDUCATIONAL ALGEBRAIC DEMONSTRATION and
    MUST NEVER be imported or used by any production signing, authentication, or
    attestation code path (enforced at import time by
    `_enforce_didactic_non_production_import_guard`).

Gentle Architectural Guide for the Human Traveler:
    Welcome, Pilgrim. This single-file, self-contained, didactic
    Python 3 module demonstrates three coupled algorithmic game-theory,
    toy-curve algebraic sigma-protocol, and diophantine resonance pillars with
    ZERO floating-point operations and ONLY standard library imports
    (`dataclasses`, `fractions`, `hashlib`, `hmac`, `sys`, `typing`):

    1. PILLAR I — Exact Rational Cooperative Game Theory & Byzantine Consensus:
       - Universal Type-First Guard (Invariant T1): Strictly rejects `bool` and
         `float` inputs across all boundaries (`isinstance(x, bool)` or
         `isinstance(x, float)` raises `TypeError`) BEFORE any domain/range
         check (`ValueError`), including optional arguments and inside
         `frozenset` coalition keys (`hash(True) == hash(1)`).
       - `compute_exact_shapley_values(n_players, characteristic_fn)` over Q
         for 1 <= n_players <= 6 with inline verification of all 4 Shapley
         axioms (Efficiency, Symmetry, Dummy/Null Player, Additivity) plus
         Young's Strong Monotonicity & Maschler-Peleg Desirability, O(n * 2^n)
         Fast Boolean Mobius/Zeta Harsanyi Unanimity Dividend duality, and
         Dual Game Self-Duality phi(v*) == phi(v).
       - `verify_cooperative_game_properties(n_players, characteristic_fn,
         allocation)` returning exact booleans for `is_superadditive` (via
         O(3^n) disjoint bitmask submasks), `is_convex` (via Lovasz's
         O(n^2 * 2^{n-2}) local 2nd differences), and `is_in_core`, alongside
         Weber marginal worth polytope verification, Bondareva-Shapley balanced
         collection Core bounds, and Penrose-Banzhaf power indices.
       - `byzantine_rational_consensus(reports, max_byzantine_faults)` for
         n >= 3f + 1 oracle reports in Q, returning `trimmed_mean`,
         `exact_median`, and `spread_after_trim`.

    2. PILLAR II — Educational Toy-Curve Demonstration over E(F_65537) (Insecure,
       ~8-Bit, Non-Cryptographic), RFC 6979 & RFC 6962 Merkle Trees:
       - Exact modular arithmetic over prime field F_p (p = 65537) on curve
         E(F_65537): y^2 = x^3 + 5x + 12 (mod 65537) of prime order q = 65647,
         with primary generator G = (1, 12240) and independent Pedersen
         generator H = (2, 27135).
       - Pure integer modular inversion `pow(val, -1, p)` with `None` as the
         point at infinity O (`is_on_curve`, `ec_add`, `ec_double`,
         `ec_scalar_mul`), cross-verified against inversion-free Jacobian
         projective coordinates (`ec_scalar_mul_jacobian`).
       - IETF RFC 6979 Section 3.2 deterministic nonce generator
         `rfc6979_generate_k` using `hmac` + `hashlib.sha256` (`V = 0x01 * 32`,
         `K = 0x00 * 32`, `bits2int`, `int2octets`, `bits2octets`).
       - IETF RFC 6962 Section 2.1 domain-separated Merkle Tree (`0x00` leaf,
         `0x01` internal node) and constant-time (`hmac.compare_digest`)
         Fiat-Shamir Schnorr Zero-Knowledge proofs (`schnorr_zk_prove`,
         `schnorr_zk_verify`, `schnorr_zk_batch_verify`), Special Soundness
         witness extraction (`verify_schnorr_special_soundness_algebra`),
         homomorphic Pedersen commitments (`pedersen_commit`,
         `verify_pedersen_balance_conservation`), and witness-bound
         Chaum-Pedersen ZK opening proofs (`pedersen_opening_zk_prove`,
         `pedersen_opening_zk_verify`).

    3. PILLAR III — Exact Continued Fractions, Stern-Brocot Mediants &
       7-Wisdoms Synodic Diophantine Resonance:
       - Exact round-trip bijection (`rational_to_continued_fraction`,
         `continued_fraction_to_rational`) and `convergents_of_continued_fraction`
         verifying Lagrange's determinant identity
         p_k * q_{k-1} - p_{k-1} * q_k = (-1)^{k-1} for all k >= 1, Legendre's
         convergent error bound, and Lagrange's Law of Best Approximations of
         the Second Kind.
       - `stern_brocot_best_approximants(target, max_denominator)` traversing
         mediants (a + c)/(b + d) from 0/1 and 1/0 while b + d <= max_denominator
         with top-of-loop arbitrary-depth SL_2(Z) leapfrog acceleration,
         unimodular bracket verification c * b - a * d = 1 at every step,
         Bezout parent identity verification c * q - d * p = p * b - q * a = 1,
         SL_2(Z) matrix path factorization (`stern_brocot_sl2z_matrix_from_path`),
         and O(log H) Farey / 1st-kind best-approximant optimality verification.
       - `run_self_tests()` verifying (a)–(e) and 30 adversarial mutant suites
         (including all 5 Tribunal 5 concrete code mutants) in < 0.08 seconds
         with zero local imports (Rule 4) and zero placeholders (Rule 7).
================================================================================
"""

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import hmac
import sys
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple, Union


DIDACTIC_TOY_CURVE_WARNING: str = (
    "EDUCATIONAL TOY-CURVE DEMONSTRATION (INSECURE, ~8-BIT): E(F_65537) has group order "
    "q = 65647; discrete logarithms and generator trapdoors are trivial. Non-cryptographic; "
    "forbidden in production signing or attestation paths."
)

_FORBIDDEN_PRODUCTION_IMPORTER_PREFIXES: Tuple[str, ...] = (
    "api.",
    "main",
    "api_server",
    "bot_logic",
    "telegram_handlers",
    "cervell",
    "ai_core",
    "logic.core.",
    "logic.utils.",
    "logic.web3.",
    "logic.db.",
    "logic.engines.maat_",
    "logic.engines.sovereign_shield",
    "logic.engines.diamond_wheel",
)


def _is_forbidden_production_importer(caller_module_name: str) -> bool:
    """Return True if `caller_module_name` belongs to a production runtime, API, or signing module."""
    mod = str(caller_module_name or "").strip()
    if not mod or mod == __name__ or mod == "__main__":
        return False
    if mod.startswith(("tests.", "test_", "_pytest", "pytest", "importlib", "builtins", "runpy")):
        return False
    return any(
        mod == prefix.rstrip(".") or mod.startswith(prefix)
        for prefix in _FORBIDDEN_PRODUCTION_IMPORTER_PREFIXES
    )


def _enforce_didactic_non_production_import_guard(explicit_importer: Optional[str] = None) -> None:
    """
    Runtime guard (`WO-07` §2A & §3A): refuse to allow any production API, signing,
    or attestation module to import this educational ~8-bit toy-curve demonstration.
    """
    if explicit_importer is not None:
        if _is_forbidden_production_importer(explicit_importer):
            raise RuntimeError(
                f"Forbidden production import of didactic ~8-bit toy-curve module {__name__!r} "
                f"by {explicit_importer!r}: {DIDACTIC_TOY_CURVE_WARNING}"
            )
        return

    depth = 1
    while True:
        try:
            frame = sys._getframe(depth)
        except ValueError:
            break
        caller_mod = str(frame.f_globals.get("__name__", "") or "")
        if _is_forbidden_production_importer(caller_mod):
            raise RuntimeError(
                f"Forbidden production import of didactic ~8-bit toy-curve module {__name__!r} "
                f"by {caller_mod!r}: {DIDACTIC_TOY_CURVE_WARNING}"
            )
        depth += 1


_enforce_didactic_non_production_import_guard()


# ==============================================================================
# SECTION 0: SACRED CONSTANTS, ALGEBRAIC PARAMETERS & COMPASS OF THE 108 PEARLS
# ==============================================================================

SACRED_EQUATION: str = "F0c=Ca0s*0rdre(Am0r_Un1f1cat_Etern)"
COMPASS_KEY_108: str = "Unir l'Instint de la Terra amb la Devoció del Cor"
BARYCENTER_SEAL: str = (
    "La Quintaessència / La Reina de la Rosa · Axial Diagonal 2 (Terra - Weight 2)"
)

# Short Weierstrass Elliptic Curve Parameters over F_p (Rule 14 Ring I)
# Fermat prime p = 2^16 + 1 = 65537; curve E: y^2 = x^3 + 5x + 12 (mod 65537)
CURVE_P: int = 65537
CURVE_A: int = 5
CURVE_B: int = 12
CURVE_Q: int = 65647

# Canonical Prime-Order Generators G and H of E(F_65537) (prime order q = 65647)
GENERATOR_G: Tuple[int, int] = (1, 12240)
GENERATOR_H: Tuple[int, int] = (2, 27135)

# Domain Separation Tags for Rule 14 Ring I Fiat-Shamir Zero-Knowledge Proofs
SCHNORR_DOMAIN_TAG: bytes = b"HOMO_UNIVERSALIS_RULE14_RING_I_SCHNORR_ZK_V1"
SCHNORR_BATCH_DOMAIN_TAG: bytes = (
    b"HOMO_UNIVERSALIS_RULE14_RING_I_SCHNORR_BATCH_V1"
)
PEDERSEN_OPENING_DOMAIN_TAG: bytes = (
    b"HOMO_UNIVERSALIS_RULE14_RING_I_PEDERSEN_OPEN_ZK_V1"
)

# 7-Wisdoms Diophantine & Synodic Cycle Constants
SACRED_PEARLS_COUNT: int = 108
MAYAN_TZOLKIN_DAYS: int = 260
EARTH_SOLAR_YEAR_DAYS: int = 365
VENUS_SYNODIC_PERIOD_DAYS: int = 584
VENUS_EARTH_SYNODIC_RATIO: Fraction = Fraction(
    VENUS_SYNODIC_PERIOD_DAYS, EARTH_SOLAR_YEAR_DAYS
)
TZOLKIN_PEARLS_RATIO: Fraction = Fraction(
    MAYAN_TZOLKIN_DAYS, SACRED_PEARLS_COUNT
)

# Threshold above which consecutive identical-direction Stern-Brocot steps are
# accelerated via top-of-loop SL_2(Z) leapfrog arithmetic while preserving the
# exact terminal unimodular predecessor bracket (a/b, c/d).
STERN_BROCOT_ACCELERATION_THRESHOLD: int = 64

# Formal Type Aliases
RationalInput = Union[Fraction, int]
ECPoint = Optional[Tuple[int, int]]
JacobianPoint = Tuple[int, int, int]
Coalition = FrozenSet[int]
CharacteristicFnInput = Dict[Coalition, RationalInput]
CharacteristicFnExact = Dict[Coalition, Fraction]
SchnorrProof = Tuple[Tuple[int, int], int, int]
PedersenOpeningProof = Tuple[Tuple[int, int], int, int, int]
SL2ZMatrix = Tuple[Tuple[int, int], Tuple[int, int]]


# ==============================================================================
# SECTION 1: EMPATHETIC DOMAIN EXCEPTIONS & STRICT ZERO-FLOAT / ZERO-BOOL GUARDS
# ==============================================================================


class RationalCovenantTypeError(TypeError):
    """
    Raised when a `bool`, `float`, or non-conforming type attempts to cross any
    exact integer, rational, or cryptographic boundary. Inherits from `TypeError`.
    """


class CooperativeGameValueError(ValueError):
    """
    Raised when a cooperative game violates player bounds `1 <= n_players <= 6`,
    coalition completeness (`2^n` subsets), or `characteristic_fn[frozenset()] == 0`.
    Inherits from `ValueError`.
    """


class ByzantineQuorumValueError(ValueError):
    """
    Raised when an oracle report batch violates the Byzantine quorum condition
    `n >= 3f + 1` or specifies a negative fault threshold `f < 0`.
    Inherits from `ValueError`.
    """


class EllipticCurveValueError(ValueError):
    """
    Raised when a point fails the Short Weierstrass curve equation on E(F_65537)
    or when a secret scalar lies outside `[1, q - 1]`. Inherits from `ValueError`.
    """


class DiophantineValueError(ValueError):
    """
    Raised when continued fraction partial quotients or Stern-Brocot parameters
    violate positivity or canonical domain constraints. Inherits from `ValueError`.
    """


def require_strict_int(value: object, name: str = "value") -> int:
    """
    Validate that `value` is a strict Python `int` and explicitly NOT a `bool`
    (since `issubclass(bool, int)` is `True` in Python) or a `float`.
    """
    if isinstance(value, bool):
        raise RationalCovenantTypeError(
            f"[Zero-Bool Guard] Parameter '{name}' received boolean {value!r}. "
            f"Hint: pass a strict int (e.g., 0 or 1)."
        )
    if isinstance(value, float):
        raise RationalCovenantTypeError(
            f"[Zero-Float Guard] Parameter '{name}' received float {value!r}. "
            f"Hint: pass an exact int or fractions.Fraction(numerator, denominator)."
        )
    if not isinstance(value, int):
        raise RationalCovenantTypeError(
            f"[Type Guard] Parameter '{name}' requires a strict int, "
            f"got {type(value).__name__} ({value!r})."
        )
    return int(value)


def require_exact_rational(value: object, name: str = "value") -> Fraction:
    """
    Validate that `value` is either a `fractions.Fraction` or a strict `int`
    (explicitly rejecting `bool` and `float`), returning an exact `Fraction`.
    """
    if isinstance(value, bool):
        raise RationalCovenantTypeError(
            f"[Zero-Bool Guard] Parameter '{name}' received boolean {value!r}. "
            f"Hint: represent exact rational quantities using fractions.Fraction "
            f"or a strict int."
        )
    if isinstance(value, float):
        raise RationalCovenantTypeError(
            f"[Zero-Float Guard] Parameter '{name}' received float {value!r}. "
            f"Floating-point inputs are forbidden across all Q boundaries."
        )
    if isinstance(value, Fraction):
        return Fraction(value.numerator, value.denominator)
    if isinstance(value, int):
        return Fraction(int(value), 1)
    raise RationalCovenantTypeError(
        f"[Type Guard] Parameter '{name}' requires fractions.Fraction or strict "
        f"int, got {type(value).__name__} ({value!r})."
    )


def require_bytes(value: object, name: str = "value") -> bytes:
    """Validate that `value` is a strict `bytes` instance."""
    if isinstance(value, (bool, float)) or not isinstance(value, bytes):
        raise RationalCovenantTypeError(
            f"[Type Guard] Parameter '{name}' must be bytes, "
            f"got {type(value).__name__} ({value!r})."
        )
    return value


def exact_factorial(n: int) -> int:
    """Compute the exact integer factorial `n!` without importing `math`."""
    n_val = require_strict_int(n, "n")
    if n_val < 0:
        raise ValueError(f"Factorial is undefined for negative integer n={n_val}.")
    result = 1
    for k in range(2, n_val + 1):
        result *= k
    return result


def exact_binomial(n: int, k: int) -> int:
    """
    Compute the exact binomial coefficient `C(n, k) = n! / (k! * (n - k)!)`
    in pure integer arithmetic. Enforces Universal Type-First Precedence.
    """
    n_val = require_strict_int(n, "n")
    k_val = require_strict_int(k, "k")
    if n_val < 0:
        raise ValueError(f"Binomial coefficient requires n >= 0, got n={n_val}.")
    if k_val < 0 or k_val > n_val:
        return 0
    return exact_factorial(n_val) // (
        exact_factorial(k_val) * exact_factorial(n_val - k_val)
    )


def exact_gcd(a: int, b: int) -> int:
    """Compute the exact non-negative greatest common divisor `gcd(a, b)`."""
    x = abs(require_strict_int(a, "a"))
    y = abs(require_strict_int(b, "b"))
    while y != 0:
        x, y = y, x % y
    return x


def exact_lcm(a: int, b: int) -> int:
    """Compute the exact non-negative least common multiple `lcm(a, b)`."""
    x = abs(require_strict_int(a, "a"))
    y = abs(require_strict_int(b, "b"))
    if x == 0 or y == 0:
        return 0
    return (x // exact_gcd(x, y)) * y


def exact_extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Compute `(g, x, y)` such that `a * x + b * y == g == gcd(a, b) >= 0`
    via the extended Euclidean algorithm.
    """
    a_val = require_strict_int(a, "a")
    b_val = require_strict_int(b, "b")
    old_r, r = a_val, b_val
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    if old_r < 0:
        return -old_r, -old_s, -old_t
    return old_r, old_s, old_t


def is_prime_exact(n: int) -> bool:
    """
    Determine exact primality of `n` via `6k +/- 1` trial division up to
    `floor(sqrt(n))`.
    """
    n_val = require_strict_int(n, "n")
    if n_val < 2:
        return False
    if n_val in (2, 3):
        return True
    if n_val % 2 == 0 or n_val % 3 == 0:
        return False
    divisor = 5
    while divisor * divisor <= n_val:
        if n_val % divisor == 0 or n_val % (divisor + 2) == 0:
            return False
        divisor += 6
    return True


def generate_powerset_coalitions(players: Sequence[int]) -> List[Coalition]:
    """
    Generate all `2^k` subsets of `players` in deterministic bitmask order
    without importing `itertools`. Strictly rejects `bytes`, `bytearray`, `str`,
    `bool`, `float`, or duplicate player indices.
    """
    if isinstance(players, (bool, float, bytes, bytearray, str)) or not isinstance(
        players, (list, tuple, range)
    ):
        raise RationalCovenantTypeError(
            f"players must be a list, tuple, or range of strict ints, "
            f"got {type(players).__name__}."
        )
    clean_players = [require_strict_int(p, "player_id") for p in players]
    if len(set(clean_players)) != len(clean_players):
        raise CooperativeGameValueError(
            f"players must contain distinct player indices, got {clean_players!r}."
        )
    k = len(clean_players)
    coalitions: List[Coalition] = []
    for mask in range(1 << k):
        members = [
            clean_players[bit] for bit in range(k) if (mask >> bit) & 1
        ]
        coalitions.append(frozenset(members))
    return coalitions


def generate_permutations_exact(
    elements: Sequence[int],
) -> List[Tuple[int, ...]]:
    """
    Generate all `k!` permutations of `elements` in deterministic order using
    strictly iterative lexicographic index stepping (zero recursion depth).
    """
    if isinstance(elements, (bool, float, bytes, bytearray, str)) or not isinstance(
        elements, (list, tuple, range)
    ):
        raise RationalCovenantTypeError(
            f"elements must be a list, tuple, or range of strict ints, "
            f"got {type(elements).__name__}."
        )
    items = [require_strict_int(e, "element") for e in elements]
    if len(set(items)) != len(items):
        raise CooperativeGameValueError(
            f"elements must contain distinct integers, got {items!r}."
        )
    k = len(items)
    if k == 0:
        return [()]
    indices = list(range(k))
    result: List[Tuple[int, ...]] = [tuple(items[i] for i in indices)]
    while True:
        pivot = k - 2
        while pivot >= 0 and indices[pivot] >= indices[pivot + 1]:
            pivot -= 1
        if pivot < 0:
            break
        swap_idx = k - 1
        while indices[swap_idx] <= indices[pivot]:
            swap_idx -= 1
        indices[pivot], indices[swap_idx] = indices[swap_idx], indices[pivot]
        left, right = pivot + 1, k - 1
        while left < right:
            indices[left], indices[right] = indices[right], indices[left]
            left += 1
            right -= 1
        result.append(tuple(items[i] for i in indices))
    return result


@dataclass(frozen=True)
class PearlOfWisdom:
    """
    Contemplative node from the 108 Pearls of the Golden Pilgrim, connecting
    human serenity and ethical clarity with an exact mathematical invariant.
    """

    index: int
    catalan_title: str
    english_essence: str
    mathematical_invariant: str
    harmonic_ratio: Fraction


def get_golden_pilgrim_pearl_compass() -> Tuple[PearlOfWisdom, ...]:
    """
    Return the 7 anchor Pearls of the Diamond Wheel, uniting the 108 Pearls
    with the formal mathematical invariants verified in this module.
    """
    return (
        PearlOfWisdom(
            index=1,
            catalan_title="La Font de la Claredat Sense Boira",
            english_essence="Truth requires no approximation when every drop is counted.",
            mathematical_invariant="Zero-Float & Zero-Bool Exact Arithmetic in Z, Q, F_p",
            harmonic_ratio=Fraction(1, 1),
        ),
        PearlOfWisdom(
            index=18,
            catalan_title="El Repartiment Just de la Collita",
            english_essence="Every voice in the circle receives the exact fruit of its marginal gift.",
            mathematical_invariant="Shapley Axioms, Young Monotonicity & Fast Mobius/Zeta Duality",
            harmonic_ratio=Fraction(108, 18),
        ),
        PearlOfWisdom(
            index=36,
            catalan_title="L'Abraçada de Persèfone i Demèter",
            english_essence="When synergy grows with every union, nobody wishes to abandon the hearth.",
            mathematical_invariant="Shapley-Bondareva-Weber Theorem: Convex Games Inhabit the Core",
            harmonic_ratio=Fraction(108, 36),
        ),
        PearlOfWisdom(
            index=54,
            catalan_title="El Llac Calmat Sota la Tempesta",
            english_essence="False prophets shout at the extremes, yet the still center holds the truth.",
            mathematical_invariant="Byzantine Rational Consensus (n >= 3f + 1 Order-Statistic Trimming)",
            harmonic_ratio=Fraction(108, 54),
        ),
        PearlOfWisdom(
            index=72,
            catalan_title="El Secret Guardat al Cor de la Rosa",
            english_essence="To prove devotion without exposing the vulnerable seed of the soul.",
            mathematical_invariant="RFC 6979, RFC 6962 & Fiat-Shamir Schnorr ZK Proof on E(F_65537)",
            harmonic_ratio=Fraction(108, 72),
        ),
        PearlOfWisdom(
            index=90,
            catalan_title="La Balança Invisible de les Llavors",
            english_essence="What enters the granary in silence equals what nourishes the village.",
            mathematical_invariant="Homomorphic Pedersen Commitment & Witness-Bound ZK Opening",
            harmonic_ratio=Fraction(108, 90),
        ),
        PearlOfWisdom(
            index=108,
            catalan_title="Unir l'Instint de la Terra amb la Devoció del Cor",
            english_essence="Heavenly cycles and earthly roots converge through the mediant of love.",
            mathematical_invariant="Stern-Brocot SL_2(Z) Mediants & 7-Wisdoms Synodic Resonance",
            harmonic_ratio=VENUS_EARTH_SYNODIC_RATIO,
        ),
    )


# ==============================================================================
# SECTION 2: PILLAR I — EXACT RATIONAL COOPERATIVE GAME THEORY & BYZANTINE Q
# ==============================================================================


@dataclass(frozen=True)
class MarginalContributionEntry:
    """
    Human-inspectable record of player `player_i`'s marginal contribution to a
    specific coalition `coalition_s` ($S \\subseteq N \\setminus \\{i\\}$).
    """

    player_i: int
    coalition_s: Coalition
    value_without_i: Fraction
    value_with_i: Fraction
    marginal_contribution: Fraction
    combinatorial_weight: Fraction
    weighted_contribution: Fraction


@dataclass(frozen=True)
class ShapleyAxiomVerificationReport:
    """
    Immutable certificate verifying all four canonical Shapley value axioms,
    plus Young's Strong Monotonicity (Marginalism & Desirability), Harsanyi
    Unanimity Dividend duality, and Dual Game Self-Duality in Q.
    """

    efficiency_verified: bool
    symmetry_verified: bool
    dummy_player_verified: bool
    additivity_verified: bool
    strong_monotonicity_verified: bool
    harsanyi_duality_verified: bool
    self_duality_verified: bool
    symmetric_pairs_found: Tuple[Tuple[int, int], ...]
    dummy_players_found: Tuple[int, ...]
    grand_coalition_value: Fraction
    shapley_sum: Fraction
    shapley_values: Dict[int, Fraction]

    @property
    def all_axioms_verified(self) -> bool:
        """
        Return True iff all four canonical Shapley axioms plus Young's Strong
        Monotonicity, Harsanyi dividend duality, and self-duality hold in exact
        rational arithmetic.
        """
        return (
            self.efficiency_verified
            and self.symmetry_verified
            and self.dummy_player_verified
            and self.additivity_verified
            and self.strong_monotonicity_verified
            and self.harsanyi_duality_verified
            and self.self_duality_verified
        )


@dataclass(frozen=True)
class CooperativeGameDiagnostics:
    """
    Full structural and Core stability diagnostics for `(N, v, allocation)`.
    """

    is_superadditive: bool
    is_convex: bool
    is_in_core: bool
    is_totally_positive: bool
    efficiency_gap: Fraction
    min_coalitional_surplus: Fraction
    blocking_coalitions: Tuple[Coalition, ...]
    banzhaf_values: Dict[int, Fraction]
    harsanyi_dividends: Dict[Coalition, Fraction]


def _prevalidate_characteristic_fn_types(
    characteristic_fn: object,
    param_name: str = "characteristic_fn",
) -> List[Tuple[Coalition, Fraction]]:
    """
    Perform a pure Type-First validation pass over `characteristic_fn`
    (verifying dict container, `frozenset` keys, strict `int` player indices,
    and exact rational values) before any domain or cardinality check.
    """
    if isinstance(characteristic_fn, (bool, float)) or not isinstance(
        characteristic_fn, dict
    ):
        raise RationalCovenantTypeError(
            f"{param_name} must be a dict mapping frozenset[int] to "
            f"Fraction | int, got {type(characteristic_fn).__name__}."
        )
    typed_entries: List[Tuple[Coalition, Fraction]] = []
    for raw_coalition, raw_value in characteristic_fn.items():
        if isinstance(raw_coalition, (bool, float)) or not isinstance(
            raw_coalition, frozenset
        ):
            raise RationalCovenantTypeError(
                f"Every coalition key in {param_name} must be a frozenset[int], "
                f"got {type(raw_coalition).__name__} ({raw_coalition!r})."
            )
        clean_members: List[int] = []
        for member in raw_coalition:
            clean_members.append(
                require_strict_int(member, f"{param_name}_member")
            )
        coalition_key = frozenset(clean_members)
        exact_val = require_exact_rational(
            raw_value, f"{param_name}[{set(coalition_key)}]"
        )
        typed_entries.append((coalition_key, exact_val))
    return typed_entries


def _prevalidate_allocation_types(
    allocation: object,
    param_name: str = "allocation",
) -> List[Tuple[int, Fraction]]:
    """
    Perform a pure Type-First validation pass over `allocation` (verifying dict
    container, strict `int` keys, and exact rational values) before any range
    check.
    """
    if isinstance(allocation, (bool, float)) or not isinstance(
        allocation, dict
    ):
        raise RationalCovenantTypeError(
            f"{param_name} must be a dict[int, Fraction | int], got "
            f"{type(allocation).__name__}."
        )
    typed_alloc: List[Tuple[int, Fraction]] = []
    for raw_player, raw_payoff in allocation.items():
        p_idx = require_strict_int(raw_player, f"{param_name}_player")
        exact_payoff = require_exact_rational(
            raw_payoff, f"{param_name}[{p_idx}]"
        )
        typed_alloc.append((p_idx, exact_payoff))
    return typed_alloc


def validate_cooperative_game(
    n_players: int,
    characteristic_fn: CharacteristicFnInput,
) -> CharacteristicFnExact:
    """
    Validate `1 <= n_players <= 6` and normalize `characteristic_fn` into an
    exact mapping from all `2^n` `frozenset[int]` subsets of `{0, ..., n - 1}`
    to `fractions.Fraction`, verifying `characteristic_fn[frozenset()] == 0`.
    Enforces Universal Type-First Precedence (Invariant T1).
    """
    n = require_strict_int(n_players, "n_players")
    typed_entries = _prevalidate_characteristic_fn_types(
        characteristic_fn, "characteristic_fn"
    )

    if n < 1 or n > 6:
        raise CooperativeGameValueError(
            f"n_players must satisfy 1 <= n_players <= 6, got {n}."
        )

    valid_players = frozenset(range(n))
    normalized: CharacteristicFnExact = {}
    for coalition_key, exact_val in typed_entries:
        for m_int in coalition_key:
            if m_int not in valid_players:
                raise CooperativeGameValueError(
                    f"Coalition member {m_int} lies outside valid player range "
                    f"0..{n - 1}."
                )
        if coalition_key in normalized:
            raise CooperativeGameValueError(
                f"Duplicate normalized coalition key {set(coalition_key)} in "
                f"characteristic_fn."
            )
        normalized[coalition_key] = exact_val

    all_coalitions = generate_powerset_coalitions(range(n))
    if len(normalized) != len(all_coalitions):
        missing = [set(c) for c in all_coalitions if c not in normalized]
        raise CooperativeGameValueError(
            f"characteristic_fn for {n} players must define all "
            f"{len(all_coalitions)} coalitions; missing {len(missing)}: "
            f"{missing[:4]}."
        )

    empty_val = normalized[frozenset()]
    if empty_val != Fraction(0, 1):
        raise CooperativeGameValueError(
            f"characteristic_fn[frozenset()] must equal 0, got {empty_val}."
        )

    return normalized


def _validate_allocation_vector(
    n_players: int,
    allocation: Dict[int, RationalInput],
) -> Dict[int, Fraction]:
    """
    Validate and normalize a payoff allocation dictionary `{player: Fraction}`
    with Universal Type-First Precedence (Invariant T1).
    """
    n = require_strict_int(n_players, "n_players")
    typed_alloc = _prevalidate_allocation_types(allocation, "allocation")

    norm_alloc: Dict[int, Fraction] = {}
    for p_idx, exact_payoff in typed_alloc:
        if p_idx < 0 or p_idx >= n:
            raise CooperativeGameValueError(
                f"Allocation player index {p_idx} out of range 0..{n - 1}."
            )
        if p_idx in norm_alloc:
            raise CooperativeGameValueError(
                f"Duplicate normalized player index {p_idx} in allocation."
            )
        norm_alloc[p_idx] = exact_payoff

    if len(norm_alloc) != n:
        raise CooperativeGameValueError(
            f"allocation must contain exactly {n} player entries (0..{n - 1}), "
            f"got {len(norm_alloc)}."
        )
    return norm_alloc


def build_marginal_contribution_ledger(
    n_players: int,
    characteristic_fn: CharacteristicFnInput,
    player_i: int,
) -> Tuple[MarginalContributionEntry, ...]:
    """
    Build a step-by-step ledger showing every coalition
    $S \\subseteq N \\setminus \\{i\\}$, player `player_i`'s exact marginal
    contribution $v(S \\cup \\{i\\}) - v(S)$, and the combinatorial Shapley
    weight $\\frac{|S|!(n - |S| - 1)!}{n!}$.
    """
    n = require_strict_int(n_players, "n_players")
    p_i = require_strict_int(player_i, "player_i")
    _prevalidate_characteristic_fn_types(
        characteristic_fn, "characteristic_fn"
    )
    norm_v = validate_cooperative_game(n, characteristic_fn)
    if p_i < 0 or p_i >= n:
        raise CooperativeGameValueError(
            f"player_i must be in 0..{n - 1}, got {p_i}."
        )

    factorials = [exact_factorial(k) for k in range(n + 1)]
    n_fact = factorials[n]
    others = [p for p in range(n) if p != p_i]
    singleton_i = frozenset((p_i,))
    entries: List[MarginalContributionEntry] = []

    for coalition_s in generate_powerset_coalitions(others):
        s_size = len(coalition_s)
        weight = Fraction(
            factorials[s_size] * factorials[n - s_size - 1],
            n_fact,
        )
        v_without = norm_v[coalition_s]
        v_with = norm_v[coalition_s | singleton_i]
        marginal = v_with - v_without
        entries.append(
            MarginalContributionEntry(
                player_i=p_i,
                coalition_s=coalition_s,
                value_without_i=v_without,
                value_with_i=v_with,
                marginal_contribution=marginal,
                combinatorial_weight=weight,
                weighted_contribution=weight * marginal,
            )
        )
    return tuple(entries)


def _compute_shapley_raw(
    n: int,
    norm_v: CharacteristicFnExact,
) -> Dict[int, Fraction]:
    """
    Internal exact Shapley evaluator over a validated game `(n, norm_v)`:
        phi_i(v) = sum_{S subseteq N \\ {i}}
                   [ |S|! * (n - |S| - 1)! / n! ] * (v(S U {i}) - v(S))
    """
    factorials = [exact_factorial(k) for k in range(n + 1)]
    n_fact = factorials[n]
    all_players = list(range(n))
    shapley: Dict[int, Fraction] = {}

    for player_i in all_players:
        others = [p for p in all_players if p != player_i]
        sub_coalitions = generate_powerset_coalitions(others)
        accum = Fraction(0, 1)
        singleton_i = frozenset((player_i,))

        for coalition_s in sub_coalitions:
            s_size = len(coalition_s)
            weight = Fraction(
                factorials[s_size] * factorials[n - s_size - 1],
                n_fact,
            )
            marginal = norm_v[coalition_s | singleton_i] - norm_v[coalition_s]
            accum += weight * marginal

        shapley[player_i] = accum

    return shapley


def _compute_harsanyi_dividends_raw(
    n: int,
    norm_v: CharacteristicFnExact,
) -> Dict[Coalition, Fraction]:
    """
    Compute the exact Harsanyi Unanimity Dividends `Delta_v(T)` for all subsets
    `T subseteq N` via Yates's Fast Boolean Mobius Transform (Sum-Over-Subsets
    DP) in exact O(n * 2^n) = O(N log N) time and O(2^n) space:
        Delta_v(T) = sum_{S subseteq T} (-1)^{|T| - |S|} v(S).
    """
    num_coalitions = 1 << n
    all_coalitions = generate_powerset_coalitions(range(n))
    dp: List[Fraction] = [norm_v[c] for c in all_coalitions]
    dp[0] = Fraction(0, 1)

    for bit in range(n):
        step = 1 << bit
        for mask in range(num_coalitions):
            if mask & step:
                dp[mask] -= dp[mask ^ step]

    return {all_coalitions[mask]: dp[mask] for mask in range(num_coalitions)}


def _fast_zeta_reconstruct_raw(
    n: int,
    dividends: Dict[Coalition, Fraction],
) -> Dict[Coalition, Fraction]:
    """
    Reconstruct characteristic function values `v(S) = sum_{emptyset != T subseteq S} Delta_v(T)`
    from Harsanyi dividends via the Fast Boolean Zeta Transform (SOS DP) in
    exact O(n * 2^n) = O(N log N) time and O(2^n) space.
    """
    num_coalitions = 1 << n
    all_coalitions = generate_powerset_coalitions(range(n))
    dp: List[Fraction] = [dividends[c] for c in all_coalitions]
    dp[0] = Fraction(0, 1)

    for bit in range(n):
        step = 1 << bit
        for mask in range(num_coalitions):
            if mask & step:
                dp[mask] += dp[mask ^ step]

    return {all_coalitions[mask]: dp[mask] for mask in range(num_coalitions)}


def compute_harsanyi_dividends(
    n_players: int,
    characteristic_fn: CharacteristicFnInput,
) -> Dict[Coalition, Fraction]:
    """
    Compute the exact Harsanyi Unanimity Dividends `Delta_v(T)` for every
    coalition `T subseteq N` and verify the inverse Fast Zeta Mobius
    reconstruction `v(S) == sum_{emptyset != T subseteq S} Delta_v(T)` in
    O(n * 2^n) = O(N log N) time.
    """
    norm_v = validate_cooperative_game(n_players, characteristic_fn)
    n = require_strict_int(n_players, "n_players")
    dividends = _compute_harsanyi_dividends_raw(n, norm_v)
    reconstructed = _fast_zeta_reconstruct_raw(n, dividends)
    if reconstructed != norm_v:
        raise ArithmeticError(
            "Fast Zeta Mobius inversion failed to reconstruct characteristic_fn."
        )
    return dividends


def compute_dual_game(
    n_players: int,
    characteristic_fn: CharacteristicFnInput,
) -> CharacteristicFnExact:
    """
    Compute the exact dual cooperative game `v*` defined by:
        v*(S) = v(N) - v(N \\ S)  for all S subseteq N.
    """
    norm_v = validate_cooperative_game(n_players, characteristic_fn)
    n = require_strict_int(n_players, "n_players")
    grand = frozenset(range(n))
    v_grand = norm_v[grand]
    return {s: v_grand - norm_v[grand - s] for s in norm_v}


def compute_weber_marginal_vectors(
    n_players: int,
    characteristic_fn: CharacteristicFnInput,
) -> List[Dict[int, Fraction]]:
    """
    Compute all `n!` Weber marginal worth vectors `m^pi(v)` across every
    player permutation `pi in S_n`.
    """
    norm_v = validate_cooperative_game(n_players, characteristic_fn)
    n = require_strict_int(n_players, "n_players")
    permutations = generate_permutations_exact(range(n))
    marginal_vectors: List[Dict[int, Fraction]] = []

    for perm in permutations:
        predecessors: Coalition = frozenset()
        prev_worth = Fraction(0, 1)
        vec: Dict[int, Fraction] = {}
        for player_i in perm:
            next_coalition = predecessors | frozenset((player_i,))
            next_worth = norm_v[next_coalition]
            vec[player_i] = next_worth - prev_worth
            predecessors = next_coalition
            prev_worth = next_worth
        marginal_vectors.append(vec)

    return marginal_vectors


def verify_weber_marginal_worth_theorem(
    n_players: int,
    characteristic_fn: CharacteristicFnInput,
) -> Dict[str, object]:
    """
    Verify the Shapley-Weber-Ichiishi Theorem across all `n!` player
    permutations:
      1. The arithmetic mean of the `n!` marginal worth vectors `m^pi` equals
         the exact Shapley value `phi(v)`.
      2. Every marginal worth vector `m^pi` lies inside the Core `C(v)` if and
         only if the game `(N, v)` is convex (supermodular).
    """
    norm_v = validate_cooperative_game(n_players, characteristic_fn)
    n = require_strict_int(n_players, "n_players")
    vectors = compute_weber_marginal_vectors(n, norm_v)
    num_perms = Fraction(len(vectors), 1)
    all_coalitions = generate_powerset_coalitions(range(n))

    all_vertices_in_core = True
    for vec in vectors:
        for s in all_coalitions:
            if sum((vec[i] for i in s), Fraction(0, 1)) < norm_v[s]:
                all_vertices_in_core = False
                break
        if not all_vertices_in_core:
            break

    barycenter = {
        i: sum((vec[i] for vec in vectors), Fraction(0, 1)) / num_perms
        for i in range(n)
    }
    shapley = _compute_shapley_raw(n, norm_v)
    props = verify_cooperative_game_properties(n, norm_v, shapley)

    return {
        "permutation_count": len(vectors),
        "barycenter_matches_shapley": (barycenter == shapley),
        "all_weber_vertices_in_core": all_vertices_in_core,
        "weber_core_iff_convex_verified": (
            all_vertices_in_core == props["is_convex"]
        ),
    }


def verify_bondareva_shapley_balanced_bound(
    n_players: int,
    characteristic_fn: CharacteristicFnInput,
) -> Dict[str, object]:
    """
    Verify the Bondareva-Shapley Balanced Collection Theorem (Bondareva, 1963;
    Shapley, 1967) across canonical balanced coalition families:
      1. Singleton partition: lambda_{i} = 1 for all i in N.
      2. Complementary 2-partitions: lambda_S = 1, lambda_{N \\ S} = 1.
      3. Uniform k-coalition families: lambda_S = 1 / C(n - 1, k - 1).
      4. Asymmetric 3-partitions {A, B, C} (weights 1, 1, 1) and dual 2-of-3
         triangle balanced families {A U B, B U C, A U C} (weights 1/2).
    """
    norm_v = validate_cooperative_game(n_players, characteristic_fn)
    n = require_strict_int(n_players, "n_players")
    grand = frozenset(range(n))
    v_grand = norm_v[grand]
    all_coalitions = generate_powerset_coalitions(range(n))

    max_balanced_worth = v_grand
    violating_family_found = False

    # 1. Singleton partition
    singleton_worth = sum(
        (norm_v[frozenset((i,))] for i in range(n)), Fraction(0, 1)
    )
    if singleton_worth > max_balanced_worth:
        max_balanced_worth = singleton_worth
    if singleton_worth > v_grand:
        violating_family_found = True

    # 2. Complementary pairs {S, N \ S}
    for s in all_coalitions:
        if 0 < len(s) < n:
            comp_worth = norm_v[s] + norm_v[grand - s]
            if comp_worth > max_balanced_worth:
                max_balanced_worth = comp_worth
            if comp_worth > v_grand:
                violating_family_found = True

    # 3. Uniform k-subset families for 1 <= k <= n - 1
    for k in range(1, n):
        weight = Fraction(1, exact_binomial(n - 1, k - 1))
        k_worth = sum(
            (weight * norm_v[s] for s in all_coalitions if len(s) == k),
            Fraction(0, 1),
        )
        if k_worth > max_balanced_worth:
            max_balanced_worth = k_worth
        if k_worth > v_grand:
            violating_family_found = True

    # 4. Asymmetric 3-partitions {A, B, C} and dual 2-of-3 triangle families
    half = Fraction(1, 2)
    for a_set in all_coalitions:
        if not a_set or len(a_set) > n - 2:
            continue
        rem_bc = grand - a_set
        for b_set in generate_powerset_coalitions(sorted(rem_bc)):
            if not b_set or b_set == rem_bc:
                continue
            c_set = rem_bc - b_set
            part3_worth = norm_v[a_set] + norm_v[b_set] + norm_v[c_set]
            if part3_worth > max_balanced_worth:
                max_balanced_worth = part3_worth
            if part3_worth > v_grand:
                violating_family_found = True

            tri_worth = half * (
                norm_v[a_set | b_set]
                + norm_v[b_set | c_set]
                + norm_v[a_set | c_set]
            )
            if tri_worth > max_balanced_worth:
                max_balanced_worth = tri_worth
            if tri_worth > v_grand:
                violating_family_found = True

    return {
        "grand_coalition_worth": v_grand,
        "max_canonical_balanced_worth": max_balanced_worth,
        "canonical_balanced_inequality_satisfied": (not violating_family_found),
    }


def verify_shapley_axioms(
    n_players: int,
    characteristic_fn: CharacteristicFnInput,
    shapley_values: Optional[Dict[int, RationalInput]] = None,
    additive_partner_fn: Optional[CharacteristicFnInput] = None,
) -> ShapleyAxiomVerificationReport:
    """
    Verify all four canonical Shapley axioms plus Young's Strong Monotonicity,
    O(n * 2^n) Fast Mobius/Zeta Harsanyi dividend duality, and Dual Game
    Self-Duality in exact rational arithmetic. Enforces Universal Type-First
    Precedence across all four parameters.
    """
    require_strict_int(n_players, "n_players")
    _prevalidate_characteristic_fn_types(
        characteristic_fn, "characteristic_fn"
    )
    if shapley_values is not None:
        _prevalidate_allocation_types(shapley_values, "shapley_values")
    if additive_partner_fn is not None:
        _prevalidate_characteristic_fn_types(
            additive_partner_fn, "additive_partner_fn"
        )

    norm_v = validate_cooperative_game(n_players, characteristic_fn)
    n = require_strict_int(n_players, "n_players")
    phi_v = (
        _compute_shapley_raw(n, norm_v)
        if shapley_values is None
        else _validate_allocation_vector(n, shapley_values)
    )
    if additive_partner_fn is not None:
        norm_w = validate_cooperative_game(n, additive_partner_fn)
    else:
        all_coalitions = generate_powerset_coalitions(range(n))
        norm_w = {}
        active_limit = max(1, n - 1)
        for c in all_coalitions:
            if not c:
                norm_w[c] = Fraction(0, 1)
            else:
                active_sum = sum(
                    (3 if idx in (0, 1) else idx + 2)
                    for idx in c
                    if idx < active_limit
                )
                norm_w[c] = Fraction(active_sum * active_sum, 2)

    grand_coalition = frozenset(range(n))
    grand_value = norm_v[grand_coalition]
    shapley_total = sum(phi_v.values(), Fraction(0, 1))
    efficiency_ok = shapley_total == grand_value

    # 2. Symmetry Axiom & Intra-Game Marginal Dominance (Desirability) Check on v
    symmetric_pairs: List[Tuple[int, int]] = []
    symmetry_ok = True
    monotonicity_ok = True
    for i in range(n):
        for j in range(i + 1, n):
            others_ij = [p for p in range(n) if p != i and p != j]
            sub_coalitions = generate_powerset_coalitions(others_ij)
            si = frozenset((i,))
            sj = frozenset((j,))
            if all(norm_v[s | si] == norm_v[s | sj] for s in sub_coalitions):
                symmetric_pairs.append((i, j))
                if phi_v[i] != phi_v[j]:
                    symmetry_ok = False
            if all(norm_v[s | si] >= norm_v[s | sj] for s in sub_coalitions):
                if phi_v[i] < phi_v[j]:
                    monotonicity_ok = False
            if all(norm_v[s | sj] >= norm_v[s | si] for s in sub_coalitions):
                if phi_v[j] < phi_v[i]:
                    monotonicity_ok = False

    # 3. Dummy / Null Player Axiom Check on v
    dummy_players: List[int] = []
    dummy_ok = True
    for i in range(n):
        others_i = [p for p in range(n) if p != i]
        sub_coalitions = generate_powerset_coalitions(others_i)
        si = frozenset((i,))
        if all(norm_v[s | si] == norm_v[s] for s in sub_coalitions):
            dummy_players.append(i)
            if phi_v[i] != Fraction(0, 1):
                dummy_ok = False

    # 4. Additivity & Young's Inter-Game Strong Monotonicity Check
    norm_v_plus_w: CharacteristicFnExact = {
        c: norm_v[c] + norm_w[c] for c in norm_v
    }
    phi_w = _compute_shapley_raw(n, norm_w)
    phi_v_plus_w = _compute_shapley_raw(n, norm_v_plus_w)
    additivity_ok = all(
        phi_v_plus_w[i] == phi_v[i] + phi_w[i] for i in range(n)
    )

    if n >= 2 and additive_partner_fn is None:
        if phi_w[n - 1] != Fraction(0, 1):
            dummy_ok = False
    if n >= 3 and additive_partner_fn is None:
        if phi_w[0] != phi_w[1]:
            symmetry_ok = False

    for i in range(n):
        others_i = [p for p in range(n) if p != i]
        sub_coalitions = generate_powerset_coalitions(others_i)
        si = frozenset((i,))
        marginals_dominate = all(
            (norm_v_plus_w[s | si] - norm_v_plus_w[s])
            >= (norm_v[s | si] - norm_v[s])
            for s in sub_coalitions
        )
        if marginals_dominate and phi_v_plus_w[i] < phi_v[i]:
            monotonicity_ok = False

    # 6. Harsanyi Dividend (Fast Boolean Mobius / Zeta) Duality Check in O(n * 2^n)
    dividends = _compute_harsanyi_dividends_raw(n, norm_v)
    reconstructed_v = _fast_zeta_reconstruct_raw(n, dividends)
    harsanyi_ok = reconstructed_v == norm_v
    for i in range(n):
        phi_i_from_dividends = sum(
            (
                dividends[t] / Fraction(len(t), 1)
                for t in dividends
                if i in t
            ),
            Fraction(0, 1),
        )
        if phi_i_from_dividends != phi_v[i]:
            harsanyi_ok = False
            break

    # 7. Dual Game Self-Duality Check: phi(v*) == phi(v)
    dual_v = {
        s: grand_value - norm_v[grand_coalition - s] for s in norm_v
    }
    phi_dual = _compute_shapley_raw(n, dual_v)
    self_duality_ok = all(phi_dual[i] == phi_v[i] for i in range(n))

    return ShapleyAxiomVerificationReport(
        efficiency_verified=efficiency_ok,
        symmetry_verified=symmetry_ok,
        dummy_player_verified=dummy_ok,
        additivity_verified=additivity_ok,
        strong_monotonicity_verified=monotonicity_ok,
        harsanyi_duality_verified=harsanyi_ok,
        self_duality_verified=self_duality_ok,
        symmetric_pairs_found=tuple(symmetric_pairs),
        dummy_players_found=tuple(dummy_players),
        grand_coalition_value=grand_value,
        shapley_sum=shapley_total,
        shapley_values=phi_v,
    )


def compute_exact_shapley_values(
    n_players: int,
    characteristic_fn: dict[frozenset[int], Fraction | int],
) -> dict[int, Fraction]:
    """
    Compute the exact rational Shapley value `phi_i(v)` for every player
    `i in 0 .. n_players - 1` (`1 <= n_players <= 6`) and verify all four
    Shapley axioms (Efficiency, Symmetry, Dummy/Null Player, and Additivity)
    plus Young's Strong Monotonicity, Harsanyi dividend duality, and
    Self-Duality in exact arithmetic.
    """
    norm_v = validate_cooperative_game(n_players, characteristic_fn)
    n = require_strict_int(n_players, "n_players")
    shapley = _compute_shapley_raw(n, norm_v)

    report = verify_shapley_axioms(n, norm_v, shapley_values=shapley)
    if not report.all_axioms_verified:
        raise ArithmeticError(
            f"Shapley axiom verification failed: {report!r}"
        )
    return shapley


def compute_exact_banzhaf_values(
    n_players: int,
    characteristic_fn: CharacteristicFnInput,
) -> Dict[int, Fraction]:
    """
    Compute the exact rational Penrose-Banzhaf power index for every player:
        beta_i(v) = (1 / 2^{n-1}) * sum_{S subseteq N \\ {i}} (v(S U {i}) - v(S)).
    """
    norm_v = validate_cooperative_game(n_players, characteristic_fn)
    n = require_strict_int(n_players, "n_players")
    denom = Fraction(1 << (n - 1), 1)
    all_players = list(range(n))
    banzhaf: Dict[int, Fraction] = {}

    for player_i in all_players:
        others = [p for p in all_players if p != player_i]
        singleton_i = frozenset((player_i,))
        total_marginal = sum(
            (
                norm_v[s | singleton_i] - norm_v[s]
                for s in generate_powerset_coalitions(others)
            ),
            Fraction(0, 1),
        )
        banzhaf[player_i] = total_marginal / denom

    return banzhaf


def compute_cooperative_game_diagnostics(
    n_players: int,
    characteristic_fn: CharacteristicFnInput,
    allocation: Dict[int, RationalInput],
) -> CooperativeGameDiagnostics:
    """
    Compute complete structural predicates (`is_superadditive` via O(3^n)
    disjoint bitmask submasks, `is_convex` via Lovasz's O(n^2 * 2^{n-2}) local
    2nd differences, `is_in_core`, `is_totally_positive`), coalitional
    surpluses, blocking coalitions, Banzhaf values, and Harsanyi dividends in
    exact rational arithmetic. Enforces Universal Type-First Precedence.
    """
    require_strict_int(n_players, "n_players")
    _prevalidate_characteristic_fn_types(
        characteristic_fn, "characteristic_fn"
    )
    _prevalidate_allocation_types(allocation, "allocation")

    norm_v = validate_cooperative_game(n_players, characteristic_fn)
    n = require_strict_int(n_players, "n_players")
    norm_alloc = _validate_allocation_vector(n, allocation)
    all_coalitions = generate_powerset_coalitions(range(n))

    num_c = 1 << n
    v_arr: List[Fraction] = [norm_v[all_coalitions[m]] for m in range(num_c)]
    full_mask = num_c - 1

    # 1. Superadditivity via exact O(3^n) disjoint bitmask submask traversal
    is_superadditive = True
    for s_mask in range(1, num_c):
        v_s = v_arr[s_mask]
        comp = full_mask ^ s_mask
        t_mask = comp
        while t_mask > s_mask:
            if v_arr[s_mask | t_mask] < v_s + v_arr[t_mask]:
                is_superadditive = False
                break
            t_mask = (t_mask - 1) & comp
        if not is_superadditive:
            break

    # 2. Convexity (supermodularity) via Lovasz's O(n^2 * 2^{n-2}) local 2nd differences
    is_convex = True
    for i in range(n):
        bit_i = 1 << i
        for j in range(i + 1, n):
            bit_j = 1 << j
            bit_ij = bit_i | bit_j
            for s_mask in range(num_c):
                if not (s_mask & bit_ij):
                    if (
                        v_arr[s_mask | bit_ij] + v_arr[s_mask]
                        < v_arr[s_mask | bit_i] + v_arr[s_mask | bit_j]
                    ):
                        is_convex = False
                        break
            if not is_convex:
                break
        if not is_convex:
            break

    grand_coalition = frozenset(range(n))
    total_allocated = sum(norm_alloc.values(), Fraction(0, 1))
    efficiency_gap = total_allocated - norm_v[grand_coalition]
    is_efficient = efficiency_gap == Fraction(0, 1)

    blocking: List[Coalition] = []
    min_surplus: Optional[Fraction] = None

    for s in all_coalitions:
        coalition_payoff = sum((norm_alloc[i] for i in s), Fraction(0, 1))
        surplus = coalition_payoff - norm_v[s]
        if s and (min_surplus is None or surplus < min_surplus):
            min_surplus = surplus
        if surplus < Fraction(0, 1):
            blocking.append(s)

    is_in_core = is_efficient and (len(blocking) == 0)
    banzhaf = compute_exact_banzhaf_values(n, norm_v)
    dividends = _compute_harsanyi_dividends_raw(n, norm_v)
    is_totally_positive = all(
        dividends[s] >= Fraction(0, 1) for s in all_coalitions if s
    )

    return CooperativeGameDiagnostics(
        is_superadditive=is_superadditive,
        is_convex=is_convex,
        is_in_core=is_in_core,
        is_totally_positive=is_totally_positive,
        efficiency_gap=efficiency_gap,
        min_coalitional_surplus=(
            min_surplus if min_surplus is not None else Fraction(0, 1)
        ),
        blocking_coalitions=tuple(blocking),
        banzhaf_values=banzhaf,
        harsanyi_dividends=dividends,
    )


def verify_cooperative_game_properties(
    n_players: int,
    characteristic_fn: dict[frozenset[int], Fraction | int],
    allocation: dict[int, Fraction | int],
) -> dict[str, bool]:
    """
    Return exact booleans for:
      - `is_superadditive`: v(S U T) >= v(S) + v(T) for all disjoint S, T subseteq N.
      - `is_convex` (supermodular): v(S U T) + v(S cap T) >= v(S) + v(T)
        for all S, T subseteq N.
      - `is_in_core`: efficiency sum_{i in N} x_i == v(N) AND coalitional
        rationality sum_{i in S} x_i >= v(S) for every coalition S subseteq N.
    """
    diag = compute_cooperative_game_diagnostics(
        n_players=n_players,
        characteristic_fn=characteristic_fn,
        allocation=allocation,
    )
    return {
        "is_superadditive": diag.is_superadditive,
        "is_convex": diag.is_convex,
        "is_in_core": diag.is_in_core,
    }


@dataclass(frozen=True)
class ByzantineConsensusCertificate:
    """
    Transparent audit record of a Byzantine-resilient rational consensus step.
    """

    total_reports_n: int
    max_byzantine_faults_f: int
    retained_count_m: int
    sorted_reports: Tuple[Fraction, ...]
    trimmed_lower: Tuple[Fraction, ...]
    retained_interior: Tuple[Fraction, ...]
    trimmed_upper: Tuple[Fraction, ...]
    trimmed_mean: Fraction
    exact_median: Fraction
    spread_after_trim: Fraction


def compute_byzantine_consensus_certificate(
    reports: list[Fraction | int],
    max_byzantine_faults: int,
) -> ByzantineConsensusCertificate:
    """
    Compute the full `ByzantineConsensusCertificate` for `n` oracle reports
    tolerating up to `f = max_byzantine_faults` arbitrary Byzantine outliers.
    Enforces Universal Type-First Precedence (Invariant T1).
    """
    f = require_strict_int(max_byzantine_faults, "max_byzantine_faults")
    if isinstance(reports, (bool, float)) or not isinstance(reports, list):
        raise RationalCovenantTypeError(
            f"reports must be a list of Fraction | int, got "
            f"{type(reports).__name__}."
        )

    exact_reports = [
        require_exact_rational(r, f"reports[{idx}]")
        for idx, r in enumerate(reports)
    ]

    if f < 0:
        raise ByzantineQuorumValueError(
            f"max_byzantine_faults must be >= 0, got {f}."
        )
    n = len(exact_reports)
    min_required = 3 * f + 1
    if n < min_required:
        raise ByzantineQuorumValueError(
            f"Byzantine consensus requires strictly n >= 3f + 1 ({min_required}) "
            f"oracle reports for f = {f}, got n = {n}."
        )

    sorted_reports = sorted(exact_reports)
    trimmed_low = sorted_reports[:f]
    trimmed = sorted_reports[f : n - f]
    trimmed_high = sorted_reports[n - f :]
    m = len(trimmed)

    trimmed_mean = sum(trimmed, Fraction(0, 1)) / Fraction(m, 1)
    mid = m // 2
    if m % 2 == 1:
        exact_median = trimmed[mid]
    else:
        exact_median = (trimmed[mid - 1] + trimmed[mid]) / Fraction(2, 1)

    spread_after_trim = trimmed[-1] - trimmed[0]

    return ByzantineConsensusCertificate(
        total_reports_n=n,
        max_byzantine_faults_f=f,
        retained_count_m=m,
        sorted_reports=tuple(sorted_reports),
        trimmed_lower=tuple(trimmed_low),
        retained_interior=tuple(trimmed),
        trimmed_upper=tuple(trimmed_high),
        trimmed_mean=trimmed_mean,
        exact_median=exact_median,
        spread_after_trim=spread_after_trim,
    )


def byzantine_rational_consensus(
    reports: list[Fraction | int],
    max_byzantine_faults: int,
) -> dict[str, Fraction]:
    """
    Compute exact Byzantine-resilient rational consensus over `n` oracle reports
    tolerating up to `f = max_byzantine_faults` arbitrary Byzantine outliers.
    """
    cert = compute_byzantine_consensus_certificate(
        reports=reports,
        max_byzantine_faults=max_byzantine_faults,
    )
    return {
        "trimmed_mean": cert.trimmed_mean,
        "exact_median": cert.exact_median,
        "spread_after_trim": cert.spread_after_trim,
    }


def build_persephone_demeter_convex_game() -> CharacteristicFnExact:
    """
    Construct the canonical 4-player Persephone-Demeter seasonal harvest convex
    cooperative game:
        v(S) = (sum_{i in S} w_i)^2 + 2 * |S| * (|S| - 1),  v(emptyset) = 0
    with weights (3, 3, 5, 7).
    """
    weights = (3, 3, 5, 7)
    game: CharacteristicFnExact = {}
    for c in generate_powerset_coalitions(range(4)):
        if not c:
            game[c] = Fraction(0, 1)
        else:
            w_sum = sum(weights[i] for i in c)
            k = len(c)
            game[c] = Fraction(w_sum * w_sum + 2 * k * (k - 1), 1)
    return game


def build_dummy_witness_convex_game() -> CharacteristicFnExact:
    """
    Construct a 4-player convex cooperative game where Players 0 and 1 are
    symmetric (weight 4 each), Player 2 has weight 6, and Player 3 is an
    explicit Dummy/Null Witness (weight 0).
    """
    weights = (4, 4, 6, 0)
    game: CharacteristicFnExact = {}
    for c in generate_powerset_coalitions(range(4)):
        w_sum = sum(weights[i] for i in c)
        game[c] = Fraction(w_sum * w_sum, 1)
    return game


def build_six_player_eleusinian_sanctuary_game() -> CharacteristicFnExact:
    """
    Construct a 6-player convex cooperative game (`n_players = 6`, `2^6 = 64`
    coalitions) with symmetric guardians (Players 0 and 1) and a Dummy Player
    (Player 5, weight 0).
    """
    weights = (2, 2, 3, 4, 5, 0)
    game: CharacteristicFnExact = {}
    for c in generate_powerset_coalitions(range(6)):
        w_sum = sum(weights[i] for i in c)
        game[c] = Fraction(w_sum * w_sum, 1)
    return game


def build_non_superadditive_empty_core_game() -> CharacteristicFnExact:
    """
    Construct a 3-player cyclical interference game that violates
    superadditivity and has a provably empty Core:
      v(emptyset) = 0, v({i}) = 5, v({i, j}) = 6, v({0, 1, 2}) = 12.
    """
    game: CharacteristicFnExact = {}
    for c in generate_powerset_coalitions(range(3)):
        k = len(c)
        if k == 0:
            game[c] = Fraction(0, 1)
        elif k == 1:
            game[c] = Fraction(5, 1)
        elif k == 2:
            game[c] = Fraction(6, 1)
        else:
            game[c] = Fraction(12, 1)
    return game


def build_superadditive_non_convex_game() -> CharacteristicFnExact:
    """
    Construct a 3-player game that IS superadditive and HAS a non-empty Core,
    but is NOT convex (supermodular), strictly separating `is_superadditive`
    from `is_convex`.
    """
    return {
        frozenset(): Fraction(0, 1),
        frozenset((0,)): Fraction(0, 1),
        frozenset((1,)): Fraction(0, 1),
        frozenset((2,)): Fraction(0, 1),
        frozenset((0, 1)): Fraction(2, 1),
        frozenset((1, 2)): Fraction(2, 1),
        frozenset((0, 2)): Fraction(0, 1),
        frozenset((0, 1, 2)): Fraction(3, 1),
    }


# ==============================================================================
# SECTION 3: PILLAR II — SHORT WEIERSTRASS ELLIPTIC CURVE OVER F_65537,
#            RFC 6979, RFC 6962 & ZERO-KNOWLEDGE SCHNORR / PEDERSEN PROOFS
# ==============================================================================


@dataclass(frozen=True)
class SchnorrProofEnvelope:
    """
    Immutable envelope for a Fiat-Shamir non-interactive Schnorr ZK proof
    `(R, e, s)` over `E(F_65537)`.
    """

    public_key: Tuple[int, int]
    commitment_r: Tuple[int, int]
    challenge_e: int
    response_s: int
    message_sha256_hex: str

    def to_proof_tuple(self) -> SchnorrProof:
        """Return the canonical `(R, e, s)` 3-tuple."""
        return (self.commitment_r, self.challenge_e, self.response_s)


def _encode_scalar_ct(scalar: int) -> bytes:
    """Encode an integer scalar canonically reduced modulo CURVE_Q into [0, q) as 4-byte big-endian bytes."""
    return (scalar % CURVE_Q).to_bytes(4, byteorder="big")


def _encode_point_ct(pt: ECPoint) -> bytes:
    """
    Canonical 9-byte constant-length encoding of a point on E(F_65537) U {O}:
      - Point at infinity None -> 0x00 || 0x00000000 || 0x00000000
      - Affine point (x, y)    -> 0x01 || x (4B BE)  || y (4B BE)
    """
    if pt is None:
        return b"\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    return (
        b"\x01"
        + (pt[0] % CURVE_P).to_bytes(4, byteorder="big")
        + (pt[1] % CURVE_P).to_bytes(4, byteorder="big")
    )


def _ct_equal_scalars(a: int, b: int) -> bool:
    """Constant-time equality check for scalars in Z_q via hmac.compare_digest."""
    return hmac.compare_digest(_encode_scalar_ct(a), _encode_scalar_ct(b))


def _ct_equal_points(pt_a: ECPoint, pt_b: ECPoint) -> bool:
    """Constant-time equality check for curve points via hmac.compare_digest."""
    return hmac.compare_digest(_encode_point_ct(pt_a), _encode_point_ct(pt_b))


def _validate_point_structure(point: object, name: str = "P") -> ECPoint:
    """
    Validate that `point` is either `None` (point at infinity O) or a 2-tuple
    of strict integers `(x, y)` (rejecting `bool` and `float` with `TypeError`).
    """
    if point is None:
        return None
    if isinstance(point, (bool, float)) or not isinstance(point, tuple):
        raise RationalCovenantTypeError(
            f"Elliptic curve point '{name}' must be None (point at infinity O) "
            f"or a 2-tuple of strict ints (x, y), got {type(point).__name__}."
        )
    if len(point) != 2:
        raise RationalCovenantTypeError(
            f"Elliptic curve point '{name}' must be a 2-tuple (x, y) of length "
            f"2, got length {len(point)}."
        )
    x = require_strict_int(point[0], f"{name}[0]")
    y = require_strict_int(point[1], f"{name}[1]")
    return (x, y)


def is_on_curve(P: tuple[int, int] | None) -> bool:
    """
    Return `True` iff `P` is `None` (point at infinity O) or lies on the Short
    Weierstrass curve `E(F_65537): y^2 === x^3 + 5x + 12 (mod 65537)` with
    canonical field coordinates `0 <= x < 65537` and `0 <= y < 65537`.
    """
    pt = _validate_point_structure(P, "P")
    if pt is None:
        return True
    x, y = pt
    if x < 0 or x >= CURVE_P or y < 0 or y >= CURVE_P:
        return False
    lhs = (y * y) % CURVE_P
    rhs = (x * x * x + CURVE_A * x + CURVE_B) % CURVE_P
    return lhs == rhs


def _require_valid_curve_point(
    P: tuple[int, int] | None, name: str = "P"
) -> ECPoint:
    """Validate structure and curve membership of `P` on E(F_65537)."""
    pt = _validate_point_structure(P, name)
    if not is_on_curve(pt):
        raise EllipticCurveValueError(
            f"Point {name}={pt!r} does not lie on E(F_{CURVE_P})."
        )
    return pt


def ec_negate(P: tuple[int, int] | None) -> tuple[int, int] | None:
    """Compute the additive inverse `-P` on `E(F_65537)`."""
    pt = _require_valid_curve_point(P, "P")
    if pt is None:
        return None
    x, y = pt
    return (x, (-y) % CURVE_P)


def ec_double(P: tuple[int, int] | None) -> tuple[int, int] | None:
    """
    Double a point `P` on `E(F_65537)` (`2 * P`) using only integer modular
    inversion `pow((2 * y) % p, -1, p)`.
    """
    pt = _require_valid_curve_point(P, "P")
    if pt is None:
        return None
    x1, y1 = pt
    if y1 == 0:
        return None

    numerator = (3 * x1 * x1 + CURVE_A) % CURVE_P
    inv_denom = pow((2 * y1) % CURVE_P, -1, CURVE_P)
    slope = (numerator * inv_denom) % CURVE_P

    x3 = (slope * slope - 2 * x1) % CURVE_P
    y3 = (slope * (x1 - x3) - y1) % CURVE_P
    return (x3, y3)


def ec_add(
    P: tuple[int, int] | None,
    Q: tuple[int, int] | None,
) -> tuple[int, int] | None:
    """
    Add two points `P` and `Q` on `E(F_65537)` (`P + Q`) using only integer
    modular inversion `pow((x_2 - x_1) % p, -1, p)`.
    """
    pt_p = _validate_point_structure(P, "P")
    pt_q = _validate_point_structure(Q, "Q")
    if not is_on_curve(pt_p):
        raise EllipticCurveValueError(
            f"Point P={pt_p!r} is not on E(F_{CURVE_P})."
        )
    if not is_on_curve(pt_q):
        raise EllipticCurveValueError(
            f"Point Q={pt_q!r} is not on E(F_{CURVE_P})."
        )

    if pt_p is None:
        return pt_q
    if pt_q is None:
        return pt_p

    x1, y1 = pt_p
    x2, y2 = pt_q

    if x1 == x2:
        if (y1 + y2) % CURVE_P == 0:
            return None
        return ec_double(pt_p)

    numerator = (y2 - y1) % CURVE_P
    inv_denom = pow((x2 - x1) % CURVE_P, -1, CURVE_P)
    slope = (numerator * inv_denom) % CURVE_P

    x3 = (slope * slope - x1 - x2) % CURVE_P
    y3 = (slope * (x1 - x3) - y1) % CURVE_P
    return (x3, y3)


def ec_scalar_mul(
    k: int,
    P: tuple[int, int] | None,
) -> tuple[int, int] | None:
    """
    Compute scalar multiplication `k * P` on `E(F_65537)` via binary
    double-and-add with zero floating-point operations.
    """
    scalar = require_strict_int(k, "k")
    pt = _require_valid_curve_point(P, "P")

    if pt is None or scalar == 0:
        return None
    if scalar < 0:
        pt = ec_negate(pt)
        scalar = -scalar

    result: ECPoint = None
    addend: ECPoint = pt
    while scalar > 0:
        if scalar & 1:
            result = ec_add(result, addend)
        addend = ec_double(addend)
        scalar >>= 1

    return result


def _affine_to_jacobian(P: ECPoint) -> JacobianPoint:
    """Lift an affine point `P` on `E(F_p)` into Jacobian coordinates `(X:Y:Z)`."""
    if P is None:
        return (1, 1, 0)
    return (P[0], P[1], 1)


def _jacobian_to_affine(J: JacobianPoint) -> ECPoint:
    """Project Jacobian coordinates `(X:Y:Z)` to affine `(X/Z^2, Y/Z^3) mod p`."""
    X, Y, Z = J
    if Z % CURVE_P == 0:
        return None
    z_inv = pow(Z % CURVE_P, -1, CURVE_P)
    z_inv2 = (z_inv * z_inv) % CURVE_P
    z_inv3 = (z_inv2 * z_inv) % CURVE_P
    return ((X * z_inv2) % CURVE_P, (Y * z_inv3) % CURVE_P)


def _jacobian_double(J: JacobianPoint) -> JacobianPoint:
    """Inversion-free point doubling in Jacobian projective coordinates `(X:Y:Z)`."""
    X1, Y1, Z1 = J
    if Z1 == 0 or Y1 == 0:
        return (1, 1, 0)
    Y1_sq = (Y1 * Y1) % CURVE_P
    S = (4 * X1 * Y1_sq) % CURVE_P
    Z1_sq = (Z1 * Z1) % CURVE_P
    Z1_4 = (Z1_sq * Z1_sq) % CURVE_P
    M = (3 * X1 * X1 + CURVE_A * Z1_4) % CURVE_P
    X3 = (M * M - 2 * S) % CURVE_P
    Y3 = (M * (S - X3) - 8 * Y1_sq * Y1_sq) % CURVE_P
    Z3 = (2 * Y1 * Z1) % CURVE_P
    return (X3, Y3, Z3)


def _jacobian_add(J1: JacobianPoint, J2: JacobianPoint) -> JacobianPoint:
    """Inversion-free point addition in Jacobian projective coordinates `(X:Y:Z)`."""
    X1, Y1, Z1 = J1
    X2, Y2, Z2 = J2
    if Z1 == 0:
        return J2
    if Z2 == 0:
        return J1
    Z1_sq = (Z1 * Z1) % CURVE_P
    Z2_sq = (Z2 * Z2) % CURVE_P
    U1 = (X1 * Z2_sq) % CURVE_P
    U2 = (X2 * Z1_sq) % CURVE_P
    S1 = (Y1 * Z2_sq * Z2) % CURVE_P
    S2 = (Y2 * Z1_sq * Z1) % CURVE_P
    if U1 == U2:
        if S1 != S2:
            return (1, 1, 0)
        return _jacobian_double(J1)
    H = (U2 - U1) % CURVE_P
    R = (S2 - S1) % CURVE_P
    H_sq = (H * H) % CURVE_P
    H_cu = (H_sq * H) % CURVE_P
    U1_H_sq = (U1 * H_sq) % CURVE_P
    X3 = (R * R - H_cu - 2 * U1_H_sq) % CURVE_P
    Y3 = (R * (U1_H_sq - X3) - S1 * H_cu) % CURVE_P
    Z3 = (H * Z1 * Z2) % CURVE_P
    return (X3, Y3, Z3)


def ec_scalar_mul_jacobian(
    k: int,
    P: tuple[int, int] | None,
) -> tuple[int, int] | None:
    """
    Compute `k * P` via inversion-free Jacobian projective double-and-add
    followed by a single modular inversion `pow(Z, -1, p)` at projection.
    """
    scalar = require_strict_int(k, "k")
    pt = _require_valid_curve_point(P, "P")
    if pt is None or scalar == 0:
        return None
    if scalar < 0:
        pt = ec_negate(pt)
        scalar = -scalar

    result: JacobianPoint = (1, 1, 0)
    addend: JacobianPoint = _affine_to_jacobian(pt)
    while scalar > 0:
        if scalar & 1:
            result = _jacobian_add(result, addend)
        addend = _jacobian_double(addend)
        scalar >>= 1
    return _jacobian_to_affine(result)


def verify_curve_and_generators() -> Dict[str, bool]:
    """
    Verify all algebraic invariants of Rule 14 Ring I curve E(F_65537).
    """
    discriminant = (4 * (CURVE_A ** 3) + 27 * (CURVE_B ** 2)) % CURVE_P
    hasse_diff = abs(CURVE_Q - (CURVE_P + 1))
    euler_exp = (CURVE_P - 1) // 2
    g_rhs = (GENERATOR_G[0] ** 3 + CURVE_A * GENERATOR_G[0] + CURVE_B) % CURVE_P
    h_rhs = (GENERATOR_H[0] ** 3 + CURVE_A * GENERATOR_H[0] + CURVE_B) % CURVE_P
    return {
        "p_is_prime": is_prime_exact(CURVE_P),
        "q_is_prime": is_prime_exact(CURVE_Q),
        "hasse_bound_satisfied": (hasse_diff * hasse_diff) <= (4 * CURVE_P),
        "non_singular": discriminant != 0,
        "euler_quadratic_residue_g_h": (
            pow(g_rhs, euler_exp, CURVE_P) == 1
            and pow(h_rhs, euler_exp, CURVE_P) == 1
        ),
        "g_on_curve": is_on_curve(GENERATOR_G),
        "h_on_curve": is_on_curve(GENERATOR_H),
        "g_prime_order_q": ec_scalar_mul(CURVE_Q, GENERATOR_G) is None,
        "h_prime_order_q": ec_scalar_mul(CURVE_Q, GENERATOR_H) is None,
        "jacobian_matches_affine": (
            ec_scalar_mul_jacobian(CURVE_Q, GENERATOR_G) is None
            and ec_scalar_mul_jacobian(12345, GENERATOR_G)
            == ec_scalar_mul(12345, GENERATOR_G)
        ),
        "generators_independent": (
            GENERATOR_G != GENERATOR_H
            and GENERATOR_G != ec_negate(GENERATOR_H)
        ),
    }


def _rfc6979_bits2int(data: bytes, qlen: int) -> int:
    """
    IETF RFC 6979 Section 2.3.2 `bits2int`: big-endian integer conversion
    followed by right-shift by `blen - qlen` if `blen = 8 * len(data) > qlen`.
    """
    val = int.from_bytes(data, byteorder="big")
    blen = len(data) * 8
    if blen > qlen:
        val >>= blen - qlen
    return val


def _rfc6979_int2octets(val: int, rolen: int) -> bytes:
    """
    IETF RFC 6979 Section 2.3.3 `int2octets`: big-endian octet encoding of
    length `rolen = ceil(qlen / 8)`.
    """
    return val.to_bytes(rolen, byteorder="big")


def _rfc6979_bits2octets(
    data: bytes, group_order_q: int, qlen: int, rolen: int
) -> bytes:
    """
    IETF RFC 6979 Section 2.3.4 `bits2octets`: `int2octets(bits2int(data) mod q)`.
    """
    z1 = _rfc6979_bits2int(data, qlen)
    z2 = z1 % group_order_q
    return _rfc6979_int2octets(z2, rolen)


def rfc6979_generate_k(
    private_key: int,
    group_order_q: int,
    message_bytes: bytes,
) -> int:
    """
    Implement IETF RFC 6979 Section 3.2 deterministic nonce generation using
    `hmac` + `hashlib.sha256` (`V = 0x01 * 32`, `K = 0x00 * 32`, `bits2int`,
    `int2octets`, `bits2octets`), returning a deterministic `k in [1, q - 1]`.
    """
    x = require_strict_int(private_key, "private_key")
    q = require_strict_int(group_order_q, "group_order_q")
    msg = require_bytes(message_bytes, "message_bytes")

    if q < 2:
        raise EllipticCurveValueError(f"group_order_q must be >= 2, got {q}.")
    if x < 1 or x >= q:
        raise EllipticCurveValueError(
            f"private_key must lie strictly in [1, {q - 1}], got {x}."
        )

    qlen = q.bit_length()
    rolen = (qlen + 7) // 8

    # Step a: h1 = SHA-256(message_bytes)
    h1 = hashlib.sha256(msg).digest()
    x_octets = _rfc6979_int2octets(x, rolen)
    h1_octets = _rfc6979_bits2octets(h1, q, qlen, rolen)

    # Steps b & c: V = 0x01 * 32, K = 0x00 * 32
    v_bytes = b"\x01" * 32
    k_bytes = b"\x00" * 32

    # Step d: K = HMAC_K(V || 0x00 || int2octets(x) || bits2octets(h1))
    k_bytes = hmac.new(
        k_bytes,
        v_bytes + b"\x00" + x_octets + h1_octets,
        hashlib.sha256,
    ).digest()

    # Step e: V = HMAC_K(V)
    v_bytes = hmac.new(k_bytes, v_bytes, hashlib.sha256).digest()

    # Step f: K = HMAC_K(V || 0x01 || int2octets(x) || bits2octets(h1))
    k_bytes = hmac.new(
        k_bytes,
        v_bytes + b"\x01" + x_octets + h1_octets,
        hashlib.sha256,
    ).digest()

    # Step g: V = HMAC_K(V)
    v_bytes = hmac.new(k_bytes, v_bytes, hashlib.sha256).digest()

    # Step h: Loop until candidate k lies in [1, q - 1]
    while True:
        t_bytes = b""
        while len(t_bytes) * 8 < qlen:
            v_bytes = hmac.new(k_bytes, v_bytes, hashlib.sha256).digest()
            t_bytes += v_bytes

        candidate_k = _rfc6979_bits2int(t_bytes, qlen)
        if 1 <= candidate_k < q:
            return candidate_k

        k_bytes = hmac.new(
            k_bytes, v_bytes + b"\x00", hashlib.sha256
        ).digest()
        v_bytes = hmac.new(k_bytes, v_bytes, hashlib.sha256).digest()


def rfc6962_merkle_leaf_hash(leaf_bytes: bytes) -> bytes:
    """
    IETF RFC 6962 §2.1 leaf hash with normative `0x00` domain separation prefix:
        MTH({d(0)}) = SHA-256(0x00 || d(0)).
    """
    data = require_bytes(leaf_bytes, "leaf_bytes")
    return hashlib.sha256(b"\x00" + data).digest()


def rfc6962_merkle_node_hash(left_hash: bytes, right_hash: bytes) -> bytes:
    """
    IETF RFC 6962 §2.1 internal node hash with normative `0x01` domain separation:
        MTH(D[n]) = SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n])).
    """
    left = require_bytes(left_hash, "left_hash")
    right = require_bytes(right_hash, "right_hash")
    if len(left) != 32 or len(right) != 32:
        raise EllipticCurveValueError(
            "RFC 6962 node children must be 32-byte SHA-256 digests."
        )
    return hashlib.sha256(b"\x01" + left + right).digest()


def _rfc6962_largest_power_of_two_less_than(n: int) -> int:
    """Return the largest power of two strictly less than `n` (for `n >= 2`)."""
    k = 1
    while (k << 1) < n:
        k <<= 1
    return k


def rfc6962_merkle_tree_head(leaves: Sequence[bytes]) -> bytes:
    """
    Compute the normative IETF RFC 6962 §2.1 Merkle Tree Hash (MTH):
      - n == 0: SHA-256(b"")
      - n == 1: SHA-256(0x00 || d(0))
      - n >= 2: SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n]))
        where k is the largest power of 2 strictly less than n.
    """
    if isinstance(leaves, (bool, float)) or not isinstance(
        leaves, (list, tuple)
    ):
        raise RationalCovenantTypeError("leaves must be a list or tuple of bytes.")
    typed_leaves = [
        require_bytes(leaf, f"leaves[{i}]") for i, leaf in enumerate(leaves)
    ]
    n = len(typed_leaves)
    if n == 0:
        return hashlib.sha256(b"").digest()
    if n == 1:
        return rfc6962_merkle_leaf_hash(typed_leaves[0])
    k = _rfc6962_largest_power_of_two_less_than(n)
    left = rfc6962_merkle_tree_head(typed_leaves[:k])
    right = rfc6962_merkle_tree_head(typed_leaves[k:])
    return rfc6962_merkle_node_hash(left, right)


def rfc6962_merkle_inclusion_proof(
    leaves: Sequence[bytes], leaf_index: int
) -> List[bytes]:
    """
    Compute the IETF RFC 6962 §2.1.1 audit path (inclusion proof) for `leaf_index`
    in `leaves`.
    """
    idx = require_strict_int(leaf_index, "leaf_index")
    if isinstance(leaves, (bool, float)) or not isinstance(
        leaves, (list, tuple)
    ):
        raise RationalCovenantTypeError("leaves must be a list or tuple of bytes.")
    typed_leaves = [
        require_bytes(leaf, f"leaves[{i}]") for i, leaf in enumerate(leaves)
    ]
    n = len(typed_leaves)
    if n == 0 or idx < 0 or idx >= n:
        raise EllipticCurveValueError(
            f"leaf_index {idx} out of range for tree of size {n}."
        )
    if n == 1:
        return []
    k = _rfc6962_largest_power_of_two_less_than(n)
    if idx < k:
        sub_path = rfc6962_merkle_inclusion_proof(typed_leaves[:k], idx)
        sub_path.append(rfc6962_merkle_tree_head(typed_leaves[k:]))
        return sub_path
    sub_path = rfc6962_merkle_inclusion_proof(typed_leaves[k:], idx - k)
    sub_path.append(rfc6962_merkle_tree_head(typed_leaves[:k]))
    return sub_path


def rfc6962_verify_inclusion_proof(
    leaf_bytes: bytes,
    leaf_index: int,
    tree_size: int,
    audit_path: Sequence[bytes],
    expected_root: bytes,
) -> bool:
    """
    Verify an IETF RFC 6962 §2.1.1 Merkle audit path in constant time via
    `hmac.compare_digest`.
    """
    leaf = require_bytes(leaf_bytes, "leaf_bytes")
    idx = require_strict_int(leaf_index, "leaf_index")
    size = require_strict_int(tree_size, "tree_size")
    root = require_bytes(expected_root, "expected_root")
    if isinstance(audit_path, (bool, float)) or not isinstance(
        audit_path, (list, tuple)
    ):
        raise RationalCovenantTypeError("audit_path must be a sequence of bytes.")
    path = [
        require_bytes(node, f"audit_path[{i}]")
        for i, node in enumerate(audit_path)
    ]

    if size < 1 or idx < 0 or idx >= size or len(root) != 32:
        return False
    if any(len(node) != 32 for node in path):
        return False

    fn = idx
    sn = size - 1
    r_hash = rfc6962_merkle_leaf_hash(leaf)
    for p_node in path:
        if sn == 0:
            return False
        if (fn & 1) == 1 or fn == sn:
            r_hash = rfc6962_merkle_node_hash(p_node, r_hash)
            while (fn & 1) == 0 and fn != 0:
                fn >>= 1
                sn >>= 1
        else:
            r_hash = rfc6962_merkle_node_hash(r_hash, p_node)
        fn >>= 1
        sn >>= 1

    if sn != 0:
        return False
    return hmac.compare_digest(r_hash, root)


def _compute_schnorr_challenge(
    point_r: Tuple[int, int],
    point_p: Tuple[int, int],
    message_bytes: bytes,
    domain_tag: bytes = SCHNORR_DOMAIN_TAG,
) -> int:
    """
    Compute domain-separated Fiat-Shamir SHA-256 challenge scalar:
        e = int.from_bytes(SHA256(domain || R_x || R_y || P_x || P_y || m)) mod q
    If `e == 0`, set `e = 1`.
    """
    transcript = (
        domain_tag
        + point_r[0].to_bytes(4, byteorder="big")
        + point_r[1].to_bytes(4, byteorder="big")
        + point_p[0].to_bytes(4, byteorder="big")
        + point_p[1].to_bytes(4, byteorder="big")
        + message_bytes
    )
    digest = hashlib.sha256(transcript).digest()
    e = int.from_bytes(digest, byteorder="big") % CURVE_Q
    return 1 if e == 0 else e


def schnorr_zk_prove(
    private_key: int,
    message_bytes: bytes,
) -> tuple[tuple[int, int], int, int]:
    """
    Generate a non-interactive Fiat-Shamir Schnorr Zero-Knowledge proof
    `(R, e, s)` proving knowledge of discrete logarithm `x = private_key`
    such that `P = x * G` on `E(F_65537)` without revealing `x`.
    """
    x = require_strict_int(private_key, "private_key")
    msg = require_bytes(message_bytes, "message_bytes")
    if x < 1 or x >= CURVE_Q:
        raise EllipticCurveValueError(
            f"private_key must lie strictly in [1, {CURVE_Q - 1}], got {x}."
        )

    public_p = ec_scalar_mul(x, GENERATOR_G)
    if public_p is None:
        raise ArithmeticError("Public key P = x * G evaluated to infinity.")

    k = rfc6979_generate_k(x, CURVE_Q, msg)
    commitment_r = ec_scalar_mul(k, GENERATOR_G)
    if commitment_r is None:
        raise ArithmeticError("Commitment R = k * G evaluated to infinity.")

    e = _compute_schnorr_challenge(commitment_r, public_p, msg)
    s = (k + e * x) % CURVE_Q
    counter = 0
    while s == 0:
        counter += 1
        k = rfc6979_generate_k(
            x, CURVE_Q, msg + b"\x00" + counter.to_bytes(4, byteorder="big")
        )
        commitment_r = ec_scalar_mul(k, GENERATOR_G)
        if commitment_r is None:
            raise ArithmeticError("Fallback R evaluated to infinity.")
        e = _compute_schnorr_challenge(commitment_r, public_p, msg)
        s = (k + e * x) % CURVE_Q

    return (commitment_r, e, s)


def schnorr_zk_verify(
    public_key_point: tuple[int, int],
    message_bytes: bytes,
    proof: tuple[tuple[int, int], int, int],
) -> bool:
    """
    Verify a non-interactive Fiat-Shamir Schnorr Zero-Knowledge proof
    `(R, e, s)` against `public_key_point` and `message_bytes`:
        s * G == R + e * P
    using constant-time `hmac.compare_digest` comparisons while strictly
    rejecting point-at-infinity, off-curve points, `bool`/`float` types, or
    out-of-range scalars.
    """
    pt_p = _validate_point_structure(public_key_point, "public_key_point")
    msg = require_bytes(message_bytes, "message_bytes")

    if (
        isinstance(proof, (bool, float))
        or not isinstance(proof, tuple)
        or len(proof) != 3
    ):
        raise RationalCovenantTypeError(
            f"proof must be a 3-tuple (R, e, s), got {proof!r}."
        )

    raw_r, raw_e, raw_s = proof
    pt_r = _validate_point_structure(raw_r, "proof.R")
    e = require_strict_int(raw_e, "proof.e")
    s = require_strict_int(raw_s, "proof.s")

    if pt_p is None or pt_r is None:
        return False
    if not is_on_curve(pt_p) or not is_on_curve(pt_r):
        return False
    if e < 1 or e >= CURVE_Q or s < 1 or s >= CURVE_Q:
        return False

    # Subgroup membership verification: q * P == O and q * R == O
    if ec_scalar_mul_jacobian(CURVE_Q, pt_p) is not None:
        return False
    if ec_scalar_mul_jacobian(CURVE_Q, pt_r) is not None:
        return False

    expected_e = _compute_schnorr_challenge(pt_r, pt_p, msg)
    if not _ct_equal_scalars(e, expected_e):
        return False

    lhs = ec_scalar_mul(s, GENERATOR_G)
    rhs = ec_add(pt_r, ec_scalar_mul(e, pt_p))
    if lhs is None or rhs is None:
        return False
    return _ct_equal_points(lhs, rhs)


def schnorr_zk_batch_verify(
    public_keys: Sequence[tuple[int, int]],
    messages: Sequence[bytes],
    proofs: Sequence[SchnorrProof],
) -> bool:
    """
    Verify a batch of Fiat-Shamir Schnorr Zero-Knowledge proofs simultaneously
    using IETF RFC 6962 Merkle Tree Head (`MTH`) transcript-bound Bellare-Garay-
    Rabin linear combination weights `alpha_j in [1, q - 1]` and inversion-free
    Jacobian projective accumulation:
        (sum_j alpha_j * s_j mod q) * G == sum_j alpha_j * R_j + sum_j (alpha_j * e_j mod q) * P_j
    Enforces Universal Type-First Precedence across all inputs.
    """
    if isinstance(public_keys, (bool, float)) or not isinstance(
        public_keys, (list, tuple)
    ):
        raise RationalCovenantTypeError("public_keys must be a list or tuple.")
    if isinstance(messages, (bool, float)) or not isinstance(
        messages, (list, tuple)
    ):
        raise RationalCovenantTypeError("messages must be a list or tuple.")
    if isinstance(proofs, (bool, float)) or not isinstance(
        proofs, (list, tuple)
    ):
        raise RationalCovenantTypeError("proofs must be a list or tuple.")

    typed_pks = [
        _validate_point_structure(pk, f"public_keys[{i}]")
        for i, pk in enumerate(public_keys)
    ]
    typed_msgs = [
        require_bytes(m, f"messages[{i}]") for i, m in enumerate(messages)
    ]
    typed_proofs: List[Tuple[ECPoint, int, int]] = []
    for i, pr in enumerate(proofs):
        if (
            isinstance(pr, (bool, float))
            or not isinstance(pr, tuple)
            or len(pr) != 3
        ):
            raise RationalCovenantTypeError(
                f"proofs[{i}] must be a 3-tuple (R, e, s)."
            )
        r_pt = _validate_point_structure(pr[0], f"proofs[{i}].R")
        e_val = require_strict_int(pr[1], f"proofs[{i}].e")
        s_val = require_strict_int(pr[2], f"proofs[{i}].s")
        typed_proofs.append((r_pt, e_val, s_val))

    count = len(typed_pks)
    if count == 0 or len(typed_msgs) != count or len(typed_proofs) != count:
        return False

    batch_leaves: List[bytes] = []
    validated_items: List[Tuple[Tuple[int, int], Tuple[int, int], int, int]] = []

    for idx in range(count):
        pt_p = typed_pks[idx]
        msg = typed_msgs[idx]
        pt_r, e, s = typed_proofs[idx]

        if pt_p is None or pt_r is None:
            return False
        if not is_on_curve(pt_p) or not is_on_curve(pt_r):
            return False
        if e < 1 or e >= CURVE_Q or s < 1 or s >= CURVE_Q:
            return False
        if ec_scalar_mul_jacobian(CURVE_Q, pt_p) is not None:
            return False
        if ec_scalar_mul_jacobian(CURVE_Q, pt_r) is not None:
            return False

        expected_e = _compute_schnorr_challenge(pt_r, pt_p, msg)
        if not _ct_equal_scalars(e, expected_e):
            return False

        leaf_payload = (
            idx.to_bytes(4, byteorder="big")
            + pt_r[0].to_bytes(4, byteorder="big")
            + pt_r[1].to_bytes(4, byteorder="big")
            + pt_p[0].to_bytes(4, byteorder="big")
            + pt_p[1].to_bytes(4, byteorder="big")
            + e.to_bytes(4, byteorder="big")
            + s.to_bytes(4, byteorder="big")
            + len(msg).to_bytes(4, byteorder="big")
            + msg
        )
        batch_leaves.append(leaf_payload)
        validated_items.append((pt_p, pt_r, e, s))

    batch_mth = rfc6962_merkle_tree_head(batch_leaves)
    total_s = 0
    rhs_jac: JacobianPoint = (1, 1, 0)

    for idx, (pt_p, pt_r, e, s) in enumerate(validated_items):
        weight_seed = (
            SCHNORR_BATCH_DOMAIN_TAG
            + batch_mth
            + idx.to_bytes(4, byteorder="big")
        )
        alpha = (
            int.from_bytes(hashlib.sha256(weight_seed).digest(), "big")
            % (CURVE_Q - 1)
        ) + 1
        total_s = (total_s + alpha * s) % CURVE_Q
        term_r = ec_scalar_mul_jacobian(alpha, pt_r)
        term_p = ec_scalar_mul_jacobian((alpha * e) % CURVE_Q, pt_p)
        rhs_jac = _jacobian_add(rhs_jac, _affine_to_jacobian(term_r))
        rhs_jac = _jacobian_add(rhs_jac, _affine_to_jacobian(term_p))

    lhs_point = ec_scalar_mul_jacobian(total_s, GENERATOR_G)
    rhs_point = _jacobian_to_affine(rhs_jac)
    return _ct_equal_points(lhs_point, rhs_point)


def verify_schnorr_special_soundness_algebra(
    private_key: int,
    nonce_k: int,
    challenge_e1: int,
    challenge_e2: int,
) -> Dict[str, bool]:
    """
    Verify the Special Soundness (2-Transcript Witness Extraction) Theorem of
    the Schnorr Sigma-Protocol over E(F_65537):
        x_extracted = (s_1 - s_2) * (e_1 - e_2)^{-1} mod q
        k_extracted = (s_1 - e_1 * x) mod q.
    """
    x_raw = require_strict_int(private_key, "private_key")
    k_raw = require_strict_int(nonce_k, "nonce_k")
    e1_raw = require_strict_int(challenge_e1, "challenge_e1")
    e2_raw = require_strict_int(challenge_e2, "challenge_e2")
    x = x_raw % CURVE_Q
    k = k_raw % CURVE_Q
    e1 = e1_raw % CURVE_Q
    e2 = e2_raw % CURVE_Q
    if x == 0 or k == 0 or e1 == 0 or e2 == 0 or e1 == e2:
        raise EllipticCurveValueError(
            "Special soundness requires non-zero scalars x, k, e1, e2 (mod q) "
            "and distinct challenges e1 != e2 (mod q)."
        )

    pub_p = ec_scalar_mul(x, GENERATOR_G)
    comm_r = ec_scalar_mul(k, GENERATOR_G)
    s1 = (k + e1 * x) % CURVE_Q
    s2 = (k + e2 * x) % CURVE_Q

    eq1_ok = _ct_equal_points(
        ec_scalar_mul(s1, GENERATOR_G),
        ec_add(comm_r, ec_scalar_mul(e1, pub_p)),
    )
    eq2_ok = _ct_equal_points(
        ec_scalar_mul(s2, GENERATOR_G),
        ec_add(comm_r, ec_scalar_mul(e2, pub_p)),
    )

    inv_de = pow((e1 - e2) % CURVE_Q, -1, CURVE_Q)
    extracted_x = ((s1 - s2) * inv_de) % CURVE_Q
    extracted_k = (s1 - e1 * extracted_x) % CURVE_Q

    return {
        "transcript_1_valid": eq1_ok,
        "transcript_2_valid": eq2_ok,
        "witness_x_extracted_exact": _ct_equal_scalars(extracted_x, x),
        "nonce_k_extracted_exact": _ct_equal_scalars(extracted_k, k),
    }


def pedersen_commit(
    value_seeds: int,
    blinding_factor: int,
) -> tuple[int, int] | None:
    """
    Compute homomorphic Pedersen commitment on `E(F_65537)`:
        C(v, r) = (v mod q) * G + (r mod q) * H
    using primary generator `G = (1, 12240)` and Pedersen generator
    `H = (2, 27135)`.
    """
    v = require_strict_int(value_seeds, "value_seeds")
    r = require_strict_int(blinding_factor, "blinding_factor")

    v_part = ec_scalar_mul(v % CURVE_Q, GENERATOR_G)
    r_part = ec_scalar_mul(r % CURVE_Q, GENERATOR_H)
    return ec_add(v_part, r_part)


def verify_pedersen_balance_conservation(
    input_commitments: list[tuple[int, int] | None],
    output_commitments: list[tuple[int, int] | None],
    excess_blinding: int,
) -> bool:
    """
    Verify zero-knowledge homomorphic seed balance conservation in constant time:
        sum C_in == sum C_out + (excess_blinding mod q) * H.
    Enforces Universal Type-First Precedence (Invariant T1).
    """
    if isinstance(input_commitments, (bool, float)) or not isinstance(
        input_commitments, list
    ):
        raise RationalCovenantTypeError(
            "input_commitments must be a list of elliptic curve points."
        )
    if isinstance(output_commitments, (bool, float)) or not isinstance(
        output_commitments, list
    ):
        raise RationalCovenantTypeError(
            "output_commitments must be a list of elliptic curve points."
        )
    r_excess = require_strict_int(excess_blinding, "excess_blinding")

    validated_ins: List[ECPoint] = [
        _validate_point_structure(c_in, f"input_commitments[{idx}]")
        for idx, c_in in enumerate(input_commitments)
    ]
    validated_outs: List[ECPoint] = [
        _validate_point_structure(c_out, f"output_commitments[{idx}]")
        for idx, c_out in enumerate(output_commitments)
    ]

    if len(validated_ins) == 0 or len(validated_outs) == 0:
        return False

    sum_in: ECPoint = None
    for pt in validated_ins:
        if not is_on_curve(pt):
            return False
        sum_in = ec_add(sum_in, pt)

    sum_out: ECPoint = None
    for pt in validated_outs:
        if not is_on_curve(pt):
            return False
        sum_out = ec_add(sum_out, pt)

    excess_point = ec_scalar_mul(r_excess % CURVE_Q, GENERATOR_H)
    rhs = ec_add(sum_out, excess_point)
    return _ct_equal_points(sum_in, rhs)


def pedersen_opening_zk_prove(
    value_seeds: int,
    blinding_factor: int,
    message_bytes: bytes,
) -> PedersenOpeningProof:
    """
    Generate a non-interactive Chaum-Pedersen / Okamoto-Schnorr Zero-Knowledge
    Opening Proof `(T, e, s_v, s_r)` proving knowledge of `(v, r)` such that
    `C = (v mod q) * G + (r mod q) * H` without revealing `v` or `r`, with
    joint witness-bound RFC 6979 nonces and strict Z_q^* response range.
    """
    v_raw = require_strict_int(value_seeds, "value_seeds")
    r_raw = require_strict_int(blinding_factor, "blinding_factor")
    msg = require_bytes(message_bytes, "message_bytes")

    v = v_raw % CURVE_Q
    r = r_raw % CURVE_Q
    commitment_c = pedersen_commit(v, r)
    if commitment_c is None:
        raise EllipticCurveValueError(
            "Pedersen commitment C evaluated to point at infinity."
        )

    witness_binding = (
        v.to_bytes(4, byteorder="big")
        + r.to_bytes(4, byteorder="big")
        + msg
    )
    seed_v = ((v + r) % (CURVE_Q - 1)) + 1
    seed_r = ((v + 2 * r + 1) % (CURVE_Q - 1)) + 1
    k_v = rfc6979_generate_k(
        seed_v, CURVE_Q, b"PEDERSEN_KV:" + witness_binding
    )
    k_r = rfc6979_generate_k(
        seed_r, CURVE_Q, b"PEDERSEN_KR:" + witness_binding
    )

    point_t = pedersen_commit(k_v, k_r)
    e = (
        _compute_schnorr_challenge(
            point_t, commitment_c, msg, domain_tag=PEDERSEN_OPENING_DOMAIN_TAG
        )
        if point_t is not None
        else 0
    )
    s_v = (k_v + e * v) % CURVE_Q
    s_r = (k_r + e * r) % CURVE_Q

    counter = 0
    while (
        point_t is None
        or s_v == 0
        or s_r == 0
        or pedersen_commit(s_v, s_r) is None
    ):
        counter += 1
        suffix = b"\x00" + counter.to_bytes(4, byteorder="big")
        k_v = rfc6979_generate_k(
            seed_v, CURVE_Q, b"PEDERSEN_KV:" + witness_binding + suffix
        )
        k_r = rfc6979_generate_k(
            seed_r, CURVE_Q, b"PEDERSEN_KR:" + witness_binding + suffix
        )
        point_t = pedersen_commit(k_v, k_r)
        if point_t is not None:
            e = _compute_schnorr_challenge(
                point_t,
                commitment_c,
                msg,
                domain_tag=PEDERSEN_OPENING_DOMAIN_TAG,
            )
            s_v = (k_v + e * v) % CURVE_Q
            s_r = (k_r + e * r) % CURVE_Q

    return (point_t, e, s_v, s_r)


def pedersen_opening_zk_verify(
    commitment_point: tuple[int, int] | None,
    message_bytes: bytes,
    opening_proof: PedersenOpeningProof,
) -> bool:
    """
    Verify a Chaum-Pedersen / Okamoto-Schnorr Zero-Knowledge Pedersen opening
    proof `(T, e, s_v, s_r)` against `commitment_point` and `message_bytes`:
        s_v * G + s_r * H == T + e * C
    in constant time via `hmac.compare_digest` with strict Z_q^* scalar bounds.
    """
    pt_c = _validate_point_structure(commitment_point, "commitment_point")
    msg = require_bytes(message_bytes, "message_bytes")

    if (
        isinstance(opening_proof, (bool, float))
        or not isinstance(opening_proof, tuple)
        or len(opening_proof) != 4
    ):
        raise RationalCovenantTypeError(
            f"opening_proof must be a 4-tuple (T, e, s_v, s_r), got "
            f"{opening_proof!r}."
        )

    raw_t, raw_e, raw_sv, raw_sr = opening_proof
    pt_t = _validate_point_structure(raw_t, "opening_proof.T")
    e = require_strict_int(raw_e, "opening_proof.e")
    s_v = require_strict_int(raw_sv, "opening_proof.s_v")
    s_r = require_strict_int(raw_sr, "opening_proof.s_r")

    if pt_c is None or pt_t is None:
        return False
    if not is_on_curve(pt_c) or not is_on_curve(pt_t):
        return False
    if (
        e < 1
        or e >= CURVE_Q
        or s_v < 1
        or s_v >= CURVE_Q
        or s_r < 1
        or s_r >= CURVE_Q
    ):
        return False

    # Subgroup membership verification: q * C == O and q * T == O
    if ec_scalar_mul_jacobian(CURVE_Q, pt_c) is not None:
        return False
    if ec_scalar_mul_jacobian(CURVE_Q, pt_t) is not None:
        return False

    expected_e = _compute_schnorr_challenge(
        pt_t, pt_c, msg, domain_tag=PEDERSEN_OPENING_DOMAIN_TAG
    )
    if not _ct_equal_scalars(e, expected_e):
        return False

    lhs = pedersen_commit(s_v, s_r)
    rhs = ec_add(pt_t, ec_scalar_mul(e, pt_c))
    if lhs is None or rhs is None:
        return False
    return _ct_equal_points(lhs, rhs)


# ==============================================================================
# SECTION 4: PILLAR III — EXACT CONTINUED FRACTIONS, STERN-BROCOT MEDIANTS &
#            7-WISDOMS SYNODIC DIOPHANTINE RESONANCE
# ==============================================================================


@dataclass(frozen=True)
class ConvergentRecord:
    """
    Detailed record of the k-th convergent `p_k / q_k` of a continued fraction.
    """

    index_k: int
    partial_quotient_a: int
    numerator_p: int
    denominator_q: int
    convergent: Fraction
    determinant_identity_value: Optional[int]


@dataclass(frozen=True)
class SternBrocotMediantStep:
    """
    Single step in the Stern-Brocot tree traversal from `0/1` and `1/0`,
    recording the unimodular bracket `(a/b, c/d)` with `c * b - a * d == 1`
    and its mediant `(a + c) / (b + d)`.
    """

    step_index: int
    left_a: int
    left_b: int
    right_c: int
    right_d: int
    mediant_num: int
    mediant_den: int
    mediant: Fraction
    unimodular_det: int
    direction: str


@dataclass(frozen=True)
class SynodicResonanceReport:
    """
    Synthesis of the 7-Wisdoms Diophantine & Synodic Resonance uniting the
    108 Sacred Pearls, the 260-day Mayan Tzolkin, and the 584/365 = 8/5
    Venus/Earth synodic ratio.
    """

    venus_earth_exact_ratio: Fraction
    venus_earth_continued_fraction: Tuple[int, ...]
    venus_earth_convergents: Tuple[Fraction, ...]
    tzolkin_pearls_exact_ratio: Fraction
    tzolkin_pearls_continued_fraction: Tuple[int, ...]
    tzolkin_pearls_convergents: Tuple[Fraction, ...]
    pentagram_lock_verified: bool
    pearls_tzolkin_lcm: int
    grand_harmonic_lcm_days: int
    stern_brocot_venus_108: Dict[str, object]
    stern_brocot_tzolkin_12: Dict[str, object]
    stern_brocot_tzolkin_20: Dict[str, object]
    stern_brocot_tzolkin_108: Dict[str, object]


def rational_to_continued_fraction(q: Fraction) -> list[int]:
    """
    Expand any exact rational `q` (`Fraction` or strict `int`) into its unique
    canonical simple continued fraction `[a_0; a_1, ..., a_k]` where `a_i >= 1`
    for all `i >= 1` and (when `k >= 1`) `a_k >= 2`.
    """
    val = require_exact_rational(q, "q")
    num = val.numerator
    den = val.denominator

    coeffs: List[int] = []
    while den != 0:
        a = num // den
        coeffs.append(a)
        num, den = den, num - a * den

    return coeffs


def _validate_continued_fraction_coeffs(coeffs: list[int]) -> List[int]:
    """
    Validate that `coeffs` is a non-empty list of strict `int`s with
    `coeffs[i] >= 1` for all `i >= 1`, enforcing Universal Type-First Precedence.
    """
    if isinstance(coeffs, (bool, float)) or not isinstance(coeffs, list):
        raise RationalCovenantTypeError(
            f"coeffs must be a list of strict ints, got "
            f"{type(coeffs).__name__}."
        )
    validated: List[int] = [
        require_strict_int(raw_c, f"coeffs[{idx}]")
        for idx, raw_c in enumerate(coeffs)
    ]
    if len(validated) == 0:
        raise DiophantineValueError(
            "coeffs must be a non-empty list of partial quotients [a_0; a_1, ...]."
        )

    for idx, c_int in enumerate(validated):
        if idx >= 1 and c_int < 1:
            raise DiophantineValueError(
                f"Continued fraction partial quotient coeffs[{idx}] must be "
                f">= 1 for all idx >= 1, got {c_int}."
            )
    return validated


def continued_fraction_to_rational(coeffs: list[int]) -> Fraction:
    """
    Reconstruct the exact `fractions.Fraction` from its simple continued
    fraction coefficients `[a_0; a_1, ..., a_k]`.
    """
    validated = _validate_continued_fraction_coeffs(coeffs)
    acc = Fraction(validated[-1], 1)
    for a in reversed(validated[:-1]):
        acc = Fraction(a, 1) + Fraction(1, acc)
    return acc


def compute_detailed_convergents(coeffs: list[int]) -> List[ConvergentRecord]:
    """
    Compute the sequence of `ConvergentRecord` entries for `coeffs` and verify
    Lagrange's unimodular determinant identity at every step `k >= 1`:
        p_k * q_{k-1} - p_{k-1} * q_k == (-1)^{k - 1}.
    """
    validated = _validate_continued_fraction_coeffs(coeffs)
    p_prev2, p_prev1 = 0, 1
    q_prev2, q_prev1 = 1, 0

    records: List[ConvergentRecord] = []
    for k, a_k in enumerate(validated):
        p_k = a_k * p_prev1 + p_prev2
        q_k = a_k * q_prev1 + q_prev2

        det_val: Optional[int] = None
        if k >= 1:
            det_val = p_k * q_prev1 - p_prev1 * q_k
            expected_det = 1 if ((k - 1) % 2 == 0) else -1
            if det_val != expected_det:
                raise ArithmeticError(
                    f"Determinant identity violated at k={k}: "
                    f"got {det_val}, expected {expected_det}."
                )

        records.append(
            ConvergentRecord(
                index_k=k,
                partial_quotient_a=a_k,
                numerator_p=p_k,
                denominator_q=q_k,
                convergent=Fraction(p_k, q_k),
                determinant_identity_value=det_val,
            )
        )
        p_prev2, p_prev1 = p_prev1, p_k
        q_prev2, q_prev1 = q_prev1, q_k

    return records


def convergents_of_continued_fraction(coeffs: list[int]) -> list[Fraction]:
    """
    Compute all convergents `[p_0/q_0, p_1/q_1, ..., p_k/q_k]` of a simple
    continued fraction `[a_0; a_1, ..., a_k]` while verifying the exact
    determinant identity `p_k * q_{k-1} - p_{k-1} * q_k = (-1)^{k - 1}` for
    all `k >= 1`.
    """
    return [rec.convergent for rec in compute_detailed_convergents(coeffs)]


def verify_lagrange_convergent_optimality(
    target: Fraction,
    max_scan_denominator: int = 2048,
) -> bool:
    """
    Verify Legendre's convergent error bound and Lagrange's Law of Best
    Approximations of the Second Kind (Khinchin, Continued Fractions, Theorem 17)
    for every principal convergent `p_k / q_k` of `target` up to
    `max_scan_denominator`.
    """
    q_target = require_exact_rational(target, "target")
    scan_cap = require_strict_int(
        max_scan_denominator, "max_scan_denominator"
    )
    if scan_cap < 1:
        raise DiophantineValueError("max_scan_denominator must be >= 1.")

    coeffs = rational_to_continued_fraction(q_target)
    records = compute_detailed_convergents(coeffs)

    for idx, rec in enumerate(records):
        if idx + 1 < len(records):
            q_next = records[idx + 1].denominator_q
            if abs(q_target - rec.convergent) > Fraction(
                1, rec.denominator_q * q_next
            ):
                return False

        if (
            rec.index_k == 0
            and len(records) > 1
            and records[1].partial_quotient_a == 1
        ):
            continue
        p_k = rec.numerator_p
        q_k = rec.denominator_q
        conv_err = abs(Fraction(q_k, 1) * q_target - Fraction(p_k, 1))
        limit_q = min(q_k, scan_cap)
        for q_cand in range(1, limit_q + 1):
            scaled = q_cand * q_target
            p_floor = scaled.numerator // scaled.denominator
            for p_cand in (p_floor, p_floor + 1):
                if Fraction(p_cand, q_cand) == rec.convergent:
                    continue
                cand_err = abs(
                    Fraction(q_cand, 1) * q_target - Fraction(p_cand, 1)
                )
                if cand_err < conv_err:
                    return False
                if cand_err == conv_err and q_cand < q_k:
                    return False
    return True


def trace_stern_brocot_mediants(
    target: Fraction,
    max_denominator: int,
) -> Tuple[Dict[str, object], Tuple[SternBrocotMediantStep, ...]]:
    """
    Traverse the Stern-Brocot tree starting from `0/1` and `1/0` by mediants
    `(a + c) / (b + d)` while `b + d <= max_denominator` for strictly positive
    `target > 0` and `max_denominator >= 1`, returning both the required
    summary dictionary and the step-by-step `SternBrocotMediantStep` trace.

    Includes Top-of-Loop Arbitrary-Depth SL_2(Z) Leapfrog Acceleration: whenever
    a run of consecutive Left or Right steps exceeds
    `STERN_BROCOT_ACCELERATION_THRESHOLD` (64), jumps `k_jump = k_limit - 1`
    steps in O(1) integer arithmetic so the unimodular parent bracket `(a/b, c/d)`
    satisfying `c * b - a * d == 1` right before the terminal step is always
    visited, verified, and recorded in `steps`.
    """
    q_target = require_exact_rational(target, "target")
    max_den = require_strict_int(max_denominator, "max_denominator")

    if q_target <= Fraction(0, 1):
        raise DiophantineValueError(
            f"target must be strictly positive (> 0), got {q_target}."
        )
    if max_den < 1:
        raise DiophantineValueError(
            f"max_denominator must be >= 1, got {max_den}."
        )

    # Initial Stern-Brocot ancestors: left = 0/1, right = 1/0
    a, b = 0, 1
    c, d = 1, 0
    p_num = q_target.numerator
    q_den = q_target.denominator

    unimodular_ok: bool = (c * b - a * d) == 1
    exact_mediant_hit: Optional[Fraction] = None
    steps: List[SternBrocotMediantStep] = []
    step_idx = 0

    while b + d <= max_den:
        # Top-of-loop arbitrary-depth SL_2(Z) leapfrog when a run of L or R
        # exceeds STERN_BROCOT_ACCELERATION_THRESHOLD
        med_cmp = p_num * (b + d) - q_den * (a + c)
        if med_cmp > 0:
            denom_gap = q_den * c - p_num * d
            if denom_gap > 0:
                k_target = (p_num * b - q_den * a) // denom_gap
                k_limit = (
                    min(k_target, (max_den - b) // d)
                    if d > 0
                    else k_target
                )
                if k_limit > STERN_BROCOT_ACCELERATION_THRESHOLD:
                    k_jump = k_limit - 1
                    a += k_jump * c
                    b += k_jump * d
        elif med_cmp < 0:
            denom_gap = p_num * b - q_den * a
            if denom_gap > 0:
                k_target = (q_den * c - p_num * d) // denom_gap
                k_limit = min(k_target, (max_den - d) // b)
                if k_limit > STERN_BROCOT_ACCELERATION_THRESHOLD:
                    k_jump = k_limit - 1
                    c += k_jump * a
                    d += k_jump * b

        det_now = c * b - a * d
        if det_now != 1:
            unimodular_ok = False
        med_num = a + c
        med_den = b + d
        mediant = Fraction(med_num, med_den)

        if mediant == q_target:
            unimodular_ok = unimodular_ok and (det_now == 1)
            exact_mediant_hit = mediant
            steps.append(
                SternBrocotMediantStep(
                    step_index=step_idx,
                    left_a=a,
                    left_b=b,
                    right_c=c,
                    right_d=d,
                    mediant_num=med_num,
                    mediant_den=med_den,
                    mediant=mediant,
                    unimodular_det=det_now,
                    direction="H",
                )
            )
            break
        elif q_target < mediant:
            steps.append(
                SternBrocotMediantStep(
                    step_index=step_idx,
                    left_a=a,
                    left_b=b,
                    right_c=c,
                    right_d=d,
                    mediant_num=med_num,
                    mediant_den=med_den,
                    mediant=mediant,
                    unimodular_det=det_now,
                    direction="L",
                )
            )
            c, d = med_num, med_den
        else:
            steps.append(
                SternBrocotMediantStep(
                    step_index=step_idx,
                    left_a=a,
                    left_b=b,
                    right_c=c,
                    right_d=d,
                    mediant_num=med_num,
                    mediant_den=med_den,
                    mediant=mediant,
                    unimodular_det=det_now,
                    direction="R",
                )
            )
            a, b = med_num, med_den
        step_idx += 1

    if (c * b - a * d) != 1:
        unimodular_ok = False

    best_lower = Fraction(a, b)
    if d > 0:
        best_upper = Fraction(c, d)
    elif exact_mediant_hit is not None:
        best_upper = exact_mediant_hit
    else:
        best_upper = Fraction(a + 1, 1)

    if exact_mediant_hit is not None:
        best_approximant = exact_mediant_hit
    else:
        candidates: List[Fraction] = [best_lower]
        if d > 0 and d <= max_den:
            candidates.append(best_upper)
        best_approximant = min(
            candidates,
            key=lambda cand: (abs(q_target - cand), cand.denominator, cand),
        )

    summary: Dict[str, object] = {
        "best_lower": best_lower,
        "best_upper": best_upper,
        "best_approximant": best_approximant,
        "unimodular_determinant_verified": unimodular_ok,
    }
    return summary, tuple(steps)


def stern_brocot_best_approximants(
    target: Fraction,
    max_denominator: int,
) -> dict[str, object]:
    """
    Traverse the Stern-Brocot tree starting from `0/1` and `1/0` by mediants
    `(a + c) / (b + d)` while `b + d <= max_denominator` for strictly positive
    `target > 0` and `max_denominator >= 1`.
    """
    summary, _ = trace_stern_brocot_mediants(
        target=target,
        max_denominator=max_denominator,
    )
    return summary


def verify_stern_brocot_best_approximant_optimality(
    target: Fraction,
    max_denominator: int,
    max_scan_denominator: int = 2048,
) -> bool:
    """
    Verify the Semi-Convergent / Best Rational Approximation of the First Kind
    Theorem (Graham, Knuth, Patashnik, Concrete Mathematics §4.5) in
    O(log H + min(max_denominator, max_scan_denominator)) time:
      1. Exact O(log H) Farey Unimodular Bracket Certificate: verifies
         best_lower <= target <= best_upper, unimodular determinant == 1, and
         (when target is not hit exactly and upper bracket is finite)
         best_lower.denominator + best_upper.denominator > max_denominator.
      2. Exhaustive denominator verification for all 1 <= q <= min(max_denominator,
         max_scan_denominator).
    """
    q_target = require_exact_rational(target, "target")
    max_den = require_strict_int(max_denominator, "max_denominator")
    scan_cap = require_strict_int(
        max_scan_denominator, "max_scan_denominator"
    )
    if scan_cap < 1:
        raise DiophantineValueError("max_scan_denominator must be >= 1.")

    summary = stern_brocot_best_approximants(q_target, max_den)
    if not summary["unimodular_determinant_verified"]:
        return False

    best_lower = summary["best_lower"]
    best_upper = summary["best_upper"]
    best_approx = summary["best_approximant"]
    assert isinstance(best_lower, Fraction)
    assert isinstance(best_upper, Fraction)
    assert isinstance(best_approx, Fraction)

    if not (best_lower <= q_target <= best_upper):
        return False
    if best_approx != q_target and best_upper <= q_target:
        return False
    if (
        best_approx != q_target
        and best_upper.denominator <= max_den
        and (best_lower.denominator + best_upper.denominator <= max_den)
    ):
        return False

    best_err = abs(q_target - best_approx)
    limit_q = min(max_den, scan_cap)
    for q_cand in range(1, limit_q + 1):
        scaled = q_cand * q_target
        p_floor = max(0, scaled.numerator // scaled.denominator)
        for p_cand in (p_floor, p_floor + 1):
            cand = Fraction(p_cand, q_cand)
            cand_err = abs(q_target - cand)
            if cand_err < best_err:
                return False
            if cand_err == best_err:
                if (cand.denominator, cand) < (
                    best_approx.denominator,
                    best_approx,
                ):
                    return False
    return True


def stern_brocot_path_encoding(
    target: Fraction,
    max_steps: int = 256,
) -> str:
    """
    Encode the Stern-Brocot navigation path from root mediant `1/1` to
    `target > 0` as a string of `'L'` (left) and `'R'` (right) steps using O(1)
    integer cross-products per step (zero intermediate `Fraction` allocations).
    """
    q_target = require_exact_rational(target, "target")
    limit = require_strict_int(max_steps, "max_steps")
    if q_target <= Fraction(0, 1):
        raise DiophantineValueError("target must be strictly positive.")
    if limit < 1:
        raise DiophantineValueError("max_steps must be >= 1.")

    a, b = 0, 1
    c, d = 1, 0
    p_num = q_target.numerator
    q_den = q_target.denominator
    steps: List[str] = []
    for _ in range(limit):
        m_num = a + c
        m_den = b + d
        cmp_val = p_num * m_den - q_den * m_num
        if cmp_val == 0:
            break
        elif cmp_val < 0:
            steps.append("L")
            c, d = m_num, m_den
        else:
            steps.append("R")
            a, b = m_num, m_den
    return "".join(steps)


def continued_fraction_to_stern_brocot_path(
    target: Fraction,
    max_path_length: int = 100000,
) -> str:
    """
    Construct the exact Stern-Brocot `'L'`/`'R'` path of `target > 0` directly
    from its canonical continued fraction `[a_0; a_1, ..., a_k]` via the
    Run-Length Isomorphism Theorem.
    """
    q_target = require_exact_rational(target, "target")
    limit = require_strict_int(max_path_length, "max_path_length")
    if q_target <= Fraction(0, 1):
        raise DiophantineValueError("target must be strictly positive.")
    if limit < 1:
        raise DiophantineValueError("max_path_length must be >= 1.")

    cf = rational_to_continued_fraction(q_target)
    total_len = sum(cf) - 1
    if total_len > limit:
        raise DiophantineValueError(
            f"Stern-Brocot path length {total_len} exceeds max_path_length={limit}."
        )
    if len(cf) == 1:
        return "R" * (cf[0] - 1)

    runs = list(cf)
    runs[-1] -= 1
    chunks: List[str] = []
    for idx, count in enumerate(runs):
        symbol = "R" if (idx % 2 == 0) else "L"
        if count > 0:
            chunks.append(symbol * count)
    return "".join(chunks)


def stern_brocot_sl2z_matrix_from_path(path: str) -> SL2ZMatrix:
    """
    Compute the unimodular SL_2(Z) matrix `M(w) = ((c, a), (d, b))` for a
    Stern-Brocot navigation path `w in {'L', 'R'}*` via the monoid generators:
        L = ((1, 0), (1, 1)),   R = ((1, 1), (0, 1))
    satisfying `det(M(w)) = c * b - a * d == 1`.
    """
    if isinstance(path, (bool, float)) or not isinstance(path, str):
        raise RationalCovenantTypeError("path must be a string of 'L' and 'R'.")
    c, a = 1, 0
    d, b = 0, 1
    for ch in path:
        if ch == "L":
            c, d = c + a, d + b
        elif ch == "R":
            a, b = c + a, d + b
        else:
            raise DiophantineValueError(
                f"Invalid Stern-Brocot path symbol {ch!r}; expected 'L' or 'R'."
            )
    if (c * b - a * d) != 1:
        raise ArithmeticError("SL_2(Z) determinant invariant violated.")
    return ((c, a), (d, b))


def analyze_seven_wisdoms_synodic_resonance() -> SynodicResonanceReport:
    """
    Execute the 7-Wisdoms Diophantine & Synodic Resonance synthesis uniting:
      1. The 108 Sacred Pearls (`SACRED_PEARLS_COUNT = 108`).
      2. The 260-day Mayan Tzolkin (`MAYAN_TZOLKIN_DAYS = 260`).
      3. The Venus/Earth synodic ratio `584 / 365 = 8 / 5 = [1; 1, 1, 2]`.
    """
    venus_cf = rational_to_continued_fraction(VENUS_EARTH_SYNODIC_RATIO)
    venus_conv = convergents_of_continued_fraction(venus_cf)

    tzolkin_cf = rational_to_continued_fraction(TZOLKIN_PEARLS_RATIO)
    tzolkin_conv = convergents_of_continued_fraction(tzolkin_cf)

    pentagram_lock = (
        5 * VENUS_SYNODIC_PERIOD_DAYS == 8 * EARTH_SOLAR_YEAR_DAYS
        and VENUS_EARTH_SYNODIC_RATIO == Fraction(8, 5)
    )

    pearls_tzolkin_lcm = exact_lcm(SACRED_PEARLS_COUNT, MAYAN_TZOLKIN_DAYS)
    venus_earth_lcm = exact_lcm(
        EARTH_SOLAR_YEAR_DAYS, VENUS_SYNODIC_PERIOD_DAYS
    )
    grand_lcm = exact_lcm(pearls_tzolkin_lcm, venus_earth_lcm)

    sb_venus_108 = stern_brocot_best_approximants(
        VENUS_EARTH_SYNODIC_RATIO, SACRED_PEARLS_COUNT
    )
    sb_tzolkin_12 = stern_brocot_best_approximants(
        TZOLKIN_PEARLS_RATIO, max_denominator=12
    )
    sb_tzolkin_20 = stern_brocot_best_approximants(
        TZOLKIN_PEARLS_RATIO, max_denominator=20
    )
    sb_tzolkin_108 = stern_brocot_best_approximants(
        TZOLKIN_PEARLS_RATIO, max_denominator=SACRED_PEARLS_COUNT
    )

    return SynodicResonanceReport(
        venus_earth_exact_ratio=VENUS_EARTH_SYNODIC_RATIO,
        venus_earth_continued_fraction=tuple(venus_cf),
        venus_earth_convergents=tuple(venus_conv),
        tzolkin_pearls_exact_ratio=TZOLKIN_PEARLS_RATIO,
        tzolkin_pearls_continued_fraction=tuple(tzolkin_cf),
        tzolkin_pearls_convergents=tuple(tzolkin_conv),
        pentagram_lock_verified=pentagram_lock,
        pearls_tzolkin_lcm=pearls_tzolkin_lcm,
        grand_harmonic_lcm_days=grand_lcm,
        stern_brocot_venus_108=sb_venus_108,
        stern_brocot_tzolkin_12=sb_tzolkin_12,
        stern_brocot_tzolkin_20=sb_tzolkin_20,
        stern_brocot_tzolkin_108=sb_tzolkin_108,
    )


def execute_synodic_harvest_protocol() -> Dict[str, object]:
    """
    Execute an end-to-end coupled verification uniting Pillar I, Pillar II,
    and Pillar III.
    """
    oracle_reports: List[Union[Fraction, int]] = [
        -(10 ** 9),
        12,
        12,
        12,
        12,
        12,
        10 ** 9,
    ]
    consensus = byzantine_rational_consensus(oracle_reports, 2)
    scale_factor = consensus["exact_median"]

    base_game = build_persephone_demeter_convex_game()
    scaled_game: CharacteristicFnExact = {
        c: val * scale_factor for c, val in base_game.items()
    }
    shapley_alloc = compute_exact_shapley_values(4, scaled_game)
    core_props = verify_cooperative_game_properties(
        4, scaled_game, shapley_alloc
    )

    total_seeds = int(scaled_game[frozenset(range(4))])
    player_seeds = [int(shapley_alloc[i]) for i in range(4)]

    master_blinding = 24680
    player_blindings = [3100, 4200, 5300, 6400]
    excess_blinding = master_blinding - sum(player_blindings)

    c_master = pedersen_commit(total_seeds, master_blinding)
    c_players = [
        pedersen_commit(player_seeds[i], player_blindings[i])
        for i in range(4)
    ]
    balance_ok = verify_pedersen_balance_conservation(
        [c_master], c_players, excess_blinding
    )

    schnorr_ok = True
    opening_ok = True
    batch_pks: List[Tuple[int, int]] = []
    batch_msgs: List[bytes] = []
    batch_proofs: List[SchnorrProof] = []

    for i in range(4):
        priv_key = (SACRED_PEARLS_COUNT * (i + 1) + player_seeds[i]) % CURVE_Q
        pub_key = ec_scalar_mul(priv_key, GENERATOR_G)
        msg = f"GUARDIAN_{i}_SEED_ALLOCATION_{player_seeds[i]}".encode("ascii")
        proof = schnorr_zk_prove(priv_key, msg)
        if pub_key is None or not schnorr_zk_verify(pub_key, msg, proof):
            schnorr_ok = False
        else:
            batch_pks.append(pub_key)
            batch_msgs.append(msg)
            batch_proofs.append(proof)
        open_proof = pedersen_opening_zk_prove(
            player_seeds[i], player_blindings[i], msg
        )
        if not pedersen_opening_zk_verify(c_players[i], msg, open_proof):
            opening_ok = False

    batch_ok = schnorr_zk_batch_verify(batch_pks, batch_msgs, batch_proofs)

    return {
        "consensus_scale_factor": scale_factor,
        "total_harvest_seeds": total_seeds,
        "player_seed_allocations": tuple(player_seeds),
        "core_properties": core_props,
        "pedersen_conservation_verified": balance_ok,
        "guardian_schnorr_proofs_verified": schnorr_ok and batch_ok,
        "guardian_opening_proofs_verified": opening_ok,
    }


def format_pilgrim_diagnostic_scroll() -> str:
    """
    Generate a serene, human-readable contemplative summary scroll uniting the
    7 Anchor Pearls of the Golden Pilgrim with the verified mathematical
    invariants of all three pillars.
    """
    resonance = analyze_seven_wisdoms_synodic_resonance()
    pearls = get_golden_pilgrim_pearl_compass()
    lines = [
        f"=== {BARYCENTER_SEAL} ===",
        f"Sacred Equation : {SACRED_EQUATION}",
        f"Compass Key 108 : {COMPASS_KEY_108}",
        f"Venus/Earth     : {resonance.venus_earth_exact_ratio} "
        f"-> CF {list(resonance.venus_earth_continued_fraction)}",
        f"Tzolkin/Pearls  : {resonance.tzolkin_pearls_exact_ratio} "
        f"-> CF {list(resonance.tzolkin_pearls_continued_fraction)}",
        f"Grand Cycle LCM : {resonance.grand_harmonic_lcm_days} days",
        "Anchor Pearls of the Golden Pilgrim:",
    ]
    for pearl in pearls:
        lines.append(
            f"  [Pearl #{pearl.index:03d}] {pearl.catalan_title} "
            f"({pearl.harmonic_ratio}) -> {pearl.mathematical_invariant}"
        )
    return "\n".join(lines)


# ==============================================================================
# SECTION 5: SELF-TEST & 30-MUTANT FORMAL INQUISITOR VERIFICATION HARNESS
# ==============================================================================


def _test_pillar_1_cooperative_games_and_byzantine() -> None:
    """
    Verify Pillar 1 across all player counts n in {1, 2, 3, 4, 5, 6} and
    Byzantine consensus sizes n in {1, 3, 5, 6, 7, 8, 13}.
    """
    # 0. Boundary n = 1 sovereign player game & n = 2 dyadic game
    game_n1: CharacteristicFnExact = {
        frozenset(): Fraction(0, 1),
        frozenset((0,)): Fraction(108, 7),
    }
    shapley_n1 = compute_exact_shapley_values(1, game_n1)
    assert shapley_n1 == {0: Fraction(108, 7)}
    assert verify_cooperative_game_properties(1, game_n1, shapley_n1) == {
        "is_superadditive": True,
        "is_convex": True,
        "is_in_core": True,
    }

    game_n2: CharacteristicFnExact = {
        frozenset(): Fraction(0, 1),
        frozenset((0,)): Fraction(3, 1),
        frozenset((1,)): Fraction(3, 1),
        frozenset((0, 1)): Fraction(10, 1),
    }
    shapley_n2 = compute_exact_shapley_values(2, game_n2)
    assert shapley_n2 == {0: Fraction(5, 1), 1: Fraction(5, 1)}
    assert verify_cooperative_game_properties(2, game_n2, shapley_n2) == {
        "is_superadditive": True,
        "is_convex": True,
        "is_in_core": True,
    }

    # 1. 4-player convex Persephone-Demeter game
    convex_game = build_persephone_demeter_convex_game()
    shapley_convex = compute_exact_shapley_values(4, convex_game)
    report_convex = verify_shapley_axioms(
        4, convex_game, shapley_values=shapley_convex
    )
    assert report_convex.all_axioms_verified is True
    assert report_convex.strong_monotonicity_verified is True
    assert report_convex.harsanyi_duality_verified is True
    assert report_convex.self_duality_verified is True
    assert (0, 1) in report_convex.symmetric_pairs_found
    assert shapley_convex[0] == shapley_convex[1]

    ledger_p0 = build_marginal_contribution_ledger(4, convex_game, 0)
    assert len(ledger_p0) == 8
    assert (
        sum((entry.weighted_contribution for entry in ledger_p0), Fraction(0, 1))
        == shapley_convex[0]
    )

    props_convex = verify_cooperative_game_properties(
        4, convex_game, shapley_convex
    )
    assert props_convex == {
        "is_superadditive": True,
        "is_convex": True,
        "is_in_core": True,
    }

    dividends_convex = compute_harsanyi_dividends(4, convex_game)
    assert dividends_convex[frozenset()] == Fraction(0, 1)
    dual_convex = compute_dual_game(4, convex_game)
    assert compute_exact_shapley_values(4, dual_convex) == shapley_convex

    weber_convex = verify_weber_marginal_worth_theorem(4, convex_game)
    assert weber_convex["permutation_count"] == 24
    assert weber_convex["barycenter_matches_shapley"] is True
    assert weber_convex["all_weber_vertices_in_core"] is True
    assert weber_convex["weber_core_iff_convex_verified"] is True

    bs_convex = verify_bondareva_shapley_balanced_bound(4, convex_game)
    assert bs_convex["canonical_balanced_inequality_satisfied"] is True

    # 2. 4-player Dummy Witness convex game & 5-player non-power-of-two game
    dummy_game = build_dummy_witness_convex_game()
    shapley_dummy = compute_exact_shapley_values(4, dummy_game)
    report_dummy = verify_shapley_axioms(
        4, dummy_game, shapley_values=shapley_dummy
    )
    assert report_dummy.all_axioms_verified is True
    assert 3 in report_dummy.dummy_players_found
    assert shapley_dummy[3] == Fraction(0, 1)
    assert shapley_dummy[0] == shapley_dummy[1]
    diag_dummy = compute_cooperative_game_diagnostics(
        4, dummy_game, shapley_dummy
    )
    assert diag_dummy.is_totally_positive is True
    assert diag_dummy.is_convex is True
    assert diag_dummy.is_superadditive is True
    assert diag_dummy.is_in_core is True

    weights_n5 = (2, 2, 3, 5, 0)
    game_n5: CharacteristicFnExact = {
        c: Fraction(sum(weights_n5[i] for i in c) ** 2, 1)
        for c in generate_powerset_coalitions(range(5))
    }
    shapley_n5 = compute_exact_shapley_values(5, game_n5)
    assert shapley_n5[0] == shapley_n5[1] and shapley_n5[4] == Fraction(0, 1)
    assert verify_cooperative_game_properties(5, game_n5, shapley_n5) == {
        "is_superadditive": True,
        "is_convex": True,
        "is_in_core": True,
    }

    # 3. 6-player upper-bound Eleusinian Sanctuary convex game (n = 6, 64 coalitions)
    game_n6 = build_six_player_eleusinian_sanctuary_game()
    shapley_n6 = compute_exact_shapley_values(6, game_n6)
    assert shapley_n6[0] == shapley_n6[1]
    assert shapley_n6[5] == Fraction(0, 1)
    assert verify_cooperative_game_properties(6, game_n6, shapley_n6) == {
        "is_superadditive": True,
        "is_convex": True,
        "is_in_core": True,
    }
    div_n6 = compute_harsanyi_dividends(6, game_n6)
    assert _fast_zeta_reconstruct_raw(6, div_n6) == game_n6

    # 4. 3-player non-superadditive game whose Core is empty
    empty_core_game = build_non_superadditive_empty_core_game()
    shapley_empty = compute_exact_shapley_values(3, empty_core_game)
    assert shapley_empty == {
        0: Fraction(4, 1),
        1: Fraction(4, 1),
        2: Fraction(4, 1),
    }
    props_empty = verify_cooperative_game_properties(
        3, empty_core_game, shapley_empty
    )
    assert props_empty == {
        "is_superadditive": False,
        "is_convex": False,
        "is_in_core": False,
    }
    weber_empty = verify_weber_marginal_worth_theorem(3, empty_core_game)
    assert weber_empty["barycenter_matches_shapley"] is True
    assert weber_empty["all_weber_vertices_in_core"] is False
    assert weber_empty["weber_core_iff_convex_verified"] is True

    bs_empty = verify_bondareva_shapley_balanced_bound(3, empty_core_game)
    assert bs_empty["canonical_balanced_inequality_satisfied"] is False
    assert bs_empty["max_canonical_balanced_worth"] == Fraction(15, 1)

    # 5. Byzantine rational consensus with n = 7, f = 2 (odd interior m = 3: 110, 112, 114)
    honest_interior = [
        Fraction(108, 1),
        Fraction(110, 1),
        Fraction(112, 1),
        Fraction(114, 1),
        Fraction(116, 1),
    ]
    baseline_reports: List[Union[Fraction, int]] = [
        Fraction(100, 1),
        *honest_interior,
        Fraction(120, 1),
    ]
    bipolar_corrupted: List[Union[Fraction, int]] = [
        Fraction(-(10 ** 9), 1),
        *honest_interior,
        Fraction(10 ** 9, 1),
    ]
    upper_corrupted: List[Union[Fraction, int]] = [
        Fraction(100, 1),
        *honest_interior[:-1],
        Fraction(10 ** 9, 1),
        Fraction(10 ** 9 + 7, 1),
    ]

    consensus_base = byzantine_rational_consensus(baseline_reports, 2)
    consensus_bipolar = byzantine_rational_consensus(bipolar_corrupted, 2)
    consensus_upper = byzantine_rational_consensus(upper_corrupted, 2)

    assert consensus_base == consensus_bipolar
    assert consensus_base == consensus_upper
    assert consensus_bipolar["trimmed_mean"] == Fraction(112, 1)
    assert consensus_bipolar["exact_median"] == Fraction(112, 1)
    assert consensus_bipolar["spread_after_trim"] == Fraction(4, 1)

    # Even interior m = 4 check (n = 8, f = 2) & non-power-of-two sizes (n = 1, 3, 5, 6, 13)
    even_res = byzantine_rational_consensus(
        [-(10 ** 9), 1, 10, 12, 15, 19, 100, 10 ** 9], 2
    )
    assert even_res["trimmed_mean"] == Fraction(56, 4)
    assert even_res["exact_median"] == Fraction(27, 2)
    assert even_res["spread_after_trim"] == Fraction(9, 1)

    zero_fault = byzantine_rational_consensus([Fraction(108, 5)], 0)
    assert zero_fault == {
        "trimmed_mean": Fraction(108, 5),
        "exact_median": Fraction(108, 5),
        "spread_after_trim": Fraction(0, 1),
    }
    assert byzantine_rational_consensus([10, 20, 30], 0)["exact_median"] == Fraction(20, 1)
    assert byzantine_rational_consensus([-999, 10, 20, 30, 999], 1)["trimmed_mean"] == Fraction(20, 1)
    assert byzantine_rational_consensus([-999, 10, 20, 30, 40, 999], 1)["exact_median"] == Fraction(25, 1)
    reports_n13: List[Union[Fraction, int]] = (
        [-(10 ** 9)] * 4 + [100, 102, 104, 106, 108] + [10 ** 9] * 4
    )
    assert byzantine_rational_consensus(reports_n13, 4) == {
        "trimmed_mean": Fraction(104, 1),
        "exact_median": Fraction(104, 1),
        "spread_after_trim": Fraction(8, 1),
    }


def _test_pillar_2_elliptic_curve_and_zero_knowledge() -> None:
    """
    Verify Pillar 2: curve & generator checks, RFC 6979 determinism, RFC 6962
    Merkle trees, Schnorr ZK proof & batch verification, Special Soundness,
    witness-bound Chaum-Pedersen ZK opening proof, and Pedersen balance
    conservation.
    """
    curve_checks = verify_curve_and_generators()
    assert all(curve_checks.values()), f"Curve checks failed: {curve_checks!r}"

    # Group law identities
    assert ec_add(None, GENERATOR_G) == GENERATOR_G
    assert ec_add(GENERATOR_G, None) == GENERATOR_G
    assert ec_add(GENERATOR_G, GENERATOR_G) == ec_double(GENERATOR_G)
    assert ec_add(GENERATOR_G, ec_negate(GENERATOR_G)) is None
    assert ec_scalar_mul(0, GENERATOR_G) is None
    assert ec_scalar_mul(-1, GENERATOR_G) == ec_negate(GENERATOR_G)
    assert ec_scalar_mul(CURVE_Q - 1, GENERATOR_G) == ec_negate(GENERATOR_G)
    assert ec_add(GENERATOR_G, GENERATOR_H) == ec_add(GENERATOR_H, GENERATOR_G)

    # RFC 6979 determinism & boundary keys 1 and CURVE_Q - 1 with empty b"" payload
    secret_key = 108260 % CURVE_Q
    message = b"PERSEPHONE_DEMETER_ELEUSIS_COVENANT_108"
    k1 = rfc6979_generate_k(secret_key, CURVE_Q, message)
    k2 = rfc6979_generate_k(secret_key, CURVE_Q, message)
    k_alt = rfc6979_generate_k(secret_key, CURVE_Q, message + b"_ALT")
    assert 1 <= k1 < CURVE_Q
    assert k1 == k2
    assert k1 != k_alt

    for boundary_sk in (1, CURVE_Q - 1):
        boundary_pk = ec_scalar_mul(boundary_sk, GENERATOR_G)
        assert boundary_pk is not None
        empty_proof = schnorr_zk_prove(boundary_sk, b"")
        assert schnorr_zk_verify(boundary_pk, b"", empty_proof) is True

    # Schnorr ZK prove, verify, batch verify (n = 0, 1, 2, 3, 5) & Special Soundness
    public_key = ec_scalar_mul(secret_key, GENERATOR_G)
    assert public_key is not None and is_on_curve(public_key)
    proof = schnorr_zk_prove(secret_key, message)
    envelope = SchnorrProofEnvelope(
        public_key=public_key,
        commitment_r=proof[0],
        challenge_e=proof[1],
        response_s=proof[2],
        message_sha256_hex=hashlib.sha256(message).hexdigest(),
    )
    assert (
        schnorr_zk_verify(public_key, message, envelope.to_proof_tuple())
        is True
    )
    assert schnorr_zk_verify(public_key, b"TAMPERED_MSG", proof) is False

    secret_key_2 = (secret_key + 108) % CURVE_Q
    public_key_2 = ec_scalar_mul(secret_key_2, GENERATOR_G)
    assert public_key_2 is not None
    message_2 = b"GUARDIAN_SECOND_WITNESS_260"
    proof_2 = schnorr_zk_prove(secret_key_2, message_2)
    assert schnorr_zk_batch_verify([], [], []) is False
    assert schnorr_zk_batch_verify([public_key], [message], [proof]) is True
    assert (
        schnorr_zk_batch_verify(
            [public_key, public_key_2], [message], [proof, proof_2]
        )
        is False
    )
    assert (
        schnorr_zk_batch_verify(
            [public_key, public_key_2],
            [message, message_2],
            [proof, proof_2],
        )
        is True
    )
    assert (
        schnorr_zk_batch_verify(
            [public_key, public_key_2],
            [message, b"WRONG"],
            [proof, proof_2],
        )
        is False
    )
    batch5_pks = [public_key, public_key_2, public_key, public_key_2, public_key]
    batch5_msgs = [message, message_2, message, message_2, message]
    batch5_proofs = [proof, proof_2, proof, proof_2, proof]
    assert (
        schnorr_zk_batch_verify(
            batch5_pks[:3], batch5_msgs[:3], batch5_proofs[:3]
        )
        is True
    )
    assert (
        schnorr_zk_batch_verify(batch5_pks, batch5_msgs, batch5_proofs) is True
    )

    soundness = verify_schnorr_special_soundness_algebra(
        secret_key, k1, proof[1], (proof[1] + 108) % CURVE_Q or 2
    )
    assert all(soundness.values())

    # Bilinear homomorphic linearity of pedersen_commit
    c_a = pedersen_commit(108, 260)
    c_b = pedersen_commit(584, 365)
    assert ec_add(c_a, c_b) == pedersen_commit(108 + 584, 260 + 365)
    assert ec_scalar_mul(7, c_a) == pedersen_commit(7 * 108, 7 * 260)

    # Homomorphic Pedersen conservation: 300 = 100 + 100 + 100 & 3-to-5 split
    c_in = pedersen_commit(300, 15000)
    c_outs = [
        pedersen_commit(100, 4100),
        pedersen_commit(100, 5200),
        pedersen_commit(100, 3300),
    ]
    excess_r = 15000 - (4100 + 5200 + 3300)
    assert (
        verify_pedersen_balance_conservation([c_in], c_outs, excess_r) is True
    )

    ins_3 = [
        pedersen_commit(100, 11),
        pedersen_commit(200, 22),
        pedersen_commit(300, 33),
    ]
    outs_5 = [
        pedersen_commit(50, 5),
        pedersen_commit(100, 10),
        pedersen_commit(120, 12),
        pedersen_commit(130, 13),
        pedersen_commit(200, 20),
    ]
    assert (
        verify_pedersen_balance_conservation(
            ins_3, outs_5, (11 + 22 + 33) - (5 + 10 + 12 + 13 + 20)
        )
        is True
    )

    # Zero-excess and negative-excess blinding conservation & identity C(0, 0) = None
    assert pedersen_commit(0, 0) is None
    assert verify_pedersen_balance_conservation([None], [None], 0) is True
    c_in_zero = pedersen_commit(300, 12000)
    c_outs_zero = [
        pedersen_commit(100, 4000),
        pedersen_commit(100, 4000),
        pedersen_commit(100, 4000),
    ]
    assert (
        verify_pedersen_balance_conservation([c_in_zero], c_outs_zero, 0)
        is True
    )
    c_in_neg = pedersen_commit(300, 5000)
    assert (
        verify_pedersen_balance_conservation(
            [c_in_neg], c_outs_zero, 5000 - 12000
        )
        is True
    )

    # Witness-bound Chaum-Pedersen ZK opening proof (including v = 0 Dummy Player)
    open_proof_1 = pedersen_opening_zk_prove(300, 15000, message)
    open_proof_2 = pedersen_opening_zk_prove(300, 25000, message)
    c_in_2 = pedersen_commit(300, 25000)
    assert pedersen_opening_zk_verify(c_in, message, open_proof_1) is True
    assert pedersen_opening_zk_verify(c_in_2, message, open_proof_2) is True
    assert pedersen_opening_zk_verify(c_outs[0], message, open_proof_1) is False
    assert open_proof_1[0] != open_proof_2[0]
    assert open_proof_1[2] != open_proof_2[2]

    c_zero_val = pedersen_commit(0, 7777)
    open_zero_val = pedersen_opening_zk_prove(0, 7777, b"DUMMY_WITNESS_ZERO")
    assert (
        pedersen_opening_zk_verify(
            c_zero_val, b"DUMMY_WITNESS_ZERO", open_zero_val
        )
        is True
    )


def _test_pillar_3_diophantine_and_synodic_resonance() -> None:
    """
    Verify Pillar 3: continued fraction bijection, determinant identity,
    Lagrange 2nd-kind & Stern-Brocot Farey 1st-kind optimality, SL_2(Z)
    factorization, Bezout parent identity, and 7-Wisdoms synodic resonance.
    """
    test_rationals = [
        Fraction(VENUS_SYNODIC_PERIOD_DAYS, EARTH_SOLAR_YEAR_DAYS),
        Fraction(MAYAN_TZOLKIN_DAYS, SACRED_PEARLS_COUNT),
        Fraction(SACRED_PEARLS_COUNT, MAYAN_TZOLKIN_DAYS),
        Fraction(355, 113),
        Fraction(377, 233),
        Fraction(610, 377),
        Fraction(-89, 55),
        Fraction(0, 1),
        Fraction(108, 1),
        Fraction(1, 7),
    ]
    for q_val in test_rationals:
        cf = rational_to_continued_fraction(q_val)
        reconstructed = continued_fraction_to_rational(cf)
        assert reconstructed == q_val
        convergents = convergents_of_continued_fraction(cf)
        assert convergents[-1] == q_val
        assert verify_lagrange_convergent_optimality(q_val) is True
        if q_val > Fraction(0, 1):
            path_str = stern_brocot_path_encoding(q_val)
            assert path_str == continued_fraction_to_stern_brocot_path(q_val)
            mat = stern_brocot_sl2z_matrix_from_path(path_str)
            (c_val, a_val), (d_val, b_val) = mat
            assert c_val * b_val - a_val * d_val == 1
            assert Fraction(a_val + c_val, b_val + d_val) == q_val
            p_num, q_den = q_val.numerator, q_val.denominator
            assert c_val * q_den - d_val * p_num == 1
            assert p_num * b_val - q_den * a_val == 1

    assert rational_to_continued_fraction(Fraction(377, 233)) == [1] * 11 + [2]
    assert rational_to_continued_fraction(Fraction(610, 377)) == [1] * 12 + [2]
    g_val, bezout_x, bezout_y = exact_extended_gcd(584, 365)
    assert g_val == 73
    assert 584 * bezout_x + 365 * bezout_y == 73

    resonance = analyze_seven_wisdoms_synodic_resonance()
    assert resonance.pentagram_lock_verified is True
    assert resonance.venus_earth_exact_ratio == Fraction(8, 5)
    assert resonance.venus_earth_continued_fraction == (1, 1, 1, 2)
    assert resonance.venus_earth_convergents == (
        Fraction(1, 1),
        Fraction(2, 1),
        Fraction(3, 2),
        Fraction(8, 5),
    )
    assert resonance.tzolkin_pearls_exact_ratio == Fraction(65, 27)
    assert resonance.tzolkin_pearls_continued_fraction == (2, 2, 2, 5)
    assert resonance.tzolkin_pearls_convergents == (
        Fraction(2, 1),
        Fraction(5, 2),
        Fraction(12, 5),
        Fraction(65, 27),
    )
    assert resonance.pearls_tzolkin_lcm == 7020

    sb_venus, trace_venus = trace_stern_brocot_mediants(
        VENUS_EARTH_SYNODIC_RATIO, SACRED_PEARLS_COUNT
    )
    assert sb_venus == resonance.stern_brocot_venus_108
    assert sb_venus["unimodular_determinant_verified"] is True
    assert sb_venus["best_lower"] == Fraction(3, 2)
    assert sb_venus["best_upper"] == Fraction(5, 3)
    assert sb_venus["best_approximant"] == Fraction(8, 5)
    assert all(step.unimodular_det == 1 for step in trace_venus)
    assert stern_brocot_path_encoding(Fraction(8, 5)) == "RLRL"
    assert (
        verify_stern_brocot_best_approximant_optimality(Fraction(8, 5), 4)
        is True
    )
    assert (
        verify_stern_brocot_best_approximant_optimality(Fraction(65, 27), 20)
        is True
    )
    assert (
        verify_stern_brocot_best_approximant_optimality(
            Fraction(10 ** 9 + 1, 10 ** 9), 10 ** 9
        )
        is True
    )

    sb_venus_4 = stern_brocot_best_approximants(Fraction(584, 365), 4)
    assert sb_venus_4["unimodular_determinant_verified"] is True
    assert sb_venus_4["best_lower"] == Fraction(3, 2)
    assert sb_venus_4["best_upper"] == Fraction(5, 3)
    assert sb_venus_4["best_approximant"] == Fraction(5, 3)

    sb_tz_12 = resonance.stern_brocot_tzolkin_12
    assert sb_tz_12["unimodular_determinant_verified"] is True
    assert sb_tz_12["best_lower"] == Fraction(12, 5)
    assert sb_tz_12["best_upper"] == Fraction(29, 12)
    assert sb_tz_12["best_approximant"] == Fraction(12, 5)

    sb_tz_20 = resonance.stern_brocot_tzolkin_20
    assert sb_tz_20["unimodular_determinant_verified"] is True
    assert sb_tz_20["best_lower"] == Fraction(12, 5)
    assert sb_tz_20["best_upper"] == Fraction(41, 17)
    assert sb_tz_20["best_approximant"] == Fraction(41, 17)

    sb_tz_108 = resonance.stern_brocot_tzolkin_108
    assert sb_tz_108["unimodular_determinant_verified"] is True
    assert sb_tz_108["best_lower"] == Fraction(12, 5)
    assert sb_tz_108["best_upper"] == Fraction(53, 22)
    assert sb_tz_108["best_approximant"] == Fraction(65, 27)

    sb_one = stern_brocot_best_approximants(Fraction(1, 1), 1)
    assert sb_one["unimodular_determinant_verified"] is True
    assert sb_one["best_approximant"] == Fraction(1, 1)

    sb_three = stern_brocot_best_approximants(Fraction(3, 1), 5)
    assert sb_three["unimodular_determinant_verified"] is True
    assert sb_three["best_lower"] == Fraction(2, 1)
    assert sb_three["best_approximant"] == Fraction(3, 1)

    harvest = execute_synodic_harvest_protocol()
    assert harvest["consensus_scale_factor"] == Fraction(12, 1)
    assert harvest["total_harvest_seeds"] == 4176
    assert harvest["core_properties"] == {
        "is_superadditive": True,
        "is_convex": True,
        "is_in_core": True,
    }
    assert harvest["pedersen_conservation_verified"] is True
    assert harvest["guardian_schnorr_proofs_verified"] is True
    assert harvest["guardian_opening_proofs_verified"] is True

    scroll = format_pilgrim_diagnostic_scroll()
    assert COMPASS_KEY_108 in scroll
    assert len(get_golden_pilgrim_pearl_compass()) == 7


def _test_adversarial_mutants() -> None:
    """
    Verify requirement (e): All 5 required adversarial mutant categories plus
    the 5 Supreme Tribunal 5 concrete code mutants (MUTANT-OBO-01, MUTANT-FPB-02,
    MUTANT-CBIT-03, MUTANT-WTS-04, MUTANT-TPN-05) and RFC 6962 second-preimage
    resistance across 30 formal mutant suites.
    """
    bad_float = float("1.5")

    # Mutant 1 & M6..M8 (Universal Type-First Precedence across 44 calls):
    type_error_calls: List[Callable[[], object]] = [
        lambda: compute_exact_shapley_values(True, {}),  # type: ignore[arg-type]
        lambda: compute_exact_shapley_values(
            1, {frozenset(): 0, frozenset((False,)): 5}
        ),
        lambda: compute_exact_shapley_values(
            1, {frozenset(): 0, frozenset((0,)): bad_float}  # type: ignore[dict-item]
        ),
        lambda: compute_exact_shapley_values(
            0, {frozenset(): bad_float}  # type: ignore[dict-item]
        ),
        lambda: verify_shapley_axioms(
            0, {frozenset(): 1}, shapley_values={0: bad_float}  # type: ignore[dict-item]
        ),
        lambda: verify_shapley_axioms(
            0, {frozenset(): 1}, additive_partner_fn={frozenset(): True}
        ),
        lambda: build_marginal_contribution_ledger(
            0, {frozenset(): 1}, True  # type: ignore[arg-type]
        ),
        lambda: compute_harsanyi_dividends(
            0, {frozenset(): bad_float}  # type: ignore[dict-item]
        ),
        lambda: compute_dual_game(0, {frozenset(): True}),
        lambda: verify_weber_marginal_worth_theorem(
            0, {frozenset(): bad_float}  # type: ignore[dict-item]
        ),
        lambda: verify_bondareva_shapley_balanced_bound(
            0, {frozenset(): bad_float}  # type: ignore[dict-item]
        ),
        lambda: exact_binomial(-1, True),  # type: ignore[arg-type]
        lambda: generate_powerset_coalitions(b"\x00\x01"),  # type: ignore[arg-type]
        lambda: generate_permutations_exact(b"\x00\x01"),  # type: ignore[arg-type]
        lambda: verify_cooperative_game_properties(
            True, {}, {}  # type: ignore[arg-type]
        ),
        lambda: verify_cooperative_game_properties(
            1, {frozenset(): 0, frozenset((0,)): 5}, {False: 5}
        ),
        lambda: verify_cooperative_game_properties(
            0, {frozenset(): 1}, {99: bad_float}  # type: ignore[dict-item]
        ),
        lambda: byzantine_rational_consensus([1, 2, 3, True], 1),
        lambda: byzantine_rational_consensus([bad_float, 2, 3, 4], 1),  # type: ignore[list-item]
        lambda: byzantine_rational_consensus([1, 2, 3, 4], False),
        lambda: byzantine_rational_consensus([bad_float], -1),  # type: ignore[list-item]
        lambda: byzantine_rational_consensus([True], -1),
        lambda: is_on_curve((1, True)),
        lambda: is_on_curve((bad_float, 12240)),  # type: ignore[arg-type]
        lambda: ec_add((0, 0), (1, True)),
        lambda: ec_scalar_mul(True, GENERATOR_G),
        lambda: ec_scalar_mul_jacobian(True, GENERATOR_G),
        lambda: rfc6979_generate_k(True, CURVE_Q, b"msg"),
        lambda: rfc6962_merkle_tree_head([True]),  # type: ignore[list-item]
        lambda: schnorr_zk_prove(True, b"msg"),
        lambda: schnorr_zk_verify(
            GENERATOR_G, b"msg", (GENERATOR_G, True, 1)
        ),
        lambda: schnorr_zk_batch_verify(
            [GENERATOR_G], [b"msg"], [(GENERATOR_G, True, 1)]
        ),
        lambda: verify_schnorr_special_soundness_algebra(
            0, 0, True, 1  # type: ignore[arg-type]
        ),
        lambda: pedersen_commit(100, False),
        lambda: pedersen_opening_zk_prove(100, True, b"msg"),
        lambda: verify_pedersen_balance_conservation(
            [GENERATOR_G], [GENERATOR_G], True
        ),
        lambda: verify_pedersen_balance_conservation(
            [], [True], 0  # type: ignore[list-item]
        ),
        lambda: verify_pedersen_balance_conservation(
            [bad_float], [], 0  # type: ignore[list-item]
        ),
        lambda: rational_to_continued_fraction(bad_float),  # type: ignore[arg-type]
        lambda: continued_fraction_to_rational([1, True]),
        lambda: stern_brocot_best_approximants(Fraction(8, 5), True),
        lambda: stern_brocot_best_approximants(bad_float, 0),  # type: ignore[arg-type]
        lambda: verify_stern_brocot_best_approximant_optimality(
            Fraction(0, 1), True
        ),
        lambda: stern_brocot_sl2z_matrix_from_path(True),  # type: ignore[arg-type]
    ]
    for call in type_error_calls:
        caught_type_error = False
        try:
            call()
        except TypeError:
            caught_type_error = True
        assert caught_type_error is True, "Mutant 1 (bool/float) not rejected!"

    # Mutant 2: Forged Schnorr `s` scalar (plus `e` challenge, `R` point, and batch)
    priv_x = 12345
    pub_p = ec_scalar_mul(priv_x, GENERATOR_G)
    assert pub_p is not None
    msg = b"DIAMOND_WHEEL_BARYCENTER_TRANSCRIPT"
    valid_r, valid_e, valid_s = schnorr_zk_prove(priv_x, msg)

    forged_s = (valid_s + 1) % CURVE_Q or 1
    assert schnorr_zk_verify(pub_p, msg, (valid_r, valid_e, forged_s)) is False
    assert schnorr_zk_verify(pub_p, msg, (valid_r, valid_e, 0)) is False
    assert schnorr_zk_verify(pub_p, msg, (valid_r, valid_e, CURVE_Q)) is False

    forged_e = (valid_e + 1) % CURVE_Q or 1
    assert schnorr_zk_verify(pub_p, msg, (valid_r, forged_e, valid_s)) is False
    doubled_r = ec_double(valid_r)
    assert doubled_r is not None
    assert schnorr_zk_verify(pub_p, msg, (doubled_r, valid_e, valid_s)) is False
    assert (
        schnorr_zk_batch_verify(
            [pub_p], [msg], [(valid_r, valid_e, forged_s)]
        )
        is False
    )

    # Mutant 3: Off-curve, point-at-infinity, and non-canonical coordinate attacks
    off_curve_pub = (GENERATOR_G[0], (GENERATOR_G[1] + 1) % CURVE_P)
    assert is_on_curve(off_curve_pub) is False
    assert (
        schnorr_zk_verify(off_curve_pub, msg, (valid_r, valid_e, valid_s))
        is False
    )
    assert (
        schnorr_zk_verify(None, msg, (valid_r, valid_e, valid_s))  # type: ignore[arg-type]
        is False
    )
    assert (
        schnorr_zk_verify(pub_p, msg, (None, valid_e, valid_s))  # type: ignore[arg-type]
        is False
    )
    non_canonical_pub = (pub_p[0] + CURVE_P, pub_p[1])
    assert is_on_curve(non_canonical_pub) is False
    assert (
        schnorr_zk_verify(non_canonical_pub, msg, (valid_r, valid_e, valid_s))
        is False
    )

    # Mutant 4: Non-conserving Pedersen commitment (300 != 100 + 100 + 101)
    c_in = pedersen_commit(300, 9000)
    c_out_1 = pedersen_commit(100, 3000)
    c_out_2 = pedersen_commit(100, 3000)
    c_out_inflated = pedersen_commit(101, 2000)
    excess_r = 9000 - (3000 + 3000 + 2000)
    assert (
        verify_pedersen_balance_conservation(
            [c_in], [c_out_1, c_out_2, c_out_inflated], excess_r
        )
        is False
    )
    assert verify_pedersen_balance_conservation([], [c_out_1], 0) is False
    assert (
        verify_pedersen_balance_conservation([off_curve_pub], [c_out_1], 0)
        is False
    )

    open_t, open_e, open_sv, open_sr = pedersen_opening_zk_prove(300, 9000, msg)
    assert (
        pedersen_opening_zk_verify(
            c_in, msg, (open_t, open_e, (open_sv + 1) % CURVE_Q, open_sr)
        )
        is False
    )
    assert (
        pedersen_opening_zk_verify(c_in, msg, (open_t, open_e, 0, open_sr))
        is False
    )
    assert (
        pedersen_opening_zk_verify(c_in, msg, (open_t, open_e, open_sv, 0))
        is False
    )

    # Mutant 5 & MUTANT-OBO-01: n < 3f + 1 off-by-one Byzantine boundary (n=6=3f, f=2; n=0, f=0)
    for bad_reports, bad_f in (
        ([], 0),
        ([1, 2, 3, 4, 5, 6], 2),
        ([1, 2, 3], -1),
    ):
        caught_byzantine = False
        try:
            byzantine_rational_consensus(bad_reports, max_byzantine_faults=bad_f)
        except ValueError:
            caught_byzantine = True
        assert caught_byzantine is True

    # MUTANT-FPB-02 (Flipped Prefix Byte in RFC 6979 steps b/c/d/f, Domain Tags & RFC 6962):
    qlen = CURVE_Q.bit_length()
    rolen = (qlen + 7) // 8
    h1_digest = hashlib.sha256(msg).digest()
    x_oct = _rfc6979_int2octets(priv_x, rolen)
    h1_oct = _rfc6979_bits2octets(h1_digest, CURVE_Q, qlen, rolen)

    def _sim_rfc6979_prefix(
        v_init_byte: bytes,
        k_init_byte: bytes,
        sep_d: bytes,
        sep_f: bytes,
    ) -> int:
        v_b = v_init_byte * 32
        k_b = k_init_byte * 32
        k_b = hmac.new(
            k_b, v_b + sep_d + x_oct + h1_oct, hashlib.sha256
        ).digest()
        v_b = hmac.new(k_b, v_b, hashlib.sha256).digest()
        k_b = hmac.new(
            k_b, v_b + sep_f + x_oct + h1_oct, hashlib.sha256
        ).digest()
        v_b = hmac.new(k_b, v_b, hashlib.sha256).digest()
        while True:
            v_b = hmac.new(k_b, v_b, hashlib.sha256).digest()
            cand = _rfc6979_bits2int(v_b, qlen)
            if 1 <= cand < CURVE_Q:
                return cand
            k_b = hmac.new(k_b, v_b + b"\x00", hashlib.sha256).digest()
            v_b = hmac.new(k_b, v_b, hashlib.sha256).digest()

    canonical_k = rfc6979_generate_k(priv_x, CURVE_Q, msg)
    assert canonical_k == _sim_rfc6979_prefix(
        b"\x01", b"\x00", b"\x00", b"\x01"
    )
    assert canonical_k != _sim_rfc6979_prefix(
        b"\x02", b"\x00", b"\x00", b"\x01"
    )
    assert canonical_k != _sim_rfc6979_prefix(
        b"\x01", b"\x01", b"\x00", b"\x01"
    )
    assert canonical_k != _sim_rfc6979_prefix(
        b"\x01", b"\x00", b"\x01", b"\x01"
    )
    assert canonical_k != _sim_rfc6979_prefix(
        b"\x01", b"\x00", b"\x00", b"\x00"
    )

    flipped_schnorr_tag = (
        bytes([SCHNORR_DOMAIN_TAG[0] ^ 0xFF]) + SCHNORR_DOMAIN_TAG[1:]
    )
    e_flipped_tag = _compute_schnorr_challenge(
        valid_r, pub_p, msg, domain_tag=flipped_schnorr_tag
    )
    s_flipped_tag = (canonical_k + e_flipped_tag * priv_x) % CURVE_Q
    assert (
        schnorr_zk_verify(pub_p, msg, (valid_r, e_flipped_tag, s_flipped_tag))
        is False
    )

    flipped_pedersen_tag = (
        bytes([PEDERSEN_OPENING_DOMAIN_TAG[0] ^ 0xFF])
        + PEDERSEN_OPENING_DOMAIN_TAG[1:]
    )
    assert c_in is not None
    e_ped_flipped = _compute_schnorr_challenge(
        open_t, c_in, msg, domain_tag=flipped_pedersen_tag
    )
    assert (
        pedersen_opening_zk_verify(
            c_in, msg, (open_t, e_ped_flipped, open_sv, open_sr)
        )
        is False
    )

    # RFC 6962 non-power-of-two tree sizes (n in {1, 2, 3, 5, 6, 7}) & splicing attack
    all_leaves = [f"GUARDIAN_{i}_LEAF".encode("ascii") for i in range(7)]
    for tree_sz in (1, 2, 3, 5, 6, 7):
        sub_leaves = all_leaves[:tree_sz]
        mth_root = rfc6962_merkle_tree_head(sub_leaves)
        for idx, leaf_data in enumerate(sub_leaves):
            proof_path = rfc6962_merkle_inclusion_proof(sub_leaves, idx)
            assert (
                rfc6962_verify_inclusion_proof(
                    leaf_data, idx, tree_sz, proof_path, mth_root
                )
                is True
            )
            assert (
                rfc6962_verify_inclusion_proof(
                    leaf_data + b"X", idx, tree_sz, proof_path, mth_root
                )
                is False
            )
            if tree_sz > 1:
                assert (
                    rfc6962_verify_inclusion_proof(
                        leaf_data,
                        (idx + 1) % tree_sz,
                        tree_sz,
                        proof_path,
                        mth_root,
                    )
                    is False
                )
                tampered_path = list(proof_path)
                tampered_path[0] = (
                    bytes([tampered_path[0][0] ^ 1]) + tampered_path[0][1:]
                )
                assert (
                    rfc6962_verify_inclusion_proof(
                        leaf_data, idx, tree_sz, tampered_path, mth_root
                    )
                    is False
                )

    h0 = rfc6962_merkle_leaf_hash(all_leaves[0])
    h1 = rfc6962_merkle_leaf_hash(all_leaves[1])
    assert (
        hmac.compare_digest(
            rfc6962_merkle_tree_head(all_leaves[:2]),
            rfc6962_merkle_tree_head([h0 + h1]),
        )
        is False
    )

    # MUTANT-CBIT-03 (Corrupted Bit in bits2int shift & single-bit XOR flips):
    all_ones_256 = b"\xff" * 32
    assert qlen == 17 and rolen == 3
    assert _rfc6979_bits2int(all_ones_256, qlen) == (1 << 17) - 1
    assert _rfc6979_bits2octets(all_ones_256, CURVE_Q, qlen, rolen) == (
        ((1 << 17) - 1) % CURVE_Q
    ).to_bytes(3, "big")

    s_bit_corrupted = (valid_s ^ 1) % CURVE_Q or 2
    e_bit_corrupted = (valid_e ^ 1) % CURVE_Q or 2
    msg_bit_corrupted = msg[:-1] + bytes([msg[-1] ^ 1])
    assert (
        schnorr_zk_verify(pub_p, msg, (valid_r, valid_e, s_bit_corrupted))
        is False
    )
    assert (
        schnorr_zk_verify(pub_p, msg, (valid_r, e_bit_corrupted, valid_s))
        is False
    )
    assert (
        schnorr_zk_verify(pub_p, msg_bit_corrupted, (valid_r, valid_e, valid_s))
        is False
    )
    assert (
        schnorr_zk_verify(
            pub_p, msg, ((valid_r[0] ^ 1, valid_r[1]), valid_e, valid_s)
        )
        is False
    )
    assert (
        pedersen_opening_zk_verify(
            c_in, msg, (open_t, open_e, open_sv ^ 1, open_sr)
        )
        is False
    )
    assert (
        pedersen_opening_zk_verify(
            c_in, msg, (open_t, open_e, open_sv, open_sr ^ 1)
        )
        is False
    )

    # MUTANT-WTS-04 (Wrong Tree Split on Stern-Brocot & Equidistant b=d=1 tie):
    sb_half_tie = stern_brocot_best_approximants(Fraction(3, 2), 1)
    assert sb_half_tie["unimodular_determinant_verified"] is True
    assert sb_half_tie["best_lower"] == Fraction(1, 1)
    assert sb_half_tie["best_upper"] == Fraction(2, 1)
    assert sb_half_tie["best_approximant"] == Fraction(1, 1)
    assert (
        verify_stern_brocot_best_approximant_optimality(Fraction(3, 2), 1)
        is True
    )

    canonical_venus_path = stern_brocot_path_encoding(Fraction(8, 5))
    assert canonical_venus_path == "RLRL"
    for split_idx in range(len(canonical_venus_path)):
        flipped_ch = "L" if canonical_venus_path[split_idx] == "R" else "R"
        mutated_path = (
            canonical_venus_path[:split_idx]
            + flipped_ch
            + canonical_venus_path[split_idx + 1 :]
        )
        (mc, ma), (md, mb) = stern_brocot_sl2z_matrix_from_path(mutated_path)
        assert Fraction(ma + mc, mb + md) != Fraction(8, 5)

    # MUTANT-TPN-05 (Tampered Proof Node: Rogue Simulator Nodes & Batch Zero-Sum):
    rogue_e = 108
    rogue_s = 260
    rogue_r = ec_add(
        ec_scalar_mul(rogue_s, GENERATOR_G),
        ec_negate(ec_scalar_mul(rogue_e, pub_p)),
    )
    assert rogue_r is not None and is_on_curve(rogue_r)
    assert ec_scalar_mul(rogue_s, GENERATOR_G) == ec_add(
        rogue_r, ec_scalar_mul(rogue_e, pub_p)
    )
    assert schnorr_zk_verify(pub_p, msg, (rogue_r, rogue_e, rogue_s)) is False

    rogue_t = ec_add(
        pedersen_commit(rogue_s, rogue_s),
        ec_negate(ec_scalar_mul(rogue_e, c_in)),
    )
    assert rogue_t is not None and is_on_curve(rogue_t)
    assert pedersen_commit(rogue_s, rogue_s) == ec_add(
        rogue_t, ec_scalar_mul(rogue_e, c_in)
    )
    assert (
        pedersen_opening_zk_verify(
            c_in, msg, (rogue_t, rogue_e, rogue_s, rogue_s)
        )
        is False
    )
    assert (
        pedersen_opening_zk_verify(
            c_in, msg_bit_corrupted, (open_t, open_e, open_sv, open_sr)
        )
        is False
    )

    priv_x2 = 23456
    pub_p2 = ec_scalar_mul(priv_x2, GENERATOR_G)
    assert pub_p2 is not None
    msg2 = b"SECOND_BATCH_TRANSCRIPT_NODE"
    valid_r2, valid_e2, valid_s2 = schnorr_zk_prove(priv_x2, msg2)
    s0_plus = (valid_s + 1) % CURVE_Q or 1
    s1_minus = (valid_s2 - 1) % CURVE_Q or 1
    assert (
        schnorr_zk_batch_verify(
            [pub_p, pub_p2],
            [msg, msg2],
            [(valid_r, valid_e, s0_plus), (valid_r2, valid_e2, s1_minus)],
        )
        is False
    )

    # Extended formal mutants (M9..M30)
    for dup_fn in (
        lambda: generate_powerset_coalitions([0, 0, 1]),
        lambda: generate_permutations_exact([0, 1, 1]),
    ):
        caught_dup = False
        try:
            dup_fn()
        except ValueError:
            caught_dup = True
        assert caught_dup is True

    for bad_n, bad_game in (
        (0, {}),
        (7, {}),
        (1, {frozenset(): Fraction(0, 1)}),
        (1, {frozenset(): Fraction(1, 1), frozenset((0,)): Fraction(2, 1)}),
    ):
        caught_game_val = False
        try:
            compute_exact_shapley_values(bad_n, bad_game)
        except ValueError:
            caught_game_val = True
        assert caught_game_val is True

    caught_neg_binom = False
    try:
        exact_binomial(-1, 0)
    except ValueError:
        caught_neg_binom = True
    assert caught_neg_binom is True

    sep_game = build_superadditive_non_convex_game()
    sep_props = verify_cooperative_game_properties(
        3, sep_game, {0: Fraction(1, 1), 1: Fraction(1, 1), 2: Fraction(1, 1)}
    )
    assert sep_props == {
        "is_superadditive": True,
        "is_convex": False,
        "is_in_core": True,
    }

    convex_game = build_persephone_demeter_convex_game()
    grand_v = convex_game[frozenset(range(4))]
    unfair_alloc = {
        0: grand_v,
        1: Fraction(0, 1),
        2: Fraction(0, 1),
        3: Fraction(0, 1),
    }
    unfair_props = verify_cooperative_game_properties(
        4, convex_game, unfair_alloc
    )
    assert unfair_props == {
        "is_superadditive": True,
        "is_convex": True,
        "is_in_core": False,
    }
    forged_shapley_report = verify_shapley_axioms(
        4, convex_game, shapley_values=unfair_alloc
    )
    assert forged_shapley_report.all_axioms_verified is False
    assert forged_shapley_report.strong_monotonicity_verified is False

    for invalid_cf in ([], [1, 0, 2], [1, -3, 2]):
        caught_cf = False
        try:
            continued_fraction_to_rational(invalid_cf)
        except ValueError:
            caught_cf = True
        assert caught_cf is True

    for bad_target, bad_den in (
        (Fraction(0, 1), 5),
        (Fraction(-3, 2), 5),
        (Fraction(8, 5), 0),
    ):
        caught_sb = False
        try:
            stern_brocot_best_approximants(bad_target, bad_den)
        except ValueError:
            caught_sb = True
        assert caught_sb is True

    caught_bad_path = False
    try:
        stern_brocot_sl2z_matrix_from_path("RLX")
    except ValueError:
        caught_bad_path = True
    assert caught_bad_path is True

    caught_long_path = False
    try:
        continued_fraction_to_stern_brocot_path(
            Fraction(10 ** 9, 1), max_path_length=1024
        )
    except ValueError:
        caught_long_path = True
    assert caught_long_path is True

    # Right-spine and left-spine SL_2(Z) leapfrog stress tests
    sb_huge_right = stern_brocot_best_approximants(Fraction(10 ** 12 + 1, 2), 5)
    assert sb_huge_right["unimodular_determinant_verified"] is True
    assert sb_huge_right["best_approximant"] == Fraction(10 ** 12 + 1, 2)

    sb_spine_turn = stern_brocot_best_approximants(Fraction(3999, 2), 1)
    assert sb_spine_turn["unimodular_determinant_verified"] is True
    assert sb_spine_turn["best_lower"] == Fraction(1999, 1)
    assert sb_spine_turn["best_upper"] == Fraction(2000, 1)
    assert sb_spine_turn["best_approximant"] == Fraction(1999, 1)

    sb_right_trunc = stern_brocot_best_approximants(Fraction(2000, 3), 2)
    assert sb_right_trunc["unimodular_determinant_verified"] is True
    assert sb_right_trunc["best_lower"] == Fraction(1333, 2)
    assert sb_right_trunc["best_upper"] == Fraction(667, 1)
    assert sb_right_trunc["best_approximant"] == Fraction(1333, 2)

    sb_tiny_left = stern_brocot_best_approximants(
        Fraction(1, 10 ** 9), 10 ** 9
    )
    assert sb_tiny_left["unimodular_determinant_verified"] is True
    assert sb_tiny_left["best_lower"] == Fraction(0, 1)
    assert sb_tiny_left["best_upper"] == Fraction(1, 10 ** 9 - 1)
    assert sb_tiny_left["best_approximant"] == Fraction(1, 10 ** 9)

    sb_interior_1 = stern_brocot_best_approximants(
        Fraction(10 ** 9 + 1, 10 ** 9), 10 ** 9
    )
    assert sb_interior_1["unimodular_determinant_verified"] is True
    assert sb_interior_1["best_lower"] == Fraction(1, 1)
    assert sb_interior_1["best_upper"] == Fraction(10 ** 9, 10 ** 9 - 1)
    assert sb_interior_1["best_approximant"] == Fraction(
        10 ** 9 + 1, 10 ** 9
    )

    sb_interior_2 = stern_brocot_best_approximants(
        Fraction(10 ** 9, 10 ** 9 + 1), 10 ** 9 + 1
    )
    assert sb_interior_2["unimodular_determinant_verified"] is True
    assert sb_interior_2["best_lower"] == Fraction(10 ** 9 - 1, 10 ** 9)
    assert sb_interior_2["best_upper"] == Fraction(1, 1)
    assert sb_interior_2["best_approximant"] == Fraction(
        10 ** 9, 10 ** 9 + 1
    )

    sb_trunc_run, trace_trunc = trace_stern_brocot_mediants(
        Fraction(1, 1999), 1000
    )
    assert sb_trunc_run["unimodular_determinant_verified"] is True
    assert sb_trunc_run["best_lower"] == Fraction(0, 1)
    assert sb_trunc_run["best_upper"] == Fraction(1, 1000)
    assert sb_trunc_run["best_approximant"] == Fraction(1, 1000)
    assert trace_trunc[-1].mediant == Fraction(1, 1000)

    sb_equidistant, trace_equi = trace_stern_brocot_mediants(
        Fraction(1, 2000), 1000
    )
    assert sb_equidistant["unimodular_determinant_verified"] is True
    assert sb_equidistant["best_lower"] == Fraction(0, 1)
    assert sb_equidistant["best_upper"] == Fraction(1, 1000)
    assert sb_equidistant["best_approximant"] == Fraction(0, 1)
    assert trace_equi[-1].mediant == Fraction(1, 1000)

    sb_nondiv, trace_nondiv = trace_stern_brocot_mediants(
        Fraction(2, 2001), 5000
    )
    assert sb_nondiv["unimodular_determinant_verified"] is True
    assert sb_nondiv["best_lower"] == Fraction(1, 1001)
    assert sb_nondiv["best_upper"] == Fraction(1, 1000)
    assert sb_nondiv["best_approximant"] == Fraction(2, 2001)
    assert trace_nondiv[-1].direction == "H"

    for bad_e1, bad_e2 in ((0, 789), (789, 0), (789, 789)):
        caught_soundness = False
        try:
            verify_schnorr_special_soundness_algebra(123, 456, bad_e1, bad_e2)
        except ValueError:
            caught_soundness = True
        assert caught_soundness is True


def run_self_tests() -> None:
    """
    Execute the complete formal verification suite across all three mathematical
    pillars and all 30 adversarial mutant suites.
    """
    _test_pillar_1_cooperative_games_and_byzantine()
    _test_pillar_2_elliptic_curve_and_zero_knowledge()
    _test_pillar_3_diophantine_and_synodic_resonance()
    _test_adversarial_mutants()

    resonance = analyze_seven_wisdoms_synodic_resonance()
    print(
        f"[LA QUINTAESSÈNCIA · 46TH SUPREME CROWN OK] {SACRED_EQUATION} | "
        f"Key: {COMPASS_KEY_108} | "
        f"Venus/Earth={resonance.venus_earth_exact_ratio} "
        f"CF={list(resonance.venus_earth_continued_fraction)} | "
        f"Tzolkin/Pearls={resonance.tzolkin_pearls_exact_ratio} "
        f"CF={list(resonance.tzolkin_pearls_continued_fraction)} | "
        f"All 3 Pillars, RFC 6962/6979 & 30 Adversarial Mutants verified."
    )


if __name__ == "__main__":
    run_self_tests()
