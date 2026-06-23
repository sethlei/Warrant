# Cross-lineage faithfulness check — the rung-4 promotion of leaf F

`SELF_VERIFICATION.md` certifies the algebra **`SOUND(impl)`** by exhaustive enumeration,
and leaves one honest residual: leaf **F**, *"does the code faithfully capture the prose
intent of the spec?"* — read so far only at **rung 3** (a fresh, same-lineage instance).

This file is the **rung-4** promotion: hand the spec and the code to a **clean-context model
of a different lineage** and have it hunt, adversarially, for divergences. A different
lineage breaks the shared-training / shared-architecture correlation that rung 3 cannot.

## What rung 4 does and does NOT establish (so the result isn't oversold)

- **Breaks:** the shared model-family / shared-memory correlation — a divergence the
  same-lineage author would systematically miss can surface here.
- **Does NOT break:** shared *prompt framing* and shared *literature priors* — both models
  read this prompt and the same public conventions. So a clean result is **corroboration of
  F, not a proof**: it raises confidence, it does not move F out of `FUZZY (L,L)`. (Per the
  method's own rule: the ladder reduces variance, never manufactures soundness.) If it finds
  a real divergence, that is a genuine finding to run down — the point of the exercise.

## How to run it (keep it blind)

1. Open a **fresh conversation** in a clean-context model of a **different lineage** than the
   one that wrote the code.
2. Attach or paste **exactly two files**: `METHODOLOGY.md` and `code/warrant.py`.
   - **Do NOT include `SELF_VERIFICATION.md`, this file, or any of the `self_verify_*.py`
     scripts.** Those carry our answer (and our oracle) — including them defeats the blind
     check by handing the reviewer the conclusion.
3. Paste the prompt below verbatim.
4. Save the reply next to this file; if it flags a divergence, route it to the code as a real
   finding. If it finds none after a thorough read, record it as the rung-4 corroboration of F.

## The prompt (paste verbatim)

> You are an independent code reviewer. You share no context with the authors of the material
> below, and you have no stake in the outcome.
>
> You are given two things: (1) a **specification** written in prose, and (2) a **Python
> implementation** that claims to faithfully implement it. Your single job is to find
> **divergences** — places where the code does something the specification does not license, or
> fails to do something the specification requires. Assume divergences exist and hunt for them.
> Only conclude "faithful" if, after a careful read of both, you genuinely cannot find one.
>
> Read the specification first and extract its load-bearing rules in your own words. Then, **at
> minimum**, verify each of the following properties against the code — for each, state whether
> the code MATCHES or DIVERGES, and cite the exact function (and the lines) that decide it:
>
> 1. The four soundness cells: the `(s_pass, s_death)` pair `(H,H)/(L,H)/(H,L)/(L,L)` maps to
>    the four named cells exactly as the spec states.
> 2. AND composition: pass-strength is the **min** of children's pass-strength; death-strength
>    is the **max** of `s_death` over the children that **died** (not over all children).
> 3. OR composition: pass-strength is the **max** of children's pass-strength; an OR dies only
>    if **all** alternatives die, and its death-strength is then the **min** over them.
> 4. The pass↔death duality between AND and OR is exact (the two are mirror images).
> 5. Composition uses **realized** trust (what was actually run), never the **achievable**
>    ceiling, and any gap between them is surfaced explicitly, not silently rounded up.
> 6. A containment (a node made moot by an upstream decision) carries the soundness of the
>    **edge** it ran through — moot via a sound edge vs a fuzzy edge are treated differently.
> 7. A FUZZY `(L,L)` death stays **soft** no matter how many independent judges concurred —
>    agreement increases confidence, never soundness.
> 8. A **split** ladder of judgments escalates to a pending/human-decision state — it never
>    becomes a majority kill or a majority pass.
> 9. The float rule for numerical deaths: a computed death is a "flare," not a kill, until it is
>    certified separated from the controlling floor; the precision-bump-invariance diagnostic
>    routes a discretization-floor case to an analytic checker; a flare with no promotion
>    condition is rejected.
>
> Then give: (a) a table of property → MATCH/DIVERGE → evidence; (b) any divergences you found
> outside that list; (c) an overall judgment — *faithful* or *divergences found*; (d) the one or
> two things you are **least sure about** and why. Be specific and cite code; do not be agreeable.
