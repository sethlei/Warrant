# `lean/` — the compose algebra, machine-proved for all N

Warrant's README recommends *Lean or Coq for math*. Warrant's core is a small algebra, so this is
Warrant taking its own advice on the math side: a **Lean 4 + mathlib** proof of the compose
algebra's general properties — the ones that hold for **every** number of children, which a bounded
model-checker (see `../tla/`) can only sample.

This is the **proof tier**. It closes the one reasoning step the bounded checks leave open: that the
compose is **order-independent for all N** (not just up to the model-checked bound). Here it's a
machine-checked theorem.

## What is proved (every statement holds for all N)

- **Order-independence** (`composeAnd_perm` / `composeOr_perm`, strengthened by
  `*_multiset_function`): permuted children give the *same* outcome — the result is a function of
  the **multiset** of children, for any N. *(The headline theorem; the bounded checker can only
  sample it.)*
- **AND/OR characterization** (`composeAnd_death` / `_pass` / `_pending`, and the OR duals): the
  composed verdict and strength match the prose rules exactly — and `maxDeath_ge` + `maxDeath_le`
  (and `minPass_le` + `le_minPass`) prove the strength fold genuinely **is** the max / min, not just
  "some value."
- **Exact De Morgan duality** (`composeOr_eq_dual`): `composeOr s = (composeAnd (dual s)).flip`,
  for all N.
- **A FUZZY (L,L) death never composes to a HARD kill** (`and_soft_death` / `or_soft_death`).
- **A PARTIAL (L,H) leaf that dies forces a HARD kill in an AND** (`and_hard_kill`) — the
  pair-vs-scalar property, the bug the directional pair fixes.
- **The four-cell mapping** (`cell_sound` / `cell_partial` / `cell_witness` / `cell_fuzzy`).

The compose definitions (`composeAnd` / `composeOr` in `Warrant/Basic.lean`) match `code/warrant.py`
node-for-node (any-death → max-over-died; all-pass → min; dual for OR), and a `Child` carries **both**
`sPass` and `sDeath` (as `warrant.py` does), so the proof is about the same algebra the code runs.

## No `sorry`, no added axioms

A Lean proof is only sound if it has no `sorry` (which would appear as `sorryAx`) and adds no axiom.
`Warrant/Axioms.lean` runs `#print axioms` on every theorem; the build prints, for each, only Lean's
standard `[propext, Classical.choice, Quot.sound]` (or *no axioms*) — **`sorryAx` appears nowhere.**
A grep of the source for `sorry`/`admit`/`axiom` finds none. That is the legitimate-proof signature;
re-running the build re-emits the evidence.

## Reproduce

Needs [`elan`](https://lean-lang.org) (the Lean toolchain manager); mathlib comes prebuilt via the
cache (no multi-hour compile):

```sh
cd lean
lake exe cache get     # downloads prebuilt mathlib .oleans (large, but fast)
lake build             # builds the proofs; clean exit + the #print axioms lines = verified
```

Toolchain: Lean `v4.31.0`, mathlib pinned at tag `v4.31.0` (see `lean-toolchain` /
`lake-manifest.json`).

## Honest scope

This proves the **algebra's** general properties for all N, in a formalism derived from the prose.
It does **not** prove "the code is correct in every sense": the `impl↔model` faithfulness leaf —
does the algebra capture the prose's *intent* — is itself derived from the prose here too, so it
stays the honest open judgment (see `../code/SELF_VERIFICATION.md`, leaf F). The graph-structure
rules (closure-leaf, faithfulness-leaf, containment, the float rule, the variance ladder) are not
modeled here; they're checked in `code/self_verify_probes.py` and the `Graph.validate` gate.

## Judgment calls (prose was silent; choices recorded for a verifier)

1. **Verdict-aligned strength.** A `Child` stores both `(sPass, sDeath)` (the leaf-contract); the
   composition selects `sPass` from passed children and `sDeath` from died children. Matches the
   prose rules and `warrant.py`.
2. **Empty multiset.** `composeAnd ∅ = pass H`, `composeOr ∅ = death H` (the monoid identities that
   keep AND/OR exact duals on ∅). This is why `or_soft_death` carries an explicit `s ≠ 0`
   hypothesis — the empty-OR identity is a vacuous `death H` with no real died child. Harmless in
   practice: `warrant.py` *forbids* empty AND/OR nodes at construction, so ∅ never arises there.
3. **PENDING / branch priority.** A child is PENDING iff it neither passed nor died; AND prioritizes
   death > all-pass > pending (OR dually) — matching the prose and `warrant.py`.
