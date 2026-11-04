---
id: cc-strata-talk
status: proposed
source: Sources/Prompts/2026-11-02-cc-strata-methodology.txt
last_reviewed: 2026-11-02
next_action: Produce the brief and claim-evidence sheet from the approved CC example
---
# Short feature talk for the inference-engine workshop

**Audience:** other M2 feature owners who know the factory objective. **Decision:** agree how the CC owner will onboard one Strata operation and how the factory and lab can consume the resulting release. Budget 8–10 minutes and six slides, leaving the workshop hour for showing the files and resolving interfaces. The previous 13-slide fleet deck is supporting material.

| Slide | Question answered | Main editable visual and evidence |
|---|---|---|
| 1. Strata on one Spark | What does CC contribute to a real application? | One request with two outputs: reproduce the upstream baseline, then compare a candidate expert pack. Show the pinned upstream engine and a blank local-results slot. |
| 2. Two factories consume and produce different things | Who builds the capability and who builds the engine? | Swimlanes for CC Factory, Software Factory, lab and RSI. Label arrows with candidate CC, admitted digest, engine release, run request and evidence. Show reviewed intake and the feedback path. |
| 3. What actually ships in a capsule | How can an agent choose and use it? | One small manifest excerpt beside an exploded package showing a capability, typed port, check, OCI reference and native Strata manifest. Distinguish built-in fields, native references and the proposed binding by consistent color. |
| 4. Replaying the upstream build and benchmark | Why is the integration small enough to try? | Compare exact reused entrypoints with AI4R-owned adapters. Trace one inputs/outputs pair. Cite the Strata package writer, verifier and benchmark. Give the strongest reason for deferring a new workflow runtime. |
| 5. What the lab learns | How do we know the candidate helps? | Sequence the lease, stage, check, run and evidence commit. Next to it show storage, peak RAM, prefill, decode and quality gates. A smaller pack that misses decode goes back to the factory. Label any example numbers hypothetical. |
| 6. First deliverable and decision | What do the other feature owners need to agree? | Show a single signed release and paired evidence packet as exit artifacts. Ask for the benchmark fixture owner, one Spark reservation and the interface owner for admission. Give the rollback path. |

Start with the vault presentation brief and a ledger linking each claim to a source, scope and evidence status. Keep the key evidence visible. Put full source URLs, method, caveats and likely questions in speaker notes. Use a graph for ownership or data movement, an excerpt for a contract, and a small table where readers must compare alternatives. Use flat, readable layouts and consistent actor colors. Give every arrow a payload and check its route at normal viewing size. Split a crowded slide before shrinking the type. Rehearse with the exported PowerPoint, then render, visually inspect, correct and render again.

The editor should ask three questions before release. Can a teammate point to the field that lets an agent discover a tool? Can they name the different products of the two factories? Can they follow an unsuccessful result into a new factory build? If any answer depends on narration alone, revise the visual. See [[Presentation Library/Presentation Guide]], [[Presentation Library/Visual Design and Whitespace]] and [[Presentation Library/Production and Review]].
