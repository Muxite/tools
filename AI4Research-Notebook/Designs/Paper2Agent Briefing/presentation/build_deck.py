"""Write deck.json for the Paper2Agent talk (revision 6: ten slides in the file, about six minutes).

Run: python build_deck.py && tundlekit deck lint deck.json && tundlekit deck build deck.json -o "Paper2Agent Decision Talk.pptx"
"""
import json
from pathlib import Path

HERE = Path(__file__).parent


def table(rows, widths, size=None):
    block = {"kind": "table", "rows": rows, "widths": widths}
    if size:
        block["size"] = size
    return block


def point(text):
    return {"kind": "point", "text": text}


def fig(name):
    return {"kind": "figure", "path": "figures/" + name}


main = [
    {"type": "title",
     "title": "Paper2Agent: research as capabilities",
     "subtitle": "What it does, why it matters to AI4Research, and how it could fit capability capsules",
     "byline": "Overview, October 2026",
     "notes": {"time": "0:15",
               "say": "Paper2Agent turns research code into tools an agent can use. The short answer: yes, it is a pattern worth adapting for AI4Research capsules."}},

    {"type": "content", "eyebrow": "Takeaway",
     "title": "Worth adapting as a capability-production pattern",
     "stage": "gates",
     "source": "Synthesis of the slides that follow; claim status is in the claim ledger",
     "body": [table([["Point", "Summary"],
                     ["What it is", "A workflow that turns a research paper and its code into tested tools an agent can call, plus a reading skill for the paper."],
                     ["Why it matters", "AI4Research could adapt it as a capability-producing process, and package suitable generated tools as candidate capability capsules."],
                     ["Qualification", "A proposed integration pattern. Not an existing M1 capability, and not a guarantee of scientific correctness."]],
                    [2.6, 9.2], 20)],
     "thus": "the rest of the talk shows how it works, what it gives us, and where it fits",
     "notes": {"time": "0:30",
               "say": "The takeaway. Paper2Agent is a repeatable workflow that turns a paper and its code into tested tools an agent can call. AI4Research could adapt it to produce candidate capsules. It is a proposed pattern, not an M1 capability, and no guarantee of scientific correctness."}},

    {"type": "content", "eyebrow": "Method",
     "title": "How it works: prepare, run, wrap, check, package",
     "stage": "build",
     "source": "Paper2Agent repo at commit 8c2d059, skill instructions and orchestration.md; read, not run",
     "body": [fig("workflow.png")],
     "thus": "upstream code runs first, wrappers stay thin, and each stage records evidence",
     "notes": {"time": "1:00",
               "say": "Two branches. The paper branch builds a reading skill; it is secondary here. The code branch has six gated stages. Select tasks tied to real upstream code. Run the upstream code first to get reference results. Write thin wrappers that turn example code into callable operations. A fresh verifier compares wrapper and upstream, and can repair the wrapper. Mount the tools and make real calls. Package a ZIP and test it from a clean location. The system does not invent an implementation from the paper. It uses the existing software and examples to prepare tested interfaces. We read these instructions at a pinned commit and have not run them.",
               "asked": ["Does it need a special host: yes, it assumes a coding agent host that runs skills and spawns parallel agents"]}},

    {"type": "content", "eyebrow": "Output",
     "title": "What comes out, and what the authors report",
     "stage": "external",
     "source": "Nature 2026 version, as recorded in our evidence notes and not re-checked; the arXiv version reports different numbers",
     "demonstrated_by": {"paper": "Reimagining research papers as interactive AI agents",
                         "setup": "Nature 2026, authors' benchmarks"},
     "body": [table([["Reported finding", "Scope", "Reported score"],
                     ["Novel questions on one genomics tool", "15 questions, 5 runs", "100% vs 78.7% for Claude with the repository"],
                     ["Execution tasks from non-biology papers", "10 papers, 42 tasks, 5 runs", "98.1%"],
                     ["Conversion across papers", "100 papers, 599 proposed tools", "74 papers converted; 593 tools pass automated validation"]],
                    [4.4, 3.4, 4.0]),
              point("Automated tool preparation looks feasible across many research packages. It does not show performance in AI4Research.")],
     "thus": "feasibility evidence; local benefit remains unmeasured",
     "notes": {"time": "0:45",
               "say": "What comes out is callable tools plus a reading skill. On fifteen new questions about one genomics tool, the authors' agent scores one hundred percent against seventy-nine for Claude reading the repository. On ten non-biology papers it scores ninety-eight. Across a hundred papers, seventy-four converted, and five hundred ninety-three of five hundred ninety-nine tools passed automated validation. That suggests feasibility at scale. It does not show performance in AI4Research.",
               "asked": ["Are these numbers verified: they are recorded in our notes from the Nature version and were not re-checked here; metric definitions are in the paper", "Does 593 of 599 mean correct: no, it means the tool passed automated validation"]}},

    {"type": "content", "eyebrow": "Value",
     "title": "Why it matters to AI4Research",
     "stage": "library",
     "source": "Our assessment; potential benefits to evaluate, not measured results",
     "body": [table([["Potential value", "What it means for AI4Research"],
                     ["Reuse existing scientific software", "Agents call established implementations instead of regenerating analysis code for each task"],
                     ["Prepare once, invoke repeatedly", "Setup, interfaces and validated execution paths are reused across supported tasks"],
                     ["Preserve source links", "A capability stays tied to its repository revision, examples and test evidence"],
                     ["Grow the capability library", "External research software yields candidates for review and admission"],
                     ["Reuse the preparation steps", "Acquisition, environment preparation and packaging serve other capability-building work"]],
                    [4.2, 7.6], 16)],
     "thus": "capsules are the abstraction; Paper2Agent is a process for making some of them",
     "notes": {"time": "0:50",
               "say": "Why it matters. Agents reuse established implementations instead of regenerating analysis code. Setup and execution paths are prepared once and reused. A capability stays tied to its source revision and evidence. External research software becomes a source of candidates for review. And the preparation steps serve other capability building. Capsules already give us the abstraction. Paper2Agent suggests a process for making some of them. These are benefits to assess, not measured results."}},

    {"type": "content", "eyebrow": "Fit",
     "title": "One example, end to end: a clustering capability",
     "stage": "freeze",
     "source": "Illustrative mapping, not an implemented integration; the capsule fields are our proposal",
     "body": [fig("example.png")],
     "thus": "an MCP package is not yet a capsule, and admitting the factory does not admit its outputs",
     "notes": {"time": "1:00",
               "say": "One operation, end to end. A notebook clusters a fixed example dataset. The factory gets a pinned source snapshot from a separate acquisition capsule, prepares the environment, extracts the operation, tests and packages it. That package is not yet a capsule. It is adapted to the capsule contract: dataset artifact and parameters in; cluster labels, plots and a run record out; declared environment and limits. A capsule may expose one operation or a coherent set. It then needs independent admission before an authorized agent can invoke it. Two calls: the factory call prepares a candidate; the product call runs the admitted capability. Admitting the factory does not admit its outputs. This is illustrative, and building it needs an authorized preparation path and adaptation to current contracts.",
               "asked": ["Why not one big composite now: composites are deferred in M1, and member-level checks must survive inside one", "Is source acquisition allowed today: not for intake, it needs its own authorized preparation path"]}},

    {"type": "content", "eyebrow": "Limits",
     "title": "One limit: the same sources build the tool and check it",
     "stage": "claims",
     "source": "Our reading of the design plus repo text (runtime.md, orchestration.md); risks to check, not findings",
     "body": [fig("leakage.png")],
     "thus": "a pass supports fidelity on tested cases, not independent scientific validation",
     "notes": {"time": "0:50",
               "say": "One limit matters for how we read the evidence. The checks come from the same tutorials and code the tools were built from, and the verifier may repair a wrapper until it passes. So the checks primarily establish that selected tools reproduce tested upstream behavior. That is good evidence of faithful wrapping. They do not independently validate the underlying science or guarantee behavior on every dataset. Integration also depends on usable code, accessible data, licensing and a supported environment. These are risks read from the design, not a claim that the authors numbers are wrong.",
               "asked": ["Is this leakage: not in the strict sense, answers are withheld from the evaluated agent; the issue is that building and testing share one source", "Is the fresh verifier independent: it is a different agent, but it can repair the code until the tutorial-derived tests pass"]}},

    {"type": "content", "eyebrow": "Next",
     "title": "Worth adapting: the integration direction and a small next step",
     "stage": "gates",
     "source": "Proposed direction; to reconcile with PRD V10 and the maintained M1 design before any implementation",
     "body": [table([["Topic", "Position"],
                     ["Value", "Converts research implementations into reusable, source-linked tools"],
                     ["Capsule fit", "The factory and its generated tools are separate capsule candidates; acquisition is its own capsule"],
                     ["Bounded assurances", "Tests cover selected operations. Reference matching shows fidelity, not scientific validation. Licences, data and hardware can block a tool"],
                     ["Next step", "Map one representative repository into the capsule contract and list the adaptations. A bounded pilot is the follow-on"]],
                    [2.8, 9.0], 18)],
     "thus": "next step: one worked mapping, not an adoption",
     "notes": {"time": "0:30",
               "say": "To close. The value is turning research implementations into reusable, source-linked tools. The factory and its tools are separate capsule candidates, with assurances bounded to tested cases. The next step is small: map one repository into the capsule contract and list the adaptations. A bounded pilot is the follow-on, in the backup."}},
]

backup = [
    {"type": "content", "eyebrow": "Backup", "insert": True,
     "title": "A bounded pilot: one repository, hidden tests written first",
     "stage": "gates",
     "source": "Proposed pilot; thresholds not set; reconcile with PRD V10 before any implementation",
     "body": [table([["Pilot element", "Design"],
                     ["Three arms", "Direct use of the repository, a governed wrapper, a CC-admitted wrapper"],
                     ["Held constant", "Same pinned repository, data, model, permissions and preparation budget"],
                     ["Fixed before generation", "Required capabilities and hidden changed-input and failure tests, written by an evaluator, not the verifier"],
                     ["Against coupling", "Fresh data from after the paper; questions beyond the tutorials; coverage reported, not only pass rate"],
                     ["Measured", "Capability coverage, hidden-test results, preparation cost, admission outcome, maintenance burden"],
                     ["Continue if", "Source-linked candidates pass the held-out gate at manageable cost"],
                     ["Stop or narrow if", "Licence, data, environment or fidelity fails, or the wrapper adds little"]],
                    [3.2, 8.8], 14)],
     "thus": "a pass covers the cases tested; it does not prove scientific truth",
     "notes": {"time": "0:30", "say": "Backup: the pilot design, with controls against the coupling points."}},

    {"type": "content", "eyebrow": "Backup", "insert": True,
     "title": "Where today's M1 stands against this workflow",
     "stage": "binding",
     "source": "Designs/Paper2Agent Briefing/1 Decision brief; proposals, not adopted M1 behavior",
     "body": [table([["Current M1 shape", "Gap", "Minimum proposed resolution"],
                     ["Fixed research workflow, one Delivery leaf", "A factory needs a different terminal product and stage links", "Amend workflow policy with a capability-factory profile; pilot a flat plan"],
                     ["Agent and tool CCs only; composition deferred", "No factory composite today", "Flat orchestration first; decide on composites after pilot evidence"],
                     ["Offline Builder; intake excludes direct cloning", "No general source-acquisition route", "An authorized preparation handoff with pinned provenance and licence findings"],
                     ["Narrow Screening RSI target", "A factory may touch resources, CCs or plans", "Keep target scope explicit; do not imply whole-system RSI authority"]],
                    [3.6, 3.8, 4.4], 14)],
     "notes": {"time": "0:30", "say": "Backup: the M1 gaps and the smallest resolution for each."}},
]

deck = {"meta": {"id": "paper2agent-decision-talk", "title": "Paper2Agent: research as capabilities",
                 "inserts": "hidden", "budget": {"target": "7:00", "max": "8:00"}, "words_per_second": 2.3},
        "slides": main + backup}
(HERE / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False), encoding="utf-8")
print("wrote deck.json")
