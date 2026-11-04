"""Revise text in the existing native PowerPoint package; preserve its geometry."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import shutil, json, hashlib

ROOT = Path(__file__).parent
NS = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main', 'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
for prefix, uri in NS.items(): ET.register_namespace(prefix, uri)
backup = ROOT/'history/rev3-before-human-interface'
backup.mkdir(parents=True, exist_ok=True)
for name in ['build_pptx.py', 'speaker-script.md', 'README.md']:
    shutil.copy2(ROOT/name, backup/(name+'.snapshot'))
shutil.copy2(ROOT/'output/Nuwa Talk rev3.pptx', backup/'Nuwa Talk rev3.pptx')

changes = {
1: {
'Use their way of thinking, judging and speaking on a new problem.':'Research a person and draft a skill around a selected trait.',
'Potential AI4R value: expert reasoning made reusable for research and review':'Potential AI4R value: a human-to-skill input for the Capability Capsule Factory',
},
2: {
'Yes, as a design pattern for building evidence-backed capabilities.':'Yes, narrowly: a human-to-skill input for the CC Factory.',
'Assessment: useful capability-authoring design pattern. AI4R integration and task-quality gains remain unmeasured.':'Assessment: useful input methodology; weak validation. AI4R retains its own evidence and qualification process.',
'Research task':'Person + target trait',
'problem + evidence':'a scoped authoring request',
'Existing AI4R agent':'Research and extract',
'applies the extracted procedure':'document the person and draft a skill',
'Critique or test plan':'Candidate for factory',
'then independent checks':'AI4R qualification required',
'Hypotheses':'Narrow value',
'Preserve competing models':'Translate a human reference',
'and their failure conditions':'into explicit candidate rules',
'Experiment design':'AI4R already has',
'Turn assumptions into':'Its own capability evidence',
'concrete evidence questions':'and qualification machinery',
'Evaluation':'Nuwa falls short',
'Retain criticism':'Persona fidelity and lint',
'and counterexamples':'do not prove task usefulness',
},
3: {
'AI4R lesson':'Human-to-skill use',
'Stable candidate principles':'Candidate trait evidence',
'Decision process beyond quotes':'Context for inferred rules',
'Adversarial evidence':'Evidence against the trait',
'Rules grounded in cases':'Compare actions with claims',
},
4: {
'Nuwa turns mental models into rules an agent can apply':'Nuwa packages inferred models and decision rules',
'Utility to AI4R':'Human-to-skill use',
'Reusable strategy with an explicit rationale':'Candidate strategy and rationale',
'Executable investigation steps':'Draft steps to test in AI4R',
'AI4R can reuse the reasoning procedure while keeping a neutral research voice.':'These filters select plausible rules; they establish neither truth nor task benefit.',
},
5: {
'Example: a Karpathy skill challenges an agent benchmark':'Example: a requested trait becomes candidate review rules',
'Illustrative derivation. Added value over a generic reviewer is untested.':'Generic review questions may do as well. A famous name adds no task evidence.',
},
6: {
"Nuwa's pitfalls suggest stronger checks for AI4R":"Nuwa's validations provide weak capability assurance",
'Nuwa template, fidelity rubric and examples @7812110. Limits and AI4R implications are our assessment.':'Pinned fidelity rubric + quality_check.py @7812110; saved local checker probe. Implications are our assessment.',
'Incomplete reconstruction':'Biased reconstruction',
'Public material leaves gaps':'Public records and a desired trait',
'and becomes outdated.':'can invite selective evidence.',
'Trace claims and label inference.':'Test counterevidence and attribution.',
'Authority from the voice':'50 points for resemblance',
'A convincing style can':'Stance (30) and style (20)',
'hide weak task evidence.':'dominate the 100-point rubric.',
'Use evidence to support conclusions.':'Similarity cannot qualify a capability.',
'Familiar test questions':'Tiny fidelity test',
'Known positions reveal':'3 known positions, 1 unfamiliar',
'little about new research tasks.':'case and 1 style sample.',
'Freeze unseen tasks and blind the scoring.':'No AI4R task baseline or gain shown.',
'Weak structural checks':'Checker fails open',
'Our empty-content probe':'A content-free placeholder',
'passed all 6 checks.':'passed 6/6, without sources.',
'Fail missing evidence and check meaning.':'Require evidence; test behavior.',
},
7: {
'Proposed AI4R design: a common lifecycle with different authoring work':'Nuwa contributes to the third input; AI4R owns capability evidence and qualification',
},
8: {
'One expert-derived review method is enough for a first trial':'A bounded trial of the human-to-skill interface',
'Proposed AI4R trial. Same-evidence comparison isolates the skill\'s contribution. No comparative result exists yet.':'Proposed trial: assess authoring utility first, then task benefit. No comparative result exists yet.',
'Choose one expert corpus':'Name + target trait',
'A documented reasoning method':'One bounded request',
'for one research responsibility':'with a strong source corpus',
'Make the use explicit':'Draft a candidate skill',
'Pinned skill and cutoff':'Verify trait and rule support',
'Sources separate from inference':'Track corrections and authoring cost',
'Compare on new tasks':'Qualify through AI4R',
'Same evidence and budget':'Same sources and budget',
'Against a generic checklist':'Compare with a generic checklist',
'Keep it when it adds useful, supported objections at an acceptable cost.':'Retain the interface only if it produces useful candidates at an acceptable cost.',
},
9: {
'A method worth testing in AI4Research':'A narrow contribution to the CC Factory',
'Assessment and proposed next step. AI4R adapts the extraction method; task-quality benefit remains unmeasured.':'Assessment: borrow the human-to-skill research workflow. AI4R supplies capability evidence, testing and admission.',
'Expert reasoning':'Human-to-skill',
'could become a reusable':'could become the third',
'research procedure.':'factory input.',
'Imitate extraction and evidence handling.':'Borrow person-and-trait research.',
'Measure whether research improves.':'Keep AI4R qualification in charge.',
'The next decision':'The next decision',
'Does one extracted procedure improve AI4R reviews on unseen work?':'Can this interface produce useful candidate skills?',
'One skill. One role. A fair comparison.':'One person. One trait. A qualified candidate.',
},
10: {'Backup: distinguish extracted methods from generic prompting':'Backup: task value requires a comparison beyond fidelity'},
11: {'Backup: governed use would pin the skill inside a bounded CC':'Backup: a human-derived skill still needs ordinary CC qualification'},
}
notes = {
1: "TIME 0:25. Nuwa researches a named person and drafts an instruction skill containing inferred models, decision heuristics, voice and limits. It approximates a public record; it does not recover private cognition or train weights. Our question is whether the human-to-skill methodology offers a useful additional input to AI4Research's Capability Capsule Factory. We should assess that narrow contribution critically.",
2: "TIME 0:55. Yes, narrowly: Nuwa offers a human-to-skill authoring interface for the CC Factory. A name and target trait become a scoped research request, followed by a candidate instruction skill. An extracted procedure is only a candidate input; AI4R must attach evidence and qualify task behavior. AI4R already has its own approach to evidence-backed capabilities. Nuwa does not supply a better assurance system. We borrow its person-and-trait research workflow; our factory retains responsibility for operationalizing a candidate, testing task behavior and admitting a capsule. Nuwa's fidelity scores and structural checks cannot establish research capability. The value claim is an interface design judgment, with actual authoring and task benefits still unmeasured.",
3: "TIME 1:05. Nuwa scopes a person and requested trait, then asks a host agent to research six streams: writings, conversations, expression, outside views, decisions and timeline. It saves sources, confidence and distinctions between direct statements, reports and inference. Primary-source preference and contradictions are useful research practices for this human-to-skill input. They are prescriptions, not proof that extraction is correct. A user-specified trait can bias source selection: first ask whether the person's documented record supports that trait, and retain contrary examples. Public repetition may reflect branding or repeated quotations. Firsthand material may still be inaccurate or selective. These source heuristics should inform candidate authoring, while AI4R's evidence process remains responsible for checking claims and capability behavior.",
4: "TIME 1:00. The product of exploration is a set of inferred models and rules. Nuwa asks for three to seven models that recur in at least two domains, generate new judgments and distinguish the person's perspective. It asks for five to ten concrete decision heuristics with cases, plus limits and tensions. These are subjective extraction filters, not validation of truth or utility. Distinctiveness can reward idiosyncrasy even when a generic method works better. The Karpathy examples here paraphrase the repository's skill; we have not independently verified these attributions. For AI4R's human-to-skill interface, treat every extracted model as a candidate with traceable support, counterevidence and an explicit scope. A rule only becomes a useful capability after our own task checks.",
5: "TIME 0:45. A request such as Karpathy plus reliability review can guide research and yield candidate questions about task coverage, tool failures and reproducibility. This example illustrates how a requested human trait becomes explicit draft rules. It does not show that Karpathy would answer this way or that the generated skill improves an AI4R review. These are familiar review questions that a generic checklist may produce equally well. The name can help a user express the requested perspective, but it provides no authority for an answer. The factory must test the resulting rules against the same task evidence and a competent baseline.",
6: "TIME 0:50. Nuwa's assurance is weak for capability claims. First, reconstructing a person from public material while targeting a chosen trait invites selection bias and attribution errors. Second, half the fidelity score rewards stance and style: 30 and 20 points. The remaining categories address boundary honesty, sources and structure, but none directly measures AI4R task improvement. Third, the prescribed behavioral test uses three known-position questions, one unfamiliar question and one style sample. Independent answer and judging agents are a useful separation, and the rubric recommends extra judges for important conclusions, but separate LLM agents can share model biases; this is not independent empirical task evidence. Fourth, the saved placeholder probe passed all six structural checks without sources. Missing or untyped sources return success, while keyword matches stand in for semantic checks. This demonstrates a checker defect, not that every Nuwa skill is poor. Its scores cannot justify admitting a research capability; AI4R retains its own evidence, behavioral tests and admission.",
7: "TIME 1:00. We propose three input interfaces to the Capsule Factory. An observed runtime gap produces a diagnosed requirement brief. A paper, repository and data provide a method to reproduce and adapt. A person's name plus target trait initiates human-focused source research and skill drafting, taking inspiration from Nuwa. This third route is Nuwa's relevant contribution. All routes produce candidates; AI4R owns the contract, body, evidence package, independent qualification and existing admission gate. A name cannot establish competence, and Nuwa's fidelity grade cannot replace our checks. Source preparation is separately authorized and pinned before offline build work. This is a proposed interface, not a claim of deployed integration or adoption of Nuwa's assurance system.",
8: "TIME 0:50. Trial the interface as an authoring tool first: choose one person, a defensible target trait and a strong corpus. Draft a candidate skill using the research and extraction workflow. Check attribution and contrary evidence; record unsupported rules, corrections, human effort and authoring cost. If the candidate is worth continuing, take it through AI4R qualification. The task comparison uses a plain reviewer, a generic checklist and the human-derived rules, all with the same frozen sources, task evidence, model, tools and runtime budget. Blind scoring on unseen tasks tests incremental utility. A useful interface can reduce the effort of specifying a capability without proving the human-inspired rules outperform a generic method. Report those outcomes separately.",
9: "TIME 0:30. Our recommendation is selective: borrow Nuwa's person-and-trait research workflow as a possible third input to the Capability Capsule Factory. We already have our own approach to evidence-backed capability production. Nuwa's reconstruction, tiny fidelity test and permissive structural checker provide insufficient assurance for that role. A familiar persona can be an accessible way to request a skill; the resulting artifact remains a candidate. Judge the interface by the useful candidates it produces and the effort it saves, then require ordinary AI4R task qualification and admission.",
11: "BACKUP. This is downstream of authoring. A human-derived instruction skill is a candidate body, not a capsule contract or permission grant. Pin source evidence, cutoff and rule support; define one bounded task with typed inputs and inspectable outputs. AI4R supplies tool/effect/budget constraints, task-level tests, versioning and admission. The semantic verifier remains declaration-and-output-only; source- and input-dependent checks belong in the protected host path. A Nuwa fidelity report can describe the approximation but cannot qualify this capsule. This is a proposed integration, not implemented deployment.",
}

with ZipFile(backup/'Nuwa Talk rev3.pptx') as src:
    files = {i.filename:src.read(i.filename) for i in src.infolist()}
presentation=ET.fromstring(files['ppt/presentation.xml'])
rels=ET.fromstring(files['ppt/_rels/presentation.xml.rels'])
targets={r.attrib['Id']:r.attrib['Target'].lstrip('/') for r in rels}
slidepaths=[]
for ident in presentation.find('p:sldIdLst', NS):
    target=targets[ident.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
    slidepaths.append(target if target.startswith('ppt/') else 'ppt/'+target)

for ordinal, path in enumerate(slidepaths, 1):
    xml=ET.fromstring(files[path])
    mapping=changes.get(ordinal,{})
    for el in xml.findall('.//a:t', NS):
        for old,new in sorted(mapping.items(),key=lambda item:len(item[0]),reverse=True):
            if el.text: el.text=el.text.replace(old,new)
    files[path]=ET.tostring(xml,encoding='utf-8',xml_declaration=True)
    if ordinal in notes:
        relpath=str(Path(path).parent).replace('\\','/')+'/_rels/'+Path(path).name+'.rels'
        relxml=ET.fromstring(files[relpath])
        nr=next(r for r in relxml if r.attrib['Type'].endswith('/notesSlide'))
        import posixpath
        np=posixpath.normpath(posixpath.join(posixpath.dirname(path),nr.attrib['Target']))
        nx=ET.fromstring(files[np])
        body=next(sp for sp in nx.findall('.//p:sp',NS) if sp.find('.//p:ph',NS) is not None and sp.find('.//p:ph',NS).get('type')=='body')
        tx=body.find('p:txBody',NS)
        original='\n'.join(el.text or '' for el in tx.findall('.//a:t',NS))
        source=original[original.find('\n\nSOURCES'):] if '\n\nSOURCES' in original else original[original.find('\nSOURCES'):]
        for p in list(tx.findall('a:p',NS)): tx.remove(p)
        for line in (notes[ordinal]+source).split('\n'):
            p=ET.SubElement(tx,'{'+NS['a']+'}p')
            r=ET.SubElement(p,'{'+NS['a']+'}r')
            ET.SubElement(r,'{'+NS['a']+'}t').text=line
        files[np]=ET.tostring(nx,encoding='utf-8',xml_declaration=True)
draft=ROOT/'.build-orange/Nuwa Human Interface draft.pptx'
with ZipFile(draft,'w',ZIP_DEFLATED) as out:
    for name,data in files.items(): out.writestr(name,data)

# Keep the legacy generator's content consistent without using it for authoring.
builder=(ROOT/'build_pptx.py').read_text(encoding='utf-8')
for mapping in changes.values():
    for old,new in mapping.items():
        builder=builder.replace(json.dumps(old,ensure_ascii=False)[1:-1],json.dumps(new,ensure_ascii=False)[1:-1])
import ast
tree=ast.parse(builder)
note_calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='note']
note_calls.sort(key=lambda n:(n.lineno,n.col_offset))
line_order=[0,4,2,1,3,5,6,7,8,9,10]
lines=builder.splitlines(keepends=True)
for ordinal,newnote in sorted(notes.items(),reverse=True,key=lambda item:note_calls[line_order[item[0]-1]].lineno):
    arg=note_calls[line_order[ordinal-1]].args[0]
    assert arg.lineno==arg.end_lineno
    line=lines[arg.lineno-1]
    lines[arg.lineno-1]=line[:arg.col_offset]+json.dumps(newnote,ensure_ascii=False)+line[arg.end_col_offset:]
(ROOT/'build_pptx.py').write_text(''.join(lines),encoding='utf-8')
finalizer=(ROOT/'finalize.mjs').read_text(encoding='utf-8').replace('Nuwa Orange draft.pptx','Nuwa Human Interface draft.pptx').replace('rev3 pipeline-order','rev3 human-interface')
(ROOT/'finalize.mjs').write_text(finalizer,encoding='utf-8')
print(draft)
