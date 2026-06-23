#!/usr/bin/env python3
"""Adversarial edge-case probe for warrant.py.

Hunts for divergence from METHODOLOGY.md on the parts the pure AND/OR enumeration
does not reach: the cell map, containment edge-soundness, empty child lists,
mixed PENDING+DEATH, realized<achievable surfacing, fuzzy-death-stays-soft,
ladder split escalation, the float rule, and the lang-sec validate() gate
(closure-leaf / faithfulness-leaf / OR-root all REJECTED loudly).
Each probe is independently re-derived from the spec, not from the code.

Compose/containment MATH fixtures use compose(_validate=False) to exercise the
math below the recognition boundary (synthetic fixtures, not user claims), just
as self_verify_enumeration.py calls the compose functions directly.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("warrant",
                                              os.path.join(HERE, "warrant.py"))
vd = importlib.util.module_from_spec(spec)
sys.modules["warrant"] = vd
spec.loader.exec_module(vd)

H, L = "H", "L"
PASS, DEATH, PENDING = "PASS", "DEATH", "PENDING"
findings = []


def expect(cond, label, detail=""):
    status = "ok" if cond else "DIVERGENCE"
    findings.append((status, label, detail))


# 1. Cell map — spec section 3 table, re-derived independently.
expected_cells = {(H, H): "SOUND", (L, H): "PARTIAL", (H, L): "WITNESS", (L, L): "FUZZY"}
for pair, name in expected_cells.items():
    expect(vd.cell(pair) == name, f"cell{pair}=={name}", vd.cell(pair))

# 2. Containment via SOUND edge (death_strength H) — spec section 3:
#    "containment through a SOUND death is a hard kill". AND dies hard at L1;
#    sibling PENDING leaf must be contained, contained_via == H.
g = vd.Graph(root="r")
g.add(vd.Node("r", "", kind=vd.AND, rests_on=["a", "b"]))
g.add(vd.Node("a", "", kind=vd.LEAF, achievable=(H, H), realized=(H, H), verdict=DEATH))
g.add(vd.Node("b", "", kind=vd.LEAF, achievable=(L, L)))  # pending fuzzy sibling
res = g.compose(_validate=False)
expect(res["b"].contained and res["b"].contained_via == H,
       "hard-death contains sibling via SOUND edge",
       f"contained={res['b'].contained} via={res['b'].contained_via}")

# 3. Containment via FUZZY/soft edge — spec section 3: "containment through a FUZZY
#    edge is a cost-win that forfeited an independent hard route; never a hard kill".
#    AND dies SOFT (fuzzy death, death_strength L); sibling contained_via must be L.
g = vd.Graph(root="r")
g.add(vd.Node("r", "", kind=vd.AND, rests_on=["f", "b"]))
g.add(vd.Node("f", "", kind=vd.LEAF, achievable=(L, L), realized=(L, L), verdict=DEATH))
g.add(vd.Node("b", "", kind=vd.LEAF, achievable=(H, H)))  # pending sound sibling
res = g.compose(_validate=False)
expect(res["b"].contained and res["b"].contained_via == L,
       "soft-death contains sibling via FUZZY/soft edge (NOT hard)",
       f"contained={res['b'].contained} via={res['b'].contained_via}")
# And the read-out must NOT call this a hard kill.
ro = vd.readout(g, res)
expect(ro.verdict == DEATH and ro.hard is False,
       "soft fuzzy death reads SOFT at root", f"hard={ro.hard}")
# The sound sibling 'b' was never realized -> must NOT appear as sound_realized.
expect("b" not in ro.sound_realized,
       "an un-run sound leaf contained by a SOFT death is not SOUND-realized",
       f"sound_realized={ro.sound_realized}")

# 4. Empty child list — was a latent IndexError (died=[] and all([])==True, then
#    kids[0] indexes out of range). The spec section 3 does not define an empty AND/OR
#    node, so it is now rejected at CONSTRUCTION with a clear ValueError instead of an
#    opaque IndexError deep in compose. This gap was surfaced by THIS probe pass and
#    closed; the two assertions below are the regression guard.
for kind, name in ((vd.AND, "AND"), (vd.OR, "OR")):
    try:
        vd.Node("e", "", kind=kind, rests_on=[])
        expect(False, f"empty {name} node should raise at construction", "no exception")
    except ValueError:
        expect(True, f"empty {name} node rejected with ValueError (was IndexError)")

# 5. Mixed PENDING + DEATH in an AND — death must win (spec: any one death kills).
g = vd.Graph(root="r")
g.add(vd.Node("r", "", kind=vd.AND, rests_on=["d", "p"]))
g.add(vd.Node("d", "", kind=vd.LEAF, achievable=(H, H), realized=(H, H), verdict=DEATH))
g.add(vd.Node("p", "", kind=vd.LEAF, achievable=(H, H)))  # pending
res = g.compose(_validate=False)
expect(res["r"].verdict == DEATH, "mixed PENDING+DEATH in AND -> DEATH", res["r"].verdict)

# 5b. Mixed PENDING + DEATH in an OR — NOT all died -> PENDING (spec: all must die).
g = vd.Graph(root="r")
g.add(vd.Node("r", "", kind=vd.OR, rests_on=["d", "p", "c"]))
g.add(vd.Node("d", "", kind=vd.LEAF, achievable=(H, H), realized=(H, H), verdict=DEATH))
g.add(vd.Node("p", "", kind=vd.LEAF, achievable=(H, H)))  # pending
g.add(vd.Node("c", "", kind=vd.LEAF, achievable=(L, L), is_closure=True))
res = g.compose(_validate=False)
expect(res["r"].verdict == PENDING,
       "OR with a pending alternative is NOT all-dead -> PENDING", res["r"].verdict)

# 6. lang-sec recognition boundary (spec section 3): malformed graphs are REJECTED
#    LOUDLY at validate(), never warned-and-composed. Three required-structure rules.
def _raises(thunk):
    try:
        thunk()
        return False
    except ValueError:
        return True

# 6a. a nested OR with NO closure-leaf is rejected (an eliminative OR can hide an
#     unstated exhaustiveness assumption — the exact thing the method exposes).
def _no_closure():
    g = vd.Graph(root="claim")
    g.add(vd.Node("claim", "", kind=vd.AND, rests_on=["f", "or1"]))
    g.add(vd.Node("f", "", kind=vd.LEAF, achievable=(L, L), is_faithfulness=True))
    g.add(vd.Node("or1", "", kind=vd.OR, rests_on=["x"]))
    g.add(vd.Node("x", "", kind=vd.LEAF, achievable=(H, L), realized=(H, L), verdict=PASS))
    g.compose()
expect(_raises(_no_closure), "OR with no closure-leaf is REJECTED at validate")

# 6b. a decomposed (AND) root with NO faithfulness-leaf is rejected.
def _no_faithfulness():
    g = vd.Graph(root="r")
    g.add(vd.Node("r", "", kind=vd.AND, rests_on=["a"]))
    g.add(vd.Node("a", "", kind=vd.LEAF, achievable=(H, H), realized=(H, H), verdict=PASS))
    g.compose()
expect(_raises(_no_faithfulness), "AND root with no faithfulness-leaf is REJECTED")

# 6c. an OR cannot be the top-level claim (the faithfulness-leaf must AND with it).
def _or_root():
    g = vd.Graph(root="r")
    g.add(vd.Node("r", "", kind=vd.OR, rests_on=["x", "c"]))
    g.add(vd.Node("x", "", kind=vd.LEAF, achievable=(H, L), realized=(H, L), verdict=PASS))
    g.add(vd.Node("c", "", kind=vd.LEAF, achievable=(L, L), is_closure=True))
    g.compose()
expect(_raises(_or_root), "OR root is REJECTED (must wrap in AND(faithfulness, OR))")

# 7. realized < achievable surfaced loudly as cost-deferred; NOT counted SOUND-realized.
g = vd.Graph(root="r")
g.add(vd.Node("r", "", kind=vd.AND, rests_on=["a"]))
g.add(vd.Node("a", "", kind=vd.LEAF, achievable=(H, H), realized=(L, H), verdict=PASS,
              deferral="cost-deferred(ran property test not proof)"))
ro = vd.readout(g, g.compose(_validate=False))
expect(ro.cost_deferred and "a" in ro.cost_deferred[0],
       "realized<achievable surfaced as cost-deferred", str(ro.cost_deferred))
expect(ro.sound_realized == [],
       "leaf below its ceiling NOT counted SOUND-realized", str(ro.sound_realized))

# 8. AND with multiple deaths of DIFFERENT strengths — death_strength = max (best cert).
#    Spec: "cite the best death certificate" = max s_death.
g = vd.Graph(root="r")
g.add(vd.Node("r", "", kind=vd.AND, rests_on=["soft", "hard"]))
g.add(vd.Node("soft", "", kind=vd.LEAF, achievable=(L, L), realized=(L, L), verdict=DEATH))
g.add(vd.Node("hard", "", kind=vd.LEAF, achievable=(H, H), realized=(H, H), verdict=DEATH))
res = g.compose(_validate=False)
expect(res["r"].death_strength == H,
       "AND multi-death -> death_strength = max (best certificate)",
       res["r"].death_strength)

# 9. Fuzzy death stays SOFT no matter how many ladder votes concurred (spec section 4).
leaf = vd.collapse_ladder([DEATH, DEATH, DEATH, DEATH, DEATH])
expect(leaf["verdict"] == DEATH and leaf["realized"] == (L, L),
       "unanimous fuzzy ladder death stays (L,L) SOFT", str(leaf))

# 10. Split ladder escalates to PENDING (no majority-kill) — spec section 4.
expect(vd.collapse_ladder([DEATH, PASS, DEATH])["verdict"] == PENDING,
       "split ladder escalates, no majority-kill")
expect(vd.collapse_ladder([PASS, PASS, DEATH])["verdict"] == PENDING,
       "split ladder (pass-majority) also escalates, no majority-pass-from-death")

# 11. Float rule — precision-bump invariance -> discretization floor -> FLARE + reroute.
fr = vd.classify_numerical_death(separated_from_floor=False, floor="precision",
                                 precision_bump_invariant=True,
                                 promotion_condition="prove analytic sign")
expect(fr["status"] == "FLARE" and fr["floor"] == "discretization",
       "precision-bump invariance -> discretization FLARE + reroute", str(fr))
# flare with NO promotion condition is INVALID (un-killable lens) — spec section 7.
bad = vd.classify_numerical_death(separated_from_floor=True, floor="precision",
                                  precision_bump_invariant=False, promotion_condition=None)
expect(bad["status"] == "INVALID", "flare w/o promotion condition is INVALID", str(bad))
# separated + precision floor + not invariant -> KILL.
k = vd.classify_numerical_death(separated_from_floor=True, floor="precision",
                                precision_bump_invariant=False,
                                promotion_condition="error bound")
expect(k["status"] == "KILL", "precision floor, separated -> KILL", str(k))
# discretization floor explicitly even if precision_bump not invariant -> FLARE.
d = vd.classify_numerical_death(separated_from_floor=True, floor="discretization",
                                precision_bump_invariant=False,
                                promotion_condition="analytic structure")
expect(d["status"] == "FLARE" and d["floor"] == "discretization",
       "explicit discretization floor -> FLARE regardless of bump", str(d))

# 12. __post_init__ guard: a verdict with realized=None must raise (can't decide unrun leaf).
try:
    vd.Node("x", "", kind=vd.LEAF, achievable=(H, H), verdict=DEATH)  # realized None
    expect(False, "verdict-without-realized should raise", "no exception")
except ValueError:
    expect(True, "verdict-without-realized raises ValueError")

# 13. OR death-strength = min (weakest death caps) with mixed-strength deaths — duality.
g = vd.Graph(root="r")
g.add(vd.Node("r", "", kind=vd.OR, rests_on=["p", "q", "c"]))
g.add(vd.Node("p", "", kind=vd.LEAF, achievable=(L, L), realized=(L, L), verdict=DEATH))
g.add(vd.Node("q", "", kind=vd.LEAF, achievable=(H, H), realized=(H, H), verdict=DEATH))
g.add(vd.Node("c", "", kind=vd.LEAF, achievable=(H, H), realized=(H, H), verdict=DEATH,
              is_closure=True))
res = g.compose(_validate=False)
expect(res["r"].death_strength == L,
       "OR all-dead death_strength = min (weakest death caps)", res["r"].death_strength)


def main():
    divergences = [f for f in findings if f[0] == "DIVERGENCE"]
    for status, label, detail in findings:
        tag = {"ok": "  ok", "DIVERGENCE": ">>DIVERGENCE", "note": "  note"}[status]
        line = f"{tag}: {label}"
        if detail and status != "ok":
            line += f"  [{detail}]"
        print(line)
    print(f"\nProbes: {len([f for f in findings if f[0] != 'note'])} assertions, "
          f"{len(divergences)} divergences, "
          f"{len([f for f in findings if f[0]=='note'])} notes.")
    return 1 if divergences else 0


if __name__ == "__main__":
    sys.exit(main())
