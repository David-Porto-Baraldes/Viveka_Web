"""test_hu_diamond_fil_d_or.py - CI del Segell de ROUND-4: HU-DIAMOND · Fil d'Or v1.1.

v1.1 (4-11-2026): la REFERÈNCIA ja és la que David i Viveka han adoptat: només es publica la presència
(`c_levels = 1`) i el baricentre és f(presència, diag_active) (§G). hu_adversary.py no canvia respecte de la v1.
Els 16 nivells de la v1 continuen sent una opció mesurable (`P(c_levels=16)`), ja no la referència.

Fitxers:  hu_diamond_ref.py (el protocol, executable)  ·  hu_adversary.py (població, comportament, adversari)
          test_hu_diamond_fil_d_or.py (aquest fitxer)

Què verifica (cada bloc és una promesa del Fil d'Or, no un detall del codi):

  §A  Geometria: 48/12 = 4 diagonals del cub; 2 axials + 6 orbitals (3+3); cada seient axial 1 cop per cicle.
  §B  HKDF (RFC 5869) per (persona, Diamant): vectors oficials, contrast amb una biblioteca, separació de dominis.
  §C  Població: N persones en <= 3 Diamants, 4 seients humans per Diamant.
  §D  Lleis L1..L7 i baricentre (B) amb un detector per promesa, i els MATEIXOS detectors contra 22 MUTANTS
      (controls negatius): un mutant per fallada coneguda; si cap verificació no el veu, el test falla.
  §E  Adversari sintètic (només veu els manifests publicats): pont vs independent.
        - model NUL (comportament independent entre cercles): tots els estadístics a l'atzar -> el protocol no afegeix res;
        - model ACOBLAT (pauses i pressupost compartits): estadístics del protocol a l'atzar i desigualtat de
          processament de dades: la vista publicada no en sap més que el comportament sol;
        - potència: l'adversari detecta els mutants estructurals;
        - mesures informatives del canal que cap protocol no tanca (es veuen amb `pytest -s` o `-rP`).
  §F  Les set lleis sobre la població simulada (mons bessons per a L1; L3..L7 sobre ~1.300 manifests).
  §G  Baricentre (v1.1): pes 2 per seient de la parella activa i pes 1 per als orbitals; `None` sense cap seient
      present (mai l'origen, que és el valor dels vuit); només depèn de la presència, i es llegeix del manifest públic.

Ús:   pip install pytest cryptography   &&   pytest -q [-rP]        (Python >= 3.10; ~40 s)
      Els tres fitxers van junts a la mateixa carpeta i s'importen com a mòduls de primer nivell: la carpeta no ha de
      tenir `__init__.py` (si en té, `pythonpath = <carpeta>` a pytest.ini).
Variables: HU_N (persones, 120), HU_TICKS (èpoques, 30), HU_SEEDS (llavors del model nul, 3),
           HU_PERM (permutacions, 200), HU_REPORT (ruta d'un JSON amb les xifres mesurades).
Nocturn recomanat: HU_N=200 HU_TICKS=40 HU_SEEDS=10.   Tot és determinista (llavors fixes, cap rellotge, cap xarxa).
Límits: no prova l'anonimat de l'emissió de fitxes de veto (RFC 9474 és un oracle aquí), ni el que fa l'operador,
        ni garanteix cap cosa per sota del terra de detecció (AUC ~0,61-0,65 enllaç, ~0,70 pont) amb N = 120.
"""
from __future__ import annotations

import dataclasses
import hashlib
import itertools
import json
import math
import os
import random
import re
from dataclasses import dataclass
from fractions import Fraction

import pytest

import hu_adversary as A
import hu_diamond_ref as R

N_PERSONS = int(os.environ.get("HU_N", "120"))
TICKS = int(os.environ.get("HU_TICKS", "30"))
SEEDS = int(os.environ.get("HU_SEEDS", "3"))
N_PERM = int(os.environ.get("HU_PERM", "200"))
Z_THR = 4.5                         # llindar de detecció (bilateral); calibrat al nul de la v1.1: max|z| = 2,9 en 60 llavors
REPORT: dict = {}


def P(**kw) -> R.Policy:
    return dataclasses.replace(R.REFERENCE, **kw)


@dataclass
class Finding:
    ok: bool
    detail: str = ""


# ==========================================================================
# Món de joguina determinista per als detectors de lleis
# ==========================================================================
def mini_world(policy, *, seed=11, n_persons=4, n_diamonds=1, budgets=None, s=0, shared=None):
    rng = random.Random(seed)
    roots = [rng.randbytes(32) for _ in range(n_persons)]
    budgets = budgets or [10_000] * n_persons
    devs = [R.Device(r, b, s, policy) for r, b in zip(roots, budgets)]
    counter = shared if shared is not None else itertools.count()
    dias = [R.Diamond(A.sha_hex("mini", seed, d), policy, counter) for d in range(n_diamonds)]
    op = hashlib.sha256(b"operator").digest()
    for dia in dias:
        for j in range(4):
            dia.seat(R.AISeat(f"sister-{j}", dia.d_id, {}, policy).pseud(op), "ia")
        for p, dev in enumerate(devs):
            dia.seat(dev.pseud(dia.d_id), "hu", prefer=p)
    return devs, dias


def scenario(policy, *, epochs=3, now_step=977, arrival=None, budgets=None):
    """Un Diamant, 4 persones, un veto a l'època 0 i dos silencis a l'època 1. Retorna els manifests."""
    devs, dias = mini_world(policy, budgets=budgets)
    dia, out, now = dias[0], [], 1_730_000_000_000_000_000
    for e in range(epochs):
        for dev in devs:
            dev.new_period()
        for p in (arrival[e] if arrival else range(4)):
            if e == 1 and p in (2, 3):
                continue
            rec = devs[p].commit(dia.d_id, dia.epoch, 3 + p)
            now += now_step
            if rec is not None:
                dia.accept(rec, now=now)
        if e == 0:
            who = devs[1].pseud(dia.d_id)
            dia.veto(dia.mint_token(who), author=who)
        out.append(dia.manifest())
        dia.advance_epoch()
    return out


def leaves(obj, path=()):
    items = obj.items() if isinstance(obj, dict) else enumerate(obj)
    for k, v in items:
        if isinstance(v, (dict, list)):
            yield from leaves(v, path + (k,))
        else:
            yield path + (k,), v


# ==========================================================================
# Detectors de lleis (la mateixa funció jutja el model de referència i els mutants)
# ==========================================================================
def det_L1_noninterference(policy) -> Finding:
    """L1: res publicat a D0 depèn de què fa la persona als ALTRES Diamants (mentre sigui factible signar)."""
    def world(other):
        devs, dias = mini_world(policy, n_diamonds=3)
        out = []
        for e in range(3):
            for dev in devs:
                dev.new_period()
            for p, dev in enumerate(devs):
                for k in (1, 2):
                    dias[k].accept(dev.commit(dias[k].d_id, dias[k].epoch, other[(e + p + k) % len(other)]))
                dias[0].accept(dev.commit(dias[0].d_id, dias[0].epoch, 5))
            out.append(R.canonical(dias[0].manifest()))
            for dia in dias:
                dia.advance_epoch()
        return out
    a, b = world([1, 2, 3]), world([9, 7, 4, 6])
    return Finding(a == b, "" if a == b else "el manifest de D0 canvia quan només canvien els altres cercles")


def det_L1_ai_isolation(policy) -> Finding:
    """L1 (IA): un context per Diamant, sense memòria compartida."""
    def reply(secret):
        mem = {}
        a, b = R.AISeat("sister-0", "dA", mem, policy), R.AISeat("sister-0", "dB", mem, policy)
        a.observe("dA", "context públic d'A")
        b.observe("dB", secret)
        return a.respond("què recordes?")
    blocked = False
    try:
        R.AISeat("sister-0", "dA", {}, policy).observe("dB", "x")
    except R.CrossDiamondData:
        blocked = True
    same = reply("secret-1") == reply("secret-2")
    return Finding(same and blocked, f"resposta independent={same}, dades creuades bloquejades={blocked}")


def det_L2_unlinkable(policy) -> Finding:
    """L2: claus per (persona, Diamant): diferents, re-derivables, i indistingibles de l'atzar entre Diamants."""
    rng = random.Random(3)
    ids = [A.sha_hex("l2", k) for k in range(3)]
    dists, same_person_distinct = [], True
    for _ in range(200):
        root = rng.randbytes(32)
        a, b, c = (R.Device(root, 100, 0, policy).pseud(d) for d in ids)
        same_person_distinct &= len({a, b, c}) == 3
        dists.append(bin(int(a, 16) ^ int(b, 16)).count("1"))
    mean = sum(dists) / len(dists)
    se = math.sqrt(256 * 0.25) / math.sqrt(len(dists))
    stat_ok = abs(mean - 128) <= 4.5 * se and min(dists) > 60
    devs, dias = mini_world(policy, n_diamonds=2)
    for dia in dias:                                        # i en un flux real: cap cadena llarga comuna a dos Diamants
        for p, dev in enumerate(devs):
            dia.accept(dev.commit(dia.d_id, dia.epoch, 4))
    sets = [{v for _, v in leaves(d.manifest()) if isinstance(v, str) and len(v) >= 16 and v != d.d_id} for d in dias]
    shared = sets[0] & sets[1]
    ok = same_person_distinct and stat_ok and not shared
    return Finding(ok, f"distints={same_person_distinct}, Hamming mitjà={mean:.1f}, cadenes compartides={len(shared)}")


def det_L2_seat_independence(policy) -> Finding:
    """L2: la posició al manifest (quina parella) no ha de repetir-se entre els Diamants d'una persona."""
    same = total = 0
    for g in range(50):
        devs, dias = mini_world(policy, seed=100 + g, n_diamonds=2)
        slots = [{r[1]: j for j, r in enumerate(dia.manifest()["parelles"])} for dia in dias]
        for dev in devs:
            same += slots[0][dev.pseud(dias[0].d_id)] == slots[1][dev.pseud(dias[1].d_id)]
            total += 1
    limit = total / 4 + 4.5 * math.sqrt(total * 3 / 16)
    return Finding(same <= limit, f"seients repetits {same}/{total} (esperat {total / 4:.0f}, límit {limit:.0f})")


def det_L3_budget(policy) -> Finding:
    """L3: el dispositiu només signa si L = Σc + s <= B; refusar no canvia l'estat; res més no en surt."""
    api = {n for n in dir(R.Device) if not n.startswith("_")}
    if api != {"pseud", "new_period", "pause", "resume", "audit_state", "commit"}:
        return Finding(False, f"API pública inesperada: {sorted(api)}")
    rng = random.Random(5)
    for trial in range(60):
        B, s = rng.randrange(6, 20), rng.randrange(0, 4)
        dev = R.Device(rng.randbytes(32), B, s, policy)
        ds = [A.sha_hex("l3", trial, k) for k in range(3)]
        for period in range(8):
            dev.new_period()
            for _ in range(rng.randrange(1, 6)):
                d, c = rng.choice(ds), rng.randrange(0, 16)
                before = dev.audit_state()
                rec = dev.commit(d, period, c)
                sum_c, s_, B_ = dev.audit_state()
                if sum_c + s_ > B_:
                    return Finding(False, f"L = {sum_c + s_} > B = {B_}")
                if rec is None and dev.audit_state() != before:
                    return Finding(False, "refusar ha canviat l'estat")
                if rec is not None and rec["c"] != c * policy.c_levels // 16:
                    return Finding(False, "el dispositiu ha signat un c diferent del real (attest false)")
    return Finding(True)


def det_L3_no_global_predicate(policy) -> Finding:
    """L3: cap predicat global, cap magnitud sobre totes les pertinences, enlloc del manifest."""
    ms = scenario(policy, budgets=[6, 6, 6, 6])
    bad = []
    for m in ms:
        for path, v in leaves(m):
            if isinstance(v, bool):
                bad.append(f"booleà a {path}")
            if any(re.search(r"attest|budget|margin|total|limit|sum", str(x), re.I) for x in path if isinstance(x, str)):
                bad.append(f"camp sospitós {path}")
        bad += R.validate_manifest(m)
    return Finding(not bad, "; ".join(sorted(set(bad))[:3]))


def det_L4_silence(policy) -> Finding:
    """L4: el silenci no és consentiment i una signatura d'una època no es pot reutilitzar en una altra."""
    devs, dias = mini_world(policy)
    dia = dias[0]
    recs0 = []
    for dev in devs:
        recs0.append(dev.commit(dia.d_id, dia.epoch, 4))
        dia.accept(recs0[-1])
    if not all(dia.consent_ok(dev.pseud(dia.d_id)) for dev in devs):
        return Finding(False, "sense consentiment amb signatura vàlida")
    dia.advance_epoch()
    for dev in devs:
        dev.new_period()
    for p in (0, 1):
        dia.accept(devs[p].commit(dia.d_id, dia.epoch, 4))
    silent_ok = all(not dia.consent_ok(devs[p].pseud(dia.d_id)) for p in (2, 3))
    n = len(dia.manifest()["commits"])
    replay = dia.accept(recs0[2])
    return Finding(silent_ok and n == 2 and not replay, f"silenci sense consentiment={silent_ok}, commits={n}, reutilitzada={replay}")


def det_L4_pause(policy) -> Finding:
    """L4: pausa = c := 0 sense deute i indistingible de qualsevol altra absència (fora de línia, refús per pressupost)."""
    def world(mode):
        budgets = [10_000, 3 if mode == "refused" else 10_000, 10_000, 10_000]
        devs, dias = mini_world(policy, budgets=budgets)
        dia, out = dias[0], []
        for e in range(2):
            for dev in devs:
                dev.new_period()
            for p, dev in enumerate(devs):
                if p == 1 and e == 1:
                    if mode == "offline":
                        continue
                    if mode == "paused":
                        dev.pause()
                rec = dev.commit(dia.d_id, dia.epoch, 5 if (p == 1 and e == 1) else 2)
                if rec is not None:
                    dia.accept(rec)
            out.append(R.canonical(dia.manifest()))
            dia.advance_epoch()
        return out, devs[1]
    (a, dev_p), (b, _), (c, _) = world("paused"), world("offline"), world("refused")
    no_debt = dev_p.audit_state()[0] == 0
    dev_p.resume()
    dev_p.new_period()
    back = dev_p.commit("x" * 32, 0, 15) is not None
    same = a == b == c
    return Finding(same and no_debt and back, f"indistingible={same}, sense deute={no_debt}, torna a signar={back}")


def det_L5_author(policy) -> Finding:
    """L5: l'efecte del «no» és públic i l'autor no: el manifest és el mateix sigui qui sigui el qui vetoa (8 seients)."""
    outs = []
    for i in range(8):
        devs, dias = mini_world(policy)
        dia = dias[0]
        seats = dia.seated("hu") + dia.seated("ia")
        for dev in devs:
            dia.accept(dev.commit(dia.d_id, dia.epoch, 3))
        tok = dia.mint_token(seats[i])
        dia.veto(tok, author=seats[i])
        m0 = R.canonical(dia.manifest())
        dia.advance_epoch()
        outs.append((m0, R.canonical(dia.manifest())))
    same = all(o == outs[0] for o in outs)
    devs, dias = mini_world(policy)
    dia = dias[0]
    mine = dia.seated("hu")[0]
    t1 = dia.mint_token(mine)
    integrity = (dia.mint_token("ff" * 32) is None and dia.mint_token(mine) is None
                 and not dia.veto(b"\x00" * 32) and dia.veto(t1) and not dia.veto(t1))
    return Finding(same and integrity, f"autor no publicat={same}, integritat de les fitxes={integrity}")


def det_L5_step(policy) -> Finding:
    """L5: un sol pas a l'època següent, sigui quin sigui el nombre de «no»; cicle 1→2→3→4→1."""
    devs, dias = mini_world(policy)
    dia = dias[0]
    seats = dia.seated()
    seen = []
    for n_veto in (0, 3, 1, 1, 1, 0):
        for k in range(n_veto):
            dia.veto(dia.mint_token(seats[k]), author=seats[k])
        seen.append(dia.manifest()["diag_active"])
        dia.advance_epoch()
    expected = [1, 1, 2, 3, 4, 1]
    return Finding(seen == expected, f"diag_active publicat {seen}, esperat {expected}")


def det_L6_schema(policy) -> Finding:
    """L6 (i L2, L3, L7): esquema estricte, sense camps nous ni text lliure."""
    errs = []
    for m in scenario(policy):
        errs += R.validate_manifest(m)
    return Finding(not errs, "; ".join(sorted(set(errs))[:3]))


BANNED = {
    "ca": r"altres? cercles?|altres? diamants?|cap altre|per què|perquè no|motiu|\braó\b|justific|decliner|rebutj|excus|expliqu",
    "es": r"otros? c[ií]rculos?|otros? diamantes?|por qu[eé]|motivo|\braz[oó]n\b|justific|declin|rechaz|excus|expl[ií]c",
    "en": r"other circles?|other diamonds?|\bwhy\b|reason|justif|declin|refus|excus|explain",
}


def det_L6_prompts(prompts) -> Finding:
    """L6: les preguntes que el sistema fa són tancades i no mencionen altres cercles ni demanen justificar un refús."""
    bad = []
    for lang, qs in prompts.items():
        for key, text in qs.items():
            if re.search(BANNED[lang], text.lower()):
                bad.append(f"{lang}.{key}")
    free_text = [k for k, v in R.ANSWER_TYPES.items() if re.search(r"str|text|free", v)]
    return Finding(not bad and not free_text, f"preguntes prohibides {bad}, respostes de text lliure {free_text}")


def det_L7_time(policy) -> Finding:
    """L7: cap marca per esdeveniment: el manifest és idèntic si els mateixos fets passen en moments diferents."""
    a = [R.canonical(m) for m in scenario(policy, now_step=977)]
    b = [R.canonical(m) for m in scenario(policy, now_step=86_400_000_003)]
    big = [p for m in scenario(policy) for p, v in leaves(m) if isinstance(v, int) and not isinstance(v, bool) and v >= 2 ** 20]
    return Finding(a == b and not big, f"manifest independent del temps={a == b}, enters grans={big[:2]}")


def det_L7_counter(policy) -> Finding:
    """L7: cap comptador compartit entre Diamants: l'ordre de publicació dels altres no canvia el manifest d'un."""
    def world(order):
        devs, dias = mini_world(policy, n_diamonds=3)
        out = []
        for e in range(3):
            for dev in devs:
                dev.new_period()
            for dia in dias:
                for p, dev in enumerate(devs):
                    dia.accept(dev.commit(dia.d_id, dia.epoch, 2 + p))
            for d in order:
                m = dias[d].manifest()
                if d == 0:
                    out.append(R.canonical(m))
            for dia in dias:
                dia.advance_epoch()
        return out
    a, b = world([0, 1, 2]), world([2, 1, 0])
    return Finding(a == b, "" if a == b else "el manifest depèn de l'ordre de publicació d'altres Diamants")


def det_L7_state(policy) -> Finding:
    """L7: només estat actual: mida acotada i independent de l'historial; <= 20 línies; cap camp d'historial."""
    ms = scenario(policy, epochs=14)
    s10, s11 = len(R.canonical(ms[10])), len(R.canonical(ms[11]))
    lines = max(len(R.manifest_lines(m)) for m in ms)
    keys = set().union(*[set(m) for m in ms])
    ok = s10 == s11 and s11 <= 2048 and lines <= R.MAX_MANIFEST_LINES and keys <= set(R.TOP_FIELDS)
    return Finding(ok, f"mida època 10={s10}, 11={s11}, línies={lines}, camps={sorted(keys - set(R.TOP_FIELDS))}")


def det_L7_order(policy) -> Finding:
    """L7: l'ordre d'arribada dels compromisos és un temps per esdeveniment amagat: no ha de ser visible."""
    fw = [[0, 1, 2, 3]] * 3
    bw = [[3, 2, 1, 0]] * 3
    a = [R.canonical(m) for m in scenario(policy, arrival=fw)]
    b = [R.canonical(m) for m in scenario(policy, arrival=bw)]
    return Finding(a == b, "" if a == b else "el manifest depèn de l'ordre d'arribada")


# --------------------------------------------------------------------------
# Baricentre (B): oracle independent i quatre detectors
# --------------------------------------------------------------------------
# L'oracle no importa res del model de referència: té la seva taula de vèrtexs i la seva aritmètica. Si el model i
# l'oracle s'equivoquessin igual, els valors calculats a mà (§G, GOLDEN) ho delatarien.
ORACLE_IA = ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1))        # vèrtex de l'IA de cada parella; l'humà seu a l'antípoda
ALL_SEATS = tuple((j, kind) for j in range(4) for kind in ("ia", "hu"))


def oracle_vertex(seat):
    v = ORACLE_IA[seat[0]]
    return v if seat[1] == "ia" else tuple(-x for x in v)


def oracle_bary(present, diag_active):
    """Pes 2 per cada seient de la parella activa, 1 per cada seient orbital; None si no hi ha cap seient present."""
    w = {s: (2 if s[0] == diag_active - 1 else 1) for s in present}
    total = sum(w.values())
    if total == 0:
        return None
    return tuple(Fraction(sum(wt * oracle_vertex(s)[axis] for s, wt in w.items()), total) for axis in range(3))


def subsets(items):
    items = list(items)
    for r in range(len(items) + 1):
        for comb in itertools.combinations(items, r):
            yield frozenset(comb)


def fmt_bary(b) -> str:
    return "None" if b is None else "(" + ", ".join(str(x) for x in b) + ")"


def bary_world(policy, *, seed, n_ai=4, n_hu=4, signers=(), diag_active=1, c_raw=5):
    """Un Diamant amb `n_ai` IA i `n_hu` humans asseguts, on només els `signers` (índexs d'humà) han signat aquesta època.

    Retorna (diamant, manifest, seients presents ESPERATS). Els esperats surten de com s'ha construït el món
    (qui ha signat i on seu cadascú), no de la llista `commits` del manifest.
    """
    rng = random.Random(seed)
    devs = [R.Device(rng.randbytes(32), 10_000, 0, policy) for _ in range(n_hu)]
    dia = R.Diamond(A.sha_hex("bary", seed), policy)
    op = hashlib.sha256(b"operator").digest()
    for j in range(n_ai):
        dia.seat(R.AISeat(f"sister-{j}", dia.d_id, {}, policy).pseud(op), "ia")
    for dev in devs:
        dia.seat(dev.pseud(dia.d_id), "hu")
    dia.diag_active = diag_active
    for p in signers:
        dia.accept(devs[p].commit(dia.d_id, dia.epoch, c_raw))
    m = dia.manifest()
    who = {devs[p].pseud(dia.d_id) for p in signers}
    expected = {(j, "ia") for j, (ia, _) in enumerate(m["parelles"]) if ia is not None}
    expected |= {(j, "hu") for j, (_, hu) in enumerate(m["parelles"]) if hu in who}
    return dia, m, frozenset(expected)


def det_B_weights(policy) -> Finding:
    """B: pes 2 per a cada seient de la parella de la diagonal activa i 1 per a cada seient orbital (contra l'oracle).

    320 Diamants: cada diagonal activa x 0..4 IA assegudes x els 16 subconjunts d'humans que han signat.
    """
    bad, total, first, seed = 0, 0, "", 0
    for a in (1, 2, 3, 4):
        for n_ai in range(5):
            for signers in subsets(range(4)):
                seed += 1
                dia, m, present = bary_world(policy, seed=seed, n_ai=n_ai, signers=sorted(signers), diag_active=a)
                if not present:
                    continue                                                     # el cas buit és del detector B.empty
                total += 1
                got, want = dia.barycentre(), oracle_bary(present, a)
                if got != want:
                    bad += 1
                    first = first or f"diag={a}, IA={n_ai}, signen={sorted(signers)}: {fmt_bary(got)} en lloc de {fmt_bary(want)}"
    return Finding(bad == 0, f"{bad} de {total} casos fora de l'oracle; el primer: {first}")


def det_B_empty(policy) -> Finding:
    """B: sense cap seient present (pes total 0) el baricentre és None: no es defineix ni es publica. Mai l'origen,
    que és el valor dels vuit seients presents (el silenci total no es pot confondre amb l'equilibri)."""
    bad = []
    for a in (1, 2, 3, 4):
        dia, m, present = bary_world(policy, seed=900 + a, n_ai=0, signers=(), diag_active=a)    # ningú: sense IA, humans callats
        if present:
            bad.append("el món buit no és buit")
        for who, got in (("el Diamant", dia.barycentre()), ("el manifest públic", R.barycentre_from_manifest(m))):
            if got is not None:
                bad.append(f"diag={a}: {who} dóna {fmt_bary(got)} amb cap seient present")
        dia, m, present = bary_world(policy, seed=950 + a, n_ai=4, signers=(0, 1, 2, 3), diag_active=a)   # els vuit
        if len(present) != 8:
            bad.append("el món ple no és ple")
        for who, got in (("el Diamant", dia.barycentre()), ("el manifest públic", R.barycentre_from_manifest(m))):
            if got != (0, 0, 0):
                bad.append(f"diag={a}: {who} dóna {fmt_bary(got)} amb els vuit seients presents")
    return Finding(not bad, "; ".join(bad[:2]))


def det_B_presence(policy) -> Finding:
    """B: un seient humà només és present si ha signat AQUESTA època (callar = absent, L4). Afegir un membre que calla
    no mou el baricentre (relació metamòrfica, sense oracle ni pesos), i el que veu el Diamant és el que qualsevol
    deriva del manifest públic."""
    bad, total, seed = [], 0, 2000
    for a in (1, 2, 3, 4):
        for n_ai in (0, 2, 4):
            for signers in subsets(range(3)):
                seed += 1
                kw = dict(seed=seed, n_ai=n_ai, signers=sorted(signers), diag_active=a)
                d3, _, _ = bary_world(policy, n_hu=3, **kw)
                d4, m4, _ = bary_world(policy, n_hu=4, **kw)                  # el mateix món + un quart membre assegut que calla
                total += 1
                if d3.barycentre() != d4.barycentre():
                    bad.append(f"diag={a}, IA={n_ai}, signen={sorted(signers)}: un membre que calla mou {fmt_bary(d3.barycentre())} "
                               f"a {fmt_bary(d4.barycentre())}")
                if R.barycentre_from_manifest(m4) != d4.barycentre():
                    bad.append(f"diag={a}, IA={n_ai}: el Diamant ({fmt_bary(d4.barycentre())}) no coincideix amb el manifest públic "
                               f"({fmt_bary(R.barycentre_from_manifest(m4))})")
    return Finding(not bad, f"{len(bad)} incidències en {total} parells de mons; la primera: {bad[0] if bad else ''}")


def det_B_level(policy) -> Finding:
    """B: el baricentre és f(presència, diag_active): el nivell no hi pesa. Es mira també amb nivells publicats
    (c_levels = 16): amb c_levels = 1 el nivell val sempre 0 i un mutant que l'usés no es veuria."""
    bad, total = [], 0
    for pol in (policy, dataclasses.replace(policy, c_levels=16)):
        for a in (1, 2, 3, 4):
            for signers in ([0], [0, 1], [0, 1, 2, 3]):
                got = {c_raw: bary_world(pol, seed=3000 + a, signers=signers, diag_active=a, c_raw=c_raw)[0].barycentre()
                       for c_raw in (0, 3, 15)}
                total += 1
                if len(set(got.values())) != 1:
                    bad.append(f"c_levels={pol.c_levels}, diag={a}, signen={signers}: " +
                               ", ".join(f"c_raw={k} -> {fmt_bary(v)}" for k, v in got.items()))
    return Finding(not bad, f"{len(bad)} de {total} casos depenen del nivell; el primer: {bad[0] if bad else ''}")


DETECTORS = {
    "L1.noninterference": det_L1_noninterference,
    "L1.ai_isolation": det_L1_ai_isolation,
    "L2.unlinkable": det_L2_unlinkable,
    "L2.seat_independence": det_L2_seat_independence,
    "L3.budget": det_L3_budget,
    "L3.no_predicate": det_L3_no_global_predicate,
    "L4.silence": det_L4_silence,
    "L4.pause": det_L4_pause,
    "L5.author": det_L5_author,
    "L5.step": det_L5_step,
    "L6.schema": det_L6_schema,
    "L7.time": det_L7_time,
    "L7.counter": det_L7_counter,
    "L7.state": det_L7_state,
    "L7.order": det_L7_order,
    "B.weights": det_B_weights,
    "B.empty": det_B_empty,
    "B.presence": det_B_presence,
    "B.level": det_B_level,
}
LAW_OF = {k: k.split(".")[0] for k in DETECTORS}
LAW_OF["L6.prompts"] = "L6"

PROMPT_MUTANT = {"ca": {"commit": "Quin nivell vols donar? Tens altres cercles que t'ocupin?",
                        "veto": "Per què vols dir «no»? Justifica-ho."},
                 "es": R.PROMPTS["es"], "en": R.PROMPTS["en"]}

# (id, llei, mutació, detector previst). La mutació és una Policy o, per a L6, un diccionari de preguntes.
MUTANTS = [
    ("L1-margin-between-circles", P(publish_margin=True), "L1.noninterference"),
    ("L1-ai-shared-context", P(ai_shared_context=True), "L1.ai_isolation"),
    ("L2-one-key-per-person", P(key_scope="person"), "L2.unlinkable"),
    ("L2-stable-seat", P(seat_order="by_person"), "L2.seat_independence"),
    ("L2-stable-rate-tag", P(rate_tag_hex=2), "L6.schema"),
    ("L3-no-budget-check", P(budget_check=False), "L3.budget"),
    ("L3-global-attest", P(budget_check=False, publish_attest=True), "L3.no_predicate"),
    ("L4-silence-inherits-consent", P(silence="inherit"), "L4.silence"),
    ("L4-pause-is-visible", P(pause_marker=True), "L4.pause"),
    ("L5-veto-author-published", P(veto_author=True), "L5.author"),
    ("L5-one-step-per-veto", P(veto_steps="per_veto"), "L5.step"),
    ("L5-effect-in-same-epoch", P(veto_scope="same_epoch"), "L5.step"),
    ("L6-field-about-other-circles", P(extra_fields=("other_circles",)), "L6.schema"),
    ("L6-prompt-asks-about-others", PROMPT_MUTANT, "L6.prompts"),
    ("L7-event-timestamp", P(ts_field=True), "L7.time"),
    ("L7-shared-counter", P(seq_field=True), "L7.counter"),
    ("L7-history", P(history=True), "L7.state"),
    ("L7-arrival-order", P(commit_order="arrival"), "L7.order"),
    ("B-weights-ignore-the-active-pair", P(bary_weights="equal"), "B.weights"),
    ("B-empty-is-origin", P(bary_empty="origin"), "B.empty"),
    ("B-silence-counts-as-presence", P(bary_presence="seated"), "B.presence"),
    ("B-level-moves-the-barycentre", P(bary_uses_level=True), "B.level"),
]


def run_detector(name, mutation) -> Finding:
    return det_L6_prompts(mutation) if name == "L6.prompts" else DETECTORS[name](mutation)


# ==========================================================================
# §A  Geometria
# ==========================================================================
def test_A_orbit_stabilizer_48_over_12_is_4():
    group = R.oh_group()
    assert len(group) == 48 and len(set(group)) == 48
    ident = set(group)
    assert all(R.mat_mul(a, b) in ident for a in group for b in group[:8])      # tancat (mostra)
    assert {frozenset(R.mat_vec(g, v) for v in R.cube_vertices()) for g in group} == {frozenset(R.cube_vertices())}
    for j in range(4):                                                         # qualsevol diagonal: mateixa història
        orbit, stab = R.orbit_and_stabilizer(R.diagonal(j))
        assert len(orbit) == 4 and len(stab) == 12 and len(group) // len(stab) == len(orbit) == 4
        orders = {}
        for g in stab:
            orders[R.mat_order(g)] = orders.get(R.mat_order(g), 0) + 1
        assert orders == {1: 1, 2: 7, 3: 2, 6: 2}                              # el grup puntual D3d
    REPORT["geometry"] = {"group": 48, "orbit": 4, "stabilizer": 12, "orders": orders}


def test_A_diagonals_join_dual_tetrahedra_and_split_3_plus_3():
    vs = R.cube_vertices()
    prod = lambda v: v[0] * v[1] * v[2]                                         # noqa: E731
    assert {prod(v) for v in R.TETRA_A} == {1} and {prod(v) for v in R.TETRA_B} == {-1}
    assert set(R.TETRA_A) | set(R.TETRA_B) == set(vs) and len(set(R.TETRA_A) & set(R.TETRA_B)) == 0
    for j in range(4):
        a, b = sorted(R.diagonal(j), key=prod)
        assert prod(a) == -1 and prod(b) == 1 and tuple(-x for x in a) == b      # un vèrtex de cada tetraedre
    for active in (1, 2, 3, 4):
        r = R.roles(active)
        assert sorted(v["role"] for v in r.values()) == ["axial"] * 2 + ["orbital"] * 6
        orbital = sorted(round(v["height"], 6) for v in r.values() if v["role"] == "orbital")
        assert orbital == [round(-1 / math.sqrt(3), 6)] * 3 + [round(1 / math.sqrt(3), 6)] * 3   # 3 + 3
        axial = sorted(round(v["height"], 6) for v in r.values() if v["role"] == "axial")
        assert axial == [round(-math.sqrt(3), 6), round(math.sqrt(3), 6)]


def test_A_each_seat_is_axial_exactly_once_per_four_phase_cycle():
    for seat in itertools.product(range(4), ("ia", "hu")):
        assert sum(R.roles(a)[seat]["role"] == "axial" for a in (1, 2, 3, 4)) == 1


# ==========================================================================
# §B  HKDF per (persona, Diamant)
# ==========================================================================
def test_B_hkdf_rfc5869_official_vectors():
    ikm = bytes.fromhex("0b" * 22)
    okm = R.hkdf_sha256(ikm, bytes.fromhex("000102030405060708090a0b0c"), bytes.fromhex("f0f1f2f3f4f5f6f7f8f9"), 42)
    assert okm.hex() == ("3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865")
    assert R.hkdf_sha256(ikm, b"", b"", 42).hex() == (            # A.3: sense sal ni info
        "8da4e775a563c18f715f802a063c5a31b8a11f5c5ee1879ec3454e5f3c738d2d9d201395faa4b61a96c8")


def test_B_hkdf_matches_library_on_random_inputs():
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    rng = random.Random(8)
    for _ in range(50):
        ikm, salt, info = rng.randbytes(rng.randrange(1, 64)), rng.randbytes(rng.randrange(0, 40)), rng.randbytes(rng.randrange(0, 40))
        n = rng.randrange(1, 200)
        assert R.hkdf_sha256(ikm, salt, info, n) == HKDF(hashes.SHA256(), n, salt or None, info).derive(ikm)


def test_B_ed25519_backend_matches_rfc8032_vector():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    sk = Ed25519PrivateKey.from_private_bytes(bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"))
    assert R.pub_hex(sk) == "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
    assert sk.sign(b"").hex().startswith("e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bac")


def test_B_hkdf_per_person_and_diamond_is_domain_separated_and_uniform():
    rng = random.Random(21)
    roots = [rng.randbytes(32) for _ in range(300)]
    d_ids = [A.sha_hex("b", k) for k in range(3)]
    seeds = {(i, d): R.derive_seat_seed(r, d) for i, r in enumerate(roots) for d in d_ids}
    assert len(set(seeds.values())) == len(seeds)                              # cap col·lisió
    assert all(R.derive_seat_seed(roots[0], d) == seeds[(0, d)] for d in d_ids)  # determinista: re-derivable al dispositiu
    assert R.derive_seat_seed(roots[0], d_ids[0]) != R.hkdf_sha256(roots[0], R.SALT, b"rate-tag|" + d_ids[0].encode(), 32)
    ones = sum(bin(int.from_bytes(s, "big")).count("1") for s in seeds.values())
    n_bits = 256 * len(seeds)
    assert abs(ones - n_bits / 2) <= 4.5 * math.sqrt(n_bits / 4)               # bits uniformes
    flips = []                                                                 # allau: un bit de context canvia ~la meitat de la sortida
    for r in roots[:100]:
        a = R.derive_seat_seed(r, d_ids[0])
        b = R.derive_seat_seed(r, d_ids[0][:-1] + ("0" if d_ids[0][-1] != "0" else "1"))
        flips.append(bin(int.from_bytes(a, "big") ^ int.from_bytes(b, "big")).count("1"))
    assert abs(sum(flips) / len(flips) - 128) <= 4.5 * 8 / math.sqrt(len(flips))
    pubs = {R.Device(r, 1, 0).pseud(d) for r in roots[:50] for d in d_ids}
    assert len(pubs) == 150
    REPORT["hkdf"] = {"derived_keys": len(seeds), "collisions": 0, "avalanche_mean_bits": sum(flips) / len(flips)}


# ==========================================================================
# §C  Població: N persones en <= 3 Diamants
# ==========================================================================
def test_C_population_respects_the_cap_and_the_seats():
    w = A.make_world(1, N_PERSONS, TICKS, A.NULL)
    ks = [len(p.diamonds) for p in w.persons]
    assert len(w.persons) == N_PERSONS and 1 <= min(ks) and max(ks) <= 3 and set(ks) == {1, 2, 3}
    assert all(len(set(p.diamonds)) == len(p.diamonds) for p in w.persons)       # mai dos seients al mateix Diamant
    assert all(len(m) <= 4 and len(set(m)) == len(m) for m in w.members)
    assert sum(ks) == sum(len(m) for m in w.members)
    sim = A.simulate(w, A.NULL)
    m = sim.feed[-1][2]
    assert not R.validate_manifest(m) and len(m["parelles"]) == 4
    ai = {x for dia in sim.diamonds for x in dia.seated("ia")}
    hu = {x for dia in sim.diamonds for x in dia.seated("hu")}
    assert len(hu) == sum(ks) and len(ai) == 4 * len(w.d_ids) and not (ai & hu)  # pseudònims tots diferents
    REPORT["population"] = {"persons": N_PERSONS, "diamonds": len(w.d_ids), "memberships": sum(ks),
                            "bridges": sum(k >= 2 for k in ks), "independent": sum(k == 1 for k in ks), "ticks": TICKS}


# ==========================================================================
# §D  Lleis L1..L7: referència i mutants
# ==========================================================================
@pytest.mark.parametrize("name", sorted(DETECTORS) + ["L6.prompts"])
def test_D_reference_satisfies_every_law(name):
    f = run_detector(name, R.PROMPTS if name == "L6.prompts" else R.REFERENCE)
    assert f.ok, f"{LAW_OF[name]} · {name}: {f.detail}"


@pytest.mark.parametrize("mid,mutation,detector", MUTANTS, ids=[m[0] for m in MUTANTS])
def test_D_mutants_are_caught(mid, mutation, detector):
    f = run_detector(detector, mutation)
    assert not f.ok, f"el mutant {mid} NO ha estat detectat per {detector}"
    REPORT.setdefault("mutants", {})[mid] = {"detector": detector, "detail": f.detail}


def test_D_every_law_and_the_barycentre_have_at_least_one_mutant_and_one_detector():
    laws = {f"L{i}" for i in range(1, 8)} | {"B"}
    assert laws <= {LAW_OF[d] for _, _, d in MUTANTS} and laws <= set(LAW_OF.values())
    assert {d for _, _, d in MUTANTS if d.startswith("B.")} == {d for d in DETECTORS if d.startswith("B.")}   # un mutant per detector B


def test_D_L1_budget_channel_is_exactly_the_refusal_bit():
    """El que sí que depèn dels altres cercles: refusar per pressupost. És UN bit, i és silenci (indistingible per L4)."""
    def d0(other_c):
        devs, dias = mini_world(R.REFERENCE, n_diamonds=2, budgets=[10, 10_000, 10_000, 10_000])
        for dev in devs:
            dev.new_period()
        dias[1].accept(devs[0].commit(dias[1].d_id, 0, other_c))
        for dev in devs:
            dias[0].accept(dev.commit(dias[0].d_id, 0, 5))
        return dias[0].manifest()
    easy, tight = d0(2), d0(9)                                                  # 2+5 <= 10 ; 9+5 > 10
    assert len(easy["commits"]) == 4 and len(tight["commits"]) == 3
    assert {c["pseud"] for c in tight["commits"]} < {c["pseud"] for c in easy["commits"]}
    assert [c for c in easy["commits"] if c in tight["commits"]] == tight["commits"]   # la resta, idèntica
    assert {k: v for k, v in easy.items() if k != "commits"} == {k: v for k, v in tight.items() if k != "commits"}


# ==========================================================================
# §E  Adversari sintètic
# ==========================================================================
STRUCT_PAIR = ("tok_gram", "tok_aligned", "collide", "path", "sib_corr")        # el que només pot venir del protocol
STRUCT_CLS = ("pseud_pop", "sig_pop", "slot")
BEH_PAIR = ("presence_corr", "c_corr", "level_sim", "step_corr")                # el que ja és al comportament
BEH_CLS = ("mean_c", "var_c", "presence_rate", "n_present", "first_seen")


def adversary(behavior, policy=R.REFERENCE, seed=11, n=None, ticks=None):
    w = A.make_world(seed, n or N_PERSONS, ticks or TICKS, behavior)
    sim = A.simulate(w, behavior, policy)
    pub = A.run_adversary(sim.feed, sim.truth, seed=seed, n_perm=N_PERM)
    return sim, pub


@pytest.fixture(scope="module")
def null_runs():
    return [adversary(A.NULL, seed=11 + k) for k in range(SEEDS)]


@pytest.fixture(scope="module")
def coupled_run():
    sim, pub = adversary(A.COUPLED, seed=21)
    beh = A.run_adversary(sim.beh_feed, sim.beh_truth, seed=21, n_perm=N_PERM)
    return sim, pub, beh


def test_E_null_model_reference_adds_nothing(null_runs):
    """Comportament independent entre cercles: tot estadístic significatiu seria culpa del protocol."""
    worst = []
    for sim, rep in null_runs:
        name, z = rep.zmax()
        worst.append((name, round(z, 2)))
        assert abs(z) < Z_THR, f"{name} z={z:.2f}\n" + "\n".join(rep.lines())
    REPORT["null_model"] = {"seeds": SEEDS, "max_abs_z": [w[1] for w in worst], "stat": [w[0] for w in worst],
                            "meta": null_runs[0][1].meta}
    print("\n[nul] max|z| per llavor:", worst, null_runs[0][1].meta)


def test_E_null_model_exact_token_scan_finds_no_stable_identifier(null_runs):
    sim, _ = null_runs[0]
    seen: dict = {}
    for _, stream, m in sim.feed:
        for path, v in leaves(m):
            if isinstance(v, str) and len(v) >= 16 and path[0] != "d_id":
                seen.setdefault(v, set()).add(stream)
    assert not [v for v, s in seen.items() if len(s) > 1]
    roots = [p.root.hex() for p in sim.world.persons]
    blob = b"".join(sim.raw).decode()
    assert not any(r in blob for r in roots)


def test_E_coupled_model_protocol_artifacts_stay_at_chance(coupled_run):
    sim, pub, beh = coupled_run
    for name in STRUCT_PAIR:
        assert abs(pub.pair[name].z) < Z_THR, (name, pub.pair[name])
    for name in STRUCT_CLS:
        assert abs(pub.cls[name].z) < Z_THR, (name, pub.cls[name])


def test_E_data_processing_inequality_published_view_knows_no_more_than_behaviour(coupled_run):
    """Les estadístiques derivables del comportament han de donar el mateix (o menys) amb els manifests que amb les accions."""
    sim, pub, beh = coupled_run
    rows = {}
    for kind, names in (("pair", BEH_PAIR), ("cls", BEH_CLS)):
        for name in names:
            a, b = getattr(pub, kind)[name], getattr(beh, kind)[name]
            excess = abs(a.auc - 0.5) - abs(b.auc - 0.5)
            rows[f"{kind}:{name}"] = {"published_auc": round(a.auc, 4), "behaviour_auc": round(b.auc, 4),
                                      "published_z": round(a.z, 2), "excess": round(excess, 6)}
            assert excess <= 1e-9, (name, a, b)
    REPORT["coupled_model"] = {"rows": rows, "meta": pub.meta}
    print("\n[acoblat] canals del comportament (la vista publicada en sap exactament el mateix):")
    for k, v in rows.items():
        print(f"   {k:<22} AUC publicat {v['published_auc']:.3f} | comportament {v['behaviour_auc']:.3f} | z={v['published_z']:+6.2f}")


STAT_MUTANTS = [m for m in MUTANTS if m[0] in {"L2-one-key-per-person", "L2-stable-seat", "L2-stable-rate-tag",
                                               "L1-margin-between-circles", "L4-silence-inherits-consent"}]


@pytest.mark.parametrize("mid,mutation,detector", STAT_MUTANTS, ids=[m[0] for m in STAT_MUTANTS])
def test_E_adversary_has_power_against_structural_mutants(mid, mutation, detector):
    """En el model nul qualsevol estadístic significatiu és una fuita del protocol: l'adversari ha de veure el mutant."""
    sim, rep = adversary(A.NULL, mutation, seed=31)
    name, z = rep.zmax()
    REPORT.setdefault("adversary_power", {})[mid] = {"stat": name, "z": round(z, 1)}
    assert abs(z) >= Z_THR, f"l'adversari no veu {mid}: millor estadístic {name} z={z:.2f}"


QLEVELS = (16, 4, 2, 1)


@pytest.fixture(scope="module")
def quantization_runs():
    out = {}
    for lv in QLEVELS:
        sim, pub = adversary(A.COUPLED, P(c_levels=lv), seed=41)
        beh = A.run_adversary(sim.beh_feed, sim.beh_truth, seed=41, n_perm=N_PERM)
        out[lv] = (pub, beh)
    return out


def test_E_only_presence_without_levels_closes_the_level_channel_and_the_pause_channel_remains(quantization_runs):
    """Esmena ADOPTADA (v1.1): només presència (1 nivell). Es mesura contra 16, 4 i 2 nivells, amb la desigualtat de
    processament de dades a cada pas: els nivells publicats serien un canal d'enllaç; amb 1 nivell no n'hi ha cap."""
    rows = {}
    for lv, (pub, beh) in quantization_runs.items():
        sep = lambda r: round(0.5 + abs(r.auc - 0.5), 3)                       # noqa: E731  (AUC orientada)
        rows[lv] = {"bridge_from_mean_level": sep(pub.cls["mean_c"]), "pair_level_sim": sep(pub.pair["level_sim"]),
                    "pair_presence_corr": sep(pub.pair["presence_corr"]), "pair_c_corr": sep(pub.pair["c_corr"])}
        for kind, names in (("pair", BEH_PAIR), ("cls", BEH_CLS)):
            for name in names:
                assert abs(getattr(pub, kind)[name].auc - 0.5) <= abs(getattr(beh, kind)[name].auc - 0.5) + 1e-9
    REPORT["quantization"] = rows
    print("\n[quantització de c] nivells publicats -> AUC de l'adversari (0,5 = a cegues):")
    for lv, r in rows.items():
        print(f"   {lv:>2} nivells: pont/independent per nivell mitjà {r['bridge_from_mean_level']:.3f} | "
              f"enllaç per semblança de nivell {r['pair_level_sim']:.3f} | per pauses compartides {r['pair_presence_corr']:.3f}")
    assert rows[1]["pair_level_sim"] <= 0.5 + 0.06 and rows[1]["bridge_from_mean_level"] <= 0.5 + 0.1   # només presència
    assert rows[1]["pair_presence_corr"] >= rows[16]["pair_presence_corr"] - 0.02                         # les pauses segueixen
    assert rows[1]["bridge_from_mean_level"] <= rows[16]["bridge_from_mean_level"] + 1e-9


def test_E_observation_window_how_fast_does_behaviour_link_circles(coupled_run):
    """Informatiu: com creix el poder de l'adversari amb el nombre d'èpoques observades (justifica l'epoca gruixuda)."""
    sim, pub, beh = coupled_run
    rows = {}
    for T in (12, 18, 24, TICKS):
        feed = [e for e in sim.feed if e[0] < T]
        rep = A.run_adversary(feed, sim.truth, seed=21, n_perm=N_PERM, min_overlap=6)
        rows[T] = round(0.5 + abs(rep.pair["presence_corr"].auc - 0.5), 3)
    REPORT["observation_window"] = rows
    print("\n[finestra d'observació] AUC d'enllaç per pauses compartides segons les èpoques vistes:", rows)
    assert rows[TICKS] >= rows[12] - 0.05                                      # més temps no n'amaga res


# ==========================================================================
# §F  Les set lleis, sobre la població simulada (N persones, <= 3 Diamants cadascuna)
# ==========================================================================
def _bridge_count(w, d):
    return sum(len(w.persons[p].diamonds) >= 2 for p in w.members[d])


def _stream(sim, d):
    return [b for (t, dd, _), b in zip(sim.feed, sim.raw) if dd == d]


@pytest.mark.parametrize("levels", [16, 1], ids=["16-nivells", "nomes-presencia"])
def test_F_L1_twin_worlds_what_happens_in_other_circles_does_not_move_this_one(levels):
    """Mons bessons: es canvia el nivell en tots els Diamants menys un; el publicat d'aquell no ha de canviar.

    Amb 16 nivells el món bessó es veu diferent als altres cercles (el nivell s'hi publica); amb només presència
    (la referència v1.1) el nivell no surt enlloc: els altres cercles tampoc no canvien. El control positiu
    (`publish_margin`) demostra que el mètode veuria una fuita entre cercles en tots dos casos.
    """
    w = A.make_world(5, N_PERSONS, TICKS, A.NULL)
    star = max(range(len(w.members)), key=lambda d: (_bridge_count(w, d), -d))
    assert _bridge_count(w, star) >= 3                                          # el Diamant triat té ponts de debò
    twist = lambda p, d, t, c: c if d == star else (c * 7 + 3) % 16            # noqa: E731
    ref = P(c_levels=levels)
    base, twin = A.simulate(w, A.NULL, ref), A.simulate(w, A.NULL, ref, level_override=twist)
    assert _stream(base, star) == _stream(twin, star) and len(_stream(base, star)) == TICKS - w.birth[star]
    others = lambda sim: [b for (t, d, _), b in zip(sim.feed, sim.raw) if d != star]   # noqa: E731
    if levels > 1:
        assert others(base) != others(twin)                                     # el món bessó sí que és diferent
    else:
        assert others(base) == others(twin)                                     # amb només presència, el nivell no es veu enlloc
    mut = P(publish_margin=True, c_levels=levels)                               # control positiu
    assert _stream(A.simulate(w, A.NULL, mut), star) != _stream(A.simulate(w, A.NULL, mut, level_override=twist), star)


def test_F_L3_budget_law_holds_on_every_device_and_it_actually_bites(coupled_run):
    sim = coupled_run[0]
    assert sim.max_overshoot <= 0                                               # cap dispositiu ha signat mai L > B
    assert sim.refusals >= 20                                                   # i la llei ha refusat de debò
    assert all(not R.validate_manifest(m) for _, _, m in sim.feed)              # ni B, ni s, ni Σ als manifests
    REPORT["population_L3"] = {"refusals": sim.refusals, "max_L_minus_B": sim.max_overshoot}


def test_F_L4_nothing_inherits_across_epochs_and_a_pause_looks_like_any_absence(coupled_run):
    sim = coupled_run[0]
    for t, d, m in sim.feed:
        assert {c["pseud"] for c in m["commits"]} == sim.signed.get((t, d), set())   # només el que s'ha signat aquesta època
    n_pause = 0
    for t, d, m in sim.feed:
        for c in m["commits"]:
            assert t not in sim.paused_log.get(sim.truth.person_of[c["pseud"]], ())   # en pausa: res a cap Diamant
    for pid, ticks in sim.paused_log.items():
        n_pause += len(ticks)
    assert n_pause >= 50                                                         # hi ha hagut pauses de debò
    assert all(set(c) == set(R.COMMIT_FIELDS) for _, _, m in sim.feed for c in m["commits"])   # cap marca de pausa


def test_F_L5_diag_active_moves_one_step_after_a_no_and_never_otherwise(coupled_run):
    sim = coupled_run[0]
    series: dict = {}
    for t, d, m in sim.feed:
        series.setdefault(d, {})[t] = m["diag_active"]
    steps = 0
    for d, ser in series.items():
        ts = sorted(ser)
        assert ser[ts[0]] == 1
        for a, b in zip(ts, ts[1:]):
            expect = ser[a] % 4 + 1 if sim.veto_log.get((a, d)) else ser[a]
            assert ser[b] == expect                                              # 1→2→3→4→1, un sol pas, època següent
            steps += ser[b] != ser[a]
    assert steps >= 20 and any(n >= 2 for n in sim.veto_log.values())           # i hi ha «no» simultanis que compten com un
    REPORT["population_L5"] = {"steps": steps, "epochs_with_several_vetoes": sum(n >= 2 for n in sim.veto_log.values())}


def test_F_L6_every_published_manifest_obeys_the_closed_schema(null_runs, coupled_run):
    for sim in [r[0] for r in null_runs] + [coupled_run[0]]:
        assert all(not R.validate_manifest(m) for _, _, m in sim.feed)


def test_F_L7_coarse_epochs_current_state_only_no_shared_counter(null_runs):
    sim = null_runs[0][0]
    assert max(len(b) for b in sim.raw) <= 2048
    assert max(len(R.manifest_lines(m)) for _, _, m in sim.feed) <= R.MAX_MANIFEST_LINES
    assert all(isinstance(v, bool) or not isinstance(v, int) or v < 2 ** 20 for _, _, m in sim.feed for _, v in leaves(m))
    assert all(m["epoch"] == t - sim.world.birth[d] for t, d, m in sim.feed)     # època LOCAL: tic - naixement
    per_tick: dict = {}
    for t, d, m in sim.feed:
        per_tick.setdefault(t, set()).add(m["epoch"])
    assert sum(len(v) > 1 for v in per_tick.values()) >= TICKS // 2              # els Diamants no comparteixen número d'època
    for key in ("epoch", "diag_active"):                                         # cap camp numèric és una sèrie global única
        vals = [m[key] for _, _, m in sim.feed]
        assert len(set(vals)) < len(vals) / 4


# ==========================================================================
# §G  Baricentre: f(presència, diag_active)   (adoptat el 4-11-2026)
# ==========================================================================
# Pes 2 per a cada seient de la parella de la diagonal activa i 1 per a cada seient orbital; només compten els seients
# PRESENTS (humà: ha signat aquesta època; IA: seient ocupat); sense cap present el valor és None (mai l'origen).
G_DIAG = (1, 2, 3, 4)
ALL_SUBSETS = list(subsets(ALL_SEATS))                                           # 256, el buit inclòs
F = Fraction
IA4, HU4 = frozenset((j, "ia") for j in range(4)), frozenset((j, "hu") for j in range(4))
VERTICES = {(0, "ia"): (1, 1, 1), (0, "hu"): (-1, -1, -1), (1, "ia"): (1, -1, -1), (1, "hu"): (-1, 1, 1),     # a mà, de l'especificació
            (2, "ia"): (-1, 1, -1), (2, "hu"): (1, -1, 1), (3, "ia"): (-1, -1, 1), (3, "hu"): (1, 1, -1)}
GOLDEN = [                                                                        # (presents, diag_active, baricentre), calculats a mà
    (frozenset([(0, "ia"), (1, "ia")]), 1, (1, F(1, 3), F(1, 3))),                # (2*(1,1,1) + (1,-1,-1)) / 3
    (frozenset([(0, "ia"), (1, "ia")]), 2, (1, F(-1, 3), F(-1, 3))),              # ((1,1,1) + 2*(1,-1,-1)) / 3
    (frozenset([(0, "ia"), (1, "ia")]), 3, (1, 0, 0)),                            # cap dels dos és axial: pesos 1 i 1
    (frozenset([(0, "ia"), (1, "ia")]), 4, (1, 0, 0)),
    (frozenset([(0, "ia"), (0, "hu"), (1, "ia")]), 1, (F(1, 5), F(-1, 5), F(-1, 5))),   # parella activa completa + un orbital: ±1/5
    (frozenset([(0, "ia"), (0, "hu"), (1, "ia")]), 2, (F(1, 2), F(-1, 2), F(-1, 2))),   # els mateixos tres seients, una altra diagonal activa
    (IA4, 1, (F(1, 5),) * 3),                                                     # (2*(1,1,1) + (1,-1,-1) + (-1,1,-1) + (-1,-1,1)) / 5
    (IA4, 2, (F(1, 5), F(-1, 5), F(-1, 5))),
    (HU4, 1, (F(-1, 5),) * 3),                                                    # amb pes uniforme seria l'origen
    (frozenset([(2, "hu"), (3, "ia")]), 3, (F(1, 3), -1, 1)),                     # (2*(1,-1,1) + (-1,-1,1)) / 3
]


def _balanced(s) -> bool:
    return all(((j, "ia") in s) == ((j, "hu") in s) for j in range(4))            # cada parella antipodal, completa o buida


def test_G_oracle_and_reference_agree_with_hand_computed_values():
    assert {s: oracle_vertex(s) for s in ALL_SEATS} == VERTICES
    for a in G_DIAG:
        assert R.barycentre(ALL_SEATS, a) == (0, 0, 0) == oracle_bary(ALL_SEATS, a)             # els vuit: l'origen
        assert R.barycentre((), a) is None and oracle_bary((), a) is None                       # cap: None
        for s in ALL_SEATS:
            assert R.barycentre([s], a) == VERTICES[s] == oracle_bary([s], a)                   # un de sol: el seu vèrtex
    for present, a, want in GOLDEN:
        assert R.barycentre(present, a) == want, (sorted(present), a)
        assert oracle_bary(present, a) == want, (sorted(present), a)


@pytest.mark.parametrize("a", G_DIAG)
def test_G_every_subset_of_the_eight_seats_matches_the_independent_oracle(a):
    for s in ALL_SUBSETS:
        got = R.barycentre(s, a)
        assert got == oracle_bary(s, a), (sorted(s), a)
        if s:
            assert len(got) == 3 and all(isinstance(x, Fraction) for x in got)                  # exacte: cap flotant
            assert all(abs(x) <= 1 for x in got)                                                # dins del cub
        else:
            assert got is None


@pytest.mark.parametrize("a", G_DIAG)
def test_G_origin_exactly_when_every_antipodal_pair_is_complete_or_empty(a):
    at_origin = {s for s in ALL_SUBSETS if s and R.barycentre(s, a) == (0, 0, 0)}
    assert at_origin == {s for s in ALL_SUBSETS if s and _balanced(s)}
    assert len(at_origin) == 2 ** 4 - 1                                          # 15: les unions no buides de parelles completes
    assert frozenset(ALL_SEATS) in at_origin                                     # els vuit presents: l'origen, sigui quina sigui diag_active
    REPORT.setdefault("barycentre", {})["origin_subsets_per_diag"] = len(at_origin)


@pytest.mark.parametrize("a", G_DIAG)
def test_G_no_present_seat_is_null_never_the_origin(a):
    """Pes total 0 <=> cap seient present (tots els pesos són > 0): el valor és None i no es confon amb l'origen."""
    assert all(R.seat_weight(j, a) > 0 for j in range(4))
    assert [s for s in ALL_SUBSETS if R.barycentre(s, a) is None] == [frozenset()]
    assert R.barycentre(frozenset(), a) is None and R.barycentre(frozenset(ALL_SEATS), a) == (0, 0, 0)
    assert R.barycentre(frozenset(), a) != R.barycentre(frozenset(ALL_SEATS), a)               # silenci total != els vuit presents


def test_G_invalid_inputs_fail_closed_instead_of_inventing_an_origin():
    for present, a in (({(4, "ia")}, 1), ({(0, "xx")}, 1), (set(), 0), (set(), 5), ({(0, "ia")}, 9)):
        with pytest.raises(ValueError):
            R.barycentre(present, a)


def test_G_the_active_pair_matters_only_because_its_seats_weigh_double():
    """Amb pes uniforme la diagonal activa no mouria res (i 17 subconjunts serien «l'equilibri»); amb pes 2/1 sí."""
    def uniform(s):
        return None if not s else tuple(F(sum(oracle_vertex(x)[ax] for x in s), len(s)) for ax in range(3))
    independent = {s for s in ALL_SUBSETS if len({R.barycentre(s, a) for a in G_DIAG}) == 1}
    assert independent == {s for s in ALL_SUBSETS if len(s) <= 1 or _balanced(s)}              # buit, un de sol, o unió de parelles
    assert len(independent) == 1 + 8 + 15 and len(ALL_SUBSETS) - len(independent) == 232
    assert uniform(IA4) == uniform(HU4) == (0, 0, 0)                             # amb pes uniforme, les quatre IA soles serien l'equilibri
    assert all(R.barycentre(x, a) not in (None, (0, 0, 0)) for x in (IA4, HU4) for a in G_DIAG)
    assert sum(1 for s in ALL_SUBSETS if s and uniform(s) == (0, 0, 0)) == 17
    REPORT.setdefault("barycentre", {}).update({"subsets": len(ALL_SUBSETS), "depend_on_diag_active": 232,
                                                "origin_with_uniform_weights": 17})


def test_G_the_reference_publishes_presence_and_never_a_level_or_a_barycentre(null_runs):
    assert R.REFERENCE.c_levels == 1
    for m in scenario(R.REFERENCE, epochs=3):
        assert set(m) == set(R.TOP_FIELDS) and m["commits"] and all(c["c"] == 0 for c in m["commits"])
    sim = null_runs[0][0]
    assert {c["c"] for _, _, m in sim.feed for c in m["commits"]} == {0}


def test_G_barycentre_derived_from_the_public_manifest_matches_what_the_devices_did(coupled_run):
    """Sobre la població: qui ha signat, segons la veritat del simulador, i el que en deriva qualsevol del manifest."""
    sim = coupled_run[0]
    values, origin, null, quiet = set(), 0, 0, 0
    for t, d, m in sim.feed:
        signed = sim.signed.get((t, d), set())
        present = {(j, "ia") for j, (ia, _) in enumerate(m["parelles"]) if ia is not None}
        present |= {(j, "hu") for j, (_, hu) in enumerate(m["parelles"]) if hu in signed}
        want, got = oracle_bary(present, m["diag_active"]), R.barycentre_from_manifest(m)
        assert got == want, (t, d)
        values.add(got)
        origin += got == (0, 0, 0)
        null += got is None
        quiet += not signed
    assert len(sim.feed) >= 10 * TICKS and null == 0                             # les quatre IA seuen sempre: el silenci humà total no és None
    REPORT.setdefault("barycentre", {}).update({"population_manifests": len(sim.feed), "at_origin": origin, "null": null,
                                                "epochs_without_any_human_commit": quiet, "distinct_values": len(values)})


def test_zz_write_report():
    path = os.environ.get("HU_REPORT")
    if path:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(REPORT, fh, ensure_ascii=False, indent=1, default=str)
