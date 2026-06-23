# `tla/` — the compose algebra, model-checked in TLA+

Warrant's README says: *if your field has a formal verification method, use it; TLA+ for code.*
The core of Warrant **is** code — a finite-state soundness-composition algebra — so its own formal
method is TLA+. This directory is Warrant following its own advice, on itself.

It is also a **route-independence cross-check**, in the method's own sense. The algebra already has
a Python reference implementation (`code/warrant.py`) and a Python enumeration oracle
(`code/self_verify_enumeration.py`). This is a **third, independent** check: a *different formalism*
(TLA+), written by a *different instance*, derived **only from the prose of `METHODOLOGY.md`** —
the author of this model did not read `warrant.py` or the oracle. A bug shared between the Python
code and its Python oracle (same language, same hand) would survive both; it would not survive a
re-derivation in TLA+.

## What it checks

`Warrant.tla` models the single-node `(s_pass, s_death)` compose algebra over the finite domain
(each child ∈ {PASS·H, PASS·L, DEATH·H, DEATH·L, PENDING}). `WarrantMC.tla` checks, as TLC
invariants over **every** N-child configuration, nine properties re-derived from the prose:

- the four-cell mapping (`SOUND/PARTIAL/WITNESS/FUZZY`);
- **AND** compose: any-death-kills · death-strength = max over died · pass-strength = min;
- **OR** compose: all-must-die · death-strength = min · pass-strength = max;
- **exact De Morgan duality** (OR = flip ∘ AND ∘ Dual), as an equation;
- a **FUZZY (L,L) death never composes to a hard kill**;
- a **PARTIAL (L,H) leaf that dies, inside an AND, yields a HARD kill** (the scalar-weakest-link
  bug the directional pair fixes);
- **order-independence** of compose under every transposition (⇒ full permutation invariance — the
  property a small hand-enumeration cannot fully cover);
- result well-typedness.

## Result

- **Exhaustive to arity N = 8** — all `5^N` child-combinations for both AND and OR:
  N=6 → 15,625 states (~6s) · N=7 → 78,125 (~39s) · **N=8 → 390,625 (~4m22s)**.
- **0 invariant violations at every N from 3 to 8.** "Model checking completed. No error has been found."
- **Negative-control verified:** planting a bug (AND death `max`→`min`) makes TLC report
  `Invariant ANDCompose is violated` — so the invariants have teeth, they are not vacuously true.

This raises the exhaustive floor for the algebra's properties (esp. order-independence) from the
Python enumeration's arity ≤3 to ≤8, in an independent formalism.

## Reproduce

```sh
# fetch the official TLA+ tools (needs a JRE; tested on Java 21)
curl -L -o tla2tools.jar https://github.com/tlaplus/tlaplus/releases/latest/download/tla2tools.jar
java -cp tla2tools.jar tlc2.TLC -config WarrantMC.cfg WarrantMC.tla
# change `N = 6` to `N = 8` in WarrantMC.cfg to reproduce the maximum bound.
```

## Honest scope (what this does NOT cover)

This models the **single-node compose algebra** — the four cells, AND/OR compose, the duality, and
the two soft/hard-kill properties. It does **not** model the graph-structure rules (the
faithfulness-leaf and OR closure-leaf requirements, containment, cost-deferred/realized, the float
rule, or the variance ladder); those are checked in `code/self_verify_probes.py` and the lang-sec
`Graph.validate` gate. Multi-level graphs reduce to repeated single-node compose (a composed node's
`(verdict, strength)` has the same shape as a child), so the recursion is covered transitively.

## Route-independence judgment calls (read these first if comparing to the reference impl)

The model was derived from prose, so a few interpretations were forced. The load-bearing one was
independently confirmed against `warrant.py` during verification:

1. **A child carries only its verdict-aligned strength** (a PASS child's `s_death` and a DEATH
   child's `s_pass` are never read by any compose rule). *Confirmed faithful:* `warrant.py`'s
   `_compose_leaf` reads `realized[1]` only for deaths and `realized[0]` only for passes. This was
   the model author's flagged "biggest bet"; it holds.
2. **AND passes only when all children pass; death dominates pending.** **OR passes if any child
   passes** (the exact dual). Both match `warrant.py`.
3. Empty-fold identities: `max ∅ = L`, `min ∅ = H` (the lattice bottom/top); only reached in
   branches whose strength is unused, so they affect no reported verdict.
4. "FUZZY death never hard" is encoded as "all-soft-deaths ⇒ composed death soft," which is
   stronger than the literal prose and correct (it does not claim softness when a hard sibling also
   dies — that is the complementary PARTIAL-hard-kill property).
