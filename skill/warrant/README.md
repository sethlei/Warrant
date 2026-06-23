# Warrant — a claim-checking skill (alpha)

A Claude skill that **rigorously checks a load-bearing claim** instead of eyeballing it. It
decomposes the claim into a graph of sub-claims, routes each one to the soundest checker that
actually exists for it (running the checks it can — type-checker, tests, property tests),
**re-audits its own verdict for where it overclaimed**, and returns a result that stays
**honest about what's proven vs merely not-yet-refuted vs still open**. Its signature move: it
will *not* tell you "verified ✓" just because the tests pass.

## How to use it

Once installed, just ask Claude to check a high-stakes claim — the skill triggers on
claim-verification requests. Concrete load-bearing claims it's built for:

- *"Verify that this refactor preserves behavior."*
- *"This migration cannot lose data — check it."*
- *"This visibility/schema change is backwards-compatible."*
- *"This admin/permissions change doesn't expose controls to normal users."*
- *"Is it safe to ship this deployment? Decompose it."*
- *"This analytics/reporting number is correct."*
- *"After the Codex/Cursor-generated edit, does the pipeline still respect the same constraints?"*

A good trigger in the wild: a reviewer says *"looks safe"* and you want to know **what that
rests on.** Skip it for tiny/one-line/throwaway changes — it's an elected burden, not a tax.

It works best on **code claims** (where leaves map to runnable checks), but the method is
general. On code it keeps two things apart that usually get blurred: *"the code realizes the
spec"* (`SOUND(impl)`) is a different claim from *"the spec is right"* (`SOUND(model)`).

## What you'll get back

Not a checkmark — a verdict that **leads with what's still open**:

> **Bottom line** in plain words (not proven / not-yet-refuted / refuted), capped at the
> weakest load-bearing leaf · **the open set as a to-do list** — split into *cost-deferred*
> (decidable, the decisive check is named, with a concrete **promotion path** to make the leaf
> stronger) vs *judgment* (a genuine open call) · then what was actually **established soundly**.

If you want the full formal `(s_pass, s_death)` vector (handy for research papers / formal
reviews), say so up front and it'll render that instead.

See `examples/refactor_claim.md` for a full worked example, and `SKILL.md` for the method itself.
(`diagrams/two-axes-schematic.dot` renders the picture with Graphviz: `dot -Tsvg`.)

## This is an alpha — feedback wanted

Especially helpful to hear:
- Did it **trigger** when you expected it to (and stay quiet on throwaway claims)?
- Was the **decomposition** useful — did it surface a non-obvious binding leaf, or feel rote?
- When something *was* wrong, did it **catch it and say so** — or did it wave a claim through?
  (The honest gap we most want tested: it's good at confirming; how sharp is it on a real miss?)
- Did the **verdict** read clearly with the residual up front, or still feel too heavy?
- Did it actually **run the checks** it could — and did the self-disprove pass catch any place
  it had overclaimed (a shared-assumption cross-check, a fake-backed "SOUND")?
- Where did it feel like ceremony vs. real signal?

Thanks for kicking the tires.
