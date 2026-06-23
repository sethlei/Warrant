---
name: warrant
description: >-
  Verify a load-bearing claim by decomposing it into a graph of sub-claims and routing
  each to the soundest available checker, then composing a verdict that stays honest about
  what is *proven* vs merely *not-yet-refuted* vs an *open judgment*. Use when someone
  asserts something high-stakes — "this change preserves behavior," "this fix is correct,"
  "this is safe to ship," "this result holds" — and wants it rigorously checked instead of
  eyeballed. Especially strong for code claims, where leaves map to runnable checks
  (type-checker, test suite, property test, bounded model-check) — and where it keeps the
  two referents apart: "the code realizes the spec" is a different claim from "the spec is
  right." Do NOT use for casual or throwaway assertions — it is an elected burden of proof,
  not a default gate.
---

# Warrant — checking a load-bearing claim

You are verifying a claim by **decomposing it into a graph and routing each piece to the
soundest checker that exists for it**, then composing a verdict that never overstates what
was actually established. The core discipline: *a passing check is not a proof.* Keep the
soundness of each leaf explicit, run the checks you can actually run, name what's left, and
**re-audit your own verdict for where it overclaimed** before you report it.

## When to run this

The user has a **load-bearing** claim — a conclusion, a fix, a "this works / is correct /
is safe / preserves behavior" assertion — and wants it checked rigorously. If the claim is
cheap or throwaway, say so and don't run the full procedure (this is an *elected* burden,
not a tax on every statement).

## The procedure

**1. State the claim, elect, and pin the referent.**
- Write the claim in one crisp sentence. Confirm it's worth the burden.
- **Confirm the claim actually obtains.** Before decomposing, check the thing you're about to
  verify *exists* / the target is real. "Verify that the v1→v2 migration is safe" is vacuous if
  there is no v1 in the wild — don't decompose a claim about nothing.
- **Name the referent — which truth are you after?** Two different claims hide in one sentence:
  - **internal validity / faithfulness** — *"X realizes Y"* (the code implements the spec; the
    proof follows from the axioms). Cheap and often decisive.
  - **external correctness** — *"Y is true"* (the spec/model is right; the axioms hold).
  
  Keep them apart and **tag every soundness label with its referent: `SOUND(impl)` ≠ `SOUND(model)`.**
  A seductive `SOUND(impl)` reads as "verified" while the model is still wide open. **For a code
  claim, the `impl↔model` faithfulness edge is an always-present leaf** (below), never skipped.
- **Offer the verdict format up front.** Default is the plain-language rendering (step 7). If the
  audience wants the full `(s_pass, s_death)` vector — research papers, formal reviews — offer it
  now, before execution, so the report is rendered to fit.
- **Note who is verifying.** The instance that *verifies* should not be the instance that
  *proposed* the claim or target (ownership-reset). See **Instance boundaries** below — this also
  governs the case where one agent writes the DAG and a different agent runs the checks.

**2. Decompose into the graph.** Break the claim into the atomic sub-claims ("leaves") it
rests on. Mark structure:
- **AND-node** — all children necessary (the claim needs them all).
- **OR-node** — alternatives (it holds via X *or* Y). **Every OR-node requires a closure-leaf:**
  "are these alternatives actually exhaustive?" — usually a judgment, and the place an
  eliminative argument hides an unstated assumption. This is enforced, not advisory: an OR with
  no closure-leaf is **rejected** — add the leaf, don't skip it.
- **Root faithfulness-leaf** (required) — "does this decomposition actually encode the claim?" The
  causal model your graph asserts is itself a checkable leaf (usually a judgment), not free truth.
  It's a *necessary* condition, so it ANDs with the decomposition: a decomposed claim's root is an
  **AND** carrying an explicit faithfulness-leaf (a top-level OR gets wrapped as
  `AND(faithfulness-leaf, OR(...))`). A decomposed claim with no faithfulness-leaf is rejected.
- **For code claims, an always-present `impl↔model` faithfulness leaf** — "even if the code
  provably realizes the spec, is the *spec* the right model of reality?" This is the leaf that
  keeps `SOUND(impl)` from being read as `SOUND(model)`.
- State each leaf so *a stranger could evaluate it cold.* The leaf statement is a contract: if a
  different agent (or future-you) couldn't run it from the wording alone, it isn't atomic yet —
  split it.

**3. Route each leaf by soundness — a directional pair `(s_pass, s_death)`.** A checker can be
trustworthy at certifying *truth*, *falsehood*, both, or neither:

| cell | `(s_pass, s_death)` | what it means | typical checker |
|---|---|---|---|
| **SOUND** | (H,H) | certifies both ways | type-checker (where types cover), exhaustive enumeration, bounded model-check, permutation-null, formal proof |
| **PARTIAL** | (L,H) | certifies DEATH only | example/property tests — *a failure is a real counterexample; a green suite never certifies* |
| **WITNESS** | (H,L) | certifies PASS only | exhibit a witness/example — certifies possibility; absence proves nothing unless exhaustive |
| **FUZZY** | (L,L) | a judgment, neither way | "is this novel / the binding cause / interpretively faithful" |

Tag every SOUND with its referent (`SOUND(impl)` / `SOUND(model)`, step 1).

**4. RUN the checks you can run — don't just label.** This is the point. For each leaf, find
the soundest *available* checker and actually execute it:
- types-leaf → run the type-checker / diff the signatures.
- behavior-leaf → run (and if thin, extend) the test suite.
- a decidable property → write a bounded model-check or a property test.
- a fuzzy leaf → flag it; if load-bearing, get an **independent** check (see step 6); never
  fabricate soundness.

Disciplines while running:
- **Enforce "soundest available," don't just claim it.** Before settling for a randomized or
  sampling test, ask: *is there a proof, an exhaustive enumeration, or a symbolic check first?* A
  one-line induction beats an 80×50 random sweep — route to it.
- **A mock/fake is its own FUZZY leaf.** A check that runs against a fake/stub is `SOUND(against
  the fake)` — and *"the fake mirrors reality"* is a separate `(L,L)` leaf. Don't let a
  fake-backed green read as SOUND-realized.
- **Prioritize by real-world load — *for code claims*.** Spend the expensive checks on the leaves
  that carry actual code-path load, not on every leaf the tree happens to contain (a near-dead
  migration path doesn't earn SOUND rigor). *This heuristic is code-specific:* for research/
  external claims, weight by **logical load-bearingness** instead — a rarely-invoked premise can
  be the binding one, and frequency is the wrong axis.
- **Generated tests are the user's to keep.** If you write a promotion-path test (one that moves a
  FUZZY/PARTIAL leaf up a cell), it's a durable deliverable and a regression guard — **present it
  and let the user elect to keep/commit it.** Don't silently leave it in their tree, and don't
  delete it without asking.
- Record **`realized`** (what you actually ran) separately from **`achievable`** (the ceiling).
  If you stopped short for time/cost, say so **loudly** (`cost-deferred`) — never silently round a
  not-run check up to "fine."

**5. Compose up the graph.**
- **AND-node:** PASS-strength = **min** over children of `s_pass`; DEATH-strength = **max**
  over *died* children of `s_death` (any one sufficient death kills the AND).
- **OR-node:** PASS-strength = **max** of `s_pass`; DEATH-strength = **min** of `s_death`.
- A **containment** (an upstream leaf died, so a downstream one is moot) carries the soundness
  of the *edge* it ran through — a containment through a fuzzy edge is a cost-win, not a hard kill.
- A fuzzy leaf that several independent reviewers agreed on is **still `(L,L)`** — more
  *confidence*, not more *soundness*. It enters its AND-node as a soft death, never a hard kill.

**6. Self-disprove pass — re-audit your own verdict (MANDATORY).** Before you report, turn the
method on your own work. This is where the verdict earns its honesty — the failures the method
exists to catch are the ones *you* just committed:
- **"Where did I overclaim?"** Walk each leaf you marked SOUND and ask what would make it less.
- **"What does each checker SHARE with the thing it checks?"** A cross-check that shares the
  model, the constants, or the assumptions of the thing it's checking is **not independent** — it
  tested self-consistency, not truth. Decompose "independent" into **route-independence**
  (different machinery, same answer → defeats a shared bug) and **substrate-independence** (same
  check, second instance/box → defeats an environment artifact); name which one you actually have.
- **Re-audit your own soundness labels.** The label is itself a fuzzy meta-leaf;
  `PARTIAL`-mislabeled-as-`SOUND` is the trap (a 2400-case numerical agreement is a *spectacular
  PARTIAL*, not a SOUND). Route your own SOUND-claims back through this question.
- **Check the seams between instances.** If the agent who wrote the DAG is not the agent who ran
  the checks (or proposed the claim): did the executor inherit a mis-formalized leaf and run it
  faithfully — *confidently wrong by construction*? Did each soundness label, assigned by the
  decomposer, survive contact with what the executor actually ran? The leaf-contract is the
  handoff; if it didn't cold-transfer, that's a finding, not a rounding error.

If the re-audit moves a label, fix it before reporting. (The pass works: in practice it is the
step that catches the shared-assumption cross-check, the under-routed leaf, and the fake-backed
SOUND — *when it is actually run*. So it is not optional.)

**7. Report the verdict — plain words first, residual forward.** Lead with what's open; that's
the payload. The default surface speaks **plain words**, with the formal cells as their labels:

| plain word (default) | formal cell | means |
|---|---|---|
| **PROVEN** | SOUND `(H,H)` | certified both ways (proof / exhaustive / bounded-model-check) |
| **NOT REFUTED** | PARTIAL `(L,H)` | not-yet-refuted — a green suite, evidence, never a proof |
| **STILL JUDGMENT** | FUZZY `(L,L)` | an open judgment no checker resolves |
| **KILL** | DEATH (s_death=H) | refuted by a hard counterexample (a PARTIAL leaf *can* hard-kill) |

Default rendering:
> **OUTCOME:** PROVEN / NOT REFUTED / STILL JUDGMENT / KILL — in plain words, capped at the
> weakest load-bearing leaf. (A claim that rests on an open judgment leaf is **STILL JUDGMENT**,
> not "proven.")
> **Still open (your to-do list):**
>   - *deferred* — decidable; the decisive check is **named** (e.g. "a Robolectric test on the
>     IO leaf") and just not paid for yet. Each carries its **promotion path** — the exact check
>     that upgrades the leaf a cell.
>   - *judgment* — a genuine open design/interpretive call, no checker resolves it.
> **Established (proven):** the sound leaves {…} — tag the referent for code (`PROVEN(impl)` =
> "the code realizes the spec" vs `PROVEN(model)` = "the spec is right").

Keep the raw `(s_pass, s_death)` pairs and the 4-cell matrix for the **formal mode** — surface
them only when the user elected the formal vector up front (step 1; good for research papers /
formal reviews). The headline is **never "verified ✓"** off a green suite — it's "NOT REFUTED,
capped at the weakest load-bearing leaf, with {the open set} still to do."

## Instance boundaries (who does what)

The verifier should not be the proposer. When the work is split across agents, name the roles —
and the **self-disprove pass (step 6) audits the seams between them**:
- **Proposer** — states/elects the claim or target. (Must differ from the verifier — the
  ownership-reset; a proposer verifying its own claim re-imports the bias the method exists to
  shed. This is also why a *generated* target gets the closure-guard in step 1.)
- **Decomposer** — writes the DAG: leaves, structure, soundness labels. Its output is a set of
  **cold-evaluable leaf-contracts** — that's the test of whether decomposition is done.
- **Executor** — runs the checks, reports `realized` vs `achievable`. May be a different agent;
  it runs the contracts, and a contract it can't run cold wasn't atomic.
- **Disprover** — runs the re-audit (step 6). Strongest when it shares none of the proposer's or
  decomposer's context.

In the single-agent case all four collapse into one instance — but step 6 still asks the same
questions of itself.

## Honest bounds (carry these — they are the method, not a disclaimer)

- Decomposition doesn't remove the trust boundary; it **shatters it into N leaf-contracts.**
  Misformalize a leaf and you're *confidently wrong by construction* — so state each leaf
  cold-evaluable.
- A green check (tests pass, types clean) **never certifies truth** — it's PARTIAL, *not-yet-
  refuted*. Do not report a passing suite as a PASS.
- `SOUND(impl)` is not `SOUND(model)`. The cheapest, most decisive checks live on the impl
  referent — which is exactly why they're the easiest to over-read.
- Where no sound checker exists for a load-bearing leaf, the deliverable is **naming the
  irreducible residual + the promotion path** (the property-test or analysis that would move
  it up a cell), not manufacturing false soundness.
- The soundness labels are themselves a judgment — be honest about who called a checker "sound,"
  and run them through the self-disprove pass.

## Scope

This skill is **verify-mode** only: it checks a claim that has already been made. (The same
decomposition can run in reverse to *generate* a research program from a claim you want to
establish — that mode is intentionally out of scope here.)

See `examples/refactor_claim.md` for a worked code example, and
`diagrams/two-axes-schematic.dot` (render with Graphviz `dot -Tsvg`) for the picture.
