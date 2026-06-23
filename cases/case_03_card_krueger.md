# Case 03 — Card–Krueger: minimum wage and employment (economics)

**Paper (cite-only):** *Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New
Jersey and Pennsylvania.* D. Card, A. B. Krueger, 1994. **American Economic Review 84(4): 772–793.**
*(The 1994 AER article predates AEA DOI assignment; cite via* AER 84(4):772–793 *and the working
paper* NBER WP 4509, DOI [`10.3386/w4509`](https://doi.org/10.3386/w4509)*.)*
**Source a reader can pull:** the replication data + paper PDF on David Card's Berkeley site
(davidcard.berkeley.edu).

> This case ships the DAG analysis and cites the paper; it reproduces none of the paper's text.

## The load-bearing claim

*"New Jersey's 1992 minimum-wage increase did not reduce — and if anything raised — fast-food
employment, relative to neighboring Pennsylvania."*

This is the case for the method's sharpest move in empirical work: **separating a re-computable
arithmetic leaf from the untestable causal-identification leaf** — and naming the second as the
binding constraint, which is precisely where the decades-long debate actually lives.

## The verification graph  `root = AND(L1, L2, L3)`

| leaf | sub-claim | cell `(s_pass,s_death)` | checker | a reader can… |
|---|---|---|---|---|
| **L1** | the difference-in-differences estimate is **computed correctly** from the survey data | **SOUND `(H,H)`** | an arithmetic re-computation on the public data — both "right" and "wrong" are decidable | re-compute the DiD from the replication file |
| **L2** | the estimate is **statistically distinguishable** from a zero/negative effect | **SOUND/PARTIAL** | a randomization-inference / permutation test over treatment assignment makes the no-effect null SOUND | re-run the permutation test |
| **L3** | **parallel trends holds**, so the DiD is **causal** (NJ would have tracked PA absent the policy) | **FUZZY `(L,L)`** | the identifying assumption is untestable — judgment; later payroll-data critiques attack exactly here | — (climbs the ladder; this is the binding leaf) |

## The vector read-out

```
VERDICT: PASS (the measured effect is real and correctly computed), pass-strength CAPPED by L3
  SOUND-realized      : {L1, L2}   ← the difference-in-differences number is what it is, on public data
  FUZZY residual (to-do): {L3}      ← parallel-trends / causal identification — the binding constraint
```

## What the method surfaces

The arithmetic (L1) is **SOUND** and re-runnable: the measured difference-in-differences is not in
dispute. What carries the *causal* weight — "the minimum wage didn't cost jobs" — is **L3**, the
parallel-trends assumption, which is **FUZZY** by construction (you cannot observe the
counterfactual). The famous Card–Krueger ↔ Neumark–Wascher controversy is a fight over **L3**, not
**L1**: a disagreement about identification, not arithmetic. That is the method's gift here — it
locates the binding constraint, so the argument happens at the leaf where the uncertainty actually
is, instead of being smeared across the whole claim. The FUZZY residual *is* the research frontier.
