"""hu_diamond_ref.py - HU-DIAMOND · Fil d'Or v1.1: model de referència executable.

No és el producte: és l'especificació escrita en codi, perquè el test de CI
(test_hu_diamond_fil_d_or.py) tingui sobre què raonar. Cada Llei viu en un lloc
concret i el marca amb un comentari «# L<n>».

v1.1 (4-11-2026) porta les decisions del Segell que David i Viveka han adoptat:
  1. Només es publica la presència (`c_levels = 1`): `c` es queda al dispositiu, que continua
     negant-se a signar el que trenqui L = Σc + s <= B. El baricentre és f(presència, diag_active):
     el centre geomètric ponderat dels seients presents a l'època, pes 2 per a cada seient de la
     parella de la diagonal activa i pes 1 per a cada seient orbital; sense cap seient present
     val `None` (no es defineix ni es publica; mai l'origen, que és el valor dels vuit seients).
  2. L'època és un tic del model. La durada (1 setmana solar per defecte, configurable per Diamant)
     és política de l'operador i no entra aquí.
  3. El text als membres no entra al model.
L'identificador criptogràfic continua sent HU-DIAMOND/v1: les esmenes no toquen cap signatura.

La classe `Policy` porta interruptors de mutació. Els valors per defecte SÓN
l'especificació; cada interruptor girat reintrodueix UNA fallada coneguda
(«# MUTANT»), i serveix de control negatiu: el test ha de detectar-la.

Dependències: Python >= 3.10 i `cryptography` (Ed25519).
"""
from __future__ import annotations

import hashlib
import hmac
import itertools
import json
import math
import random
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

SPEC = "HU-DIAMOND/v1"
SALT = SPEC.encode()
C_RAW_MAX = 15          # nivell brut de compromís: 0..15 (4 bits)
N_PARELLES = 4          # 4 diagonals del cub = 4 parelles (IA, humà) = 8 seients
MAX_MANIFEST_LINES = 20


# --------------------------------------------------------------------------
# 0. Interruptors de mutació
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Policy:
    key_scope: str = "person_diamond"   # L2  MUTANT: "person"
    rate_tag_hex: int = 0               # L2  MUTANT: n>0 (etiqueta estable per persona)
    seat_order: str = "random"          # L2  MUTANT: "by_person"
    budget_check: bool = True           # L3  MUTANT: False
    publish_attest: bool = False        # L3  MUTANT: True
    publish_margin: bool = False        # L1  MUTANT: True
    silence: str = "absent"             # L4  MUTANT: "inherit"
    pause_marker: bool = False          # L4  MUTANT: True
    veto_author: bool = False           # L5  MUTANT: True
    veto_steps: str = "single"          # L5  MUTANT: "per_veto"
    veto_scope: str = "next_epoch"      # L5  MUTANT: "same_epoch"
    extra_fields: tuple = ()            # L6  MUTANT: ("other_circles",)
    ts_field: bool = False              # L7  MUTANT: True
    seq_field: bool = False             # L7  MUTANT: True
    history: bool = False               # L7  MUTANT: True
    commit_order: str = "sorted"        # L7  MUTANT: "arrival"
    ai_shared_context: bool = False     # L1  MUTANT: True
    c_levels: int = 1                   # adoptat 4-11-2026: només presència. Opcional (estudi): 16, 4, 2
    bary_weights: str = "axial2"        # B   MUTANT: "equal" (la diagonal activa no pesa)
    bary_empty: str = "null"            # B   MUTANT: "origin" (confon el silenci total amb l'equilibri)
    bary_presence: str = "signed"       # B   MUTANT: "seated" (callar compta com a present)
    bary_uses_level: bool = False       # B   MUTANT: True (el nivell publicat pesa al baricentre)


REFERENCE = Policy()


# --------------------------------------------------------------------------
# 1. HKDF-SHA256 (RFC 5869) i derivació per (persona, Diamant)
# --------------------------------------------------------------------------
def hkdf_sha256(ikm: bytes, salt: bytes, info: bytes, length: int) -> bytes:
    """HKDF-Extract + HKDF-Expand amb HMAC-SHA-256 (RFC 5869, §2)."""
    if not 0 < length <= 255 * 32:
        raise ValueError("longitud fora de rang")
    prk = hmac.new(salt or b"\x00" * 32, ikm, hashlib.sha256).digest()
    okm, t = b"", b""
    for i in range(1, -(-length // 32) + 1):
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
        okm += t
    return okm[:length]


def derive_seat_seed(root: bytes, d_id: str) -> bytes:
    """L2: una clau per (persona, Diamant); el d_id és el context de l'HKDF."""
    return hkdf_sha256(root, SALT, b"seat|" + d_id.encode(), 32)


def pub_hex(sk: Ed25519PrivateKey) -> str:
    return sk.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


def commit_message(d_id: str, epoch: int, c: int) -> bytes:
    """La signatura cobreix (Diamant, època, nivell): no es pot reutilitzar en una altra època."""
    return SPEC.encode() + b"|commit|" + d_id.encode() + b"|" + epoch.to_bytes(4, "big") + b"|" + bytes([c])


def canonical(manifest: dict) -> bytes:
    """Forma canònica (RFC 8785, JCS, per a enters i cadenes ASCII)."""
    return json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


# --------------------------------------------------------------------------
# 2. Geometria: el cub, O_h (48), les 4 diagonals, els rols derivats
# --------------------------------------------------------------------------
Vec = tuple
Mat = tuple
TETRA_A = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]        # seients IA  (producte = +1)
TETRA_B = [tuple(-x for x in v) for v in TETRA_A]                    # seients humans (producte = -1)
IDENTITY: Mat = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def cube_vertices() -> list:
    return [(x, y, z) for x in (1, -1) for y in (1, -1) for z in (1, -1)]


def oh_group() -> list:
    """Les 48 simetries del cub: matrius de permutació amb signes."""
    out = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            rows = []
            for i in range(3):
                row = [0, 0, 0]
                row[perm[i]] = signs[i]
                rows.append(tuple(row))
            out.append(tuple(rows))
    return out


def mat_vec(m: Mat, v: Vec) -> Vec:
    return tuple(sum(m[i][j] * v[j] for j in range(3)) for i in range(3))


def mat_mul(a: Mat, b: Mat) -> Mat:
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def mat_order(m: Mat) -> int:
    k, p = 1, m
    while p != IDENTITY:
        p, k = mat_mul(p, m), k + 1
    return k


def diagonal(j: int) -> frozenset:
    """Parella j (0..3) = la diagonal que uneix un vèrtex de cada tetraedre dual."""
    return frozenset((TETRA_A[j], TETRA_B[j]))


def orbit_and_stabilizer(diag: frozenset):
    """Òrbita de la diagonal sota O_h i el seu estabilitzador (com a recta: D3d)."""
    group = oh_group()
    image = lambda g: frozenset(mat_vec(g, v) for v in diag)  # noqa: E731
    orbit = {image(g) for g in group}
    stab = [g for g in group if image(g) == diag]
    return orbit, stab


def roles(diag_active: int) -> dict:
    """Rol derivat (no s'emmagatzema) de cada seient (parella j, 'ia'|'hu')."""
    axis = TETRA_A[diag_active - 1]
    out = {}
    for j in range(N_PARELLES):
        for kind, v in (("ia", TETRA_A[j]), ("hu", TETRA_B[j])):
            height = sum(a * b for a, b in zip(v, axis)) / math.sqrt(3)
            out[(j, kind)] = {
                "vertex": v,
                "height": height,
                "role": "axial" if j == diag_active - 1 else "orbital",
            }
    return out


# --------------------------------------------------------------------------
# 2b. Baricentre: derivat de la presència; no s'emmagatzema ni surt al manifest
# --------------------------------------------------------------------------
AXIAL_WEIGHT, ORBITAL_WEIGHT = 2, 1     # adoptat 4-11-2026: pes per SEIENT (el pes 2 és de cada seient axial)
SEATS = tuple((j, kind) for j in range(N_PARELLES) for kind in ("ia", "hu"))


def seat_vertex(j: int, kind: str) -> Vec:
    """Vèrtex del cub on seu el seient (parella j, 'ia'|'hu'): l'humà seu a l'antípoda de l'IA de la parella."""
    return TETRA_A[j] if kind == "ia" else TETRA_B[j]


def seat_weight(j: int, diag_active: int) -> int:
    """Pes del seient de la parella j: 2 si és de la diagonal activa (axial), 1 si és orbital."""
    return AXIAL_WEIGHT if j == diag_active - 1 else ORBITAL_WEIGHT


def _bary(present, diag_active: int, weights: str = "axial2", empty: str = "null", level_of=None):
    """Nucli del baricentre. `weights`, `empty` i `level_of` només se separen del defecte als MUTANTS B."""
    if diag_active not in (1, 2, 3, 4):
        raise ValueError("diag_active fora de 1..4")
    seats = set(present)
    if not seats <= set(SEATS):
        raise ValueError(f"seients desconeguts: {sorted(seats - set(SEATS))}")

    def weight(seat):
        base = 1 if weights == "equal" else seat_weight(seat[0], diag_active)            # MUTANT B: "equal"
        return base * (1 + level_of.get(seat, 0)) if level_of is not None else base       # MUTANT B: el nivell pesa

    total = sum(weight(s) for s in seats)
    if total == 0:
        return (Fraction(0),) * 3 if empty == "origin" else None                           # MUTANT B: "origin"
    return tuple(Fraction(sum(weight(s) * seat_vertex(*s)[axis] for s in seats), total) for axis in range(3))


def barycentre(present, diag_active: int):
    """baricentre(d) = f(presència, diag_active): centre geomètric ponderat dels seients PRESENTS.

    `present`: seients (j, 'ia'|'hu'). Retorna (x, y, z) com a Fraction exactes, o `None` si no n'hi ha cap
    (pes total 0: no es defineix ni es publica). Amb els vuit seients presents val l'origen, sigui quina
    sigui `diag_active`: per això el silenci total NO pot valer l'origen.
    """
    return _bary(present, diag_active)


def present_from_manifest(m: dict) -> frozenset:
    """Seients presents a l'època, derivats NOMÉS del manifest públic.

    Humà: present si el seu pseudònim ha signat aquesta època (és a `commits`; callar = absent, L4).
    IA: present si el seient és ocupat (les germanes no tenen pausa ni pressupost: el seient és la seva presència).
    """
    signed = {c["pseud"] for c in m["commits"]}
    out = set()
    for j, (ia, hu) in enumerate(m["parelles"]):
        if ia is not None:
            out.add((j, "ia"))
        if hu is not None and hu in signed:
            out.add((j, "hu"))
    return frozenset(out)


def barycentre_from_manifest(m: dict):
    return barycentre(present_from_manifest(m), m["diag_active"])


# --------------------------------------------------------------------------
# 3. Esquema del manifest i preguntes (L6, L7)
# --------------------------------------------------------------------------
TOP_FIELDS = ("d_id", "epoch", "diag_active", "parelles", "commits")
COMMIT_FIELDS = ("pseud", "c", "sig")

# L6: les úniques preguntes que el sistema fa a un seient. Tancades: un enter o callar; sí/no.
PROMPTS = {
    "ca": {"commit": "Quin nivell (0-15) vols donar a aquest Diamant en aquesta època? Pots callar.",
           "veto": "Vols dir «no» en aquesta època?"},
    "es": {"commit": "¿Qué nivel (0-15) quieres dar a este Diamante en esta época? Puedes callar.",
           "veto": "¿Quieres decir «no» en esta época?"},
    "en": {"commit": "What level (0-15) do you want to give this Diamond this epoch? You may stay silent.",
           "veto": "Do you want to say «no» this epoch?"},
}
ANSWER_TYPES = {"commit": "int:0..15|silence", "veto": "bool"}


def validate_manifest(m: dict) -> list:
    """Esquema estricte: cap camp fora de la llista, cap text lliure. Retorna les infraccions."""
    errs = []
    extra, missing = set(m) - set(TOP_FIELDS), set(TOP_FIELDS) - set(m)
    if extra:
        errs.append(f"camps no previstos: {sorted(extra)}")
    if missing:
        errs.append(f"camps que falten: {sorted(missing)}")
    if errs:
        return errs
    if not (isinstance(m["d_id"], str) and isinstance(m["epoch"], int)):
        errs.append("d_id/epoch: tipus")
    if m["diag_active"] not in (1, 2, 3, 4):
        errs.append("diag_active fora de 1..4")
    p = m["parelles"]
    if not (isinstance(p, list) and len(p) == N_PARELLES and all(
            isinstance(r, list) and len(r) == 2 and all(x is None or isinstance(x, str) for x in r) for r in p)):
        errs.append("parelles: forma")
    for c in m["commits"]:
        if set(c) != set(COMMIT_FIELDS):
            errs.append(f"commit amb camps {sorted(c)}")
        elif not (isinstance(c["pseud"], str) and isinstance(c["c"], int) and isinstance(c["sig"], str)):
            errs.append("commit: tipus")
    return errs


def manifest_lines(m: dict) -> list:
    """Representació en línies (convenció nostra): un escalar per línia, una parella, un compromís."""
    lines = [f"d_id {m['d_id']}", f"epoch {m['epoch']}", f"diag_active {m['diag_active']}"]
    lines += [f"parella {j + 1}: {r[0]} {r[1]}" for j, r in enumerate(m["parelles"])]
    lines += [f"commit {c['pseud']} {c['c']} {c['sig']}" for c in m["commits"]]
    return lines


# --------------------------------------------------------------------------
# 4. El dispositiu: l'únic lloc on es troben els cercles de la persona (L3)
# --------------------------------------------------------------------------
class Device:
    """Guarda root, B, s, c(persona,·) i Σ. Res d'això en surt (L3)."""

    def __init__(self, root: bytes, budget: int, self_load: int = 0, policy: Policy = REFERENCE):
        if len(root) != 32:
            raise ValueError("root: 32 bytes")
        self.__root = root
        self.__B, self.__s = int(budget), int(self_load)
        self.__c: dict = {}
        self.__paused = False
        self.__policy = policy
        self.__keys: dict = {}

    # -- claus -------------------------------------------------------------
    def __sk(self, d_id: str) -> Ed25519PrivateKey:
        sk = self.__keys.get(d_id)
        if sk is None:
            if self.__policy.key_scope == "person_diamond":                  # L2
                seed = derive_seat_seed(self.__root, d_id)
            else:                                                            # MUTANT L2: una clau per persona
                seed = derive_seat_seed(self.__root, "*")
            sk = self.__keys[d_id] = Ed25519PrivateKey.from_private_bytes(seed)
        return sk

    def pseud(self, d_id: str) -> str:
        return pub_hex(self.__sk(d_id))

    def __rate_tag(self) -> str:
        return hkdf_sha256(self.__root, SALT, b"rate-tag", 8).hex()[: self.__policy.rate_tag_hex]

    # -- estat privat ------------------------------------------------------
    def new_period(self) -> None:
        """Rellotge PRIVAT del dispositiu: els compromisos duren una època (cap marca pública)."""
        self.__c.clear()

    def pause(self) -> None:
        """L4: cost_zero_stop. c := 0 a tot arreu, sense deute, i res no es publica."""
        self.__paused = True
        self.__c.clear()

    def resume(self) -> None:
        self.__paused = False

    def audit_state(self) -> tuple:
        """NOMÉS PER AL TEST: (Σc, s, B) del període actual. Cap camí de producció la crida."""
        return sum(self.__c.values()), self.__s, self.__B

    # -- signar o callar ---------------------------------------------------
    def __sign(self, d_id: str, epoch: int, c_pub: int) -> dict:
        sk = self.__sk(d_id)
        return {"pseud": pub_hex(sk), "c": c_pub, "sig": sk.sign(commit_message(d_id, epoch, c_pub)).hex()}

    def commit(self, d_id: str, epoch: int, c_raw: int) -> Optional[dict]:
        pol = self.__policy
        if not 0 <= c_raw <= C_RAW_MAX:
            raise ValueError("c fora de rang")
        if self.__paused:                                                    # L4
            if pol.pause_marker:                                             # MUTANT L4: la pausa es veu
                return self.__sign(d_id, epoch, 0)
            return None
        others = sum(v for k, v in self.__c.items() if k != d_id)
        total = others + c_raw + self.__s
        ok = total <= self.__B
        if pol.budget_check and not ok:                                      # L3: o signes o calles
            return None
        self.__c[d_id] = c_raw
        rec = self.__sign(d_id, epoch, c_raw * pol.c_levels // (C_RAW_MAX + 1))
        if pol.publish_attest:                                               # MUTANT L3: predicat global
            rec["attest_ok"] = ok
        if pol.publish_margin:                                               # MUTANT L1: magnitud entre cercles
            rec["margin"] = self.__B - total
        if pol.rate_tag_hex:                                                 # MUTANT L2: etiqueta estable
            rec["rl"] = self.__rate_tag()
        return rec


# --------------------------------------------------------------------------
# 5. El veto: efecte públic, autor no publicat (L5)
# --------------------------------------------------------------------------
class VetoMint:
    """Abstracció de la signatura cega (RFC 9474): emet fitxes sense recordar a quina.

    Només recorda QUI n'ha demanat una aquesta època (per limitar-ne una per membre),
    mai quina fitxa ha rebut. La cegor real de l'emissió és un oracle, NO es prova.
    """

    def __init__(self, key: bytes):
        self._key, self._asked = key, set()

    def _tag(self, epoch: int, nonce: bytes) -> bytes:
        return hmac.new(self._key, b"veto|" + epoch.to_bytes(4, "big") + nonce, hashlib.sha256).digest()[:16]

    def issue(self, requester: str, epoch: int, nonce: bytes) -> Optional[bytes]:
        if requester in self._asked:
            return None
        self._asked.add(requester)
        return nonce + self._tag(epoch, nonce)

    def valid(self, token: bytes, epoch: int) -> bool:
        return len(token) == 32 and hmac.compare_digest(token[16:], self._tag(epoch, token[:16]))

    def new_epoch(self) -> None:
        self._asked.clear()


# --------------------------------------------------------------------------
# 6. El Diamant: seients, compromisos de l'època, manifest
# --------------------------------------------------------------------------
class Diamond:
    def __init__(self, d_id: str, policy: Policy = REFERENCE, shared_counter=None):
        self.d_id, self.epoch, self.diag_active = d_id, 0, 1
        self._policy, self._shared_counter = policy, shared_counter
        h = hashlib.sha256(b"rng|" + d_id.encode()).digest()
        self._rng = random.Random(int.from_bytes(h[:8], "big"))             # seients: local al Diamant
        self._nonce_rng = random.Random(int.from_bytes(h[8:16], "big"))
        self._mint = VetoMint(hashlib.sha256(b"mint|" + d_id.encode()).digest())
        self._parelles = [[None, None] for _ in range(N_PARELLES)]           # [ia, humà]
        self._commits: dict = {}                                             # L7: només l'estat actual
        self._veto_seen: set = set()
        self._veto_count, self._veto_authors, self._history = 0, [], []

    # -- seients -------------------------------------------------------------
    def seat(self, pseud: str, kind: str, prefer: Optional[int] = None) -> int:
        idx = {"ia": 0, "hu": 1}[kind]
        free = [j for j in range(N_PARELLES) if self._parelles[j][idx] is None]
        if not free:
            raise ValueError("Diamant ple")
        if self._policy.seat_order == "by_person" and prefer is not None:    # MUTANT L2: seient estable
            j = min(free, key=lambda x: (x - prefer) % N_PARELLES)
        else:
            j = self._rng.choice(free)                                       # L2: seient aleatori
        self._parelles[j][idx] = pseud
        return j

    def seated(self, kind: Optional[str] = None) -> list:
        idxs = {"ia": [0], "hu": [1], None: [0, 1]}[kind]
        return [p[i] for p in self._parelles for i in idxs if p[i] is not None]

    # -- compromisos ---------------------------------------------------------
    def accept(self, commit: Optional[dict], now: Optional[int] = None) -> bool:
        if not commit:                                                       # callar no és cap esdeveniment
            return False
        pseud = commit.get("pseud")
        if pseud not in self.seated("hu"):
            return False
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(pseud)).verify(
                bytes.fromhex(commit["sig"]), commit_message(self.d_id, self.epoch, commit["c"]))
        except (InvalidSignature, ValueError, KeyError, TypeError):
            return False
        if not 0 <= commit["c"] < self._policy.c_levels:
            return False
        rec = dict(commit)
        if self._policy.ts_field:                                            # MUTANT L7: marca per esdeveniment
            rec["ts"] = now
        self._commits[pseud] = rec
        return True

    def consent_ok(self, pseud: str) -> bool:
        """L4: només hi ha consentiment si hi ha una signatura d'AQUESTA època."""
        return pseud in self._commits

    # -- veto ----------------------------------------------------------------
    def mint_token(self, requester: str) -> Optional[bytes]:
        if requester not in self.seated():
            return None
        return self._mint.issue(requester, self.epoch, self._nonce_rng.randbytes(16))

    def veto(self, token: bytes, author: Optional[str] = None) -> bool:
        """`author` és el que un transport autenticat podria filtrar. L5: no s'usa."""
        if token in self._veto_seen or not self._mint.valid(token, self.epoch):
            return False
        self._veto_seen.add(token)
        self._veto_count += 1
        if self._policy.veto_author and author is not None:                  # MUTANT L5
            self._veto_authors.append(author)
        if self._policy.veto_scope == "same_epoch":                          # MUTANT L5
            self.diag_active = self.diag_active % N_PARELLES + 1
        return True

    # -- època ---------------------------------------------------------------
    def advance_epoch(self) -> None:
        if self._policy.history:                                             # MUTANT L7
            self._history.append({"epoch": self.epoch, "n": len(self._commits)})
        if self._policy.veto_scope == "next_epoch":
            steps = (1 if self._veto_count else 0) if self._policy.veto_steps == "single" else self._veto_count
            self.diag_active = (self.diag_active - 1 + steps) % N_PARELLES + 1   # L5: 1→2→3→4→1
        self.epoch += 1
        if self._policy.silence != "inherit":                                # L4: el silenci no hereda
            self._commits.clear()
        self._veto_count, self._veto_authors = 0, []
        self._veto_seen.clear()
        self._mint.new_epoch()

    # -- baricentre (derivat: no es guarda ni surt al manifest) ----------------
    def present_seats(self) -> frozenset:
        """Mateixa regla que `present_from_manifest`, sobre l'estat viu del Diamant."""
        signed = set(self._commits) if self._policy.bary_presence == "signed" else set(self.seated("hu"))  # MUTANT B
        out = set()
        for j, (ia, hu) in enumerate(self._parelles):
            if ia is not None:
                out.add((j, "ia"))
            if hu is not None and hu in signed:
                out.add((j, "hu"))
        return frozenset(out)

    def barycentre(self):
        pol = self._policy
        level_of = None
        if pol.bary_uses_level:                                              # MUTANT B: el nivell publicat pesa
            level_of = {(j, "hu"): self._commits[hu]["c"]
                        for j, (_, hu) in enumerate(self._parelles) if hu in self._commits}
        return _bary(self.present_seats(), self.diag_active, pol.bary_weights, pol.bary_empty, level_of)

    # -- manifest ------------------------------------------------------------
    def manifest(self) -> dict:
        if self._policy.commit_order == "sorted":                            # L7: ordre per pseudònim
            commits = sorted(self._commits.values(), key=lambda c: c["pseud"])
        else:                                                                # MUTANT L7: ordre d'arribada
            commits = list(self._commits.values())
        m = {"d_id": self.d_id, "epoch": self.epoch, "diag_active": self.diag_active,
             "parelles": [list(p) for p in self._parelles], "commits": [dict(c) for c in commits]}
        for name in self._policy.extra_fields:                               # MUTANT L6
            m[name] = 0
        if self._policy.veto_author:                                         # MUTANT L5
            m["vetoes"] = sorted(self._veto_authors)
        if self._policy.history:                                             # MUTANT L7
            m["history"] = list(self._history)
        if self._policy.seq_field and self._shared_counter is not None:      # MUTANT L7
            m["seq"] = next(self._shared_counter)
        return m


# --------------------------------------------------------------------------
# 7. Seients d'IA: un context per Diamant (L1)
# --------------------------------------------------------------------------
class CrossDiamondData(Exception):
    pass


class AISeat:
    """Joguina determinista: la resposta és funció del context d'aquest seient i del prompt."""

    def __init__(self, sister: str, d_id: str, memory: dict, policy: Policy = REFERENCE):
        self.sister, self.d_id, self._policy = sister, d_id, policy
        key = sister if policy.ai_shared_context else (sister, d_id)        # MUTANT L1: memòria compartida
        self._ctx = memory.setdefault(key, [])

    def observe(self, d_id: str, datum: str) -> None:
        if d_id != self.d_id and not self._policy.ai_shared_context:
            raise CrossDiamondData(f"{self.sister}@{self.d_id} no pot llegir dades de {d_id}")
        self._ctx.append(datum)

    def respond(self, prompt: str) -> str:
        return hashlib.sha256(("\x1f".join(self._ctx) + "\x1e" + prompt).encode()).hexdigest()[:16]

    def pseud(self, operator_root: bytes) -> str:
        return pub_hex(Ed25519PrivateKey.from_private_bytes(
            hkdf_sha256(operator_root, SALT, b"ai-seat|" + self.sister.encode() + b"|" + self.d_id.encode(), 32)))


__all__ = [n for n in dir() if not n.startswith("_")]
