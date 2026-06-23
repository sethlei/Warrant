import Mathlib

set_option linter.style.header false
set_option linter.style.longLine false
set_option linter.style.whitespace false

/-!
# Soundness-composition algebra (Warrant METHODOLOGY §3)

A machine-checked formalization, derived solely from the prose of
`METHODOLOGY.md`, of the AND/OR composition over the four
soundness cells, and the *all-N* properties a bounded model-checker can only
sample.

## Modeling decisions (recorded for the verifier)

* **Strength** is the two-point linear order `L < H` (the doc: "H > L"). It is a
  `Lattice` with `OrderBot` (⊥ = L) and `OrderTop` (⊤ = H), so `min`/`max` and
  `⊓`/`⊔` coincide and the `Multiset.sup`/`Multiset.inf` folds apply.
* **A child / leaf** carries `verdict ∈ {PASS, DEATH, PENDING}` and the
  directional pair `(sPass, sDeath)` (the leaf-contract `soundness:` field,
  doc lines 104-105 / 143). Composition uses the **verdict-aligned** strength: a
  *passed* child contributes `sPass`; a *died* child contributes `sDeath`.
* **Result `Outcome`**: `pass s | death s | pending`. PASS/DEATH carry a
  strength; PENDING carries none (the doc gives no strength to a pending node).
* **Folds over a possibly-empty sub-multiset.** DEATH-strength of an AND is the
  `Multiset.sup` (= max, identity ⊥ = L) of `sDeath` over *died* children;
  PASS-strength is `Multiset.inf` (= min, identity ⊤ = H) of `sPass` over
  *passed* children. The empty identities only surface in the AND/OR-of-∅ case.
* **Empty-multiset / identity case.** AND ∅ : vacuously "all pass" ⇒ `pass H`
  (top of the min-fold). OR ∅ : vacuously "all died" ⇒ `death H` (top of the
  min-of-deaths fold). Standard monoid identities; they keep AND/OR exact duals
  on ∅ too. Flagged as a judgment call (the doc does not state ∅ explicitly).
* **PENDING semantics.** A child is PENDING iff it neither passed nor died. AND
  is PENDING exactly when no child died and not all passed; OR is the dual.
-/

namespace Warrant

/-! ## Strength: the two-point linear order `L < H`. -/

inductive Strength
  | L : Strength
  | H : Strength
deriving DecidableEq, Repr

namespace Strength

def le : Strength → Strength → Prop
  | L, _ => True
  | H, H => True
  | H, L => False

instance decLe : (a b : Strength) → Decidable (le a b)
  | L, _ => isTrue trivial
  | H, H => isTrue trivial
  | H, L => isFalse (by simp [le])

instance : LinearOrder Strength where
  le := le
  le_refl a := by cases a <;> trivial
  le_trans a b c := by cases a <;> cases b <;> cases c <;> simp_all [le]
  le_antisymm a b := by cases a <;> cases b <;> simp_all [le]
  le_total a b := by cases a <;> cases b <;> simp [le]
  toDecidableLE := decLe
  lt_iff_le_not_ge a b := by cases a <;> cases b <;> simp [le]

instance : OrderBot Strength where
  bot := L
  bot_le a := by cases a <;> trivial

instance : OrderTop Strength where
  top := H
  le_top a := by cases a <;> trivial

@[simp] theorem L_le (a : Strength) : L ≤ a := by cases a <;> trivial
@[simp] theorem le_H (a : Strength) : a ≤ H := by cases a <;> trivial
@[simp] theorem bot_eq_L : (⊥ : Strength) = L := rfl
@[simp] theorem top_eq_H : (⊤ : Strength) = H := rfl

/-- The only two values: a strength is `L` or `H`. -/
theorem eq_L_or_H (a : Strength) : a = L ∨ a = H := by cases a <;> simp

/-- `a ≤ L` forces `a = L`. -/
theorem le_L_eq {a : Strength} (h : a ≤ L) : a = L :=
  le_antisymm h (L_le a)

end Strength

open Strength

/-! ## Verdicts and children. -/

inductive Verdict
  | PASS : Verdict
  | DEATH : Verdict
  | PENDING : Verdict
deriving DecidableEq, Repr

structure Child where
  verdict : Verdict
  sPass : Strength
  sDeath : Strength
deriving DecidableEq, Repr

inductive Outcome
  | pass : Strength → Outcome
  | death : Strength → Outcome
  | pending : Outcome
deriving DecidableEq, Repr

/-! ## The four cells (doc §3 table). -/

def Child.isSound (c : Child)   : Prop := c.sPass = H ∧ c.sDeath = H
def Child.isPartial (c : Child) : Prop := c.sPass = L ∧ c.sDeath = H
def Child.isWitness (c : Child) : Prop := c.sPass = H ∧ c.sDeath = L
def Child.isFuzzy (c : Child)   : Prop := c.sPass = L ∧ c.sDeath = L

/-! ## Predicates picking out died / passed children. -/

def died (c : Child) : Bool := c.verdict = Verdict.DEATH
def passed (c : Child) : Bool := c.verdict = Verdict.PASS

@[simp] theorem died_iff (c : Child) : died c = true ↔ c.verdict = Verdict.DEATH := by
  simp [died]
@[simp] theorem passed_iff (c : Child) : passed c = true ↔ c.verdict = Verdict.PASS := by
  simp [passed]

/-- Died / passed sub-multisets. -/
def diedSet (s : Multiset Child) : Multiset Child := s.filter (fun c => died c)
def passSet (s : Multiset Child) : Multiset Child := s.filter (fun c => passed c)

/-- AND folds: `maxDeath` = sup (max) of `sDeath` over *died*;
`minPass` = inf (min) of `sPass` over *passed*. -/
def maxDeath (s : Multiset Child) : Strength := ((diedSet s).map Child.sDeath).sup
def minPass (s : Multiset Child) : Strength := ((passSet s).map Child.sPass).inf

/-- OR folds (dual): `maxPass` = sup of `sPass` over *passed*;
`minDeath` = inf of `sDeath` over *died*. -/
def maxPass (s : Multiset Child) : Strength := ((passSet s).map Child.sPass).sup
def minDeath (s : Multiset Child) : Strength := ((diedSet s).map Child.sDeath).inf

/-! ## Composition. -/

def anyDeath (s : Multiset Child) : Bool := diedSet s ≠ 0
def anyPass (s : Multiset Child) : Bool := passSet s ≠ 0
def allPass (s : Multiset Child) : Bool := passSet s = s
def allDeath (s : Multiset Child) : Bool := diedSet s = s

def composeAnd (s : Multiset Child) : Outcome :=
  if anyDeath s then Outcome.death (maxDeath s)
  else if allPass s then Outcome.pass (minPass s)
  else Outcome.pending

def composeOr (s : Multiset Child) : Outcome :=
  if anyPass s then Outcome.pass (maxPass s)
  else if allDeath s then Outcome.death (minDeath s)
  else Outcome.pending

def composeAndList (l : List Child) : Outcome := composeAnd (l : Multiset Child)
def composeOrList (l : List Child) : Outcome := composeOr (l : Multiset Child)

@[simp] theorem maxDeath_zero : maxDeath 0 = L := by simp [maxDeath, diedSet]
@[simp] theorem minPass_zero : minPass 0 = H := by simp [minPass, passSet]
@[simp] theorem maxPass_zero : maxPass 0 = L := by simp [maxPass, passSet]
@[simp] theorem minDeath_zero : minDeath 0 = H := by simp [minDeath, diedSet]

/-! ## THEOREM 1 — Order independence for all N.

For permutations `l ~ l'` (and more generally equal multisets), the composed
AND and OR are equal: the result depends only on the multiset of children. -/

theorem composeAnd_perm {l l' : List Child} (h : l.Perm l') :
    composeAndList l = composeAndList l' := by
  unfold composeAndList
  rw [Multiset.coe_eq_coe.mpr h]

theorem composeOr_perm {l l' : List Child} (h : l.Perm l') :
    composeOrList l = composeOrList l' := by
  unfold composeOrList
  rw [Multiset.coe_eq_coe.mpr h]

theorem composeAnd_multiset_function {l l' : List Child}
    (h : (l : Multiset Child) = (l' : Multiset Child)) :
    composeAndList l = composeAndList l' := by
  unfold composeAndList; rw [h]

theorem composeOr_multiset_function {l l' : List Child}
    (h : (l : Multiset Child) = (l' : Multiset Child)) :
    composeOrList l = composeOrList l' := by
  unfold composeOrList; rw [h]

/-! ## THEOREM 2 — AND/OR characterization (the rule on each branch). -/

theorem composeAnd_death (s : Multiset Child) (h : anyDeath s) :
    composeAnd s = Outcome.death (maxDeath s) := by
  simp only [composeAnd, if_pos h]

theorem composeAnd_pass (s : Multiset Child)
    (h₁ : ¬ anyDeath s) (h₂ : allPass s) :
    composeAnd s = Outcome.pass (minPass s) := by
  simp only [composeAnd, if_neg h₁, if_pos h₂]

theorem composeAnd_pending (s : Multiset Child)
    (h₁ : ¬ anyDeath s) (h₂ : ¬ allPass s) :
    composeAnd s = Outcome.pending := by
  simp only [composeAnd, if_neg h₁, if_neg h₂]

theorem composeOr_pass (s : Multiset Child) (h : anyPass s) :
    composeOr s = Outcome.pass (maxPass s) := by
  simp only [composeOr, if_pos h]

theorem composeOr_death (s : Multiset Child)
    (h₁ : ¬ anyPass s) (h₂ : allDeath s) :
    composeOr s = Outcome.death (minDeath s) := by
  simp only [composeOr, if_neg h₁, if_pos h₂]

theorem composeOr_pending (s : Multiset Child)
    (h₁ : ¬ anyPass s) (h₂ : ¬ allDeath s) :
    composeOr s = Outcome.pending := by
  simp only [composeOr, if_neg h₁, if_neg h₂]

/-- Membership in `diedSet`. -/
theorem mem_diedSet {s : Multiset Child} {c : Child} :
    c ∈ diedSet s ↔ c ∈ s ∧ died c := by
  simp [diedSet, Multiset.mem_filter]

theorem mem_passSet {s : Multiset Child} {c : Child} :
    c ∈ passSet s ↔ c ∈ s ∧ passed c := by
  simp [passSet, Multiset.mem_filter]

/-- The death strength is `≥` each died child's `sDeath` (faithful "max"). -/
theorem maxDeath_ge {s : Multiset Child} {c : Child}
    (hc : c ∈ s) (hd : died c) : c.sDeath ≤ maxDeath s := by
  apply Multiset.le_sup
  exact Multiset.mem_map.mpr ⟨c, mem_diedSet.mpr ⟨hc, hd⟩, rfl⟩

/-- ...and the death strength is the sup: it is `≤` any upper bound of the died
`sDeath`s. Together with `maxDeath_ge`, this pins `maxDeath` as the genuine max. -/
theorem maxDeath_le {s : Multiset Child} {a : Strength}
    (h : ∀ c ∈ s, died c → c.sDeath ≤ a) : maxDeath s ≤ a := by
  apply Multiset.sup_le.mpr
  intro b hb
  obtain ⟨c, hcmem, rfl⟩ := Multiset.mem_map.mp hb
  obtain ⟨hc, hd⟩ := mem_diedSet.mp hcmem
  exact h c hc hd

/-- The pass strength is `≤` each passed child's `sPass` (faithful "min"). -/
theorem minPass_le {s : Multiset Child} {c : Child}
    (hc : c ∈ s) (hp : passed c) : minPass s ≤ c.sPass := by
  apply Multiset.inf_le
  exact Multiset.mem_map.mpr ⟨c, mem_passSet.mpr ⟨hc, hp⟩, rfl⟩

theorem le_minPass {s : Multiset Child} {a : Strength}
    (h : ∀ c ∈ s, passed c → a ≤ c.sPass) : a ≤ minPass s := by
  apply Multiset.le_inf.mpr
  intro b hb
  obtain ⟨c, hcmem, rfl⟩ := Multiset.mem_map.mp hb
  obtain ⟨hc, hp⟩ := mem_passSet.mp hcmem
  exact h c hc hp

/-! ## THEOREM 3 — Exact De Morgan duality.

Dualize each child (flip verdict, swap the `(sPass, sDeath)` pair). Then OR of a
multiset equals the verdict-flip of AND on the dualized children, for all N. -/

def Verdict.flip : Verdict → Verdict
  | PASS => DEATH
  | DEATH => PASS
  | PENDING => PENDING

def Outcome.flip : Outcome → Outcome
  | pass s => death s
  | death s => pass s
  | pending => pending

def Child.dual (c : Child) : Child :=
  { verdict := c.verdict.flip, sPass := c.sDeath, sDeath := c.sPass }

@[simp] theorem Child.dual_dual (c : Child) : c.dual.dual = c := by
  cases c with
  | mk v p d => cases v <;> simp [Child.dual, Verdict.flip]

/-- Dualization is injective (it is an involution). -/
theorem Child.dual_injective : Function.Injective Child.dual := by
  intro a b h
  have := congrArg Child.dual h
  simpa using this

/-- A child of the dualized multiset *died* iff the original *passed*. -/
@[simp] theorem died_dual (c : Child) : died c.dual = passed c := by
  obtain ⟨v, p, d⟩ := c
  cases v <;> simp [died, passed, Child.dual, Verdict.flip]

@[simp] theorem passed_dual (c : Child) : passed c.dual = died c := by
  obtain ⟨v, p, d⟩ := c
  cases v <;> simp [died, passed, Child.dual, Verdict.flip]

/-- The died-set of the dualized multiset is the dual-image of the pass-set. -/
theorem diedSet_map_dual (s : Multiset Child) :
    diedSet (s.map Child.dual) = (passSet s).map Child.dual := by
  simp only [diedSet, passSet, Multiset.filter_map]
  congr 1
  apply Multiset.filter_congr
  intro c _
  simp [Function.comp]

theorem passSet_map_dual (s : Multiset Child) :
    passSet (s.map Child.dual) = (diedSet s).map Child.dual := by
  simp only [diedSet, passSet, Multiset.filter_map]
  congr 1
  apply Multiset.filter_congr
  intro c _
  simp [Function.comp]

/-- `anyDeath (dual s) = anyPass s`. -/
theorem anyDeath_map_dual (s : Multiset Child) :
    anyDeath (s.map Child.dual) = anyPass s := by
  simp only [anyDeath, anyPass, diedSet_map_dual, ne_eq, Multiset.map_eq_zero]

/-- `maxPass s = maxDeath (dual s)` — the OR pass-fold equals the dual AND
death-fold (sup of the same strengths after the swap). -/
theorem maxPass_eq_maxDeath_dual (s : Multiset Child) :
    maxPass s = maxDeath (s.map Child.dual) := by
  unfold maxPass maxDeath
  rw [diedSet_map_dual, Multiset.map_map]
  rfl

/-- `minDeath s = minPass (dual s)`. -/
theorem minDeath_eq_minPass_dual (s : Multiset Child) :
    minDeath s = minPass (s.map Child.dual) := by
  unfold minDeath minPass
  rw [passSet_map_dual, Multiset.map_map]
  rfl

/-- The AND-pass-branch test `allPass (dual s)` equals the OR-death-branch test
`allDeath s`. -/
theorem allPass_map_dual (s : Multiset Child) :
    allPass (s.map Child.dual) = allDeath s := by
  simp only [allPass, allDeath, passSet_map_dual]
  simp only [(Multiset.map_injective Child.dual_injective).eq_iff]

/-- **Exact De Morgan duality, all N.**
`composeOr s = (composeAnd (dual s)).flip`. -/
theorem composeOr_eq_dual (s : Multiset Child) :
    composeOr s = (composeAnd (s.map Child.dual)).flip := by
  unfold composeOr composeAnd
  rw [anyDeath_map_dual, allPass_map_dual]
  by_cases hp : anyPass s
  · simp only [if_pos hp, Outcome.flip, maxPass_eq_maxDeath_dual]
  · simp only [if_neg hp]
    by_cases hda : allDeath s
    · simp only [if_pos hda, Outcome.flip, minDeath_eq_minPass_dual]
    · simp only [if_neg hda, Outcome.flip]

/-! ## THEOREM 4 — FUZZY (L,L) death never composes to a HARD kill. -/

theorem and_soft_death (s : Multiset Child)
    (hall : ∀ c ∈ s, died c → c.sDeath = L) :
    ∀ str, composeAnd s = Outcome.death str → str = L := by
  intro str h
  by_cases hd : anyDeath s
  · rw [composeAnd_death s hd] at h
    injection h with heq
    subst heq
    apply Strength.le_L_eq
    apply maxDeath_le
    intro c hc hdied
    rw [hall c hc hdied]
  · -- no death branch: composeAnd is pass or pending, never death
    simp only [composeAnd, if_neg hd] at h
    by_cases hp : allPass s <;> simp [hp] at h

/-- For OR, the death branch fires only via `allDeath`, which on a *nonempty*
multiset gives a real death certificate. We require `s ≠ 0` because the empty OR
is the vacuous identity `death H` (the `OR ∅` case) — there is no died child to
make the death soft, so the claim genuinely does not hold for `∅`. This is an
honest edge-case exclusion, not a weakening of the substantive content. -/
theorem or_soft_death (s : Multiset Child) (hne : s ≠ 0)
    (hall : ∀ c ∈ s, died c → c.sDeath = L) :
    ∀ str, composeOr s = Outcome.death str → str = L := by
  intro str h
  by_cases hp : anyPass s
  · rw [composeOr_pass s hp] at h; cases h
  · by_cases hd : allDeath s
    · rw [composeOr_death s hp hd] at h
      injection h with heq
      subst heq
      apply Strength.le_L_eq
      -- allDeath s with s ≠ 0 ⇒ diedSet s ≠ 0 ⇒ a real died child exists.
      have hzero : diedSet s ≠ 0 := by
        simp only [allDeath, decide_eq_true_eq] at hd
        rw [hd]; exact hne
      obtain ⟨c, hc⟩ := Multiset.exists_mem_of_ne_zero hzero
      obtain ⟨hcs, hcd⟩ := mem_diedSet.mp hc
      have hcL : c.sDeath = L := hall c hcs hcd
      calc minDeath s ≤ c.sDeath := by
              apply Multiset.inf_le
              exact Multiset.mem_map.mpr ⟨c, hc, rfl⟩
        _ = L := hcL
    · rw [composeOr_pending s hp hd] at h; cases h

/-! ## THEOREM 5 — A PARTIAL (L,H) leaf that dies, in an AND ⇒ HARD kill. -/

theorem and_hard_kill (s : Multiset Child) {c : Child}
    (hc : c ∈ s) (hd : died c) (hH : c.sDeath = H) :
    composeAnd s = Outcome.death H := by
  have hany : anyDeath s := by
    simp only [anyDeath, ne_eq, decide_eq_true_eq]
    intro hzero
    have : c ∈ diedSet s := mem_diedSet.mpr ⟨hc, hd⟩
    rw [hzero] at this; exact (Multiset.notMem_zero c) this
  rw [composeAnd_death s hany]
  have hle : maxDeath s ≤ H := Strength.le_H _
  have hge : H ≤ maxDeath s := by
    rw [← hH]; exact maxDeath_ge hc hd
  have : maxDeath s = H := le_antisymm hle hge
  rw [this]

/-! ## THEOREM 6 — The four-cell mapping. -/

theorem cell_sound (c : Child)   : c.isSound   ↔ c.sPass = H ∧ c.sDeath = H := Iff.rfl
theorem cell_partial (c : Child) : c.isPartial ↔ c.sPass = L ∧ c.sDeath = H := Iff.rfl
theorem cell_witness (c : Child) : c.isWitness ↔ c.sPass = H ∧ c.sDeath = L := Iff.rfl
theorem cell_fuzzy (c : Child)   : c.isFuzzy   ↔ c.sPass = L ∧ c.sDeath = L := Iff.rfl

theorem witness_dual_partial (c : Child) : c.isWitness ↔ c.dual.isPartial := by
  cases c with
  | mk v p d => simp [Child.isWitness, Child.isPartial, Child.dual]; tauto

end Warrant
