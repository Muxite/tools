# 04 — Conventions, gates, and agent governance

The most transferable non-code artifact in this repo. dsh governs its *agents*
with the same rigor it governs its code, and it makes most of the rules
machine-checkable.

Source: `AGENTS.md` (155 lines), `packages/AGENTS.md`, `.agents/notes/README.md`,
`docs/AGENTS.md`, `scripts/`.

---

## 1. Agent Notes — mandatory, dated, classified, frozen

> **Every non-trivial change MUST add or update at least one Agent Note in the
> same PR.**

An **Agent Note** records a decision or proposal — *the why and what we gave up*,
"the parts code and docs can't carry."

**Path encodes two axes:** `{lifecycle}/{class}/yyyy-mm-dd-topic-title.md`

- **Lifecycle** (top folder) = status, and the file *moves* as status changes:
  `proposed/` → `implemented/` , or `rejected/`.
- **Class** (nested folder), from a **closed set** in `scripts/agent-note-tree.ts`:
  `feature` · `bug-fix` · `simplification` · `architecture` · `process` · `testing`.
  The classification gate rejects any other folder.
- The **date is when the topic was first proposed** (per git history), not when
  the file was written.

Counts at HEAD [verified]: **309 implemented · 21 proposed · 629 archived.**

### The rules that make it work

- **`implemented/` notes are kept current with what actually shipped.** When code
  later moves a file, renames a package, or changes a default, the note is updated
  in the same change — **facts only** (paths, names, structure), never the
  decision itself.
- **A note is never edited into a different decision.** Supersede it with a new
  one and cross-link both.
- **Consolidation has preconditions.** A fully superseded note may be merged into
  its owner and deleted, but only after preserving every unique rationale,
  alternative, consequence, required verification, and named coverage gap, and
  repairing every inbound link. *Partial* supersession does not qualify.
  "Removing one transport, default, implementation, or presentation is partial
  supersession, as is any surviving durable data or compatibility handling."
  Explicitly forbidden: relying on git history as the only copy of rationale.
- **The archive is append-only and permanently frozen.** Archival may only move
  the English/Chinese/sidecar triplet, retain `Status: implemented`, insert an
  `Archived: YYYY-MM-DD` line, re-record the sidecar hash, and repair inbound
  links. After that: no editing, translating, reformatting, moving, or deleting.
  Archived notes are **not authority for current behavior**.
  `verify-archived-agent-notes.ts` enforces the class tree, complete triplets,
  archive metadata, sidecar hashes, and an append-only frozen-content manifest.
- **No index file.** Deliberate — the lifecycle/class tree *is* the inventory,
  and there's an Agent Note explaining why a generated index was removed.
- **Cross-references must be relative markdown links**, never bare prose or
  numbers, so they are mechanically checkable and survive folder moves.

**Takeaway for our own notes:** the two ideas worth copying are (a) *the note's
status lives in its path, so moving the file is the state transition*, and
(b) *implemented notes are maintained as current fact while archived ones are
frozen and explicitly stripped of authority.* Our notes currently mix "what we
found" with "what is true now"; dsh separates those by construction.

## 2. The gate wall [verified]

`scripts/` holds **215 scripts, 55 of them `verify-*`**. A selection, because the
list itself tells you what they consider worth automating:

| Gate | Enforces |
|---|---|
| `verify-application-entrypoints` | no Node app path bypasses the `dsh` CLI |
| `verify-export-jsdoc` | every function-like export has `@param`/`@returns` |
| `verify-package-readme-model-experience` | every package README covers "Model Experience" (with an explicit allowlist for model-agnostic packages) |
| `verify-package-readme-limitations` | every package README carries `## Known Limitations and Deferred Work` |
| `verify-client-ui-i18n` | **rejects hardcoded UI copy** — product text must route through typed dictionaries and `t` |
| `verify-translation-pairing` / `verify-translation-prompt` | the `.md` / `.zh.md` / `.i18n.yaml` triplet stays consistent |
| `verify-doc-budgets` | per-document **word budgets** (raising a ceiling is a deliberate act) |
| `verify-doc-refs`, `verify-md-links`, `verify-md-wrap`, `verify-mermaid` | docs hygiene incl. one-physical-line-per-paragraph |
| `verify-agent-note-format` / `-classification` / `verify-archived-agent-notes` | the Agent Note system above |
| `verify-cordis-config` | bare plugins in `cordis.yml` appear in the resolver manifest's `dependencies` |
| `verify-runtime-closure`, `verify-package-dependencies`, `verify-optional-dependency-imports`, `verify-npm-install-layout` | dependency and publish correctness |
| `verify-package-invariants` | runtime invariants are only published where they're legitimate (see §4) |
| `verify-type-equiv`, `verify-node-next-types` | type-level consistency; NodeNext consumer compatibility |
| `verify-skill-invocation-metadata` | the repo's own `.agents/skills/` metadata |

Aggregates: `pnpm run doc-sync` (all documentation gates),
`pnpm run test:docs` (quick, no build), `pnpm run hygiene`,
`pnpm run duplication` (cross-file TypeScript clone detection via jscpd).

**Coverage gate:** `pnpm run test:coverage` — **per-file 100% on
`packages/*/*/src`**. `AGENTS.md` is careful to say `test:coverage`, *not*
`test`, is the CI coverage gate.

**Test tiers:** `test` (unit) · `test:e2e` (real API, self-skips without
`DEEPSEEK_API_KEY`) · `test:expected` (owner-local process expectations) ·
`test:snapshot` (**keyless recorded-session replay** through shipped profiles) ·
`benchmarks/` (performance gates).

## 3. Agent working discipline

`AGENTS.md` tells agents how to *behave*, not just what to write:

- **"Run relevant checks locally"** — match evidence to the surface: focused
  behavior tests, model/user-output snapshots, `doc-sync` for docs, built smokes
  for published paths, real-API e2e for providers.
- **"Never default to the full suite"** and never repeat a passing check for
  commit or push. CI owns exhaustive coverage and the platform matrix. Rehearse
  everything locally only on explicit request, for CI diagnosis, or for an
  irreducibly repo-wide change.
- **"Report only commands run."**
- **Host sandbox failures:** if a command fails because the sandbox blocks
  credentials/network/IPC/watching, retry unchanged with the **narrowest** host
  escalation — and **"require sandbox evidence; never bypass test failures or the
  product sandbox."**
- **12 repo-owned skills** in `.agents/skills/`: `dsh-pre-push-checks`,
  `dsh-code-review`, `dsh-doc`, `dsh-prose-standard`, `dsh-find-simplifications`,
  `dsh-archive-agent-notes`, `dsh-merging-stacked-prs`, `dsh-ci-test-reliability`,
  `dsh-speed-up-perf`, `dsh-translate-docs`, `dsh-trim-cot-leakage`,
  `record-browser-gif`.
  - `dsh-trim-cot-leakage` is the interesting one: a dedicated workflow for
    removing chain-of-thought residue from committed prose.
  - `dsh-translate-docs` may run **only on explicit user invocation**.

## 4. Code rules worth remembering

The ones that would actually change how you write code here:

- **Registrations are effects.** Every contribution goes through `ctx.effect()` /
  `ctx.on()`; a registry's `register()` returns the disposer.
- **Trust TypeScript at typed same-process boundaries.** Do **not** add runtime
  validation, fallbacks, or hostile-input tests for values the static interface
  requires. Validate at the *real* boundaries: parser/config, queued, model/tool
  JSON, durable/file, worker, process, wire.
- **Explicit > implicit at package boundaries.** Defaulting is an explicit
  `resolve(request): Spec` step in the owning implementation — **never a hidden
  `?? default` inside `run()`**. The `dsh-shell` request/spec split is the template.
- **No hardcoded tunables in plugins.** Deployment-varying choices are validated
  `Config` fields changeable from `cordis.yml`. "A `DEFAULT_*` constant or test
  hook is not configurability." Protocol constants, external specs, and security
  invariants stay fixed.
- **Misconfiguration fails loud** at load when self-contained, otherwise at the
  earliest resolvable point. **Never silently skip a missing referent.**
- **Opaque cross-boundary ids are branded** (`Branded<B>` from `dsh-brand`), never
  bare `string`.
- **Runtime invariants assert *owned relationships*.** Publish `./invariant` only
  when independent observations can diverge — otherwise omit it and record why in
  the README. Explicitly invalid: empty installers, and checks of service
  presence, plugin metadata, effects, or fixed examples.
- **Source plane vs artifact plane, never mixed.** Static gates and tests resolve
  workspace imports through tsconfig `paths` to `src`; gates that consume built
  `lib/` declare that dependency.
- **Switch on discriminant tags**; closed unions end in `assertNever`.
- **An empty `catch` names what it swallows** and why nothing else can reach it,
  and the `try` stays one statement.
- **Prefer symmetry for parallel values** — "unexplained asymmetry usually
  signals a missed extraction."
- **Tests describe behavior, not correctness.** Change obsolete behavior *with*
  its tests and explain why in the PR.
- **Prefer maintained dependencies over hand-rolling** when they genuinely delete
  owned code and tests.
- Files end with exactly one trailing newline, gated by pre-commit
  `git diff --cached --check`.

## 5. The prose standard

There is an enforced house style for comments and docs, and it is unusually
specific:

> "Comments and docs state **complete contracts and context, not reasoning
> transcripts**. Use direct, concrete terms. **Do not use metaphors.**"

> "Before writing `contract`, `boundary`, or `shape`, ask whether a more exact
> term names the subject: write `response fields`, `JSON validation`, or `ESM
> exports` instead of `response shape`, `validation boundary`, or `module shape`."

`contract` is reserved for preconditions, postconditions, invariants, and
compatibility promises. `boundary` is reserved for a literal process, wire,
security, transaction, or lifecycle boundary. Also banned: narrating control flow
or tests, preserving review history, restating code. Keep behavior, failure,
timing, ownership, and safe-use facts; **link** the rationale.

Plus: **current-state prose, one physical line per paragraph, one home per fact,
and word budgets** (`verify-doc-budgets`).

**This is worth adopting.** "One home per fact" and "current-state prose" are
exactly the two failure modes our own multi-panel notes are prone to.

## 6. Git and PR process

- **Choose PR history deliberately.** Split independent changes; fix the
  introducing PR before propagation.
- Rewrites use `--force-with-lease`, **abort on remote movement, never raw
  `--force`**; preserve an in-progress merge-forward checkpoint before taking a
  newer base.
- **Labels:** exactly one `kind/*`, all material `area/*`, plus a native Issue Type.
- Native GitHub stacks with optional rebases; `gh stack sync` then validate
  immediately; never merge before checks pass.
- Observed at HEAD [verified]: branch names like
  `worktree/release-0.1.5-sync-master` and `turtle/ci-smoke-20260910-1820` —
  i.e. heavy worktree- and automation-driven development.
- **Both SDKs project the loop:** agent-loop, session-lifecycle, and
  `SessionEventMap` changes must update **TypeScript and Python SDK expected
  outputs in the same PR** — and `pnpm run test` covers neither, so this is a
  documented manual-vigilance point.
