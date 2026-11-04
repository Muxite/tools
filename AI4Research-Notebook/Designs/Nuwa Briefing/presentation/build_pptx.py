"""Nuwa, orange revision: a person becomes a skill; value and use in AI4Research."""
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = Path(__file__).parent
OUT = HERE / ".build-orange" / "Nuwa Orange draft.pptx"

# Orange palette: burnt orange for Nuwa, terracotta for application, warm neutrals for evidence.
BG, INK, GREY, RULE = "FFFBF6", "34261D", "776A5E", "E5D8CA"
ORANGE, ORANGE_L = "B94D0B", "FFF0DE"
TERRA, TERRA_L = "8E3E20", "F8E4D9"
AMBER, AMBER_L = "C35A0C", "FFF0D9"
PANEL = "F3EDE4"
FONT = "Segoe UI"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def rgb(h):
    return RGBColor.from_string(h)


def put(shape, paras, size=16, color=INK, bold=False, align="c", anchor="m", inset=0.08, spacing=None):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(inset)
    tf.margin_top = tf.margin_bottom = Inches(0.04)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    if isinstance(paras, str):
        paras = [paras]
    for i, p in enumerate(paras):
        spec = p if isinstance(p, dict) else {"t": p}
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = {"c": PP_ALIGN.CENTER, "l": PP_ALIGN.LEFT, "r": PP_ALIGN.RIGHT}[spec.get("align", align)]
        if spacing or spec.get("before"):
            para.space_before = Pt(spec.get("before", spacing or 0))
        run = para.add_run()
        run.text = spec["t"]
        f = run.font
        f.name = FONT
        f.size = Pt(spec.get("size", size))
        f.bold = spec.get("bold", bold)
        f.italic = spec.get("italic", False)
        f.color.rgb = rgb(spec.get("color", color))


def shape(sl, kind, x, y, w, h, fill=None, line=None, lw=1.5, dash=False, adj=None):
    s = sl.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    s.shadow.inherit = False
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(lw)
        if dash:
            s.line.dash_style = MSO_LINE.DASH
    else:
        s.line.fill.background()
    if adj is not None:
        s.adjustments[0] = adj
    return s


def rbox(sl, x, y, w, h, fill=None, line=None, lw=1.5, dash=False, adj=0.12):
    return shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line, lw, dash, adj)


def doc(sl, x, y, w, h, fill="FFFFFF", line=GREY, lw=1.5):
    return shape(sl, MSO_SHAPE.FOLDED_CORNER, x, y, w, h, fill, line, lw)


def text(sl, x, y, w, h, paras, **kw):
    tb = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    put(tb, paras, **kw)
    return tb


def arrow(sl, x1, y1, x2, y2, color=INK, w=1.75, dash=False, head=True):
    c = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(w)
    if dash:
        c.line.dash_style = MSO_LINE.DASH
    if head:
        etree.SubElement(c.line._get_or_add_ln(), qn("a:tailEnd")).set("type", "triangle")
    return c


def marker(sl, x, y, label, color=AMBER, d=0.36):
    s = shape(sl, MSO_SHAPE.OVAL, x, y, d, d, fill=color)
    put(s, label, size=13, color="FFFFFF", bold=True, inset=0)
    return s


def new(title=None, source=None, notes="", n=None, tag=None, backup=False):
    sl = prs.slides.add_slide(BLANK)
    sl.background.fill.solid()
    sl.background.fill.fore_color.rgb = rgb(BG)
    if title:
        text(sl, 0.6, 0.4, 12.1, 1.0, title, size=30, bold=True, align="l", anchor="t", inset=0)
    if source:
        text(sl, 0.6, 6.72, 11.0, 0.3, source, size=11, color=GREY, align="l", inset=0)
    if title:
        label = "Nuwa" + ("  /  Backup" if backup else "")
        text(sl, 0.6, 7.08, 6.0, 0.28, label, size=10, color=GREY, align="l", inset=0)
        if n:
            text(sl, 11.7, 7.08, 1.03, 0.28, str(n), size=10, color=GREY, align="r", inset=0)
    if tag:
        t = rbox(sl, 0.6, 1.05, 2.13, 0.34, fill=ORANGE_L, line=None, adj=0.5)
        put(t, tag, size=11, color=ORANGE, bold=True, inset=0.04)
    sl.notes_slide.notes_text_frame.text = notes
    if backup:
        sl._element.set("show", "0")
    return sl


def table(sl, x, y, widths, rows, size=14, rh=0.56):
    gs = sl.shapes.add_table(len(rows), len(widths), Inches(x), Inches(y), Inches(sum(widths)), Inches(0.5 + rh * (len(rows) - 1)))
    tbl = gs.table
    pr = tbl._tbl.tblPr
    pr.set("firstRow", "0")
    pr.set("bandRow", "0")
    sid = pr.find(qn("a:tableStyleId"))
    if sid is not None:
        sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"  # no style, no grid
    for j, w in enumerate(widths):
        tbl.columns[j].width = Inches(w)
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(0.5 if i == 0 else rh)
        for j, val in enumerate(row):
            c = tbl.cell(i, j)
            c.fill.background()
            c.margin_left = c.margin_right = Inches(0.08)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            head = i == 0
            put(c, val, size=size - 2 if head else size, color=GREY if head else INK, bold=head, align="l", inset=0.08)
            tcPr = c._tc.get_or_add_tcPr()
            ln = etree.Element(qn("a:lnB"), w="12700" if head else "9525")
            sf = etree.SubElement(ln, qn("a:solidFill"))
            etree.SubElement(sf, qn("a:srgbClr")).set("val", INK if head else RULE)
            tcPr.insert(0, ln)
    return tbl


PIN = "7812110bf7e5a2b01b6aa5a738568044121bbfa2"
URL = f"https://github.com/alchaincyf/nuwa-skill/blob/{PIN}/"
SOURCES = {
    "core": URL + "SKILL.md",
    "framework": URL + "references/extraction-framework.md",
    "template": URL + "references/skill-template.md",
    "rubric": URL + "references/fidelity-scorecard.md",
    "checker": URL + "scripts/quality_check.py",
    "karpathy": URL + "examples/andrej-karpathy-perspective/SKILL.md",
    "musk": URL + "examples/elon-musk-perspective/FIDELITY.md",
}


def note(script, *keys, local=""):
    return script + "\n\nSOURCES\n" + "\n".join(SOURCES[k] for k in keys) + ("\nLOCAL CONTEXT\n" + local if local else "")


def card(sl, x, y, w, h, title, body, color=ORANGE, body_size=18):
    rbox(sl, x, y, w, h, fill="FFFFFF", line=RULE, adj=0.05)
    shape(sl, MSO_SHAPE.RECTANGLE, x, y, w, 0.07, fill=color)
    text(sl, x+0.22, y+0.22, w-0.44, 0.55, title, size=19, bold=True, color=color, align="l", anchor="t", inset=0)
    text(sl, x+0.22, y+0.95, w-0.44, h-1.07, body, size=body_size, align="l", anchor="t", inset=0, spacing=11)


def node(sl, x, y, w, h, title, sub="", color=ORANGE, filled=False, size=18):
    b=rbox(sl,x,y,w,h,fill=color if filled else "FFFFFF",line=color,adj=0.06)
    paras=[{"t":title,"bold":True,"size":size,"color":"FFFFFF" if filled else color}]
    if sub: paras.append({"t":sub,"size":14,"color":"FFF0DD" if filled else GREY,"before":6})
    put(b,paras,inset=0.08)
    return b


def person(sl, x, y, scale=1, color=ORANGE):
    shape(sl, MSO_SHAPE.OVAL, x+0.38*scale, y, 0.64*scale, 0.64*scale, fill=color)
    shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, x, y+0.76*scale, 1.4*scale, 1.15*scale, fill=color, adj=0.2)


def rule(sl,x,y,w=12.05):
    arrow(sl,x,y,x+w,y,color=RULE,w=1,head=False)


# 1. Person to skill. 0:25.
s=new(notes=note("TIME 0:25. Nuwa researches a named person and drafts an instruction skill containing inferred models, decision heuristics, voice and limits. It approximates a public record; it does not recover private cognition or train weights. Our question is whether the human-to-skill methodology offers a useful additional input to AI4Research's Capability Capsule Factory. We should assess that narrow contribution critically.","core","template"))
text(s,0.7,0.63,6,1.1,"Nuwa",size=60,bold=True,color=ORANGE,align="l",inset=0)
text(s,0.75,1.93,5.7,1.6,"A person becomes\nan AI skill",size=38,bold=True,align="l",anchor="t",inset=0)
text(s,0.75,3.85,5.55,1.15,"Research a person and draft a skill around a selected trait.",size=24,align="l",anchor="t",inset=0)
person(s,7.0,1.45,0.83)
text(s,6.5,3.18,2.2,0.4,"A named person",size=19,bold=True,color=ORANGE,align="c",inset=0)
arrow(s,8.56,2.3,9.3,2.3,color=ORANGE,w=2.5)
d=doc(s,9.55,1.25,2.8,2.45,line=ORANGE,lw=2)
put(d,[{"t":"SKILL.md","size":25,"bold":True,"color":ORANGE},{"t":"Models\nDecision rules\nVoice and limits","size":19,"before":12}],align="l",inset=0.22)
text(s,6.75,4.22,5.6,0.7,"Nuwa researches the person\nand writes the skill",size=23,bold=True,color=TERRA,align="c",inset=0)
rule(s,0.75,5.55,11.65)
text(s,0.75,5.87,11.65,0.6,"Potential AI4R value: a human-to-skill input for the Capability Capsule Factory",size=22,bold=True,color=ORANGE,align="l",inset=0)
text(s,0.75,6.95,11.6,0.3,"Nuwa repository @7812110. Public evidence gives an approximation of a person. AI4R use remains proposed.",size=10.5,color=GREY,align="l",inset=0)

# 2. Extraction criteria and utility. 1:00.
s=new("Nuwa packages inferred models and decision rules",n=2,
      source="Nuwa core + extraction framework @7812110. Examples paraphrase the repo's Karpathy skill. AI4R uses are proposals.",
      notes=note("TIME 1:00. The product of exploration is a set of inferred models and rules. Nuwa asks for three to seven models that recur in at least two domains, generate new judgments and distinguish the person's perspective. It asks for five to ten concrete decision heuristics with cases, plus limits and tensions. These are subjective extraction filters, not validation of truth or utility. Distinctiveness can reward idiosyncrasy even when a generic method works better. The Karpathy examples here paraphrase the repository's skill; we have not independently verified these attributions. For AI4R's human-to-skill interface, treat every extracted model as a candidate with traceable support, counterevidence and an explicit scope. A rule only becomes a useful capability after our own task checks.","core","framework","karpathy","template"))
table(s,0.7,1.62,[2.05,3.25,3.7,2.9],[
    ["What Nuwa extracts","Example from the skill","Nuwa's retention criterion","Human-to-skill use"],
    ["Mental models\n3–7 lenses","Understanding through construction","Recurs in at least 2 domains, generates new judgments, and is distinctive","Candidate strategy and rationale"],
    ["Decision rules\n5–10 heuristics","Before training a model, inspect the data","A concrete if-then rule with a supporting case","Draft steps to test in AI4R"],
    ["Limits and tensions","Construction is a narrow test of understanding","Keep counterexamples, scope limits and changes over time","Applicability and failure conditions"],
    ["Research directions","For reliability claims, inspect tail failures","Derive specific evidence questions from the models","Tool use driven by evidence needs"]],size=16.5,rh=0.97)
shape(s,MSO_SHAPE.RECTANGLE,0.7,6.16,11.9,0.4,fill=ORANGE_L)
put(s.shapes[-1],"These filters select plausible rules; they establish neither truth nor task benefit.",size=17,bold=True,color=TERRA)

# 3. Source exploration and research criteria. 1:05.
s=new("Nuwa researches six views of the person",n=3,
      source="Nuwa SKILL.md, Phase 1 @7812110. A host agent executes these research instructions and saves each stream.",
      notes=note("TIME 1:05. Nuwa scopes a person and requested trait, then asks a host agent to research six streams: writings, conversations, expression, outside views, decisions and timeline. It saves sources, confidence and distinctions between direct statements, reports and inference. Primary-source preference and contradictions are useful research practices for this human-to-skill input. They are prescriptions, not proof that extraction is correct. A user-specified trait can bias source selection: first ask whether the person's documented record supports that trait, and retain contrary examples. Public repetition may reflect branding or repeated quotations. Firsthand material may still be inaccurate or selective. These source heuristics should inform candidate authoring, while AI4R's evidence process remains responsible for checking claims and capability behavior.","core","framework","rubric"))
text(s,0.7,1.15,11.9,0.35,"Six parallel research agents, with serial fallback. Each stream saves a sourced research file.",size=17,color=TERRA,align="l",inset=0)
table(s,0.7,1.62,[2.05,3.5,3.35,3.0],[
    ["Research stream","Where it explores","What it tries to establish","Human-to-skill use"],
    ["Writings","Books, essays, papers, newsletters","Claims repeated at least 3 times; original concepts","Candidate trait evidence"],
    ["Conversations","Long interviews, podcasts, AMA","Reasoning under questions and changing positions","Context for inferred rules"],
    ["Expression","Posts and short-form writing","Vocabulary, rhythm, certainty and humor","Separate voice from method"],
    ["Outside views","Criticism, biographies, peer accounts","Blind spots do not prove task usefulness","Evidence against the trait"],
    ["Decisions","Major choices, actions and outcomes","Whether behavior supports stated beliefs","Compare actions with claims"],
    ["Timeline","Milestones and recent developments","When views changed and what is current","Version and refresh conditions"]],size=16,rh=0.65)
shape(s,MSO_SHAPE.RECTANGLE,0.7,6.1,11.9,0.55,fill=ORANGE_L)
put(s.shapes[-1],["Sources: primary material first, with confidence, contradictions and inference labels.","Prescribed fidelity test: 3 known positions, 1 unfamiliar case and voice; over 50% primary sources."],size=16,bold=True,color=TERRA)

# 4. Concrete example with the person retained. 0:45.
s=new("Example: a requested trait becomes candidate review rules",n=4,
      source="Karpathy perspective example @7812110. The research question and response below are illustrative framework inferences.",
      notes=note("TIME 0:45. A request such as Karpathy plus reliability review can guide research and yield candidate questions about task coverage, tool failures and reproducibility. This example illustrates how a requested human trait becomes explicit draft rules. It does not show that Karpathy would answer this way or that the generated skill improves an AI4R review. These are familiar review questions that a generic checklist may produce equally well. The name can help a user express the requested perspective, but it provides no authority for an answer. The factory must test the resulting rules against the same task evidence and a competent baseline.","karpathy"))
shape(s,MSO_SHAPE.RECTANGLE,0.7,1.62,3.25,4.72,fill=ORANGE_L)
person(s,1.72,1.97,0.6)
text(s,0.98,3.36,2.7,0.6,"Karpathy perspective",size=23,bold=True,color=ORANGE,align="l",inset=0)
text(s,0.98,4.22,2.68,1.6,"Deployment reliability\nTail failures\nImplementation evidence",size=19,align="l",anchor="t",inset=0,spacing=10)
text(s,4.45,1.65,7.93,1.12,"Paper claim: “Our research agent is highly reliable.”",size=28,bold=True,align="l",anchor="t",inset=0)
arrow(s,4.55,3.03,4.55,5.85,color=ORANGE,head=False,w=3)
for i,(hd,bd) in enumerate([
    ("Task coverage","Does the benchmark cover the intended research workload?"),
    ("Failure modes","What happens during tool errors and long runs?"),
    ("Evidence","Can we inspect code and reproduce the key result?")]):
    y=3.0+i*1.04
    text(s,4.85,y,2.45,0.48,hd,size=20,bold=True,color=ORANGE,align="l",inset=0)
    text(s,7.5,y,4.85,0.87,bd,size=20,align="l",anchor="t",inset=0)
text(s,4.45,6.15,7.93,0.4,"Generic review questions may do as well. A famous name adds no task evidence.",size=15,bold=True,color=TERRA,align="l",inset=0)

# 5. Value and connection to AI4R, grounded in existing agents. 0:55.
s=new("Is Nuwa-skill's methodology valuable to AI4Research?",n=5,
      source="Assessment: useful input methodology; weak validation. AI4R retains its own evidence and qualification process.",
      notes=note("TIME 0:55. Yes, narrowly: Nuwa offers a human-to-skill authoring interface for the CC Factory. A name and target trait become a scoped research request, followed by a candidate instruction skill. An extracted procedure is only a candidate input; AI4R must attach evidence and qualify task behavior. AI4R already has its own approach to evidence-backed capabilities. Nuwa does not supply a better assurance system. We borrow its person-and-trait research workflow; our factory retains responsibility for operationalizing a candidate, testing task behavior and admitting a capsule. Nuwa's fidelity scores and structural checks cannot establish research capability. The value claim is an interface design judgment, with actual authoring and task benefits still unmeasured.","core","framework","template",local="Designs/CC Reference.md; Designs/skills-to-cc-mapping.md. Design-value assessment, not an implemented integration or measured task gain."))
text(s,0.7,1.45,11.9,0.76,"Yes, narrowly: a human-to-skill input for the CC Factory.",size=26,bold=True,color=ORANGE,align="l",anchor="t",inset=0)
node(s,0.7,2.65,2.65,1.16,"Person + target trait","a scoped authoring request",color=GREY,size=23)
arrow(s,3.5,3.24,4.2,3.24,color=ORANGE,w=2)
node(s,4.4,2.65,4.2,1.16,"Research and extract","document the person and draft a skill",filled=True,size=24)
arrow(s,8.76,3.24,9.43,3.24,color=ORANGE,w=2)
node(s,9.63,2.65,2.95,1.16,"Candidate for factory","AI4R qualification required",color=TERRA,size=22)
for i,(hd,bd) in enumerate([
    ("Narrow value","Translate a human reference\ninto explicit candidate rules"),
    ("AI4R already has","Its own capability evidence\nand qualification machinery"),
    ("Nuwa falls short","Persona fidelity and lint\ndo not prove task usefulness")]):
    x=0.75+i*4.08
    text(s,x,4.48,3.72,0.55,hd,size=24,bold=True,color=ORANGE,align="l",inset=0)
    text(s,x,5.18,3.65,0.95,bd,size=21,align="l",anchor="t",inset=0)

# 6. Limits that are specific to persona distillation. 0:50.
s=new("Nuwa's validations provide weak capability assurance",n=6,
      source="Pinned fidelity rubric + quality_check.py @7812110; saved local checker probe. Implications are our assessment.",
      notes=note("TIME 0:50. Nuwa's assurance is weak for capability claims. First, reconstructing a person from public material while targeting a chosen trait invites selection bias and attribution errors. Second, half the fidelity score rewards stance and style: 30 and 20 points. The remaining categories address boundary honesty, sources and structure, but none directly measures AI4R task improvement. Third, the prescribed behavioral test uses three known-position questions, one unfamiliar question and one style sample. Independent answer and judging agents are a useful separation, and the rubric recommends extra judges for important conclusions, but separate LLM agents can share model biases; this is not independent empirical task evidence. Fourth, the saved placeholder probe passed all six structural checks without sources. Missing or untyped sources return success, while keyword matches stand in for semantic checks. This demonstrates a checker defect, not that every Nuwa skill is poor. Its scores cannot justify admitting a research capability; AI4R retains its own evidence, behavioral tests and admission.","template","rubric","checker","musk"))
for i,(hd,bd,imp) in enumerate([
    ("Biased reconstruction","Public records and a desired trait\ncan invite selective evidence.","Test counterevidence and attribution."),
    ("50 points for resemblance","Stance (30) and style (20)\ndominate the 100-point rubric.","Similarity cannot qualify a capability."),
    ("Tiny fidelity test","3 known positions, 1 unfamiliar\ncase and 1 style sample.","No AI4R task baseline or gain shown."),
    ("Checker fails open","A content-free placeholder\npassed 6/6, without sources.","Require evidence; test behavior.")]):
    y=1.62+i*1.18
    marker(s,0.75,y+0.07,str(i+1),color=ORANGE,d=0.48)
    text(s,1.48,y,3.05,0.93,hd,size=22,bold=True,color=ORANGE,align="l",anchor="t",inset=0)
    text(s,4.76,y,4.13,0.94,bd,size=20,align="l",anchor="t",inset=0)
    text(s,9.15,y,3.28,0.94,imp,size=20,bold=True,align="l",anchor="t",inset=0)
    if i<3: rule(s,1.48,y+1.03,10.95)

# 7. Three proposed entry interfaces to one factory. 1:00.
s=new("Three entry points could feed one Capability Capsule Factory",n=7,
      source="Proposed AI4R interfaces: runtime gap, paper/repo/data, and person + trait. Authoring routes differ; qualification and admission remain shared.",
      notes=note("TIME 1:00. We propose three input interfaces to the Capsule Factory. An observed runtime gap produces a diagnosed requirement brief. A paper, repository and data provide a method to reproduce and adapt. A person's name plus target trait initiates human-focused source research and skill drafting, taking inspiration from Nuwa. This third route is Nuwa's relevant contribution. All routes produce candidates; AI4R owns the contract, body, evidence package, independent qualification and existing admission gate. A name cannot establish competence, and Nuwa's fidelity grade cannot replace our checks. Source preparation is separately authorized and pinned before offline build work. This is a proposed interface, not a claim of deployed integration or adoption of Nuwa's assurance system.","core","framework",local="User direction, 2026-10-23: three factory inputs. Designs/Capability Capsule Factory Feature.md; Designs/Per Lab Capability Factory Design.md. Proposed M2 extension, not implemented interfaces."))
text(s,0.7,1.35,11.9,0.4,"Nuwa contributes to the third input; AI4R owns capability evidence and qualification",size=19,bold=True,color=TERRA,align="l",inset=0)
shape(s,MSO_SHAPE.RECTANGLE,4.35,1.93,8.25,4.55,fill=ORANGE_L)
text(s,4.6,2.03,7.7,0.35,"CC factory",size=17,bold=True,color=ORANGE,align="l",inset=0)
entries=[
    (2.48,"Observed capability gap","missing task + run evidence","Diagnose and specify","requirement brief"),
    (3.94,"Paper + repo + data","method + code + dataset","Reproduce and adapt","source implementation"),
    (5.40,"Person name + trait","e.g. Karpathy + reliability review","Research and extract","verify the trait in sources")]
for y,hd,bd,stage,detail in entries:
    node(s,0.7,y,3.15,0.96,hd,bd,color=ORANGE,size=20)
    arrow(s,3.98,y+0.48,4.47,y+0.48,color=ORANGE)
    node(s,4.6,y,2.7,0.96,stage,detail,filled=True,size=18)
    arrow(s,7.43,y+0.48,7.88,y+0.48,color=ORANGE,head=False)
arrow(s,7.88,2.96,7.88,5.88,color=ORANGE,head=False)
arrow(s,7.88,4.42,8.37,4.42,color=ORANGE,head=False)
node(s,8.5,2.62,3.83,1.0,"Author candidate CC","contract + body + evidence",color=TERRA,size=22)
# Converging entry routes feed the candidate package before qualification.
arrow(s,8.37,4.42,8.37,3.12,color=ORANGE,head=False)
arrow(s,8.37,3.12,8.48,3.12,color=ORANGE)
arrow(s,10.42,3.76,10.42,4.02,color=TERRA)
node(s,8.5,4.15,3.83,0.78,"Independent qualification",color=TERRA,size=20)
arrow(s,10.42,5.06,10.42,5.32,color=TERRA)
node(s,8.5,5.45,3.83,0.78,"Existing admission gate",color=TERRA,size=20)

# 7. What we can do, without importing a different workflow. 0:50.
s=new("A bounded trial of the human-to-skill interface",n=8,
      source="Proposed trial: assess authoring utility first, then task benefit. No comparative result exists yet.",
      notes=note("TIME 0:50. Trial the interface as an authoring tool first: choose one person, a defensible target trait and a strong corpus. Draft a candidate skill using the research and extraction workflow. Check attribution and contrary evidence; record unsupported rules, corrections, human effort and authoring cost. If the candidate is worth continuing, take it through AI4R qualification. The task comparison uses a plain reviewer, a generic checklist and the human-derived rules, all with the same frozen sources, task evidence, model, tools and runtime budget. Blind scoring on unseen tasks tests incremental utility. A useful interface can reduce the effort of specifying a capability without proving the human-inspired rules outperform a generic method. Report those outcomes separately.","core","rubric",local="Designs/skills-to-cc-mapping.md; separate proposal, not a revision to the maintained accuracy study."))
for i,(hd,bd) in enumerate([
    ("Name + target trait","One bounded request\nwith a strong source corpus"),
    ("Draft a candidate skill","Verify trait and rule support\nTrack corrections and authoring cost"),
    ("Qualify through AI4R","Same sources and budget\nCompare with a generic checklist")]):
    x=0.75+i*4.05
    text(s,x,1.72,3.63,0.7,str(i+1),size=42,bold=True,color=ORANGE,align="l",inset=0)
    text(s,x,2.68,3.65,0.94,hd,size=26,bold=True,align="l",anchor="t",inset=0)
    text(s,x,3.98,3.65,1.45,bd,size=22,align="l",anchor="t",inset=0)
rule(s,0.75,5.65,11.8)
text(s,0.75,5.94,11.75,0.55,"Retain the interface only if it produces useful candidates at an acceptable cost.",size=23,bold=True,color=TERRA,align="l",inset=0)

# 8. Close with the actual Nuwa value proposition. 0:30.
s=new("A narrow contribution to the CC Factory",n=9,
      source="Assessment: borrow the human-to-skill research workflow. AI4R supplies capability evidence, testing and admission.",
      notes=note("TIME 0:30. Our recommendation is selective: borrow Nuwa's person-and-trait research workflow as a possible third input to the Capability Capsule Factory. We already have our own approach to evidence-backed capability production. Nuwa's reconstruction, tiny fidelity test and permissive structural checker provide insufficient assurance for that role. A familiar persona can be an accessible way to request a skill; the resulting artifact remains a candidate. Judge the interface by the useful candidates it produces and the effort it saves, then require ordinary AI4R task qualification and admission.","core","template",local="Designs/skills-to-cc-mapping.md; Designs/Capability Capsule Factory Feature.md"))
text(s,0.75,1.83,6.52,2.1,"Human-to-skill\ncould become the third\nfactory input.",size=36,bold=True,color=ORANGE,align="l",anchor="t",inset=0)
text(s,0.75,4.45,6.3,1.3,"Borrow person-and-trait research.\nKeep AI4R qualification in charge.",size=24,align="l",anchor="t",inset=0)
shape(s,MSO_SHAPE.RECTANGLE,7.75,1.75,4.78,4.45,fill=ORANGE_L)
text(s,8.08,2.08,4.12,0.6,"The next decision",size=23,bold=True,color=ORANGE,align="l",inset=0)
text(s,8.08,3.13,4.12,2.0,"Can this interface produce useful candidate skills?",size=29,bold=True,align="l",anchor="t",inset=0)
text(s,8.08,5.47,4.12,0.7,"One person. One trait. A qualified candidate.",size=18,bold=True,color=TERRA,align="l",inset=0)

# 9. Hidden backup: what the score measures.
s=new("Backup: task value requires a comparison beyond fidelity",n=10,backup=True,
      source="Proposed comparison after Luna review. Nuwa's fidelity reports do not establish AI4R task benefit.",
      notes=note("BACKUP. All arms receive the same frozen expert-source excerpts and task evidence. The plain reviewer gets no added procedure. The generic arm gets a length-matched general review checklist. The extracted-method arm gets neutral rules and limits produced through the Nuwa-inspired process. Hold the model, tools, permissions and runtime budgets fixed, freeze unseen tasks and scoring before generation, and blind human assessment. Judge supported useful objections, missed failure modes, unsupported claims, uncertainty, latency and cost. Record corpus preparation and authoring effort separately from runtime cost. This identifies the increment beyond a generic checklist, not the causal effect of each Nuwa phase. A later voice ablation can test whether persona framing helps or hurts. No experimental result is claimed.","rubric",local="Designs/skills-to-cc-mapping.md; Luna adversarial review, 2026-10-23."))
table(s,0.75,1.68,[3.1,4.45,4.25],[
    ["Arm","Added instructions","What the comparison estimates"],
    ["Plain reviewer","No added procedure","Baseline with identical sources"],
    ["Generic checklist","Length-matched general review instructions","Benefit of structured prompting"],
    ["Extracted method","Neutral Nuwa-derived rules and limits","Increment beyond a generic checklist"]],size=18,rh=0.9)
text(s,0.8,5.2,11.7,1.08,"Same expert excerpts, task evidence, model, tools and runtime budget.\nFreeze unseen tasks and scoring first. Record authoring cost separately.",size=20,align="l",anchor="t",inset=0)

# 10. Hidden backup: governed use, separate from the creation workflow.
s=new("Backup: a human-derived skill still needs ordinary CC qualification",n=11,backup=True,
      source="AI4R CC Reference and skills-to-cc-mapping. Proposed adaptation, not an implemented Nuwa integration.",
      notes=note("BACKUP. This is downstream of authoring. A human-derived instruction skill is a candidate body, not a capsule contract or permission grant. Pin source evidence, cutoff and rule support; define one bounded task with typed inputs and inspectable outputs. AI4R supplies tool/effect/budget constraints, task-level tests, versioning and admission. The semantic verifier remains declaration-and-output-only; source- and input-dependent checks belong in the protected host path. A Nuwa fidelity report can describe the approximation but cannot qualify this capsule. This is a proposed integration, not implemented deployment.","core","template",local="Designs/CC Reference.md; Designs/skills-to-cc-mapping.md"))
table(s,0.75,1.68,[3.15,4.75,3.9],[
    ["Element","Proposed binding","Reason"],
    ["Person-perspective skill","Pin body, source manifest and cutoff","Repeatable version of the perspective"],
    ["Agent responsibility","Choose one task step; explicit activation","Avoid silent influence on unrelated work"],
    ["Inputs and output","Task + evidence; supported critique + uncertainty","Make behavior and failures inspectable"],
    ["Tools and effects","Explicit needs, budgets and permissions","Prompt instructions confer no runtime authority"],
    ["Checks and admission","Ordinary CC versioning and independent checks","Generation alone does not approve deployment"]],size=16,rh=0.77)

# Put AI4R value immediately after the introduction. Notes move with their slide.
slide_ids = prs.slides._sldIdLst
original_ids = list(slide_ids)
for element in original_ids:
    slide_ids.remove(element)
for index in [0, 4, 2, 1, 3, 5, 6, 7, 8, 9, 10]:
    slide_ids.append(original_ids[index])
for slide_number, slide in enumerate(prs.slides, 1):
    for item in slide.shapes:
        if item.has_text_frame and abs(item.left - Inches(11.7)) < 100 and abs(item.top - Inches(7.08)) < 100:
            item.text_frame.paragraphs[0].runs[0].text = str(slide_number)

OUT.parent.mkdir(exist_ok=True)
prs.save(OUT)
print("wrote",OUT,"with",len(prs.slides),"slides (9 main, 2 hidden)")


