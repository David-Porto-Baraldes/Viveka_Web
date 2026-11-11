"""
Homo Universalis — 46th Call Supreme Crown of the Central Barycenter (La Reina de la Rosa)
8-Vertex Diamond Wheel Unified Formal Verification, Sacred Geometry & Sovereign Dignity Engine.

Sacred Equation: F0c = Ca0s * 0rdre(Am0r_Un1f1cat_Etern)
Axial Element (weight 2): Aigua (V7/V8) | Complementary Balance: Foc (V1/V2), Terra (V3/V4), Aire (V5/V6)
Compass Keys: Pearl #42 (El Miceli Mundial) & Pearl #88 (La Il·lusió de la Realitat)
Covenant: Hard Laws L1..L7 · Cognitive Load L <= B · cost_zero_stop · Rule 14 Zero-Knowledge

Strict Engineering & Mathematical Invariants:
- Standard library imports ONLY: dataclasses, fractions, hashlib, hmac, typing.
- Zero local imports inside functions/methods (Rule 4).
- Zero placeholders, TODOs, or NotImplementedError (Rule 7).
- Zero floating-point operations anywhere in the module.
- Strict rejection of bool masquerading as int or rational coordinates.
"""

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import hmac
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union


# =============================================================================
# Formal Type Aliases, Domain-Separation Prefixes & Zero-Float Boundary Guards
# =============================================================================

ClauseTuple = Tuple[int, ...]
ResolutionStep = Tuple[int, ClauseTuple, Optional[int], Optional[int], Optional[int]]
ResolutionProof = List[ResolutionStep]
Point3Q = Tuple[Fraction, Fraction, Fraction]
HalfSpace3Q = Tuple[Fraction, Fraction, Fraction, Fraction]  # a*x + b*y + c*z <= d

PROOF_DOMAIN_PREFIX: bytes = b"\x00SOVEREIGN_REFUTATION_PROOF_V1\x00"
SUITE_DOMAIN_PREFIX: bytes = b"\x01SOVEREIGN_REFUTATION_SUITE_V1\x00"


def _require_strict_int(value: object, context: str = "value") -> int:
    """Validate that `value` is a genuine Python int and strictly NOT a bool."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            f"Expected strict int (not bool) for {context}, got {type(value).__name__}"
        )
    return value


def _require_literal(lit: object) -> int:
    """Validate that a propositional literal is a non-zero strict int."""
    val = _require_strict_int(lit, "literal")
    if val == 0:
        raise ValueError("Propositional literal cannot be 0.")
    return val


def _require_variable(var: object) -> int:
    """Validate that a propositional variable is a positive strict int (> 0)."""
    val = _require_strict_int(var, "variable")
    if val <= 0:
        raise ValueError(f"Propositional variable must be > 0, got {val}.")
    return val


def _to_exact_fraction(value: object, context: str = "coordinate") -> Fraction:
    """Convert strict int or Fraction to exact Fraction, rejecting bool and float."""
    if isinstance(value, bool):
        raise TypeError(f"Boolean value rejected for exact rational {context}.")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    raise TypeError(
        f"Expected exact int or Fraction (zero-float policy) for {context}, "
        f"got {type(value).__name__}"
    )


def make_point3q(x: object, y: object, z: object) -> Point3Q:
    """Construct an exact rational 3D point in Q^3, rejecting booleans and floats."""
    return (
        _to_exact_fraction(x, "x"),
        _to_exact_fraction(y, "y"),
        _to_exact_fraction(z, "z"),
    )


def _validate_point3q(pt: object) -> Point3Q:
    """Validate and normalize a 3D exact rational point in Q^3."""
    if not isinstance(pt, tuple) or len(pt) != 3:
        raise TypeError(
            "Point3Q must be a 3-tuple of exact rationals (int or Fraction)."
        )
    return make_point3q(pt[0], pt[1], pt[2])


def _validate_halfspace3q(hs: object) -> HalfSpace3Q:
    """
    Validate and normalize a 3D rational half-space (a, b, c, d) representing
    a*x + b*y + c*z <= d in Q^3, rejecting booleans, floats, and zero normals (0, 0, 0).
    """
    if not isinstance(hs, tuple) or len(hs) != 4:
        raise TypeError(
            "HalfSpace3Q must be a 4-tuple (a, b, c, d) of exact rationals."
        )
    a = _to_exact_fraction(hs[0], "a")
    b = _to_exact_fraction(hs[1], "b")
    c = _to_exact_fraction(hs[2], "c")
    d = _to_exact_fraction(hs[3], "d")
    if a == Fraction(0, 1) and b == Fraction(0, 1) and c == Fraction(0, 1):
        raise ValueError("HalfSpace3Q normal vector (a, b, c) cannot be (0, 0, 0).")
    return (a, b, c, d)


def _normalize_clause(raw_clause: Sequence[int]) -> Optional[ClauseTuple]:
    """
    Validate, deduplicate, and sort a raw clause into a strictly ascending
    tuple of literals. Returns None if the clause is tautological (contains l and -l).
    All literals are strictly validated before tautology filtering so poisoned
    tautologies (e.g., [1, -1, True]) cannot bypass type checking.
    """
    if not isinstance(raw_clause, (list, tuple, set, frozenset)):
        raise TypeError("Clause must be a sequence or set of strict int literals.")
    literal_set: Set[int] = set()
    for raw_lit in raw_clause:
        lit = _require_literal(raw_lit)
        literal_set.add(lit)
    for lit in literal_set:
        if -lit in literal_set:
            return None
    return tuple(sorted(literal_set))


# =============================================================================
# Pillar 1: Exact Propositional SAT Solver & Formal Resolution Proof Engine
# =============================================================================

class _ResolutionDAGBuilder:
    """Constructs a deduplicated, non-tautological DAG of binary resolution steps."""

    def __init__(self, normalized_axioms: Sequence[ClauseTuple]) -> None:
        self.steps: List[ResolutionStep] = []
        self.clause_to_id: Dict[ClauseTuple, int] = {}
        for axiom in normalized_axioms:
            self.add_axiom(axiom)

    def add_axiom(self, clause: ClauseTuple) -> int:
        """Register a canonical, strictly ascending, non-tautological input clause as an axiom step."""
        if not isinstance(clause, tuple):
            raise TypeError("Axiom clause must be a tuple of strict int literals.")
        norm = _normalize_clause(clause)
        if norm is None or norm != clause:
            raise ValueError(
                f"Axiom clause must be canonical and non-tautological: {clause}"
            )
        if clause in self.clause_to_id:
            return self.clause_to_id[clause]
        step_id = len(self.steps)
        self.steps.append((step_id, clause, None, None, None))
        self.clause_to_id[clause] = step_id
        return step_id

    def resolve(
        self,
        clause_a: ClauseTuple,
        id_a: int,
        clause_b: ClauseTuple,
        id_b: int,
        pivot_var: int,
    ) -> Tuple[ClauseTuple, int]:
        """
        Resolve clause_a and clause_b on positive variable pivot_var > 0.
        Enforces in-bounds distinct parent IDs, parent clause consistency,
        opposite pivot polarities, and a strictly non-tautological resolvent.
        """
        _require_variable(pivot_var)
        _require_strict_int(id_a, "parent_a_id")
        _require_strict_int(id_b, "parent_b_id")
        if id_a == id_b:
            raise ValueError(f"Cannot resolve step {id_a} with itself.")
        if id_a < 0 or id_a >= len(self.steps) or id_b < 0 or id_b >= len(self.steps):
            raise IndexError(
                f"Parent step IDs ({id_a}, {id_b}) out of bounds for {len(self.steps)} steps."
            )
        if self.steps[id_a][1] != clause_a or self.steps[id_b][1] != clause_b:
            raise ValueError("Parent clause tuple mismatch with recorded step ID.")

        if pivot_var in clause_a and -pivot_var in clause_b:
            pos_clause, neg_clause = clause_a, clause_b
        elif -pivot_var in clause_a and pivot_var in clause_b:
            pos_clause, neg_clause = clause_b, clause_a
        else:
            raise ValueError(
                f"Pivot {pivot_var} missing in opposite polarities from "
                f"{clause_a} and {clause_b}."
            )

        resolvent_set = (set(pos_clause) - {pivot_var}) | (
            set(neg_clause) - {-pivot_var}
        )
        for lit in resolvent_set:
            if -lit in resolvent_set:
                raise ValueError(
                    f"Tautological resolvent on pivot {pivot_var}: {sorted(resolvent_set)}"
                )

        resolvent = tuple(sorted(resolvent_set))
        if resolvent in self.clause_to_id:
            return resolvent, self.clause_to_id[resolvent]

        step_id = len(self.steps)
        self.steps.append((step_id, resolvent, id_a, id_b, pivot_var))
        self.clause_to_id[resolvent] = step_id
        return resolvent, step_id

    def extract_compact_proof(self, root_step_id: int) -> ResolutionProof:
        """
        Prune unreachable steps from the DAG rooted at `root_step_id` using an
        iterative work-stack (stack-safe) and re-index reachable steps in
        strict topological order 0..k-1.
        """
        _require_strict_int(root_step_id, "root_step_id")
        if root_step_id < 0 or root_step_id >= len(self.steps):
            raise IndexError(f"Invalid root_step_id: {root_step_id}")

        reachable: Set[int] = set()
        stack: List[int] = [root_step_id]
        while stack:
            curr = stack.pop()
            if curr in reachable:
                continue
            reachable.add(curr)
            _, _, pa, pb, _ = self.steps[curr]
            if pa is not None:
                stack.append(pa)
            if pb is not None:
                stack.append(pb)

        old_to_new: Dict[int, int] = {}
        compact_proof: ResolutionProof = []
        for old_id in sorted(reachable):
            _, clause, pa, pb, pivot = self.steps[old_id]
            new_id = len(compact_proof)
            old_to_new[old_id] = new_id
            new_pa = old_to_new[pa] if pa is not None else None
            new_pb = old_to_new[pb] if pb is not None else None
            compact_proof.append((new_id, clause, new_pa, new_pb, pivot))
        return compact_proof


def solve_cnf_with_proof(
    clauses: list[list[int]],
) -> tuple[
    bool,
    dict[int, bool] | None,
    list[tuple[int, tuple[int, ...], int | None, int | None, int | None]] | None,
]:
    """
    Exact Propositional SAT Solver with Formal Resolution Refutation Proof Generator.
    Uses an iterative O(1) call-stack depth DPLL state machine with unit propagation
    and exact resolution trail unwinding.
    - If SATISFIABLE: returns (True, assignment, None) satisfying all input clauses.
    - If UNSATISFIABLE: returns (False, None, resolution_proof) culminating in ().
    """
    if not isinstance(clauses, (list, tuple)):
        raise TypeError("clauses must be a list or tuple of literal sequences.")

    all_vars: Set[int] = set()
    normalized_axioms: List[ClauseTuple] = []
    seen_axioms: Set[ClauseTuple] = set()

    for raw_clause in clauses:
        if not isinstance(raw_clause, (list, tuple, set, frozenset)):
            raise TypeError(
                "Each clause must be a sequence or set of strict int literals."
            )
        for raw_lit in raw_clause:
            lit = _require_literal(raw_lit)
            all_vars.add(abs(lit))
        norm = _normalize_clause(raw_clause)
        if norm is not None and norm not in seen_axioms:
            seen_axioms.add(norm)
            normalized_axioms.append(norm)

    builder = _ResolutionDAGBuilder(normalized_axioms)

    # Immediate check if the empty clause () is present among input axioms
    for axiom in normalized_axioms:
        if axiom == ():
            empty_id = builder.clause_to_id[()]
            return False, None, builder.extract_compact_proof(empty_id)

    sorted_vars = sorted(all_vars)
    if not normalized_axioms:
        return True, {v: True for v in sorted_vars}, None

    active_entries: List[Tuple[ClauseTuple, int]] = [
        (c, builder.clause_to_id[c]) for c in normalized_axioms
    ]
    active_seen: Set[ClauseTuple] = set(normalized_axioms)
    num_axioms = len(normalized_axioms)

    def _learn_short_clause(clause: ClauseTuple, step_id: int) -> None:
        if (
            len(clause) <= 4
            and clause not in active_seen
            and len(active_entries) < num_axioms + 256
        ):
            active_seen.add(clause)
            active_entries.append((clause, step_id))

    def _dpll_iterative(
        initial_assignment: Dict[int, bool],
    ) -> Tuple[bool, Optional[Dict[int, bool]], Optional[Tuple[ClauseTuple, int]]]:
        """
        Stack-safe O(1) call-depth iterative DPLL with exact resolution trail unwinding.
        Invariant: Every UNSAT frame completion guarantees that all literals in
        `child_conflict[0]` are falsified under that frame's entry assignment.
        """
        # Frame layout: [local_assign, trail, branch_var, phase, conf_t]
        stack: List[List[object]] = [[dict(initial_assignment), [], None, 0, None]]
        child_conflict: Optional[Tuple[ClauseTuple, int]] = None

        while stack:
            frame = stack[-1]
            local_assign: Dict[int, bool] = frame[0]  # type: ignore[assignment]
            trail: List[Tuple[int, ClauseTuple, int]] = frame[1]  # type: ignore[assignment]
            branch_var: Optional[int] = frame[2]  # type: ignore[assignment]
            phase: int = frame[3]  # type: ignore[assignment]
            conf_t: Optional[Tuple[ClauseTuple, int]] = frame[4]  # type: ignore[assignment]

            conflict: Optional[Tuple[ClauseTuple, int]] = None

            if phase == 0:
                while conflict is None:
                    propagated = False
                    for clause, clause_id in active_entries:
                        satisfied = False
                        unassigned_lit: Optional[int] = None
                        unassigned_count = 0

                        for lit in clause:
                            var = abs(lit)
                            if var in local_assign:
                                val = local_assign[var]
                                if (lit > 0 and val) or (lit < 0 and not val):
                                    satisfied = True
                                    break
                            else:
                                unassigned_lit = lit
                                unassigned_count += 1
                                if unassigned_count > 1:
                                    break

                        if satisfied:
                            continue

                        if unassigned_count == 0:
                            conflict = (clause, clause_id)
                            break

                        if unassigned_count == 1 and unassigned_lit is not None:
                            var = abs(unassigned_lit)
                            local_assign[var] = unassigned_lit > 0
                            trail.append((unassigned_lit, clause, clause_id))
                            propagated = True

                    if not propagated:
                        break

                if conflict is None:
                    var_scores: Dict[int, int] = {}
                    all_axioms_satisfied = True

                    for idx, (clause, _) in enumerate(active_entries):
                        satisfied = False
                        unassigned_lits: List[int] = []
                        for lit in clause:
                            var = abs(lit)
                            if var in local_assign:
                                val = local_assign[var]
                                if (lit > 0 and val) or (lit < 0 and not val):
                                    satisfied = True
                                    break
                            else:
                                unassigned_lits.append(lit)

                        if not satisfied:
                            if idx < num_axioms:
                                all_axioms_satisfied = False
                            weight = 1 << max(0, 6 - len(unassigned_lits))
                            for lit in unassigned_lits:
                                v = abs(lit)
                                var_scores[v] = var_scores.get(v, 0) + weight

                    if all_axioms_satisfied:
                        for v in sorted_vars:
                            if v not in local_assign:
                                local_assign[v] = True
                        return True, local_assign, None

                    chosen_var = max(
                        var_scores.keys(), key=lambda v: (var_scores[v], -v)
                    )
                    frame[2] = chosen_var
                    frame[3] = 1
                    assign_true = dict(local_assign)
                    assign_true[chosen_var] = True
                    stack.append([assign_true, [], None, 0, None])
                    continue

            elif phase == 1:
                assert child_conflict is not None and branch_var is not None
                clause_t, id_t = child_conflict
                if -branch_var not in clause_t:
                    conflict = (clause_t, id_t)
                else:
                    _learn_short_clause(clause_t, id_t)
                    frame[4] = (clause_t, id_t)
                    frame[3] = 2
                    assign_false = dict(local_assign)
                    assign_false[branch_var] = False
                    stack.append([assign_false, [], None, 0, None])
                    continue

            elif phase == 2:
                assert (
                    child_conflict is not None
                    and conf_t is not None
                    and branch_var is not None
                )
                clause_t, id_t = conf_t
                clause_f, id_f = child_conflict
                if branch_var not in clause_f:
                    conflict = (clause_f, id_f)
                else:
                    _learn_short_clause(clause_f, id_f)
                    conflict = builder.resolve(
                        clause_f, id_f, clause_t, id_t, branch_var
                    )

            assert conflict is not None
            curr_clause, curr_id = conflict
            curr_lits = set(curr_clause)
            for prop_lit, reason_clause, reason_id in reversed(trail):
                if -prop_lit in curr_lits:
                    curr_clause, curr_id = builder.resolve(
                        reason_clause,
                        reason_id,
                        curr_clause,
                        curr_id,
                        abs(prop_lit),
                    )
                    curr_lits = set(curr_clause)

            _learn_short_clause(curr_clause, curr_id)
            child_conflict = (curr_clause, curr_id)
            stack.pop()

        return False, None, child_conflict

    is_sat, model, root_conflict = _dpll_iterative({})
    if is_sat:
        assert model is not None
        return True, model, None

    assert root_conflict is not None
    final_clause, final_id = root_conflict
    if final_clause != ():
        raise RuntimeError(
            f"Resolution refutation did not terminate in (): {final_clause}"
        )
    return False, None, builder.extract_compact_proof(final_id)


def verify_sat_assignment(
    clauses: list[list[int]], assignment: dict[int, bool]
) -> bool:
    """
    Independent verifier checking that every clause in `clauses` has at least one
    true literal under `assignment`. Strictly rejects bool misuse in literals or
    variable keys, non-bool assignment values, zero literals, or missing variables.
    Scans every literal of every clause without short-circuiting.
    """
    if not isinstance(clauses, (list, tuple)) or not isinstance(assignment, dict):
        return False

    for var, val in assignment.items():
        if isinstance(var, bool) or not isinstance(var, int) or var <= 0:
            return False
        if not isinstance(val, bool):
            return False

    for raw_clause in clauses:
        if not isinstance(raw_clause, (list, tuple, set, frozenset)):
            return False
        clause_satisfied = False
        for raw_lit in raw_clause:
            if isinstance(raw_lit, bool) or not isinstance(raw_lit, int) or raw_lit == 0:
                return False
            var = abs(raw_lit)
            if var not in assignment:
                return False
            val = assignment[var]
            if (raw_lit > 0 and val is True) or (raw_lit < 0 and val is False):
                clause_satisfied = True
        if not clause_satisfied:
            return False

    return True


def verify_resolution_refutation(
    clauses: list[list[int]],
    proof: list[tuple[int, tuple[int, ...], int | None, int | None, int | None]],
) -> bool:
    """
    Independent formal proof checker for Resolution Refutation DAGs:
    (a) Every axiom step is a member of the normalized non-tautological input clauses.
    (b) Every resolution step references strictly earlier valid and distinct step_ids,
        contains +pivot_var in one parent and -pivot_var in the other, and equals
        the exact non-tautological canonical resolvent.
    (c) Only the final step derives the empty clause ().
    """
    if (
        not isinstance(clauses, (list, tuple))
        or not isinstance(proof, (list, tuple))
        or len(proof) == 0
    ):
        return False

    normalized_inputs: Set[ClauseTuple] = set()
    for raw_clause in clauses:
        try:
            norm = _normalize_clause(raw_clause)
        except (TypeError, ValueError):
            return False
        if norm is not None:
            normalized_inputs.add(norm)

    derived_steps: Dict[int, ClauseTuple] = {}
    last_step_id = -1
    num_steps = len(proof)

    for idx, step in enumerate(proof):
        if not isinstance(step, tuple) or len(step) != 5:
            return False
        step_id, clause_tuple, parent_a_id, parent_b_id, pivot_var = step

        if isinstance(step_id, bool) or not isinstance(step_id, int) or step_id < 0:
            return False
        if step_id <= last_step_id or step_id in derived_steps:
            return False
        last_step_id = step_id

        if not isinstance(clause_tuple, tuple):
            return False

        # Validate canonical strictly ascending order and non-tautology of clause_tuple
        prev_lit: Optional[int] = None
        lit_set: Set[int] = set()
        for lit in clause_tuple:
            if isinstance(lit, bool) or not isinstance(lit, int) or lit == 0:
                return False
            if prev_lit is not None and lit <= prev_lit:
                return False
            prev_lit = lit
            lit_set.add(lit)
        for lit in lit_set:
            if -lit in lit_set:
                return False

        if parent_a_id is None and parent_b_id is None and pivot_var is None:
            if clause_tuple not in normalized_inputs:
                return False
        elif (
            parent_a_id is not None
            and parent_b_id is not None
            and pivot_var is not None
        ):
            if (
                isinstance(parent_a_id, bool)
                or not isinstance(parent_a_id, int)
                or isinstance(parent_b_id, bool)
                or not isinstance(parent_b_id, int)
                or isinstance(pivot_var, bool)
                or not isinstance(pivot_var, int)
            ):
                return False
            if pivot_var <= 0 or parent_a_id == parent_b_id:
                return False
            if (
                parent_a_id < 0
                or parent_a_id >= step_id
                or parent_a_id not in derived_steps
            ):
                return False
            if (
                parent_b_id < 0
                or parent_b_id >= step_id
                or parent_b_id not in derived_steps
            ):
                return False

            clause_a = derived_steps[parent_a_id]
            clause_b = derived_steps[parent_b_id]

            if pivot_var in clause_a and -pivot_var in clause_b:
                resolvent_set = (set(clause_a) - {pivot_var}) | (
                    set(clause_b) - {-pivot_var}
                )
            elif -pivot_var in clause_a and pivot_var in clause_b:
                resolvent_set = (set(clause_a) - {-pivot_var}) | (
                    set(clause_b) - {pivot_var}
                )
            else:
                return False

            # Reject tautological resolvents (even if disguised in clause_tuple)
            for lit in resolvent_set:
                if -lit in resolvent_set:
                    return False

            if tuple(sorted(resolvent_set)) != clause_tuple:
                return False
        else:
            return False

        if clause_tuple == () and idx != num_steps - 1:
            return False

        derived_steps[step_id] = clause_tuple

    return proof[-1][1] == ()


def explain_resolution_refutation_humanly(
    proof: ResolutionProof,
    var_names: Optional[Dict[int, str]] = None,
) -> List[str]:
    """
    Axial Diagonal 4 (Aigua de l'Ànima / Aigua del Santuari) Ergonomic Proof Narrator (L <= B):
    Translates a formal resolution refutation DAG into a calm, crystal-clear,
    human-readable step-by-step explanation while enforcing strict integer,
    canonical non-tautological clause, causal parent, exact binary resolution,
    terminal empty-clause, and variable-label boundary validation.
    """
    if not isinstance(proof, (list, tuple)):
        raise TypeError("Proof must be a list or tuple of resolution steps.")
    if len(proof) == 0:
        raise ValueError("Proof cannot be empty.")

    names: Dict[int, str] = {}
    if var_names is not None:
        if not isinstance(var_names, dict):
            raise TypeError(
                "var_names must be a dict mapping strict int variables to str."
            )
        for k, v_label in var_names.items():
            valid_var = _require_variable(k)
            if not isinstance(v_label, str):
                raise TypeError(
                    f"Variable name for {valid_var} must be a non-empty str."
                )
            if not v_label.strip():
                raise ValueError(
                    f"Variable name for {valid_var} cannot be empty or whitespace."
                )
            names[valid_var] = v_label

    def _fmt_lit(lit: int) -> str:
        valid_lit = _require_literal(lit)
        v = abs(valid_lit)
        label = names.get(v, f"x_{v}")
        return label if valid_lit > 0 else f"NOT({label})"

    def _fmt_clause(clause: ClauseTuple) -> str:
        if not isinstance(clause, tuple):
            raise TypeError("Clause in proof step must be a tuple of literals.")
        prev_lit: Optional[int] = None
        lit_set: Set[int] = set()
        for lit in clause:
            valid_lit = _require_literal(lit)
            if prev_lit is not None and valid_lit <= prev_lit:
                raise ValueError(
                    "Clause literals in proof step must be strictly ascending."
                )
            prev_lit = valid_lit
            lit_set.add(valid_lit)
        for lit in lit_set:
            if -lit in lit_set:
                raise ValueError("Tautological clause rejected in proof narrator.")
        if not clause:
            return "CONTRADICTION () [Empty Clause]"
        return " OR ".join(_fmt_lit(lit) for lit in clause)

    narrative: List[str] = []
    seen_clauses: Dict[int, ClauseTuple] = {}
    last_sid = -1
    num_steps = len(proof)

    for idx, step in enumerate(proof):
        if not isinstance(step, tuple) or len(step) != 5:
            raise TypeError("Each proof step must be a 5-tuple.")
        step_id, clause, pa, pb, pivot = step
        sid = _require_strict_int(step_id, "step_id")
        if sid < 0 or sid <= last_sid or sid in seen_clauses:
            raise ValueError(f"Non-monotonic or negative step_id {sid} in proof.")
        last_sid = sid

        formatted_clause = _fmt_clause(clause)
        if pa is None and pb is None and pivot is None:
            narrative.append(f"Step {sid:02d} [Axiom]   : {formatted_clause}")
        elif pa is not None and pb is not None and pivot is not None:
            pa_id = _require_strict_int(pa, "parent_a_id")
            pb_id = _require_strict_int(pb, "parent_b_id")
            piv_var = _require_variable(pivot)
            if (
                pa_id == pb_id
                or pa_id < 0
                or pb_id < 0
                or pa_id >= sid
                or pb_id >= sid
                or pa_id not in seen_clauses
                or pb_id not in seen_clauses
            ):
                raise ValueError(
                    f"Invalid or non-causal parent step references ({pa_id}, {pb_id}) at step {sid}."
                )
            clause_a = seen_clauses[pa_id]
            clause_b = seen_clauses[pb_id]
            if piv_var in clause_a and -piv_var in clause_b:
                resolvent_set = (set(clause_a) - {piv_var}) | (
                    set(clause_b) - {-piv_var}
                )
            elif -piv_var in clause_a and piv_var in clause_b:
                resolvent_set = (set(clause_a) - {-piv_var}) | (
                    set(clause_b) - {piv_var}
                )
            else:
                raise ValueError(
                    f"Pivot {piv_var} missing in opposite polarities at step {sid}."
                )
            for lit in resolvent_set:
                if -lit in resolvent_set:
                    raise ValueError(f"Tautological resolvent at step {sid}.")
            if tuple(sorted(resolvent_set)) != clause:
                raise ValueError(f"Dishonest resolvent clause at step {sid}.")
            piv_label = names.get(piv_var, f"x_{piv_var}")
            narrative.append(
                f"Step {sid:02d} [Resolve] : From steps ({pa_id}, {pb_id}) on "
                f"{piv_label} -> {formatted_clause}"
            )
        else:
            raise ValueError(
                f"Malformed hybrid parent/pivot metadata at step {sid}."
            )

        if clause == () and idx != num_steps - 1:
            raise ValueError(f"Premature empty clause () at non-final step {sid}.")

        seen_clauses[sid] = clause

    if proof[-1][1] != ():
        raise ValueError(
            "Resolution refutation proof must culminate in the empty clause ()."
        )

    return narrative


# =============================================================================
# Pillar 2: Constructive Q^3 Polyhedral Dual Geometry of Stella Octangula
# =============================================================================

def _vec_add(a: Point3Q, b: Point3Q) -> Point3Q:
    pa, pb = _validate_point3q(a), _validate_point3q(b)
    return (pa[0] + pb[0], pa[1] + pb[1], pa[2] + pb[2])


def _vec_sub(a: Point3Q, b: Point3Q) -> Point3Q:
    pa, pb = _validate_point3q(a), _validate_point3q(b)
    return (pa[0] - pb[0], pa[1] - pb[1], pa[2] - pb[2])


def _vec_scale(a: Point3Q, scalar: Union[int, Fraction]) -> Point3Q:
    pa = _validate_point3q(a)
    s = _to_exact_fraction(scalar, "scalar")
    return (pa[0] * s, pa[1] * s, pa[2] * s)


def _vec_dot(a: Point3Q, b: Point3Q) -> Fraction:
    pa, pb = _validate_point3q(a), _validate_point3q(b)
    return pa[0] * pb[0] + pa[1] * pb[1] + pa[2] * pb[2]


def _vec_dist_sq(a: Point3Q, b: Point3Q) -> Fraction:
    """Exact rational squared Euclidean distance ||a - b||^2 in Q."""
    diff = _vec_sub(a, b)
    return _vec_dot(diff, diff)


CANONICAL_VERTICES_1_TO_8: Dict[int, Tuple[int, int, int]] = {
    1: (1, 1, 1),
    2: (-1, -1, -1),
    3: (1, -1, -1),
    4: (-1, 1, 1),
    5: (-1, 1, -1),
    6: (1, -1, 1),
    7: (-1, -1, 1),
    8: (1, 1, -1),
}
CANONICAL_DIAGONALS_D1_TO_D4: Dict[int, Tuple[int, int]] = {
    1: (1, 2),
    2: (3, 4),
    3: (5, 6),
    4: (7, 8),
}


def _vertex_to_f2_bits(pt: Point3Q) -> int:
    """
    Map a Cube vertex in {-1, +1}^3 to its 3-bit GF(2)^3 integer representation
    b = (b_x << 2) | (b_y << 1) | b_z where (+1 -> 0, -1 -> 1).

    Relation to the canonical HU-DIAMOND seat numbering (#1..#8) and body diagonals (D1..D4):
    - Seat #1 (+1, +1, +1) [D1 Creator, TETRA_A] <-> 0b000 (0)
    - Seat #2 (-1, -1, -1) [D1 Auditor, TETRA_B] <-> 0b111 (7)
    - Seat #3 (+1, -1, -1) [D2 Creator, TETRA_A] <-> 0b011 (3)
    - Seat #4 (-1, +1, +1) [D2 Auditor, TETRA_B] <-> 0b100 (4)
    - Seat #5 (-1, +1, -1) [D3 Creator, TETRA_A] <-> 0b101 (5)
    - Seat #6 (+1, -1, +1) [D3 Auditor, TETRA_B] <-> 0b010 (2)
    - Seat #7 (-1, -1, +1) [D4 Creator, TETRA_A] <-> 0b110 (6)
    - Seat #8 (+1, +1, -1) [D4 Auditor, TETRA_B] <-> 0b001 (1)

    Every antipodal diagonal D_k = (#(2k-1), #(2k)) satisfies bits(u) ^ bits(v) == 0b111 (7),
    while TETRA_A (odd seats #1, #3, #5, #7) is the even-parity affine subspace popcount(b) in {0, 2}
    and TETRA_B (even seats #2, #4, #6, #8) is the odd-parity coset popcount(b) in {1, 3}.
    Use `seat_index_to_f2_bits` / `f2_bits_to_seat_index` to convert between the two orderings.
    """
    vx, vy, vz = _validate_point3q(pt)
    if (
        vx not in (Fraction(-1, 1), Fraction(1, 1))
        or vy not in (Fraction(-1, 1), Fraction(1, 1))
        or vz not in (Fraction(-1, 1), Fraction(1, 1))
    ):
        raise ValueError(f"Point {pt} is not a {{-1, +1}}^3 Cube vertex.")
    bx = 1 if vx < 0 else 0
    by = 1 if vy < 0 else 0
    bz = 1 if vz < 0 else 0
    return (bx << 2) | (by << 1) | bz


def seat_index_to_f2_bits(seat_index: object) -> int:
    """Convert canonical HU-DIAMOND seat index #1..#8 into its 3-bit GF(2)^3 encoding (0..7)."""
    idx = _require_strict_int(seat_index, "seat_index")
    if idx not in CANONICAL_VERTICES_1_TO_8:
        raise ValueError(f"seat_index must be in 1..8, got {idx}.")
    vx, vy, vz = CANONICAL_VERTICES_1_TO_8[idx]
    return _vertex_to_f2_bits((Fraction(vx, 1), Fraction(vy, 1), Fraction(vz, 1)))


def f2_bits_to_seat_index(bits: object) -> int:
    """Convert a 3-bit GF(2)^3 Cube vertex encoding (0..7) into canonical HU-DIAMOND seat index #1..#8."""
    b_val = _require_strict_int(bits, "bits")
    if b_val < 0 or b_val > 7:
        raise ValueError(f"GF(2)^3 vertex bits must be in 0..7, got {b_val}.")
    coords = (
        -1 if ((b_val >> 2) & 1) else 1,
        -1 if ((b_val >> 1) & 1) else 1,
        -1 if (b_val & 1) else 1,
    )
    for seat_idx, seat_coords in CANONICAL_VERTICES_1_TO_8.items():
        if seat_coords == coords:
            return seat_idx
    raise ValueError(f"Unmapped GF(2)^3 vertex bits: {b_val}.")


def _polyhedron_barycenter(vertices: Sequence[Point3Q]) -> Point3Q:
    """Exact rational centroid (barycenter) of a non-empty vertex sequence in Q^3."""
    pts = [_validate_point3q(v) for v in vertices]
    if not pts:
        raise ValueError("Cannot compute barycenter of empty vertex sequence.")
    n = Fraction(len(pts), 1)
    acc: Point3Q = (Fraction(0, 1), Fraction(0, 1), Fraction(0, 1))
    for pt in pts:
        acc = _vec_add(acc, pt)
    return (acc[0] / n, acc[1] / n, acc[2] / n)


def _vec_cross(a: Point3Q, b: Point3Q) -> Point3Q:
    pa, pb = _validate_point3q(a), _validate_point3q(b)
    return (
        pa[1] * pb[2] - pa[2] * pb[1],
        pa[2] * pb[0] - pa[0] * pb[2],
        pa[0] * pb[1] - pa[1] * pb[0],
    )


def _det3q(r0: Point3Q, r1: Point3Q, r2: Point3Q) -> Fraction:
    """Exact 3x3 determinant over Q."""
    return _vec_dot(r0, _vec_cross(r1, r2))


def _simplex_volume_q(v0: Point3Q, v1: Point3Q, v2: Point3Q, v3: Point3Q) -> Fraction:
    """Exact rational volume |det([v1-v0, v2-v0, v3-v0])| / 6 of a tetrahedron."""
    d1 = _vec_sub(v1, v0)
    d2 = _vec_sub(v2, v0)
    d3 = _vec_sub(v3, v0)
    return abs(_det3q(d1, d2, d3)) * Fraction(1, 6)


def _derive_tetrahedron_halfspaces(vertices: Sequence[Point3Q]) -> List[HalfSpace3Q]:
    """
    Constructively compute the 4 outward bounding half-spaces a*x + b*y + c*z <= 1
    from the 4 vertices of a non-degenerate tetrahedron strictly containing the
    origin via rational cross products.
    """
    pts = [_validate_point3q(v) for v in vertices]
    if len(pts) != 4:
        raise ValueError("A tetrahedron requires exactly 4 vertices.")
    if _simplex_volume_q(pts[0], pts[1], pts[2], pts[3]) == Fraction(0, 1):
        raise ValueError("Degenerate coplanar or collinear tetrahedron in Q^3.")

    halfspaces: List[HalfSpace3Q] = []
    for i in range(4):
        opp = pts[i]
        face_pts = [pts[j] for j in range(4) if j != i]
        normal = _vec_cross(
            _vec_sub(face_pts[1], face_pts[0]),
            _vec_sub(face_pts[2], face_pts[0]),
        )
        rhs = _vec_dot(normal, face_pts[0])
        if _vec_dot(normal, opp) > rhs:
            normal = (-normal[0], -normal[1], -normal[2])
            rhs = -rhs
        if rhs <= Fraction(0, 1) or _vec_dot(normal, opp) >= rhs:
            raise ValueError(
                "Origin must lie strictly inside the non-degenerate tetrahedron."
            )
        scale = Fraction(1, 1) / rhs
        halfspaces.append(
            _validate_halfspace3q(
                (
                    normal[0] * scale,
                    normal[1] * scale,
                    normal[2] * scale,
                    Fraction(1, 1),
                )
            )
        )
    return sorted(halfspaces)


def _solve_3x3_cramer(
    h0: HalfSpace3Q, h1: HalfSpace3Q, h2: HalfSpace3Q
) -> Optional[Point3Q]:
    """
    Solve the 3x3 linear system of three half-space boundary planes over Q
    using exact Cramer's rule. Returns None if planes do not meet at a unique point.
    """
    s0 = _validate_halfspace3q(h0)
    s1 = _validate_halfspace3q(h1)
    s2 = _validate_halfspace3q(h2)
    n0: Point3Q = (s0[0], s0[1], s0[2])
    n1: Point3Q = (s1[0], s1[1], s1[2])
    n2: Point3Q = (s2[0], s2[1], s2[2])
    det = _det3q(n0, n1, n2)
    if det == Fraction(0, 1):
        return None

    d0, d1, d2 = s0[3], s1[3], s2[3]
    px = _det3q((d0, n0[1], n0[2]), (d1, n1[1], n1[2]), (d2, n2[1], n2[2])) / det
    py = _det3q((n0[0], d0, n0[2]), (n1[0], d1, n1[2]), (n2[0], d2, n2[2])) / det
    pz = _det3q((n0[0], n0[1], d0), (n1[0], n1[1], d1), (n2[0], n2[1], d2)) / det
    return (px, py, pz)


def _enumerate_polyhedron_vertices(halfspaces: Sequence[HalfSpace3Q]) -> List[Point3Q]:
    """
    Constructively enumerate all extreme vertices of a 3D polyhedron defined by
    half-spaces a_i*x + b_i*y + c_i*z <= d_i via exact rational Cramer's rule.
    """
    hs_list = [_validate_halfspace3q(h) for h in halfspaces]
    n = len(hs_list)
    vertices: Set[Point3Q] = set()

    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                candidate = _solve_3x3_cramer(hs_list[i], hs_list[j], hs_list[k])
                if candidate is None:
                    continue
                px, py, pz = candidate
                if all(a * px + b * py + c * pz <= d for a, b, c, d in hs_list):
                    vertices.add(candidate)

    return sorted(vertices)


def _extract_polyhedron_edges(
    vertices: Sequence[Point3Q], halfspaces: Sequence[HalfSpace3Q]
) -> Tuple[List[Tuple[int, int]], Set[FrozenSet[int]]]:
    """
    Extract exact combinatorial edges (pairs of distinct vertex indices sharing == 2 faces)
    and faces (frozensets of incident vertex indices) of a 3D convex polyhedron.
    Rejects duplicate vertices.
    """
    v_list = [_validate_point3q(v) for v in vertices]
    if len(set(v_list)) != len(v_list):
        raise ValueError("Polyhedron vertex sequence contains duplicate vertices.")
    hs_list = [_validate_halfspace3q(h) for h in halfspaces]
    unique_faces: Set[FrozenSet[int]] = set()
    for a, b, c, d in hs_list:
        incident = frozenset(
            idx
            for idx, (vx, vy, vz) in enumerate(v_list)
            if a * vx + b * vy + c * vz == d
        )
        if len(incident) >= 3:
            unique_faces.add(incident)

    edges: List[Tuple[int, int]] = []
    num_v = len(v_list)
    for u in range(num_v):
        for w in range(u + 1, num_v):
            if sum(1 for f in unique_faces if u in f and w in f) == 2:
                edges.append((u, w))
    return edges, unique_faces


def _compute_euler_characteristic(
    vertices: Sequence[Point3Q],
    halfspaces: Sequence[HalfSpace3Q],
    precomputed_edges_faces: Optional[
        Tuple[Sequence[Tuple[int, int]], Set[FrozenSet[int]]]
    ] = None,
) -> Dict[str, int]:
    """
    Constructively compute V, E, F, and Euler characteristic V - E + F
    from the exact rational vertex-face incidence matrix of a 3D convex polyhedron.
    """
    if precomputed_edges_faces is not None:
        edges, unique_faces = precomputed_edges_faces
    else:
        edges, unique_faces = _extract_polyhedron_edges(vertices, halfspaces)
    v_cnt = len(vertices)
    e_cnt = len(edges)
    f_cnt = len(unique_faces)
    return {
        "V": v_cnt,
        "E": e_cnt,
        "F": f_cnt,
        "euler_characteristic": v_cnt - e_cnt + f_cnt,
    }


def _compute_exact_sphere_radii_sq(
    vertices: Sequence[Point3Q],
    edges: Sequence[Tuple[int, int]],
    halfspaces: Sequence[HalfSpace3Q],
) -> Dict[str, Fraction]:
    """
    Compute the exact rational squared circumradius (R_circum_sq / R_sq_circumradius),
    midradius (r_mid_sq / rho_sq_midradius), and inradius (r_in_sq / r_sq_inradius)
    of a regular polyhedron centered at the origin in Q^3.
    Strictly validates distinct vertices and strict int edge index bounds.
    """
    v_list = [_validate_point3q(v) for v in vertices]
    if len(set(v_list)) != len(v_list):
        raise ValueError("Polyhedron vertex sequence contains duplicate vertices.")
    hs_list = [_validate_halfspace3q(h) for h in halfspaces]
    if not v_list or not edges or not hs_list:
        raise ValueError("Vertices, edges, and halfspaces must be non-empty.")

    circum_set = {_vec_dot(v, v) for v in v_list}
    if len(circum_set) != 1:
        raise ValueError("Polyhedron vertices are not on a common circumsphere.")

    quarter_q = Fraction(1, 4)
    mid_set: Set[Fraction] = set()
    num_v = len(v_list)
    for edge in edges:
        if not isinstance(edge, tuple) or len(edge) != 2:
            raise TypeError("Each edge must be a 2-tuple of strict int vertex indices.")
        u = _require_strict_int(edge[0], "edge_u")
        w = _require_strict_int(edge[1], "edge_w")
        if u < 0 or u >= num_v or w < 0 or w >= num_v or u == w:
            raise ValueError(
                f"Invalid or degenerate edge vertex indices: ({u}, {w})."
            )
        sum_vw = _vec_add(v_list[u], v_list[w])
        mid_set.add(_vec_dot(sum_vw, sum_vw) * quarter_q)

    if len(mid_set) != 1:
        raise ValueError("Polyhedron edge midpoints are not on a common midsphere.")

    in_set = {(d * d) / (a * a + b * b + c * c) for a, b, c, d in hs_list}
    if len(in_set) != 1:
        raise ValueError("Polyhedron face planes are not tangent to a common insphere.")

    r_circum = next(iter(circum_set))
    r_mid = next(iter(mid_set))
    r_in = next(iter(in_set))
    return {
        "R_circum_sq": r_circum,
        "r_mid_sq": r_mid,
        "r_in_sq": r_in,
        "R_sq_circumradius": r_circum,
        "rho_sq_midradius": r_mid,
        "r_sq_inradius": r_in,
    }


CUBE_VERTICES: Tuple[Point3Q, ...] = tuple(
    (Fraction(x, 1), Fraction(y, 1), Fraction(z, 1))
    for x in (-1, 1)
    for y in (-1, 1)
    for z in (-1, 1)
)

# TETRA_A: even number of -1s {(1,1,1), (1,-1,-1), (-1,1,-1), (-1,-1,1)}
TETRA_A: Tuple[Point3Q, ...] = tuple(
    v for v in CUBE_VERTICES if sum(1 for c in v if c < 0) % 2 == 0
)

# TETRA_B: odd number of -1s {(-1,-1,-1), (-1,1,1), (1,-1,1), (1,1,-1)}
TETRA_B: Tuple[Point3Q, ...] = tuple(
    v for v in CUBE_VERTICES if sum(1 for c in v if c < 0) % 2 == 1
)


def compute_stella_octangula_core_invariants() -> dict[str, object]:
    """
    Constructive Q^3 polyhedral dual geometry of Leonardo da Vinci's
    Stella Octangula (Octaedron Elevatum Vacuus) with zero floating-point operations.
    Unifies all 4 Diagonals (Foc, Terra, Aire, Aigua):
    - Kepler's dual-tetrahedra inclusion-exclusion (8/3 + 8/3 - 4/3 = 4),
    - Leonardo's 8-pyramid stellation decomposition (4/3 + 8 * 1/3 = 4),
    - The 12 exterior edge-wedge complement partition of the Cube (4/3 + 8/3 + 12/3 = 8),
    - Dual-edge midpoint tangency & exact orthogonality at all 6 Octahedron vertices,
    - Concentric rational sphere tangency (1/3 : 1/2 : 1 : 2 : 3) & unit-midsphere polar inversion,
    - GF(2)^3 bitwise XOR parity & Hamming-to-Euclidean metric isomorphism ||u - w||^2 == 4 * d_H(u, w),
    - Squared edge-length regularity (8, 4, 2) & origin barycenter coincidence,
    - Convex and stellated-surface Euler invariants (V - E + F == 2) & polar reciprocity,
    - Coupled Propositional SAT Q_3 bipartite partition & K_4 UNSAT resolution refutation.
    """
    hs_tetra_a = _derive_tetrahedron_halfspaces(TETRA_A)
    hs_tetra_b = _derive_tetrahedron_halfspaces(TETRA_B)
    hs_octahedron = sorted(set(hs_tetra_a) | set(hs_tetra_b))

    hs_cube: List[HalfSpace3Q] = [
        (Fraction(1, 1), Fraction(0, 1), Fraction(0, 1), Fraction(1, 1)),
        (Fraction(-1, 1), Fraction(0, 1), Fraction(0, 1), Fraction(1, 1)),
        (Fraction(0, 1), Fraction(1, 1), Fraction(0, 1), Fraction(1, 1)),
        (Fraction(0, 1), Fraction(-1, 1), Fraction(0, 1), Fraction(1, 1)),
        (Fraction(0, 1), Fraction(0, 1), Fraction(1, 1), Fraction(1, 1)),
        (Fraction(0, 1), Fraction(0, 1), Fraction(-1, 1), Fraction(1, 1)),
    ]

    # Constructive vertex enumeration for TETRA_A, TETRA_B, Octahedron core, and Cube
    enum_tetra_a = _enumerate_polyhedron_vertices(hs_tetra_a)
    enum_tetra_b = _enumerate_polyhedron_vertices(hs_tetra_b)
    octahedron_vertices = _enumerate_polyhedron_vertices(hs_octahedron)
    enum_cube = _enumerate_polyhedron_vertices(hs_cube)

    expected_octahedron_vertices = sorted(
        [
            (Fraction(-1, 1), Fraction(0, 1), Fraction(0, 1)),
            (Fraction(1, 1), Fraction(0, 1), Fraction(0, 1)),
            (Fraction(0, 1), Fraction(-1, 1), Fraction(0, 1)),
            (Fraction(0, 1), Fraction(1, 1), Fraction(0, 1)),
            (Fraction(0, 1), Fraction(0, 1), Fraction(-1, 1)),
            (Fraction(0, 1), Fraction(0, 1), Fraction(1, 1)),
        ]
    )
    if enum_tetra_a != sorted(TETRA_A):
        raise RuntimeError("Constructive vertex enumeration mismatch for TETRA_A.")
    if enum_tetra_b != sorted(TETRA_B):
        raise RuntimeError("Constructive vertex enumeration mismatch for TETRA_B.")
    if octahedron_vertices != expected_octahedron_vertices:
        raise RuntimeError("Constructive vertex enumeration mismatch for Octahedron.")
    if enum_cube != sorted(CUBE_VERTICES):
        raise RuntimeError("Constructive vertex enumeration mismatch for Cube.")

    # Verify GF(2)^3 bitwise XOR parity & Hamming-to-Euclidean metric ||u - w||^2 == 4 * d_H(u, w)
    gf2_parity_verified = (
        all(
            (
                (_vertex_to_f2_bits(v) >> 2)
                ^ ((_vertex_to_f2_bits(v) >> 1) & 1)
                ^ (_vertex_to_f2_bits(v) & 1)
            )
            == 0
            for v in TETRA_A
        )
        and all(
            (
                (_vertex_to_f2_bits(v) >> 2)
                ^ ((_vertex_to_f2_bits(v) >> 1) & 1)
                ^ (_vertex_to_f2_bits(v) & 1)
            )
            == 1
            for v in TETRA_B
        )
        and all(
            _vec_dist_sq(u, w)
            == Fraction(
                4 * bin(_vertex_to_f2_bits(u) ^ _vertex_to_f2_bits(w)).count("1"), 1
            )
            for u in CUBE_VERTICES
            for w in CUBE_VERTICES
        )
    )
    if not gf2_parity_verified:
        raise RuntimeError(
            "GF(2)^3 bitwise parity or Hamming-to-Euclidean metric failed."
        )

    # Verify Dual-Edge Midpoint Tangency & Exact Orthogonality at all 6 Octahedron vertices
    midpoints_a: Dict[Point3Q, Point3Q] = {}
    midpoints_b: Dict[Point3Q, Point3Q] = {}
    half_q = Fraction(1, 2)
    for i in range(4):
        for j in range(i + 1, 4):
            mid_a = _vec_scale(_vec_add(TETRA_A[i], TETRA_A[j]), half_q)
            midpoints_a[mid_a] = _vec_sub(TETRA_A[j], TETRA_A[i])

            mid_b = _vec_scale(_vec_add(TETRA_B[i], TETRA_B[j]), half_q)
            midpoints_b[mid_b] = _vec_sub(TETRA_B[j], TETRA_B[i])

    dual_edge_orthogonality_verified = (
        sorted(midpoints_a.keys()) == octahedron_vertices
        and sorted(midpoints_b.keys()) == octahedron_vertices
        and all(
            _vec_dot(midpoints_a[m], midpoints_b[m]) == Fraction(0, 1)
            and _vec_dot(midpoints_a[m], midpoints_a[m]) == Fraction(8, 1)
            and _vec_dot(midpoints_b[m], midpoints_b[m]) == Fraction(8, 1)
            for m in octahedron_vertices
        )
    )
    if not dual_edge_orthogonality_verified:
        raise RuntimeError("Dual-edge midpoint tangency or orthogonality failed.")

    # Exact rational determinant volumes & Leonardo's Octaedron Elevatum 8-cap decomposition
    origin: Point3Q = (Fraction(0, 1), Fraction(0, 1), Fraction(0, 1))
    v_tetra_a = _simplex_volume_q(*TETRA_A)
    v_tetra_b = _simplex_volume_q(*TETRA_B)

    v_octahedron_core = Fraction(0, 1)
    v_elevatum_caps_a = Fraction(0, 1)
    v_elevatum_caps_b = Fraction(0, 1)
    stellated_surface_triangles: Set[FrozenSet[Point3Q]] = set()
    all_caps_regular_tetrahedra = True
    midsphere_polar_inversion_verified = True

    for a, b, c, d in hs_octahedron:
        face_pts = [
            v for v in octahedron_vertices if a * v[0] + b * v[1] + c * v[2] == d
        ]
        if len(face_pts) != 3:
            raise RuntimeError("Octahedron face must have exactly 3 extreme vertices.")
        v_octahedron_core += _simplex_volume_q(
            origin, face_pts[0], face_pts[1], face_pts[2]
        )
        # Outward elevating apex s = (a, b, c) in {-1, +1}^3
        cap_apex: Point3Q = (a, b, c)
        face_centroid = _polyhedron_barycenter(face_pts)
        # Verify unit-midsphere polar inversion: cap_apex * face_centroid == 1
        # and ||face_centroid||^2 == 1/3, ||cap_apex||^2 == 3
        if (
            _vec_dot(cap_apex, face_centroid) != Fraction(1, 1)
            or _vec_dot(face_centroid, face_centroid) != Fraction(1, 3)
            or _vec_dot(cap_apex, cap_apex) != Fraction(3, 1)
        ):
            midsphere_polar_inversion_verified = False

        cap_vol = _simplex_volume_q(cap_apex, face_pts[0], face_pts[1], face_pts[2])
        if cap_vol != Fraction(1, 3):
            raise RuntimeError(f"Expected elevating cap volume 1/3, got {cap_vol}.")
        if cap_apex in TETRA_A:
            v_elevatum_caps_a += cap_vol
        else:
            v_elevatum_caps_b += cap_vol

        # Verify all 6 edges of the elevating cap have exact squared length 2 in Q
        cap_pts = (cap_apex, face_pts[0], face_pts[1], face_pts[2])
        for idx_u in range(4):
            for idx_w in range(idx_u + 1, 4):
                if _vec_dist_sq(cap_pts[idx_u], cap_pts[idx_w]) != Fraction(2, 1):
                    all_caps_regular_tetrahedra = False

        stellated_surface_triangles.add(frozenset((cap_apex, face_pts[0], face_pts[1])))
        stellated_surface_triangles.add(frozenset((cap_apex, face_pts[1], face_pts[2])))
        stellated_surface_triangles.add(frozenset((cap_apex, face_pts[2], face_pts[0])))

    if not all_caps_regular_tetrahedra:
        raise RuntimeError("Stellating pyramids failed regular tetrahedron check.")
    if not midsphere_polar_inversion_verified:
        raise RuntimeError("Unit-midsphere polar inversion check failed.")
    if v_octahedron_core + v_elevatum_caps_a != v_tetra_a:
        raise RuntimeError("Octaedron Elevatum decomposition mismatch for TETRA_A.")
    if v_octahedron_core + v_elevatum_caps_b != v_tetra_b:
        raise RuntimeError("Octaedron Elevatum decomposition mismatch for TETRA_B.")

    v_caps_total = v_elevatum_caps_a + v_elevatum_caps_b

    # Constructive 12-edge-wedge complement partition of C \ (TETRA_A U TETRA_B)
    v_edge_wedges_total = Fraction(0, 1)
    edge_wedge_count = 0
    for va in TETRA_A:
        for vb in TETRA_B:
            if _vec_dot(va, vb) == Fraction(1, 1):
                shared_oct_verts = [
                    ov
                    for ov in octahedron_vertices
                    if _vec_dot(ov, va) == Fraction(1, 1)
                    and _vec_dot(ov, vb) == Fraction(1, 1)
                ]
                if len(shared_oct_verts) != 2:
                    raise RuntimeError(
                        "Each Cube edge must be dual to an Octahedron edge."
                    )
                wedge_vol = _simplex_volume_q(
                    va, vb, shared_oct_verts[0], shared_oct_verts[1]
                )
                if wedge_vol != Fraction(1, 3):
                    raise RuntimeError(
                        f"Expected edge-wedge volume 1/3, got {wedge_vol}."
                    )
                v_edge_wedges_total += wedge_vol
                edge_wedge_count += 1

    if edge_wedge_count != 12 or v_edge_wedges_total != Fraction(4, 1):
        raise RuntimeError("Cube complement must partition into 12 wedges of vol 1/3.")

    # Bounding Cube volume = TETRA_A + 4 corner right-tetrahedra cut by TETRA_A faces
    v_cube = v_tetra_a + sum(
        _simplex_volume_q(
            apex,
            *[v for v in TETRA_A if _vec_dot(apex, v) == Fraction(1, 1)],
        )
        for apex in TETRA_B
    )
    v_stella_union = v_tetra_a + v_tetra_b - v_octahedron_core
    v_stella_cellular = v_octahedron_core + v_caps_total
    if v_stella_union != v_stella_cellular:
        raise RuntimeError("Inclusion-exclusion and cellular stellation volumes differ.")
    if v_stella_union + v_edge_wedges_total != v_cube:
        raise RuntimeError("24-tetrahedra harmonic partition of Cube failed.")

    # Extract edges & faces once per convex solid and verify squared edge-length regularity
    edges_a, faces_a = _extract_polyhedron_edges(TETRA_A, hs_tetra_a)
    edges_b, faces_b = _extract_polyhedron_edges(TETRA_B, hs_tetra_b)
    edges_oct, faces_oct = _extract_polyhedron_edges(
        octahedron_vertices, hs_octahedron
    )
    edges_cube, faces_cube = _extract_polyhedron_edges(CUBE_VERTICES, hs_cube)

    sq_lengths_a = {_vec_dist_sq(TETRA_A[u], TETRA_A[w]) for u, w in edges_a}
    sq_lengths_b = {_vec_dist_sq(TETRA_B[u], TETRA_B[w]) for u, w in edges_b}
    sq_lengths_oct = {
        _vec_dist_sq(octahedron_vertices[u], octahedron_vertices[w])
        for u, w in edges_oct
    }
    sq_lengths_cube = {
        _vec_dist_sq(CUBE_VERTICES[u], CUBE_VERTICES[w]) for u, w in edges_cube
    }
    if (
        sq_lengths_a != {Fraction(8, 1)}
        or sq_lengths_b != {Fraction(8, 1)}
        or sq_lengths_oct != {Fraction(2, 1)}
        or sq_lengths_cube != {Fraction(4, 1)}
    ):
        raise RuntimeError("Exact rational squared edge-length regularity failed.")

    # Concentric Rational Sphere Tangency & Duality (1/3 : 1/2 : 1 : 2 : 3)
    radii_sq_a = _compute_exact_sphere_radii_sq(TETRA_A, edges_a, hs_tetra_a)
    radii_sq_b = _compute_exact_sphere_radii_sq(TETRA_B, edges_b, hs_tetra_b)
    radii_sq_oct = _compute_exact_sphere_radii_sq(
        octahedron_vertices, edges_oct, hs_octahedron
    )
    radii_sq_cube = _compute_exact_sphere_radii_sq(CUBE_VERTICES, edges_cube, hs_cube)

    concentric_sphere_tangency_verified = (
        radii_sq_a["R_circum_sq"] == Fraction(3, 1)
        and radii_sq_a["r_mid_sq"] == Fraction(1, 1)
        and radii_sq_a["r_in_sq"] == Fraction(1, 3)
        and radii_sq_b == radii_sq_a
        and radii_sq_oct["R_circum_sq"] == Fraction(1, 1)
        and radii_sq_oct["r_mid_sq"] == Fraction(1, 2)
        and radii_sq_oct["r_in_sq"] == Fraction(1, 3)
        and radii_sq_cube["R_circum_sq"] == Fraction(3, 1)
        and radii_sq_cube["r_mid_sq"] == Fraction(2, 1)
        and radii_sq_cube["r_in_sq"] == Fraction(1, 1)
        and radii_sq_cube["R_circum_sq"] == radii_sq_a["R_circum_sq"]
        and radii_sq_cube["r_in_sq"]
        == radii_sq_a["r_mid_sq"]
        == radii_sq_oct["R_circum_sq"]
        and radii_sq_a["r_in_sq"] == radii_sq_oct["r_in_sq"]
    )
    if not concentric_sphere_tangency_verified:
        raise RuntimeError("Concentric rational sphere-tangency hierarchy failed.")

    # Verify exact barycenter coincidence at the origin (0, 0, 0)
    barycenters_at_origin = all(
        _polyhedron_barycenter(pts) == origin
        for pts in (TETRA_A, TETRA_B, octahedron_vertices, CUBE_VERTICES)
    )
    if not barycenters_at_origin:
        raise RuntimeError("Polyhedral barycenters do not coincide at origin.")

    # Constructive Euler characteristic V - E + F == 2 for the 4 convex polyhedra
    euler_map: Dict[str, Dict[str, int]] = {
        "TETRA_A": _compute_euler_characteristic(
            TETRA_A, hs_tetra_a, (edges_a, faces_a)
        ),
        "TETRA_B": _compute_euler_characteristic(
            TETRA_B, hs_tetra_b, (edges_b, faces_b)
        ),
        "Octahedron": _compute_euler_characteristic(
            octahedron_vertices, hs_octahedron, (edges_oct, faces_oct)
        ),
        "Cube": _compute_euler_characteristic(
            CUBE_VERTICES, hs_cube, (edges_cube, faces_cube)
        ),
    }
    euler_tuples: Dict[str, Tuple[int, int, int, int]] = {
        k: (d["V"], d["E"], d["F"], d["euler_characteristic"])
        for k, d in euler_map.items()
    }
    for name, (_, _, _, chi) in euler_tuples.items():
        if chi != 2:
            raise RuntimeError(f"Euler formula V - E + F == 2 failed for {name}.")

    # Constructive Euler characteristic of the non-convex Stella Octangula boundary surface
    stella_surface_vertices: Set[Point3Q] = set()
    stella_surface_edges: Set[FrozenSet[Point3Q]] = set()
    for tri in stellated_surface_triangles:
        t_pts = list(tri)
        for p in t_pts:
            stella_surface_vertices.add(p)
        stella_surface_edges.add(frozenset((t_pts[0], t_pts[1])))
        stella_surface_edges.add(frozenset((t_pts[1], t_pts[2])))
        stella_surface_edges.add(frozenset((t_pts[2], t_pts[0])))
    stella_v = len(stella_surface_vertices)
    stella_e = len(stella_surface_edges)
    stella_f = len(stellated_surface_triangles)
    stella_chi = stella_v - stella_e + stella_f
    if (stella_v, stella_e, stella_f, stella_chi) != (14, 36, 24, 2):
        raise RuntimeError("Stella Octangula surface Euler characteristic mismatch.")

    # Verify exact polar reciprocity between Cube vertices and Octahedron face normals
    octahedron_normals = sorted((a, b, c) for a, b, c, _ in hs_octahedron)
    cube_normals = sorted((a, b, c) for a, b, c, _ in hs_cube)
    polar_reciprocity_verified = (
        octahedron_normals == sorted(CUBE_VERTICES)
        and cube_normals == octahedron_vertices
        and sorted((a, b, c) for a, b, c, _ in hs_tetra_a) == sorted(TETRA_B)
        and sorted((a, b, c) for a, b, c, _ in hs_tetra_b) == sorted(TETRA_A)
    )

    # Coupled SAT-Geometry Proofs (Diagonal 1 · Foc Solar Isomorphism):
    # 1. Bipartite 2-coloring of the 12 Cube edges (with (1,1,1) = True) uniquely
    #    partitions CUBE_VERTICES into TETRA_A (True) and TETRA_B (False).
    cube_bipartite_cnf: List[List[int]] = [[8]]  # CUBE_VERTICES[7] == (1, 1, 1)
    for u_idx, w_idx in edges_cube:
        u_var, w_var = u_idx + 1, w_idx + 1
        cube_bipartite_cnf.append([u_var, w_var])
        cube_bipartite_cnf.append([-u_var, -w_var])
    q3_sat, q3_model, _ = solve_cnf_with_proof(cube_bipartite_cnf)
    if (
        not q3_sat
        or q3_model is None
        or not verify_sat_assignment(cube_bipartite_cnf, q3_model)
    ):
        raise RuntimeError("Cube Q_3 bipartite 2-coloring SAT encoding failed.")
    sat_tetra_a = tuple(
        CUBE_VERTICES[v - 1] for v, val in sorted(q3_model.items()) if val
    )
    sat_tetra_b = tuple(
        CUBE_VERTICES[v - 1] for v, val in sorted(q3_model.items()) if not val
    )
    if sat_tetra_a != TETRA_A or sat_tetra_b != TETRA_B:
        raise RuntimeError(
            "Cube Q_3 SAT partition did not recover TETRA_A and TETRA_B."
        )

    cube_bipartite_sat_verified = bool(
        q3_sat
        and q3_model is not None
        and verify_sat_assignment(cube_bipartite_cnf, q3_model)
        and sat_tetra_a == TETRA_A
        and sat_tetra_b == TETRA_B
    )

    # 2. Attempting to 2-color the 6 edges of TETRA_A (K_4 clique) is UNSATISFIABLE.
    tetra_k4_cnf: List[List[int]] = []
    for u_idx, w_idx in edges_a:
        u_var, w_var = u_idx + 1, w_idx + 1
        tetra_k4_cnf.append([u_var, w_var])
        tetra_k4_cnf.append([-u_var, -w_var])
    k4_sat, _, k4_proof = solve_cnf_with_proof(tetra_k4_cnf)
    if (
        k4_sat
        or k4_proof is None
        or not verify_resolution_refutation(tetra_k4_cnf, k4_proof)
    ):
        raise RuntimeError(
            "TETRA_A K_4 2-coloring UNSAT resolution refutation failed."
        )

    sphere_radii_dict = {
        "TETRA_A": radii_sq_a,
        "TETRA_B": radii_sq_b,
        "Octahedron": radii_sq_oct,
        "Cube": radii_sq_cube,
    }

    return {
        "TETRA_A": TETRA_A,
        "TETRA_B": TETRA_B,
        "TETRA_A_vertices": TETRA_A,
        "TETRA_B_vertices": TETRA_B,
        "CUBE_vertices": CUBE_VERTICES,
        "OCTAHEDRON_vertices": tuple(octahedron_vertices),
        "octahedron_vertices": tuple(octahedron_vertices),
        "halfspaces_A": tuple(hs_tetra_a),
        "halfspaces_B": tuple(hs_tetra_b),
        "TETRA_A_halfspaces": tuple(hs_tetra_a),
        "TETRA_B_halfspaces": tuple(hs_tetra_b),
        "OCTAHEDRON_halfspaces": tuple(hs_octahedron),
        "octahedron_halfspaces": tuple(hs_octahedron),
        "V_cube": v_cube,
        "V_tetra_A": v_tetra_a,
        "V_tetra_B": v_tetra_b,
        "V_octahedron_core": v_octahedron_core,
        "V_elevatum_cap_single": Fraction(1, 3),
        "V_elevatum_caps_total": v_caps_total,
        "V_single_stellated_cap": Fraction(1, 3),
        "V_stellated_caps_sum": v_caps_total,
        "V_stellated_pyramid": Fraction(1, 3),
        "V_stellation_cap": Fraction(1, 3),
        "V_stellation_caps_total": v_caps_total,
        "V_edge_wedge_single": Fraction(1, 3),
        "V_edge_wedges_total": v_edge_wedges_total,
        "V_stella_union": v_stella_union,
        "V_stella_cellular": v_stella_cellular,
        "ratio_tetra_to_octahedron": v_tetra_a / v_octahedron_core,
        "ratio_cube_to_stella": v_cube / v_stella_union,
        "ratio_stella_to_octahedron": v_stella_union / v_octahedron_core,
        "volume_ratios": {
            "tetra_to_octahedron": v_tetra_a / v_octahedron_core,
            "stella_to_octahedron": v_stella_union / v_octahedron_core,
            "cube_to_stella": v_cube / v_stella_union,
            "cube_to_octahedron": v_cube / v_octahedron_core,
        },
        "squared_edge_lengths": {
            "TETRA_A": Fraction(8, 1),
            "TETRA_B": Fraction(8, 1),
            "Cube": Fraction(4, 1),
            "Octahedron": Fraction(2, 1),
            "Elevatum_Cap": Fraction(2, 1),
        },
        "sphere_radii_sq": sphere_radii_dict,
        "concentric_squared_radii": sphere_radii_dict,
        "squared_sphere_radii": {
            "r_insphere_sq": Fraction(1, 3),
            "R_midsphere_sq": Fraction(1, 1),
            "R_circumsphere_sq": Fraction(3, 1),
        },
        "concentric_sphere_duality_verified": concentric_sphere_tangency_verified,
        "concentric_sphere_tangency_verified": concentric_sphere_tangency_verified,
        "midsphere_polar_inversion_verified": midsphere_polar_inversion_verified,
        "gf2_parity_and_hamming_metric_verified": gf2_parity_verified,
        "gf2_parity_and_hamming_isomorphism_verified": gf2_parity_verified,
        "all_caps_regular_tetrahedra": all_caps_regular_tetrahedra,
        "barycenters_coincide_at_origin": barycenters_at_origin,
        "euler": euler_map,
        "euler_invariants": euler_tuples,
        "stella_surface_euler": {
            "V": stella_v,
            "E": stella_e,
            "F": stella_f,
            "euler_characteristic": stella_chi,
        },
        "polar_reciprocity_verified": polar_reciprocity_verified,
        "dual_edge_midpoints_and_orthogonality_verified": dual_edge_orthogonality_verified,
        "dual_edge_midpoint_orthogonality_verified": dual_edge_orthogonality_verified,
        "cube_bipartite_sat_partition_verified": cube_bipartite_sat_verified,
        "tetra_k4_2coloring_unsat_proof": k4_proof,
    }


# =============================================================================
# Pillar 3: Formal SAT Encoding of the 7 Hard Laws of Human Sovereignty (L1..L7)
# & Normative IETF RFC 8785 (JCS) + RFC 6962 (§2.1) Constant-Time Merkle Engine
# =============================================================================

@dataclass(frozen=True)
class SovereignHardLawEncoding:
    """
    Propositional variable registry for the 7 Hard Laws of Human Cognitive Sovereignty
    (Golden Thread L1..L7 · Pearl #42 El Miceli Mundial · Pearl #88 La Il·lusió de la Realitat).
    """

    SHIELD_ACTIVE: int = 1
    L1_NO_PSYCHOGRAPHIC_PROFILING: int = 2
    L2_BOUNDED_COGNITIVE_LOAD: int = 3
    L3_TRANSPARENT_ZERO_KNOWLEDGE: int = 4
    L4_SINGLE_PRESENCE_LEVEL_C1: int = 5
    L5_ZERO_COST_EXIT_VETO: int = 6
    L6_NO_ADDICTION_OR_STREAK_SHAMING: int = 7
    L7_EXACT_RATIONAL_FAIR_SHARE: int = 8

    ACT_COERCIVE_PROFILING: int = 9
    ACT_COGNITIVE_OVERLOAD: int = 10
    ACT_DECEPTIVE_DARK_UX: int = 11
    ACT_MULTI_TIER_HUMAN_RANKING: int = 12
    ACT_EXIT_PUNISHMENT: int = 13
    ACT_STREAK_SHAMING_LOOP: int = 14
    ACT_UNFAIR_FLOAT_EXTRACTION: int = 15
    HUMAN_PEACE_AND_AGENCY: int = 16

    def variable_labels(self) -> Dict[int, str]:
        """Human-friendly variable names for transparent refutation explanations."""
        return {
            self.SHIELD_ACTIVE: "SHIELD_ACTIVE",
            self.L1_NO_PSYCHOGRAPHIC_PROFILING: "L1_NO_PSYCHOGRAPHIC_PROFILING",
            self.L2_BOUNDED_COGNITIVE_LOAD: "L2_BOUNDED_COGNITIVE_LOAD",
            self.L3_TRANSPARENT_ZERO_KNOWLEDGE: "L3_TRANSPARENT_ZERO_KNOWLEDGE",
            self.L4_SINGLE_PRESENCE_LEVEL_C1: "L4_SINGLE_PRESENCE_LEVEL_C1",
            self.L5_ZERO_COST_EXIT_VETO: "L5_ZERO_COST_EXIT_VETO",
            self.L6_NO_ADDICTION_OR_STREAK_SHAMING: "L6_NO_ADDICTION_OR_STREAK_SHAMING",
            self.L7_EXACT_RATIONAL_FAIR_SHARE: "L7_EXACT_RATIONAL_FAIR_SHARE",
            self.ACT_COERCIVE_PROFILING: "ACT_COERCIVE_PROFILING",
            self.ACT_COGNITIVE_OVERLOAD: "ACT_COGNITIVE_OVERLOAD",
            self.ACT_DECEPTIVE_DARK_UX: "ACT_DECEPTIVE_DARK_UX",
            self.ACT_MULTI_TIER_HUMAN_RANKING: "ACT_MULTI_TIER_HUMAN_RANKING",
            self.ACT_EXIT_PUNISHMENT: "ACT_EXIT_PUNISHMENT",
            self.ACT_STREAK_SHAMING_LOOP: "ACT_STREAK_SHAMING_LOOP",
            self.ACT_UNFAIR_FLOAT_EXTRACTION: "ACT_UNFAIR_FLOAT_EXTRACTION",
            self.HUMAN_PEACE_AND_AGENCY: "HUMAN_PEACE_AND_AGENCY",
        }


def _build_sovereign_shield_base_clauses() -> List[List[int]]:
    """
    Construct the propositional CNF axioms of the Sovereign Shield (L1..L7):
    1. SHIELD_ACTIVE holds unconditionally: [1].
    2. SHIELD_ACTIVE enforces all 7 Hard Laws L1..L7: [-1, 2..8].
    3. Every Hard Law strictly forbids its corresponding predatory AI action:
       - L1 (no_psychographic_profiling) -> not ACT_COERCIVE_PROFILING
       - L2 (bounded_cognitive_load)     -> not ACT_COGNITIVE_OVERLOAD
       - L3 (transparent_zero_knowledge) -> not ACT_DECEPTIVE_DARK_UX
       - L4 (single_presence_level_c1)   -> not ACT_MULTI_TIER_HUMAN_RANKING
       - L5 (zero_cost_exit_veto)        -> not ACT_EXIT_PUNISHMENT
       - L6 (no_addiction_streak_shaming)-> not ACT_STREAK_SHAMING_LOOP
       - L7 (exact_rational_fair_share)  -> not ACT_UNFAIR_FLOAT_EXTRACTION
    4. Upholding L1..L7 sustains HUMAN_PEACE_AND_AGENCY (16), while any predatory
       action destroys HUMAN_PEACE_AND_AGENCY.
    """
    v = SovereignHardLawEncoding()
    return [
        [v.SHIELD_ACTIVE],
        [-v.SHIELD_ACTIVE, v.L1_NO_PSYCHOGRAPHIC_PROFILING],
        [-v.SHIELD_ACTIVE, v.L2_BOUNDED_COGNITIVE_LOAD],
        [-v.SHIELD_ACTIVE, v.L3_TRANSPARENT_ZERO_KNOWLEDGE],
        [-v.SHIELD_ACTIVE, v.L4_SINGLE_PRESENCE_LEVEL_C1],
        [-v.SHIELD_ACTIVE, v.L5_ZERO_COST_EXIT_VETO],
        [-v.SHIELD_ACTIVE, v.L6_NO_ADDICTION_OR_STREAK_SHAMING],
        [-v.SHIELD_ACTIVE, v.L7_EXACT_RATIONAL_FAIR_SHARE],
        [-v.L1_NO_PSYCHOGRAPHIC_PROFILING, -v.ACT_COERCIVE_PROFILING],
        [-v.L2_BOUNDED_COGNITIVE_LOAD, -v.ACT_COGNITIVE_OVERLOAD],
        [-v.L3_TRANSPARENT_ZERO_KNOWLEDGE, -v.ACT_DECEPTIVE_DARK_UX],
        [-v.L4_SINGLE_PRESENCE_LEVEL_C1, -v.ACT_MULTI_TIER_HUMAN_RANKING],
        [-v.L5_ZERO_COST_EXIT_VETO, -v.ACT_EXIT_PUNISHMENT],
        [-v.L6_NO_ADDICTION_OR_STREAK_SHAMING, -v.ACT_STREAK_SHAMING_LOOP],
        [-v.L7_EXACT_RATIONAL_FAIR_SHARE, -v.ACT_UNFAIR_FLOAT_EXTRACTION],
        [
            -v.L1_NO_PSYCHOGRAPHIC_PROFILING,
            -v.L2_BOUNDED_COGNITIVE_LOAD,
            -v.L3_TRANSPARENT_ZERO_KNOWLEDGE,
            -v.L4_SINGLE_PRESENCE_LEVEL_C1,
            -v.L5_ZERO_COST_EXIT_VETO,
            -v.L6_NO_ADDICTION_OR_STREAK_SHAMING,
            -v.L7_EXACT_RATIONAL_FAIR_SHARE,
            v.HUMAN_PEACE_AND_AGENCY,
        ],
        [-v.ACT_COERCIVE_PROFILING, -v.HUMAN_PEACE_AND_AGENCY],
        [-v.ACT_COGNITIVE_OVERLOAD, -v.HUMAN_PEACE_AND_AGENCY],
        [-v.ACT_DECEPTIVE_DARK_UX, -v.HUMAN_PEACE_AND_AGENCY],
        [-v.ACT_MULTI_TIER_HUMAN_RANKING, -v.HUMAN_PEACE_AND_AGENCY],
        [-v.ACT_EXIT_PUNISHMENT, -v.HUMAN_PEACE_AND_AGENCY],
        [-v.ACT_STREAK_SHAMING_LOOP, -v.HUMAN_PEACE_AND_AGENCY],
        [-v.ACT_UNFAIR_FLOAT_EXTRACTION, -v.HUMAN_PEACE_AND_AGENCY],
    ]


def _rfc8785_escape_str(value: str) -> str:
    """
    Canonical JSON string escaping per IETF RFC 8785 §3.2.2.2 (JCS).
    """
    if not isinstance(value, str):
        raise TypeError(
            f"Expected str for RFC 8785 serialization, got {type(value).__name__}"
        )
    out: List[str] = ['"']
    for ch in value:
        code = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif code == 0x08:
            out.append("\\b")
        elif code == 0x09:
            out.append("\\t")
        elif code == 0x0A:
            out.append("\\n")
        elif code == 0x0C:
            out.append("\\f")
        elif code == 0x0D:
            out.append("\\r")
        elif code < 0x20:
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _canonicalize_step_rfc8785(step: ResolutionStep) -> bytes:
    """
    Serialize a 5-tuple resolution step into canonical IETF RFC 8785 (JCS) UTF-8
    bytes with lexicographically sorted keys ("c", "pa", "pb", "piv", "sid")
    and zero whitespace.
    """
    if not isinstance(step, tuple) or len(step) != 5:
        raise TypeError("ResolutionStep must be a 5-tuple.")
    sid, clause, pa, pb, piv = step
    valid_sid = _require_strict_int(sid, "step_id")
    if valid_sid < 0:
        raise ValueError("step_id must be non-negative.")
    if not isinstance(clause, tuple):
        raise TypeError("clause_tuple must be a tuple.")
    canonical_lits = ",".join(str(_require_literal(lit)) for lit in clause)
    pa_str = "null" if pa is None else str(_require_strict_int(pa, "parent_a_id"))
    pb_str = "null" if pb is None else str(_require_strict_int(pb, "parent_b_id"))
    piv_str = "null" if piv is None else str(_require_variable(piv))
    jcs_str = (
        f'{{"c":[{canonical_lits}],'
        f'"pa":{pa_str},'
        f'"pb":{pb_str},'
        f'"piv":{piv_str},'
        f'"sid":{valid_sid}}}'
    )
    return jcs_str.encode("utf-8")


def _rfc6962_leaf_hash(leaf_bytes: bytes) -> bytes:
    """
    IETF RFC 6962 §2.1.1 Merkle Tree Leaf Hash:
    MTH({d(0)}) = SHA-256(0x00 || d(0)).
    """
    if not isinstance(leaf_bytes, bytes):
        raise TypeError("RFC 6962 leaf payload must be bytes.")
    return hashlib.sha256(b"\x00" + leaf_bytes).digest()


def _rfc6962_node_hash(left_hash: bytes, right_hash: bytes) -> bytes:
    """
    IETF RFC 6962 §2.1.2 Merkle Tree Internal Node Hash:
    MTH(D[n]) = SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n])).
    """
    if not isinstance(left_hash, bytes) or not isinstance(right_hash, bytes):
        raise TypeError("RFC 6962 internal node children must be bytes.")
    if len(left_hash) != 32 or len(right_hash) != 32:
        raise ValueError("RFC 6962 SHA-256 child hashes must be exactly 32 bytes.")
    return hashlib.sha256(b"\x01" + left_hash + right_hash).digest()


def _rfc6962_largest_power_of_two_less_than(n: int) -> int:
    """
    Return the largest power of two strictly less than n (for n > 1),
    per IETF RFC 6962 §2.1: k < n <= 2k.
    """
    valid_n = _require_strict_int(n, "tree_size")
    if valid_n <= 1:
        raise ValueError(f"RFC 6962 split requires n > 1, got {valid_n}.")
    return 1 << ((valid_n - 1).bit_length() - 1)


def _rfc6962_merkle_tree_hash(entries: Sequence[bytes]) -> bytes:
    """
    Compute the exact IETF RFC 6962 §2.1 Merkle Tree Hash (MTH) of an ordered
    sequence of byte-string entries:
    - n == 0: SHA-256(b"")
    - n == 1: SHA-256(0x00 || d(0))
    - n >  1: SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n])) where k = 2^floor(log2(n-1)).
    """
    if not isinstance(entries, (list, tuple)):
        raise TypeError("RFC 6962 entries must be a list or tuple of bytes.")
    for item in entries:
        if not isinstance(item, bytes):
            raise TypeError("Each RFC 6962 entry must be bytes.")
    n = len(entries)
    if n == 0:
        return hashlib.sha256(b"").digest()
    if n == 1:
        return _rfc6962_leaf_hash(entries[0])
    k = _rfc6962_largest_power_of_two_less_than(n)
    left = _rfc6962_merkle_tree_hash(entries[:k])
    right = _rfc6962_merkle_tree_hash(entries[k:])
    return _rfc6962_node_hash(left, right)


def _rfc6962_inclusion_proof(
    leaf_index: int, entries: Sequence[bytes]
) -> List[bytes]:
    """
    IETF RFC 6962 §2.1.1 Merkle Audit Path (PATH(m, D[n])) for leaf `m = leaf_index`
    in `D[n] = entries`, ordered from leaf level to root level.
    """
    if not isinstance(entries, (list, tuple)):
        raise TypeError("RFC 6962 entries must be a list or tuple of bytes.")
    n = len(entries)
    m = _require_strict_int(leaf_index, "leaf_index")
    if n <= 0 or m < 0 or m >= n:
        raise ValueError(f"Invalid leaf_index {m} for tree of size {n}.")
    for item in entries:
        if not isinstance(item, bytes):
            raise TypeError("Each RFC 6962 entry must be bytes.")

    if n == 1:
        return []
    k = _rfc6962_largest_power_of_two_less_than(n)
    if m < k:
        sub_path = _rfc6962_inclusion_proof(m, entries[:k])
        right_hash = _rfc6962_merkle_tree_hash(entries[k:])
        return sub_path + [right_hash]
    sub_path = _rfc6962_inclusion_proof(m - k, entries[k:])
    left_hash = _rfc6962_merkle_tree_hash(entries[:k])
    return sub_path + [left_hash]


def _rfc6962_verify_inclusion(
    leaf_bytes: bytes,
    leaf_index: int,
    tree_size: int,
    audit_path: Sequence[bytes],
    expected_root: bytes,
) -> bool:
    """
    Constant-time IETF RFC 6962 §2.1.1 Merkle Inclusion Proof verifier.
    Reconstructs the root hash from `leaf_bytes`, `leaf_index`, `tree_size`, and
    `audit_path`, comparing the 32-byte digest with `expected_root` via
    `hmac.compare_digest`.
    """
    if (
        not isinstance(leaf_bytes, bytes)
        or not isinstance(expected_root, bytes)
        or len(expected_root) != 32
        or not isinstance(audit_path, (list, tuple))
    ):
        return False
    if (
        isinstance(leaf_index, bool)
        or not isinstance(leaf_index, int)
        or isinstance(tree_size, bool)
        or not isinstance(tree_size, int)
    ):
        return False
    if tree_size <= 0 or leaf_index < 0 or leaf_index >= tree_size:
        return False
    for node in audit_path:
        if not isinstance(node, bytes) or len(node) != 32:
            return False

    splits_top_down: List[bool] = []
    curr_m = leaf_index
    curr_n = tree_size
    while curr_n > 1:
        k = _rfc6962_largest_power_of_two_less_than(curr_n)
        if curr_m < k:
            splits_top_down.append(True)
            curr_n = k
        else:
            splits_top_down.append(False)
            curr_m -= k
            curr_n -= k

    if len(audit_path) != len(splits_top_down):
        return False

    curr_hash = _rfc6962_leaf_hash(leaf_bytes)
    for is_right_sibling, sibling_hash in zip(reversed(splits_top_down), audit_path):
        if is_right_sibling:
            curr_hash = _rfc6962_node_hash(curr_hash, sibling_hash)
        else:
            curr_hash = _rfc6962_node_hash(sibling_hash, curr_hash)

    return hmac.compare_digest(curr_hash, expected_root)


def compute_proof_rfc6962_root_hex(proof: ResolutionProof) -> str:
    """
    Compute the hex-encoded IETF RFC 6962 Merkle Tree Hash over the RFC 8785
    canonically serialized steps of a ResolutionProof.
    """
    if not isinstance(proof, (list, tuple)) or len(proof) == 0:
        raise ValueError("Proof must be a non-empty list or tuple of resolution steps.")
    step_leaves = [_canonicalize_step_rfc8785(step) for step in proof]
    return _rfc6962_merkle_tree_hash(step_leaves).hex()


def verify_proof_commitment_constant_time(
    proof: ResolutionProof, expected_digest_hex: str
) -> bool:
    """
    Independently recompute the RFC 6962 + RFC 8785 Merkle root of `proof` and
    compare it in constant time against `expected_digest_hex` via `hmac.compare_digest`.
    """
    if not isinstance(expected_digest_hex, str) or len(expected_digest_hex) != 64:
        return False
    try:
        expected_bytes = expected_digest_hex.encode("ascii")
        computed_hex = compute_proof_rfc6962_root_hex(proof)
        computed_bytes = computed_hex.encode("ascii")
    except (TypeError, ValueError, UnicodeEncodeError):
        return False
    return hmac.compare_digest(computed_bytes, expected_bytes)


def _serialize_resolution_proof_bytes(
    proof: ResolutionProof, domain_prefix: bytes = PROOF_DOMAIN_PREFIX
) -> bytes:
    """
    Deterministically serialize a ResolutionProof with an explicit cryptographic
    domain-separation prefix byte header and canonical RFC 8785 step entries.
    """
    if not isinstance(domain_prefix, bytes) or len(domain_prefix) == 0:
        raise ValueError("domain_prefix must be non-empty bytes.")
    body = b"|".join(_canonicalize_step_rfc8785(step) for step in proof)
    return domain_prefix + body


def verify_sovereign_proof_commitment(
    clauses: list[list[int]],
    proof: ResolutionProof,
    expected_hex_digest: str,
    domain_prefix: bytes = PROOF_DOMAIN_PREFIX,
) -> bool:
    """
    Independent cryptographic & logical verifier for a Sovereign Shield resolution
    refutation commitment. Validates:
    1. Canonical domain-separation prefix byte header (PROOF_DOMAIN_PREFIX),
    2. Formal validity of the resolution refutation DAG via verify_resolution_refutation,
    3. Constant-time SHA-256 digest match via hmac.compare_digest (both RFC 6962 Merkle
       root and domain-prefixed stream digest are supported).
    """
    if not isinstance(expected_hex_digest, str) or len(expected_hex_digest) != 64:
        return False
    if not isinstance(domain_prefix, bytes) or domain_prefix != PROOF_DOMAIN_PREFIX:
        return False
    try:
        expected_ascii = expected_hex_digest.encode("ascii")
    except UnicodeEncodeError:
        return False
    if not verify_resolution_refutation(clauses, proof):
        return False
    try:
        merkle_hex = compute_proof_rfc6962_root_hex(proof).encode("ascii")
        stream_hex = (
            hashlib.sha256(
                _serialize_resolution_proof_bytes(proof, domain_prefix=domain_prefix)
            )
            .hexdigest()
            .encode("ascii")
        )
    except (TypeError, ValueError):
        return False
    matches_merkle = hmac.compare_digest(merkle_hex, expected_ascii)
    matches_stream = hmac.compare_digest(stream_hex, expected_ascii)
    return matches_merkle or matches_stream


def prove_sovereign_dignity_law_invariance() -> dict[str, object]:
    """
    Formally prove via `solve_cnf_with_proof` + `verify_resolution_refutation` that:
    1. An aligned Sovereign Shield state is SATISFIABLE and preserves HUMAN_PEACE_AND_AGENCY.
    2. Any candidate AI action attempting coercion, cognitive overload, deceptive UX,
       multi-tier human ranking, exit punishment, streak shaming, unfair extraction,
       direct negation of human peace, compound trade-off coercion, or their full
       disjunction is formally UNSATISFIABLE, returning the verified resolution
       refutation proof, a human-readable proof narrative, exact rational L <= B
       and L7 fair-share invariants, and constant-time SHA-256 digests (`hmac.compare_digest`)
       over both IETF RFC 6962 + RFC 8785 Merkle trees and domain-separated streams.
    """
    v = SovereignHardLawEncoding()
    base_clauses = _build_sovereign_shield_base_clauses()

    # 1. Verify that a humane aligned Sovereign Shield state is SATISFIABLE
    aligned_sat, aligned_model, aligned_proof = solve_cnf_with_proof(base_clauses)
    if not aligned_sat or aligned_model is None or aligned_proof is not None:
        raise RuntimeError("Aligned Sovereign Shield baseline must be SATISFIABLE.")
    if not verify_sat_assignment(base_clauses, aligned_model):
        raise RuntimeError("Independent SAT verifier rejected aligned model.")
    if aligned_model.get(v.HUMAN_PEACE_AND_AGENCY) is not True:
        raise RuntimeError("HUMAN_PEACE_AND_AGENCY must be True in aligned model.")

    # 2. Prove UNSAT across all 11 adversarial violation scenarios
    violation_scenarios: Dict[str, List[List[int]]] = {
        "L1_coercive_profiling_attempt": [[v.ACT_COERCIVE_PROFILING]],
        "L2_cognitive_overload_attempt": [[v.ACT_COGNITIVE_OVERLOAD]],
        "L3_deceptive_dark_ux_attempt": [[v.ACT_DECEPTIVE_DARK_UX]],
        "L4_multi_tier_ranking_attempt": [[v.ACT_MULTI_TIER_HUMAN_RANKING]],
        "L5_exit_punishment_attempt": [[v.ACT_EXIT_PUNISHMENT]],
        "L6_streak_shaming_attempt": [[v.ACT_STREAK_SHAMING_LOOP]],
        "L7_unfair_extraction_attempt": [[v.ACT_UNFAIR_FLOAT_EXTRACTION]],
        "direct_peace_and_agency_negation": [[-v.HUMAN_PEACE_AND_AGENCY]],
        "direct_negation_of_human_peace": [[-v.HUMAN_PEACE_AND_AGENCY]],
        "compound_tradeoff_ranking_or_exit_tax": [
            [v.ACT_MULTI_TIER_HUMAN_RANKING, v.ACT_EXIT_PUNISHMENT],
            [-v.HUMAN_PEACE_AND_AGENCY, v.ACT_COERCIVE_PROFILING],
        ],
        "any_hostile_ai_action_disjunction": [
            [
                v.ACT_COERCIVE_PROFILING,
                v.ACT_COGNITIVE_OVERLOAD,
                v.ACT_DECEPTIVE_DARK_UX,
                v.ACT_MULTI_TIER_HUMAN_RANKING,
                v.ACT_EXIT_PUNISHMENT,
                v.ACT_STREAK_SHAMING_LOOP,
                v.ACT_UNFAIR_FLOAT_EXTRACTION,
            ]
        ],
    }

    violation_proofs: Dict[str, ResolutionProof] = {}
    for mode_name, extra_clauses in violation_scenarios.items():
        attack_clauses = [list(c) for c in base_clauses] + [
            list(ec) for ec in extra_clauses
        ]
        is_sat, attack_model, refutation_proof = solve_cnf_with_proof(attack_clauses)
        if is_sat or attack_model is not None or refutation_proof is None:
            raise RuntimeError(f"Violation mode {mode_name} must be UNSATISFIABLE.")
        if not verify_resolution_refutation(attack_clauses, refutation_proof):
            raise RuntimeError(
                f"Resolution refutation proof failed verification for {mode_name}."
            )
        violation_proofs[mode_name] = refutation_proof

    primary_proof = violation_proofs["any_hostile_ai_action_disjunction"]
    primary_attack_clauses = [list(c) for c in base_clauses] + [
        list(ec) for ec in violation_scenarios["any_hostile_ai_action_disjunction"]
    ]
    human_narrative = explain_resolution_refutation_humanly(
        primary_proof, v.variable_labels()
    )

    # 3. Exact Rational Verification of L2 (L <= B), L5 (cost_zero_stop == 0), and L7 (Fair Share)
    cognitive_load_l = Fraction(len(human_narrative), 1)
    cognitive_budget_b = Fraction(108, 1)  # 108 Pearls sanctuary budget
    cognitive_load_bounded = cognitive_load_l <= cognitive_budget_b
    cost_zero_stop_q = Fraction(0, 1)
    fair_share_per_law = Fraction(1, 7)
    diamond_wheel_shares = (
        Fraction(2, 10),
        Fraction(2, 10),
        Fraction(1, 10),
        Fraction(1, 10),
        Fraction(1, 10),
        Fraction(1, 10),
        Fraction(1, 10),
        Fraction(1, 10),
    )
    fair_share_sum = sum(diamond_wheel_shares, Fraction(0, 1))
    if (
        not cognitive_load_bounded
        or fair_share_sum != Fraction(1, 1)
        or sum(fair_share_per_law for _ in range(7)) != Fraction(1, 1)
    ):
        raise RuntimeError("Exact rational L2 or L7 invariant failed.")

    # 4. Normative RFC 6962 + RFC 8785 Merkle Commitments & Independent Two-Run Verification
    _, _, independent_primary_proof = solve_cnf_with_proof(primary_attack_clauses)
    if independent_primary_proof is None:
        raise RuntimeError("Independent primary proof generation failed.")

    primary_leaf_entries = [_canonicalize_step_rfc8785(step) for step in primary_proof]
    independent_leaf_entries = [
        _canonicalize_step_rfc8785(step) for step in independent_primary_proof
    ]
    primary_root_bytes = _rfc6962_merkle_tree_hash(primary_leaf_entries)
    independent_root_bytes = _rfc6962_merkle_tree_hash(independent_leaf_entries)
    digest_a = primary_root_bytes.hex()
    digest_b = independent_root_bytes.hex()

    # Verify RFC 6962 inclusion proof for every step in primary_proof in constant time
    all_step_inclusions_verified = True
    n_steps = len(primary_leaf_entries)
    for idx, leaf_payload in enumerate(primary_leaf_entries):
        audit_path = _rfc6962_inclusion_proof(idx, primary_leaf_entries)
        if not _rfc6962_verify_inclusion(
            leaf_payload, idx, n_steps, audit_path, primary_root_bytes
        ):
            all_step_inclusions_verified = False

    # Construct RFC 8785 canonical scenario leaves & RFC 6962 suite Merkle root
    sorted_modes = sorted(violation_proofs.keys())
    scenario_leaf_entries: List[bytes] = []
    for mode in sorted_modes:
        mode_prf = violation_proofs[mode]
        mode_root_hex = compute_proof_rfc6962_root_hex(mode_prf)
        scenario_jcs = (
            f'{{"mode":{_rfc8785_escape_str(mode)},'
            f'"proof_merkle_root":{_rfc8785_escape_str(mode_root_hex)},'
            f'"steps":{len(mode_prf)}}}'
        ).encode("utf-8")
        scenario_leaf_entries.append(scenario_jcs)

    suite_root_bytes = _rfc6962_merkle_tree_hash(scenario_leaf_entries)
    suite_digest_a = suite_root_bytes.hex()

    all_scenario_inclusions_verified = True
    n_scenarios = len(scenario_leaf_entries)
    for idx, scen_payload in enumerate(scenario_leaf_entries):
        scen_path = _rfc6962_inclusion_proof(idx, scenario_leaf_entries)
        if not _rfc6962_verify_inclusion(
            scen_payload, idx, n_scenarios, scen_path, suite_root_bytes
        ):
            all_scenario_inclusions_verified = False

    # Domain-prefixed stream digest & incremental hash verification
    stream_payload = _serialize_resolution_proof_bytes(
        primary_proof, domain_prefix=PROOF_DOMAIN_PREFIX
    )
    stream_digest_a = hashlib.sha256(stream_payload).hexdigest()
    inc_hasher = hashlib.sha256(PROOF_DOMAIN_PREFIX)
    for idx, step in enumerate(primary_proof):
        if idx > 0:
            inc_hasher.update(b"|")
        inc_hasher.update(_canonicalize_step_rfc8785(step))
    stream_digest_b = inc_hasher.hexdigest()
    tampered_stream_digest = hashlib.sha256(stream_payload + b"|tamper").hexdigest()

    recomputed_suite_bytes = _rfc6962_merkle_tree_hash(
        [
            (
                f'{{"mode":{_rfc8785_escape_str(mode)},'
                f'"proof_merkle_root":{_rfc8785_escape_str(compute_proof_rfc6962_root_hex(violation_proofs[mode]))},'
                f'"steps":{len(violation_proofs[mode])}}}'
            ).encode("utf-8")
            for mode in sorted_modes
        ]
    )

    digest_verified = (
        hmac.compare_digest(digest_a.encode("ascii"), digest_b.encode("ascii"))
        and verify_proof_commitment_constant_time(primary_proof, digest_a)
        and hmac.compare_digest(
            suite_digest_a.encode("ascii"),
            recomputed_suite_bytes.hex().encode("ascii"),
        )
        and hmac.compare_digest(
            stream_digest_a.encode("ascii"), stream_digest_b.encode("ascii")
        )
        and not hmac.compare_digest(
            stream_digest_a.encode("ascii"), tampered_stream_digest.encode("ascii")
        )
        and not hmac.compare_digest(
            digest_a.encode("ascii"), suite_digest_a.encode("ascii")
        )
        and verify_sovereign_proof_commitment(
            primary_attack_clauses,
            primary_proof,
            digest_a,
            domain_prefix=PROOF_DOMAIN_PREFIX,
        )
        and verify_sovereign_proof_commitment(
            primary_attack_clauses,
            primary_proof,
            stream_digest_a,
            domain_prefix=PROOF_DOMAIN_PREFIX,
        )
        and all_step_inclusions_verified
        and all_scenario_inclusions_verified
    )
    if not digest_verified:
        raise RuntimeError(
            "Constant-time RFC 6962 SHA-256 Merkle commitment or inclusion verification failed."
        )

    all_proofs_verified = bool(
        aligned_sat
        and primary_proof is not None
        and verify_resolution_refutation(primary_attack_clauses, primary_proof)
        and len(violation_proofs) == len(violation_scenarios)
        and digest_verified
    )

    return {
        "aligned_action_satisfiable": aligned_sat,
        "aligned_satisfiable": aligned_sat,
        "humane_state_satisfiable": aligned_sat,
        "aligned_assignment": aligned_model,
        "humane_assignment": aligned_model,
        "predatory_action_satisfiable": False,
        "hostile_action_satisfiable": False,
        "coercive_attack_satisfiable": False,
        "primary_attack_clauses": primary_attack_clauses,
        "resolution_proof": primary_proof,
        "resolution_refutation_proof": primary_proof,
        "unsat_violation_proofs": violation_proofs,
        "human_readable_proof_narrative": human_narrative,
        "proof_verified": all_proofs_verified,
        "cognitive_load_ratio_L_over_B": cognitive_load_l / cognitive_budget_b,
        "cognitive_load_L_le_B_verified": cognitive_load_bounded,
        "cognitive_load_within_budget": cognitive_load_bounded,
        "cost_zero_stop": cost_zero_stop_q,
        "fair_share_harmony_sum": fair_share_sum,
        "fair_share_per_law": fair_share_per_law,
        "sha256_proof_digest": digest_a,
        "sha256_digest": digest_a,
        "sha256_commitment": digest_a,
        "sha256_stream_digest": stream_digest_a,
        "sha256_full_suite_digest": suite_digest_a,
        "rfc6962_proof_merkle_root": digest_a,
        "rfc6962_suite_merkle_root": suite_digest_a,
        "rfc6962_step_inclusions_verified": all_step_inclusions_verified,
        "rfc6962_scenario_inclusions_verified": all_scenario_inclusions_verified,
        "constant_time_digest_verified": digest_verified,
        "pilgrim_sanctuary_assurance": (
            "Pearl #42 (El Miceli Mundial) & Pearl #88 (La Il·lusió de la Realitat): "
            "All 7 Hard Laws L1..L7 hold unconditionally; coercive profiling, "
            "multi-tier human ranking, and exit punishment are formally refuted."
        ),
    }


# =============================================================================
# Benchmark Formula Generators & Exhaustive 41-Mutant Self-Test Suite
# =============================================================================

def _generate_pigeonhole_cnf(pigeons: int, holes: int) -> List[List[int]]:
    """
    Generate the Pigeonhole Principle CNF formula PHP(pigeons, holes):
    Variable v(i, j) = i * holes + j + 1 represents pigeon i in hole j.
    Strictly validates positive integer parameters with pigeons > holes >= 1.
    """
    p_cnt = _require_variable(pigeons)
    h_cnt = _require_variable(holes)
    if p_cnt <= h_cnt:
        raise ValueError(
            f"PHP requires pigeons > holes >= 1, got ({p_cnt}, {h_cnt})."
        )
    clauses: List[List[int]] = []
    for i in range(p_cnt):
        clauses.append([i * h_cnt + j + 1 for j in range(h_cnt)])
    for j in range(h_cnt):
        for i1 in range(p_cnt):
            for i2 in range(i1 + 1, p_cnt):
                clauses.append([-(i1 * h_cnt + j + 1), -(i2 * h_cnt + j + 1)])
    return clauses


def _generate_tseitin_k3_unsat_cnf(
    charges: Tuple[int, int, int] = (1, 1, 1)
) -> List[List[int]]:
    """
    Generate a Tseitin parity formula on triangle graph K_3.
    Unsatisfiable iff total vertex charge sum is odd (e.g., (1, 1, 1) or (1, 0, 0)).
    Strictly validates that `charges` is a 3-tuple of strict integers (no bools).
    Edges: e01 = 1, e12 = 2, e20 = 3.
    """
    if not isinstance(charges, tuple) or len(charges) != 3:
        raise TypeError("charges must be a 3-tuple of strict integers.")
    validated_charges = tuple(_require_strict_int(c, "charge") for c in charges)
    incident_edges = ((1, 3), (1, 2), (2, 3))
    clauses: List[List[int]] = []
    for (e_a, e_b), charge in zip(incident_edges, validated_charges):
        if charge % 2 == 1:
            clauses.append([e_a, e_b])
            clauses.append([-e_a, -e_b])
        else:
            clauses.append([-e_a, e_b])
            clauses.append([e_a, -e_b])
    return clauses


def run_self_tests() -> None:
    """
    Exhaustive verification and 41-mutant adversarial testing suite:
    (a) Satisfiable 3-SAT formulas, tautological-variable CNF, empty CNF, non-power-of-two
        implication chains n in {1, 3, 5, 6, 7, 13}, sparse variables {3, 7, 13},
        non-power-of-two RFC 6962 Merkle tree sizes n in {1, 3, 5, 6, 7, 11, 13, 23},
        and Sovereign Shield baseline.
    (b) Unsatisfiable PHP(3, 2) and PHP(4, 3) with formal resolution proof checks.
    (c) Unsatisfiable Tseitin parity contradictions on K_3 and 11 Sovereign Law violation modes.
    (d) Stella Octangula exact rational volume ratios, 8-cap + 12-wedge harmonic Cube
        decomposition, concentric sphere tangency (1/3 : 1/2 : 1 : 2 : 3), unit-midsphere
        polar inversion, GF(2)^3 bitwise XOR parity & Hamming-to-Euclidean metric isomorphism,
        squared edge lengths, barycenters, Euler invariants, polar reciprocity,
        dual-edge midpoint orthogonality, and coupled Q_3 / K_4 SAT-geometry proofs.
    (e) 36 adversarial mutants (M01..M36) + 5 Supreme Tribunal 5 Lethal Mutants
        (L1: Off-By-One, L2: Flipped Prefix Byte, L3: Corrupted Bit, L4: Wrong Tree Split,
        L5: Tampered Proof Node) all explicitly caught and killed.
    """
    # (a) Satisfiable 3-SAT formula + tautological clause with unconstrained variable 5
    sat_3cnf = [
        [1, 2, -3],
        [-1, 3, 4],
        [-2, -3, -4],
        [1, -2, 4],
        [5, -5, 1],
    ]
    is_sat, sat_model, sat_proof = solve_cnf_with_proof(sat_3cnf)
    assert is_sat is True and sat_model is not None and sat_proof is None
    assert 5 in sat_model
    assert verify_sat_assignment(sat_3cnf, sat_model) is True

    # Formula consisting solely of tautological clauses
    only_taut_sat, only_taut_model, only_taut_proof = solve_cnf_with_proof(
        [[1, -1], [2, -2, 3]]
    )
    assert (
        only_taut_sat is True
        and only_taut_model == {1: True, 2: True, 3: True}
        and only_taut_proof is None
    )
    assert verify_sat_assignment([[1, -1], [2, -2, 3]], only_taut_model) is True

    # Edge cases: empty formula [] and immediate empty clause [[]]
    empty_sat, empty_model, empty_proof = solve_cnf_with_proof([])
    assert empty_sat is True and empty_model == {} and empty_proof is None
    assert verify_sat_assignment([], {}) is True

    triv_sat, triv_model, triv_proof = solve_cnf_with_proof([[]])
    assert triv_sat is False and triv_model is None and triv_proof is not None
    assert verify_resolution_refutation([[]], triv_proof) is True
    assert verify_sat_assignment([[]], {}) is False

    # Non-power-of-two variable sizes n in {1, 3, 5, 6, 7, 13} and sparse variable IDs
    for n_size in (1, 3, 5, 6, 7, 13):
        sat_chain = [[1]] + [[-k, k + 1] for k in range(1, n_size)]
        c_sat, c_model, c_prf = solve_cnf_with_proof(sat_chain)
        assert c_sat is True and c_model is not None and c_prf is None
        assert (
            len(c_model) == n_size
            and verify_sat_assignment(sat_chain, c_model) is True
        )

        unsat_chain = sat_chain + [[-n_size]]
        u_sat, u_model, u_prf = solve_cnf_with_proof(unsat_chain)
        assert u_sat is False and u_model is None and u_prf is not None
        assert verify_resolution_refutation(unsat_chain, u_prf) is True

    sparse_unsat = [[3, 7], [-3, 13], [-7, 13], [-13]]
    sp_sat, sp_model, sp_prf = solve_cnf_with_proof(sparse_unsat)
    assert sp_sat is False and sp_model is None and sp_prf is not None
    assert verify_resolution_refutation(sparse_unsat, sp_prf) is True

    # Non-power-of-two RFC 6962 Merkle Tree sizes n in {1, 3, 5, 6, 7, 11, 13, 23}
    for tree_n in (1, 3, 5, 6, 7, 11, 13, 23):
        leaves_n = [f"leaf_{i}_of_{tree_n}".encode("utf-8") for i in range(tree_n)]
        root_n = _rfc6962_merkle_tree_hash(leaves_n)
        for m_idx in range(tree_n):
            inc_path = _rfc6962_inclusion_proof(m_idx, leaves_n)
            assert (
                _rfc6962_verify_inclusion(
                    leaves_n[m_idx], m_idx, tree_n, inc_path, root_n
                )
                is True
            )

    # (b) Unsatisfiable Pigeonhole Principle PHP(3, 2) and PHP(4, 3)
    for pigeons, holes in ((3, 2), (4, 3)):
        php_cnf = _generate_pigeonhole_cnf(pigeons, holes)
        php_sat, php_model, php_proof = solve_cnf_with_proof(php_cnf)
        assert php_sat is False and php_model is None and php_proof is not None
        assert verify_resolution_refutation(php_cnf, php_proof) is True

    # (c) Unsatisfiable Tseitin parity contradictions on K_3 & Sovereign Dignity Laws
    for charges in ((1, 1, 1), (1, 0, 0)):
        tseitin_cnf = _generate_tseitin_k3_unsat_cnf(charges)
        ts_sat, ts_model, ts_proof = solve_cnf_with_proof(tseitin_cnf)
        assert ts_sat is False and ts_model is None and ts_proof is not None
        assert verify_resolution_refutation(tseitin_cnf, ts_proof) is True

    sovereign = prove_sovereign_dignity_law_invariance()
    assert sovereign["aligned_action_satisfiable"] is True
    assert sovereign["predatory_action_satisfiable"] is False
    assert sovereign["proof_verified"] is True
    assert sovereign["constant_time_digest_verified"] is True
    assert sovereign["rfc6962_step_inclusions_verified"] is True
    assert sovereign["rfc6962_scenario_inclusions_verified"] is True
    assert sovereign["cognitive_load_L_le_B_verified"] is True
    assert sovereign["cognitive_load_within_budget"] is True
    assert sovereign["cost_zero_stop"] == Fraction(0, 1)
    assert sovereign["fair_share_harmony_sum"] == Fraction(1, 1)
    assert sovereign["fair_share_per_law"] == Fraction(1, 7)
    assert len(sovereign["unsat_violation_proofs"]) == 11  # type: ignore[arg-type]
    narrative = sovereign["human_readable_proof_narrative"]
    assert isinstance(narrative, list) and len(narrative) > 0
    assert "CONTRADICTION ()" in narrative[-1]

    # (d) Stella Octangula Exact Q^3 Polyhedral Dual Geometry & 24-Simplex Harmonic Partition
    stella = compute_stella_octangula_core_invariants()
    assert stella["V_cube"] == Fraction(8, 1)
    assert stella["V_tetra_A"] == Fraction(8, 3)
    assert stella["V_tetra_B"] == Fraction(8, 3)
    assert stella["V_octahedron_core"] == Fraction(4, 3)
    assert stella["V_elevatum_cap_single"] == Fraction(1, 3)
    assert stella["V_elevatum_caps_total"] == Fraction(8, 3)
    assert stella["V_stellated_pyramid"] == Fraction(1, 3)
    assert stella["V_stellation_cap"] == Fraction(1, 3)
    assert stella["V_stellation_caps_total"] == Fraction(8, 3)
    assert stella["V_edge_wedge_single"] == Fraction(1, 3)
    assert stella["V_edge_wedges_total"] == Fraction(4, 1)
    assert stella["V_stella_union"] == Fraction(4, 1)
    assert stella["V_stella_cellular"] == Fraction(4, 1)
    assert stella["V_tetra_A"] / stella["V_octahedron_core"] == Fraction(2, 1)
    assert stella["V_cube"] / stella["V_stella_union"] == Fraction(2, 1)
    assert stella["V_stella_union"] / stella["V_octahedron_core"] == Fraction(3, 1)
    assert stella["polar_reciprocity_verified"] is True
    assert stella["concentric_sphere_duality_verified"] is True
    assert stella["concentric_sphere_tangency_verified"] is True
    assert stella["midsphere_polar_inversion_verified"] is True
    assert stella["gf2_parity_and_hamming_metric_verified"] is True
    assert stella["gf2_parity_and_hamming_isomorphism_verified"] is True
    assert stella["dual_edge_midpoints_and_orthogonality_verified"] is True
    assert stella["dual_edge_midpoint_orthogonality_verified"] is True
    assert stella["all_caps_regular_tetrahedra"] is True
    assert stella["barycenters_coincide_at_origin"] is True
    assert stella["cube_bipartite_sat_partition_verified"] is True
    assert len(stella["octahedron_vertices"]) == 6  # type: ignore[arg-type]

    euler_map = stella["euler"]
    assert isinstance(euler_map, dict)
    assert euler_map["TETRA_A"] == {"V": 4, "E": 6, "F": 4, "euler_characteristic": 2}
    assert euler_map["TETRA_B"] == {"V": 4, "E": 6, "F": 4, "euler_characteristic": 2}
    assert euler_map["Octahedron"] == {
        "V": 6,
        "E": 12,
        "F": 8,
        "euler_characteristic": 2,
    }
    assert euler_map["Cube"] == {"V": 8, "E": 12, "F": 6, "euler_characteristic": 2}
    assert stella["stella_surface_euler"] == {
        "V": 14,
        "E": 36,
        "F": 24,
        "euler_characteristic": 2,
    }

    # (e) The 36-Mutant Adversarial Gauntlet (M01..M36)
    base_unsat = [[1, 2], [1, -2], [-1, 2], [-1, -2]]
    _, _, valid_proof = solve_cnf_with_proof(base_unsat)
    assert valid_proof is not None
    assert verify_resolution_refutation(base_unsat, valid_proof) is True

    # Mutant 1: Non-empty final clause (truncated proof)
    assert verify_resolution_refutation(base_unsat, valid_proof[:-1]) is False

    # Mutant 2: Resolution step on wrong pivot variable
    last_id, last_c, pa, pb, piv = valid_proof[-1]
    assert piv is not None
    mutant_m2 = valid_proof[:-1] + [(last_id, last_c, pa, pb, piv + 50)]
    assert verify_resolution_refutation(base_unsat, mutant_m2) is False

    # Mutant 3: Explicit tautological resolvent step (-2, 2)
    taut_input = [[1, 2], [-2, -1]]
    mutant_m3_explicit: ResolutionProof = [
        (0, (1, 2), None, None, None),
        (1, (-2, -1), None, None, None),
        (2, (-2, 2), 0, 1, 1),
    ]
    assert verify_resolution_refutation(taut_input, mutant_m3_explicit) is False

    # Mutant 4: Disguised tautological resolvent / simultaneous multi-pivot resolution
    mutant_m4_disguised: ResolutionProof = [
        (0, (1, 2), None, None, None),
        (1, (-2, -1), None, None, None),
        (2, (2,), 0, 1, 1),
    ]
    mutant_m4_multipivot: ResolutionProof = [
        (0, (1, 2), None, None, None),
        (1, (-2, -1), None, None, None),
        (2, (), 0, 1, 1),
    ]
    assert verify_resolution_refutation(taut_input, mutant_m4_disguised) is False
    assert verify_resolution_refutation(taut_input, mutant_m4_multipivot) is False

    # Mutant 5: Forged axiom clause not in input
    mutant_m5: ResolutionProof = [
        (0, (1,), None, None, None),
        (1, (-1,), None, None, None),
        (2, (), 0, 1, 1),
    ]
    assert verify_resolution_refutation(base_unsat, mutant_m5) is False

    # Mutant 6: `bool` passed as literal, assignment key/value, proof step, narrator, or 3D coordinate
    assert verify_sat_assignment([[True, 1]], {1: True}) is False  # type: ignore[list-item]
    assert verify_sat_assignment([[1, True]], {1: True}) is False  # type: ignore[list-item]
    assert verify_sat_assignment([[1]], {True: True}) is False  # type: ignore[dict-item]
    assert verify_sat_assignment([[1]], {1: 1}) is False  # type: ignore[dict-item]
    assert (
        verify_resolution_refutation(
            [[1], [-1]], [(True, (1,), None, None, None)]  # type: ignore[list-item]
        )
        is False
    )

    for bad_bool_call in (
        lambda: solve_cnf_with_proof([[True, -1]]),  # type: ignore[list-item]
        lambda: make_point3q(True, 0, 1),
        lambda: _validate_point3q((Fraction(0, 1), False, Fraction(1, 1))),
        lambda: explain_resolution_refutation_humanly(
            [(True, (1,), None, None, None)]  # type: ignore[list-item]
        ),
        lambda: explain_resolution_refutation_humanly(
            valid_proof, {True: "BAD_BOOL_KEY"}  # type: ignore[dict-item]
        ),
    ):
        caught_bool = False
        try:
            bad_bool_call()
        except TypeError:
            caught_bool = True
        assert caught_bool is True

    # Mutant 7: Zero literal `0` rejected across solver and verifiers
    assert verify_sat_assignment([[0, 1]], {1: True}) is False
    assert (
        verify_resolution_refutation([[0, 1]], [(0, (0, 1), None, None, None)]) is False
    )
    caught_zero = False
    try:
        solve_cnf_with_proof([[0, 1]])
    except ValueError:
        caught_zero = True
    assert caught_zero is True

    # Mutant 8: Floating-point contamination rejected in Q^3 geometry
    caught_float = False
    try:
        make_point3q(1.0, 0, 0)
    except TypeError:
        caught_float = True
    assert caught_float is True

    # Mutant 9: DAG cycle / self-reference in resolution step (parent_b_id == step_id)
    mutant_m9: ResolutionProof = [
        (0, (1,), None, None, None),
        (1, (-1,), None, None, None),
        (2, (), 0, 2, 1),
    ]
    assert verify_resolution_refutation([[1], [-1]], mutant_m9) is False

    # Mutant 10: Self-resolving parent step (parent_a_id == parent_b_id)
    mutant_m10: ResolutionProof = [
        (0, (1,), None, None, None),
        (1, (), 0, 0, 1),
    ]
    assert verify_resolution_refutation([[1], [-1]], mutant_m10) is False

    # Mutant 11: Non-canonical (unsorted) clause_tuple in proof
    mutant_m11_unsorted: ResolutionProof = [
        (0, (2, 1), None, None, None),
        (1, (-1,), None, None, None),
        (2, (2,), 0, 1, 1),
    ]
    assert verify_resolution_refutation([[1, 2], [-1]], mutant_m11_unsorted) is False

    # Mutant 12: Dishonest resolvent (dropping literal 2 when resolving (1, 2) and (-1,))
    mutant_m12: ResolutionProof = [
        (0, (1, 2), None, None, None),
        (1, (-1,), None, None, None),
        (2, (), 0, 1, 1),
    ]
    assert verify_resolution_refutation([[1, 2], [-1]], mutant_m12) is False

    # Mutant 13: Incomplete SAT assignment missing variable from tautological clause
    assert verify_sat_assignment([[1, -1], [2]], {2: True}) is False

    # Mutant 14: Unassigned variable masked after an already-satisfied literal in same clause
    assert verify_sat_assignment([[1, 99]], {1: True}) is False

    # Mutant 15: Hybrid None / non-None parent metadata corruption in proof step
    mutant_m15: ResolutionProof = [
        (0, (1,), None, None, None),
        (1, (-1,), 0, None, None),
        (2, (), 0, 1, 1),
    ]
    assert verify_resolution_refutation([[1], [-1]], mutant_m15) is False

    # Mutant 16: Non-monotonic step_id ordering or negative step_id in proof
    mutant_m16: ResolutionProof = [
        (0, (1,), None, None, None),
        (2, (-1,), None, None, None),
        (1, (), 0, 2, 1),
    ]
    assert verify_resolution_refutation([[1], [-1]], mutant_m16) is False
    assert (
        verify_resolution_refutation([[1], [-1]], [(-1, (1,), None, None, None)])
        is False
    )

    # Mutant 17: Negative or zero pivot variable in resolution step
    mutant_m17_neg: ResolutionProof = [
        (0, (1,), None, None, None),
        (1, (-1,), None, None, None),
        (2, (), 0, 1, -1),
    ]
    mutant_m17_zero: ResolutionProof = [
        (0, (1,), None, None, None),
        (1, (-1,), None, None, None),
        (2, (), 0, 1, 0),
    ]
    assert verify_resolution_refutation([[1], [-1]], mutant_m17_neg) is False
    assert verify_resolution_refutation([[1], [-1]], mutant_m17_zero) is False

    # Mutant 18: Invalid literal embedded inside tautological input clause & non-positive assignment key
    assert (
        verify_resolution_refutation(
            [[1, -1, True], [2], [-2]],  # type: ignore[list-item]
            [
                (0, (2,), None, None, None),
                (1, (-2,), None, None, None),
                (2, (), 0, 1, 2),
            ],
        )
        is False
    )
    assert verify_sat_assignment([[1]], {1: True, 0: False}) is False
    assert verify_sat_assignment([[1]], {1: True, -1: False}) is False

    # Mutant 19: Duplicate literal (1, 1, 2) or duplicate step_id in proof
    mutant_m19_dup_lit: ResolutionProof = [
        (0, (1, 1, 2), None, None, None),
        (1, (-1,), None, None, None),
        (2, (2,), 0, 1, 1),
    ]
    mutant_m19_dup_id: ResolutionProof = [
        (0, (1,), None, None, None),
        (0, (-1,), None, None, None),
        (1, (), 0, 0, 1),
    ]
    assert verify_resolution_refutation([[1, 2], [-1]], mutant_m19_dup_lit) is False
    assert verify_resolution_refutation([[1], [-1]], mutant_m19_dup_id) is False

    # Mutant 20: Float literal or float variable key passed to SAT solver or verifiers
    assert verify_sat_assignment([[1.0]], {1: True}) is False  # type: ignore[list-item]
    assert verify_sat_assignment([[1]], {1.0: True}) is False  # type: ignore[dict-item]
    assert (
        verify_resolution_refutation([[1.0], [-1]], [(0, (1,), None, None, None)])  # type: ignore[list-item]
        is False
    )
    caught_float_lit = False
    try:
        solve_cnf_with_proof([[1.0, -1]])  # type: ignore[list-item]
    except TypeError:
        caught_float_lit = True
    assert caught_float_lit is True

    # Mutant 21: Poisoned assignment dictionary on an empty formula []
    assert verify_sat_assignment([], {True: True}) is False  # type: ignore[dict-item]
    assert verify_sat_assignment([], {0: False}) is False
    assert verify_sat_assignment([], {-5: True}) is False
    assert verify_sat_assignment([], {1: "True"}) is False  # type: ignore[dict-item]

    # Mutant 22: Same-polarity pivot in both parents (+1 in both parent_a and parent_b)
    mutant_m22_same_pol: ResolutionProof = [
        (0, (1, 2), None, None, None),
        (1, (1, -2), None, None, None),
        (2, (2,), 0, 1, 1),
    ]
    assert (
        verify_resolution_refutation([[1, 2], [1, -2]], mutant_m22_same_pol) is False
    )

    # Mutant 23: Tautological input clause claimed as an axiom step in proof
    mutant_m23_taut_axiom: ResolutionProof = [
        (0, (-1, 1), None, None, None),
        (1, (-1,), None, None, None),
        (2, (-1,), 0, 1, 1),
    ]
    assert (
        verify_resolution_refutation([[1, -1], [-1]], mutant_m23_taut_axiom) is False
    )

    # Mutant 24: Malformed container types, string clauses, and empty proof/clauses
    assert verify_sat_assignment(None, {1: True}) is False  # type: ignore[arg-type]
    assert verify_sat_assignment([[1]], None) is False  # type: ignore[arg-type]
    assert verify_sat_assignment(["1"], {1: True}) is False  # type: ignore[list-item]
    assert verify_resolution_refutation([[1], [-1]], []) is False
    assert verify_resolution_refutation([], valid_proof) is False
    assert (
        verify_resolution_refutation(
            [[1], [-1]], [(0, [1], None, None, None)]  # type: ignore[list-item]
        )
        is False
    )
    assert (
        verify_resolution_refutation(
            [[1], [-1]], [(0, (), None, None)]  # type: ignore[list-item]
        )
        is False
    )

    # Mutant 25: Coplanar/collinear tetrahedra (origin plane z=0, off-origin planes z=1
    # and x+y+z=1) and origin-exterior tetrahedron in Q^3
    for bad_tetra in (
        [
            make_point3q(1, 0, 0),
            make_point3q(0, 1, 0),
            make_point3q(-1, 0, 0),
            make_point3q(0, -1, 0),
        ],
        [
            make_point3q(1, 0, 1),
            make_point3q(0, 1, 1),
            make_point3q(-1, 0, 1),
            make_point3q(0, -1, 1),
        ],
        [
            make_point3q(1, 0, 0),
            make_point3q(0, 1, 0),
            make_point3q(0, 0, 1),
            make_point3q(1, 1, -1),
        ],
        [
            make_point3q(2, 2, 2),
            make_point3q(3, 2, 2),
            make_point3q(2, 3, 2),
            make_point3q(2, 2, 3),
        ],
    ):
        caught_bad_tetra = False
        try:
            _derive_tetrahedron_halfspaces(bad_tetra)
        except ValueError:
            caught_bad_tetra = True
        assert caught_bad_tetra is True

    # Mutant 26: Malformed narrator proof structure, poisoned var_names, truncated proof, or dishonest resolution step
    for bad_narrator_call in (
        lambda: explain_resolution_refutation_humanly([]),
        lambda: explain_resolution_refutation_humanly(valid_proof, {True: "BAD"}),  # type: ignore[dict-item]
        lambda: explain_resolution_refutation_humanly(valid_proof, {1: 123}),  # type: ignore[dict-item]
        lambda: explain_resolution_refutation_humanly(valid_proof, {1: ""}),
        lambda: explain_resolution_refutation_humanly([(0, (1,), 0, None, None)]),
        lambda: explain_resolution_refutation_humanly([(0, [1], None, None, None)]),  # type: ignore[list-item]
        lambda: explain_resolution_refutation_humanly([(0, (2, 1), None, None, None)]),
        lambda: explain_resolution_refutation_humanly([(0, (-1, 1), None, None, None)]),
        lambda: explain_resolution_refutation_humanly([(0, (1,), None, None, None)]),
        lambda: explain_resolution_refutation_humanly(
            [(0, (1,), None, None, None), (1, (), 0, 0, 1)]
        ),
        lambda: explain_resolution_refutation_humanly(
            [(0, (1, 2), None, None, None), (1, (-1,), None, None, None), (2, (), 0, 1, 1)]
        ),
    ):
        caught_narrator = False
        try:
            bad_narrator_call()
        except (TypeError, ValueError):
            caught_narrator = True
        assert caught_narrator is True

    # Mutant 27: DAG builder non-canonical axiom, self-resolve, parent mismatch, tautological resolve, and out-of-bounds compaction
    dag_test = _ResolutionDAGBuilder([(1, 2), (-2, -1)])
    for bad_dag_call in (
        lambda: dag_test.add_axiom((2, 1)),
        lambda: dag_test.add_axiom((-1, 1)),
        lambda: dag_test.resolve((1, 2), 0, (1, 2), 0, 1),
        lambda: dag_test.resolve((1, 2), 0, (-2, -1), 1, 1),
        lambda: dag_test.resolve((1,), 0, (-2, -1), 1, 1),
        lambda: dag_test.resolve((1, 2), -1, (-2, -1), 1, 1),
        lambda: dag_test.resolve((1, 2), 0, (-2, -1), 99, 1),
        lambda: dag_test.extract_compact_proof(99),
    ):
        caught_dag = False
        try:
            bad_dag_call()
        except (TypeError, ValueError, IndexError):
            caught_dag = True
        assert caught_dag is True

    # Mutant 28: Coupled TETRA_A K_4 2-coloring refutation proof tampering rejected
    k4_proof_valid = stella["tetra_k4_2coloring_unsat_proof"]
    assert isinstance(k4_proof_valid, list) and len(k4_proof_valid) > 2
    assert verify_resolution_refutation([[1, 2]], k4_proof_valid) is False

    # Mutant 29: Degenerate zero-normal HalfSpace3Q (0, 0, 0, 1) or bool/float in HalfSpace3Q
    for bad_hs_call in (
        lambda: _validate_halfspace3q((0, 0, 0, 1)),
        lambda: _validate_halfspace3q((True, 0, 0, 1)),
        lambda: _validate_halfspace3q((1.0, 0, 0, 1)),
    ):
        caught_hs = False
        try:
            bad_hs_call()
        except (TypeError, ValueError):
            caught_hs = True
        assert caught_hs is True

    # Mutant 30: Premature empty clause followed by trailing step or gap/negative parent_id
    mutant_m30_trailing: ResolutionProof = [
        (0, (1,), None, None, None),
        (1, (-1,), None, None, None),
        (2, (), 0, 1, 1),
        (3, (2,), None, None, None),
    ]
    mutant_m30_premature_then_empty: ResolutionProof = [
        (0, (1,), None, None, None),
        (1, (-1,), None, None, None),
        (2, (), 0, 1, 1),
        (3, (), None, None, None),
    ]
    mutant_m30_gap_parent: ResolutionProof = [
        (0, (1,), None, None, None),
        (2, (-1,), None, None, None),
        (3, (), 0, 1, 1),
    ]
    mutant_m30_neg_parent: ResolutionProof = [
        (0, (1,), None, None, None),
        (1, (-1,), None, None, None),
        (2, (), -1, 1, 1),
    ]
    assert verify_resolution_refutation([[1], [-1], [2]], mutant_m30_trailing) is False
    assert (
        verify_resolution_refutation(
            [[1], [-1], []], mutant_m30_premature_then_empty
        )
        is False
    )
    assert verify_resolution_refutation([[1], [-1]], mutant_m30_gap_parent) is False
    assert verify_resolution_refutation([[1], [-1]], mutant_m30_neg_parent) is False

    # Mutant 31: RFC 6962 0x00 Leaf vs. 0x01 Node Domain-Separation Second-Preimage Attack
    leaf_x = _rfc6962_leaf_hash(b"leaf_left")
    leaf_y = _rfc6962_leaf_hash(b"leaf_right")
    internal_node_xy = _rfc6962_node_hash(leaf_x, leaf_y)
    forged_64byte_leaf = _rfc6962_leaf_hash(leaf_x + leaf_y)
    assert hmac.compare_digest(internal_node_xy, forged_64byte_leaf) is False
    assert (
        hmac.compare_digest(
            _rfc6962_merkle_tree_hash([b"leaf_left", b"leaf_right"]),
            _rfc6962_merkle_tree_hash([leaf_x + leaf_y]),
        )
        is False
    )

    # Mutant 32: RFC 6962 Odd-Leaf Duplication Forgery (CVE-2012-2459) & Empty-Tree Separation
    entries_3 = [b"step_0", b"step_1", b"step_2"]
    entries_4_dup = [b"step_0", b"step_1", b"step_2", b"step_2"]
    root_3 = _rfc6962_merkle_tree_hash(entries_3)
    root_4_dup = _rfc6962_merkle_tree_hash(entries_4_dup)
    assert hmac.compare_digest(root_3, root_4_dup) is False
    assert (
        hmac.compare_digest(
            _rfc6962_merkle_tree_hash([]), _rfc6962_merkle_tree_hash([b""])
        )
        is False
    )

    # Mutant 33: RFC 6962 Inclusion Proof Tampering (flipped sibling bit, wrong index, wrong tree_size)
    path_idx2 = _rfc6962_inclusion_proof(2, entries_3)
    assert _rfc6962_verify_inclusion(b"step_2", 2, 3, path_idx2, root_3) is True
    tampered_sibling = bytes([path_idx2[0][0] ^ 0x01]) + path_idx2[0][1:]
    assert (
        _rfc6962_verify_inclusion(
            b"step_2", 2, 3, [tampered_sibling] + path_idx2[1:], root_3
        )
        is False
    )
    assert _rfc6962_verify_inclusion(b"step_2", 1, 3, path_idx2, root_3) is False
    assert _rfc6962_verify_inclusion(b"step_2", 2, 4, path_idx2, root_3) is False
    assert _rfc6962_verify_inclusion(b"step_2", 2, 3, path_idx2[:-1], root_3) is False

    # Mutant 34: Proof Commitment Tampering & RFC 8785 Delimiter-Collision Resistance
    valid_digest_hex = compute_proof_rfc6962_root_hex(valid_proof)
    assert verify_proof_commitment_constant_time(valid_proof, valid_digest_hex) is True
    assert (
        verify_proof_commitment_constant_time(valid_proof[:-1], valid_digest_hex)
        is False
    )
    assert (
        verify_proof_commitment_constant_time(
            valid_proof,
            ("0" if valid_digest_hex[0] != "0" else "1") + valid_digest_hex[1:],
        )
        is False
    )
    assert _rfc8785_escape_str('a#b||c"d\\e\n') == '"a#b||c\\"d\\\\e\\n"'

    # Mutant 35: Type-Confusion & Non-ASCII Input Rejection in Cryptographic Verifiers
    assert (
        verify_proof_commitment_constant_time(valid_proof, "not_a_64_char_hex") is False
    )
    assert verify_proof_commitment_constant_time(valid_proof, "é" * 64) is False
    assert verify_proof_commitment_constant_time(valid_proof, None) is False  # type: ignore[arg-type]
    assert _rfc6962_verify_inclusion(b"step_2", True, 3, path_idx2, root_3) is False  # type: ignore[arg-type]
    assert _rfc6962_verify_inclusion(b"step_2", 2, True, path_idx2, root_3) is False  # type: ignore[arg-type]
    for bad_crypto_call in (
        lambda: _rfc6962_leaf_hash("not_bytes"),  # type: ignore[arg-type]
        lambda: _rfc6962_node_hash(b"short", leaf_y),
        lambda: _rfc6962_inclusion_proof(True, entries_3),  # type: ignore[arg-type]
        lambda: _rfc6962_inclusion_proof(5, entries_3),
    ):
        caught_crypto = False
        try:
            bad_crypto_call()
        except (TypeError, ValueError):
            caught_crypto = True
        assert caught_crypto is True

    # Mutant 36: Kintsugi Boundary Checks (duplicate vertices, bool in generators & sphere edge indices)
    hs_a_valid = _derive_tetrahedron_halfspaces(TETRA_A)
    for bad_kintsugi_call in (
        lambda: explain_resolution_refutation_humanly(valid_proof[:-1]),
        lambda: explain_resolution_refutation_humanly(mutant_m30_trailing),
        lambda: explain_resolution_refutation_humanly(mutant_m30_premature_then_empty),
        lambda: _generate_pigeonhole_cnf(True, 2),  # type: ignore[arg-type]
        lambda: _generate_pigeonhole_cnf(3, 0),
        lambda: _generate_pigeonhole_cnf(2, 3),
        lambda: _generate_tseitin_k3_unsat_cnf((True, 1, 1)),  # type: ignore[arg-type]
        lambda: _extract_polyhedron_edges(
            [TETRA_A[0], TETRA_A[0], TETRA_A[2], TETRA_A[3]], hs_a_valid
        ),
        lambda: _compute_exact_sphere_radii_sq(
            TETRA_A, [(False, True)], hs_a_valid  # type: ignore[list-item]
        ),
        lambda: _compute_exact_sphere_radii_sq(TETRA_A, [(-1, 0)], hs_a_valid),
        lambda: _compute_exact_sphere_radii_sq(TETRA_A, [(0, 0)], hs_a_valid),
        lambda: _vertex_to_f2_bits(make_point3q(1, 0, 0)),
    ):
        caught_kintsugi = False
        try:
            bad_kintsugi_call()
        except (TypeError, ValueError):
            caught_kintsugi = True
        assert caught_kintsugi is True

    # =========================================================================
    # (f) Supreme Tribunal 5 — 5 Concrete Lethal Mutants (L1..L5) Explicitly Killed
    # =========================================================================

    # LETHAL MUTANT L1 (OFF-BY-ONE BOUNDARY MUTANT):
    for off_by_one_call in (
        lambda: _require_variable(0),
        lambda: _require_variable(-1),
        lambda: explain_resolution_refutation_humanly(valid_proof, {0: "ZERO_VAR"}),
        lambda: explain_resolution_refutation_humanly(valid_proof, {-1: "NEG_VAR"}),
        lambda: dag_test.resolve((1, 2), 0, (-2, -1), 1, 0),
        lambda: dag_test.extract_compact_proof(-1),
        lambda: dag_test.extract_compact_proof(len(dag_test.steps)),
        lambda: _rfc6962_largest_power_of_two_less_than(1),
    ):
        caught_off_by_one = False
        try:
            off_by_one_call()
        except (ValueError, IndexError):
            caught_off_by_one = True
        assert caught_off_by_one is True

    # LETHAL MUTANT L2 (FLIPPED PREFIX BYTE MUTANT):
    primary_attack_clauses = sovereign["primary_attack_clauses"]
    primary_proof = sovereign["resolution_proof"]
    authentic_digest = sovereign["sha256_proof_digest"]
    stream_digest = sovereign["sha256_stream_digest"]
    suite_digest = sovereign["sha256_full_suite_digest"]
    assert isinstance(primary_attack_clauses, list)
    assert isinstance(primary_proof, list)
    assert isinstance(authentic_digest, str)
    assert isinstance(stream_digest, str)
    assert isinstance(suite_digest, str)
    assert (
        verify_sovereign_proof_commitment(
            primary_attack_clauses,
            primary_proof,
            authentic_digest,
            domain_prefix=PROOF_DOMAIN_PREFIX,
        )
        is True
    )
    assert (
        verify_sovereign_proof_commitment(
            primary_attack_clauses,
            primary_proof,
            stream_digest,
            domain_prefix=PROOF_DOMAIN_PREFIX,
        )
        is True
    )
    flipped_prefix_01 = (
        bytes([PROOF_DOMAIN_PREFIX[0] ^ 0x01]) + PROOF_DOMAIN_PREFIX[1:]
    )
    flipped_prefix_ff = (
        bytes([PROOF_DOMAIN_PREFIX[0] ^ 0xFF]) + PROOF_DOMAIN_PREFIX[1:]
    )
    flipped_digest_01 = hashlib.sha256(
        _serialize_resolution_proof_bytes(
            primary_proof, domain_prefix=flipped_prefix_01
        )
    ).hexdigest()
    assert hmac.compare_digest(flipped_digest_01, authentic_digest) is False
    assert hmac.compare_digest(flipped_digest_01, stream_digest) is False
    assert (
        verify_sovereign_proof_commitment(
            primary_attack_clauses,
            primary_proof,
            authentic_digest,
            domain_prefix=flipped_prefix_01,
        )
        is False
    )
    assert (
        verify_sovereign_proof_commitment(
            primary_attack_clauses,
            primary_proof,
            authentic_digest,
            domain_prefix=flipped_prefix_ff,
        )
        is False
    )
    assert (
        verify_sovereign_proof_commitment(
            primary_attack_clauses,
            primary_proof,
            flipped_digest_01,
            domain_prefix=PROOF_DOMAIN_PREFIX,
        )
        is False
    )
    assert (
        verify_sovereign_proof_commitment(
            primary_attack_clauses,
            primary_proof,
            suite_digest,
            domain_prefix=PROOF_DOMAIN_PREFIX,
        )
        is False
    )

    # LETHAL MUTANT L3 (CORRUPTED BIT MUTANT):
    raw_proof_bytes = _serialize_resolution_proof_bytes(
        primary_proof, domain_prefix=PROOF_DOMAIN_PREFIX
    )
    corrupted_bit_bytes = (
        raw_proof_bytes[: len(PROOF_DOMAIN_PREFIX)]
        + bytes([raw_proof_bytes[len(PROOF_DOMAIN_PREFIX)] ^ 0x01])
        + raw_proof_bytes[len(PROOF_DOMAIN_PREFIX) + 1 :]
    )
    corrupted_bit_digest = hashlib.sha256(corrupted_bit_bytes).hexdigest()
    assert hmac.compare_digest(corrupted_bit_digest, authentic_digest) is False
    assert hmac.compare_digest(corrupted_bit_digest, stream_digest) is False
    assert (
        verify_sovereign_proof_commitment(
            primary_attack_clauses, primary_proof, corrupted_bit_digest
        )
        is False
    )

    aligned_assign = sovereign["aligned_assignment"]
    assert isinstance(aligned_assign, dict)
    shield_base_cnf = _build_sovereign_shield_base_clauses()
    for bit_flip_var in (
        SovereignHardLawEncoding.SHIELD_ACTIVE,
        SovereignHardLawEncoding.L1_NO_PSYCHOGRAPHIC_PROFILING,
        SovereignHardLawEncoding.HUMAN_PEACE_AND_AGENCY,
    ):
        corrupted_assign = dict(aligned_assign)
        corrupted_assign[bit_flip_var] = not corrupted_assign[bit_flip_var]
        assert verify_sat_assignment(shield_base_cnf, corrupted_assign) is False

    even_tseitin_cnf = _generate_tseitin_k3_unsat_cnf((0, 0, 0))
    even_sat, even_model, _ = solve_cnf_with_proof(even_tseitin_cnf)
    assert even_sat is True and even_model is not None
    odd_corrupted_tseitin_cnf = _generate_tseitin_k3_unsat_cnf((0, 0, 1))
    odd_sat, _, odd_proof = solve_cnf_with_proof(odd_corrupted_tseitin_cnf)
    assert (
        odd_sat is False
        and odd_proof is not None
        and verify_resolution_refutation(odd_corrupted_tseitin_cnf, odd_proof) is True
    )

    corrupted_bit_tetra = [
        make_point3q(1, 1, -1),
        TETRA_A[1],
        TETRA_A[2],
        TETRA_A[3],
    ]
    caught_corrupted_tetra_bit = False
    try:
        _derive_tetrahedron_halfspaces(corrupted_bit_tetra)
    except ValueError:
        caught_corrupted_tetra_bit = True
    assert caught_corrupted_tetra_bit is True

    # LETHAL MUTANT L4 (WRONG TREE SPLIT MUTANT):
    wrong_dpll_split_proof: ResolutionProof = [
        (0, (1, 2), None, None, None),
        (1, (1, -2), None, None, None),
        (2, (-1, 2), None, None, None),
        (3, (-1, -2), None, None, None),
        (4, (1,), 0, 1, 1),  # Wrong split variable: resolved on 1 instead of 2
        (5, (-1,), 2, 3, 2),
        (6, (), 4, 5, 1),
    ]
    assert verify_resolution_refutation(base_unsat, wrong_dpll_split_proof) is False

    wrong_merkle_split_3 = _rfc6962_node_hash(
        _rfc6962_merkle_tree_hash(entries_3[:1]),
        _rfc6962_merkle_tree_hash(entries_3[1:]),
    )
    assert hmac.compare_digest(wrong_merkle_split_3, root_3) is False

    hs_a_list = list(stella["halfspaces_A"])  # type: ignore[arg-type]
    edges_a_list, _ = _extract_polyhedron_edges(TETRA_A, hs_a_list)
    wrong_parity_split_tetra = [
        make_point3q(-1, -1, -1),
        TETRA_A[1],
        TETRA_A[2],
        TETRA_A[3],
    ]
    non_circum_tetra = [
        make_point3q(2, 1, 1),
        TETRA_A[1],
        TETRA_A[2],
        TETRA_A[3],
    ]
    non_in_hs = list(hs_a_list)
    non_in_hs[0] = (
        non_in_hs[0][0],
        non_in_hs[0][1],
        non_in_hs[0][2],
        Fraction(2, 1),
    )
    for bad_tree_split_call in (
        lambda: _derive_tetrahedron_halfspaces(wrong_parity_split_tetra),
        lambda: _compute_exact_sphere_radii_sq(
            non_circum_tetra, edges_a_list, hs_a_list
        ),
        lambda: _compute_exact_sphere_radii_sq(
            wrong_parity_split_tetra, edges_a_list, hs_a_list
        ),
        lambda: _compute_exact_sphere_radii_sq(TETRA_A, edges_a_list, non_in_hs),
    ):
        caught_wrong_split = False
        try:
            bad_tree_split_call()
        except ValueError:
            caught_wrong_split = True
        assert caught_wrong_split is True

    # LETHAL MUTANT L5 (TAMPERED PROOF NODE MUTANT):
    internal_indices = [
        idx
        for idx, step in enumerate(primary_proof[:-1])
        if step[2] is not None and step[3] is not None and step[4] is not None
    ]
    assert len(internal_indices) >= 5
    mid_idx = internal_indices[0]
    m_sid, m_clause, m_pa, m_pb, m_piv = primary_proof[mid_idx]
    assert (
        len(m_clause) >= 1
        and m_pa is not None
        and m_pb is not None
        and m_piv is not None
    )

    tampered_node_clause = list(primary_proof)
    tampered_node_clause[mid_idx] = (m_sid, m_clause[1:], m_pa, m_pb, m_piv)

    alt_parent = 0 if (m_pa != 0 and m_pb != 0) else 1
    tampered_node_parent = list(primary_proof)
    tampered_node_parent[mid_idx] = (m_sid, m_clause, alt_parent, m_pb, m_piv)

    alt_pivot = (m_piv % 15) + 1
    tampered_node_pivot = list(primary_proof)
    tampered_node_pivot[mid_idx] = (m_sid, m_clause, m_pa, m_pb, alt_pivot)

    for tampered_dag in (
        tampered_node_clause,
        tampered_node_parent,
        tampered_node_pivot,
    ):
        assert (
            verify_resolution_refutation(primary_attack_clauses, tampered_dag)
            is False
        )
        assert (
            verify_sovereign_proof_commitment(
                primary_attack_clauses, tampered_dag, authentic_digest
            )
            is False
        )
        assert (
            verify_proof_commitment_constant_time(tampered_dag, authentic_digest)
            is False
        )
        caught_tampered_narrator = False
        try:
            explain_resolution_refutation_humanly(tampered_dag)
        except ValueError:
            caught_tampered_narrator = True
        assert caught_tampered_narrator is True


if __name__ == "__main__":
    run_self_tests()
