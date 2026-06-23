#!/usr/bin/env python3
"""self_verify_graph.py — the method graded by its OWN algebra.

Constructs the self-verification graph (root = AND(L1..L11, F)) described in
SELF_VERIFICATION.md and runs warrant.py's own composer + read-out on it. The
output is Warrant's verdict ON ITSELF: SOUND(impl) on the enumerable algebra,
capped at FUZZY by the spec<->prose faithfulness leaf F.

Each leaf's cell mirrors SELF_VERIFICATION.md:
  L1..L9  : SOUND  (H,H), realized (H,H)  -- certified by self_verify_enumeration.py
            (310 compose cases vs an INDEPENDENT oracle) + self_verify_probes.py.
  L10,L11 : PARTIAL (L,H), realized (L,H) -- closure-warning + adversarial corners;
            a failing case would be real, a pass is only not-yet-refuted.
  F       : FUZZY  (L,L)                  -- "does the code faithfully capture the
            ENGLISH of METHODOLOGY.md?"; read at rung 3 (fresh same-lineage) only.

Run:  python3 self_verify_graph.py
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

Node, Graph, readout = vd.Node, vd.Graph, vd.readout
H, L = vd.H, vd.L
LEAF, AND = vd.LEAF, vd.AND
PASS = vd.PASS

# the nine algebra leaves -- SOUND, exhaustively certified, all PASS
ALGEBRA = {
    "L1": "the four cells map (s_pass,s_death) -> {SOUND,PARTIAL,WITNESS,FUZZY}",
    "L2": "AND: pass=min(s_pass); death=max(s_death over DIED children)",
    "L3": "OR: pass=max(s_pass); death=min(s_death); all alternatives must die",
    "L4": "exact AND<->OR / pass<->death duality",
    "L5": "compose on REALIZED, never rounded up to achievable; gap surfaced loud",
    "L6": "containment carries the soundness of the EDGE it runs through",
    "L7": "a FUZZY death stays SOFT no matter how many ladder votes concurred",
    "L8": "a split ladder escalates to PENDING -- no majority-kill",
    "L9": "float rule: precision-bump -> discretization -> reroute; flare needs promotion",
}


def build_self_verification() -> Graph:
    g = Graph(root="claim")
    g.add(Node("claim",
               "warrant.py faithfully implements METHODOLOGY.md sections 3-8",
               kind=AND, rests_on=list(ALGEBRA) + ["L10", "L11", "F"]))
    # L1..L9 : SOUND, realized (H,H), PASS  (enumeration + probes, 0 divergences)
    for lid, claim in ALGEBRA.items():
        g.add(Node(lid, claim, kind=LEAF,
                   achievable=(H, H), realized=(H, H), verdict=PASS,
                   checker="exhaustive enumeration vs an independent oracle (+ probes)"))
    # L10, L11 : PARTIAL, realized (L,H), PASS  (a failure would be real; pass = not-yet-refuted)
    g.add(Node("L10", "an OR-node requires a closure-leaf; a missing one warns",
               kind=LEAF, achievable=(L, H), realized=(L, H), verdict=PASS,
               checker="presence/absence probe"))
    g.add(Node("L11", "adversarial corners (mixed PENDING+DEATH, empty children, multi-death)",
               kind=LEAF, achievable=(L, H), realized=(L, H), verdict=PASS,
               checker="hand-built adversarial graphs"))
    # F : the always-present impl<->model faithfulness leaf -- FUZZY, soft PASS at rung 3
    ladder = vd.collapse_ladder([PASS])   # one rung-3 read, no divergence -> soft PASS, stays (L,L)
    g.add(Node("F", "the encoded algebra faithfully captures the PROSE intent of the spec",
               kind=LEAF, is_faithfulness=True,
               checker="judgment; rung-3 read only (rungs 4-5 cost-deferred)", **ladder))
    return g


def main() -> int:
    g = build_self_verification()
    ro = readout(g, g.compose())
    print("=== Warrant, graded by its own algebra (formal notation) ===\n")
    print(ro.render(formal=True))
    print()
    print("Reading: PASS-strength is capped at L by the FUZZY leaf F (and the two")
    print("PARTIAL corners) -- the same weakest-link rule the algebra implements. The")
    print("enumerable algebra is SOUND(impl) and exhaustively so; whether it faithfully")
    print("captures the PROSE -- SOUND(model) -- is the open judgment, named not hidden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
