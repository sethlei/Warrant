# Self-verification — `code/warrant.py` against `METHODOLOGY.md` §3–8

This is the method applied to itself: Warrant run on the very code that implements it.
It is rendered **two ways** — the **code template** (practitioner-facing, residual-first)
and the **formal template** (the full `(s_pass, s_death)` vector) — because one method
has two renderings, and a code claim keeps two referents apart:

> *"the code realizes the spec"* — **`SOUND(impl)`** — is a different claim from
> *"the spec is the right model"* — **`SOUND(model)`**.

**The verdict, up front.** The algebra is **`SOUND(impl)` — exhaustively**, against an
independent oracle (310 compose cases + 27 adversarial probes, zero divergences). The
overall claim *"faithfully implements the method"* is **capped at FUZZY** by the
spec↔prose faithfulness leaf **F**. The honest ceiling *is* the result — and it is exactly
what the code template's always-present `impl↔model` leaf is built to surface. **Rung 4
(cross-lineage) has since run** — it corroborated the algebra and surfaced two
structural-enforcement gaps (the closure-leaf and faithfulness-leaf requirements), now
fixed; see *Rung-4* below.

## The load-bearing claim

*"`code/warrant.py` faithfully implements the `(s_pass, s_death)` soundness algebra
specified in `METHODOLOGY.md` §3–8 — the four cells, the AND/OR compose with exact
pass↔death duality, compose-on-realized, edge-soundness containment, the always-soft
fuzzy death, ladder escalation, and the float rule."*

The claim welds two sub-claims of very different soundness: the **algebra over the finite
`(s_pass, s_death)` domain** (exhaustively enumerable → SOUND) and the **faithfulness of
the English-to-code translation** (interpretive → irreducibly FUZZY). The referent split
pulls them apart so a `SOUND(impl)` can never be read as a `SOUND(model)`.

---

## Rendering A — the code template (practitioner-facing)

**Pin the referent — two claims hide in "faithfully implements":**
- **`SOUND(impl)`** — the code realizes the algebra as specified (cells, AND/OR compose,
  the exact pass↔death duality, compose-on-realized, edge-soundness containment,
  always-soft fuzzy death, the float rule).
- **`SOUND(model)`** — the specified algebra is the right formalization of the prose
  intent. For a code claim the **`impl↔model` faithfulness leaf is always present** — and
  here it is the binding one.

**What actually ran (realized, not labeled):**
- `warrant.py --self-test` → green — but a green example suite is **`(L,H)` PARTIAL**,
  never SOUND. It certifies "no known failing case," not correctness. (The method's own
  thesis, applied to its own self-test.)
- `self_verify_enumeration.py` → **310 compose cases vs an independent oracle, 0
  divergences.** The oracle re-derives §3's min/max + died-set rules from scratch — it
  does *not* call the code's `_compose_and` / `_compose_or`.
- `self_verify_probes.py` → **27 adversarial probes, 0 divergences.**

**Self-disprove pass — where did I overclaim, and what does each checker share with the
thing it checks?**
1. **The "exhaustive" enumeration is exhaustive for node arity ≤ 3.** The compose code is
   a uniform `min`/`max` fold over the whole child list with **no arity special-case**, so
   the same code path runs for many children as for three, and `min`/`max` associate.
   `SOUND(impl)` therefore extends to all arities — but **by a small reduction argument
   (uniform fold + associativity) that is not itself enumerated.** Naming it is the
   discipline; the result stands. *Since corroborated (rung-4 follow-on):* an independent
   **TLA+ model** (`tla/`, derived from the prose by a different instance, in a different
   formalism) model-checks the compose properties — including **order-independence under all
   permutations** — exhaustively to **arity 8** (390,625 states, 0 violations,
   negative-control-verified). The reduction argument's conclusion is now machine-checked at
   ≤8 in a formalism that shares neither our language nor our oracle — **and proved for all N**
   in Lean 4 + mathlib (`lean/`): order-independence is a machine-checked theorem (no `sorry`;
   standard axioms only), not a reasoning step at all. **Residual #1 is closed.**
2. **The oracle is route-independent, not prose-independent.** It defeats a shared *coding*
   bug (different machinery, same answer). It does **not** defeat a shared *misreading*:
   the oracle and the code share one author and one source prose, so a misread of the spec
   would survive both. **That shared dependency is exactly the `impl↔model` faithfulness
   leaf F** — and it is why F stays FUZZY. (Substrate axis: a fresh, same-lineage disprove
   instance ran it, same machine/runtime; a second-machine run is cost-deferred — near-nil
   risk for deterministic arithmetic.)

**Verdict — plain, residual first:**
> **Bottom line: not "verified."** The *algebra* is `SOUND(impl)` — exhaustively, against
> an independent oracle. But the claim *"faithfully implements the method"* is capped at
> **FUZZY** by the `impl↔model` leaf: whether the encoded algebra matches the prose's
> intent is a judgment, read at a fresh same-lineage instance only.
> **Still open (the to-do list):** *cost-deferred* — take F up the ladder: a **cross-lineage
> read** + a **human review** of spec-vs-prose (the named promotion path).
> **Established:** `SOUND(impl)` on the full algebra (310 cases + 27 probes, 0 divergences).
> **Found & fixed in-pass:** the empty-AND/OR node now raises a clear `ValueError` at
> construction (was an opaque `IndexError`), regression-guarded.

---

## Rendering B — the formal template (the full `(s_pass, s_death)` vector)

`root = AND(L1 … L11, F)`. Each leaf's falsifier was fixed **before** its checker ran.

| leaf | sub-claim (spec ref) | referent | cell `(s_pass,s_death)` | what was RUN | verdict |
|---|---|---|---|---|---|
| **L1** | the four cells map the pairs (§3) | impl | **SOUND (H,H)** | probes: all 4 pairs vs an independent table | PASS |
| **L2** | AND: pass=min; death=max-over-died (§3) | impl | **SOUND (H,H)** | enumeration, all AND combos, arity 1–3 | PASS |
| **L3** | OR: pass=max; death=min; all must die (§3) | impl | **SOUND (H,H)** | enumeration, all OR combos, arity 1–3 | PASS |
| **L4** | exact AND↔OR / pass↔death duality (§3) | impl | **SOUND (H,H)** | the same 310 cases cover both halves | PASS |
| **L5** | compose on `realized`, gap surfaced loud (§3) | impl | **SOUND (H,H)** | probe: `cost_deferred` fires; leaf ∉ `sound_realized` | PASS |
| **L6** | containment carries the **edge's** soundness (§3) | impl | **SOUND (H,H)** | hard-edge + soft-edge containment probes | PASS |
| **L7** | a FUZZY death stays SOFT under any ladder (§4) | impl | **SOUND (H,H)** | unanimous 5-vote ladder → leaf in an AND | PASS |
| **L8** | a split ladder → PENDING, no majority-kill (§4) | impl | **SOUND (H,H)** | enumerated split-vote vectors | PASS |
| **L9** | float rule: bump→discretization→reroute (§7) | impl | **SOUND (H,H)** | the reachable branch states | PASS |
| **L10** | the validate() gate: OR-closure · faithfulness-leaf · OR-root all **enforced** (§3) | impl | **PARTIAL (L,H)** | presence + the **raise** on each violation | PASS |
| **L11** | adversarial corners (mixed / empty / multi-death) | impl | **PARTIAL (L,H)** | hand-built adversarial graphs | PASS |
| **F** | the encoded algebra = the **prose's intent** | **model** | **FUZZY (L,L)** | rung-3 + rung-4 (cross-lineage); rung-5 (human) deferred | PASS (soft) |

L2–L4 are the spine, and they are **SOUND, not example-based**: the compose rules range
over a **finite** domain (each child carries `verdict ∈ {PASS,DEATH,PENDING}`,
`strength ∈ {H,L}`), so all combinations for 1–3 children are **exhaustively enumerated**
against an **independent oracle**.

> **VERDICT: PASS — capped at FUZZY by leaf F.**
> `SOUND(impl)-realized`: {L1–L9} — the `(s_pass,s_death)` algebra, certified by exhaustive
> enumeration (310 compose cases) + 27 probes, **0 divergences**. *(Arity ≤3 by Python
> enumeration; the compose properties incl. order-independence model-checked to arity 8 in
> an independent TLA+ formalism (`tla/`) and **machine-proved for all N** in Lean 4 + mathlib
> (`lean/`).)*
> `PARTIAL`: {L10, L11} — a failing case would be real; a pass is only not-yet-refuted.
> `FUZZY(model)` residual (to-do): {F} — spec↔prose faithfulness.
> `cost-deferred (LOUD)`: human review (rung 5) on F — rung 4 (cross-lineage) has run; see *Rung-4* below.
>
> PASS-strength of the root = **FUZZY**, by the same weakest-link rule the algebra
> implements. The enumerable algebra is sound and provably so; the prose-to-code
> faithfulness is not, and is not pretended to be.

---

## The method graded by its own algebra (runnable)

`python3 code/self_verify_graph.py` builds the graph above and runs `warrant.py`'s own
composer and read-out on it — the tool printing its verdict on itself:

```
=== Warrant, graded by its own algebra (formal notation) ===

VERDICT: PASS  (s_pass=L)
  SOUND-realized leaves : ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9']
  FUZZY residual (to-do): ['F']
```

PASS-strength is capped at `L` by the FUZZY leaf F (and the two PARTIAL corners) — the
same weakest-link rule the algebra implements. The enumerable algebra is `SOUND(impl)` and
exhaustively so; whether it faithfully captures the prose — `SOUND(model)` — is the open
judgment, named not hidden.

---

## Exhaustive-enumeration results  (`code/self_verify_enumeration.py`)

```
Child-states enumerated     : 5  { PASS·H, PASS·L, DEATH·H, DEATH·L, PENDING }
Children counts             : {1, 2, 3}
Total compose cases checked : 310   (AND + OR, both directions of the duality)
Divergences from oracle     : 0
RESULT                      : code matches the independent oracle on every case.
```

The oracle is built from the spec text alone (§3 combine-rules + §5 "different combinators,
never swap them"); it does **not** call the code's compose functions. Code output
`(verdict, pass_strength, death_strength)` was compared cell-for-cell to the oracle's for
all 310 cases. **Zero divergences.**

## Adversarial probe results  (`code/self_verify_probes.py`)

```
Assertions : 27     Divergences : 0     Notes : 0
```

Each probe re-derives its expectation from the spec, not the code: the cell map (§3),
hard-edge and soft-edge containment (§3), realized<achievable surfaced + excluded from
`sound_realized` (§3), AND multi-death → max certificate (§3), OR all-dead → min cap
(§3 duality), unanimous fuzzy ladder death stays `(L,L)` SOFT (§4), split-ladder
escalation (§4), the four float-rule branches (§7), the **lang-sec validate() gate** — an
OR with no closure-leaf, a decomposed root with no faithfulness-leaf, and an OR-as-root are
each **REJECTED loudly** (§3) — the `realized=None` guard, and the empty-node guard (below).
(Compose/containment math fixtures run below the recognition boundary via
`compose(_validate=False)`; the gate probes run through it and assert the raise.)

## Found and fixed — the disprove pass actioning its own to-do

Empty AND / empty OR *previously* raised an opaque `IndexError` (an `all(...)` over an
empty child list is vacuously satisfied, then `kids[0]` indexes out of range). The spec §3
does **not define** an empty node, and no graph in the module builds one — a latent
robustness gap on a spec-undefined input, reachable only if a *user* of the library hand-
builds such a node. **This adversarial pass surfaced it, and it was closed:** an AND/OR
node with no children is now rejected **at construction** with a clear `ValueError`,
regression-guarded by both the self-test (check 11) and the probe set. Found by the
disprove pass → fixed → re-verified clean. That loop — not the absence of any gap — is the
behavior the method is built to produce.

## Rung-4 cross-lineage check — executed (provenance: `cross_lineage_review_2026-06-23.md`)

The faithfulness leaf **F**, first read at rung 3 (a fresh same-lineage instance), has now
been taken to **rung 4 (cross-lineage)**: `METHODOLOGY.md` and `warrant.py` were handed,
blind, to a clean-context model of a **different lineage** (prompt:
`cross_lineage_faithfulness_check.md`; `SELF_VERIFICATION.md` and the oracle were withheld
so the check stayed blind). Outcome:

- **The algebra was corroborated** — cells, AND, OR, duality, realized-not-achievable, the
  ladder, and the float rule all read as faithful by an independent lineage. The
  exhaustively-SOUND part agrees across lineages.
- **Two real structural-enforcement gaps were surfaced — and FIXED.** The spec *required* an
  OR-closure-leaf and a root faithfulness-leaf; the code only *warned* / stored a flag. A
  cross-lineage reader — not sharing the assumption baked into our own probes ("a warning is
  fine") — flagged both. They are now enforced at the recognition boundary
  (`Graph.validate`): a malformed graph is **rejected loudly**. This is the rung-4 analogue
  of the empty-node catch — a stronger rung looked, found a gap the weaker rung's own
  fixtures hid, and the loop closed (found → fixed → re-verified; 27 probes green).
- **Two findings were honest false-positives** (each flagged by the reviewer as its own
  least-sure point, then checked against the code): (i) *"containment loses directional
  soundness"* — it doesn't; a contained node is moot via *one* direction (the death-edge or
  the pass-edge) and the code records that direction correctly; (ii) *"containment only
  marks PENDING nodes"* — correct for its cost-saving role. Both are spec-wording clarity at
  most, not bugs.

What rung 4 does **not** settle: it shares this prompt's framing and the public literature,
so it **corroborates** F — it does not make F sound. F stays `FUZZY (L,L)`. **Rung 5 (human
+ experiment)** remains the named, deferred promotion step. The full verbatim review and the
per-finding disposition are in `cross_lineage_review_2026-06-23.md`.

---

## Independent TLA+ cross-check (`tla/`)

A **third** independent check, beyond the Python code and its Python oracle: the compose
algebra re-formalized in **TLA+** by a different instance, from the prose alone, and
model-checked with TLC. Exhaustive to **arity 8** (390,625 states), **0 invariant violations**,
with a verified negative control (a planted `max`→`min` bug is caught). It confirms the four
cells, AND/OR compose, the **De Morgan duality as an equation**, the fuzzy-soft / PARTIAL-hard
properties, and **order-independence under all permutations** — the last being the concrete
corroboration of the arity residual above. Because TLA+ shares neither our language nor our
oracle, a bug common to the Python code and its Python oracle would not survive it. The one
load-bearing interpretation (a child carries only its verdict-aligned strength) was confirmed
against `warrant.py` during verification. Full record + judgment calls: `tla/README.md`.

## Machine-checked Lean proof (`lean/`) — the proof tier

A **fourth** independent check, and the only one above the bounded tier: the compose algebra
re-formalized in **Lean 4 + mathlib** by a different instance, from the prose alone, and the
general properties **machine-proved for all N**. Where TLC samples to arity 8, Lean proves —
order-independence (`composeAnd_perm`: permuted children give the same outcome, for any N), the
AND/OR characterization (with `maxDeath_ge`/`maxDeath_le` proving the fold genuinely *is* the
max), exact De Morgan duality, the fuzzy-soft and PARTIAL-hard-kill properties, and the cells.
**No `sorry`, no added axioms** — `#print axioms` on every theorem shows only Lean's standard
`[propext, Classical.choice, Quot.sound]` (or none); `sorryAx` appears nowhere (re-verified by
re-running the build). The Lean `composeAnd`/`composeOr` match `warrant.py` node-for-node and a
`Child` carries both strengths as the code does, so the proof is about the same algebra the code
runs. This **closes residual #1** (arity / order-independence) as a theorem. Honest limit: like
the TLA+ model it's derived from the prose, so leaf F (code-matches-prose-*intent*) stays FUZZY.
Full record + judgment calls: `lean/README.md`.

---

*Reproduce:*
- `python3 code/self_verify_enumeration.py` — the 310-case SOUND enumeration
- `python3 code/self_verify_probes.py` — the 27 adversarial probes
- `python3 code/warrant.py --self-test` — the PARTIAL example suite
- `python3 code/self_verify_graph.py` — the method graded by its own algebra
- `java -cp tla2tools.jar tlc2.TLC -config tla/WarrantMC.cfg tla/WarrantMC.tla` — the
  independent TLA+ cross-check (fetch `tla2tools.jar` first; see `tla/README.md`)
- `cd lean && lake exe cache get && lake build` — the machine-checked Lean proof (all-N;
  needs `elan`; clean build + the `#print axioms` lines = verified; see `lean/README.md`)
