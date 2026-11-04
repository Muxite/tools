# Claim verification protocol

You are checking specific factual claims about source code against the source. Someone else wrote the claims.
Your job is to find out whether each one is true, **not** to agree with it.

## Ground rules

1. **You get the claim and nothing else.** Do not read `DESIGN.md`, anything in `notes/`, or another
   verifier's output. Those contain the reasoning that produced these claims, and reading them will bias you
   toward confirming. If a claim is ambiguous, say so in your report rather than going looking for what the
   author meant.
2. **Read-only.** Do not modify any file in any repository. Write only your own report file.
3. **No network.** Do not use WebSearch or WebFetch, and do not touch arXiv — a long sequential arXiv job is
   running on this machine and must not be disturbed.
4. **No clones, no WSL, no new processes beyond ordinary reads.** The repositories are already on disk.
5. **Quote what you find.** Every verdict cites a file path, a line number, and the text you read there. A
   verdict without a quote is not a verdict.

## Verdicts

Use exactly one per claim:

| Verdict | Meaning |
|---|---|
| `VERIFIED` | the claim is true as stated, and you quote the evidence |
| `REFUTED` | the claim is false, and you quote what is actually there |
| `PARTLY` | some of it holds and some does not — say precisely which part fails |
| `IMPRECISE` | literally true but misleading, or true only under a reading the wording does not support |
| `CANNOT-CHECK` | you could not determine it; say exactly what blocked you |

**`REFUTED`, `PARTLY` and `IMPRECISE` are the valuable outcomes.** The author of these claims has already been
wrong once in a way that mattered, by concluding a thing did not exist because a `grep` for the wrong word
returned nothing. Assume more of that. Specifically:

- When a claim says "there is no X" or "nothing does Y", **do not confirm it from a single grep.** Search for
  synonyms, look for the concept under other names, and check whether a subsystem you have not opened might
  implement it. A negative claim needs a real search behind it, and you should say which searches you ran.
- When a claim quotes a docstring or comment, check that the code actually does what the comment says.
- When a claim cites a line number, check the line number too. Code moves.
- When a claim gives a count, recount it yourself and say what you counted and how.

## Report format

Write to the output file named in your prompt. For each claim:

```
### C<n>. <the claim, restated in one line>
**Verdict:** VERIFIED | REFUTED | PARTLY | IMPRECISE | CANNOT-CHECK
**Evidence:** <file:line> — quoted text, and the command you ran if you counted something
**Note:** <only when the verdict is not VERIFIED: what is actually true, in one or two sentences>
```

Then a final section:

```
## What else I noticed
```

Anything you found while checking that the claims do not cover and that someone designing on top of this code
would want to know — especially a subsystem, a default, or a behaviour that contradicts the general shape the
claims imply. Keep it short and factual. This section is often the most useful part of the report.

Finish with a one-line tally: how many VERIFIED, REFUTED, PARTLY, IMPRECISE, CANNOT-CHECK.
