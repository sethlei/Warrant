# `cases/` — worked examples on public papers

Each case applies the method to a **real, public, citable** result, so a reader can pull the same
source and re-run a leaf for themselves. The point is not to re-grade famous papers — it is to show
the method **separating "proven" from "not refuted" from "still judgment"** on claims whose stakes
are real, and turning the residual into a to-do list.

## Ground rules (so the cases are trustworthy)

- **Cite-only.** Every case ships *our DAG analysis* and cites the paper by DOI. We reproduce **no**
  paper text — this sidesteps licensing entirely and keeps each case to the part that is ours: the
  decomposition.
- **Reproducible.** Every case names a leaf a reader can actually re-run, and the public source
  (data/code) to pull. Where a leaf is only checkable in principle, we say so.
- **Identifiers resolved.** Every DOI / arXiv id below was resolved against Crossref / arXiv /
  DataCite, not trusted from memory (machine-emitted identifiers are wrong often enough that
  resolving them is part of the method, not an afterthought).

## The shared template

Each case file carries: the **paper** (cite-only) → the **load-bearing claim** → the **verification
graph** (leaves, each with its cell `(s_pass, s_death)`, its checker, and what a reader can run) →
the **vector read-out** (verdict + the SOUND-realized set + the FUZZY residual = the to-do list) →
**what the method surfaces.** The catch-demo additionally carries the **documented bad leaf** and
the public ground truth it is checked against.

## The set

| # | case | domain | what it teaches | reader-re-runnable leaf |
|---|---|---|---|---|
| 01 | [GW150914](case_01_gw150914.md) | physics | one sentence, three claims of different soundness; detection is SOUND (permutation-null), the source-model is FUZZY | re-run the time-slide background on public strain data |
| 02 | [ResNet](case_02_resnet.md) | ML / CV | an accuracy claim is **PARTIAL**, not SOUND — a green benchmark is "no known failing case" | re-train and check the claim band; run the plain-vs-residual ablation |
| 03 | [Card–Krueger](case_03_card_krueger.md) | economics | a re-computable **SOUND** arithmetic leaf vs a **FUZZY** causal-identification leaf (parallel trends) | re-compute the difference-in-differences on public data |
| catch | [Reinhart–Rogoff](case_retracted_reinhart_rogoff.md) | economics | the DAG **catches a documented bad leaf**: a SOUND arithmetic cell that *dies* on a spreadsheet error, checked against the public re-analysis | re-compute the average over the full data; watch −0.1% become +2.2% |

**Plus a self-referential case (ships with the code):** the method run against **its own reference
implementation** — see [`../code/SELF_VERIFICATION.md`](../code/SELF_VERIFICATION.md). The release is
itself a load-bearing claim ("this code faithfully implements the method"), so the method is run on
it; several leaves promote to SOUND by exhaustive enumeration, and the faithfulness-to-the-prose leaf
stays FUZZY — that honest residual is shipped, not hidden. It is the strongest worked example in the
set precisely because it is the method applied to itself.

## Cell coverage

Across the set the four cells all appear, and — deliberately — the cases lean on the **PARTIAL** and
**FUZZY** leaves (ResNet, Card–Krueger, GW150914's source-model) as much as the SOUND ones. The
method earns its keep exactly where "tests passed" tempts you to stop, so the cases are chosen to
show that boundary, not just to show off clean wins.
