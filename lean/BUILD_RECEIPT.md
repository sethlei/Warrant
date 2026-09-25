# `lean/` build receipt — 2026-09-25

**Outcome: BUILD NOT RUN. The Lean toolchain could not be installed.** No Lean ever ran, so this
receipt says nothing about whether the proofs check, in either direction. It records an
environment failure, not a proof failure. No `.lean` file was edited.

## Where and what

| field | value |
|---|---|
| date (UTC) | 2026-09-25, 19:26:40 → 19:26:42 |
| environment | Claude Code cloud session (Linux container, outbound HTTPS through an egress-policy proxy) |
| repo commit | `9e4a98f` (`main` head at branch point) |
| elan | `elan 4.2.4 (227caca13 2026-08-25)`, installed fresh via `elan-init.sh -y --default-toolchain none` |
| toolchain requested | `leanprover/lean4:v4.31.0` (from `lean-toolchain`); **never installed** |
| Mathlib | `inputRev` `v4.31.0`, locked `rev` `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (from `lake-manifest.json`); **never fetched** |
| `lake exe cache get` | exit 1, 0 s |
| `lake build` | exit 1, 1 s |
| total wall time | ~2 s |

## First error (verbatim)

`lake exe cache get` and `lake build` both failed the same way: the elan proxy tried to install the
pinned toolchain before running `lake`.

```
warning: could not check for elan self-update: failed to parse latest release tag
error: error during download
info: caused by: [56] Failure when receiving data from the peer (CONNECT tunnel failed, response 403)
```

(elan then printed a Rust backtrace that ends in `elan::toolchain::Toolchain::install` →
`elan_dist::manifestation::Manifestation::install` → `elan_utils::utils::fetch_url`.)

## Diagnosis

The session's egress proxy logged the rejected destination as:

```
"kind": "connect_rejected",
"detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
"host": "release.lean-lang.org:443"
```

`release.lean-lang.org` is where elan downloads Lean releases. The session's network policy does
not allow it. Per the proxy's own guidance and the session instructions, the failure was not
routed around: no mirror was tried and no toolchain was fetched from elsewhere.

## To reproduce a real build

Allow `release.lean-lang.org` in the environment's network settings, then run the steps in
`lean/README.md`:

```sh
cd lean
lake exe cache get
lake build
```

Getting past the toolchain step will likely need more hosts: GitHub, to clone Mathlib and its
dependencies at the manifest revisions, and whatever host `lake exe cache get` downloads prebuilt
`.olean` files from. This session never reached those steps, so which of these hosts are blocked
here is unknown.
