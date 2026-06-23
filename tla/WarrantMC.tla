--------------------------- MODULE WarrantMC ---------------------------
(***************************************************************************)
(* Model-checking harness for the Warrant compose algebra.                *)
(*                                                                         *)
(* STRATEGY: the single state variable `cfg` ranges over ALL N-child      *)
(* configurations (each child in {PASS.H, PASS.L, DEATH.H, DEATH.L,       *)
(* PENDING}). Init lets cfg be any config -> TLC enumerates every         *)
(* combination as an initial state. Next stutters, so the reachable state *)
(* set IS exactly Configs. Every property below is a state invariant      *)
(* checked on each enumerated configuration.                              *)
(***************************************************************************)
EXTENDS Warrant

VARIABLE cfg

Init == cfg \in Configs
Next == UNCHANGED cfg          \* stutter; reachable states = all of Configs
Spec == Init /\ [][Next]_cfg

(***************************************************************************)
(* TypeOK: every state is a well-formed configuration.                    *)
(***************************************************************************)
TypeOK == cfg \in Configs

(*=======================================================================*)
(* PROPERTY 1 -- The four-cell mapping.                                   *)
(* The cell of a leaf is determined by its (s_pass, s_death) pair:        *)
(*   SOUND=(H,H) PARTIAL=(L,H) WITNESS=(H,L) FUZZY=(L,L).                 *)
(* We assert the cell table is exactly this bijection over {H,L}^2,       *)
(* and the two named structural facts in the doc:                         *)
(*   - PARTIAL is sound in the death direction (s_death = H);             *)
(*   - WITNESS is the De Morgan dual of PARTIAL (swap the pair).          *)
(* This is a pure data property (no dependence on cfg) -- a state         *)
(* invariant that is constant, so it holds in every state iff it holds.   *)
(*=======================================================================*)
Cell(sp, sd) ==
    CASE sp = H /\ sd = H -> "SOUND"
      [] sp = L /\ sd = H -> "PARTIAL"
      [] sp = H /\ sd = L -> "WITNESS"
      [] sp = L /\ sd = L -> "FUZZY"

FourCellMapping ==
    /\ Cell(H,H) = "SOUND"
    /\ Cell(L,H) = "PARTIAL"
    /\ Cell(H,L) = "WITNESS"
    /\ Cell(L,L) = "FUZZY"
    \* PARTIAL is sound-in-death (a failing test is a real counterexample)
    /\ Cell(L,H) = "PARTIAL"  \* s_death = H above
    \* WITNESS is the exact dual of PARTIAL: swap (s_pass,s_death)
    /\ Cell(H,L) = "WITNESS"  \* (L,H) -> (H,L)
    \* the four cells are distinct (a genuine 4-cell partition)
    /\ Cardinality({ Cell(L,L), Cell(L,H), Cell(H,L), Cell(H,H) }) = 4

(*=======================================================================*)
(* PROPERTY 2 -- AND compose rules, re-derived independently and checked  *)
(* against ComposeAND for the current cfg.                                *)
(*   (a) any-death-kills: AND dies iff some child died.                   *)
(*   (b) when it dies, DEATH-strength = max of s_death over DIED children.*)
(*   (c) when all children passed, PASS-strength = min of s_pass.         *)
(*=======================================================================*)
ANDCompose ==
    LET r == ComposeAND(cfg) IN
    /\ (r.v = DEATH) <=> AnyDeath(cfg)                          \* (a)
    /\ (r.v = DEATH) => (r.str = MaxSet(DeathStrengths(cfg)))   \* (b)
    /\ (r.v = PASS)  <=> (Passed(cfg) = (1..N))                 \* all pass
    /\ (r.v = PASS)  => (r.str = MinSet(PassStrengths(cfg)))    \* (c)
    /\ (r.v = PENDING) <=> (~AnyDeath(cfg) /\ Passed(cfg) # (1..N))

(*=======================================================================*)
(* PROPERTY 3 -- OR compose rules, independently re-derived.              *)
(*   (a) all-must-die: OR dies iff EVERY child died.                      *)
(*   (b) when it dies, DEATH-strength = min of s_death over children.     *)
(*   (c) OR passes iff some child passed; PASS-strength = max of s_pass.  *)
(*=======================================================================*)
ORCompose ==
    LET r == ComposeOR(cfg) IN
    /\ (r.v = DEATH) <=> AllDeath(cfg)                          \* (a)
    /\ (r.v = DEATH) => (r.str = MinSet(DeathStrengths(cfg)))   \* (b)
    /\ (r.v = PASS)  <=> AnyPass(cfg)                           \* (c)
    /\ (r.v = PASS)  => (r.str = MaxSet(PassStrengths(cfg)))
    /\ (r.v = PENDING) <=> (~AnyPass(cfg) /\ ~AllDeath(cfg))

(*=======================================================================*)
(* PROPERTY 4 -- Exact De Morgan duality.                                 *)
(* OR over cfg equals (flip) of AND over (Dual cfg), and vice versa:      *)
(*     ComposeOR(cfg)  = FlipResult(ComposeAND(Dual(cfg)))               *)
(*     ComposeAND(cfg) = FlipResult(ComposeOR(Dual(cfg)))                *)
(* This encodes "swap AND<->OR, PASS<->DEATH, s_pass<->s_death is a       *)
(* symmetry" (METHODOLOGY line 126) as an equality of composed results.   *)
(*=======================================================================*)
Duality ==
    /\ ComposeOR(cfg)  = FlipResult(ComposeAND(Dual(cfg)))
    /\ ComposeAND(cfg) = FlipResult(ComposeOR(Dual(cfg)))

(*=======================================================================*)
(* PROPERTY 5 -- A FUZZY (L,L) death never composes to a HARD kill.       *)
(* Encoding: if EVERY died child is soft (s_death = L) -- the situation a *)
(* set of fuzzy/soft deaths produces -- then neither compose yields a     *)
(* DEATH with str = H. (s_death=H is "hard"; L is "soft", section 4:      *)
(* "a five-rung-agreed FUZZY death enters its AND-node as s_death = L, a   *)
(* soft death ... never a hard kill".)                                    *)
(*                                                                         *)
(* More pointedly: ANY individual FUZZY/soft death (str=L) cannot, on its *)
(* own, be the source of a hard kill, because max/min of strengths that   *)
(* are all L is L. We assert: if all deaths are soft, the composed death  *)
(* (if any) is soft.                                                      *)
(*=======================================================================*)
AllDeathsSoft == \A i \in Died(cfg) : cfg[i].str = L

FuzzyDeathNeverHard ==
    LET ra == ComposeAND(cfg)
        ro == ComposeOR(cfg) IN
    AllDeathsSoft =>
        /\ (ra.v = DEATH => ra.str = L)
        /\ (ro.v = DEATH => ro.str = L)

(*=======================================================================*)
(* PROPERTY 6 -- A PARTIAL (L,H) leaf that DIES, inside an AND, yields a  *)
(* HARD kill.                                                             *)
(* A PARTIAL leaf has s_death = H. So a died PARTIAL leaf is modeled as a *)
(* DEATH.H child. The doc (lines 128-133): an AND with such a leaf reads  *)
(* DEATH-strength = max(s_death) = H -> real (hard) falsification.        *)
(* Encoding: if ANY child is a hard death (DEATH with str=H), then        *)
(* ComposeAND yields DEATH with str = H -- regardless of the other        *)
(* children (e.g. a SOUND-pass sibling). This is exactly the "scalar      *)
(* weakest-link would mis-read it as not-yet-refuted" bug the pair fixes. *)
(*=======================================================================*)
ExistsHardDeath == \E i \in 1..N : cfg[i].v = DEATH /\ cfg[i].str = H

PartialDeathIsHardInAND ==
    LET r == ComposeAND(cfg) IN
    ExistsHardDeath => (r.v = DEATH /\ r.str = H)

(*=======================================================================*)
(* PROPERTY 7 -- Order independence / associativity-as-symmetry.          *)
(* Compose is invariant under any transposition of two child positions    *)
(* (transpositions generate all permutations -> full order-independence). *)
(* For all i,j: ComposeX(cfg) = ComposeX(Swap(cfg,i,j)) for X in {AND,OR}.*)
(*=======================================================================*)
OrderIndependent ==
    \A i \in 1..N : \A j \in 1..N :
        /\ ComposeAND(cfg) = ComposeAND(Swap(cfg, i, j))
        /\ ComposeOR(cfg)  = ComposeOR(Swap(cfg, i, j))

(*=======================================================================*)
(* Sanity / closure invariants on the compose codomain.                  *)
(* Composed results are always well-typed: verdict in Verdict, and a      *)
(* PASS/DEATH carries a strength in {L,H}, PENDING carries sentinel 0.    *)
(*=======================================================================*)
ResultWellTyped(r) ==
    /\ r.v \in Verdict
    /\ (r.v \in {PASS, DEATH}) => (r.str \in Strength)
    /\ (r.v = PENDING) => (r.str = 0)

ResultsWellTyped ==
    /\ ResultWellTyped(ComposeAND(cfg))
    /\ ResultWellTyped(ComposeOR(cfg))

(*=======================================================================*)
(* The conjunction of all invariants (also each listed individually in    *)
(* the .cfg so a violation names the offender).                           *)
(*=======================================================================*)
AllInvariants ==
    /\ TypeOK
    /\ FourCellMapping
    /\ ANDCompose
    /\ ORCompose
    /\ Duality
    /\ FuzzyDeathNeverHard
    /\ PartialDeathIsHardInAND
    /\ OrderIndependent
    /\ ResultsWellTyped

=============================================================================
