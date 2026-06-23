---------------------------- MODULE Warrant ----------------------------
(***************************************************************************)
(* An INDEPENDENT TLA+ formalization of the soundness-composition algebra *)
(* described (in English prose only) in METHODOLOGY.md.  *)
(*                                                                         *)
(* Route-independence cross-check: derived solely from the methodology     *)
(* document's sections 3 ("the soundness axis", four cells + AND/OR        *)
(* compose + duality) and 4 (the fuzzy soft-death rule). No reference      *)
(* implementation or oracle was consulted.                                 *)
(*                                                                         *)
(* DOMAIN MODEL                                                            *)
(*   Each LEAF/child carries a verdict in {PASS, DEATH, PENDING} and a     *)
(*   directional soundness pair (s_pass, s_death), each in {H, L}.         *)
(*                                                                         *)
(*   The four cells (METHODOLOGY table, lines 109-114):                    *)
(*       SOUND   = (H,H)   PARTIAL = (L,H)                                  *)
(*       WITNESS = (H,L)   FUZZY   = (L,L)                                  *)
(*     s_pass  = "can this checker certify the claim TRUE?"                 *)
(*     s_death = "can this checker certify the claim FALSE?"               *)
(*                                                                         *)
(*   The task enumerates each child over 5 observable states:              *)
(*       PASS.H, PASS.L, DEATH.H, DEATH.L, PENDING                         *)
(*   We model a child as a record [v |-> verdict, str |-> strength]. For   *)
(*   composition the prose says PASS-strength is built from s_pass of      *)
(*   children and DEATH-strength from s_death of DIED children, so the     *)
(*   "H/L" attached to a PASS child is its s_pass and the "H/L" attached   *)
(*   to a DEATH child is its s_death. See JUDGMENT CALLS at the bottom of  *)
(*   the deliverable message for the off-direction component.             *)
(***************************************************************************)
EXTENDS Naturals, Sequences, FiniteSets, TLC

CONSTANT N            \* arity: number of children being composed

(***************************************************************************)
(* Soundness strengths. We order L < H so min/max are ordinary numeric    *)
(* min/max on a 2-point lattice. (METHODOLOGY: "weakest link" = min;       *)
(* "best death certificate" = max; encoded numerically.)                   *)
(***************************************************************************)
L == 0
H == 1
Strength == {L, H}

Max2(a, b) == IF a >= b THEN a ELSE b
Min2(a, b) == IF a =< b THEN a ELSE b

\* Verdicts
PASS    == "PASS"
DEATH   == "DEATH"
PENDING == "PENDING"
Verdict == {PASS, DEATH, PENDING}

(***************************************************************************)
(* The 5 observable child states the task asks us to enumerate.           *)
(*   PASS.H  = passed,  contributing s_pass  = H                          *)
(*   PASS.L  = passed,  contributing s_pass  = L                          *)
(*   DEATH.H = died,    contributing s_death = H  (a HARD kill)           *)
(*   DEATH.L = died,    contributing s_death = L  (a SOFT kill)           *)
(*   PENDING = not yet decided; contributes no strength                   *)
(*                                                                         *)
(* JUDGMENT CALL: the prose's compose rules only ever read s_pass FROM    *)
(* passed children and s_death FROM died children. A PASS child's s_death  *)
(* and a DEATH child's s_pass are never consulted by any compose rule in   *)
(* the doc, so the 5-state enumeration is faithful: the off-direction     *)
(* component is inert. We carry the verdict-aligned strength only.        *)
(***************************************************************************)
ChildStates ==
    { [v |-> PASS,    str |-> H],
      [v |-> PASS,    str |-> L],
      [v |-> DEATH,   str |-> H],
      [v |-> DEATH,   str |-> L],
      [v |-> PENDING, str |-> 0] }   \* str irrelevant for PENDING; sentinel 0

(***************************************************************************)
(* A configuration: a function from 1..N (positions) to ChildStates.      *)
(***************************************************************************)
Configs == [1..N -> ChildStates]

\* Helper predicates over a configuration cfg
Died(cfg)   == { i \in 1..N : cfg[i].v = DEATH }
Passed(cfg) == { i \in 1..N : cfg[i].v = PASS  }
AnyDeath(cfg)  == Died(cfg)   # {}
AllDeath(cfg)  == Died(cfg)   = (1..N)
AnyPass(cfg)   == Passed(cfg) # {}

(***************************************************************************)
(* Aggregators over a (possibly empty) set of strengths.                  *)
(* MaxSet: max with identity L (0) -- empty set -> L                      *)
(* MinSet: min with identity H (1) -- empty set -> H                      *)
(* These identities are the lattice bottom/top that make the fold well    *)
(* defined; chosen so an empty contribution is neutral under min/max.     *)
(***************************************************************************)
RECURSIVE MaxSet(_)
MaxSet(S) ==
    IF S = {} THEN L
    ELSE LET x == CHOOSE e \in S : TRUE
         IN  Max2(x, MaxSet(S \ {x}))

RECURSIVE MinSet(_)
MinSet(S) ==
    IF S = {} THEN H
    ELSE LET x == CHOOSE e \in S : TRUE
         IN  Min2(x, MinSet(S \ {x}))

\* strengths of the PASSED children / strengths of the DIED children
PassStrengths(cfg)  == { cfg[i].str : i \in Passed(cfg) }
DeathStrengths(cfg) == { cfg[i].str : i \in Died(cfg) }

(***************************************************************************)
(* AND-node composition (METHODOLOGY lines 121-123).                      *)
(*   - any one death kills the AND.                                       *)
(*   - PASS-strength = min over children of s_pass (weakest link).        *)
(*       JUDGMENT CALL: an AND truly PASSes only when ALL children PASS    *)
(*       (no death, nothing pending); only then is min-over-s_pass the    *)
(*       composed pass-strength. If something is pending and nothing      *)
(*       died, the AND is PENDING.                                        *)
(*   - DEATH-strength = max over DIED children of s_death.                *)
(* Result is [v |-> verdict, str |-> composed strength]: str is the       *)
(* PASS-strength when v=PASS, the DEATH-strength when v=DEATH, sentinel 0  *)
(* when PENDING.                                                          *)
(***************************************************************************)
ComposeAND(cfg) ==
    IF AnyDeath(cfg)
        THEN [v |-> DEATH, str |-> MaxSet(DeathStrengths(cfg))]
    ELSE IF Passed(cfg) = (1..N)            \* all children passed
        THEN [v |-> PASS,  str |-> MinSet(PassStrengths(cfg))]
    ELSE [v |-> PENDING, str |-> 0]

(***************************************************************************)
(* OR-node composition (METHODOLOGY lines 124-125).                       *)
(*   - dies only if ALL children die; then DEATH-strength = min of s_death*)
(*     (weakest death caps it).                                           *)
(*   - PASS-strength = max of s_pass (best path certifies); an OR passes   *)
(*     as soon as any child passes.                                       *)
(*       JUDGMENT CALL: OR passes if ANY child passes (dual of AND's "any *)
(*       death kills"); else if all died -> DEATH; else PENDING.          *)
(***************************************************************************)
ComposeOR(cfg) ==
    IF AnyPass(cfg)
        THEN [v |-> PASS,  str |-> MaxSet(PassStrengths(cfg))]
    ELSE IF AllDeath(cfg)
        THEN [v |-> DEATH, str |-> MinSet(DeathStrengths(cfg))]
    ELSE [v |-> PENDING, str |-> 0]

(***************************************************************************)
(* DUALITY (METHODOLOGY line 126): swap AND<->OR, PASS<->DEATH,           *)
(* s_pass<->s_death and the algebra is a symmetry.                        *)
(*                                                                         *)
(* We realize the swap as an involution on a configuration: flip every    *)
(* child's verdict PASS<->DEATH (PENDING fixed). Because a PASS child's   *)
(* contributed strength is its s_pass and a DEATH child's is its s_death, *)
(* swapping s_pass<->s_death keeps the SAME number on the flipped child   *)
(* (the verdict-aligned strength just changes which direction it labels). *)
(* So Dual(cfg) keeps str, flips v.                                       *)
(***************************************************************************)
FlipVerdict(v) == CASE v = PASS    -> DEATH
                    [] v = DEATH   -> PASS
                    [] v = PENDING -> PENDING
Dual(cfg) == [ i \in 1..N |-> [v |-> FlipVerdict(cfg[i].v), str |-> cfg[i].str] ]

\* Flip a composed result the same way (verdict swap, strength preserved).
FlipResult(r) == [v |-> FlipVerdict(r.v), str |-> r.str]

(***************************************************************************)
(* ORDER INDEPENDENCE: permute the positions of a configuration.          *)
(* Compare ComposeX(cfg) to ComposeX of cfg with two positions swapped    *)
(* -- transpositions generate the symmetric group, so invariance under    *)
(* every transposition == invariance under every permutation.             *)
(***************************************************************************)
Swap(cfg, i, j) ==
    [ k \in 1..N |-> IF k = i THEN cfg[j]
                     ELSE IF k = j THEN cfg[i]
                     ELSE cfg[k] ]

=============================================================================
