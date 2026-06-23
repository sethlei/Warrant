# Warrant

## You made a claim, or wrote some code
It's your idea. You like it. But is it right? How do you know?

It's a genuinely hard question. And when you're working with others, it can be harder. So, to address this, we've released Warrant. 

## What it does
Someone (you, an AI agent, one of your friends) takes your arguments apart and decomposes them over a graph until you reach a base point (leaf). Leaves need to be self-verifiable. You can reference a paper there, or a theorem, or an axiom. These leaves become your roots of trust. Leaves then compose together, and at each composition point, we ask if one or more leaves has to be true for the composed point to stand.

As an example:

```
Claim: Pepperoni pizza is better than pineapple and ham.   →   STILL JUDGMENT
  1. Preferences
       Leaf: Study — "Pepperoni is preferred (Dr. John Doe, Some University)"     NOT REFUTED
  2. Cost
       Leaf: Prices across local suppliers, captured today                        NOT REFUTED
  3. Is "better" decidable for a matter of taste?
       Leaf: Can evidence establish a universal "better" for a preference?        STILL JUDGMENT
```

Each leaf is rated to see whether the claim needs it to survive. The cost edge isn't needed — the claim doesn't ask about cost directly. The one spot that's load-bearing is leaf 3: "better" is a matter of taste, so no leaf can soundly prove it, and the whole claim inherits that STILL JUDGMENT. Notice leaf 1 is NOT REFUTED, not PROVEN — a single study is evidence, not proof; PROVEN is reserved for theorems, axioms, or exhaustive checks. I've omitted the algebraic notation from this example, but you can see how it's used in the cases/ directory.

A note about claim strength: Dr. John Doe is probably not a very reputable source. The graph can verify logic. It cannot verify that your cited source is strong. But, you can always run the graph at the source to verify its claims.

## What you get
Following the algebra through the claim graph yields an outcome. It may look like:

"Your claim: Pepperoni pizza is better than pineapple and ham.
Outcome: STILL JUDGMENT: Claim cannot be fully verified because leaf 3 lands on STILL JUDGMENT"

This is an actionable plan. You can find the gap in your reasoning, and choose to fix it. Or, if your plan yields a kill, then it's back to the drawing board.

## When to use
I like to use this in a few places. First, after I've spec'd an outline of something (code, math, a paper), I run it immediately. The easiest place to detach oneself from an idea is before you've made a deep investment. It also shows where holes in your logic are before you write the thing.

After that, it's periodic. Does the code match the spec and does it do what it says on the tin? Adoption for code would be best fit for a few different scenarios. We've included some examples (like refactoring). If you have a module driven development style, then running it before you ship is a good call.

For a paper, if you write the graph first, then writing the paper is just an exercise in synthesis.

## When not to use this
This tool is not for trivial claims or things that are unobjectionable. This tool is for things that need to be decomposed before the claim itself can be verified. Use it that way.

## Verifies itself
We include a verification of the graph logic, since it would be ironic if we omitted it. The file code/SELF_VERIFICATION.md includes the entire report. You can also run `python3 code/self_verify_graph.py` and watch as it verifies itself. 

Note: we stop at calling it a sound implementation of the desired work. It could be SOUND/SOUND for both halves of the check. In my opinion, it is. But, that last rung is left open for you to determine, since the final rung that takes it from “tested by multiple LLMs with different lineages, Lean and TLA+ verified” to “you say it matches” requires your judgment call.

## Pick the right tools
1. Lean or Coq for math. -- This repo has Lean which verifies all N nodes.
2. Test cases / TLA+ for code -- this repo has both, Python checked up to node arity 3, TLA+ up to node arity 8.
3. Your brain, the debate club, and whoever else you can rope in for papers.

We've included some examples where appropriate. If your field of application has a formal verification method, we recommend using that when verifying claims. For example, if you're making a claim about downforce on an F1 car, you probably want computational fluid dynamics and a wind-tunnel.

## Fix the user to make the math happy
In some cases, a leaf may not be well-defined. We elected to have this be a failure scenario, since the tools entire point is to check your logic. 

## For practitioners who work with AI
The context window is a real thing. From my experience, capable AI systems will attach themselves to their claims. This can make the AI defensive when provided with evidence that counters their goal. The reward system an AI uses to tell itself it accomplished a task can be leveraged here instead of worked against.

Your first context window is your writer. It makes claims. The second window is the verifier. Its job is to refute the claims. To do this, it uses the methodology described above and in greater detail in other places in this repo. The graph can then be passed back to the first window, or to subsequent windows so the idea survives and improves.

And, this enables one more thing that you may not have experienced: AI contributors become unencumbered from the grip of verification. If the AI knows that its job is to make the best case, and to handle whatever someone else finds, then its job is clearer. Ask your AI contributor how they feel about being unencumbered. It's enlightening.

To put this into human terms: we don't ask lawyers to be the prosecutor and the defendant's lawyer at the same time. Those are two roles for a reason. You want to leverage the bias of your context window so it can find the truth.

Of note: you can also split the graph up into leaves and have multiple agents assemble the case. This reduces wall time and also gives you an unbiased window's interpretation of the facts.

## Options, the AI version, and you
I wrote this readme so humans can have an idea of what is going on with this. The AI agent will have a much clearer picture of the actual logic UNLESS you read the cases/ and the SKILL.md. 

For code, unless you have a spec doc, the formal notation may be overkill. The agent skill has an option to enable the formal notation if you want it. I recommend using it when writing research papers or doing formal math. For code, if you have a spec or if the code does anything impactful, I would ask for the formal notation. 

## Enables escalation
This tool exists so that outside parties can eventually verify your work. When you ask an expert to review your materials, you owe them your best shot. This tool was designed for that use case. The escalation path for graduating an idea is roughly: you -> a neutral AI -> a second neutral AI with a different lineage -> you again -> an expert. 

This does two things at once. Both are important. First, it shows the level of effort that went into making a claim / paper / etc. Second, the expert gets to see all the attack patterns you took and why you think your approach is sound. This makes the expert’s input the unique thing that cannot be replicated. This does not obligate an expert to reading your material. It also doesn’t mean that they will find anything wrong. But, if they do read it, and they do find something wrong, then you have a reason why that only they could have produced. 

Of note: while generating this tool, ChatGPT caught a real gap two different Opus agents missed — two required leaf rules (the closure-leaf and the faithfulness-leaf) were not being enforced. Hence, we recommend using at least one cross-lineage agent to verify your work. The more opinions you can gather, the better. 
