# Case 02 — ResNet: deep residual learning (machine learning / computer vision)

**Paper (cite-only):** *Deep Residual Learning for Image Recognition.* K. He, X. Zhang, S. Ren, J.
Sun, 2016. **CVPR 2016, pp. 770–778.** DOI [`10.1109/CVPR.2016.90`](https://doi.org/10.1109/CVPR.2016.90)
· arXiv:1512.03385.
**Source a reader can pull:** official code + pretrained models (github.com/KaimingHe/deep-residual-networks);
ImageNet and CIFAR-10 are standard public datasets.

> This case ships the DAG analysis and cites the paper; it reproduces none of the paper's text.

## The load-bearing claim

*"Residual connections let very deep networks (up to 152 layers) train and improve accuracy; an
ensemble reaches 3.57% top-5 error on ImageNet, winning ILSVRC-2015."*

This is the case for the method's central caution: **a green benchmark proves "no known failing
case," not correctness.** ML accuracy claims live almost entirely in the **PARTIAL** cell — and the
graph shows exactly where the one genuinely sound leaf is, and where it stops.

## The verification graph  `root = AND(L1, L2, L3, L4)`

| leaf | sub-claim | cell `(s_pass,s_death)` | checker | a reader can… |
|---|---|---|---|---|
| **L1** | the *released model* scores the reported error on the *fixed* public test set | **SOUND `(H,H)`** | a deterministic, exhaustive evaluation over the fixed val set — no sampling | run the released weights on ImageNet val and get the number exactly |
| **L2** | the result **reproduces from scratch** (training reaches the claimed band) | **PARTIAL `(L,H)`** | re-train; a wildly-off rerun is a real counterexample, a close one is *not-yet-refuted* (GPU non-determinism forbids a bit-exact certificate) | re-train and check the band (compute-heavy but real) |
| **L3** | the gain is **caused by residual connections** (not depth/params alone) | **PARTIAL `(L,H)`** | the paper's own plain-vs-residual ablation; a failing ablation refutes, a passing one supports | re-run the ablation |
| **L4** | the method **generalizes** / "a better way to build networks" | **FUZZY `(L,L)`** | interpretive significance — no decidable checker | — (climbs the ladder; history has since supported it, but that is judgment, not proof) |

## The vector read-out

```
VERDICT: PASS (the benchmarked claim is not refuted), pass-strength CAPPED by L2/L3 (PARTIAL) and L4 (FUZZY)
  SOUND-realized      : {L1}        ← the number on the fixed test set is exact and re-checkable
  PARTIAL (not refuted): {L2, L3}   ← reproducibility + the residual-causes-it attribution
  FUZZY residual (to-do): {L4}      ← "this is the better architecture" is judgment, not proof
```

## What the method surfaces

There **is** a sound leaf here — L1, evaluating the fixed released model on the fixed test set, is a
genuine `(H,H)`: a reader gets the exact number. But the *load-bearing scientific claim* — that
residual learning is a better way to train deep networks — rests on L2 and L3, which are **PARTIAL**:
a green result is "no known failing case," and a passing ablation supports without certifying. The
method's value is refusing to let L1's exactness ("we hit 3.57%") launder into a soundness the
general claim doesn't have. The honest read of almost every ML benchmark result is **PARTIAL with a
FUZZY significance leaf** — which is exactly the gap that "tests passed → it's safe" papers over.
