**Why the schema is safer: a declared contract is checked before any run uses a capability, and every later check has a target.** Diagram: `capsule-openjiuwen/merged/figures/declared.png`.

| | Observed (outcome-judged) | Declared (this schema) |
|---|---|---|
| First check | after runs used it | before any run uses it |
| Reference for "correct" | task success, quality from use | the author's declaration, tested |
| What cannot run | offered, then fails or is refused | removed by code before any model sees it |
| A lenient judge | keeps bad capabilities with no sign | its measured error is on the Verdict |
| A wrong output in AI4Research | becomes a claim; the plan can swap only to approved fallbacks | traced from the claim to the exact Binding and hash |

- **The guarantee**: a capsule blocked by its own declared precondition could not have completed in that state (2608.01050 p3). Observation can only give a rate, after the fact. → [[Predicate Parity]]
- **The limits**: a declaration can be false, so admission compares declared and observed effects, and certification tests parity. Passing a precondition grants no right to any effect.
- **The claim, stated narrowly** (after review): every check still observes behaviour. What changes is that the target is stated before use, and someone other than the builder checks it. Observation-driven curation can work (Library Drift +0.328); observation alone, by the builder or an unmeasured judge, can fail without a sign.
- **Who else does which** (companion Table 14): Alita-G and the Darwin Gödel Machine judge by task outcome; Symphony's fingerprint by quality from use; Contract2Tool infers contracts; skillhub reviews. *Don't Offer What Can't Be Done* declares, at selection only. jiuwenswarm declares dependencies and limits as prose a model reads.
