# Case (catch-demo) — Reinhart–Rogoff: a spreadsheet error in a load-bearing claim (economics)

**Paper (cite-only):** *Growth in a Time of Debt.* C. M. Reinhart, K. S. Rogoff, 2010. **American
Economic Review 100(2): 573–578** (Papers & Proceedings). DOI
[`10.1257/aer.100.2.573`](https://doi.org/10.1257/aer.100.2.573) · also NBER WP 15639, DOI
[`10.3386/w15639`](https://doi.org/10.3386/w15639).
**Status:** *corrected, not formally retracted* (a non-peer-reviewed Papers & Proceedings piece) —
but one of the most thoroughly documented errors in empirical economics, which is what the catch is
checked against.

> This case ships the DAG analysis and cites the paper; it reproduces none of the paper's text.

## The load-bearing claim

*"Above a 90%-of-GDP public-debt threshold, average real GDP growth turns negative (≈ −0.1%)."*

**Why it is load-bearing (stated precisely):** the "90% threshold" became *the* most-cited empirical
justification for austerity during the 2010–2013 European debt crisis — invoked by the European
Commission, by UK and US policymakers. It did **not** by itself cause any country's austerity
(those were driven by bailout conditionality, bond markets, and the crisis itself); it supplied the
**academic cover** that made the policy look like settled science. A trivial error in a claim doing
that much work is the strongest possible argument for running a sound check before believing it.

## The verification graph  `root = AND(L1, L2, L3)`

| leaf | sub-claim | cell `(s_pass,s_death)` | checker | verdict |
|---|---|---|---|---|
| **L1** | the **−0.1% mean is computed correctly** from the dataset | **SOUND `(H,H)`** | an arithmetic re-computation over the *full* country set | **DEATH** |
| **L2** | the 90% point is a **real discontinuity** (not a weighting/exclusion artifact) | PARTIAL/FUZZY | robustness to weighting + country-year exclusions | (moot) |
| **L3** | high debt **causes** slow growth (not reverse causality) | FUZZY `(L,L)` | judgment; slow growth can itself raise the debt ratio | (moot) |

## The catch — the documented bad leaf (ground truth)

The method routes **L1 to a SOUND arithmetic re-computation** — the soundest possible checker — and
says *run the cheapest decisive falsifier first.* Running it kills the claim:

- **The bad leaf:** an Excel averaging range that silently omitted five countries (Australia,
  Austria, Belgium, Canada, Denmark), plus selective exclusions and unconventional weighting.
  Correcting the spreadsheet range, the >90%-debt average growth rises from **−0.1% to +2.2%** — the
  "growth falls off a cliff" finding disappears.
- **Ground truth:** Herndon, Ash & Pollin, *Does high public debt consistently stifle economic
  growth? A critique of Reinhart and Rogoff*, Cambridge Journal of Economics 38(2): 257–279, DOI
  [`10.1093/cje/bet075`](https://doi.org/10.1093/cje/bet075); public replication (UMass/PERI).
  Documented at Retraction Watch
  (retractionwatch.com/2013/04/18/influential-reinhart-rogoff-economics-paper-suffers-database-error/).

So **L1 returns DEATH with `s_death = H`** — a real, sound counterexample on public data. In an
AND-node, one sound death kills the root: the claim is **hard-falsified on a sound leaf**, and L2/L3
(the weighting and causality questions) are **moot — contained via a SOUND edge.**

## The vector read-out

```
VERDICT: DEATH  (s_death = H, HARD) — falsified on a sound arithmetic leaf
  SOUND-realized      : {L1}        ← the re-computation that kills it, re-runnable on public data
  moot via SOUND edge : {L2, L3}    ← you never reach the causal debate; the claim is already dead
  FUZZY residual      : —            ← settled; don't spend here
```

## What the method surfaces

This is the catch-demo, and it is the real-world twin of the methodology's own §6 walkthrough: **a
single sound leaf settles the whole claim, and the rest is moot.** The bad leaf was not subtle — it
was an arithmetic error a five-minute re-computation on public data refutes — and the method's
discipline (*find the sound leaf-checker before reaching for a judge; run the cheapest decisive
falsifier first; contain the blast*) is exactly what would have caught it before the causal arguments
ever mattered. The lesson is not that economists can't use spreadsheets. It is that a claim carrying
that much policy weight earns an elected burden of proof, and the cheapest decisive check — *is the
headline number even computed correctly?* — was sound, available, and skipped.
