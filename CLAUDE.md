# CLAUDE.md — orientation for agents working in this repo

## What Warrant is

Warrant is a method for checking a load-bearing claim. You break the claim into a graph of leaves
(AND/OR nodes). Each leaf goes to the soundest checker available for it and gets a directional
soundness pair `(s_pass, s_death)`: SOUND `(H,H)`, PARTIAL `(L,H)`, WITNESS `(H,L)` or FUZZY `(L,L)`.
The verdict is composed back up the graph with min/max rules that are exact duals. The output is
honest about what is proven, what is only not-yet-refuted, and what is still a judgment. The
FUZZY residual is shipped as a to-do list, not hidden.

The method is described three ways: `METHODOLOGY.md` (human-facing), `skill/warrant/SKILL.md`
(the model-facing Claude skill) and `code/warrant.py` (a runnable reference implementation). The
compose algebra is machine-checked in `lean/` (all N) and `tla/` (exhaustive to arity 8).

## Layout

| path | what is there |
|---|---|
| `README.md` | human intro, when to use it and when not, the escalation path |
| `METHODOLOGY.md` | the full method: actors, generate/disprove split, the graph (§3), the disprove ladder (§4), how the two axes compose (§5), walkthrough (§6), float rule (§7), honest bounds (§8) |
| `skill/warrant/` | the Claude skill: `SKILL.md` (YAML frontmatter `name`/`description`, then the 7-step procedure), `README.md` (user-facing), `examples/refactor_claim.md`, `diagrams/` |
| `cases/` | worked examples on public papers (see below); `cases/README.md` holds the ground rules, the shared template and the index table |
| `code/` | `warrant.py` (pure-stdlib algebra), `self_verify_*.py` (the method run on its own code), `SELF_VERIFICATION.md` (that case, written up), the cross-lineage prompt and its dated verbatim reply |
| `lean/` | Lean 4 + Mathlib proof of the compose algebra for all N: `Warrant/Basic.lean` (definitions and theorems), `Warrant/Axioms.lean` (`#print axioms` on every theorem) |
| `tla/` | TLA+ model of the single-node compose (`Warrant.tla`, harness `WarrantMC.tla`, config `WarrantMC.cfg`) |
| `diagrams/` | `two-axes-schematic.dot` (Graphviz source; there is an identical copy in `skill/warrant/diagrams/`) |

`METHODOLOGY.md` links `diagrams/two-axes-schematic.svg` and mentions a `CITATION.cff`. Neither
file is in the repo; only the `.dot` source exists.

## Cases

- **Filename:** `cases/case_NN_<slug>.md` for numbered cases (`case_01_gw150914.md`, …). The
  catch-demo, where the method catches a documented bad leaf, is `case_retracted_<slug>.md`.
- **Structure (every case file follows this):**
  1. `# Case NN — <Paper short name>: <topic> (<domain>)`
  2. `**Paper (cite-only):**` with authors, year, venue, DOI and/or arXiv id; then
     `**Source a reader can pull:**` naming the public data or code.
  3. The blockquote `> This case ships the DAG analysis and cites the paper; it reproduces none of
     the paper's text.`
  4. `## The load-bearing claim`: the claim in italics, then why it is a good case for the method.
  5. `## The verification graph  \`root = AND(L1, …)\``: a table with columns
     `leaf | sub-claim | cell (s_pass,s_death) | checker | a reader can…`. The catch-demo uses
     `verdict` for the last column.
  6. `## The vector read-out`: a fenced block with `VERDICT: …`, then `SOUND-realized`, any
     `PARTIAL`/`WITNESS`/`moot` sets, and `FUZZY residual (to-do)`.
  7. `## What the method surfaces`: the prose lesson.
- **Ground rules (from `cases/README.md`):** cite-only (never reproduce paper text), name a leaf a
  reader can re-run, and resolve every DOI and arXiv id against Crossref, arXiv or DataCite instead
  of trusting memory.
- **Adding a case:** put the file in `cases/` and add a row to the table under `## The set` in
  `cases/README.md`.

## Building and running

**Lean** (`lean/`). The toolchain is pinned in `lean/lean-toolchain` (`leanprover/lean4:v4.31.0`).
Mathlib is required at tag `v4.31.0` in `lakefile.toml` and locked to a commit in
`lake-manifest.json`. You need [`elan`](https://github.com/leanprover/elan).

```sh
cd lean
lake exe cache get     # prebuilt Mathlib .oleans
lake build             # clean exit + the #print axioms lines = verified
```

A good build prints only `[propext, Classical.choice, Quot.sound]` (or no axioms) for each
theorem, never `sorryAx`. `lean/.lake/` is gitignored. The last recorded build attempt is in
`lean/BUILD_RECEIPT.md`. In a sandbox, elan needs to reach `release.lean-lang.org` to fetch the
toolchain.

**Python** (`code/`, stdlib only; all four were run from the repo root and passed):

```sh
python3 code/warrant.py --self-test      # offline checks of the whole algebra
python3 code/self_verify_graph.py        # the method's verdict on its own code
python3 code/self_verify_enumeration.py  # 310 compose cases vs an independent oracle
python3 code/self_verify_probes.py       # 27 adversarial probes
```

**TLA+** (`tla/`): needs a JRE and `tla2tools.jar`; see `tla/README.md`.

## Conventions visible in the files

- **Directory READMEs** start with ``# `dir/` — <what it is>``, then say what is checked, the
  result, `## Reproduce` commands, and an `## Honest scope` section saying what is *not* covered.
  `lean/README.md` and `tla/README.md` also record their judgment calls.
- **Vocabulary is fixed.** The cells are SOUND / PARTIAL / WITNESS / FUZZY, written with the pair,
  e.g. `**PARTIAL `(L,H)`**`. Verdicts are PASS / DEATH / PENDING. In plain-language reports they
  become PROVEN / NOT REFUTED / STILL JUDGMENT / KILL. For code claims the referent is tagged:
  `SOUND(impl)` vs `SOUND(model)`.
- **Graph shape is enforced.** Every OR node needs a closure-leaf. A decomposed root is an AND with
  a faithfulness-leaf, and an OR root is wrapped as `AND(faithfulness-leaf, OR(…))`.
  `Graph.validate` in `warrant.py` rejects graphs that break these rules.
- **Receipts** are recorded as:
  - `realized` kept separate from `achievable` in the leaf contract, with gaps marked
    `cost-deferred`, `in-principle` or `contained(...)`;
  - the leaf contract's `verdict:` field, which carries who ran it and when;
  - reproduce commands next to every result, so the result can be re-emitted
    (`#print axioms`, TLC output, the enumeration counts);
  - dated provenance files that keep an external reviewer's reply verbatim, followed by a
    per-finding **Disposition** (REAL → FIXED / FALSE POSITIVE). See
    `code/cross_lineage_review_2026-06-23.md`.
- **Honest scope is part of every artifact.** Each result says what it does not establish.
  Residuals are named, not hidden.
- **Prose style:** Markdown with bold for key terms, italics for claims, and em-dashes. Except for
  the top-level `README.md`, `.md` files are hard-wrapped at about 100 columns (table rows are
  not). Lean sources use `/-! … -/` module docs listing
  modeling decisions. Python scripts start with a shebang and a module docstring.
- **Git:** `main` is the default branch. Existing commits have short imperative messages.
