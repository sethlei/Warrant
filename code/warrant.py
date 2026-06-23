#!/usr/bin/env python3
"""warrant.py — reference implementation of the soundness-axis algebra.

This is the runnable companion to METHODOLOGY.md. It implements, with no
dependencies beyond the Python standard library:

  - the directional-pair leaf contract  (s_pass, s_death), each H or L
  - the four cells  SOUND(H,H) / PARTIAL(L,H) / WITNESS(H,L) / FUZZY(L,L)
  - the AND / OR composition, with its EXACT pass<->death duality
        AND: pass = min(s_pass);  death = max(s_death over DIED children)
        OR : pass = max(s_pass);  death = min(s_death over children, all must die)
  - compose on REALIZED trust (what you paid to run), never on the achievable
    ceiling; every gap is surfaced LOUDLY as cost-deferred
  - containment that carries the soundness of the edge it runs through
        (death via a SOUND edge = hard kill; via a FUZZY edge = soft, a cost-win
         that forfeited an independent hard route)
  - a VECTOR read-out (verdict + SOUND-realized set + FUZZY residual = the
    next-investigation to-do list), never a single scalar score

HARD CONSTRAINTS (so the artifact stays trustworthy):
  - Pure stdlib. No network. Deterministic: same graph -> same read-out.
  - The algebra never rounds realized trust UP toward achievable.
  - A FUZZY death is ALWAYS soft, no matter how many judges concurred:
    variance reduction (the ladder) cannot manufacture soundness.

USAGE:
  python3 warrant.py              # run the worked walkthrough
  python3 warrant.py --self-test  # run the algebra checks (offline)

The method is substrate-general: "the author" of a claim is a human or a model;
the bias it engineers around is motivated reasoning, which both have. This file
is the cross-tool layer — it runs the same under any agent or none.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from typing import Optional

# --------------------------------------------------------------------------- #
# Soundness levels and the four cells
# --------------------------------------------------------------------------- #

H, L = "H", "L"                      # high / low soundness, per direction
_RANK = {L: 0, H: 1}                 # H outranks L for min / max


def _min(a: str, b: str) -> str:
    return a if _RANK[a] <= _RANK[b] else b


def _max(a: str, b: str) -> str:
    return a if _RANK[a] >= _RANK[b] else b


def cell(pair: tuple[str, str]) -> str:
    """Name the cell for an (s_pass, s_death) pair."""
    return {
        (H, H): "SOUND",
        (L, H): "PARTIAL",
        (H, L): "WITNESS",
        (L, L): "FUZZY",
    }[pair]


# verdict / node-kind string constants (kept as plain strings for portability)
PASS, DEATH, PENDING = "PASS", "DEATH", "PENDING"
LEAF, AND, OR = "LEAF", "AND", "OR"


# --------------------------------------------------------------------------- #
# The leaf contract (the unit) and internal nodes
# --------------------------------------------------------------------------- #

@dataclass
class Node:
    """A node in the verification graph.

    A LEAF is an atomic sub-claim / definition / falsifier with a checker.
    An AND / OR node composes its children (`rests_on`).
    """
    id: str
    claim: str
    kind: str = LEAF
    rests_on: list[str] = field(default_factory=list)   # child ids (edges)

    # leaf-only fields -------------------------------------------------------
    falsifier: str = ""                       # death-condition, fixed BEFORE the run
    checker: str = ""                          # the instrument
    achievable: tuple[str, str] = (L, L)       # ceiling per direction
    realized: Optional[tuple[str, str]] = None # what you PAID; None = not run
    verdict: str = PENDING                      # PASS | DEATH | PENDING (leaf input)
    deferral: str = "none"                      # none | cost-deferred(why) | in-principle(why)
    conservatism: bool = False                  # fuzzy-ladder leaf with default-down bias

    # structural flags -------------------------------------------------------
    is_closure: bool = False                    # the "are these exhaustive?" leaf of an OR
    is_faithfulness: bool = False               # the root's "does the graph encode the claim?" leaf

    def __post_init__(self) -> None:
        if self.realized is None and self.verdict != PENDING:
            raise ValueError(
                f"leaf {self.id!r} has a verdict {self.verdict} but realized=None; "
                "you cannot decide a leaf you did not pay to run"
            )
        if self.kind in (AND, OR) and not self.rests_on:
            raise ValueError(
                f"{self.kind} node {self.id!r} needs at least one child; "
                "an AND/OR over no children is undefined"
            )


@dataclass
class NodeResult:
    """The computed read-out for one node."""
    id: str
    kind: str
    verdict: str = PENDING
    pass_strength: Optional[str] = None      # s_pass of the certifying path, if PASS
    death_strength: Optional[str] = None     # s_death of the killing leaf, if DEATH
    cell: Optional[str] = None               # leaf cell (achievable), for leaves
    contained: bool = False                  # made moot by an upstream decision
    contained_via: Optional[str] = None      # soundness of the edge that contained it
    is_closure: bool = False                  # carried up so an OR can check exhaustiveness
    notes: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# The graph + the composer
# --------------------------------------------------------------------------- #

class Graph:
    def __init__(self, root: str) -> None:
        self.root = root
        self.nodes: dict[str, Node] = {}

    def add(self, node: Node) -> Node:
        if node.id in self.nodes:
            raise ValueError(f"duplicate node id {node.id!r}")
        self.nodes[node.id] = node
        return node

    # -- recognition boundary (lang-sec): reject malformed graphs LOUDLY -------
    def validate(self) -> None:
        """Recognize the graph as well-formed BEFORE composing.

        Lang-sec posture: a malformed graph is REJECTED loudly so the *user*
        fixes the claim — the method never massages malformed input into a
        verdict. Enforced:

          * `is_faithfulness` is a LEAF-only flag.
          * The top-level claim carries a faithfulness-leaf. A decomposed root
            is an AND with an explicit `is_faithfulness=True` child leaf ("does
            this decomposition encode the claim?"). A bare LEAF root is the
            trivial, undecomposed case. A top-level OR is rejected: the
            faithfulness-leaf must AND with the decomposition, so wrap it as
            `AND(faithfulness_leaf, your_OR)`.
          * Every OR-node carries a closure-leaf ("are these alternatives
            exhaustive?") — an eliminative OR without one can hide an unstated
            assumption, the exact place the method exists to expose.
        """
        nodes = self.nodes
        for nid, node in nodes.items():
            if node.is_faithfulness and node.kind != LEAF:
                raise ValueError(
                    f"node {nid!r} sets is_faithfulness but is a {node.kind}; "
                    "the faithfulness-leaf must be a LEAF"
                )
        root = nodes[self.root]
        if root.kind == OR:
            raise ValueError(
                f"root {self.root!r} is an OR; an OR cannot be the top-level "
                "claim because the faithfulness-leaf must AND with the "
                "decomposition — wrap it as AND(faithfulness_leaf, your_OR)"
            )
        if root.kind == AND and not any(
            nodes[c].kind == LEAF and nodes[c].is_faithfulness
            for c in root.rests_on
        ):
            raise ValueError(
                f"root {self.root!r} decomposes the claim but carries no "
                "faithfulness-leaf; add an explicit is_faithfulness=True child "
                "leaf answering 'does this decomposition encode the claim?'"
            )
        for nid, node in nodes.items():
            if node.kind == OR and not any(
                nodes[c].is_closure for c in node.rests_on
            ):
                raise ValueError(
                    f"OR-node {nid!r} has no closure-leaf; add an explicit "
                    "is_closure=True child leaf ('are these alternatives "
                    "exhaustive?') — an eliminative OR without it can hide an "
                    "unstated assumption"
                )

    # -- bottom-up composition ------------------------------------------------
    def compose(self, *, _validate: bool = True) -> dict[str, NodeResult]:
        # _validate is test-only: the enumeration/probe harnesses exercise the
        # compose MATH on synthetic fixtures below the recognition boundary
        # (as self_verify_enumeration.py calls _compose_and/_compose_or directly).
        # All real usage and every demo go through validate().
        if _validate:
            self.validate()
        results: dict[str, NodeResult] = {}
        self._compose(self.root, results, set())
        self._propagate_containment(self.root, results)
        return results

    def _compose(self, nid: str, results: dict, seen: set) -> NodeResult:
        if nid in results:
            return results[nid]
        if nid in seen:
            raise ValueError(f"cycle detected at {nid!r}")
        seen.add(nid)
        node = self.nodes[nid]

        if node.kind == LEAF:
            r = self._compose_leaf(node)
            results[nid] = r
            return r

        child_results = [self._compose(c, results, seen) for c in node.rests_on]
        if node.kind == AND:
            r = self._compose_and(node, child_results)
        elif node.kind == OR:
            r = self._compose_or(node, child_results)
        else:
            raise ValueError(f"unknown node kind {node.kind!r} on {nid!r}")
        results[nid] = r
        return r

    @staticmethod
    def _compose_leaf(node: Node) -> NodeResult:
        r = NodeResult(id=node.id, kind=LEAF, verdict=node.verdict,
                       cell=cell(node.achievable), is_closure=node.is_closure)
        if node.verdict == DEATH:
            # the strength of THIS death is the realized s_death we paid for
            r.death_strength = node.realized[1]
        elif node.verdict == PASS:
            r.pass_strength = node.realized[0]
        # surface any gap between achievable and realized, loudly
        if node.realized is not None and node.realized != node.achievable:
            r.notes.append(
                f"cost-deferred: achievable {cell(node.achievable)} "
                f"{node.achievable} but realized {node.realized} ({node.deferral})"
            )
        if node.achievable == (L, L) and node.verdict == DEATH:
            r.notes.append("fuzzy death is SOFT (a judgment flipped), never a hard kill")
        return r

    @staticmethod
    def _compose_and(node: Node, kids: list[NodeResult]) -> NodeResult:
        r = NodeResult(id=node.id, kind=AND)
        died = [k for k in kids if k.verdict == DEATH]
        if died:
            # ANY one death kills the AND; cite the best death certificate (max s_death)
            r.verdict = DEATH
            r.death_strength = died[0].death_strength
            for k in died[1:]:
                r.death_strength = _max(r.death_strength, k.death_strength)
            killer = max(died, key=lambda k: _RANK[k.death_strength])
            r.notes.append(f"AND died on {killer.id} (s_death={r.death_strength})")
        elif all(k.verdict == PASS for k in kids):
            # all necessary children passed; weakest link sets pass-strength (min)
            r.verdict = PASS
            r.pass_strength = kids[0].pass_strength
            for k in kids[1:]:
                r.pass_strength = _min(r.pass_strength, k.pass_strength)
            weakest = min(kids, key=lambda k: _RANK[k.pass_strength])
            r.notes.append(f"AND passes; weakest link {weakest.id} (s_pass={r.pass_strength})")
        else:
            r.verdict = PENDING
            pend = [k.id for k in kids if k.verdict == PENDING]
            r.notes.append(f"AND pending on {pend}")
        return r

    @staticmethod
    def _compose_or(node: Node, kids: list[NodeResult]) -> NodeResult:
        # The OR-REQUIRES-a-closure-leaf rule is enforced at the recognition
        # boundary (Graph.validate), not here: a malformed graph never reaches
        # compose. This function is pure compose math.
        r = NodeResult(id=node.id, kind=OR)
        passed = [k for k in kids if k.verdict == PASS]
        if passed:
            # the best path certifies (max s_pass)
            r.verdict = PASS
            r.pass_strength = passed[0].pass_strength
            for k in passed[1:]:
                r.pass_strength = _max(r.pass_strength, k.pass_strength)
            best = max(passed, key=lambda k: _RANK[k.pass_strength])
            r.notes.append(f"OR passes on best path {best.id} (s_pass={r.pass_strength})")
        elif all(k.verdict == DEATH for k in kids):
            # all alternatives must die; the weakest death caps it (min s_death)
            r.verdict = DEATH
            r.death_strength = kids[0].death_strength
            for k in kids[1:]:
                r.death_strength = _min(r.death_strength, k.death_strength)
            r.notes.append(f"OR died (all alternatives dead); capped at s_death={r.death_strength}")
        else:
            r.verdict = PENDING
            r.notes.append("OR pending (no path certified, not all alternatives dead)")
        return r

    # -- top-down containment -------------------------------------------------
    def _propagate_containment(self, nid: str, results: dict,
                               via: Optional[str] = None) -> None:
        node = self.nodes[nid]
        r = results[nid]
        if via is not None and r.verdict == PENDING:
            r.contained = True
            r.contained_via = via
            edge = "SOUND" if via == H else "FUZZY/soft"
            r.notes.append(f"contained (moot) via a {edge} edge")
        if node.kind == LEAF:
            return
        kids = [results[c] for c in node.rests_on]
        for c in node.rests_on:
            cr = results[c]
            child_via = via  # already-moot subtree stays moot with the same edge
            if r.verdict == DEATH and node.kind == AND and cr.verdict != DEATH:
                # the AND died elsewhere; this branch is moot, contained via the death's edge
                child_via = r.death_strength
            elif r.verdict == PASS and node.kind == OR and cr.verdict != PASS:
                # the OR found its path; the other alternatives are moot
                child_via = r.pass_strength
            self._propagate_containment(c, results, child_via)


# --------------------------------------------------------------------------- #
# Vector read-out
# --------------------------------------------------------------------------- #

@dataclass
class ReadOut:
    verdict: str
    pass_strength: Optional[str]
    death_strength: Optional[str]
    hard: Optional[bool]                       # for a DEATH: hard (SOUND) vs soft (FUZZY)
    sound_realized: list[str]                  # leaves actually realized at (H,H)
    fuzzy_residual: list[str]                  # live FUZZY leaves = the to-do list
    moot_fuzzy: list[str]                      # FUZZY leaves contained via a SOUND edge (settled)
    cost_deferred: list[str]                   # leaves whose realized < achievable
    warnings: list[str]                        # closure-missing, etc.

    def render(self, formal: bool = False) -> str:
        """Human-facing read-out by default; `formal=True` for the
        `(s_pass, s_death)` / SOUND-PARTIAL-FUZZY notation (research/formal use)."""
        return self._render_formal() if formal else self._render_human()

    def _render_human(self) -> str:
        # The default surface speaks plain words: PROVEN / NOT REFUTED / STILL
        # JUDGMENT / KILL (SOUND / PARTIAL / FUZZY / DEATH are the formal labels).
        if self.verdict == DEATH:
            word = ("KILL — refuted by a hard counterexample" if self.hard
                    else "KILL (soft) — a judgment flipped, not a hard refutation")
        elif self.verdict == PENDING:
            word = "INCOMPLETE — unresolved leaves remain"
        elif self.fuzzy_residual:
            word = "STILL JUDGMENT — rests on an open judgment leaf"
        elif self.pass_strength == L:
            word = "NOT REFUTED — evidence holds, but not proven"
        else:
            word = "PROVEN"
        lines = [f"OUTCOME: {word}"]
        lines.append(f"  proven (sound) leaves       : {self.sound_realized or '—'}")
        lines.append(f"  still judgment (your to-do) : {self.fuzzy_residual or '—'}")
        if self.moot_fuzzy:
            lines.append(f"  settled — don't spend here  : {self.moot_fuzzy}")
        if self.cost_deferred:
            lines.append(f"  deferred (named, not done)  : {self.cost_deferred}")
        return "\n".join(lines)

    def _render_formal(self) -> str:
        lines = []
        head = f"VERDICT: {self.verdict}"
        if self.verdict == DEATH:
            head += f"  (s_death={self.death_strength}, {'HARD' if self.hard else 'SOFT'})"
        elif self.verdict == PASS:
            head += f"  (s_pass={self.pass_strength})"
        lines.append(head)
        lines.append(f"  SOUND-realized leaves : {self.sound_realized or '—'}")
        lines.append(f"  FUZZY residual (to-do): {self.fuzzy_residual or '—'}")
        if self.moot_fuzzy:
            lines.append(f"  moot via SOUND edge   : {self.moot_fuzzy}  (claim settled; don't spend here)")
        if self.cost_deferred:
            lines.append(f"  cost-deferred (LOUD)  : {self.cost_deferred}")
        for w in self.warnings:
            lines.append(f"  ! {w}")
        return "\n".join(lines)


def readout(graph: Graph, results: dict[str, NodeResult]) -> ReadOut:
    root = results[graph.root]
    hard = None
    if root.verdict == DEATH:
        hard = (root.death_strength == H)

    sound_realized, fuzzy_residual, moot_fuzzy, cost_deferred, warnings = [], [], [], [], []
    for nid, node in graph.nodes.items():
        r = results[nid]
        if node.kind != LEAF:
            continue
        if node.realized == (H, H) and node.verdict in (PASS, DEATH):
            sound_realized.append(nid)
        if node.achievable == (L, L):
            # a FUZZY leaf hard-contained by a SOUND death is settled (moot), not to-do
            if r.contained and r.contained_via == H:
                moot_fuzzy.append(nid)
            else:
                fuzzy_residual.append(nid)
        if node.realized is not None and node.realized != node.achievable:
            cost_deferred.append(f"{nid} ({node.deferral})")
    return ReadOut(
        verdict=root.verdict,
        pass_strength=root.pass_strength,
        death_strength=root.death_strength,
        hard=hard,
        sound_realized=sorted(sound_realized),
        fuzzy_residual=sorted(fuzzy_residual),
        moot_fuzzy=sorted(moot_fuzzy),
        cost_deferred=sorted(cost_deferred),
        warnings=warnings,
    )


# --------------------------------------------------------------------------- #
# The disprove ladder (variance axis) — collapses N judges into ONE fuzzy leaf
# --------------------------------------------------------------------------- #

def collapse_ladder(votes: list[str], conservative: bool = False) -> dict:
    """Collapse a ladder of independent fuzzy judgments into a single leaf-verdict.

    The ladder reduces VARIANCE; it cannot make a fuzzy verdict SOUND. The
    returned leaf is ALWAYS achievable (L, L) — climbing rungs makes you more
    *confident*, never more *correct*. Disagreement escalates to PENDING (the
    human-in-the-loop floor), never silently to a majority kill.

    `votes` are each PASS / DEATH / PENDING, ordered author -> ... -> most-different.

    `conservative` marks a reject-biased ladder ("default-down on doubt"). The bias is
    DIRECTIONAL — read it as a discount on the DEATH direction, never a scalar: a fuzzy DEATH
    off a reject-biased ladder is weaker than face value (it may be the bias, not a real
    refutation), while a fuzzy PASS that survives it is hard-won — *stronger* than face value,
    not weaker. (A scalar "weaker" would reintroduce the conflation the directional pair kills.)
    The flag rides on the leaf (`conservatism`); reading it is the caller's, per the rule above.
    """
    decisive = [v for v in votes if v in (PASS, DEATH)]
    leaf = dict(achievable=(L, L), conservatism=conservative)
    if not decisive:
        leaf["verdict"], leaf["realized"] = PENDING, None
        return leaf
    if all(v == DEATH for v in decisive):
        leaf["verdict"], leaf["realized"] = DEATH, (L, L)  # SOFT death by construction
    elif all(v == PASS for v in decisive):
        leaf["verdict"], leaf["realized"] = PASS, (L, L)
    else:
        leaf["verdict"], leaf["realized"] = PENDING, None  # split -> escalate, no majority-kill
    return leaf


# --------------------------------------------------------------------------- #
# The float rule (numerical deaths on continuous claims)
# --------------------------------------------------------------------------- #

def classify_numerical_death(*, separated_from_floor: bool,
                             floor: str,
                             precision_bump_invariant: bool,
                             promotion_condition: Optional[str]) -> dict:
    """Classify a computed numerical 'death' on a continuous claim as flare vs kill.

    A computed death is a FLARE, not a kill, until certified as separated from
    the controlling floor. `floor` is "precision" (an error bound can certify) or
    "discretization" (no error bound at any precision; only analytic structure
    certifies). The precision-bump diagnostic: if bumping precision leaves the
    death INVARIANT, you are at the discretization floor -> the error bound is the
    wrong instrument; escalate to analysis. Every flare must name an achievable
    promotion-to-kill condition or it is an un-killable lens, not a result.
    """
    if promotion_condition is None:
        return {"status": "INVALID",
                "reason": "a flare with no promotion-to-kill condition is an un-killable lens"}
    if floor == "discretization" or precision_bump_invariant:
        return {"status": "FLARE",
                "floor": "discretization",
                "reroute": "re-route to an analytic checker (a soundness cell-change, not a vote)",
                "promotion": promotion_condition}
    if floor == "precision" and separated_from_floor:
        return {"status": "KILL", "floor": "precision",
                "certified_by": "error bound separates the death from the cancellation floor"}
    return {"status": "FLARE", "floor": "precision",
            "promotion": promotion_condition,
            "reason": "not yet certified separated from the precision/cancellation floor"}


# --------------------------------------------------------------------------- #
# Worked walkthrough (METHODOLOGY §6) + a second graph for the pair-vs-scalar bug
# --------------------------------------------------------------------------- #

def build_walkthrough() -> Graph:
    """ "intervention X causes outcome Y" — the §6 grounding walkthrough. """
    g = Graph(root="claim")
    g.add(Node("claim", "intervention X causes outcome Y", kind=AND,
               rests_on=["F", "L1", "L2", "L3", "L4"]))
    # F FUZZY — the required root faithfulness-leaf: does {L1..L4} encode "X causes Y"?
    g.add(Node("F", "does {not-noise, out-of-sample, mechanism, binding} encode 'X causes Y'?",
               kind=LEAF, achievable=(L, L), is_faithfulness=True,
               checker="judgment; does this decomposition encode the claim?"))
    # L1 SOUND, run, lands in the null band -> hard DEATH
    g.add(Node("L1", "the effect is not noise",
               kind=LEAF, achievable=(H, H), realized=(H, H), verdict=DEATH,
               falsifier="observed effect sits inside the 95% band of a permutation null",
               checker="permutation-null over matched random labelings"))
    # L2 PARTIAL, not run (moot once L1 kills)
    g.add(Node("L2", "the effect holds out-of-sample",
               kind=LEAF, achievable=(L, H),
               checker="property test over held-out slices"))
    # L3 WITNESS, not run
    g.add(Node("L3", "a mechanism exists that could produce it",
               kind=LEAF, achievable=(H, L),
               checker="exhibit one mechanism"))
    # L4 FUZZY, not run -> the residual / to-do
    g.add(Node("L4", "this mechanism is the BINDING one (not a confound)",
               kind=LEAF, achievable=(L, L),
               checker="judgment; climbs the disprove ladder, blind-backstopped"))
    return g


def build_walkthrough_pass() -> Graph:
    """The §6 counterfactual: "had L1 passed." L1 SOUND-passes; L2 PARTIAL-passes
    (not-yet-refuted, s_pass=L); L3 WITNESS-passes (s_pass=H); L4 is a fuzzy PASS
    off the disprove ladder (still (L,L)). The AND passes with pass-strength CAPPED
    at L (by L2 and L4), SOUND-realized={L1}, and L4 stays in the live to-do list.
    """
    g = Graph(root="claim")
    g.add(Node("claim", "intervention X causes outcome Y", kind=AND,
               rests_on=["F", "L1", "L2", "L3", "L4"]))
    # F — the required root faithfulness-leaf, here a fuzzy soft-PASS (judged faithful)
    g.add(Node("F", "does the decomposition encode 'X causes Y'?",
               kind=LEAF, is_faithfulness=True,
               checker="judgment; does this decomposition encode the claim?",
               **collapse_ladder([PASS])))
    g.add(Node("L1", "the effect is not noise", kind=LEAF,
               achievable=(H, H), realized=(H, H), verdict=PASS,
               checker="permutation-null"))
    g.add(Node("L2", "the effect holds out-of-sample", kind=LEAF,
               achievable=(L, H), realized=(L, H), verdict=PASS,
               checker="property test over held-out slices (passed = not-yet-refuted)"))
    g.add(Node("L3", "a mechanism exists", kind=LEAF,
               achievable=(H, L), realized=(H, L), verdict=PASS,
               checker="witness exhibited"))
    ladder = collapse_ladder([PASS, PASS, PASS])  # fuzzy PASS, stays (L,L)
    g.add(Node("L4", "this mechanism is the BINDING one (not a confound)",
               kind=LEAF, checker="judgment; disprove ladder", **ladder))
    return g


def build_pair_vs_scalar() -> Graph:
    """The bug the pair fixes: an AND with a SOUND leaf (pending) and a PARTIAL
    leaf that RETURNS DEATH. A scalar 'PARTIAL < SOUND, weakest link' reading
    mis-calls this 'not yet refuted'. The pair gets it: death = max(s_death) = H,
    a REAL falsification, because PARTIAL is sound in the death direction.
    """
    g = Graph(root="root")
    g.add(Node("root", "claim C", kind=AND, rests_on=["F", "A", "B"]))
    g.add(Node("F", "does {A, B} encode claim C?",                  # required faithfulness-leaf
               kind=LEAF, achievable=(L, L), is_faithfulness=True,
               checker="judgment; does this decomposition encode the claim?"))
    g.add(Node("A", "sound sub-claim, not yet run",
               kind=LEAF, achievable=(H, H)))                       # PENDING
    g.add(Node("B", "property test found a counterexample",
               kind=LEAF, achievable=(L, H), realized=(L, H), verdict=DEATH,
               checker="property test", falsifier="any held-out slice fails"))
    return g


def build_or_closure() -> Graph:
    """A top-level OR must be wrapped: AND(faithfulness-leaf, OR(...)). The OR
    proves via path X OR path Y; its closure-leaf asks whether {X, Y} is
    exhaustive. Demonstrates the canonical well-formed shape + max-pass + the
    required closure-leaf.
    """
    g = Graph(root="claim")
    g.add(Node("claim", "result R holds", kind=AND, rests_on=["F", "orR"]))
    # F — the required root faithfulness-leaf (fuzzy soft-PASS: judged faithful)
    g.add(Node("F", "does 'R via X or Y' encode the claim?",
               kind=LEAF, is_faithfulness=True,
               checker="judgment; does this decomposition encode the claim?",
               **collapse_ladder([PASS])))
    g.add(Node("orR", "result R via path X or path Y", kind=OR,
               rests_on=["X", "Y", "closure"]))
    g.add(Node("X", "path X (witness found)",
               kind=LEAF, achievable=(H, L), realized=(H, L), verdict=PASS,
               checker="exhibit assignment"))
    g.add(Node("Y", "path Y (not pursued)", kind=LEAF, achievable=(H, L)))
    g.add(Node("closure", "are {X, Y} the only routes?",
               kind=LEAF, achievable=(L, L), is_closure=True,
               checker="judgment"))
    return g


def _demo(graph: Graph, title: str, formal: bool = False) -> None:
    results = graph.compose()
    ro = readout(graph, results)
    print(f"\n=== {title} ===")
    print(ro.render(formal=formal))


def run_walkthrough(formal: bool = False) -> None:
    _demo(build_walkthrough(),
          "Walkthrough: X causes Y — the not-noise leaf KILLs it (§6 run; rest moot)", formal)
    _demo(build_walkthrough_pass(),
          "Counterfactual: had it passed — NOT REFUTED, capped low; the judgment leaf stays open",
          formal)
    _demo(build_pair_vs_scalar(),
          "The bug the pair fixes: a PARTIAL leaf returning DEATH is a HARD kill, not 'not refuted'",
          formal)
    _demo(build_or_closure(),
          "AND(faithfulness, OR+closure): the OR certifies via its best path", formal)
    print("\nThe output is a VECTOR, not a score — the open (still-judgment) set is your to-do list.")
    print("Run with --formal for the (s_pass, s_death) / SOUND-PARTIAL-FUZZY notation.")


# --------------------------------------------------------------------------- #
# Self-test
# --------------------------------------------------------------------------- #

def self_test() -> int:
    failures = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            failures.append(msg)

    # 1. cells
    check(cell((H, H)) == "SOUND" and cell((L, H)) == "PARTIAL"
          and cell((H, L)) == "WITNESS" and cell((L, L)) == "FUZZY", "cell map")

    # 2. walkthrough death case: hard DEATH at L1; SOUND-realized={L1}; L4 MOOT (settled), rest contained
    g = build_walkthrough()
    res = g.compose()
    ro = readout(g, res)
    check(ro.verdict == DEATH and ro.hard is True, "walkthrough should be a HARD death")
    check(ro.sound_realized == ["L1"], f"SOUND-realized should be [L1], got {ro.sound_realized}")
    check(ro.fuzzy_residual == [] and "L4" in ro.moot_fuzzy,
          "a hard death must move L4 from to-do to moot (contained via SOUND edge)")
    check(res["L2"].contained and res["L2"].contained_via == H,
          "L2 must be contained via a SOUND edge")

    # 2b. counterfactual pass case: AND passes capped at L; L4 is a LIVE to-do; SOUND-realized={L1}
    gp = build_walkthrough_pass()
    rop = readout(gp, gp.compose())
    check(rop.verdict == PASS and rop.pass_strength == L,
          f"pass-branch must cap pass-strength at L, got {rop.pass_strength}")
    check("L4" in rop.fuzzy_residual and rop.sound_realized == ["L1"],
          "pass-branch: L4 stays a live to-do; only L1 is SOUND-realized")

    # 3. THE bug the pair fixes: PARTIAL death inside an AND => HARD kill, not 'pending'
    g2 = build_pair_vs_scalar()
    ro2 = readout(g2, g2.compose())
    check(ro2.verdict == DEATH and ro2.hard is True,
          "PARTIAL-death inside an AND must compose to a HARD kill (max s_death=H)")

    # 4. canonical AND(faithfulness, OR+closure): the OR certifies via the best path (max s_pass)
    g3 = build_or_closure()
    res3 = g3.compose()
    ro3 = readout(g3, res3)
    check(ro3.verdict == PASS, "well-formed AND(faithfulness, OR) with a passing path should PASS")
    check(res3["orR"].pass_strength == H,
          "the OR certifies via the witness path X (max s_pass = H)")

    def raises_valueerror(thunk) -> bool:
        try:
            thunk()
            return False
        except ValueError:
            return True

    # 5. lang-sec: a nested OR with NO closure-leaf is REJECTED at validate (not warned)
    def _no_closure():
        g = Graph(root="claim")
        g.add(Node("claim", "C", kind=AND, rests_on=["F", "or1"]))
        g.add(Node("F", "faithfulness", kind=LEAF, achievable=(L, L), is_faithfulness=True))
        g.add(Node("or1", "R via x", kind=OR, rests_on=["x"]))
        g.add(Node("x", "only path", kind=LEAF, achievable=(H, L),
                   realized=(H, L), verdict=PASS))
        g.compose()
    check(raises_valueerror(_no_closure), "an OR with no closure-leaf must be REJECTED loudly")

    # 5b. lang-sec: a decomposed (AND) root with NO faithfulness-leaf is REJECTED
    def _no_faithfulness():
        g = Graph(root="r")
        g.add(Node("r", "R", kind=AND, rests_on=["a"]))
        g.add(Node("a", "sub", kind=LEAF, achievable=(H, H), realized=(H, H), verdict=PASS))
        g.compose()
    check(raises_valueerror(_no_faithfulness),
          "an AND root with no faithfulness-leaf must be REJECTED loudly")

    # 5c. lang-sec: an OR cannot be the top-level claim (must be wrapped in an AND)
    def _or_root():
        g = Graph(root="r")
        g.add(Node("r", "R", kind=OR, rests_on=["x", "c"]))
        g.add(Node("x", "path", kind=LEAF, achievable=(H, L), realized=(H, L), verdict=PASS))
        g.add(Node("c", "closure", kind=LEAF, achievable=(L, L), is_closure=True))
        g.compose()
    check(raises_valueerror(_or_root), "an OR root must be REJECTED (wrap in AND(faithfulness, OR))")

    # 5d. lang-sec: is_faithfulness on a non-leaf is REJECTED
    def _faithfulness_on_nonleaf():
        g = Graph(root="r")
        g.add(Node("r", "R", kind=AND, rests_on=["a"], is_faithfulness=True))
        g.add(Node("a", "sub", kind=LEAF, achievable=(H, H), realized=(H, H), verdict=PASS))
        g.compose()
    check(raises_valueerror(_faithfulness_on_nonleaf),
          "is_faithfulness on a non-leaf must be REJECTED")

    # 6. compose on realized, never rounded up: a cost-deferred leaf is surfaced loudly.
    #    (_validate=False: this is a compose/readout MATH fixture, not a user claim.)
    g5 = Graph(root="r")
    g5.add(Node("r", "R", kind=AND, rests_on=["a"]))
    g5.add(Node("a", "could be SOUND, run cheap", kind=LEAF,
                achievable=(H, H), realized=(L, H), verdict=PASS,
                deferral="cost-deferred(ran a property test instead of the proof)"))
    ro5 = readout(g5, g5.compose(_validate=False))
    check(ro5.cost_deferred and "a" in ro5.cost_deferred[0], "cost-deferred must be surfaced")
    check(ro5.sound_realized == [], "a leaf run below its ceiling is NOT SOUND-realized")

    # 7. fuzzy death stays SOFT even with unanimous ladder agreement
    leaf = collapse_ladder([DEATH, DEATH, DEATH, DEATH, DEATH])
    check(leaf["verdict"] == DEATH and leaf["realized"] == (L, L),
          "a unanimous fuzzy ladder death must remain (L,L) — SOFT")
    g6 = Graph(root="r")
    g6.add(Node("r", "R", kind=AND, rests_on=["f"]))
    g6.add(Node("f", "binding-constraint judgment", kind=LEAF, **leaf))
    ro6 = readout(g6, g6.compose(_validate=False))
    check(ro6.verdict == DEATH and ro6.hard is False,
          "a fuzzy death must compose to a SOFT kill, never hard")

    # 8. ladder split -> escalate to PENDING, never a majority-kill
    split = collapse_ladder([DEATH, PASS, DEATH])
    check(split["verdict"] == PENDING, "a split ladder must escalate, not majority-kill")

    # 9. float rule: precision-bump invariance -> discretization floor -> FLARE + reroute
    fr = classify_numerical_death(separated_from_floor=False, floor="precision",
                                  precision_bump_invariant=True,
                                  promotion_condition="prove the analytic sign of the integrand")
    check(fr["status"] == "FLARE" and fr["floor"] == "discretization", "float-rule reroute")
    bad = classify_numerical_death(separated_from_floor=True, floor="precision",
                                   precision_bump_invariant=False, promotion_condition=None)
    check(bad["status"] == "INVALID", "a flare with no promotion condition is invalid")

    # 10. duality sanity: OR death caps at the WEAKEST death (min s_death).
    #     (_validate=False: pure OR-compose math fixture.)
    gor = Graph(root="r")
    gor.add(Node("r", "R", kind=OR, rests_on=["p", "q", "c"]))
    gor.add(Node("p", "alt p died soft", kind=LEAF, achievable=(L, L),
                 realized=(L, L), verdict=DEATH))
    gor.add(Node("q", "alt q died hard", kind=LEAF, achievable=(H, H),
                 realized=(H, H), verdict=DEATH))
    gor.add(Node("c", "closure", kind=LEAF, achievable=(H, H),
                 realized=(H, H), verdict=DEATH, is_closure=True))
    ror = readout(gor, gor.compose(_validate=False))
    check(ror.verdict == DEATH and ror.death_strength == L,
          "OR death must cap at the weakest alternative's death (min s_death)")

    # 11. an AND/OR node with no children is rejected at construction (a clear error,
    #     not an IndexError deep in compose)
    for k in (AND, OR):
        try:
            Node("empty", "no children", kind=k, rests_on=[])
            check(False, f"empty {k} node should raise at construction")
        except ValueError:
            check(True, f"empty {k} node rejected with ValueError")

    if failures:
        print("SELF-TEST FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("SELF-TEST PASSED: cells, the §6 walkthrough (death + pass branches), the")
    print("  pair-vs-scalar bug, containment, compose-on-realized, soft-fuzzy-death,")
    print("  ladder escalation, the float-rule, the AND/OR death duality, and the")
    print("  lang-sec validate() gate (closure-leaf, faithfulness-leaf, OR-root).")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="reference implementation of the soundness-axis algebra")
    ap.add_argument("--self-test", action="store_true", help="run offline algebra checks")
    ap.add_argument("--formal", action="store_true",
                    help="show the (s_pass,s_death) / SOUND-PARTIAL-FUZZY notation instead of plain words")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    run_walkthrough(formal=args.formal)
    return 0


if __name__ == "__main__":
    sys.exit(main())
