---
id: amendment-ccav-evidence
status: source-snapshot
source: M1 source commit d3d7f565c6c05ccf764fe0780fde149b7dc89b95
last_reviewed: 2026-10-21
next_action: Recheck file receipt against selected implementation checkout before coding
---
# Portable evidence snapshot

These excerpts were captured from source commit `d3d7f565c6c05ccf764fe0780fde149b7dc89b95`. Hashes cover the complete source blobs returned by `git show`, not these shortened excerpts. Verify the receipt against the selected coding checkout before implementation. The commit is not asserted to be deployed.

## Runtime verifier payload (`jiuwenswarm/research/gate.py:86-102`)

SHA-256: `9a3ead19679d170fda062c394591b579c38916f8186c02af935852fecc8a039a`

```python
async def review(self, declaration_ref, output_ref, profile_ref, review_context_ref, port, invoke, *, zip_output=False):
    declaration = self.store.read_blob(declaration_ref)
    output = self.store.read_blob(output_ref)
    profile = self.store.read_record(profile_ref, contract_id="checking-profile")
    criteria = [c for c in profile["criteria"] if c["target_port"] in (None, port)]
    instructions = self.store.read_blob(profile["instruction_ref"]).decode("utf-8")
    payload = {"subject_declaration": declaration.decode("utf-8"), "subject_output": output.decode("utf-8")}
    raw = await invoke(json.dumps(payload, ensure_ascii=False), system=instructions)
```

The review manifest may refer to original inputs as local evidence identity; the model payload above does not pass those inputs. Keep the invariant precise: runtime verifier sees the declaration and exact output only, plus separately pinned review instructions/criteria. It must not receive original input values, hidden fixtures, keys, or hidden case outcomes. The evaluated producer receives the one case input assigned to its active invocation; it cannot enumerate the held-out suite or query keys/results.

## Existing binding/dispatch seam (`jiuwenswarm/research/runner.py:48-60,648-675`)

SHA-256: `affcb51f2c9830b146afafa3321ad35159b56d6bcfe57840f7c5604b564c3998`

```python
key = (cc_id, version, declaration_sha256)
...
handler, pinned = self.registry.resolve(identity["name"], identity["version_label"], declaration_sha256)
if pinned and tuple(binding["implementation_refs"]) != pinned:
    raise ResearchError("carrier_pin_mismatch", ...)
call = handler.execute if hasattr(handler, "execute") else handler
produced = await asyncio.wait_for(pending, remaining_deadline)
if not isinstance(produced, dict): raise ResearchError("output_invalid", ...)
```

This is a candidate adapter seam, not permission for a candidate to own registry, gate, or evidence authority. Existing host output capture and gate remain authoritative.

## Maintained design boundary

The captured branch's design describes mandatory checks and host-owned release. Its top-level product navigation still points to the October 13 PRD (255,245 bytes, hash beginning `890c63ee`). However, its actual M1 task register and source-baseline use October 15 V10 (`source/PRD/PRD_Oct_15.md`, 270,791 bytes, including an extra terminal LF versus the separately maintained canonical receipt). The maintained `ai4r_muk` product navigation identifies October 15 V10 as current. These are different source pointers; the task register is not registration-pending. Preserve and reconcile this conflict instead of claiming the older embedded design receipt is V10. No product-source replacement is authorized by this evidence excerpt.
