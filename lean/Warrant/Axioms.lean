import Warrant.Basic

set_option linter.style.header false

open Warrant

-- THEOREM 1 — order independence (all N)
#print axioms composeAnd_perm
#print axioms composeOr_perm
#print axioms composeAnd_multiset_function
#print axioms composeOr_multiset_function

-- THEOREM 2 — AND/OR characterization
#print axioms composeAnd_death
#print axioms composeAnd_pass
#print axioms composeAnd_pending
#print axioms composeOr_pass
#print axioms composeOr_death
#print axioms composeOr_pending
#print axioms maxDeath_ge
#print axioms maxDeath_le
#print axioms minPass_le
#print axioms le_minPass

-- THEOREM 3 — exact De Morgan duality
#print axioms composeOr_eq_dual

-- THEOREM 4 — FUZZY (L,L) death never composes to a HARD kill
#print axioms and_soft_death
#print axioms or_soft_death

-- THEOREM 5 — PARTIAL/SOUND hard death forces AND to DEATH H
#print axioms and_hard_kill

-- THEOREM 6 — four-cell mapping
#print axioms cell_sound
#print axioms cell_partial
#print axioms cell_witness
#print axioms cell_fuzzy
#print axioms witness_dual_partial
