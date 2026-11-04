"""Build the Nuwa talk using the editable native-shape grammar of the Paper2Agent reference."""
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
OUT = HERE / ".build" / "Nuwa Talk draft.pptx"

# Palette: indigo = Paper2Agent and its workflow, teal = AI4Research integration, amber = limits only.
BG, INK, GREY, RULE = "FAF8F4", "1F2A44", "6B7280", "D6D3CC"
INDIGO, INDIGO_L = "3D4FB0", "E7E9F7"
TEAL, TEAL_L = "0F8B8D", "DFF1F1"
AMBER, AMBER_L = "B7791F", "FBF0DC"
PANEL = "F0EDE6"
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
        label = "Nuwa overview" + ("  |  Backup" if backup else "")
        text(sl, 0.6, 7.08, 6.0, 0.28, label, size=10, color=GREY, align="l", inset=0)
        if n:
            text(sl, 11.7, 7.08, 1.03, 0.28, str(n), size=10, color=GREY, align="r", inset=0)
    if tag:
        t = rbox(sl, 0.6, 1.05, 2.13, 0.34, fill=INDIGO_L, line=None, adj=0.5)
        put(t, tag, size=11, color=INDIGO, bold=True, inset=0.04)
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


def card(sl, x, y, w, h, title, body, color=INDIGO, body_size=18):
    rbox(sl, x, y, w, h, fill="FFFFFF", line=RULE, adj=0.05)
    shape(sl, MSO_SHAPE.RECTANGLE, x, y, w, 0.07, fill=color)
    text(sl, x+0.22, y+0.22, w-0.44, 0.55, title, size=19, bold=True, color=color, align="l", anchor="t", inset=0)
    text(sl, x+0.22, y+0.95, w-0.44, h-1.07, body, size=body_size, align="l", anchor="t", inset=0, spacing=11)


def node(sl, x, y, w, h, title, sub="", color=INDIGO, filled=False, size=18):
    b=rbox(sl,x,y,w,h,fill=color if filled else "FFFFFF",line=color,adj=0.06)
    paras=[{"t":title,"bold":True,"size":size,"color":"FFFFFF" if filled else color}]
    if sub: paras.append({"t":sub,"size":14,"color":"ECEEFA" if filled else GREY,"before":6})
    put(b,paras,inset=0.08)
    return b


# 1 — Opening. 0:20.
s=new(notes=note("TIME 0:20. Nuwa offers a way to turn documented thinking into reusable research methods. For AI4Research, the value is an authoring pattern: collect evidence, extract decision rules, and package them for repeated use. Today I will show the idea, one example, and how it could fit our capability factory. The integration is proposed; no accuracy gain has been measured.","core"))
text(s,0.9,0.85,11.5,1.1,"Nuwa",size=58,bold=True,color=INDIGO,align="l",inset=0)
text(s,0.9,2.03,11.5,0.8,"From documented thinking to reusable research methods",size=29,align="l",inset=0)
text(s,0.9,2.95,11.5,0.55,"What it does, where it adds value, and how it could fit AI4Research",size=18,color=GREY,align="l",inset=0)
shape(s,MSO_SHAPE.RECTANGLE,0.9,3.8,0.08,0.65,fill=TEAL)
text(s,1.12,3.8,11.05,0.65,"Value to AI4Research: reusable, source-linked ways to analyze and review",size=21,bold=True,color=TEAL,align="l",inset=0)
node(s,0.9,5.02,3.35,1.15,"Source material","writings, interviews, decisions",color=GREY)
arrow(s,4.38,5.6,5.02,5.6)
node(s,5.15,5.02,3.35,1.15,"Nuwa workflow","research, extract, check",filled=True)
arrow(s,8.63,5.6,9.27,5.6)
node(s,9.4,5.02,3.0,1.15,"Reusable skill","methods + evidence",color=TEAL)
text(s,0.9,6.95,11.5,0.3,"October 2026  |  Repository reviewed at 7812110  |  Integration proposed",size=11,color=GREY,align="l",inset=0)

# 2 — Value first. 0:45.
s=new("Value: make useful thinking explicit and reusable",n=2,
      source="Nuwa SKILL.md + extraction-framework.md @7812110. AI4Research benefits are hypotheses.",
      notes=note("TIME 0:45. There are two kinds of value. The idea is to turn a useful way of thinking into something an agent can repeatedly apply: which questions to ask, which evidence to seek, and when a rule fails. That can support technical review, hypothesis critique, or experiment planning. The methodology gives us a repeatable authoring process, with research files, decision rules, contradictions, and limits. This could reduce repeated prompt writing and make a review easier to inspect. Paper2Agent packages operations; Nuwa packages analysis and judgment methods. Those are complementary kinds of reusable capability. Whether Nuwa improves our research outputs remains a testable hypothesis.","core","framework",local="Designs/skills-to-cc-mapping.md; Designs/Capability Capsule Factory Feature.md"))
card(s,0.65,1.65,5.9,3.95,"THE IDEA",[
    {"t":"Reuse a way of analyzing a problem","size":27,"bold":True},
    {"t":"Choose questions, evidence and decision rules","size":20,"before":22},
    {"t":"Apply it to review, planning and hypothesis critique","size":20,"before":16}],color=TEAL)
card(s,6.8,1.65,5.9,3.95,"THE METHODOLOGY",[
    {"t":"Build the method from traceable sources","size":27,"bold":True},
    {"t":"Preserve evidence, contradictions and failure conditions","size":20,"before":22},
    {"t":"Update the package when the evidence changes","size":20,"before":16}],color=INDIGO)
text(s,0.8,5.95,11.75,0.5,"Paper2Agent packages operations; Nuwa packages analysis and judgment methods.",size=21,bold=True,align="c",inset=0)

# 3 — Workflow. 0:50.
s=new("Six research streams become one runnable skill",n=3,
      source="Nuwa SKILL.md, Phases 0–5; extraction-framework.md @7812110. Helper scripts do not execute the whole workflow.",
      notes=note("TIME 0:50. The workflow starts with a named person, topic, or need. Sources may be public, supplied locally, or restricted to the supplied corpus. Six research streams cover writings, conversations, expression, outside criticism, decisions, and the timeline. Each saves a research file. Synthesis then selects a small number of mental models and decision rules. A model should recur across domains, generate reasoning on new questions, and be distinctive. The output combines those rules with an answer workflow, source references, and limitations. Separate agents test known positions, unfamiliar questions, and style, followed by refinement. This is a set of instructions executed by the host agent, with helper scripts; it is not a standalone orchestration engine.","core","framework"))
node(s,0.65,1.7,2.0,0.9,"Scope + sources","person or topic",color=GREY,size=17)
arrow(s,2.78,2.15,3.25,2.15)
rbox(s,3.35,1.52,4.9,2.6,fill=INDIGO_L,line=None)
text(s,3.55,1.68,4.5,0.4,"Parallel research → saved evidence",size=19,bold=True,color=INDIGO,align="l",inset=0)
streams=["Writings","Interviews","Expression","Criticism","Decisions","Timeline"]
for i,t in enumerate(streams):
    x=3.55+(i%3)*1.5;y=2.3+(i//3)*0.8
    node(s,x,y,1.35,0.62,t,color=INDIGO,size=13.5)
arrow(s,8.38,2.78,8.9,2.78)
node(s,9.02,2.18,3.65,1.2,"Extract the framework","3–7 models; 5–10 rules",filled=True,size=20)
arrow(s,10.85,3.52,10.85,4.05)
node(s,9.02,4.18,3.65,1.18,"Build + validate","SKILL.md + research files",color=TEAL,size=20)
rbox(s,0.65,4.35,7.55,1.65,fill="FFFFFF",line=RULE,adj=0.05)
text(s,0.9,4.55,7.05,0.45,"A mental model must pass three filters",size=21,bold=True,align="l",inset=0)
for i,t in enumerate(["Recurs across domains","Reasons about new cases","Distinctive perspective"]):
    text(s,0.9+i*2.38,5.22,2.18,0.6,t,size=17,color=INDIGO,align="l",inset=0)
text(s,9.02,5.65,3.65,0.55,"Known cases · uncertainty · style",size=16,color=TEAL,bold=True,align="c",inset=0)

# 4 — Product. 0:40.
s=new("The output is a prompt package with supporting evidence",n=4,
      source="Nuwa skill-template.md + SKILL.md @7812110. “Distillation” means instruction synthesis; model weights are unchanged.",
      notes=note("TIME 0:40. What do we actually get? A directory containing a skill file, research notes, and available source material. The skill states when to activate, which models and rules to apply, how to gather facts, and what its boundaries are. The research files let an author inspect where the rules came from. At use time, the agent classifies the question, obtains facts when necessary, and applies the framework. The repository calls this distillation, but there is no model training or weight change. A person skill also includes speaking style. A topic skill combines methods from several schools using neutral language, which is a useful option for AI4Research.","template","core"))
rbox(s,0.65,1.65,5.65,4.5,fill=INDIGO_L,line=None,adj=0.05)
text(s,0.95,1.9,5.05,0.5,"[person]-perspective / [topic]-framework",size=21,bold=True,color=INDIGO,align="l",inset=0)
for i,(t,b) in enumerate([
    ("SKILL.md","activation, models, rules, answer workflow, limits"),
    ("references/research/","evidence, criticism, decisions, timeline"),
    ("sources/ + optional scripts/","available source material and helper tools")]):
    d=doc(s,0.95,2.65+i*1.05,5.05,0.85,line=INDIGO)
    put(d,[{"t":t,"size":19,"bold":True,"color":INDIGO},{"t":b,"size":15,"color":GREY}],align="l",inset=0.16)
arrow(s,6.45,3.85,6.95,3.85,color=TEAL)
text(s,7.17,1.82,5.1,0.5,"At use time",size=23,bold=True,color=TEAL,align="l",inset=0)
for i,(hd,bd) in enumerate([
    ("Classify the question","Facts, framework, or a mixture?"),
    ("Gather needed evidence","Search according to the framework"),
    ("Apply rules and state uncertainty","Distinguish sources from inference")]):
    marker(s,7.18,2.75+i*1.05,str(i+1),color=TEAL,d=0.4)
    text(s,7.78,2.67+i*1.05,4.6,0.5,hd,size=20,bold=True,align="l",inset=0)
    text(s,7.78,3.18+i*1.05,4.6,0.4,bd,size=16,color=GREY,align="l",inset=0)
text(s,7.2,5.92,5.1,0.4,"Person perspective or neutral topic framework",size=17,bold=True,color=TEAL,align="l",inset=0)

# 5 — Worked example. 0:55.
s=new("Example: turn an engineering lens into a repeatable review",n=5,
      source="Karpathy example @7812110. The agent-reliability task and candidate CC below are our illustration; no result is claimed.",
      notes=note("TIME 0:55. Here is a concrete use. The repository's Karpathy skill asks about the gap between a demo and reliable deployment, actual implementation evidence, and difficult edge cases. Suppose our research question is whether an agent method is ready for a long-running research workflow. The reusable method would ask for the task distribution, failure and recovery evidence, and reproducible code or evaluation records. Its output could be a structured review: a readiness judgment, supporting claims, unresolved risks, and suggested tests. For AI4Research I would package those useful questions and rules as an engineering-reliability review capability. Speaking in Karpathy's voice is optional. The research task, output schema, and capsule are illustrative proposals. We have not built or tested this conversion.","karpathy",local="Designs/skills-to-cc-mapping.md"))
text(s,0.65,1.52,12.0,0.55,"Question: is this agent method ready for a long-running research workflow?",size=22,bold=True,align="l",inset=0)
card(s,0.65,2.35,3.65,3.2,"DOCUMENTED LENS",[
    {"t":"Demo → reliable deployment","size":23,"bold":True},
    {"t":"Implementation evidence","size":19,"before":18},
    {"t":"Hard cases and tail failures","size":19,"before":14}],body_size=19)
arrow(s,4.42,3.98,4.88,3.98)
card(s,5.0,2.35,3.65,3.2,"REVIEW QUESTIONS",[
    {"t":"What was tested?","size":21,"bold":True},
    {"t":"What fails or needs recovery?","size":19,"before":18},
    {"t":"Can we reproduce it?","size":19,"before":14}],color=INDIGO)
arrow(s,8.77,3.98,9.23,3.98,color=TEAL)
card(s,9.35,2.35,3.35,3.2,"CANDIDATE OUTPUT",[
    {"t":"Readiness review","size":23,"bold":True},
    {"t":"Judgment + source links","size":19,"before":18},
    {"t":"Risks + next tests","size":19,"before":14}],color=TEAL)
rbox(s,0.65,5.92,12.05,0.56,fill=TEAL_L,line=None,adj=0.05)
put(s.shapes[-1],"Possible CC: engineering-reliability review  |  input: evidence bundle  →  output: structured review",size=17,bold=True,color=TEAL)

# 6 — Integration. 1:00.
s=new("Include Nuwa in the capability factory",n=6,
      source="Proposed M2 mapping: skills-to-cc-mapping + per-lab Factory plan. Nuwa generation does not grant CC admission.",
      notes=note("TIME 1:00. The proposed fit has two separate flows. At authoring time, prepared and versioned sources enter a Nuwa-inspired workflow. It produces a candidate method package and an evidence bundle. Sources remain resources; the authoring stages and the generated product have separate identities. Before the product becomes an agent CC, define typed inputs and outputs, explicit needs and effects, budgets, failure behavior, and independent checks. It then goes through ordinary admission. At run time, the planner selects an admitted capability for a bounded task; current task evidence is supplied to it, and its structured output goes through the existing review and host-check paths. This is a proposed M2 factory extension, not current M1 behavior. A lightweight first step is to author and compare one framework package before building factory automation.","core","template",local="Designs/skills-to-cc-mapping.md; Designs/Capability Capsule Factory Feature.md; Designs/Per Lab Capability Factory Design.md; Designs/CC Reference.md. Semantic verifier remains declaration + output only; input-dependent checks are separate."))
text(s,0.65,1.48,12.05,0.4,"AUTHORING · proposed M2 factory extension",size=16,bold=True,color=INDIGO,align="l",inset=0)
rbox(s,0.65,2.02,12.05,2.2,fill=INDIGO_L,line=None,adj=0.03)
node(s,0.9,2.5,2.05,1.03,"Pinned sources","resource manifest",color=GREY,size=18)
arrow(s,3.06,3.02,3.44,3.02)
node(s,3.55,2.5,2.5,1.03,"Research + extract","Nuwa-style stages",filled=True,size=18)
arrow(s,6.16,3.02,6.54,3.02)
node(s,6.65,2.5,2.45,1.03,"Candidate method","body + evidence",size=18)
arrow(s,9.21,3.02,9.59,3.02,color=TEAL)
node(s,9.7,2.5,2.7,1.03,"Adapt + admit","contract + checks",color=TEAL,size=18)
text(s,0.95,3.7,11.4,0.32,"Version sources separately  ·  Declare ports, needs, effects and budgets  ·  Check independently",size=15,color=INK,align="c",inset=0)
arrow(s,11.05,4.32,11.05,4.62,color=TEAL,head=False)
arrow(s,11.05,4.62,7.87,4.62,color=TEAL,head=False)
arrow(s,7.87,4.62,7.87,4.9,color=TEAL)
text(s,0.65,4.5,6.7,0.38,"USE · invoke through the existing CC path",size=16,bold=True,color=TEAL,align="l",inset=0)
node(s,0.9,5.02,2.05,1.05,"Task + evidence","current inputs",color=GREY,size=18)
arrow(s,3.06,5.55,3.44,5.55,color=TEAL)
node(s,3.55,5.02,2.5,1.05,"Plan + bind","select pinned CC",color=TEAL,size=18)
arrow(s,6.16,5.55,6.54,5.55,color=TEAL)
node(s,6.65,5.02,2.45,1.05,"Admitted agent CC","apply the method",color=TEAL,filled=True,size=18)
arrow(s,9.21,5.55,9.59,5.55,color=TEAL)
node(s,9.7,5.02,2.7,1.05,"Structured output","review + host checks",color=TEAL,size=18)

# 7 — Balanced evaluation limits. 0:50.
s=new("One limit: the skill and its tests can share the same evidence",n=7,
      source="Nuwa fidelity rubric + quality_check.py @7812110. Coupling risks are our analysis; local checker probe: 6/6 on empty content.",
      notes=note("TIME 0:50. There is a useful evaluation idea here, but a limit. The same public material can supply both the extracted rules and the known-position questions. A pass then shows agreement on familiar material, with limited evidence of transfer. Different answering and judging agents reduce direct self-evaluation, but may still share model assumptions. The structural checker is weaker: our deliberately empty placeholder skill passed all six checks, including the source check without a source section. That is a test of the checker, not of persona quality. The right response is to preserve known-position checks while adding held-out source passages, genuinely new tasks, independent evidence checks, and a matched baseline. The repository's high fidelity scores are project-reported, not demonstrated AI4Research gains.","rubric","checker","musk"))
rbox(s,0.65,1.55,7.25,4.78,fill=PANEL,line=None,adj=0.04)
node(s,0.95,1.88,2.7,0.88,"Public source corpus",color=GREY,size=18)
node(s,4.35,1.88,3.2,0.88,"Known-position questions",color=GREY,size=17)
arrow(s,3.77,2.32,4.23,2.32,color=GREY)
arrow(s,2.3,2.88,2.3,3.34)
node(s,0.95,3.47,2.7,0.9,"Extracted skill",filled=True,size=18)
arrow(s,3.77,3.92,4.23,3.92)
node(s,4.35,3.47,3.2,0.9,"Answering agent",size=18)
arrow(s,5.95,2.88,5.95,3.34,color=GREY)
arrow(s,5.95,4.5,5.95,4.96,color=TEAL)
node(s,4.35,5.1,3.2,0.88,"Separate judging agent",color=TEAL,size=17)
text(s,0.95,4.98,2.9,0.9,"Familiar-source agreement\nis useful but narrow",size=18,bold=True,color=INK,align="l",inset=0)
marker(s,3.49,1.74,"1")
marker(s,7.35,4.94,"2")
for y,n,hd,bd in [
    (1.65,"1","Source overlap","Known positions can repeat the material used to build the skill."),
    (3.1,"2","Judge dependence","Separate agents can still share model assumptions and biases."),
    (4.55,"3","Structure ≠ evidence","An empty mock skill passed all six automated checks in our probe.")]:
    marker(s,8.35,y+0.04,n)
    text(s,8.88,y,3.82,0.43,hd,size=20,bold=True,align="l",inset=0)
    text(s,8.88,y+0.52,3.82,0.85,bd,size=17,align="l",anchor="t",inset=0)

# 8 — Close. 0:30.
s=new("Adapt the method; test one useful capability",n=8,
      source="Proposed next step. No Nuwa-to-CC conversion, factory integration or accuracy improvement has been demonstrated.",
      notes=note("TIME 0:30. The value is to make useful research and review methods explicit, inspectable, and reusable. The fit is a factory authoring pattern whose product becomes a bounded agent capsule after adaptation and admission. The next step is one technical-review framework, with a matched comparison against the same evidence without the framework. Continue if the method improves blinded task judgments at acceptable cost. The goal is better research behavior; resemblance to a famous person is only a secondary property.","core",local="Designs/skills-to-cc-mapping.md; Designs/Capability Capsule Factory Feature.md"))
for i,(lab,col,msg) in enumerate([
    ("VALUE",INDIGO,"Reuse source-linked research and review methods."),
    ("FIT",TEAL,"Factory stages author candidates; admission governs use."),
    ("NEXT",INK,"Compare one review framework against matched evidence.")]):
    x=0.65+i*4.1
    rbox(s,x,1.78,3.85,3.65,fill="FFFFFF",line=RULE,adj=0.05)
    shape(s,MSO_SHAPE.RECTANGLE,x,1.78,0.08,3.65,fill=col)
    text(s,x+0.3,2.08,3.25,0.42,lab,size=15,bold=True,color=col,align="l",inset=0)
    text(s,x+0.3,2.83,3.25,2.25,msg,size=26,bold=True,align="l",anchor="t",inset=0)
text(s,0.8,5.86,11.9,0.6,"Measure task quality and calibration; treat persona resemblance as secondary.",size=21,bold=True,color=TEAL,align="l",inset=0)

# 9 — Hidden backup: experiment.
s=new("Backup: test the framework beyond familiar source material",n=9,backup=True,
      source="Proposed pilot. No cases, scores or acceptance threshold are presented as completed research.",
      notes=note("BACKUP. Compare three arms: plain agent, agent with the same evidence, and agent with that evidence plus the Nuwa-derived framework. The second versus third isolates the framework contribution. Use matched model, tools, task inputs and budgets. Freeze held-out tasks and scoring criteria before generation; keep scorer keys unavailable to the authoring workflow. Assess supported conclusions, source correctness, calibration, failure behavior, cost, and latency. Persona-recognition scores are secondary. A small pilot establishes feasibility and useful failure cases; it cannot prove broad superiority.","rubric",local="Designs/skills-to-cc-mapping.md; Experiments/CC Accuracy Study.md (context only; this is a separate Nuwa proposal)."))
table(s,0.65,1.55,[2.55,9.5],[
    ["Element","Proposed design"],
    ["Three arms","Plain agent / same evidence / same evidence + extracted framework"],
    ["Held constant","Model, tools, source bundle, task inputs, permissions and budget"],
    ["Held out first","New source passages; unseen review tasks; missing and contradictory evidence"],
    ["Independent judgment","Blinded human assessment; scorer keys hidden from the authoring workflow"],
    ["Measure","Supported conclusions, citation accuracy, uncertainty, task quality, time and cost"],
    ["Continue if","Useful gains over the same-evidence arm, without unacceptable regressions or cost"],
    ["Narrow or stop if","Only the voice changes, claims become less supported, or maintenance outweighs value"]],size=15,rh=0.58)

# 10 — Hidden backup: engineering fit.
s=new("Backup: a skill needs a contract before it becomes a CC",n=10,backup=True,
      source="AI4Research skills-to-cc-mapping + CC Reference. Proposed M2 integration; ordinary admission remains required.",
      notes=note("BACKUP. Keep sources as versioned resources and the method as a separately pinned body. Add typed ports, explicit capabilities and effects, caps, failure behavior, and independently assigned checks. The semantic verifier sees declaration and output only. Input-dependent citation or source-presence checks belong in the separate host-check path. Adapt runtime-specific paths rather than hardcoding Claude's directory. The Nuwa instructions also need a clear policy for fact research versus source cutoff. This deck does not modify the maintained architecture or authorize automatic installation or promotion.","core","template",local="Designs/skills-to-cc-mapping.md; Designs/CC Reference.md; Designs/Capability Capsule Factory Feature.md; Designs/Lab Capsule and Factory Design Plan.md."))
table(s,0.65,1.55,[2.65,4.35,5.05],[
    ["Nuwa provides","CC adaptation","Evidence / boundary"],
    ["Prompt + research files","Pinned body and resource manifest","Source identity, cutoff, rights and claim links"],
    ["Free-form answer","Typed task/evidence inputs; structured review","Missing-input behavior; uncertainty and source fields"],
    ["Tool-use instructions","Explicit model/tool needs, effects and caps","Bounded network, time, tokens and artifact writes"],
    ["Fidelity checks","Independent task checks + semantic review","Verifier: declaration + output; host checks inputs"],
    ["Generated skill directory","Versioned candidate; ordinary admission","No automatic promotion or replacement of pinned runs"],
    ["Claude-oriented paths","Runtime adapter and M2 factory-stage mapping","No claim of current M1 factory support"]],size=14.5,rh=0.68)

OUT.parent.mkdir(exist_ok=True)
prs.save(OUT)
print("wrote", OUT, len(prs.slides), "slides (8 shown + 2 hidden)")


