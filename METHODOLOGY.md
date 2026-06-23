# A verification methodology for load-bearing claims
### (human-facing exposition — a model-facing operational version ships alongside)

*Decide how much to trust a high-stakes claim by **decomposing it into a graph** and routing
each node to the soundest checker that exists for it — then climbing, with independent judges,
only the residual that no sound checker can reach.*

## What this is (plain)

Most verification is a single fuzzy judgment — "does this hold up?" — from one evaluator. That
floor is **unsound**: a confident evaluator who is wrong leaves no trace, and adding more
evaluators makes you *more confident*, not more *correct*. This method separates the two things
that get conflated there:

- **Soundness** — *how the claim is structured for checking.* A graph: break the claim into
  atomic sub-claims, route each to the soundest available checker, compose the verdict back up.
- **Variance** — *who checks a judgment, and how independent they are.* A ladder of evaluators
  for the pieces that bottom out in judgment and have no sound checker at all.

It is **not** a gate every idea must pass — that would strangle exploration. It is a **burden of
proof you elect**, once a claim is load-bearing enough to invest in *as a system*. Below that
threshold nothing changes; exploration runs free. And it is **substrate-general**: "the author"
below is a human or a model — the bias it engineers around is just *motivated reasoning*, which
both have.

> **The shape in one picture:** the claim at the top decomposes into a graph; leaves are
> color-coded by how soundly they can be checked (green/blue/tan/red); the red **fuzzy** leaves —
> the ones no sound checker reaches — are the only ones that climb the judge-ladder. See
> [`diagrams/two-axes-schematic.svg`](diagrams/two-axes-schematic.dot).

## Actors (roles, not people)

| role | what it does |
|---|---|
| **the author** | produces the claim; attached to it *by design* (a human or a model; the maker role is preserved, not engineered away) |
| **the disprover** | a **different instance** than the author; runs this method. The instance boundary is the ownership-reset |
| **an independent reviewer** | a separate party that audits the disprover's grades; *external but not blind* — a check, not the terminus |
| **a blind judge** | a party that shares nothing with the author — the *none-of-us* backstop for load-bearing judgment calls |
| **a cross-lineage checker** | a checker with maximally different priors (a different training/discipline) — breaks shared-assumption correlation |
| **the principal** | the human who *elects* the burden of proof and is the final human-in-the-loop floor |

---

## 1. The bias it engineers around

Authors **cling to claims they own** and **drop others' freely**. The asymmetry is
*magnitude-graded by investment*, not binary: cheap throwaway hypotheses are dropped cleanly;
expensive, identity-adjacent ones cling. Naming the bias does not cure it — an author who *knows*
the tell still leaks it (e.g., letting their preferred answer shape the very test meant to check
it). The fix is structural, and it gates on **load-bearing claims only** — never a blanket tax on
hypothesizing.

## 2. The generate / disprove split

Don't fight the bias *during* generation — that fights the author's strength. Split the two modes
**by instance**, each with its own success criterion:

- **GENERATE — unencumbered.** The author produces the claim and may go all-in making it right,
  with **no self-disproof tax in the same session.** Success = the strongest case made. This
  keeps the author as **co-inventor**; the bias-fix must not cost the maker-role.
- **DISPROVE — a different instance + the method below.** A **different instance** — not the one
  that made the claim — runs the verification. At the boundary the claim arrives as *someone
  else's*, so "drop others' freely" fires and "cling to my own" never gets the chance. **The bug,
  flipped into the engine.**
- **Rule:** never produce-and-disprove a *load-bearing* claim in the **same session.**
  Magnitude-gated; cheap hypotheses exempt.

Generation stays unencumbered precisely *because* the verification graph below makes a sound
floor that discards wrong candidates cheaply — **you earn the aggression by building the floor.**

---

## 3. The verification graph — the soundness axis

This is the spine. At the election point, before the claim reaches any judge, **decompose it into
a graph.**

**Nodes and edges.**
- **Leaf** = an atomic sub-claim, a definition/axiom the claim rests on, or the falsifier.
- **Edge** = a dependency (B rests on A).
- **AND-node** = all children necessary. **OR-node** = alternatives (prove via X *or* Y).
- An **OR-node requires a closure-leaf**: "are these alternatives exhaustive?" — almost always a
  judgment, and the place an eliminative argument hides an unstated exhaustiveness assumption.
  This is a hard requirement, not advice: a graph whose OR lacks a closure-leaf is **rejected**,
  not warned-and-composed — fix the claim, don't compose around it.
- The **root carries a faithfulness-leaf**: "does this decomposition actually encode the claim?"
  The causal model the graph asserts is itself a checkable (usually fuzzy) leaf, not free truth.
  Faithfulness is a *necessary* condition on the whole claim, so it ANDs with the decomposition:
  a decomposed claim's root is an **AND** carrying an explicit faithfulness-leaf — a top-level OR
  must be wrapped as `AND(faithfulness-leaf, OR(...))`. A decomposed claim with no
  faithfulness-leaf is **rejected**: you cannot verify a decomposition you won't vouch encodes the
  claim. (Both requirements are enforced at the graph's recognition boundary — a malformed graph
  fails loudly so the *author* fixes the claim, the same discipline the method asks of every leaf.)

**Route each leaf by a directional pair, not a scalar.** A checker's soundness is asymmetric —
it can be trustworthy at certifying *truth*, or *falsehood*, or both, or neither. So every leaf
carries a pair:
- `s_pass` — can this checker certify the claim **true**?
- `s_death` — can it certify the claim **false**?

Four cells:

| cell | `(s_pass, s_death)` | example |
|---|---|---|
| **SOUND** | (H, H) | permutation-null, exhaustive finite enumeration, a bounded model-check, a type guarantee, a formal proof |
| **PARTIAL** | (L, H) | example/property tests — *a failing test is a real counterexample; a green suite never certifies* (Dijkstra) |
| **WITNESS** | (H, L) | an existence/witness proof — certifies TRUE on a found assignment; its absence proves nothing unless exhaustive |
| **FUZZY** | (L, L) | a judgment — novelty, fit, "is this the binding constraint," interpretive faithfulness |

WITNESS is the exact De Morgan dual of PARTIAL; the symmetric algebra *requires* it. The scalar
ordering `SOUND > PARTIAL > FUZZY` omits it and silently loses the verify/falsify asymmetry —
which is where the real bug lives (below).

**Compose up the graph (the combine-rule + its exact duality):**
- **AND-node:** PASS-strength = **min** over children of `s_pass` (weakest link); DEATH-strength
  = **max** over *died* children of `s_death` (any one sufficient death kills the AND — cite the
  best death certificate).
- **OR-node:** PASS-strength = **max** of `s_pass` (the best path certifies); DEATH-strength =
  **min** of `s_death` (all alternatives must die; the weakest death caps it).
- **Duality, exact:** swap `AND↔OR`, `PASS↔DEATH`, `s_pass↔s_death` and it is a symmetry.

**The bug the pair fixes (and the scalar hides).** An AND-node with one SOUND leaf and one
PARTIAL leaf where *the PARTIAL leaf returns DEATH*: the scalar weakest-link rule reads the result
as "PARTIAL = not-yet-refuted" — **wrong**, because a PARTIAL *death* is a genuine counterexample
(PARTIAL is sound in the death direction). The pair gets it: DEATH-strength = max(`s_death`) = H →
real falsification. A clean worked example *hides* this; don't let one clean case ratify the
scalar.

**The leaf-contract (the unit).**
```
LEAF
  claim:      <atomic sub-claim, stated so a stranger can evaluate it cold>
  rests-on:   [leaf-ids]                       # edges
  node-type:  AND | OR                         # OR REQUIRES a closure-leaf
  falsifier:  <death-condition for THIS leaf, fixed BEFORE the check runs>
  checker:    <the instrument: script | proof obligation | measurement | judge>
  soundness:  (s_pass, s_death)  each H|L      # ACHIEVABLE ceiling, per direction
  realized:   (s_pass, s_death) | NONE         # what you actually PAID to run
  deferral:   none | cost-deferred(<why>) | contained(<Lx via SOUND|FUZZY edge>)
  verdict:    PASS | DEATH | PENDING  (+ who ran it, when)
```
**Stopping rule for "how atomic":** decompose until every leaf is either checkable in at least one
direction or an irreducible FUZZY judgment — no further. *A `(L,L)` leaf with no narrower checker
is the honest residual **and** the next investigation target — naming it is the point, not a
failure.*

**Compose on `realized`, not `achievable`.** Trust is what you actually paid to check. Any gap —
a leaf that *could* be SOUND but was run cheaper for budget — is surfaced **loudly** as
`cost-deferred`, never silently rounded up. Three reasons a leaf is un-realized, and the leaf says
which: **cost-deferred** (recoverable — pay later to close it), **in-principle** (achievable
itself < SOUND — the real residual / investigate-signal), and **contained** (an upstream leaf
died, so building this one is moot). *A containment carries the soundness of the edge it runs
through:* containment through a SOUND death is a hard kill; containment through a FUZZY edge is a
**cost-win that forfeited an independent hard route** — log it as such, never as a hard kill.

**Containment + independence.** Invalidate a leaf and the graph localizes the blast: transitive
dependents are dirtied. But evidence also flows through **shared leaves and shared OR-parents** —
so "independent" means **no shared leaf AND no shared alternative-parent**, not merely "no
dependency path." Under that definition, genuinely independent subtrees are contained, and the
graph tells you *before you spend* which claims are load-bearing on the weakest leaf — i.e., where
to put the checking budget.

## 4. The disprove ladder — the variance axis (for fuzzy leaves only)

A FUZZY leaf has no sound checker in either direction. You cannot make it sound — but you can
reduce the *variance* of the judgment by routing it up a ladder of increasing independence:

**author → independent reviewer → fresh clean instance → cross-lineage checker → human + experiment.**

Each rung adds an evaluator less correlated with the last. Two disciplines keep it honest:
- **Verifiable channels only.** A rung counts only if you can read its full input. An evaluator
  with hidden shared state gives *correlated* votes wearing the costume of independence — false
  consensus. Transparency *is* the independence guarantee.
- **The strongest rung is the most-different checker.** Zero shared priors (a different
  discipline; in the limit, someone who can't see the problem at all) is the purest falsifier.
  Surviving it is a stronger result than surviving an evaluator who shares your assumptions.

Load-bearing judgment calls are **blind-backstopped**: the deciding question goes to a party that
shares nothing — its *blindness*, not its cleverness, is the guarantee.

**The ladder reduces variance; it cannot make a fuzzy verdict sound.** A FUZZY leaf that climbs
all five rungs is **still `(L,L)`** — you are more *confident* in the judgment, not more *correct*.
The graph enforces this: a five-rung-agreed FUZZY death enters its AND-node as `s_death = L`, a
**soft** death (a judgment flipped), never a hard kill, no matter how many rungs concurred.

## 5. How the two axes compose

They are orthogonal **because they move different quantities** — the graph sets *soundness*, the
ladder reduces *variance*. **Confidence/soundness = vertical/horizontal = the same wall.** Two
places not to let the wall leak:

- **An experiment is a *checker*, not a ladder rung.** The first four rungs are all fuzzy
  evaluators (pure variance reduction; the leaf stays `(L,L)`). But a pre-committed empirical test
  is at least PARTIAL, often SOUND — it moves the leaf's *cell* `L→H`. So an experiment is not a
  rung at all; it is the gradient-push that **re-routes the leaf to a new checker** (a soundness
  move on the graph). Keep *human judgment* on the ladder; lift *experiment* onto the graph.
- **The two axes use different combinators; never swap them.** Leaves stack by **min/max** on
  `(s_pass, s_death)` (soundness). Independent judges of one leaf stack by **consensus/escalation**
  (variance). The compose is clean precisely because the ladder first collapses N judges into one
  `(L,L)` leaf-verdict, which *then* enters min/max as a single leaf. Forbidden: "this reviewer is
  more sound than that one, take the max" — the rungs are *equi-sound* (all `(L,L)`); they differ
  in *independence*, not soundness.

*(One tag to carry — and make it **directional**, or it reintroduces the scalar conflation the
pair exists to kill: a conservative ladder — "default-down on doubt" — biases toward rejection, so
its verdicts are asymmetric. A fuzzy **DEATH** off a reject-biased ladder is **weaker** than face
value — it may be the bias talking, not a real refutation — so discount the **death-direction**; a
fuzzy **PASS** that survives it is **stronger** (hard-won against the rejection bias), not weaker.
For a disprove tool the death-direction discount is the one that earns its keep: the dangerous
failure is a reject-biased ladder's cheap soft-DEATH killing a good idea.)*

## 6. A grounding walkthrough

Take a load-bearing claim — *"intervention X causes outcome Y."* Elect the burden; decompose:

- **L1 — "the effect is not noise."** Checker: a permutation-null over matched random labelings.
  `(H,H)` **SOUND**. Run it. Verdict: the observed effect sits inside the 95% band of the null →
  **DEATH**. *Hard.* (This single sound leaf can settle the whole claim — and a fuzzy whole-claim
  intuition that "X clearly beats the alternatives" would have shipped it. Find the sound
  leaf-checker **before** reaching for a judge.)
- **L2 — "the effect holds out-of-sample."** Checker: a property test over held-out slices.
  `(L,H)` **PARTIAL** — a failure is a real counterexample; passing is only *not-yet-refuted*.
- **L3 — "a mechanism exists that could produce it."** Checker: exhibit one. `(H,L)` **WITNESS** —
  a found mechanism certifies possibility; not finding one proves nothing.
- **L4 — "this mechanism is the *binding* one (not a confound)."** No decidable checker. `(L,L)`
  **FUZZY** → climbs the ladder; blind-backstopped; stays a soft verdict.

The composed read is not a single number but a **vector**: *"DEATH at L1 (s_death = H, hard) — the
claim is falsified on a sound leaf; the rest is moot (contained via a SOUND edge). Had L1 passed:
PASS-strength capped by L2's PARTIAL and L4's FUZZY; SOUND-realized on {L1}; the FUZZY set {L4,
closure} is both the residual and the next-investigation list."* That last clause is the point —
**the method's output is also a to-do list.**

## 7. The float rule (a sub-case: numerical deaths on continuous claims)

When a leaf is a *numerical* check on a *continuous* claim, a computed "death" is a **flare, not a
kill**, until it is certified as **separated from the controlling floor**. Two floors:
- **precision/cancellation** — an error bound certifies the death; tightening precision tightens
  it.
- **discretization** — *no* error bound is achievable at any precision; only **analytic structure**
  certifies. **Diagnostic gate:** bump the precision (e.g. double→quad). *Invariance* means you are
  at the discretization floor → the error bound is the wrong instrument; escalate to analysis.

Density/pointwise statements sit at the discretization floor by construction (default to flare);
cumulative/integral statements integrate the floor down and can carry a kill. And **every flare
must name an achievable promotion-to-kill condition** — the bound or the analytic fact that would
make it a kill — or it is an un-killable lens, not a result. (In graph terms: a numerical leaf is
`(L,L)` for the *sign* at the discretization floor and must be **re-routed to an analytic
checker** — a §5 cell-change, not another vote.)

## 8. Honest bounds (these are the method, not a disclaimer)

- **"Properly" carries enormous load.** Decomposition does not *remove* the trust boundary — it
  *shatters* it into N leaf-contracts. Misformalize a leaf and you are *confidently wrong by
  construction*, and harder to catch (clean composition on a rotten foundation). The win is the
  trade: many small checkable units beat one opaque whole — but each contract must be validated,
  which recurses to *who validates the leaf-contracts* (why definitions/axioms are pinned as
  explicit contracts — that's where the recursion bottoms).
- **Trees assume independence; real claims share sub-claims** — hence a **DAG with shared leaves**,
  and the containment definition above.
- **Where no sound checker exists**, the value is **naming the irreducible residual**, not
  manufacturing false soundness.
- **The soundness labels are themselves a fuzzy meta-leaf.** Who calls a checker "sound"?
  Mislabeling is the failure mode one level up — so the labels live in the disprove-pass and bottom
  at the same human-in-the-loop. The label does not self-certify.
- **It validated itself by catching an error in its own first application.** On its first real use,
  the layered blind-check caught a mistake the first pass had made — a hard premise-death mislabeled
  as a hard conclusion-death, when the inference actually ran through a fuzzy edge. A method whose
  first act is to catch its own author's error is evidence worth more than a clean demo.

## 9. Worked examples

Reproducible analyses on **public papers** — including a **retracted** one, where the documented
retraction is the ground truth the method's "caught the bad leaf" verdict is checked against. See
[`cases/`](cases/README.md). Public and citable so a reader can re-run the method against the same
source; no unverifiable internal work is used as evidence.

---

*License: **Apache-2.0** — explicit patent grant; the method is open, any underlying framework
patent is unaffected. See `LICENSE`. Cite via `CITATION.cff`. A model-facing operational version
(and a drop-in skill) ship alongside this exposition.*
