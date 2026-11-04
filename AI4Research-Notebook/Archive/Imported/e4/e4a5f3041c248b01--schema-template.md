---
type: template
tags: [schema, template]
---

# Schema template

*Reference, not for review: the starting point for a new schema page.*

Copy the block below to start a new schema. First check the three cheaper options in the [invariants](invariants.md): an `ext` field (INV-18), a registry row (INV-13) or a policy value (INV-4). Most additions are one of those, not a new schema.

**A new schema is justified only when** it has one writer of its own (INV-3), its own readers, and its own lifecycle (it is created or kept at a different time from existing records). Make that argument when you propose it.

**After creating it:**
1. Add its stem to `RECORDS` in `tools/sync.py`.
2. Add it to the `reads`, `writes` or `stores` properties of the components that use it.
3. Add a row for it to the [sign-off tracker](schemas.md#sign-off-tracker).
4. Run `python tools/sync.py`.

Do not write `written_by`, `read_by`, `stored_by` or `traces` by hand: they are generated.

---

````markdown
---
type: schema
id: cc.<name>.v1
status: draft
owner: "<name>"
first_needed: "B1"
written_by: []
read_by: []
stored_by: []
traces: []
tags: [schema]
---

# <Name> · `cc.<name>.v1`

**What it is.** <Two sentences: what the record says was done, or what must be true.>

**Rules that matter most here:** <INV-n, ...>

A box becomes a clickable link in Obsidian when both of these hold:
- its label is exactly a page's file name, without `.md`;
- it is listed on the `class ... internal-link` line.

Use only ASCII in diagram labels, and no `;`.

## What: the core

Extends [`cc.common.v1`](common.md), with `scope.<run_id | candidate_id | library>`.

| Field | Type | Req | From | State | Description |
|---|---|---|---|---|---|
| `<field>` | `<type from the grammar>` | req | B1 | proposed | <What it means, who sets it, any constraint. Example: `<value>`> |

## How: lives elsewhere

| Rule or value | Where it lives |
|---|---|
| | a policy section, or a part page |

## Reuse

| Existing | Where (file:line) | Verdict |
|---|---|---|
| | | reuse as is / adapt / do not reuse, and why |

## Extension points

- <which lists are registries; what goes in ext; which optional parts switch on by kind>
