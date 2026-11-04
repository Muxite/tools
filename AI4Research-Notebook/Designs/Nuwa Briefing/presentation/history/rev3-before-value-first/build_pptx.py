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
s=new(notes=note("TIME 0:25. Nuwa takes a person and turns their documented thinking into an AI skill. You name someone, Nuwa researches what they wrote, said and did, and the result tells an agent how to reason and respond from that perspective. The promise for AI4Research is access to useful ways of thinking on demand. This talk asks where that adds value, where the approximation fails, and what we should test first.","core","template"))
text(s,0.7,0.63,6,1.1,"Nuwa",size=60,bold=True,color=ORANGE,align="l",inset=0)
text(s,0.75,1.93,5.7,1.6,"A person becomes\nan AI skill",size=38,bold=True,align="l",anchor="t",inset=0)
text(s,0.75,3.85,5.55,1.15,"Use their way of thinking, judging and speaking on a new problem.",size=24,align="l",anchor="t",inset=0)
person(s,7.0,1.45,0.83)
text(s,6.5,3.18,2.2,0.4,"A named person",size=19,bold=True,color=ORANGE,align="c",inset=0)
arrow(s,8.56,2.3,9.3,2.3,color=ORANGE,w=2.5)
d=doc(s,9.55,1.25,2.8,2.45,line=ORANGE,lw=2)
put(d,[{"t":"SKILL.md","size":25,"bold":True,"color":ORANGE},{"t":"Models\nDecision rules\nVoice and limits","size":19,"before":12}],align="l",inset=0.22)
text(s,6.75,4.22,5.6,0.7,"Nuwa researches the person\nand writes the skill",size=23,bold=True,color=TERRA,align="c",inset=0)
rule(s,0.75,5.55,11.65)
text(s,0.75,5.87,11.65,0.6,"Potential AI4R value: expert reasoning made reusable for research and review",size=22,bold=True,color=ORANGE,align="l",inset=0)
text(s,0.75,6.95,11.6,0.3,"Nuwa repository @7812110. Public evidence gives an approximation of a person. AI4R use remains proposed.",size=10.5,color=GREY,align="l",inset=0)

# 2. What makes the product person-specific. 0:45.
s=new("Nuwa organizes public evidence into a person-specific skill",n=2,
      source="Nuwa SKILL.md and skill-template.md @7812110. Each perspective includes limits and a research cutoff.",
      notes=note("TIME 0:45. The skill has five layers. Mental models capture how the person frames a problem. Decision heuristics capture their quick rules for making judgments. Expression DNA gives the answer their characteristic voice. Values, anti-patterns and contradictions preserve priorities and tensions, rather than smoothing the person into generic advice. Honest limits state what the reconstruction cannot know. The result can therefore do more than repeat quotations: it can apply a documented pattern to a question the person never answered. That last step is an inference. It must remain distinguishable from the person's actual public position. Public statements, incomplete records, and a date cutoff constrain the result.","core","framework","template"))
person(s,1.18,2.42,1.05)
text(s,0.75,4.68,2.8,0.9,"One person's\ndocumented perspective",size=22,bold=True,color=ORANGE,align="c",inset=0)
arrow(s,3.0,3.45,3.6,3.45,color=ORANGE,head=False)
arrow(s,3.6,1.88,3.6,5.89,color=ORANGE,head=False)
rows=[("Mental models","How they frame a problem"),
      ("Decision heuristics","How they choose and judge"),
      ("Expression DNA","Their voice, rhythm and vocabulary"),
      ("Values and tensions","Priorities, refusals and contradictions"),
      ("Honest limits","Where the reconstruction runs out")]
for i,(hd,bd) in enumerate(rows):
    y=1.55+i*0.96
    arrow(s,3.6,y+0.34,4.08,y+0.34,color=ORANGE)
    text(s,4.3,y,3.3,0.6,hd,size=23,bold=True,color=ORANGE,align="l",inset=0)
    text(s,7.67,y,4.85,0.62,bd,size=21,align="l",inset=0)
    if i<4: rule(s,4.3,y+0.79,8.18)

# 3. Nuwa's actual workflow. 0:50.
s=new("Nuwa studies the person before it writes the skill",n=3,
      source="Nuwa SKILL.md, Phases 0–5, and extraction-framework.md @7812110. The host agent executes this workflow.",
      notes=note("TIME 0:50. Nuwa starts with a named person and a scope. Its six research streams look at writings, long conversations, short-form expression, outside criticism, actual decisions, and the timeline. The decisions and criticism matter because stated beliefs may differ from behavior. The agent saves this research, then extracts three to seven mental models, five to ten heuristics, and the person's expression patterns. It checks whether a model recurs across domains, supports reasoning on new cases, and distinguishes this person. It writes a skill with sources and boundaries, then tests known positions, an unfamiliar question, and recognizable style. The work can be expensive, so the instructions also support reduced research and serial execution. The deliverable is a skill directory, with supporting research.","core","framework"))
text(s,0.7,1.15,11.9,0.35,"Nuwa supplies instructions. A host agent performs the research and authoring.",size=17,color=TERRA,align="l",inset=0)
for x,n,hd in [(0.7,"1","Research the person"),(4.6,"2","Distill their patterns"),(8.52,"3","Write and test the skill")]:
    marker(s,x,1.65,n,color=ORANGE,d=0.46)
    text(s,x+0.6,1.55,3.1,0.85,hd,size=23,bold=True,align="l",inset=0)
rule(s,0.7,2.48,11.9)
text(s,0.75,2.83,3.15,2.75,["Writings and interviews","Expression and criticism","Decisions and timeline"],size=22,align="l",anchor="t",inset=0,spacing=18)
arrow(s,3.75,3.82,4.22,3.82,color=ORANGE,w=2)
text(s,4.63,2.83,3.2,2.75,[{"t":"3–7 mental models","bold":True},{"t":"5–10 decision rules","before":18},{"t":"Voice, values and limits","before":18}],size=22,align="l",anchor="t",inset=0)
arrow(s,7.76,3.82,8.23,3.82,color=ORANGE,w=2)
d=doc(s,8.57,2.85,3.85,1.32,line=ORANGE)
put(d,[{"t":"Person-perspective skill","size":21,"bold":True,"color":ORANGE},{"t":"Instructions + research sources","size":16,"before":8}])
text(s,8.57,4.52,3.85,1.1,"Check known positions,\nnew questions and voice",size=22,align="l",inset=0)
shape(s,MSO_SHAPE.RECTANGLE,0.7,5.88,11.9,0.53,fill=ORANGE_L)
put(s.shapes[-1],"A useful model recurs across domains, supports new judgments and distinguishes the person.",size=19,bold=True,color=TERRA)

# 4. Concrete example with the person retained. 0:45.
s=new("Example: a Karpathy skill challenges an agent benchmark",n=4,
      source="Karpathy perspective example @7812110. The research question and response below are illustrative framework inferences.",
      notes=note("TIME 0:45. Take the Karpathy perspective included in the repository. Its documented lenses include the gap between a demo and reliable deployment, difficult tail cases, and learning from real implementations. Suppose an AI4Research agent sees a paper claiming a highly reliable research assistant. A procedure derived from those lenses would ask which task distribution the benchmark covers, what happens in a long run when tools fail, and which evidence can be reproduced. This shows how a model becomes research questions. The response is our illustration derived from the skill, not a quotation or a claim about Karpathy's view of a particular paper. These questions may also arise from a generic checklist. Added value over a generic reviewer is untested, which is why that comparator belongs in the trial.","karpathy"))
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
text(s,4.45,6.15,7.93,0.4,"Illustrative derivation. Added value over a generic reviewer is untested.",size=15,bold=True,color=TERRA,align="l",inset=0)

# 5. Value and connection to AI4R, grounded in existing agents. 0:55.
s=new("What AI4R can reuse: reasoning grounded in expert evidence",n=5,
      source="Proposed use. AI4R role context: CC Reference and skills-to-cc-mapping. No integration or task-quality gain has been measured.",
      notes=note("TIME 0:55. AI4Research is the point of studying Nuwa. The reusable lesson is how to turn documented reasoning into a procedure an agent can apply. Nuwa gathers primary material, decisions and criticism; extracts explicit models with failure conditions; and derives concrete research questions from them. We can imitate that method in hypothesis generation, experiment design and evaluation. The result could retain a named perspective or become a neutral research procedure with its intellectual sources visible. Hypothesis work should preserve competing explanations. Experiment design should turn assumptions into evidence questions. Evaluation should retain counterexamples rather than write a persuasive consensus. These are proposed improvements to how AI4R authors and uses reasoning capabilities. Their task benefit still needs measurement; importing a famous voice alone would not establish it.","core","framework","template",local="Designs/CC Reference.md; Designs/skills-to-cc-mapping.md. Proposed capability improvement, not implemented support or a measured gain."))
node(s,0.7,2.65,2.65,1.16,"Research task","problem + evidence",color=GREY,size=23)
arrow(s,3.5,3.24,4.2,3.24,color=ORANGE,w=2)
node(s,4.4,2.65,4.2,1.16,"Existing AI4R agent","applies the extracted procedure",filled=True,size=24)
arrow(s,8.76,3.24,9.43,3.24,color=ORANGE,w=2)
node(s,9.63,2.65,2.95,1.16,"Critique or test plan","then independent checks",color=TERRA,size=22)
d=doc(s,4.86,1.48,3.28,0.75,line=ORANGE)
put(d,"Evidence-derived reasoning procedure",size=17,bold=True,color=ORANGE)
arrow(s,6.5,2.28,6.5,2.54,color=ORANGE)
for i,(hd,bd) in enumerate([
    ("Hypotheses","Preserve competing models\nand their failure conditions"),
    ("Experiment design","Turn assumptions into\nconcrete evidence questions"),
    ("Evaluation","Retain criticism\nand counterexamples")]):
    x=0.75+i*4.08
    text(s,x,4.48,3.72,0.55,hd,size=24,bold=True,color=ORANGE,align="l",inset=0)
    text(s,x,5.18,3.65,0.95,bd,size=21,align="l",anchor="t",inset=0)

# 6. Limits that are specific to persona distillation. 0:50.
s=new("Nuwa's pitfalls suggest stronger checks for AI4R",n=6,
      source="Nuwa template, fidelity rubric and examples @7812110. Limits and AI4R implications are our assessment.",
      notes=note("TIME 0:50. There are four lessons to carry into AI4Research. A public record is incomplete, so we should keep claim-level sources and label inference. A distinctive voice can create authority, so scientific outputs should use evidence rather than a person's name as support. Familiar public-position tests measure a narrow kind of fidelity, so we need new research tasks and independent scoring. Finally, the quality checker counts structure and keywords: our saved empty-content probe passed all six functions, including missing sources. AI4R should fail checks when required evidence is missing and use semantic assessment separately from lint. Separate judging agents still need protection against shared-model biases. Nuwa itself acknowledges many limitations; the issue is whether its checks enforce them in the output.","template","rubric","checker","musk"))
for i,(hd,bd,imp) in enumerate([
    ("Incomplete reconstruction","Public material leaves gaps\nand becomes outdated.","Trace claims and label inference."),
    ("Authority from the voice","A convincing style can\nhide weak task evidence.","Use evidence to support conclusions."),
    ("Familiar test questions","Known positions reveal\nlittle about new research tasks.","Freeze unseen tasks and blind the scoring."),
    ("Weak structural checks","Our empty-content probe\npassed all 6 checks.","Fail missing evidence and check meaning.")]):
    y=1.62+i*1.18
    marker(s,0.75,y+0.07,str(i+1),color=ORANGE,d=0.48)
    text(s,1.48,y,3.05,0.93,hd,size=22,bold=True,color=ORANGE,align="l",anchor="t",inset=0)
    text(s,4.76,y,4.13,0.94,bd,size=20,align="l",anchor="t",inset=0)
    text(s,9.15,y,3.28,0.94,imp,size=20,bold=True,align="l",anchor="t",inset=0)
    if i<3: rule(s,1.48,y+1.03,10.95)

# 7. Additional slide: a Nuwa-inspired branch of the CC factory.
s=new("A Nuwa-like pipeline could extend the CC factory",n=7,
      source="Proposed AI4R pipeline. Resources, authoring CC and generated product CC have separate identities; normal admission remains required.",
      notes=note("TIME 0:50. This is the additional link to the CC factory. We could make a bounded Nuwa-like authoring capability that consumes a prepared expert corpus and a target research responsibility. It would extract source-linked reasoning rules, contradictions and failure conditions, then draft a reviewer CC with typed inputs and outputs. That is a proposed reasoning-skill branch within the broader factory, with a different transformation from tool wrapping. Authoring stages, evidence resources and generated product CCs have separate versions. The product still needs independent source checks, held-out task evaluation and ordinary admission. A flat pipeline should come first; a composite authoring CC can follow only if repeated value justifies it. Source preparation remains separately authorized, and the existing offline Builder should consume prepared inputs. Start with one expert-derived review procedure rather than automate every part of Nuwa.","core","framework","template",local="Designs/Capability Capsule Factory Feature.md; Designs/Per Lab Capability Factory Design.md; Designs/skills-to-cc-mapping.md. Proposed M2 branch, not implemented or admitted."))
text(s,0.7,1.43,11.9,0.4,"Proposed M2 reasoning-method branch, with a flat authoring workflow first",size=19,bold=True,color=TERRA,align="l",inset=0)
shape(s,MSO_SHAPE.RECTANGLE,3.05,2.05,9.55,2.1,fill=ORANGE_L)
text(s,3.3,2.17,8.95,0.35,"CC-factory authoring pipeline",size=17,bold=True,color=ORANGE,align="l",inset=0)
node(s,0.7,2.72,2.0,1.12,"Evidence resources","prepared corpus",color=GREY,size=19)
arrow(s,2.82,3.28,3.23,3.28,color=ORANGE)
node(s,3.35,2.72,3.65,1.12,"Authoring stage CCs","extract rules and draft a contract",filled=True,size=21)
arrow(s,7.13,3.28,7.87,3.28,color=ORANGE)
node(s,8.0,2.72,4.27,1.12,"Candidate reviewer-method CC","rules + sources + limits",size=21)
arrow(s,10.13,4.0,10.13,4.5,color=TERRA,head=False)
arrow(s,10.13,4.5,5.15,4.5,color=TERRA,head=False)
arrow(s,5.15,4.5,5.15,4.87,color=TERRA)
text(s,0.75,4.72,2.05,1.18,"Failures return for revision or stop.",size=18,bold=True,color=TERRA,align="l",anchor="t",inset=0)
node(s,3.1,5.0,4.1,1.08,"Independent qualification","source checks + unseen task tests",color=TERRA,size=22)
arrow(s,7.33,5.54,7.97,5.54,color=TERRA)
node(s,8.1,5.0,4.4,1.08,"Existing admission gate","passing products enter future plans",color=TERRA,size=22)

# 7. What we can do, without importing a different workflow. 0:50.
s=new("One expert-derived review method is enough for a first trial",n=8,
      source="Proposed AI4R trial. Same-evidence comparison isolates the skill's contribution. No comparative result exists yet.",
      notes=note("TIME 0:50. Start with one source-rich expert corpus and one bounded responsibility, such as reviewing an agent benchmark. Use Nuwa's extraction method to draft a neutral, source-linked review procedure. Pin the procedure and cutoff, and require outputs to distinguish source-supported rules, framework inference and current task evidence. Compare it against a plain reviewer and a length-matched generic review checklist. All arms get the same expert-source excerpts and task evidence, model, tools and runtime budget. Freeze new tasks and scoring before generation, and use blinded human judgment. Measure supported useful objections, missed failures, calibration and cost. Record authoring cost separately. Retain the procedure only if it improves real review behavior beyond the generic checklist. A persona-voice ablation can follow later if relevant.","core","rubric",local="Designs/skills-to-cc-mapping.md; separate proposal, not a revision to the maintained accuracy study."))
for i,(hd,bd) in enumerate([
    ("Choose one expert corpus","A documented reasoning method\nfor one research responsibility"),
    ("Make the use explicit","Pinned skill and cutoff\nSources separate from inference"),
    ("Compare on new tasks","Same evidence and budget\nAgainst a generic checklist")]):
    x=0.75+i*4.05
    text(s,x,1.72,3.63,0.7,str(i+1),size=42,bold=True,color=ORANGE,align="l",inset=0)
    text(s,x,2.68,3.65,0.94,hd,size=26,bold=True,align="l",anchor="t",inset=0)
    text(s,x,3.98,3.65,1.45,bd,size=22,align="l",anchor="t",inset=0)
rule(s,0.75,5.65,11.8)
text(s,0.75,5.94,11.75,0.55,"Keep it when it adds useful, supported objections at an acceptable cost.",size=23,bold=True,color=TERRA,align="l",inset=0)

# 8. Close with the actual Nuwa value proposition. 0:30.
s=new("A method worth testing in AI4Research",n=9,
      source="Assessment and proposed next step. AI4R adapts the extraction method; task-quality benefit remains unmeasured.",
      notes=note("TIME 0:30. Nuwa shows how documented human reasoning can become a reusable skill. For AI4Research, we should learn the evidence-to-procedure method: preserve sources and disagreement, extract usable rules, and derive concrete investigation steps. A Nuwa-like authoring pipeline could become a reasoning-skill branch of the CC factory. We should improve its assurance with explicit source checks, independent unseen tasks and bounded cost. The next decision is whether one such reviewer improves real AI4R work beyond an equally informed agent. That experiment earns further integration; resemblance to a person does not.","core","template",local="Designs/skills-to-cc-mapping.md; Designs/Capability Capsule Factory Feature.md"))
text(s,0.75,1.83,6.52,2.1,"Expert reasoning\ncould become a reusable\nresearch procedure.",size=36,bold=True,color=ORANGE,align="l",anchor="t",inset=0)
text(s,0.75,4.45,6.3,1.3,"Imitate extraction and evidence handling.\nMeasure whether research improves.",size=24,align="l",anchor="t",inset=0)
shape(s,MSO_SHAPE.RECTANGLE,7.75,1.75,4.78,4.45,fill=ORANGE_L)
text(s,8.08,2.08,4.12,0.6,"The next decision",size=23,bold=True,color=ORANGE,align="l",inset=0)
text(s,8.08,3.13,4.12,2.0,"Does one extracted procedure improve AI4R reviews on unseen work?",size=29,bold=True,align="l",anchor="t",inset=0)
text(s,8.08,5.47,4.12,0.7,"One skill. One role. A fair comparison.",size=18,bold=True,color=TERRA,align="l",inset=0)

# 9. Hidden backup: what the score measures.
s=new("Backup: distinguish extracted methods from generic prompting",n=10,backup=True,
      source="Proposed comparison after Luna review. Nuwa's fidelity reports do not establish AI4R task benefit.",
      notes=note("BACKUP. All arms receive the same frozen expert-source excerpts and task evidence. The plain reviewer gets no added procedure. The generic arm gets a length-matched general review checklist. The extracted-method arm gets neutral rules and limits produced through the Nuwa-inspired process. Hold the model, tools, permissions and runtime budgets fixed, freeze unseen tasks and scoring before generation, and blind human assessment. Judge supported useful objections, missed failure modes, unsupported claims, uncertainty, latency and cost. Record corpus preparation and authoring effort separately from runtime cost. This identifies the increment beyond a generic checklist, not the causal effect of each Nuwa phase. A later voice ablation can test whether persona framing helps or hurts. No experimental result is claimed.","rubric",local="Designs/skills-to-cc-mapping.md; Luna adversarial review, 2026-10-23."))
table(s,0.75,1.68,[3.1,4.45,4.25],[
    ["Arm","Added instructions","What the comparison estimates"],
    ["Plain reviewer","No added procedure","Baseline with identical sources"],
    ["Generic checklist","Length-matched general review instructions","Benefit of structured prompting"],
    ["Extracted method","Neutral Nuwa-derived rules and limits","Increment beyond a generic checklist"]],size=18,rh=0.9)
text(s,0.8,5.2,11.7,1.08,"Same expert excerpts, task evidence, model, tools and runtime budget.\nFreeze unseen tasks and scoring first. Record authoring cost separately.",size=20,align="l",anchor="t",inset=0)

# 10. Hidden backup: governed use, separate from the creation workflow.
s=new("Backup: governed use would pin the skill inside a bounded CC",n=11,backup=True,
      source="AI4R CC Reference and skills-to-cc-mapping. Proposed adaptation, not an implemented Nuwa integration.",
      notes=note("BACKUP. A skill is an instruction bundle, not a capsule declaration or runtime permission. For governed use, bind a pinned skill body and evidence resources to a selected agent responsibility. Declare typed task and evidence inputs, a structured critique output, tool needs, effects, budgets and failure behavior. Changes to the worker body require the existing versioning, checks and admission path. The semantic verifier remains declaration-and-output-only; source/input-dependent checks belong in the protected host path. Nuwa's creation workflow can remain an authoring tool while this deployment is tested. Automating that workflow is a later choice, not a prerequisite or the main value proposition.","core","template",local="Designs/CC Reference.md; Designs/skills-to-cc-mapping.md"))
table(s,0.75,1.68,[3.15,4.75,3.9],[
    ["Element","Proposed binding","Reason"],
    ["Person-perspective skill","Pin body, source manifest and cutoff","Repeatable version of the perspective"],
    ["Agent responsibility","Choose one task step; explicit activation","Avoid silent influence on unrelated work"],
    ["Inputs and output","Task + evidence; supported critique + uncertainty","Make behavior and failures inspectable"],
    ["Tools and effects","Explicit needs, budgets and permissions","Prompt instructions confer no runtime authority"],
    ["Checks and admission","Ordinary CC versioning and independent checks","Generation alone does not approve deployment"]],size=16,rh=0.77)

OUT.parent.mkdir(exist_ok=True)
prs.save(OUT)
print("wrote",OUT,"with",len(prs.slides),"slides (9 main, 2 hidden)")


