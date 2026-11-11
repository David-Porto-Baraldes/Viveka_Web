"""
Reed-Muller RM(1, m) Exact Rational Fast Walsh-Hadamard Decoder &
IETF RFC 6962 Binary Merkle Tree with Consistency Subproofs.

Standard-library-only module (`dataclasses`, `fractions`, `hashlib`, `hmac`, `typing`)
implementing exact integer/rational maximum-likelihood decoding (zero floating-point
operations) and constant-time RFC 6962 cryptographic consistency verification.
"""

import dataclasses
import fractions
import hashlib
import hmac
import typing

__all__ = [
    "RMCodeParameters",
    "RationalLLR",
    "rm_encode",
    "fast_walsh_hadamard_transform",
    "rm_decode_soft_rational",
    "merkle_tree_hash",
    "merkle_consistency_proof",
    "verify_merkle_consistency_proof",
    "run_self_tests",
]

RationalLLR: typing.TypeAlias = fractions.Fraction | int


# ============================================================================
# 1. General First-Order Reed-Muller Code RM(1, m) & O(N log N) FWHT Decoder
# ============================================================================


@dataclasses.dataclass(frozen=True)
class RMCodeParameters:
    """
    Immutable structural parameters for a First-Order Reed-Muller code RM(1, m):
      - block_length:      N = 2^m
      - dimension:         k = m + 1
      - minimum_distance:  d_min = 2^(m - 1)
      - correction_radius: t = floor((d_min - 1) / 2) = 2^(m - 2) - 1
    """

    m: int
    block_length: int
    dimension: int
    minimum_distance: int
    correction_radius: int

    @classmethod
    def for_order_one(cls, m: int) -> "RMCodeParameters":
        if not isinstance(m, int) or isinstance(m, bool) or m < 1:
            raise ValueError(f"RM(1, m) requires an integer m >= 1, got {m!r}")
        block_length = 1 << m
        dimension = m + 1
        minimum_distance = 1 << (m - 1)
        correction_radius = (minimum_distance - 1) // 2
        return cls(
            m=m,
            block_length=block_length,
            dimension=dimension,
            minimum_distance=minimum_distance,
            correction_radius=correction_radius,
        )


def _gcd_int(a: int, b: int) -> int:
    """Exact greatest common divisor over integers via Euclid's algorithm."""
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


def _lcm_int(a: int, b: int) -> int:
    """Exact least common multiple of two integers."""
    if a == 0 or b == 0:
        return 0
    return abs((a // _gcd_int(a, b)) * b)


def _rm_encode_unchecked(message_bits: list[int], m: int) -> list[int]:
    """
    Internal O(N) recursive truth-table doubling kernel for pre-validated inputs.
    Uses list comprehension doubling to avoid generator frame suspension overhead.
    """
    codeword: list[int] = [message_bits[0]]
    for j in range(m):
        if message_bits[j + 1]:
            codeword += [b ^ 1 for b in codeword]
        else:
            codeword += codeword
    return codeword


def rm_encode(message_bits: list[int], m: int) -> list[int]:
    """
    Encode k = m + 1 message bits [u_0, u_1, ..., u_m] into an N = 2^m bit
    First-Order Reed-Muller RM(1, m) codeword over GF(2).

    For evaluation coordinate x in {0, ..., 2^m - 1} with binary expansion
    x = sum_{j=0}^{m-1} x_j * 2^j, codeword bit c[x] is:
        c[x] = (u_0 + sum_{j=0}^{m-1} u_{j+1} * x_j) mod 2.
    Constructed in O(N) exact operations via recursive Boolean doubling.
    """
    params = RMCodeParameters.for_order_one(m)
    if not isinstance(message_bits, list) or len(message_bits) != params.dimension:
        raise ValueError(
            f"Expected list of {params.dimension} message bits for RM(1, {m}), "
            f"got {len(message_bits) if isinstance(message_bits, list) else type(message_bits).__name__}"
        )
    clean_bits: list[int] = []
    for idx, bit in enumerate(message_bits):
        if type(bit) is not int:
            if not isinstance(bit, int) or isinstance(bit, bool):
                raise ValueError(
                    f"Message bit at index {idx} must be int 0 or 1, got {bit!r}"
                )
            bit = int(bit)
        if bit != 0 and bit != 1:
            raise ValueError(f"Message bit at index {idx} must be 0 or 1, got {bit!r}")
        clean_bits.append(bit)

    return _rm_encode_unchecked(clean_bits, m)


def _fwht_inplace(result: list[int]) -> list[int]:
    """
    Internal O(N log N) in-place iterative radix-2 Sylvester FWHT kernel over Z.
    """
    n = len(result)
    h = 1
    while h < n:
        step = h << 1
        for base in range(0, n, step):
            for offset in range(base, base + h):
                left = result[offset]
                right = result[offset + h]
                result[offset] = left + right
                result[offset + h] = left - right
        h = step
    return result


def fast_walsh_hadamard_transform(vec: list[int]) -> list[int]:
    """
    Compute the exact 1D Fast Walsh-Hadamard Transform W = H_m * vec in O(N log N)
    using strictly exact integer arithmetic (zero floats).

    For N = 2^m, returns a new list W (leaving `vec` unmutated) where:
        W[w] = sum_{x=0}^{N-1} vec[x] * (-1)^(<w, x>_2)
    and <w, x>_2 = popcount(w & x) mod 2.
    """
    if not isinstance(vec, list) or len(vec) == 0:
        raise ValueError("Input vector to FWHT must be a non-empty list of integers.")
    n = len(vec)
    if (n & (n - 1)) != 0:
        raise ValueError(f"FWHT length must be a positive power of two, got {n}.")
    clean_vec: list[int] = []
    for idx, val in enumerate(vec):
        if type(val) is not int:
            if not isinstance(val, int) or isinstance(val, bool):
                raise ValueError(
                    f"FWHT requires exact int elements; got {val!r} at index {idx}."
                )
            val = int(val)
        clean_vec.append(val)

    return _fwht_inplace(clean_vec)


def rm_decode_soft_rational(
    received_llr: list[fractions.Fraction | int],
    m: int,
) -> tuple[list[int], list[int], bool]:
    """
    Maximum-likelihood soft-decision decoder for RM(1, m) over Q in O(N log N)
    via exact denominator-cleared Fast Walsh-Hadamard Transform.

    Convention:
      - Positive LLR favors bit 0 (BPSK +1).
      - Negative LLR favors bit 1 (BPSK -1).
      - Zero LLR indicates an erasure / complete bit ambiguity.

    Returns:
      (decoded_message_bits, decoded_codeword, is_unique_ml_winner)
      where `is_unique_ml_winner` is True iff a single codeword strictly
      maximizes the rational correlation metric among all 2^(m+1) codewords.
    """
    params = RMCodeParameters.for_order_one(m)
    if not isinstance(received_llr, list) or len(received_llr) != params.block_length:
        raise ValueError(
            f"Expected received_llr of length {params.block_length} for RM(1, {m}), "
            f"got {len(received_llr) if isinstance(received_llr, list) else type(received_llr).__name__}"
        )

    numerators: list[int] = []
    denominators: list[int] = []
    common_den = 1

    for idx, val in enumerate(received_llr):
        if type(val) is int:
            numerators.append(val)
            denominators.append(1)
        elif type(val) is fractions.Fraction:
            num = val.numerator
            den = val.denominator
            numerators.append(num)
            denominators.append(den)
            if den != 1 and common_den % den != 0:
                common_den = _lcm_int(common_den, den)
        elif isinstance(val, bool):
            raise TypeError(
                f"received_llr[{idx}] must be int or fractions.Fraction, got bool"
            )
        elif isinstance(val, int):
            numerators.append(int(val))
            denominators.append(1)
        elif isinstance(val, fractions.Fraction):
            num = int(val.numerator)
            den = int(val.denominator)
            numerators.append(num)
            denominators.append(den)
            if den != 1 and common_den % den != 0:
                common_den = _lcm_int(common_den, den)
        else:
            raise TypeError(
                f"received_llr[{idx}] must be int or fractions.Fraction, got {type(val).__name__}"
            )

    if common_den == 1:
        scaled_int_llr = numerators
    else:
        scaled_int_llr = [
            num * (common_den // den) for num, den in zip(numerators, denominators)
        ]

    spectrum = _fwht_inplace(scaled_int_llr)

    best_abs = -1
    best_w = 0
    tie_count = 0

    for w, coeff in enumerate(spectrum):
        abs_coeff = -coeff if coeff < 0 else coeff
        if abs_coeff > best_abs:
            best_abs = abs_coeff
            best_w = w
            tie_count = 1
        elif abs_coeff == best_abs:
            tie_count += 1

    # By INV-RM-4, if best_abs == 0, every (u_0=0, w) and (u_0=1, w) yields correlation 0 (2^(m+1)-way tie).
    is_unique_ml_winner = (best_abs > 0) and (tie_count == 1)

    u_0 = 0 if spectrum[best_w] >= 0 else 1
    decoded_message_bits: list[int] = [u_0] + [(best_w >> j) & 1 for j in range(m)]
    decoded_codeword = _rm_encode_unchecked(decoded_message_bits, m)

    return decoded_message_bits, decoded_codeword, is_unique_ml_winner


# ============================================================================
# 2. IETF RFC 6962 §2.1.1 & §2.1.2 Binary Merkle Tree & Consistency Proofs
# ============================================================================

_EMPTY_TREE_HASH: typing.Final[bytes] = hashlib.sha256(b"").digest()
_LEAF_PREFIX: typing.Final[bytes] = b"\x00"
_NODE_PREFIX: typing.Final[bytes] = b"\x01"
_SHA256_DIGEST_SIZE: typing.Final[int] = 32


def _hash_leaf(data: bytes) -> bytes:
    """RFC 6962 §2.1 domain-separated leaf hash: SHA-256(0x00 || data)."""
    return hashlib.sha256(_LEAF_PREFIX + data).digest()


def _hash_internal(left: bytes, right: bytes) -> bytes:
    """RFC 6962 §2.1 domain-separated internal node hash: SHA-256(0x01 || left || right)."""
    return hashlib.sha256(_NODE_PREFIX + left + right).digest()


def _largest_power_of_two_less_than(n: int) -> int:
    """Return the largest power of two k such that k < n for integer n >= 2."""
    if n < 2:
        raise ValueError(f"n must be >= 2 to split, got {n}")
    return 1 << ((n - 1).bit_length() - 1)


def _validate_leaves(leaves: list[bytes]) -> int:
    """Validate that `leaves` is a list of `bytes` objects and return its length."""
    if not isinstance(leaves, list):
        raise TypeError(f"leaves must be a list of bytes, got {type(leaves).__name__}")
    for idx, leaf in enumerate(leaves):
        if type(leaf) is not bytes and not isinstance(leaf, bytes):
            raise TypeError(
                f"Leaf at index {idx} must be bytes, got {type(leaf).__name__}"
            )
    return len(leaves)


def _mth_range(leaves: list[bytes], lo: int, hi: int) -> bytes:
    """Zero-slice index-window computation of RFC 6962 §2.1 MTH(D[lo:hi])."""
    n = hi - lo
    if n == 0:
        return _EMPTY_TREE_HASH
    if n == 1:
        return _hash_leaf(leaves[lo])
    k = _largest_power_of_two_less_than(n)
    left_hash = _mth_range(leaves, lo, lo + k)
    right_hash = _mth_range(leaves, lo + k, hi)
    return _hash_internal(left_hash, right_hash)


def merkle_tree_hash(leaves: list[bytes]) -> bytes:
    """
    Compute the IETF RFC 6962 §2.1 Merkle Tree Hash MTH(D[n]).

      - MTH({})     = SHA-256(b"")
      - MTH({d(0)}) = SHA-256(0x00 || d(0))
      - MTH(D[n])   = SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n]))
        where k is the largest power of two strictly less than n (k < n).
    """
    n = _validate_leaves(leaves)
    return _mth_range(leaves, 0, n)


def _subproof_range(
    leaves: list[bytes],
    lo: int,
    hi: int,
    m: int,
    is_start_root: bool,
) -> list[bytes]:
    """Zero-slice index-window implementation of RFC 6962 §2.1.2 SUBPROOF(m, D[lo:hi], b)."""
    n = hi - lo
    if m == n:
        if is_start_root:
            return []
        return [_mth_range(leaves, lo, hi)]

    k = _largest_power_of_two_less_than(n)
    if m <= k:
        proof = _subproof_range(leaves, lo, lo + k, m, is_start_root)
        proof.append(_mth_range(leaves, lo + k, hi))
        return proof
    else:
        proof = _subproof_range(leaves, lo + k, hi, m - k, False)
        proof.append(_mth_range(leaves, lo, lo + k))
        return proof


def merkle_consistency_proof(leaves: list[bytes], m: int) -> list[bytes]:
    """
    Generate the IETF RFC 6962 §2.1.2 Merkle consistency proof:
        PROOF(m, D[n]) = SUBPROOF(m, D[n], True)
    for 1 <= m <= n = len(leaves).
    """
    n = _validate_leaves(leaves)
    if not isinstance(m, int) or isinstance(m, bool) or m < 1 or m > n:
        raise ValueError(
            f"Consistency proof requires integer 1 <= m <= n ({n}), got m={m!r}"
        )
    return _subproof_range(leaves, 0, n, m, True)


def verify_merkle_consistency_proof(
    first_size: int,
    second_size: int,
    first_root: bytes,
    second_root: bytes,
    proof: list[bytes],
) -> bool:
    """
    Verify an IETF RFC 6962 §2.1.2 Merkle consistency proof between tree sizes
    `first_size` (m) and `second_size` (n) using exact bit-decomposition
    and constant-time `hmac.compare_digest` root verification.

    Acts as a total boolean verifier: any malformed size, oversized proof,
    non-bytes digest, wrong digest length, or tampered proof node returns `False`
    without raising.
    """
    if (
        not isinstance(first_size, int)
        or isinstance(first_size, bool)
        or not isinstance(second_size, int)
        or isinstance(second_size, bool)
    ):
        return False

    if first_size <= 0 or second_size <= 0 or first_size > second_size:
        return False

    if (
        not isinstance(first_root, bytes)
        or len(first_root) != _SHA256_DIGEST_SIZE
        or not isinstance(second_root, bytes)
        or len(second_root) != _SHA256_DIGEST_SIZE
    ):
        return False

    if not isinstance(proof, list):
        return False

    max_proof_len = (
        0 if first_size == second_size else (second_size - 1).bit_length() + 1
    )
    if len(proof) > max_proof_len:
        return False

    for node in proof:
        if not isinstance(node, bytes) or len(node) != _SHA256_DIGEST_SIZE:
            return False

    if first_size == second_size:
        return hmac.compare_digest(first_root, second_root)

    if len(proof) == 0:
        return False

    fn = first_size - 1
    sn = second_size - 1

    # Strip trailing 1-bits of fn in O(1) where first_size is aligned to a power-of-two boundary.
    tz_ones = (~fn & (fn + 1)).bit_length() - 1
    if tz_ones:
        fn >>= tz_ones
        sn >>= tz_ones

    # If fn == 0, first_size is an exact power of two, so first_root is the base subtree.
    # Otherwise, proof[0] is the base subtree MTH(D[m - lsb(m) : m]).
    if fn == 0:
        fr = first_root
        sr = first_root
        idx = 0
    else:
        fr = proof[0]
        sr = proof[0]
        idx = 1

    while sn > 0:
        if idx >= len(proof):
            return False
        sibling = proof[idx]
        idx += 1

        if (fn & 1) == 1 or fn == sn:
            # Left sibling `sibling` is combined into both the m-tree (`fr`) and n-tree (`sr`).
            # When fn == sn and (fn & 1) == 0, we have reached the root of an incomplete
            # right subtree of D[n]; jumping right by trailing zeros of fn in O(1) skips
            # absent intermediate power-of-two levels in exact lockstep with top-down SUBPROOF.
            fr = _hash_internal(sibling, fr)
            sr = _hash_internal(sibling, sr)
            if fn > 0:
                tz_zeros = (fn & -fn).bit_length() - 1
                if tz_zeros:
                    fn >>= tz_zeros
                    sn >>= tz_zeros
        else:
            # Right sibling `sibling` belongs only to the newer n-tree (`sr`).
            sr = _hash_internal(sr, sibling)

        fn >>= 1
        sn >>= 1

    if idx != len(proof):
        return False

    first_matches = hmac.compare_digest(fr, first_root)
    second_matches = hmac.compare_digest(sr, second_root)
    return bool(first_matches & second_matches)


# ============================================================================
# 3. Exhaustive Self-Test & Adversarial Mutant Suite
# ============================================================================


def _int_to_bits(val: int, length: int) -> list[int]:
    return [(val >> i) & 1 for i in range(length)]


def _codeword_to_bipolar(codeword: list[int]) -> list[int]:
    return [1 if bit == 0 else -1 for bit in codeword]


def _rm_encode_reference_inner_product(message_bits: list[int], m: int) -> list[int]:
    """Reference O(N) bit-mask inner-product encoder for cross-verification."""
    u0 = message_bits[0]
    mask = 0
    for j in range(m):
        if message_bits[j + 1]:
            mask |= 1 << j
    return [u0 ^ ((x & mask).bit_count() & 1) for x in range(1 << m)]


def _brute_force_rational_ml_oracle(
    received_llr: list[fractions.Fraction | int],
    all_messages: list[list[int]],
    all_codewords: list[list[int]],
) -> tuple[list[list[int]], fractions.Fraction]:
    """
    Reference exact rational inner-product ML oracle over Q: evaluates
    sum_{x=0}^{N-1} L_x * (-1)^{c[x]} directly in Q across all 2^(m+1) codewords.
    """
    best_corr: fractions.Fraction | None = None
    winners: list[list[int]] = []
    for msg, cw in zip(all_messages, all_codewords):
        corr = fractions.Fraction(0, 1)
        for llr, bit in zip(received_llr, cw):
            corr += llr if bit == 0 else -llr
        if best_corr is None or corr > best_corr:
            best_corr = corr
            winners = [msg]
        elif corr == best_corr:
            winners.append(msg)
    assert best_corr is not None
    return winners, best_corr


def _test_rm_1_3_exhaustive() -> None:
    """
    Exhaustively verify RM(1, 3) ([8, 4, 4]_2, d_min = 4, t = 1):
      - Equivalence between recursive Boolean doubling and affine inner product.
      - Minimum distance d_min = 4 across all 16 codewords.
      - Parseval's identity sum(W[u]^2) == N^2 == 64 for all bipolar codewords,
        general Parseval identity sum(W[u]^2) == N * sum(v[x]^2) for arbitrary
        integer vectors (including all-zero), and involution FWHT(FWHT(v)) == N * v.
      - Direct isomorphism against exact brute-force Q-correlation oracle for
        asymmetric prime-denominator LLRs (both positive u_0=0 and negated u_0=1
        spectral peaks), beyond-t soft recovery, non-uniform rational ties (both
        same-sign and antipodal mixed-sign +M* vs -M*), and sub-IEEE-754-float64
        (10^-18) tie-breaking perturbations.
      - Exhaustive 0-bit and 1-bit error correction across all 16 messages with
        prime-denominator rational LLRs and mixed (int | Fraction) LLRs.
      - Exhaustive 2-bit (d_min / 2 = 2) tie detection across all 16 * 28 = 448 pairs,
        plus all-zero erasure tie detection.
    """
    m = 3
    params = RMCodeParameters.for_order_one(m)
    assert (params.block_length, params.dimension, params.minimum_distance) == (8, 4, 4)
    assert params.correction_radius == 1

    all_messages = [
        _int_to_bits(msg_int, params.dimension)
        for msg_int in range(1 << params.dimension)
    ]
    all_codewords = [rm_encode(msg, m) for msg in all_messages]

    for idx, (msg, cw) in enumerate(zip(all_messages, all_codewords)):
        assert cw == _rm_encode_reference_inner_product(msg, m)
        bipolar = _codeword_to_bipolar(cw)
        spectrum = fast_walsh_hadamard_transform(bipolar)
        parseval_lhs = sum([w * w for w in spectrum])
        assert parseval_lhs == params.block_length * params.block_length, (
            f"Parseval identity failed on RM(1, 3) codeword {idx}: {parseval_lhs} != 64"
        )
        for other_idx in range(idx + 1, len(all_codewords)):
            dist = sum([a ^ b for a, b in zip(cw, all_codewords[other_idx])])
            assert dist >= params.minimum_distance, (
                f"RM(1, 3) distance violation between {idx} and {other_idx}: {dist}"
            )

    # General integer Parseval identity (including all-zero vector) and FWHT involution
    zero_spec = fast_walsh_hadamard_transform([0] * params.block_length)
    assert (
        zero_spec == [0] * params.block_length
        and sum([w * w for w in zero_spec]) == 0
    )
    asymmetric_vec = [3, -5, 7, 0, -2, 11, -13, 4]
    asymmetric_spec = fast_walsh_hadamard_transform(asymmetric_vec)
    assert sum([w * w for w in asymmetric_spec]) == params.block_length * sum(
        [x * x for x in asymmetric_vec]
    )
    involution_vec = fast_walsh_hadamard_transform(asymmetric_spec)
    assert involution_vec == [params.block_length * x for x in asymmetric_vec]

    # 1. Cross-check FWHT decoder against exact brute-force Q-correlation oracle
    oracle_llr: list[fractions.Fraction | int] = [
        fractions.Fraction(5, 3),
        fractions.Fraction(-7, 5),
        fractions.Fraction(11, 7),
        fractions.Fraction(-2, 11),
        fractions.Fraction(-13, 13),
        fractions.Fraction(4, 5),
        fractions.Fraction(-9, 7),
        3,
    ]
    winners, _ = _brute_force_rational_ml_oracle(
        oracle_llr, all_messages, all_codewords
    )
    dec_o_msg, dec_o_cw, dec_o_uniq = rm_decode_soft_rational(oracle_llr, m)
    assert dec_o_uniq is True and len(winners) == 1
    assert dec_o_msg == winners[0] and dec_o_cw == rm_encode(dec_o_msg, m)

    # Also verify the negated oracle vector uniquely recovers the antipodal coset (u_0 = 1)
    neg_oracle_llr: list[fractions.Fraction | int] = [-x for x in oracle_llr]
    neg_winners, _ = _brute_force_rational_ml_oracle(
        neg_oracle_llr, all_messages, all_codewords
    )
    dec_no_msg, dec_no_cw, dec_no_uniq = rm_decode_soft_rational(neg_oracle_llr, m)
    assert dec_no_uniq is True and len(neg_winners) == 1
    assert dec_no_msg == neg_winners[0] and dec_no_cw == rm_encode(dec_no_msg, m)
    assert dec_no_msg[0] == (dec_o_msg[0] ^ 1) and dec_no_msg[1:] == dec_o_msg[1:]

    # 2. All-zero erasure vector must report a 16-way tie (is_unique_ml_winner is False)
    zero_frac = fractions.Fraction(0, 1)
    zero_llr: list[fractions.Fraction | int] = [zero_frac] * params.block_length
    _, _, unique_zero = rm_decode_soft_rational(zero_llr, m)
    zero_winners, _ = _brute_force_rational_ml_oracle(
        zero_llr, all_messages, all_codewords
    )
    assert unique_zero is False and len(zero_winners) == 16

    # 3. Soft-decision recovery beyond hard-decision radius t = 1:
    # 2 sign flips (weight 2 > t) with weak rational reliability (-1/5, -1/7)
    # vs strong reliability (+1) on the 6 uncorrupted coordinates of all-zero codeword.
    soft_beyond_t: list[fractions.Fraction | int] = [
        fractions.Fraction(-1, 5),
        fractions.Fraction(-1, 7),
        1,
        1,
        1,
        1,
        1,
        1,
    ]
    dec_soft_msg, dec_soft_cw, uniq_soft = rm_decode_soft_rational(soft_beyond_t, m)
    soft_winners, _ = _brute_force_rational_ml_oracle(
        soft_beyond_t, all_messages, all_codewords
    )
    assert uniq_soft is True and soft_winners == [[0, 0, 0, 0]]
    assert dec_soft_msg == [0, 0, 0, 0] and dec_soft_cw == [0] * 8

    # 4. Heterogeneous rational LLR tie & sub-float64 (+10^-18) perturbation resolution:
    # First 4 coordinates sum to 4/3 + 7/6 + 5/4 + 5/4 = +5;
    # last 4 coordinates sum to -2/5 - 1/10 + 3/20 + 7/20 = 0 (with |L_4|+..+|L_7| = 1).
    # Thus masks w=0 ([0,0,0,0]) and w=4 ([0,0,0,1]) both achieve exact rational
    # correlation +5 (2-way tie), while all other masks w have |W[w]| <= 7/6 < 5.
    rational_tie_llr: list[fractions.Fraction | int] = [
        fractions.Fraction(4, 3),
        fractions.Fraction(7, 6),
        fractions.Fraction(5, 4),
        fractions.Fraction(5, 4),
        fractions.Fraction(-2, 5),
        fractions.Fraction(-1, 10),
        fractions.Fraction(3, 20),
        fractions.Fraction(7, 20),
    ]
    _, _, is_unique_rat_tie = rm_decode_soft_rational(rational_tie_llr, m)
    tie_winners, tie_corr = _brute_force_rational_ml_oracle(
        rational_tie_llr, all_messages, all_codewords
    )
    assert is_unique_rat_tie is False and len(tie_winners) == 2 and tie_corr == 5

    # Perturbing coordinate 7 by +10^-18 (strictly below IEEE-754 float64 machine epsilon 2^-53)
    # breaks the tie uniquely in favor of w=0 ([0, 0, 0, 0]) in exact Q -> Z arithmetic.
    perturbed_llr = list(rational_tie_llr)
    perturbed_llr[7] = fractions.Fraction(7, 20) + fractions.Fraction(1, 10**18)
    dec_msg_p, dec_cw_p, is_unique_p = rm_decode_soft_rational(perturbed_llr, m)
    perturbed_winners, _ = _brute_force_rational_ml_oracle(
        perturbed_llr, all_messages, all_codewords
    )
    assert is_unique_p is True and perturbed_winners == [[0, 0, 0, 0]]
    assert dec_msg_p == [0, 0, 0, 0] and dec_cw_p == [0] * 8

    # 5. Antipodal mixed-sign spectral tie (W[0] = -5 vs W[4] = +5) & -10^-18 perturbation:
    # First 4 coordinates sum to 0; last 4 coordinates sum to -5.
    # Thus mask w=0 attains W[0] = -5 (winner [1,0,0,0] with u_0=1, correlation +5)
    # and mask w=4 attains W[4] = +5 (winner [0,0,0,1] with u_0=0, correlation +5).
    mixed_sign_tie_llr: list[fractions.Fraction | int] = [
        fractions.Fraction(-2, 5),
        fractions.Fraction(-1, 10),
        fractions.Fraction(3, 20),
        fractions.Fraction(7, 20),
        fractions.Fraction(-4, 3),
        fractions.Fraction(-7, 6),
        fractions.Fraction(-5, 4),
        fractions.Fraction(-5, 4),
    ]
    _, _, is_unique_mixed_tie = rm_decode_soft_rational(mixed_sign_tie_llr, m)
    mixed_winners, mixed_corr = _brute_force_rational_ml_oracle(
        mixed_sign_tie_llr, all_messages, all_codewords
    )
    assert is_unique_mixed_tie is False and len(mixed_winners) == 2 and mixed_corr == 5

    # Perturbing coordinate 0 by -10^-18 makes W[0] = -5 - 10^-18 (|W[0]| > |W[4]|),
    # selecting the antipodal coset winner [1, 0, 0, 0] (u_0 = 1) uniquely.
    perturbed_mixed_llr = list(mixed_sign_tie_llr)
    perturbed_mixed_llr[0] = fractions.Fraction(-2, 5) - fractions.Fraction(1, 10**18)
    dec_msg_pm, dec_cw_pm, is_unique_pm = rm_decode_soft_rational(
        perturbed_mixed_llr, m
    )
    pm_winners, _ = _brute_force_rational_ml_oracle(
        perturbed_mixed_llr, all_messages, all_codewords
    )
    assert is_unique_pm is True and pm_winners == [[1, 0, 0, 0]]
    assert dec_msg_pm == [1, 0, 0, 0] and dec_cw_pm == [1] * 8

    # Pre-construct rational scale factors with prime denominators
    prime_denoms = (3, 5, 7, 11, 13, 5, 7, 3)
    pos_fracs = [fractions.Fraction(2, d) for d in prime_denoms]
    neg_fracs = [fractions.Fraction(-2, d) for d in prime_denoms]

    for msg, cw in zip(all_messages, all_codewords):
        bipolar = _codeword_to_bipolar(cw)
        frac_llr: list[fractions.Fraction | int] = [
            pos_fracs[i] if bipolar[i] > 0 else neg_fracs[i]
            for i in range(params.block_length)
        ]
        # Mix exact int and Fraction in coordinate 0 to verify heterogeneous union handling
        frac_llr[0] = 2 * bipolar[0]
        dec_msg, dec_cw, is_unique = rm_decode_soft_rational(frac_llr, m)
        assert is_unique is True and dec_msg == msg and dec_cw == cw

        # All 8 single-bit hard flips (weight 1 <= t = 1)
        for err_pos in range(params.block_length):
            corrupted_1 = list(bipolar)
            corrupted_1[err_pos] = -corrupted_1[err_pos]
            dec_msg, dec_cw, is_unique = rm_decode_soft_rational(corrupted_1, m)
            assert is_unique is True and dec_msg == msg and dec_cw == cw

        # All 28 double-bit hard flips (weight 2 == d_min / 2 -> tie)
        for i in range(params.block_length):
            for j in range(i + 1, params.block_length):
                corrupted_2 = list(bipolar)
                corrupted_2[i] = -corrupted_2[i]
                corrupted_2[j] = -corrupted_2[j]
                _, _, is_unique_tie = rm_decode_soft_rational(corrupted_2, m)
                assert is_unique_tie is False, (
                    f"Expected tie at weight d_min/2=2 for indices ({i}, {j})"
                )


def _test_rm_1_5_exhaustive_and_multi_error() -> None:
    """
    Verify RM(1, 5) ([32, 6, 16]_2, d_min = 16, t = 7):
      - All 64 codewords satisfy weight distribution {0, 16, 32} and Parseval's
        identity sum(W[u]^2) == 32^2 == 1024.
      - Single-bit errors (w = 1) and multi-bit error patterns across every weight
        w in {1, 2, 3, 4, 5, 6, 7} up to t = 7 are uniquely corrected, including
        exact rational Fraction LLR scaling.
      - Soft erasure recovery: 7 bit flips + 1 zero-LLR erasure decodes uniquely.
      - Half-distance weight d_min / 2 = 8 error patterns trigger tie detection
        (`is_unique_ml_winner is False`) across all 64 codewords.
    """
    m = 5
    params = RMCodeParameters.for_order_one(m)
    assert (params.block_length, params.dimension, params.minimum_distance) == (
        32,
        6,
        16,
    )
    assert params.correction_radius == 7

    all_messages = [
        _int_to_bits(msg_int, params.dimension)
        for msg_int in range(1 << params.dimension)
    ]
    all_codewords = [rm_encode(msg, m) for msg in all_messages]

    half_d_positions = [x for x in range(params.block_length) if (x & 1) == 1][:8]
    assert len(half_d_positions) == 8

    for idx, (msg, cw) in enumerate(zip(all_messages, all_codewords)):
        assert cw == _rm_encode_reference_inner_product(msg, m)
        bipolar = _codeword_to_bipolar(cw)
        spectrum = fast_walsh_hadamard_transform(bipolar)
        assert (
            sum([w * w for w in spectrum])
            == params.block_length * params.block_length
        )
        if idx > 0:
            assert sum(cw) in (params.minimum_distance, params.block_length)

        # Verify weight d_min / 2 = 8 half-distance tie detection on all 64 codewords
        tied_bipolar = list(bipolar)
        for pos in half_d_positions:
            tied_bipolar[pos] = -tied_bipolar[pos]
        _, _, is_unique_tie = rm_decode_soft_rational(tied_bipolar, m)
        assert is_unique_tie is False

    # Pre-construct exact Fraction constants once
    f_pos = fractions.Fraction(7, 3)
    f_neg = fractions.Fraction(-7, 3)
    f_zero = fractions.Fraction(0, 1)

    # Test all 32 single-bit errors, all weights w in 1..7, and soft rational
    # LLRs across representative codewords spanning the code space
    representative_indices = (0, 1, 7, 21, 42, 63)
    for msg_idx in representative_indices:
        msg = all_messages[msg_idx]
        cw = all_codewords[msg_idx]
        bipolar = _codeword_to_bipolar(cw)

        # All 32 single-bit errors
        for pos in range(params.block_length):
            corrupted = list(bipolar)
            corrupted[pos] = -corrupted[pos]
            dec_msg, dec_cw, is_unique = rm_decode_soft_rational(corrupted, m)
            assert is_unique is True and dec_msg == msg and dec_cw == cw

        # Multi-bit errors for every weight w in 1..7 with exact rational Fraction LLRs
        # Since gcd(3, 32) == 1, (msg_idx * 5 + 3 * k) % 32 generates distinct indices in O(1)
        base_rational = [f_pos if b > 0 else f_neg for b in bipolar]
        for weight in range(1, params.correction_radius + 1):
            rational_llr = list(base_rational)
            for k in range(weight):
                pos = (msg_idx * 5 + 3 * k) % params.block_length
                rational_llr[pos] = -rational_llr[pos]

            dec_msg, dec_cw, is_unique = rm_decode_soft_rational(rational_llr, m)
            assert is_unique is True and dec_msg == msg and dec_cw == cw

        # 7 bit flips + 1 coordinate zero-LLR erasure (effective distance 7.5 < 8)
        erasure_llr = list(base_rational)
        for pos in half_d_positions[:7]:
            erasure_llr[pos] = -erasure_llr[pos]
        erasure_llr[half_d_positions[7]] = f_zero
        dec_msg_er, dec_cw_er, is_unique_er = rm_decode_soft_rational(erasure_llr, m)
        assert is_unique_er is True and dec_msg_er == msg and dec_cw_er == cw


def _test_rfc6962_merkle_consistency_and_adversarial() -> None:
    """
    Verify IETF RFC 6962 §2.1.1 & §2.1.2 Merkle Tree Hash and Consistency Proofs:
      - Domain separation invariants (empty tree vs 1-leaf empty payload `b""`,
        0x00 leaf prefix, 0x01 node prefix, 64-byte leaf second-preimage resistance,
        and non-power-of-two k=2 < 3 split).
      - All 153 pairs 1 <= m <= n <= 17 (explicitly covering non-power-of-two sizes
        m in {3, 5, 6, 7, 11, 13, 15, 17}) plus logarithmic proof length bounds.
      - All 5 adversarial tampering classes across power-of-two (m=4, n=13),
        non-power-of-two (m=6, n=13; m=7, n=15), and incomplete right subtree
        (m=9, n=11) configurations, including cross-size proof replay rejection,
        same-root replay rejection, oversized proof rejection, and non-bytes node rejection.
    """
    # Domain separation, empty-payload leaf vs empty tree, 64-byte leaf second-preimage resistance & k=2 < 3 split
    assert merkle_tree_hash([]) == hashlib.sha256(b"").digest()
    assert merkle_tree_hash([b""]) == hashlib.sha256(b"\x00").digest()
    assert merkle_tree_hash([]) != merkle_tree_hash([b""])
    h_a = hashlib.sha256(b"\x00alpha").digest()
    h_b = hashlib.sha256(b"\x00beta").digest()
    h_c = hashlib.sha256(b"\x00gamma").digest()
    h_ab = hashlib.sha256(b"\x01" + h_a + h_b).digest()
    assert merkle_tree_hash([b"alpha"]) == h_a
    assert verify_merkle_consistency_proof(1, 1, h_a, h_a, []) is True
    assert verify_merkle_consistency_proof(1, 1, h_a, h_a, [h_a]) is False
    assert merkle_tree_hash([b"alpha", b"beta"]) == h_ab
    assert merkle_tree_hash([h_a + h_b]) != h_ab
    assert (
        merkle_tree_hash([b"alpha", b"beta", b"gamma"])
        == hashlib.sha256(b"\x01" + h_ab + h_c).digest()
    )

    max_n = 17
    leaves = [f"rfc6962-leaf-{i:02d}".encode("ascii") for i in range(max_n)]
    roots = {size: merkle_tree_hash(leaves[:size]) for size in range(1, max_n + 1)}

    non_power_of_two_targets = {3, 5, 6, 7, 11, 13, 15, 17}
    tested_non_pow2: set[int] = set()

    for n in range(1, max_n + 1):
        tree_n = leaves[:n]
        root_n = roots[n]
        for m in range(1, n + 1):
            if m in non_power_of_two_targets:
                tested_non_pow2.add(m)
            root_m = roots[m]
            proof = merkle_consistency_proof(tree_n, m)
            if m == n:
                assert len(proof) == 0
            else:
                assert 1 <= len(proof) <= (n - 1).bit_length() + 1
            assert (
                verify_merkle_consistency_proof(m, n, root_m, root_n, proof) is True
            ), f"Valid RFC 6962 consistency proof rejected for (m={m}, n={n})"

    assert tested_non_pow2 == non_power_of_two_targets

    # Test all 5 adversarial tampering classes across non-power-of-two (m=7, n=15; m=6, n=13),
    # power-of-two (m=4, n=13), and incomplete right subtree (m=9, n=11) configurations.
    extra_digest = hashlib.sha256(b"extra-node").digest()
    for m_adv, n_adv in ((7, 15), (6, 13), (4, 13), (9, 11)):
        root_m_adv = roots[m_adv]
        root_n_adv = roots[n_adv]
        valid_proof = merkle_consistency_proof(leaves[:n_adv], m_adv)
        assert len(valid_proof) >= 2
        assert (
            verify_merkle_consistency_proof(
                m_adv, n_adv, root_m_adv, root_n_adv, valid_proof
            )
            is True
        )

        # Adversarial Test 1: Corrupted first_root or second_root (for m < n and m == n)
        # plus same-root replay attack when m < n (second_root set to first_root).
        bad_first_root = bytes([root_m_adv[0] ^ 0xFF]) + root_m_adv[1:]
        bad_second_root = bytes([root_n_adv[0] ^ 0xFF]) + root_n_adv[1:]
        assert (
            verify_merkle_consistency_proof(
                m_adv, n_adv, bad_first_root, root_n_adv, valid_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                m_adv, n_adv, root_m_adv, bad_second_root, valid_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                m_adv, n_adv, root_m_adv, root_m_adv, valid_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                n_adv, n_adv, root_n_adv, bad_second_root, []
            )
            is False
        )

        # Adversarial Test 2: Flipped byte inside every proof node & swapped proof nodes
        for idx in range(len(valid_proof)):
            tampered_proof = list(valid_proof)
            node = tampered_proof[idx]
            tampered_proof[idx] = node[:15] + bytes([node[15] ^ 0x01]) + node[16:]
            assert (
                verify_merkle_consistency_proof(
                    m_adv, n_adv, root_m_adv, root_n_adv, tampered_proof
                )
                is False
            )
        swapped_proof = list(valid_proof)
        swapped_proof[0], swapped_proof[1] = swapped_proof[1], swapped_proof[0]
        assert (
            verify_merkle_consistency_proof(
                m_adv, n_adv, root_m_adv, root_n_adv, swapped_proof
            )
            is False
        )

        # Adversarial Test 3: Extra trailing node(s) appended to proof (for m < n, m == n, and > max_proof_len)
        extended_proof = list(valid_proof) + [extra_digest]
        assert (
            verify_merkle_consistency_proof(
                m_adv, n_adv, root_m_adv, root_n_adv, extended_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                m_adv,
                n_adv,
                root_m_adv,
                root_n_adv,
                list(valid_proof) + [extra_digest] * 10,
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                n_adv,
                n_adv,
                root_n_adv,
                root_n_adv,
                [extra_digest],
            )
            is False
        )

        # Adversarial Test 4: Truncated proof (missing last node or empty proof when m < n)
        truncated_proof = valid_proof[:-1]
        assert (
            verify_merkle_consistency_proof(
                m_adv, n_adv, root_m_adv, root_n_adv, truncated_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(m_adv, n_adv, root_m_adv, root_n_adv, [])
            is False
        )

        # Adversarial Test 5: Invalid sizes (m > n, m <= 0, bool sizes, cross-size replay, malformed digest)
        assert (
            verify_merkle_consistency_proof(
                n_adv, m_adv, root_n_adv, root_m_adv, valid_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                m_adv - 1, n_adv, roots[m_adv - 1], root_n_adv, valid_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                m_adv, n_adv + 1, root_m_adv, roots[n_adv + 1], valid_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                0, n_adv, _EMPTY_TREE_HASH, root_n_adv, valid_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                -1, n_adv, root_m_adv, root_n_adv, valid_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                True, n_adv, root_m_adv, root_n_adv, valid_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                m_adv, True, root_m_adv, root_n_adv, valid_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                m_adv, n_adv, root_m_adv[:31], root_n_adv, valid_proof
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                m_adv,
                n_adv,
                root_m_adv,
                root_n_adv,
                [valid_proof[0][:31]] + valid_proof[1:],
            )
            is False
        )
        assert (
            verify_merkle_consistency_proof(
                m_adv,
                n_adv,
                root_m_adv,
                root_n_adv,
                [valid_proof[0], 1337],  # type: ignore[list-item]
            )
            is False
        )


def _test_type_and_boundary_guards() -> None:
    """
    Verify m=1 and N=1 boundaries, int-subclass normalization, asymptotic scaling
    (m=8 RM decoding and n=65 Merkle consistency), caller input immutability,
    and strict type rejection.
    """

    class _IntSub(int):
        pass

    # Degenerate N = 2^0 = 1 FWHT boundary & int subclass normalization
    fwht_n1 = fast_walsh_hadamard_transform([_IntSub(42)])
    assert fwht_n1 == [42] and type(fwht_n1[0]) is int
    enc_sub = rm_encode([_IntSub(1), _IntSub(0)], 1)
    assert enc_sub == [1, 1] and all(type(b) is int for b in enc_sub)

    # RM(1, 1) ([2, 2, 1]_2) boundary & single-erasure half-distance tie check
    llr_m1: list[fractions.Fraction | int] = [_IntSub(2), fractions.Fraction(-5, 3)]
    llr_m1_snapshot = list(llr_m1)
    dec_m1, dec_cw1, uniq_m1 = rm_decode_soft_rational(llr_m1, 1)
    assert llr_m1 == llr_m1_snapshot
    assert uniq_m1 is True and dec_m1 == [0, 1] and dec_cw1 == [0, 1]
    _, _, uniq_m1_tie = rm_decode_soft_rational([1, 0], 1)
    assert uniq_m1_tie is False

    # Verify FWHT does not mutate caller's input list
    fwht_in = [5, -3, 2, 7]
    fwht_out = fast_walsh_hadamard_transform(fwht_in)
    assert fwht_in == [5, -3, 2, 7] and fwht_out != fwht_in

    # Asymptotic scaling guard: RM(1, 8) (N=256, d_min=128, t=63) & non-pow2 Merkle (n=65, m=37)
    msg_m8 = [1, 0, 1, 1, 0, 0, 1, 0, 1]
    cw_m8 = rm_encode(msg_m8, 8)
    llr_m8: list[fractions.Fraction | int] = list(_codeword_to_bipolar(cw_m8))
    for err_idx in range(63):
        llr_m8[err_idx] = -llr_m8[err_idx]
    dec_m8, dec_cw8, uniq_m8 = rm_decode_soft_rational(llr_m8, 8)
    assert uniq_m8 is True and dec_m8 == msg_m8 and dec_cw8 == cw_m8

    leaves_65 = [f"leaf-{i:02d}".encode("ascii") for i in range(65)]
    proof_37_65 = merkle_consistency_proof(leaves_65, 37)
    assert len(proof_37_65) <= (65 - 1).bit_length() + 1
    assert (
        verify_merkle_consistency_proof(
            37,
            65,
            merkle_tree_hash(leaves_65[:37]),
            merkle_tree_hash(leaves_65),
            proof_37_65,
        )
        is True
    )

    # Verify total boolean behavior of verify_merkle_consistency_proof on untrusted non-bytes/non-list/zero types
    valid_digest = _EMPTY_TREE_HASH
    assert (
        verify_merkle_consistency_proof(0, 0, valid_digest, valid_digest, []) is False
    )
    assert (
        verify_merkle_consistency_proof(
            1, 1, bytearray(valid_digest), valid_digest, []  # type: ignore[arg-type]
        )
        is False
    )
    assert (
        verify_merkle_consistency_proof(
            1, 2, valid_digest, valid_digest, (valid_digest,)  # type: ignore[arg-type]
        )
        is False
    )
    assert (
        verify_merkle_consistency_proof(
            1, 2, valid_digest, valid_digest, [bytearray(valid_digest)]  # type: ignore[list-item]
        )
        is False
    )

    for empty_tree_m in (0, 1, -1):
        try:
            merkle_consistency_proof([], empty_tree_m)
            raise AssertionError(
                f"Expected ValueError for empty tree with m={empty_tree_m}"
            )
        except ValueError:
            pass

    for bad_m in (0, -2, True, False, 1.5):
        try:
            rm_encode([0, 0], bad_m)  # type: ignore[arg-type]
            raise AssertionError(f"Expected ValueError for m={bad_m!r}")
        except ValueError:
            pass

    for bad_bits in ([0, 1], [True, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 1.0]):
        try:
            rm_encode(bad_bits, 3)  # type: ignore[arg-type]
            raise AssertionError(f"Expected ValueError for message_bits={bad_bits!r}")
        except ValueError:
            pass

    for bad_vec in ([], [1, 2, 3], [True, 0, 1, 0], [1.0, 0, 0, 0]):
        try:
            fast_walsh_hadamard_transform(bad_vec)  # type: ignore[arg-type]
            raise AssertionError(f"Expected ValueError for vec={bad_vec!r}")
        except ValueError:
            pass

    for bad_llr in ([True] * 8, [1.5] * 8, [fractions.Fraction(1, 3)] * 7):
        try:
            rm_decode_soft_rational(bad_llr, 3)  # type: ignore[arg-type]
            raise AssertionError(f"Expected error for bad_llr={bad_llr!r}")
        except (TypeError, ValueError):
            pass

    for bad_sub_m in (0, 5, True, False):
        try:
            merkle_consistency_proof([b"a", b"b", b"c", b"d"], bad_sub_m)
            raise AssertionError(f"Expected ValueError for m={bad_sub_m!r}")
        except ValueError:
            pass

    for bad_leaves in (b"not-a-list", [b"ok", "not-bytes"], [bytearray(b"mut")]):
        try:
            merkle_tree_hash(bad_leaves)  # type: ignore[arg-type]
            raise AssertionError(f"Expected TypeError for leaves={bad_leaves!r}")
        except TypeError:
            pass


def run_self_tests() -> None:
    """Execute the full verification and adversarial mutant test suite."""
    _test_rm_1_3_exhaustive()
    _test_rm_1_5_exhaustive_and_multi_error()
    _test_rfc6962_merkle_consistency_and_adversarial()
    _test_type_and_boundary_guards()
    print(
        "ALL SELF-TESTS PASSED: RM(1, 3) & RM(1, 5) exact Q-FWHT ML decoding, "
        "Parseval identity, half-distance tie detection, and RFC 6962 Merkle "
        "consistency subproofs (1 <= m <= n <= 17 + adversarial mutants)."
    )


if __name__ == "__main__":
    run_self_tests()
