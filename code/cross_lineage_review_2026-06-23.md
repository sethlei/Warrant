# Rung-4 cross-lineage review — provenance record

A clean-context model of a **different lineage** was handed `METHODOLOGY.md` and
`warrant.py` (blind — our verdict and oracle withheld) and asked, adversarially, to find
spec↔code divergences. This is the verbatim reply. **Disposition** (each claim re-checked
against the code; full reasoning in `SELF_VERIFICATION.md` → *Rung-4* section):

- **Algebra (props 1–5, 7–9): corroborated.** An independent lineage reads the compose
  algebra as faithful — cross-lineage agreement on the exhaustively-SOUND part.
- **"A — OR closure-leaf only warned" → REAL → FIXED.** Now enforced at `Graph.validate`
  (rejected, not warned).
- **"B — faithfulness-leaf not enforced" → REAL → FIXED.** Now required at `Graph.validate`
  (a decomposed root must carry an explicit faithfulness-leaf; an OR root must be wrapped).
- **"6 — containment loses directional info" → FALSE POSITIVE** (reviewer flagged as its
  own least-sure point): a contained node is moot via *one* direction; the code records that
  direction (`death_strength` / `pass_strength`) correctly.
- **"C — containment only on PENDING nodes" → DEFENSIBLE** (reviewer unsure): correct for
  containment's cost-saving role; spec-wording clarity at most.

The two REAL findings are the rung-4 win: a different lineage, not sharing the assumption
baked into our own probes ("a warning is fine"), surfaced a structural gap the same-lineage
verification missed — exactly what the cross-lineage rung is for.

---

## Load-bearing rules extracted from the specification

The specification defines a two-axis system:

1. **Soundness is directional**, represented by `(s_pass, s_death)` rather than a scalar.
2. The four cells are exactly:

   * SOUND = `(H,H)`
   * PARTIAL = `(L,H)`
   * WITNESS = `(H,L)`
   * FUZZY = `(L,L)`
3. Composition operates on **realized** trust, not achievable trust.
4. **AND**

   * PASS-strength = `min(s_pass)` over children.
   * DEATH-strength = `max(s_death)` over the children that actually died.
5. **OR**

   * PASS-strength = `max(s_pass)`.
   * Dies only when **all** alternatives die.
   * Then DEATH-strength = `min(s_death)` over them.
6. AND/OR must obey the exact pass↔death duality.
7. Containment must preserve the soundness of the edge through which mootness occurred.
8. FUZZY judgments never become sound through agreement.
9. Split judgments escalate to a pending/human state.
10. Numerical deaths are flares until certified away from the relevant floor; discretization-floor cases must be routed to analytic checking.

---

# Property audit

| Property                                                                  | MATCH / DIVERGE         | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Four soundness cells map exactly as specified                          | **MATCH**               | `cell()` maps `(H,H)->SOUND`, `(L,H)->PARTIAL`, `(H,L)->WITNESS`, `(L,L)->FUZZY` at lines 57–64.                                                                                                                                                                                                                                                                                                                                                                       |
| 2. AND composition: pass=min(pass), death=max(death among died children)  | **MATCH**               | PASS branch uses `_min` over child `pass_strength` lines 205–212. DEATH branch first filters `died = [...]` line 196, then takes `_max` only over those died children lines 197–203.                                                                                                                                                                                                                                                                                   |
| 3. OR composition: pass=max(pass); dies only if all die; death=min(death) | **MATCH**               | PASS branch uses `_max` over passed children lines 228–236. DEATH branch only entered under `all(k.verdict == DEATH ...)` line 237 and computes `_min` over deaths lines 239–242.                                                                                                                                                                                                                                                                                      |
| 4. Exact AND/OR duality                                                   | **MATCH (with caveat)** | The algebra implemented in `_compose_and()` and `_compose_or()` is the stated dual: AND uses min-pass/max-death-over-killers; OR uses max-pass/min-death-after-all-die (lines 194–246). The closure-leaf requirement is additional structure, but does not break the stated algebra.                                                                                                                                                                                   |
| 5. Uses realized trust, not achievable trust; gaps surfaced               | **MATCH**               | Leaf PASS strength comes from `node.realized[0]`, DEATH strength from `node.realized[1]` (lines 178–182). Achievable is only used for labeling and gap reporting (lines 183–188). Readout marks realized-vs-achievable gaps as cost-deferred (lines 329–330).                                                                                                                                                                                                          |
| 6. Containment carries edge soundness                                     | **DIVERGE**             | The specification distinguishes containment via SOUND vs FUZZY edges. The implementation collapses edge soundness to a single bit (`H` vs `L`) in `_propagate_containment()` lines 254–258 and 265–270. A containment through a **PARTIAL death** `(L,H)` or **WITNESS pass** `(H,L)` is represented only as `H`, thereby losing the directional information the methodology emphasizes. The spec's soundness model is directional; containment records only a scalar. |
| 7. FUZZY death stays soft regardless of agreement                         | **MATCH**               | `collapse_ladder()` always returns achievable `(L,L)` (lines 348–370). Unanimous DEATH becomes `(L,L)` DEATH at lines 363–364. Readout hardness is determined solely by `death_strength == H` (lines 311–313), so a fuzzy death remains soft.                                                                                                                                                                                                                          |
| 8. Split ladder escalates to pending/human state                          | **MATCH**               | Mixed PASS/DEATH votes produce `PENDING` and `realized=None` (lines 367–368). No majority rule exists.                                                                                                                                                                                                                                                                                                                                                                 |
| 9. Float rule                                                             | **MATCH**               | No promotion condition → INVALID (lines 392–394). Precision-bump invariance or discretization floor → FLARE and reroute to analytic checker (lines 395–399). Precision floor + certified separation → KILL (lines 400–402). Otherwise FLARE (lines 403–405).                                                                                                                                                                                                           |

---

# Additional divergences outside the requested list

## A. OR-node closure leaf is only warned about, not enforced

**Specification**

> “An OR-node requires a closure-leaf.”

This is written as a requirement, not a recommendation.

**Implementation**

If no closure leaf exists, `_compose_or()` merely appends a warning:

* lines 222–227

The OR still composes normally and may PASS or DEATH.

**Why this is a divergence**

The spec presents the closure leaf as mandatory because eliminative arguments can hide unstated exhaustiveness assumptions. The code treats it as advisory.

---

## B. Root faithfulness leaf is not enforced

**Specification**

> “The root carries a faithfulness-leaf.”

**Implementation**

There is an `is_faithfulness` flag on `Node` (line 99), but no composition rule, validation, or enforcement checks for its existence anywhere in the graph.

**Why this is a divergence**

The methodology elevates faithfulness of the decomposition to a required leaf. The implementation merely stores metadata and never verifies that such a leaf exists.

---

## C. Containment is only applied to PENDING nodes

**Specification**

Containment is defined as a node made moot by an upstream decision.

**Implementation**

A node is marked contained only when:

* `via is not None and r.verdict == PENDING`
* lines 254–258

A node that has already been evaluated PASS or DEATH but is subsequently rendered moot is not marked contained.

**Why this may diverge**

The specification defines containment semantically (mootness), not as “moot and unrun.” The implementation narrows containment to pending nodes only. Whether that is intended is not explicitly stated, but it is a behavioral restriction not licensed by the text.

---

# Overall judgment

**DIVERGENCES FOUND**

The core algebra (cells, AND, OR, duality, realized-vs-achievable, ladder behavior, float rule) is implemented faithfully.

However, I found at least two substantive divergences:

1. **Containment loses directional soundness information**, reducing it to a single `H/L` scalar rather than preserving the directional structure central to the methodology.
2. **The OR closure-leaf requirement is not enforced**, only warned about.

A third likely divergence is that the **faithfulness-leaf requirement is not enforced at all**.

---

# Things I am least sure about

### 1. Containment soundness representation

I marked this as a divergence because the specification repeatedly stresses directional soundness `(s_pass, s_death)`, whereas containment records only a single `H` or `L` value (`contained_via`). It is possible the authors intended containment to track only the realized edge outcome's soundness direction rather than the full pair. The text is not completely explicit on the representation.

### 2. Whether closure-leaf absence should be a hard error

The prose says:

> “An OR-node requires a closure-leaf.”

I interpret that as mandatory. The implementation treats it as a warning. It is conceivable the authors intentionally chose a permissive runtime that surfaces violations rather than rejecting them. The text, however, reads more strongly than the implementation.
