# 5. Coordination support and continuity

**Key point:** Git-tracked context and low-cost automation can make cross-component change easier to coordinate.

## High-level design CI as a change radar

**Proposal:** When design changes, automated checks can catch broken links, missing sections, naming drift, schema/version changes and diagrams that need refresh. A bounded agent review can summarize likely affected modules, documents, evidence and unanswered questions. It can help notify the contributors working in those areas.

Agents should identify and explain likely issues. The team decides meaning and consequential changes. Agents do not silently rewrite design or approve a decision. Keep this support separate from product runtime gates, and add checks when experience shows they prevent real rework.

Integrated agents can also make it easier to maintain English and Chinese documents together. Linking versions and checking their structure and meaning helps the project keep both aligned as the design evolves.

## Keep context when contributors change

Use existing Git-tracked design and work records to retain decisions, rationale, component responsibility, open questions and next evidence. Avoid a second decision log. A new contributor should be able to find the current contract, connected consumers, why it exists, which evidence is current, and what remains open.

## Measure the effect

Start with a short trial. Check whether important design changes reach affected parts of the project, whether agent findings are useful, how much manual coordination they save, and whether they catch stale or mismatched information before implementation. Keep, improve or remove checks based on observed value.

This is an exploratory project without active users. Favor fast, reversible learning over production ceremony. AI can help draft, code and review, but measure its end-to-end effect. A 2025 METR randomized study found early AI tools slowed a small sample of experienced developers on mature open-source tasks, despite their expectations. That result does not predict this team. It does support measuring outcomes rather than assuming generated code saves time. [METR study](https://metr.org/Early_2025_AI_Experienced_OS_Devs_Study-paper.pdf).

NASA's traceability and decision-analysis practices explain why impact and rationale should persist. We borrow those engineering principles and tailor the process to our project. [NASA NPR 7123.1C](https://nodis3.gsfc.nasa.gov/displayAll.cfm?Internal_ID=N_PR_7123_001C_&page_name=all).
