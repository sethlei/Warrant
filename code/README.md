# `code/` — runnable reference implementation

A small, dependency-light reference implementation that makes the method **runnable**, not
just described — the "cross-domain viability with code" layer. `warrant.py` runs under any
tool or none; this is the layer a non-Claude user (e.g. another agent, or a human at a REPL)
leans on.

## `warrant.py` — the soundness-axis algebra (zero dependencies)

A faithful, pure-stdlib implementation of the graph algebra in `METHODOLOGY.md` §3–§8:

- the directional-pair leaf contract `(s_pass, s_death)`, each `H` or `L`;
- the four cells **SOUND** `(H,H)` / **PARTIAL** `(L,H)` / **WITNESS** `(H,L)` / **FUZZY** `(L,L)`;
- AND / OR composition with the exact pass↔death duality
  (`AND`: pass `= min` s_pass, death `= max` s_death over *died* children;
   `OR`: pass `= max`, death `= min`, all alternatives must die);
- composition on **realized** trust, never the achievable ceiling — every gap is
  surfaced loudly as `cost-deferred`;
- containment that carries the **soundness of the edge** it runs through
  (death via a SOUND edge = hard kill; via a FUZZY edge = a soft, cost-win);
- a **vector** read-out: verdict + the SOUND-realized set + the FUZZY residual
  (which *is* the next-investigation to-do list), never a single scalar score;
- the **disprove ladder** collapsed into one `(L,L)` leaf (variance reduction that
  can never make a fuzzy verdict sound; a split escalates, never a majority-kill);
- the **float rule** for numerical deaths on continuous claims (flare vs kill, the
  precision-bump diagnostic, the re-route to an analytic checker).

```sh
python3 warrant.py              # the worked walkthrough (METHODOLOGY §6) + 3 more graphs
python3 warrant.py --self-test  # offline checks of the whole algebra
```

The self-test pins the load-bearing behaviors, including **the bug the directional
pair fixes and a scalar score hides**: an AND-node with a SOUND leaf and a PARTIAL
leaf where the PARTIAL leaf *returns DEATH* composes to a **hard kill** (a PARTIAL
death is a real counterexample), not "not-yet-refuted."

## `SELF_VERIFICATION.md` + `self_verify_*.py` — the method run on this code

The release is itself a load-bearing claim — *"this code faithfully implements the
method."* So the method is run on it. `SELF_VERIFICATION.md` is the resulting case, rendered
**two ways** (the practitioner-facing *code template* and the full *formal* `(s_pass,
s_death)` vector): the algebra is certified **`SOUND(impl)`** by an *exhaustive enumeration*
over its finite domain (`self_verify_enumeration.py` — 310 compose cases against an
independent oracle that does **not** call the code's own compose functions), plus 27
adversarial probes (`self_verify_probes.py`). The faithfulness-of-prose-to-code leaf stays
**`FUZZY(model)`** — the honest residual, read at the fresh-instance rung with cross-lineage
+ human rungs named as deferred. The adversarial pass found one real (benign) robustness gap
and **closed it** — the method actioning its own to-do list.

`self_verify_graph.py` makes it **runnable**: it builds the self-verification graph
(`root = AND(L1…L11, F)`) and runs `warrant.py`'s own composer on it, so the tool prints its
verdict *on itself* (`SOUND(impl)`-realized on the nine algebra leaves, capped at FUZZY by
the faithfulness leaf F). Reproduce with the commands at the bottom of that file.

## How this maps to the method

- `warrant.py` is the **soundness axis** (the graph): decompose, route each
  leaf to its soundest checker, compose verdicts back up.
- the **variance axis** (the disprove ladder) reduces noise on a FUZZY leaf by routing it to
  independent judges — `warrant.py`'s `collapse_ladder` composes their votes into one `(L,L)`
  leaf; the blind, most-different judge itself is a manual paste into a clean-context model
  (see `cross_lineage_faithfulness_check.md` for a worked rung-4 instance).

Worked, reproducible end-to-end analyses on public papers live in [`../cases/`](../cases/).
