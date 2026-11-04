"""Build the Paper2Agent talk with native PowerPoint shapes (revision 9: factory alignment).

Run: python build_pptx.py
Writes "Paper2Agent Talk rev9.pptx" beside this file. Eight shown slides, two hidden backups.
Replaces the tundlekit deck.json route (build_deck.py, revision 6), which could not express these layouts.
"""
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
OUT = HERE / "Paper2Agent Talk rev9.pptx"

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
        label = "Paper2Agent overview" + ("  |  Backup" if backup else "")
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


# ---------------------------------------------------------------- 1. Opening
s = new(notes="TIME 0:20. Start with the value. For AI4Research, Paper2Agent is a repeatable way to turn research code into reusable, source-linked capabilities, so agents stop regenerating analysis code for every task. It is worth adapting as a capability-production pattern. The strip shows the story in one line. The strip shows the whole story in one line: research artifacts go in, a preparation workflow runs, and callable capabilities come out. Everything after this shows how, what it gives us, and one limit.")
text(s, 0.9, 1.0, 11.5, 1.1, "Paper2Agent", size=58, bold=True, color=INDIGO, align="l", inset=0)
text(s, 0.9, 2.15, 11.5, 0.7, "From research code to reusable capabilities", size=30, align="l", inset=0)
text(s, 0.9, 2.95, 11.5, 0.5, "What it does, where it adds value, and how it could fit AI4Research", size=18, color=GREY, align="l", inset=0)
shape(s, MSO_SHAPE.RECTANGLE, 0.9, 3.85, 0.08, 0.5, fill=TEAL)
text(s, 1.1, 3.85, 11.0, 0.5, "Value to AI4Research: research code becomes reusable, source-linked capabilities", size=18, bold=True, color=TEAL, align="l", inset=0)
d = doc(s, 0.9, 5.0, 3.3, 1.2, fill="FFFFFF", line=GREY)
put(d, [{"t": "Research artifacts", "bold": True, "size": 18}, {"t": "paper, notebooks, code", "size": 14, "color": GREY}])
arrow(s, 4.3, 5.6, 5.1, 5.6)
r = rbox(s, 5.2, 5.0, 3.3, 1.2, fill=INDIGO)
put(r, [{"t": "Preparation workflow", "bold": True, "size": 18, "color": "FFFFFF"}, {"t": "run, wrap, check, package", "size": 14, "color": "DDE0F5"}])
arrow(s, 8.6, 5.6, 9.4, 5.6)
p = rbox(s, 9.5, 5.0, 3.3, 1.2, fill="FFFFFF", line=INK, lw=2)
put(p, [{"t": "Callable capabilities", "bold": True, "size": 18}, {"t": "tested, source-linked", "size": 14, "color": GREY}])
text(s, 0.9, 6.95, 6, 0.3, "Overview, October 2026", size=11, color=GREY, align="l", inset=0)

# ---------------------------------------------------------------- 2. Pipeline
s = new("Run the original method, then extract and check tools", n=3,
        source="Paper2Agent repository at commit 8c2d059: skill instructions and orchestration notes. Read, not run.",
        notes="TIME 0:50. Two branches. The paper branch builds a reading skill and is secondary here. The code branch is the story. Select the operations the code supports. Run the upstream code first to get reference outputs. Write thin wrappers that turn example code into callable functions. Check: a fresh verifier compares wrapper and upstream, and may repair the wrapper, then the tools are mounted and really called. Package a ZIP and test it from a clean location. The system does not invent an implementation from the paper; it prepares tested interfaces around existing software and examples. The repository lists six gated stages; mount-and-run is folded into Check here. We read these instructions at a pinned commit and have not run them. Question likely: does it need a special host? Yes, it assumes a coding-agent host that runs skills and spawns parallel agents.")
stages = [("01", "Select", "Identify supported operations", "Task inventory"),
          ("02", "Run", "Execute upstream examples", "Reference outputs"),
          ("03", "Wrap", "Define reusable interfaces", "Tool functions"),
          ("04", "Check", "Compare behavior, then call the tools", "Test report"),
          ("05", "Package", "Assemble and test from a clean location", "Tool package")]
W, G, X0 = 2.25, 0.2, 0.64
for i, (num, name, act, art) in enumerate(stages):
    x = X0 + i * (W + G)
    h = shape(s, MSO_SHAPE.PENTAGON, x, 1.75, W, 0.8, fill=INDIGO, adj=0.3)
    put(h, [{"t": f"{num}  {name}", "bold": True, "size": 20, "color": "FFFFFF"}], align="l", inset=0.18)
    text(s, x, 2.7, W, 0.95, act, size=16, align="l", anchor="t", inset=0.05)
    text(s, x, 3.7, W, 0.25, "ARTIFACT", size=10, bold=True, color=GREY, align="l", inset=0.05)
    dd = doc(s, x, 3.98, W - 0.1, 0.75, fill="FFFFFF", line=INDIGO)
    put(dd, art, size=15, bold=True, color=INDIGO)
text(s, X0 + 3 * (W + G), 4.85, W, 0.8, "A fresh verifier may repair the wrapper", size=13, color=AMBER, align="l", anchor="t", inset=0.05)
b = rbox(s, 0.64, 5.35, 6.2, 1.0, fill=None, line=GREY, dash=True)
put(b, [{"t": "Paper branch (secondary)", "bold": True, "size": 14, "color": GREY},
        {"t": "Page-by-page review of the paper builds a reading skill", "size": 14, "color": GREY}], align="l", inset=0.2)
text(s, 7.2, 5.35, 5.5, 1.0, "Upstream code runs first. Wrappers stay thin. Every stage records evidence.", size=17, bold=True, align="l", inset=0)

# ---------------------------------------------------------------- 3. Example
s = new("One research operation becomes a candidate tool capsule", n=5, tag="Illustrative mapping",
        source="Illustrative mapping, not an implemented integration. The capsule fields are our proposal.",
        notes="TIME 0:55. One operation, end to end. A notebook clusters a fixed example dataset; the setup is manual and the outputs stay inside the notebook. The factory gets a pinned source snapshot from a separate acquisition capsule, prepares the environment, extracts the operation and runs checks. The result is a candidate product capsule with no standing: its draft declaration is adapted to the capsule contract with a dataset artifact and parameters in, and results, figures and a run record out, plus a declared environment, source link and test evidence. A capsule may expose one operation or a coherent set. Two calls exist: the factory call prepares a candidate from an authorized snapshot; the product call later runs the admitted capability. An MCP package is an input to capsule adaptation, not automatically a capsule. Likely questions: why not one big composite now? Composites are deferred in M1 and member-level checks must survive inside one. Is source acquisition allowed today? Not for intake; it needs its own authorized preparation path.")
PW, PG, PX = 3.55, 0.7, 0.64
px = [PX + i * (PW + PG) for i in range(3)]
for i, name in enumerate(["SOURCE", "FACTORY", "CANDIDATE CC"]):
    text(s, px[i], 1.6, PW, 0.3, name, size=12, bold=True, color=INDIGO if i == 1 else GREY, align="l", inset=0.02)
rbox(s, px[0], 1.95, PW, 3.5, fill=PANEL, adj=0.04)
for k, (head, sub) in enumerate([("Analysis notebook", "fixed example dataset"),
                                  ("Original examples", "manual edits and setup"),
                                  ("Pinned repository", "from a separate acquisition capsule")]):
    dd = doc(s, px[0] + 0.2, 2.15 + k * 1.05, PW - 0.4, 0.88, fill="FFFFFF", line=GREY)
    put(dd, [{"t": head, "bold": True, "size": 16}, {"t": sub, "size": 12.5, "color": GREY}], align="l", inset=0.15)
rbox(s, px[1], 1.95, PW, 3.5, fill=INDIGO_L, adj=0.04)
for k, step in enumerate(["Prepare environment", "Extract operation", "Run checks"]):
    st = rbox(s, px[1] + 0.25, 2.2 + k * 1.05, PW - 0.5, 0.8, fill=INDIGO)
    put(st, step, size=17, bold=True, color="FFFFFF")
    if k < 2:
        arrow(s, px[1] + PW / 2, 3.0 + k * 1.05, px[1] + PW / 2, 3.25 + k * 1.05, color=INDIGO, w=1.5)
pk = rbox(s, px[2], 1.95, PW, 3.5, fill="FFFFFF", line=INK, lw=2.25, adj=0.04)
for k, (head, sub) in enumerate([("Input contract", "dataset + parameters"),
                                  ("Output contract", "results, figures, run record"),
                                  ("Runtime requirements", "declared environment, limits"),
                                  ("Evidence", "source link + test results")]):
    text(s, px[2] + 0.2, 2.1 + k * 0.82, PW - 0.4, 0.75,
         [{"t": head, "bold": True, "size": 16}, {"t": sub, "size": 12.5, "color": GREY}], align="l", anchor="t", inset=0.05)
arrow(s, px[0] + PW + 0.05, 3.7, px[1] - 0.05, 3.7)
arrow(s, px[1] + PW + 0.05, 3.7, px[2] - 0.05, 3.7)
text(s, px[1] + PW + 0.05, 3.2, PG - 0.1, 0.4, "adapt", size=11, color=GREY, inset=0)
iv = rbox(s, 0.64, 5.7, 12.05, 0.8, fill="FFFFFF", line=RULE, adj=0.2)
put(iv, [{"t": "Invocation:   input = dataset artifact + parameters      →      output = result artifact + figures + execution record", "size": 16, "bold": True}])

# ---------------------------------------------------------------- 4. Evidence
s = new("Reported results support feasibility across research packages", n=4,
        source="Paper2Agent pinned manuscript paper.md, lines 139 and 183; authors' reported results. Different arXiv versions should not be mixed.",
        notes="TIME 0:45. Three different measures, shown separately on purpose. Task performance: on fifteen novel questions about one genomics tool, five runs, the authors' agent scores 100 percent against 78.7 percent for Claude reading the repository. Breadth: on ten non-biology papers and 42 execution tasks, five runs, 98.1 percent accuracy; this is execution-task accuracy as reported in the paper. Conversion: of 100 papers, 74 converted, and 593 of 599 proposed tools passed automated validation. A validation pass is not scientific correctness. Together this suggests feasibility at scale. It does not show performance in AI4Research. These values were checked against paper.md in the pinned local reference clone; they remain authors' reported results, not our replication.")
CW, CG, CX = 3.9, 0.2, 0.6
cards = [("TASK PERFORMANCE", [("100% vs 78.7%", "authors' agent vs Claude with the repository"),],
          "15 novel questions, one genomics tool, 5 runs"),
         ("BREADTH", [("98.1%", "accuracy on execution tasks")],
          "10 non-biology papers, 42 tasks, 5 runs"),
         ("CONVERSION", [("74 of 100", "papers converted"), ("593 of 599", "tools pass automated validation")],
          "Validation is automated; it is not scientific correctness")]
for i, (head, stats, foot) in enumerate(cards):
    x = CX + i * (CW + CG)
    rbox(s, x, 1.65, CW, 3.9, fill="FFFFFF", line=RULE, adj=0.05)
    shape(s, MSO_SHAPE.RECTANGLE, x, 1.65, CW, 0.09, fill=INDIGO)
    text(s, x + 0.25, 1.9, CW - 0.5, 0.3, head, size=12, bold=True, color=GREY, align="l", inset=0)
    y = 2.35
    for big, cap in stats:
        text(s, x + 0.25, y, CW - 0.5, 0.8, big, size=30 if len(big) > 10 else 34, bold=True, color=INDIGO, align="l", inset=0)
        text(s, x + 0.25, y + 0.8, CW - 0.5, 0.6, cap, size=15, align="l", anchor="t", inset=0)
        y += 1.35
    text(s, x + 0.25, 4.5 if len(stats) == 1 else 4.85, CW - 0.5, 0.5, foot, size=12.5, color=GREY, align="l", anchor="t", inset=0)
text(s, 0.6, 5.85, 12.1, 0.6, "Preparation looks feasible at scale. Local benefit for AI4Research is unmeasured.", size=18, bold=True, align="l", inset=0)

# ---------------------------------------------------------------- 5. Value
s = new("Value: reusable capabilities from a process with evidence", n=2, tag="Value to AI4Research",
        source="Our assessment. These are potential benefits to evaluate, not measured results.",
        notes="TIME 0:45. The value to AI4Research, first. Why it matters. First, agents call established implementations instead of regenerating analysis code for each task. Second, setup, interfaces and validated execution paths are prepared once and carried forward, with the environment, source links and checks kept. Third, external research software becomes a source of candidate capabilities, feeding review and admission with structured evidence. The preparation steps themselves, acquisition, environment preparation and packaging, also serve other capability-building work. Capsules already give us the abstraction; Paper2Agent suggests a process for making some of them. These are benefits to assess, not measured results.")
panels = [("THE IDEA", TEAL, "Turn research code into capabilities agents can call",
           ["Reuse established scientific code instead of regenerating it for each task",
            "Grow the capability library from existing research software"]),
          ("THE METHODOLOGY", INDIGO, "A gated process that records its evidence",
           ["Run the upstream code first; wrappers stay thin",
            "Source links and test results travel with each tool, ready for review"])]
for i, (lab, col, head, pts) in enumerate(panels):
    x = 0.6 + i * 6.15
    rbox(s, x, 1.75, 5.95, 4.4, fill="FFFFFF", line=RULE, adj=0.04)
    shape(s, MSO_SHAPE.RECTANGLE, x, 1.75, 5.95, 0.09, fill=col)
    text(s, x + 0.35, 2.05, 5.2, 0.3, lab, size=13, bold=True, color=col, align="l", inset=0)
    text(s, x + 0.35, 2.5, 5.25, 1.3, head, size=26, bold=True, align="l", anchor="t", inset=0)
    for k, pt in enumerate(pts):
        shape(s, MSO_SHAPE.OVAL, x + 0.38, 4.25 + k * 0.95 + 0.1, 0.14, 0.14, fill=col)
        text(s, x + 0.65, 4.15 + k * 0.95, 5.0, 0.9, pt, size=17, align="l", anchor="t", inset=0)

# ---------------------------------------------------------------- 6. Integration
s = new("The factory makes candidates and evidence", n=6, tag="Proposed integration",
        source="Proposed: Designs/Paper2Agent Capability Factory and Capability Capsule Factory Feature. Not implemented in M1.",
        notes="TIME 0:55. The factory is a proposed governed workflow whose bounded stage capsules inspect, run, wrap, check and package. Its orchestration form remains open: a flat host plan first, perhaps a composite capsule later. Keep three things separate: factory and stage capsules do the work; generated product capsules are candidates; versioned resources hold the pinned source and evidence. The diagram's lower line is that resource record, not another executable capsule. A candidate gets ordinary independent admission before it can be invoked. Admitting a factory stage never admits its products. Acquisition is a separate authorized preparation capsule supplying a pinned snapshot; our M1 intake cannot clone repositories, and our Builder is offline. Paper-only input may yield a reviewed reading resource. Today's policy and plan gaps are in backup slide 10. This is our adaptation proposal, not current upstream JiuwenSwarm behavior or a demonstrated runtime result.")
cy, ch = 2.0, 1.7
items = [("sources", 0.5, 1.4), ("factory", 2.25, 2.3), ("cands", 4.9, 1.6), ("gate", 6.85, 2.0), ("admitted", 9.2, 1.75), ("agent", 11.3, 1.5)]
cx = {k: (x, w) for k, x, w in items}
dd = doc(s, 0.5, cy, 1.4, ch, line=GREY)
put(dd, [{"t": "Authorized sources", "bold": True, "size": 14}])
fb = rbox(s, 2.25, cy, 2.3, ch, fill=INDIGO)
put(fb, [{"t": "Factory flow", "bold": True, "size": 17, "color": "FFFFFF"},
         {"t": "bounded stage CCs", "size": 12, "color": "DDE0F5", "before": 4},
         {"t": "select · run · wrap · check", "size": 11, "color": "DDE0F5"}])
for k, nm in enumerate(["tool A", "tool B", "tool C"]):
    pkg = rbox(s, 4.9, cy + k * 0.6 - 0.05, 1.6, 0.5, fill="FFFFFF", line=INK, lw=1.75, adj=0.2)
    put(pkg, nm, size=13, bold=True)
dm = shape(s, MSO_SHAPE.DIAMOND, 6.85, cy - 0.15, 2.0, ch + 0.3, fill="FFFFFF", line=INK, lw=2)
put(dm, [{"t": "Adapt +", "bold": True, "size": 14}, {"t": "admit", "bold": True, "size": 14}])
ad = rbox(s, 9.2, cy, 1.75, ch, fill=TEAL)
put(ad, [{"t": "Admitted scientific CCs", "bold": True, "size": 15, "color": "FFFFFF"}, {"t": "versioned, standing recorded", "size": 11, "color": "DFF1F1", "before": 4}])
ag = rbox(s, 11.3, cy, 1.5, ch, fill="FFFFFF", line=TEAL, lw=2)
put(ag, [{"t": "Research agent invokes", "bold": True, "size": 14}, {"t": "only if authorized", "size": 11, "color": GREY, "before": 4}])
for a, b in [(1.9, 2.25), (4.55, 4.9), (6.5, 6.85), (8.85, 9.2), (10.95, 11.3)]:
    arrow(s, a + 0.02, cy + ch / 2, b - 0.02, cy + ch / 2)
caps = [(0.5, 1.4, "Pinned snapshot from separate acquisition"),
        (2.25, 2.3, "Flat plan first; composite later"),
        (4.9, 1.6, "Candidate product CCs; no standing"),
        (6.85, 2.0, "Contract adaptation + independent evidence"),
        ]
for x, w, c in caps:
    text(s, x - 0.1, cy + ch + 0.3, w + 0.2, 0.9, c, size=12, color=GREY, anchor="t", inset=0)
# provenance (dashed): sources -> under row -> admitted
arrow(s, 0.5, cy + ch / 2, 0.28, cy + ch / 2, color=TEAL, dash=True, head=False)
arrow(s, 0.28, cy + ch / 2, 0.28, 4.95, color=TEAL, dash=True, head=False)
arrow(s, 0.28, 4.95, 10.07, 4.95, color=TEAL, dash=True, head=False)
arrow(s, 10.07, 4.95, 10.07, cy + ch + 0.02, color=TEAL, dash=True)
text(s, 2.2, 4.98, 8.1, 0.3, "Versioned resources: source, references, checks, package record", size=12, color=TEAL, inset=0)
bd = rbox(s, 0.6, 5.65, 12.1, 0.8, fill=AMBER_L, line=AMBER, lw=1.5, adj=0.2)
put(bd, "Factory admission does not automatically admit its products.", size=20, bold=True)

# ---------------------------------------------------------------- 7. Limit
s = new("One limit: the tool and its checks share the same sources", n=7,
        source="Our reading of the design and repository text (runtime.md, orchestration.md). Risks to check, not findings.",
        notes="TIME 0:50. One limit matters for how we read the evidence. Top lane: the authors' materials, data, code, tutorials and the paper, all public and linked. Middle lane: Paper2Agent reads them, runs the code to get a reference, an LLM writes a wrapper, and a fresh verifier compares wrapper to reference and may repair the wrapper. Bottom lane: evaluation questions come largely from the same tutorials. Three coupling points. One: results in the paper were chosen on the data; if the code was tuned on it, the wrapper inherits that. This is an inference, not a documented fact. Two: the reference is the source; tests are the tutorial computation and the verifier may repair until they pass. Three: the questions come from the material the tool was built from. What a pass does show: the wrapper reproduces tested upstream behavior, which is good evidence of faithful wrapping. It does not independently validate the science. Strictly this is not leakage: the evaluated agent is not given the expected answer. The issue is that building and testing share one source. Integration also depends on usable code, accessible data, licensing and a supported environment.")
lanes = [("AUTHORS, BEFORE PAPER2AGENT", 1.6), ("PAPER2AGENT BUILDS THE TOOL", 3.25), ("EVALUATION", 4.9)]
for name, y in lanes:
    rbox(s, 0.6, y, 7.9, 1.45, fill=PANEL, adj=0.06)
    text(s, 0.75, y + 0.05, 5, 0.28, name, size=10.5, bold=True, color=GREY, align="l", inset=0)
for k, (nm, sub) in enumerate([("Data D", ""), ("Code C", "used on D"), ("Tutorials T", "demos on D"), ("Paper P", "results on D")]):
    d = doc(s, 0.8 + k * 1.9, 2.0, 1.65, 0.85, fill="FFFFFF", line=GREY)
    put(d, [{"t": nm, "bold": True, "size": 14}] + ([{"t": sub, "size": 11, "color": GREY}] if sub else []))
marker(s, 8.0, 1.88, "1")
steps = [(0.8, 2.3, "Run C on D", "reference R"), (3.4, 2.1, "LLM writes", "wrapper W"), (5.8, 2.5, "Verifier: W vs R", "may repair W")]
for x, w, a, b2 in steps:
    r = rbox(s, x, 3.65, w, 0.85, fill="FFFFFF", line=INDIGO, lw=1.75)
    put(r, [{"t": a, "bold": True, "size": 14}, {"t": b2, "size": 11.5, "color": GREY}])
arrow(s, 3.12, 4.07, 3.38, 4.07, color=INDIGO)
arrow(s, 5.52, 4.07, 5.78, 4.07, color=INDIGO)
arrow(s, 4.2, 2.88, 4.2, 3.63, color=GREY, dash=True)
text(s, 4.3, 2.93, 1.8, 0.3, "public sources", size=10.5, color=GREY, inset=0, align="l")
marker(s, 8.0, 3.57, "2")
q = rbox(s, 0.8, 5.3, 2.5, 0.85, fill="FFFFFF", line=TEAL, lw=1.75)
put(q, [{"t": "Questions", "bold": True, "size": 14}, {"t": "from tutorials + novel", "size": 11.5, "color": GREY}])
sc = rbox(s, 3.85, 5.3, 2.3, 0.85, fill="FFFFFF", line=TEAL, lw=1.75)
put(sc, [{"t": "Score", "bold": True, "size": 14}, {"t": "vs baseline agent", "size": 11.5, "color": GREY}])
tp = rbox(s, 6.7, 5.3, 1.6, 0.85, fill="FFFFFF", line=INK, lw=1.75, adj=0.2)
put(tp, "Tool package", size=13, bold=True)
arrow(s, 3.32, 5.72, 3.83, 5.72, color=TEAL)
arrow(s, 6.68, 5.72, 6.17, 5.72, color=TEAL)
arrow(s, 7.5, 4.52, 7.5, 5.28, color=INDIGO)
marker(s, 3.1, 5.18, "3")
lg = [("1", "Selection", "Results in the paper were chosen on the data. If the code was tuned on it, the wrapper inherits that."),
      ("2", "Reference is the source", "Tests are the tutorial computation, and the verifier may repair the wrapper. A pass shows the wrapper matches the code."),
      ("3", "Same material", "Benchmark questions come from the tutorials the tool was built from.")]
for k, (n, hd, bd2) in enumerate(lg):
    y = 1.6 + k * 1.3
    marker(s, 8.9, y + 0.03, n)
    text(s, 9.4, y, 3.35, 0.35, hd, size=16, bold=True, align="l", anchor="t", inset=0)
    text(s, 9.4, y + 0.36, 3.35, 0.9, bd2, size=12.5, color=INK, align="l", anchor="t", inset=0)
ck = shape(s, MSO_SHAPE.OVAL, 8.9, 5.53, 0.36, 0.36, fill=TEAL)
put(ck, "✓", size=14, color="FFFFFF", bold=True, inset=0)
text(s, 9.4, 5.5, 3.35, 0.35, "What a pass does show", size=16, bold=True, color=TEAL, align="l", anchor="t", inset=0)
text(s, 9.4, 5.86, 3.35, 0.8, "The wrapper reproduces tested upstream behavior: faithful wrapping, not independent validation.", size=12.5, align="l", anchor="t", inset=0)

# ---------------------------------------------------------------- 8. Conclusion
s = new("Adapt the pattern; demonstrate one complete mapping", n=8,
        source="Proposed direction. Reconcile with PRD V10 and the maintained M1 design before any implementation.",
        notes="TIME 0:30. To close. Value: research implementations become reusable, source-linked capabilities. Fit: factory stages, candidate products, and versioned resources have separate identities; acquisition is a separate authorized preparation capsule. Next: map one representative repository into the existing capsule contract and list the adaptations needed. A bounded pilot is the follow-on, in the backup. Tested behavior is not independent scientific validation. Licences, data and hardware can also block a tool.")
blocks = [("VALUE", INDIGO, "Research implementations become reusable capabilities."),
          ("FIT", TEAL, "Factory stages, product CCs and resources stay distinct."),
          ("NEXT", INK, "Map one repository into the existing capsule contract.")]
for i, (lab, col, msg) in enumerate(blocks):
    x = CX + i * (CW + CG)
    rbox(s, x, 1.7, CW, 3.3, fill="FFFFFF", line=RULE, adj=0.05)
    shape(s, MSO_SHAPE.RECTANGLE, x, 1.7, 0.09, 3.3, fill=col)
    text(s, x + 0.35, 2.0, CW - 0.6, 0.4, lab, size=14, bold=True, color=col, align="l", inset=0)
    text(s, x + 0.35, 2.6, CW - 0.6, 2.2, msg, size=24, bold=True, align="l", anchor="t", inset=0)
shape(s, MSO_SHAPE.OVAL, 0.64, 5.65, 0.3, 0.3, fill=AMBER)
text(s, 1.1, 5.55, 11.5, 0.5, "Tested behavior is not independent scientific validation.", size=18, color=INK, align="l", inset=0)

# ---------------------------------------------------------------- 9. Backup: pilot
s = new("Backup: a bounded pilot with hidden tests first", n=9, backup=True,
        source="Proposed pilot. Thresholds not set. Reconcile with PRD V10 before any implementation.",
        notes="Backup: the pilot design, with controls against the coupling points. A pass covers the cases tested; it does not prove scientific truth.")
table(s, 0.6, 1.5, [3.0, 9.1], [["Element", "Design"],
      ["Three arms", "Direct use of the repository, a governed wrapper, a CC-admitted wrapper"],
      ["Held constant", "Same pinned repository, data, model, permissions and preparation budget"],
      ["Fixed before generation", "Required capabilities; hidden changed-input and failure tests written by an evaluator, not the verifier"],
      ["Against coupling", "Fresh data from after the paper; questions beyond the tutorials; report coverage, not only pass rate"],
      ["Measured", "Capability coverage, hidden-test results, preparation cost, admission outcome, maintenance burden"],
      ["Continue if", "Source-linked candidates pass the held-out gate at manageable cost"],
      ["Stop or narrow if", "Licence, data, environment or fidelity fails, or the wrapper adds little"]], size=15, rh=0.62)

# ---------------------------------------------------------------- 10. Backup: M1 gaps
s = new("Backup: where today's M1 stands against this flow", n=10, backup=True,
        source="Designs/Paper2Agent Briefing/1 Decision brief. Proposals, not adopted M1 behavior.",
        notes="Backup: the M1 gaps and the smallest resolution for each. Composition is deferred; intake cannot clone; the Builder is offline; RSI is limited to Screening.")
table(s, 0.6, 1.5, [3.9, 3.9, 4.3], [["Current M1 shape", "Gap", "Minimum proposed resolution"],
      ["Fixed research workflow, one Delivery leaf", "A factory needs a different terminal product", "Capability-factory profile; pilot a flat plan"],
      ["Agent and tool CCs only; composition deferred", "No factory composite today", "Flat orchestration first; decide on composites after the pilot"],
      ["Offline Builder; intake excludes cloning", "No general source-acquisition route", "Authorized preparation handoff with pinned provenance and licence findings"],
      ["Narrow Screening RSI target", "A factory may touch resources, CCs or plans", "Keep target scope explicit; no whole-system RSI authority implied"]], size=14, rh=0.95)

ids = prs.slides._sldIdLst
order = [0, 4, 1, 3, 2, 5, 6, 7, 8, 9]
items = list(ids)
for el in items:
    ids.remove(el)
for i in order:
    ids.append(items[i])
prs.save(OUT)
print("wrote", OUT.name, len(prs.slides._sldIdLst), "slides")
