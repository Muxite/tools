# Meeting Notes: Intent Compiler Document Comparison

**Date:** October 8, 2026

## Experiment setup

- Reviewed a 2×2 comparison of:
  - Spec Kit with full documents
  - Spec Kit with compact documents
  - No Spec Kit with full documents
  - No Spec Kit with compact documents
- The build goal was to implement the Intent Compiler. Four Codex sessions ran in parallel, each using GPT-6.1-Sol at ultra reasoning effort.
- Each condition used a separate branch. The PRD and design document package were placed in special folders alongside one another; each package was split into a main document and context documents. The main documents cover the Intent Compiler.
- The prompt was standardized, and the same test was used for all four conditions.
- The Intent Compiler takes user text and produces `Research_Brief.json`. Its outputs include verification and gates, as well as two capability capsules.

## Document variants

- The compact PRD removes elaborated feature requirements.
- The compact design package removes elaboration about intent and detailed explanatory guidance. Schemas, fields, and components remain exactly the same.
- Compact design documents use three layers:
  1. **Layer 1:** Required human reading, designed to take about 15 minutes.
  2. **Layer 2:** Recommended reading about models and components.
  3. **Layer 3:** Schemas and fields for AI reference; humans do not need to read it.
- Writing and modifying the compact design package takes roughly 60% of the work required for the full package.

## Full-document results

- Reviewed the Spec Kit + full-documents result and the no-Spec-Kit + full-documents result, including their front ends and `intentIR.json` files.
- The AI judged the no-Spec-Kit + full-documents result to be better; human reviewers judged the Spec Kit + full-documents result to be better.
- The difference was marginal and mostly involved choices about how to use fields such as `idea` and `categories`. All required schema fields were present, and most were used.
- Both results included `out_of_scope`, but left it empty.
- The no-Spec-Kit result added a `model-eligibility` category. This label may be confusing: it could refer to models available to the system or models available in the context of the user prompt.
- Some `intentIR` fields may be ambiguous or overlapping. That is not necessarily a problem, since interpretation can determine what belongs in each field and what belongs in more than one.
- When the PRD and design documents are fully elaborated, Spec Kit appears to make little difference to the result.

## Compact-document results

- Compared the compact Spec Kit and compact no-Spec-Kit results.
- Neither result appears complete. Their site designs differ considerably from one another and are more minimal and less developed than the results based on the full document package.
- More debugging is needed to determine how far each compact result is from completion.

## Additional observations and questions

- **How specific should the design be about `intentIR`?** In both full-document runs, the AI followed the field definitions. The definitions allow some interpretation, but neither result appears incorrect. It remains open whether the design should prescribe more detail.
- The implementation process was not examined. It is unclear whether the AI in the capability capsule generated the JSON in one shot. The output looks good, but only one test input was used, so its durability and correctness across inputs are unknown.
- Both working programs return a large folder of artifacts, making `intentIR.json` and `Research_Brief.json` difficult to find.
- Reviewed the Spec Kit-generated Markdown files to understand how the agent chose its schema interpretation, but could not find that reasoning.

## Open questions and next steps

- Review `Research_Brief.json` for the results already examined.
- Test more execution branches for the Intent Compiler’s subnodes.
- Debug both compact results and assess how much work remains to complete each one.
- Consider whether the design should specify more precisely how `intentIR` fields should be interpreted.
- Inspect the implementation path that produces the JSON and test it with additional inputs to assess reliability.
- Make the key output files easier to locate among the generated artifacts.
- Find a way to make the agent’s schema interpretation and reasoning traceable in the generated documentation.
- The current comparison is not enough to decide whether to use Spec Kit or whether to use compact or full documents.
