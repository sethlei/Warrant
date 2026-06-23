#!/usr/bin/env python3
"""Independent exhaustive oracle for the (s_pass, s_death) compose algebra.

This script does NOT trust warrant.py's compose functions. It re-derives
the spec's AND/OR + duality rules from scratch (METHODOLOGY.md sections 3-8) as an
INDEPENDENT oracle, then exhaustively enumerates every combination of 1, 2, and 3
children for both AND and OR nodes and checks the code's output against the oracle.

Finite domain per child:
  verdict in {PASS, DEATH, PENDING}
  if PASS  -> carries a pass_strength in {H, L}   (death_strength irrelevant)
  if DEATH -> carries a death_strength in {H, L}  (pass_strength irrelevant)
  if PENDING -> carries neither

We import the module under test by path via importlib (stdlib only).
"""
import itertools
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_PATH = os.path.join(HERE, "warrant.py")
spec = importlib.util.spec_from_file_location("warrant", MOD_PATH)
vd = importlib.util.module_from_spec(spec)
sys.modules["warrant"] = vd   # needed so dataclass type hints resolve
spec.loader.exec_module(vd)

H, L = "H", "L"
PASS, DEATH, PENDING = "PASS", "DEATH", "PENDING"
RANK = {L: 0, H: 1}


def omin(a, b):
    return a if RANK[a] <= RANK[b] else b


def omax(a, b):
    return a if RANK[a] >= RANK[b] else b


# --------------------------------------------------------------------------- #
# INDEPENDENT ORACLE — re-derived from METHODOLOGY.md sections 3, 5
# --------------------------------------------------------------------------- #
# A "child state" is (verdict, pass_strength_or_None, death_strength_or_None).

def oracle_and(children):
    """Spec section 3 AND-node:
       - if ANY child DIED: AND = DEATH; death-strength = max over DIED of s_death.
       - elif ALL children PASS: AND = PASS; pass-strength = min over s_pass.
       - else: PENDING.
    """
    died = [c for c in children if c[0] == DEATH]
    if died:
        ds = died[0][2]
        for c in died[1:]:
            ds = omax(ds, c[2])
        return (DEATH, None, ds)
    if all(c[0] == PASS for c in children):
        ps = children[0][1]
        for c in children[1:]:
            ps = omin(ps, c[1])
        return (PASS, ps, None)
    return (PENDING, None, None)


def oracle_or(children):
    """Spec section 3 OR-node (exact De Morgan dual of AND):
       - if ANY child PASSES: OR = PASS; pass-strength = max over PASSED of s_pass.
       - elif ALL children DIED: OR = DEATH; death-strength = min over s_death
         (all alternatives must die; the weakest death caps it).
       - else: PENDING.
    """
    passed = [c for c in children if c[0] == PASS]
    if passed:
        ps = passed[0][1]
        for c in passed[1:]:
            ps = omax(ps, c[1])
        return (PASS, ps, None)
    if all(c[0] == DEATH for c in children):
        ds = children[0][2]
        for c in children[1:]:
            ds = omin(ds, c[2])
        return (DEATH, None, ds)
    return (PENDING, None, None)


# --------------------------------------------------------------------------- #
# Materialize a child state into a vd.NodeResult (what the code's composer eats)
# --------------------------------------------------------------------------- #

def make_child_result(idx, state):
    verdict, ps, ds = state
    r = vd.NodeResult(id=f"c{idx}", kind=vd.LEAF, verdict=verdict)
    r.pass_strength = ps
    r.death_strength = ds
    return r


def enumerate_child_states():
    """All distinct child states over the finite domain."""
    out = []
    out.append((PASS, H, None))
    out.append((PASS, L, None))
    out.append((DEATH, None, H))
    out.append((DEATH, None, L))
    out.append((PENDING, None, None))
    return out


def code_and(child_states):
    kids = [make_child_result(i, s) for i, s in enumerate(child_states)]
    node = vd.Node("n", "", kind=vd.AND, rests_on=[k.id for k in kids])
    r = vd.Graph._compose_and(node, kids)
    return (r.verdict, r.pass_strength, r.death_strength)


def code_or(child_states):
    kids = [make_child_result(i, s) for i, s in enumerate(child_states)]
    # OR warns on a missing closure leaf but that does not affect verdict/strength;
    # we test verdict + strengths here (closure is a separate leaf check).
    node = vd.Node("n", "", kind=vd.OR, rests_on=[k.id for k in kids])
    r = vd.Graph._compose_or(node, kids)
    return (r.verdict, r.pass_strength, r.death_strength)


def run():
    states = enumerate_child_states()
    total = 0
    fails = []
    for n_children in (1, 2, 3):
        for combo in itertools.product(states, repeat=n_children):
            combo = list(combo)
            # AND
            oc = oracle_and(combo)
            cc = code_and(combo)
            total += 1
            if oc != cc:
                fails.append(("AND", combo, oc, cc))
            # OR
            oc = oracle_or(combo)
            cc = code_or(combo)
            total += 1
            if oc != cc:
                fails.append(("OR", combo, oc, cc))
    print(f"Exhaustive enumeration: child-states={len(states)}, "
          f"children counts={{1,2,3}}")
    print(f"Total compose cases checked (AND+OR): {total}")
    if fails:
        print(f"DIVERGENCES FOUND: {len(fails)}")
        for kind, combo, oc, cc in fails[:50]:
            print(f"  {kind} children={combo}")
            print(f"     oracle={oc}  code={cc}")
        return 1
    print("RESULT: 0 divergences — code matches the independent oracle on every case.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
