"""hu_adversary.py - població sintètica, models de comportament i adversari estadístic.

L'adversari només veu el que és públic: els manifests que surten del Diamant, amb el
número de tic global de publicació. No coneix l'esquema: aplana el JSON, cerca «nanses»
(cadenes llargues que persisteixen) i els valors germans de cada nansa, i en calcula
estadístics genèrics. Si un mutant afegeix un camp que no existia, l'adversari el fa servir
sense haver-lo previst.

Dependències: només la biblioteca estàndard (i hu_diamond_ref).
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from statistics import NormalDist
from typing import Optional

import hu_diamond_ref as R


# ==========================================================================
# 1. Estadística mínima
# ==========================================================================
def avg_ranks(xs: list) -> list:
    """Rangs mitjans (empats = mitjana), base 1."""
    order = sorted(range(len(xs)), key=xs.__getitem__)
    ranks = [0.0] * len(xs)
    i, n = 0, len(order)
    while i < n:
        j, xi = i, xs[order[i]]
        while j + 1 < n and xs[order[j + 1]] == xi:
            j += 1
        r = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def auc(pos: list, neg: list) -> float:
    """AUC de Mann-Whitney amb empats; 0.5 = sense informació."""
    if not pos or not neg:
        return 0.5
    r = avg_ranks(list(pos) + list(neg))
    n1, n0 = len(pos), len(neg)
    return (sum(r[:n1]) - n1 * (n1 + 1) / 2.0) / (n1 * n0)


def auc_null_se(n1: int, n0: int) -> float:
    """Error estàndard de l'AUC sota la hipòtesi nul·la (mostres independents)."""
    return math.sqrt((n1 + n0 + 1) / (12.0 * n1 * n0))


def pearson(xs: list, ys: list) -> Optional[float]:
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 1e-12 or syy <= 1e-12:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sxx * syy)


# ==========================================================================
# 2. Població, models de comportament, simulador
# ==========================================================================
@dataclass(frozen=True)
class Behavior:
    """Com es comporten les persones (el món, no el protocol)."""
    name: str
    shared_pause: bool      # la pausa és de la persona (tots els seus Diamants alhora)
    budget_split: bool      # els nivells surten d'un pressupost finit repartit entre els seus cercles
    shared_mood: bool       # el «no» és correlacionat a nivell de persona
    saturation: float = 0.9     # fracció del pressupost disponible que realment es compromet
    p_offline: float = 0.08
    p_pause_on: float = 0.07
    p_pause_off: float = 0.35
    p_mood_on: float = 0.05
    p_mood_off: float = 0.40
    p_veto_calm: float = 0.02
    p_veto_grumpy: float = 0.60


NULL = Behavior("null", shared_pause=False, budget_split=False, shared_mood=False)
COUPLED = Behavior("coupled", shared_pause=True, budget_split=True, shared_mood=True)


@dataclass
class Person:
    pid: int
    root: bytes
    B: int
    s: int
    a: int
    diamonds: list
    weights: list
    mu: dict            # d -> nivell habitual (model nul)


@dataclass
class World:
    seed: int
    ticks: int
    persons: list
    d_ids: list
    birth: list
    members: list       # members[d] = [pid, ...]  (4 seients humans per Diamant)


def sha_hex(*parts, n: int = 32) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:n]


def make_world(seed: int, n_persons: int = 120, ticks: int = 30, behavior: Behavior = NULL,
               k_probs=(0.55, 0.30, 0.15), birth_max: int = 6) -> World:
    """N persones, cadascuna en 1..3 Diamants (≤ 3), 4 seients humans per Diamant."""
    rng = random.Random(f"world|{seed}")
    ks = rng.choices((1, 2, 3), weights=k_probs, k=n_persons)
    n_d = -(-sum(ks) // 4)
    for _ in range(500):
        members, ok = [[] for _ in range(n_d)], True
        for p in sorted(range(n_persons), key=lambda q: (-ks[q], rng.random())):
            pool = [d for d in range(n_d) if len(members[d]) < 4]
            if len(pool) < ks[p]:
                ok = False
                break
            wts, chosen = [4 - len(members[d]) for d in pool], []
            for _ in range(ks[p]):
                i = rng.choices(range(len(pool)), weights=wts)[0]
                chosen.append(pool.pop(i))
                wts.pop(i)
            for d in chosen:
                members[d].append(p)
        if ok:
            break
    else:
        raise RuntimeError("no s'ha pogut repartir la població")
    persons = []
    for p in range(n_persons):
        ds = [d for d in range(n_d) if p in members[d]]
        w = [rng.random() + 0.5 for _ in ds]
        w = [x / sum(w) for x in w]
        if behavior.budget_split:
            B, s = rng.randrange(10, 17), rng.randrange(1, 4)
        else:
            B, s = 10_000, 0
        persons.append(Person(p, rng.randbytes(32), B, s, B - s, ds, w, {d: rng.randrange(3, 13) for d in ds}))
    birth = [rng.randrange(0, birth_max + 1) for _ in range(n_d)]
    return World(seed, ticks, persons, [sha_hex("d", seed, d) for d in range(n_d)], birth, members)


@dataclass
class Truth:
    person_of: dict         # nansa publicada -> pid
    k_of: list              # pid -> nombre de Diamants
    members: list           # members[d] -> [pid]


@dataclass
class Sim:
    world: World
    behavior: Behavior
    policy: R.Policy
    feed: list              # [(tic, stream, manifest)]  tal com es publica (JSON canònic reanalitzat)
    raw: list               # bytes canònics, mateix ordre
    beh_feed: list          # vista de comportament: el que van decidir els dispositius, amb etiquetes opaques
    truth: Truth
    beh_truth: Truth
    devices: list = field(default_factory=list)
    diamonds: list = field(default_factory=list)
    signed: dict = field(default_factory=dict)          # (tic, Diamant) -> {pseudònims que han signat aquest tic}
    veto_log: dict = field(default_factory=dict)        # (tic, Diamant) -> nombre de fitxes de veto acceptades
    paused_log: dict = field(default_factory=dict)      # pid -> {tics en pausa de persona}
    refusals: int = 0                                   # signatures refusades pel dispositiu (pressupost)
    max_overshoot: int = -10 ** 9                       # max(Σc + s - B) vist als dispositius


def U(*key) -> float:
    """Atzar amb clau: cada decisió (persona, Diamant, tic) és independent de la resta de la simulació.

    Això permet mons bessons: canviar el que passa als ALTRES Diamants no mou l'atzar d'aquest.
    """
    h = hashlib.blake2b("|".join(map(str, key)).encode(), digest_size=8).digest()
    return int.from_bytes(h, "big") / 2.0 ** 64


def gauss(*key) -> float:
    u1, u2 = max(U(*key, "a"), 1e-12), U(*key, "b")
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


def chain(state: bool, p_on: float, p_off: float, u: float) -> bool:
    return (u >= p_off) if state else (u < p_on)


def simulate(world: World, behavior: Behavior, policy: R.Policy = R.REFERENCE, level_override=None) -> Sim:
    """level_override(pid, d, tic, c) -> c': contrafactual per als tests de no-interferència (L1)."""
    base = f"{world.seed}|{behavior.name}"
    n_d, persons = len(world.d_ids), world.persons
    devices = [R.Device(p.root, p.B, p.s, policy) for p in persons]
    counter = itertools.count()
    dias = [R.Diamond(d_id, policy, counter) for d_id in world.d_ids]
    op_root = hashlib.sha256(f"operator|{world.seed}".encode()).digest()
    pseud = {}
    for d, dia in enumerate(dias):                                   # seients: IA primer, humans després
        for j in range(4):
            dia.seat(R.AISeat(f"sister-{j}", dia.d_id, {}).pseud(op_root), "ia")
        for p in world.members[d]:
            pseud[(p, d)] = devices[p].pseud(dia.d_id)
            dia.seat(pseud[(p, d)], "hu", prefer=p)
    opaque = {k: sha_hex("opaque", world.seed, *k, n=64) for k in pseud}
    k_of = [len(p.diamonds) for p in persons]
    truth = Truth({v: k[0] for k, v in pseud.items()}, k_of, world.members)
    beh_truth = Truth({v: k[0] for k, v in opaque.items()}, k_of, world.members)
    out = Sim(world, behavior, R.REFERENCE if policy is None else policy, [], [], [], truth, beh_truth, devices, dias)

    paused: dict = {}
    mood: dict = {}
    paused_log = defaultdict(set)
    diag_gt = [1] * n_d
    for t in range(world.ticks):
        alive = [d for d in range(n_d) if world.birth[d] <= t]
        alive_set, beh_commits = set(alive), defaultdict(list)
        for p in persons:
            dev = devices[p.pid]
            dev.new_period()
            ds = sorted((d for d in p.diamonds if d in alive_set), key=lambda d: U(base, "ord", p.pid, t, d))
            if behavior.shared_pause:                                # pausa de persona: cost_zero_stop al dispositiu
                was = paused.get(p.pid, False)
                now = chain(was, behavior.p_pause_on, behavior.p_pause_off, U(base, "pause", p.pid, t))
                paused[p.pid] = now
                if now and not was:
                    dev.pause()
                elif was and not now:
                    dev.resume()
                if now:
                    paused_log[p.pid].add(t)
            if behavior.shared_mood:
                mood[p.pid] = chain(mood.get(p.pid, False), behavior.p_mood_on, behavior.p_mood_off, U(base, "mood", p.pid, t))
            for d in ds:
                if not behavior.shared_pause:                        # model nul: una cadena per (persona, Diamant)
                    paused[(p.pid, d)] = chain(paused.get((p.pid, d), False), behavior.p_pause_on, behavior.p_pause_off,
                                               U(base, "pause", p.pid, d, t))
                if not behavior.shared_mood:
                    mood[(p.pid, d)] = chain(mood.get((p.pid, d), False), behavior.p_mood_on, behavior.p_mood_off,
                                             U(base, "mood", p.pid, d, t))
                is_paused = paused[p.pid] if behavior.shared_pause else paused[(p.pid, d)]
                grumpy = mood[p.pid] if behavior.shared_mood else mood[(p.pid, d)]
                if is_paused or U(base, "off", p.pid, d, t) < behavior.p_offline:
                    continue
                if behavior.budget_split:
                    c_raw = round(p.a * behavior.saturation * p.weights[p.diamonds.index(d)] + 0.6 * gauss(base, "c", p.pid, d, t))
                else:
                    c_raw = p.mu[d] + int(U(base, "c", p.pid, d, t) * 3) - 1
                c_raw = min(max(c_raw, 0), R.C_RAW_MAX)
                if level_override is not None:
                    c_raw = min(max(level_override(p.pid, d, t, c_raw), 0), R.C_RAW_MAX)
                rec = dev.commit(dias[d].d_id, dias[d].epoch, c_raw)
                sum_c, s_, B_ = dev.audit_state()
                out.max_overshoot = max(out.max_overshoot, sum_c + s_ - B_)
                if rec is None:
                    out.refusals += 1
                elif dias[d].accept(rec, now=t * 86_400_000_000_000 + int(U(base, "now", p.pid, d, t) * 86_400_000_000_000)):
                    beh_commits[d].append({"pseud": opaque[(p.pid, d)], "c": rec["c"]})
                    out.signed.setdefault((t, d), set()).add(rec["pseud"])
                if U(base, "veto", p.pid, d, t) < (behavior.p_veto_grumpy if grumpy else behavior.p_veto_calm):
                    tok = dias[d].mint_token(pseud[(p.pid, d)])
                    if tok is not None and dias[d].veto(tok, author=pseud[(p.pid, d)]):
                        out.veto_log[(t, d)] = out.veto_log.get((t, d), 0) + 1
        for d in alive:                                              # publicació per lots, un manifest per Diamant
            b = R.canonical(dias[d].manifest())
            out.raw.append(b)
            out.feed.append((t, d, json.loads(b)))
            out.beh_feed.append((t, d, {"d_id": world.d_ids[d], "diag_active": diag_gt[d],
                                        "commits": sorted(beh_commits[d], key=lambda c: c["pseud"])}))
            dias[d].advance_epoch()
            if out.veto_log.get((t, d)):
                diag_gt[d] = diag_gt[d] % 4 + 1
    out.paused_log = dict(paused_log)
    return out


# ==========================================================================
# 3. Adversari: extracció genèrica
# ==========================================================================
@dataclass
class Handle:
    stream: int
    s: str
    paths: Counter = field(default_factory=Counter)
    ticks: set = field(default_factory=set)
    series: dict = field(default_factory=lambda: defaultdict(dict))     # clau numèrica germana -> {tic: valor}
    strs: dict = field(default_factory=lambda: defaultdict(list))       # clau textual germana -> [valors]
    present: set = field(default_factory=set)


def walk(obj, path=()):
    """Fulles (camí, valor, contenidor immediat)."""
    items = obj.items() if isinstance(obj, dict) else enumerate(obj)
    for k, v in items:
        if isinstance(v, (dict, list)):
            yield from walk(v, path + (k,))
        else:
            yield path + (k,), v, obj


def extract(feed: list):
    """Nanses = cadenes llargues (>= 16) no de primer nivell que persisteixen >= 2 tics d'un mateix flux."""
    hs: dict = {}
    ticks_of = defaultdict(set)
    sser = defaultdict(lambda: defaultdict(dict))
    for t, stream, m in feed:
        ticks_of[stream].add(t)
        for k, v in m.items():
            if isinstance(v, (bool, int, float)):
                sser[stream][k][t] = float(v)
        for path, val, parent in walk(m):
            if not (isinstance(val, str) and len(val) >= 16 and len(path) >= 2):
                continue
            h = hs.get((stream, val))
            if h is None:
                h = hs[(stream, val)] = Handle(stream, val)
            h.paths[path] += 1
            h.ticks.add(t)
            if isinstance(parent, dict):
                for k2, v2 in parent.items():
                    if k2 == path[-1]:
                        continue
                    if isinstance(v2, (bool, int, float)):
                        h.series[k2][t] = float(v2)
                        h.present.add(t)
                    elif isinstance(v2, str):
                        h.strs[k2].append(v2)
    handles = [h for h in hs.values() if len(h.ticks) >= 2 and h.present]
    alive = {s: (min(ts), max(ts)) for s, ts in ticks_of.items()}
    return handles, alive, sser


def stable_paths(h: Handle) -> set:
    return {p for p, c in h.paths.items() if c >= 0.9 * len(h.ticks)}


# ==========================================================================
# 4. Adversari: estadístics i contrast per permutació
# ==========================================================================
@dataclass
class Result:
    auc: float
    z: float
    null_mean: float = 0.5
    null_sd: float = 0.0
    n_pos: int = 0
    n_neg: int = 0


def binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k) per a X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    if p <= 0.0:
        return 0.0
    tot = 0.0
    for x in range(k, n + 1):
        tot += math.exp(math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(n - x + 1)
                        + x * math.log(p) + (n - x) * math.log1p(-p))
    return min(1.0, tot)


def sparse_test(scores: dict, positives: list) -> Result:
    """Estadístics gairebé sempre 0 (k-grams, col·lisions): l'AUC per permutació és patològic.

    Contrast exacte: quants positius tenen una puntuació > la base, davant la taxa dels negatius.
    """
    pos = set(positives)
    base = min(scores.values())
    neg = [v for q, v in scores.items() if q not in pos]
    p0 = (sum(1 for v in neg if v > base) + 1.0) / (len(neg) + 2.0)         # suavitzat de Laplace
    hits = sum(1 for q in positives if scores[q] > base)
    pv = binom_sf(hits, len(positives), p0)
    z = -NormalDist().inv_cdf(max(pv, 1e-300)) if pv < 0.5 else 0.0
    a = auc([scores[q] for q in positives], neg)
    return Result(a, z, 0.5, 0.0, len(positives), len(neg))


def pair_test(n: int, groups: list, scores: dict, positives: list, rng: random.Random, n_perm: int) -> Result:
    """AUC dels positius entre tots els parells candidats; nul per permutació de nanses DINS de cada grup.

    Els parells comparteixen nanses (no són independents): per això el nul és de permutació
    i no la fórmula analítica.
    """
    pairs = sorted(scores)
    vals = [scores[p] for p in pairs]
    if positives and len(positives) < len(pairs):
        lo = min(vals)
        if sum(1 for v in vals if v > lo) < 0.02 * len(vals):
            return sparse_test(scores, positives)
    ranks = dict(zip(pairs, avg_ranks(vals)))
    total = len(pairs)

    def auc_of(posset) -> float:
        npos, nneg = len(posset), total - len(posset)
        return (sum(ranks[p] for p in posset) - npos * (npos + 1) / 2.0) / (npos * nneg)

    if not positives or total <= len(positives):
        return Result(0.5, 0.0)
    obs = auc_of(positives)
    by_group = defaultdict(list)
    for i in range(n):
        by_group[groups[i]].append(i)
    null = []
    for _ in range(n_perm):
        perm = list(range(n))
        for idxs in by_group.values():
            sh = idxs[:]
            rng.shuffle(sh)
            for a, b in zip(idxs, sh):
                perm[a] = b
        null.append(auc_of([(min(perm[i], perm[j]), max(perm[i], perm[j])) for i, j in positives]))
    mean = sum(null) / len(null)
    sd = math.sqrt(sum((x - mean) ** 2 for x in null) / (len(null) - 1))
    z = 0.0 if abs(obs - mean) < 1e-12 else ((obs - mean) / sd if sd > 1e-12 else math.copysign(1e9, obs - mean))
    return Result(obs, z, mean, sd, len(positives), total - len(positives))


def cls_test(values: list, labels: list) -> Result:
    """AUC (positiu = pont) d'una característica per pseudònim; z bilateral amb l'error analític."""
    pos = [v for v, l in zip(values, labels) if l]
    neg = [v for v, l in zip(values, labels) if not l]
    a = auc(pos, neg)
    se = auc_null_se(len(pos), len(neg)) if pos and neg else 1.0
    return Result(a, (a - 0.5) / se, 0.5, se, len(pos), len(neg))


@dataclass
class Report:
    pair: dict
    cls: dict
    meta: dict

    def zmax(self, kinds=("pair", "cls"), names=None):
        best = ("-", 0.0)
        for kind in kinds:
            for name, r in getattr(self, kind).items():
                if names is not None and name not in names:
                    continue
                if abs(r.z) > abs(best[1]):
                    best = (f"{kind}:{name}", r.z)
        return best

    def lines(self) -> list:
        out = [f"  {k}:{n:<14} AUC={r.auc:.3f}  z={r.z:+7.2f}  (nul {r.null_mean:.3f}±{r.null_sd:.3f}, +{r.n_pos}/-{r.n_neg})"
               for k in ("pair", "cls") for n, r in getattr(self, k).items()]
        return out


def run_adversary(feed: list, truth: Truth, *, seed: int = 0, n_perm: int = 300, min_overlap: int = 8) -> Report:
    H, alive, sser = extract(feed)
    n = len(H)
    T = 1 + max(t for t, _, _ in feed)
    person = [truth.person_of.get(h.s) for h in H]
    stream = [h.stream for h in H]
    rng = random.Random(f"perm|{seed}")

    # --- precòmput per nansa -------------------------------------------------
    gram = [{h.s[k:k + 6] for k in range(len(h.s) - 5)} for h in H]
    vals = [{h.s} | {v for vs in h.strs.values() for v in vs} for h in H]
    df = Counter(v for s in vals for v in s)
    vals = [{v for v in s if df[v] <= max(3, 0.1 * n)} for s in vals]           # fora constants comunes
    sp = [stable_paths(h) for h in H]
    vec = []
    for h in H:
        lo, hi = alive[h.stream]
        v = [None] * T
        for t in range(lo, hi + 1):
            v[t] = 1.0 if t in h.present else 0.0
        vec.append(v)
    cser = [h.series.get("c", {}) for h in H]
    mean_c = [sum(s.values()) / len(s) if s else None for s in cser]

    def aligned_z(a: str, b: str) -> float:
        L = min(len(a), len(b))
        m = sum(1 for k in range(L) if a[k] == b[k])
        return (m - L / 16.0) / math.sqrt(L * (1 / 16.0) * (15 / 16.0))

    def presence_corr(i: int, j: int) -> float:
        lo, hi = max(alive[stream[i]][0], alive[stream[j]][0]), min(alive[stream[i]][1], alive[stream[j]][1])
        xs, ys = [], []
        for t in range(lo, hi + 1):
            xs.append(vec[i][t])
            ys.append(vec[j][t])
        r = pearson(xs, ys) if len(xs) >= min_overlap else None
        return 0.0 if r is None else r

    def series_corr(si: dict, sj: dict) -> Optional[float]:
        common = sorted(si.keys() & sj.keys())
        return pearson([si[t] for t in common], [sj[t] for t in common]) if len(common) >= 6 else None

    def c_corr(i: int, j: int) -> float:
        r = series_corr(cser[i], cser[j])
        return 0.0 if r is None else abs(r)

    def level_sim(i: int, j: int) -> float:
        if mean_c[i] is None or mean_c[j] is None or len(cser[i]) < 3 or len(cser[j]) < 3:
            return -16.0
        return -abs(mean_c[i] - mean_c[j])

    def sib_corr(i: int, j: int) -> float:
        best = 0.0
        for k in (H[i].series.keys() & H[j].series.keys()) - {"c"}:
            r = series_corr(H[i].series[k], H[j].series[k])
            if r is not None:
                best = max(best, abs(r))
        return best

    pair_stats = {
        "tok_gram": lambda i, j: float(len(gram[i] & gram[j])),
        "tok_aligned": lambda i, j: aligned_z(H[i].s, H[j].s),
        "collide": lambda i, j: float(len(vals[i] & vals[j])),
        "path": lambda i, j: 1.0 if sp[i] & sp[j] else 0.0,
        "sib_corr": sib_corr,
        "presence_corr": presence_corr,
        "c_corr": c_corr,
        "level_sim": level_sim,
    }
    cand = [(i, j) for i in range(n) for j in range(i + 1, n) if stream[i] != stream[j]]
    positives = [(i, j) for i, j in cand if person[i] is not None and person[i] == person[j]]
    res_pair = {name: pair_test(n, stream, {(i, j): f(i, j) for i, j in cand}, positives, rng, n_perm)
                for name, f in pair_stats.items()}

    # --- nivell Diamant: els «no» (canvis de les magnituds de primer nivell) coincideixen? ---
    chg = {}
    for s, keys in sser.items():
        for k, ser in keys.items():
            ts = sorted(ser)
            chg.setdefault(s, {})[k] = {t: (1.0 if ser[t] != ser[p] else 0.0) for p, t in zip(ts, ts[1:])}
    streams = sorted(chg)
    sidx = {s: i for i, s in enumerate(streams)}

    def step_corr(a: int, b: int) -> float:
        best = 0.0
        for k in chg[streams[a]].keys() & chg[streams[b]].keys():
            r = series_corr(chg[streams[a]][k], chg[streams[b]][k])
            if r is not None:
                best = max(best, r)
        return best

    d_pairs = [(a, b) for a in range(len(streams)) for b in range(a + 1, len(streams))]
    shared = set()
    pid_streams = defaultdict(set)
    for d, mem in enumerate(truth.members):
        for p in mem:
            pid_streams[p].add(d)
    for ds in pid_streams.values():
        for x, y in itertools.combinations(sorted(ds), 2):
            if x in sidx and y in sidx:
                shared.add((min(sidx[x], sidx[y]), max(sidx[x], sidx[y])))
    if len(d_pairs) > len(shared) > 0:
        res_pair["step_corr"] = pair_test(len(streams), [0] * len(streams), {p: step_corr(*p) for p in d_pairs},
                                          sorted(shared), rng, n_perm)

    # --- pont o independent? (per pseudònim) ----------------------------------
    labels = [(truth.k_of[p] >= 2) if p is not None else None for p in person]
    keep = [i for i in range(n) if labels[i] is not None]

    def sigs(h: Handle) -> list:
        for k, vs in h.strs.items():
            if vs and all(len(v) >= 64 for v in vs):
                return vs
        return []

    feats = {
        "mean_c": [mean_c[i] if mean_c[i] is not None else 0.0 for i in range(n)],
        "var_c": [(sum((x - mean_c[i]) ** 2 for x in cser[i].values()) / len(cser[i])) if cser[i] else 0.0 for i in range(n)],
        "presence_rate": [len(H[i].present) / (alive[stream[i]][1] - alive[stream[i]][0] + 1) for i in range(n)],
        "n_present": [float(len(H[i].present)) for i in range(n)],
        "first_seen": [float(alive[stream[i]][0]) for i in range(n)],
        "pseud_pop": [float(int(H[i].s, 16).bit_count()) if all(c in "0123456789abcdef" for c in H[i].s) else 0.0 for i in range(n)],
        "sig_pop": [(sum(int(v, 16).bit_count() for v in sigs(H[i])) / len(sigs(H[i]))) if sigs(H[i]) else 0.0 for i in range(n)],
    }
    # «slot»: primer índex enter del primer camí estable (la posició de la nansa al manifest)
    feats["slot"] = [float(next((x for q in sorted(sp[i], key=str) for x in q if isinstance(x, int)), -1)) for i in range(n)]
    res_cls = {name: cls_test([v[i] for i in keep], [labels[i] for i in keep]) for name, v in feats.items()}
    meta = {"n_handles": n, "n_pairs": len(cand), "n_pos": len(positives), "n_bridge": sum(1 for i in keep if labels[i]),
            "n_indep": sum(1 for i in keep if not labels[i])}
    return Report(res_pair, res_cls, meta)
