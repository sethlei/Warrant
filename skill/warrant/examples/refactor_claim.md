# Worked example — "this refactor preserves behavior"

A code-shaped walkthrough of the verify procedure. The claim is the everyday one a developer
makes before merging, and the value of the method is that it **refuses to rubber-stamp it off
a green test run** — and tells you exactly what to do to earn a stronger verdict.

---

**Claim (elected, load-bearing — it's going to prod):**
*"This refactor — extracting `computeTotal()` out of `checkout()`, no intended behavior
change — preserves behavior."*

## Decompose (the graph)

Root **AND-node** over the leaves below. First, the honest part most checks skip:

- **L0 — root faithfulness (FUZZY).** "Preserves behavior" really means *"for all inputs, old
  output ≡ new output, including side-effects and ordering."* Exhaustive comparison is
  infeasible, so the decomposition *approximates* behavior as `{typed interface, test outputs,
  observable side-effects}`. **That approximation is itself a leaf** — flag it `(L,L)`; the
  verdict is only as faithful as this edge.

- **L1 — the public interface/signature is unchanged.**
  `(H,H)` **SOUND(impl)** where types cover. **Run it:** type-check + diff the exported
  signatures. → say it passes. *(Note the referent: this is sound about the code, not about
  whether the interface is the right one — that's L0's job.)*

- **L2 — the existing test suite passes on the refactored code.**
  `(L,H)` **PARTIAL** — a failure is a real counterexample; passing is *not-yet-refuted*.
  **Run it.** → say it's green.

- **L3 — no new observable side-effects** (I/O, global/state mutation, call ordering).
  `(L,H)`→`(L,L)` — a targeted check can catch *some* (diff a trace), but the general claim
  is a judgment. PARTIAL where you can trace it, FUZZY otherwise.

- **L4 — behavior matches on inputs the test suite does NOT cover.**
  `(L,L)` **FUZZY** — no sound checker without exhaustive enumeration or a proof. **This is the
  binding leaf**, and the one a green run hides.

## Compose

AND-node over {L0, L1, L2, L3, L4}, all green/passed so far:
- **DEATH-strength:** nothing died (no failing test) → no kill. *(Had L2 returned a failing
  test, that's `s_death = H` — a real, hard counterexample, even though L2 is "only" PARTIAL.)*
- **PASS-strength = min over children of `s_pass`** = **L** — because L4 (uncovered inputs) and
  L0 (the faithfulness approximation) are `(L,L)`. The SOUND leaf L1 cannot lift the min.

## Self-disprove pass (re-audit before reporting)

Turn the method on the verdict-in-progress:
- **Where did I overclaim?** L1 is `SOUND(impl)` — sound that the *signature* is intact, not that
  behavior is. Keep the referent tag so it can't be read as "behavior verified."
- **What does the L2 checker share with the thing it checks?** The test suite was written against
  the *same* author's understanding of the code — it shares the assumptions. So a green suite is
  self-consistency, not independent truth: L2 stays `(L,H)` PARTIAL, and it cannot lift the
  PASS-strength. (This is exactly why L4 is the binding leaf, not L2.)

Nothing moves a hard cell here, but the re-audit is what keeps L2-green from creeping into the
headline as a PASS.

## Verdict — plain first, residual forward (not "verified ✓")

> **Bottom line:** *not proven* — and *not refuted*. PASS-strength is capped **LOW** by the
> weakest load-bearing leaf; nothing died (no failing check).
>
> **Still open (the to-do list):**
> - *cost-deferred* — **L4: behavior on uncovered inputs.** Decidable; the decisive check is named
>   (property test → bounded model-check, below). The binding leaf, and the one a green run hides.
> - *judgment* — **L0: behavior ≈ {types, tests, effects}** (the faithfulness approximation) and
>   **L3: side-effect generality**. No checker fully resolves these without a tighter model.
>
> **Established:** `SOUND(impl)` on **{L1: interface unchanged}**. Not-yet-refuted (PARTIAL) on
> **{L2: tests green}**.
>
> *(Full formal vector, if elected: PASS-strength = L, DEATH-strength = none; `(s_pass,s_death)`
> per leaf available.)*
>
> **Plain English:** the interface is provably intact and nothing is refuted, but "preserves
> behavior" is **not proven** — a green suite never certifies, and the real exposure is the inputs
> the tests don't touch.

## The promotion path (what makes this actionable)

The method doesn't stop at "low confidence" — it names how to **move the binding leaf up a cell:**
- **L4 → PARTIAL:** add a **property test** (`old(x) == new(x)` over generated inputs, e.g.
  Hypothesis / fast-check / QuickCheck). Now a divergence is a real counterexample.
- **L4 → SOUND:** if the input domain is bounded, a **characterization/golden test over the
  full bounded domain**, or a **bounded model-check**, certifies it exhaustively over that model.
- **L0 → tighter:** if side-effects matter, add a trace/spy assertion so "behavior" includes
  the effects you actually care about, shrinking the faithfulness gap.

Do one of those and re-run: PASS-strength rises from LOW to whatever the new weakest leaf allows
— *earned*, not asserted. **That is the difference between "tests pass" and "I checked it."**
