# `lean/` build receipt — 2026-09-25

**Outcome: BUILD SUCCEEDED** (attempt 2). `lake build` exited 0 (`Build completed successfully
(8561 jobs).`). Every `#print axioms` line in `Warrant/Axioms.lean` reports only a subset of Lean's
standard `[propext, Classical.choice, Quot.sound]`, or no axioms. **`sorryAx` appears nowhere.** A
grep of `lean/Warrant/` and `lean/Warrant.lean` for `sorry` / `admit` / `axiom` (not counting
`#print axioms`) finds nothing. No `.lean` file was edited.

Attempt 1 failed earlier the same day because of an environment block. It is kept below as a record.

## Attempt 2 — succeeded

| field | value |
|---|---|
| date (UTC) | 2026-09-25, 19:33:22 → 19:36:18 |
| environment | Claude Code cloud session (Linux x86_64 container, outbound HTTPS through an egress-policy proxy), after the network policy was widened |
| repo commit | `ead95cd` (Lean sources unchanged from `main` head `9e4a98f`) |
| elan | `elan 4.2.4 (227caca13 2026-08-25)` |
| toolchain | `leanprover/lean4:v4.31.0`, downloaded from `https://releases.lean-lang.org/lean4/v4.31.0/lean-4.31.0-linux.tar.zst` |
| `lean --version` | `Lean (version 4.31.0, x86_64-unknown-linux-gnu, commit 68218e876d2a38b1985b8590fff244a83c321783, Release)` |
| `lake --version` | `Lake version 5.0.0-src+68218e8 (Lean version 4.31.0)` |
| Mathlib | `inputRev` `v4.31.0`, checked out at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (matches `lake-manifest.json`), cloned from `https://github.com/leanprover-community/mathlib4` |
| `lake exe cache get` | exit 0, **147 s**. Built the `cache` exe (25 jobs), then `Attempting to download 8542 file(s) from leanprover-community/mathlib4 cache` (Azure), `Decompressed 8542 file(s)` |
| `lake build` | exit 0, **29 s**. `Warrant.Basic` 10 s, `Warrant.Axioms` 6.5 s, `Warrant` 6.3 s |
| total wall time | **176 s** |

### `#print axioms` output (verbatim, from `lake build`)

```
✔ [8558/8561] Built Warrant.Basic (10s)
ℹ [8559/8561] Built Warrant.Axioms (6.5s)
info: Warrant/Axioms.lean:8:0: 'Warrant.composeAnd_perm' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:9:0: 'Warrant.composeOr_perm' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:10:0: 'Warrant.composeAnd_multiset_function' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:11:0: 'Warrant.composeOr_multiset_function' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:14:0: 'Warrant.composeAnd_death' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:15:0: 'Warrant.composeAnd_pass' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:16:0: 'Warrant.composeAnd_pending' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:17:0: 'Warrant.composeOr_pass' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:18:0: 'Warrant.composeOr_death' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:19:0: 'Warrant.composeOr_pending' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:20:0: 'Warrant.maxDeath_ge' depends on axioms: [propext, Quot.sound]
info: Warrant/Axioms.lean:21:0: 'Warrant.maxDeath_le' depends on axioms: [propext, Quot.sound]
info: Warrant/Axioms.lean:22:0: 'Warrant.minPass_le' depends on axioms: [propext, Quot.sound]
info: Warrant/Axioms.lean:23:0: 'Warrant.le_minPass' depends on axioms: [propext, Quot.sound]
info: Warrant/Axioms.lean:26:0: 'Warrant.composeOr_eq_dual' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:29:0: 'Warrant.and_soft_death' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:30:0: 'Warrant.or_soft_death' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:33:0: 'Warrant.and_hard_kill' depends on axioms: [propext, Classical.choice, Quot.sound]
info: Warrant/Axioms.lean:36:0: 'Warrant.cell_sound' does not depend on any axioms
info: Warrant/Axioms.lean:37:0: 'Warrant.cell_partial' does not depend on any axioms
info: Warrant/Axioms.lean:38:0: 'Warrant.cell_witness' does not depend on any axioms
info: Warrant/Axioms.lean:39:0: 'Warrant.cell_fuzzy' does not depend on any axioms
info: Warrant/Axioms.lean:40:0: 'Warrant.witness_dual_partial' does not depend on any axioms
✔ [8560/8561] Built Warrant (6.3s)
Build completed successfully (8561 jobs).
```

There is one non-fatal warning, printed by elan before each command:
`warning: could not check for elan self-update: failed to parse latest release tag`.

### What this receipt does and does not establish

It establishes that Lean `v4.31.0` type-checks these sources against Mathlib `fabf563a…` with no
`sorry` and no added axioms. That is the evidence `lean/README.md` describes, re-emitted
independently on a fresh machine. It does **not** establish that the Lean definitions faithfully
encode the prose of `METHODOLOGY.md`. That is the open `impl↔model` leaf `lean/README.md` names
under *Honest scope*.

Side note, no change made: the build prints `witness_dual_partial`, which the theorem list in
`lean/README.md` does not mention.

## Attempt 1 — failed on an environment block (same day, 19:26:40 → 19:26:42)

With elan freshly installed (`elan-init.sh -y --default-toolchain none`), `lake exe cache get` and
`lake build` both exited 1 within about 1 s. The elan proxy tried to install the pinned toolchain
first and failed. First error, verbatim:

```
warning: could not check for elan self-update: failed to parse latest release tag
error: error during download
info: caused by: [56] Failure when receiving data from the peer (CONNECT tunnel failed, response 403)
```

The session's egress proxy logged `connect_rejected` ("gateway answered 403 to CONNECT") for
`release.lean-lang.org:443`. The failure was not routed around. After the environment's network
policy was changed, attempt 2 was run unmodified with the same commands. It reached
`releases.lean-lang.org`, `github.com` (Mathlib and its dependencies) and the Mathlib Azure cache,
and the proxy logged no rejections.

## Reproduce

```sh
cd lean
lake exe cache get
lake build
```
