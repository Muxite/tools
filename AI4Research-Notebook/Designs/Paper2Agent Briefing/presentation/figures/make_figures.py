"""Draw the three talk figures (workflow, leakage, fit) with the tundlekit palette.

Run: python make_figures.py   (writes workflow/leakage/fit .png and .svg beside it)
Figures are 11.8 x 4.4 in so the deck can show them full width without shrinking text.
"""
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

HERE = Path(__file__).parent
GREY, BLUE, GREEN, RED, PURPLE, ORANGE, BROWN, INK = (
    '#6b6b6b', '#3D4FB0', '#008A63', '#D55E00', '#7B3FA0', '#D98200', '#8C5A2B', '#000000')
CYAN, PINK = '#0072B2', '#B8527F'
plt.rcParams['font.family'] = 'DejaVu Sans'
W, H = 118, 44


def canvas():
    fig = plt.figure(figsize=(11.8, 4.4), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    return fig, ax


def band(ax, x0, y0, x1, y1, color, fill, title, tx=None, size=11):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle='round,pad=0,rounding_size=1',
                                fc=fill, ec=color, lw=1.2, ls='--'))
    ax.text(tx if tx is not None else x0 + 1, y1 - 1.5, title, color=color, fontsize=size,
            fontweight='bold', va='center')


def box(ax, x, y, w, h, title, sub, color, fill='white', tag=None, record=False, size=12):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=1' if not record else 'square,pad=0',
                                fc=fill, ec=color, lw=1.8))
    cy = y + h / 2 + (0.9 if sub else 0)
    ax.text(x + w / 2, cy, title, ha='center', va='center', fontsize=size, fontweight='bold',
            color=INK, linespacing=1.2)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 1.7, sub, ha='center', va='center', fontsize=9.5, color='#333333',
                linespacing=1.2)
    if tag:
        ax.text(x + 1, y + h - 1.0, tag, fontsize=7.5, fontweight='bold', color=color, va='center')


def arrow(ax, p, q, color=INK, rad=0.0, lw=1.6):
    ax.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='-|>', color=color, lw=lw,
                connectionstyle=f'arc3,rad={rad}', shrinkA=0, shrinkB=0))


def poly(ax, pts, color=INK, lw=1.6):
    xs, ys = zip(*pts)
    ax.plot(xs[:-1] + (xs[-1],), ys[:-1] + (ys[-1],), color=color, lw=lw, solid_capstyle='butt')
    ax.annotate('', xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle='-|>', color=color, lw=lw, shrinkA=0, shrinkB=0))


def label(ax, x, y, text, size=9.5, color='#333333'):
    ax.text(x, y, text, ha='center', va='center', fontsize=size, color=color, style='italic',
            bbox=dict(fc='white', ec='none', pad=0.8, alpha=0.9))


def leak(ax, x, y, n):
    ax.add_patch(Circle((x, y), 1.55, fc=RED, ec='white', lw=1.5, zorder=5))
    ax.text(x, y - 0.05, str(n), color='white', fontsize=11.5, fontweight='bold', ha='center', va='center', zorder=6)


def save(fig, name):
    fig.savefig(HERE / f'{name}.png', dpi=200, facecolor='white')
    fig.savefig(HERE / f'{name}.svg', facecolor='white')
    plt.close(fig)


def workflow():
    fig, ax = canvas()
    band(ax, 0.5, 33, 117.5, 43.5, CYAN, '#eef6fb', 'PAPER BRANCH')
    box(ax, 3, 34.2, 22, 6.6, 'paper + supplement', None, GREY, '#ececec', size=11.5)
    box(ax, 34, 34.2, 32, 6.6, 'page-by-page review', None, CYAN, '#cfe3f0', tag='MODEL', size=11.5)
    box(ax, 75, 34.2, 22, 6.6, 'paper skill', None, BROWN, record=True, size=11.5)
    arrow(ax, (25, 37.5), (34, 37.5)); arrow(ax, (66, 37.5), (75, 37.5))
    ax.text(100, 37.5, 'reading package,\nreview record', fontsize=9.5, color='#333333', va='center')

    band(ax, 0.5, 0.5, 117.5, 31.5, BLUE, '#f1f2fa', 'CODE BRANCH: SIX GATED STAGES, EVIDENCE CALLED FOR AT EACH')
    r1, r2 = 19.5, 5.5
    box(ax, 3, r1, 20, 8.5, 'code repository', 'tutorials, API, tests', GREY, '#ececec', size=11.5)
    box(ax, 30, r1, 26, 8.5, '1  Select tasks', 'evidence: task inventory', BLUE, '#d9dcf1', 'MODEL')
    box(ax, 63, r1, 26, 8.5, '2  Run upstream', 'evidence: reference results', ORANGE, 'white', 'CODE')
    box(ax, 96, r1, 20.5, 8.5, '3  Write wrappers', 'evidence: source binding', BLUE, '#d9dcf1', 'MODEL', size=11.5)
    for a, b in [(23, 30), (56, 63), (89, 96)]:
        arrow(ax, (a, r1 + 4.2), (b, r1 + 4.2))
    box(ax, 3, r2, 26, 8.5, '4  Fresh verifier', 'may repair, up to 6 tries', GREEN, '#cfeae0', 'MODEL')
    box(ax, 36, r2, 26, 8.5, '5  Mount + run tools', 'evidence: inventory, real calls', ORANGE, 'white', 'CODE')
    box(ax, 69, r2, 24, 8.5, '6  Package ZIP', 'evidence: hash, relocation test', PINK, 'white', 'CODE')
    box(ax, 100, r2, 16.5, 8.5, 'MCP tool\npackage', 'candidate only', BROWN, record=True, size=11.5)
    for a, b in [(29, 36), (62, 69), (93, 100)]:
        arrow(ax, (a, r2 + 4.2), (b, r2 + 4.2))
    poly(ax, [(106, r1), (106, 17), (16, 17), (16, r2 + 8.5)])

    save(fig, 'workflow')


def leakage():
    fig, ax = canvas()
    band(ax, 0.5, 30.5, 84, 43.5, GREY, '#f3f3f3', 'AUTHORS, BEFORE PAPER2AGENT')
    band(ax, 0.5, 16, 84, 29.5, BLUE, '#eef0fa', 'PAPER2AGENT BUILDS THE TOOL', tx=40)
    band(ax, 0.5, 0.5, 84, 15, GREEN, '#eef8f4', 'EVALUATION')
    box(ax, 2, 32, 11, 7.6, 'Data D', None, GREY, '#e6e6e6')
    box(ax, 19, 32, 17, 7.6, 'Code C', 'used on D', GREY, '#e6e6e6')
    box(ax, 42, 32, 17, 7.6, 'Tutorials T', 'demos run on D', GREY, '#e6e6e6')
    box(ax, 64, 32, 18, 7.6, 'Paper P', 'results on D', GREY, '#e6e6e6')
    for a, b in [(13, 19), (36, 42), (59, 64)]:
        arrow(ax, (a, 35.8), (b, 35.8))
    leak(ax, 16, 35.8, 1)

    box(ax, 2, 18, 15, 8, 'Read', 'C, T, P', BLUE)
    box(ax, 22, 18, 19, 8, 'Run C on D', 'reference R', BLUE)
    box(ax, 46, 18, 17, 8, 'LLM writes', 'wrapper W', BLUE, '#dcdff1')
    box(ax, 67, 18, 16, 8, 'Verifier', 'W vs R, may repair W', BLUE, '#dcdff1')
    arrow(ax, (9.5, 30.5), (9.5, 26.2), GREY)
    ax.text(12, 28.4, 'C, T, P, D public', fontsize=9, color=GREY, va='center')
    for a, b in [(17, 22), (41, 46), (63, 67)]:
        arrow(ax, (a, 22), (b, 22))
    leak(ax, 40.5, 25.4, 2)

    box(ax, 2, 2.5, 22, 9, 'Questions', 'from T (300)\n+ novel (15)', GREEN)
    box(ax, 32, 2.5, 20, 9, 'Score vs', 'baseline agent', GREEN, '#d6efe6')
    box(ax, 62, 2.5, 20, 9, 'Tool package', None, BLUE)
    arrow(ax, (75, 18), (75, 11.7), BLUE)
    arrow(ax, (62, 7), (52, 7)); arrow(ax, (24, 7), (32, 7))
    leak(ax, 23.5, 10.4, 3)

    ax.text(88, 41.8, 'COUPLING POINTS', color=RED, fontsize=12.5, fontweight='bold', va='center')
    items = [(1, 'Selection', 'Results in P were chosen on D. If C was tuned on D, W inherits that.', RED),
             (2, 'Reference = source', 'Tests are the tutorial computation; the verifier may repair W. A pass shows W copies C.', RED),
             (3, 'Same material', 'Questions come from T, the material the tool was built from.', RED),
             ('\u2713', 'What a pass does show', 'W reproduces tested upstream behavior: good evidence of faithful wrapping.', GREEN)]
    y = 37.2
    for n, head, body, col in items:
        ax.add_patch(Circle((89.2, y + 0.3), 1.55, fc=col, ec='white', lw=1.5, zorder=5))
        ax.text(89.2, y + 0.25, str(n), color='white', fontsize=11.5, fontweight='bold', ha='center', va='center', zorder=6)
        ax.text(92, y + 0.6, head, fontsize=12, fontweight='bold', color=INK, va='center')
        ax.text(92, y - 1.2, '\n'.join(textwrap.wrap(body, 34)), fontsize=9.5, color='#222222', va='top',
                linespacing=1.3)
        y -= 9.9
    save(fig, 'leakage')


def fit():
    fig, ax = canvas()
    band(ax, 0.5, 23, 117.5, 43.5, BLUE, '#f1f2fa', 'ACQUISITION, THEN FACTORY STAGES: FLAT DAG FIRST, COMPOSITE LATER')
    y1, h = 26, 11
    box(ax, 3, y1, 24, h, 'Source acquisition CC', 'pin repo, revision, license', BLUE, '#d9dcf1', 'MODEL', size=11.5)
    box(ax, 34, y1, 24, h, 'Task selection CC', 'bind tasks to upstream code', BLUE, '#d9dcf1', 'MODEL', size=11.5)
    box(ax, 65, y1, 24, h, 'Reference run CC', 'upstream results, recorded', ORANGE, 'white', 'CODE', size=11.5)
    box(ax, 93, y1, 23.5, h, 'Wrapper builder CC', 'never sees held-out tests', BLUE, '#d9dcf1', 'MODEL', size=11.5)
    for a, b, t in [(27, 34, 'pinned\nsource'), (58, 65, ''), (89, 93, '')]:
        arrow(ax, (a, y1 + h / 2), (b, y1 + h / 2))
    label(ax, 30.5, y1 + h + 1.3, 'pinned source', 9); label(ax, 91, y1 + h + 1.3, 'R', 9)
    ax.text(3, 24.3, 'trigger: a run found a capability gap', fontsize=9.5, color=GREY, style='italic', va='center')

    band(ax, 0.5, 0.5, 117.5, 21.5, PURPLE, '#f6f1f9', 'INDEPENDENT ADMISSION: THE JUDGE SITS OUTSIDE THE BUILDER', tx=32)
    box(ax, 3, 10.5, 25, 7.5, 'Candidate package', 'not admitted, no run permission', BROWN, record=True, size=11.5)
    box(ax, 3, 1.5, 25, 7, 'Evaluator', 'hidden tests, written first', GREEN, '#cfeae0', 'MODEL', size=11.5)
    box(ax, 47, 3.5, 34, 11, 'Admission gate', 'FIXED BEFORE GENERATION\nscoped pass, fail or skipped', PURPLE, 'white', 'CODE')
    box(ax, 94, 5.5, 22.5, 7, 'CC library', 'versioned, standing recorded', BROWN, record=True, size=11.5)
    poly(ax, [(104.7, y1), (104.7, 22.4), (15.5, 22.4), (15.5, 18)], INK)
    arrow(ax, (28, 14.2), (47, 10.5)); arrow(ax, (28, 5), (47, 7.5))
    arrow(ax, (81, 9), (94, 9))
    label(ax, 37, 13.4, 'submitted'); label(ax, 37, 4.2, 'held-out tests'); label(ax, 87.5, 11.6, 'admitted')
    ax.text(116.5, 1.4, 'Proposed: nothing here is built or measured yet', ha='right', va='center',
            fontsize=9.5, color=GREY, style='italic')
    save(fig, 'fit')


def capsules():
    fig, ax = canvas()
    band(ax, 0.5, 0.5, 52, 43.5, BLUE, '#f1f2fa', 'FACTORY: ONE BOUNDED AGENT CAPSULE')
    box(ax, 2.5, 30, 47, 9, 'Inputs', 'pinned snapshot from a separate acquisition\ncapsule, requested operations, limits', GREY, '#ececec', size=11.5)
    ax.add_patch(FancyBboxPatch((2.5, 17.5), 47, 9, boxstyle='round,pad=0,rounding_size=1', fc='white', ec=BLUE, lw=1.4, ls='--'))
    ax.text(26, 23.6, 'Stages inside', ha='center', va='center', fontsize=11.5, fontweight='bold')
    ax.text(26, 20.4, 'select, reference run, wrap, test, package\n(each a reusable CC only where reuse pays)', ha='center', va='center', fontsize=9.3, color='#333333', linespacing=1.25)
    box(ax, 2.5, 5.5, 47, 9, 'Outputs', 'candidate package (for example MCP tools),\nsource and environment records, test results', BROWN, record=True, size=11.5)
    arrow(ax, (26, 30), (26, 26.7)); arrow(ax, (26, 17.5), (26, 14.7))

    band(ax, 56, 0.5, 117.5, 43.5, PURPLE, '#f6f1f9', 'GENERATED TOOLS: CANDIDATE CAPSULES')
    for i, name in enumerate(['score_variant', 'run_clustering', 'plot_results']):
        box(ax, 58, 31.5 - i * 9.5, 24, 7.5, name, 'tool CC, candidate', BROWN, record=True, size=11)
    ax.text(70, 3.5, 'illustrative names', ha='center', fontsize=9, color=GREY, style='italic')
    ax.text(101, 4.2, 'one operation or a coherent set', ha='center', fontsize=9, color=GREY, style='italic')
    ax.add_patch(FancyBboxPatch((86, 8), 30, 30, boxstyle='round,pad=0,rounding_size=1', fc='white', ec=PURPLE, lw=1.6))
    ax.text(101, 35.2, 'Each capsule needs', ha='center', va='center', fontsize=11.5, fontweight='bold')
    for i, line in enumerate(['inputs and outputs', 'dependencies, environment', 'permissions, limits',
                              'source provenance', 'verification scope', 'admission status']):
        ax.text(89, 31 - i * 3.9, '\u2022 ' + line, fontsize=10.5, va='center')
    ax.plot([49.5, 54, 54], [10, 10, 35.25], color=BROWN, lw=1.6, solid_capstyle='butt')
    for yy in (35.25, 25.75, 16.25):
        arrow(ax, (54, yy), (58, yy), BROWN)
    label(ax, 52, 6.6, 'adapted', 9)
    save(fig, 'capsules')


def example():
    fig, ax = canvas()
    box(ax, 2, 26, 24, 10, 'Research notebook', 'clusters a fixed\nexample dataset', GREY, '#ececec', size=11.5)
    box(ax, 33, 26, 27, 10, 'Factory', 'prepare environment, extract\noperation, test, package', BLUE, '#d9dcf1', 'MODEL', size=12)
    ax.add_patch(FancyBboxPatch((67, 20), 28, 20, boxstyle='round,pad=0,rounding_size=1', fc='white', ec=PURPLE, lw=1.8))
    ax.text(81, 37.2, 'Candidate tool capsule', ha='center', va='center', fontsize=11.5, fontweight='bold')
    for i, line in enumerate(['in: dataset artifact, parameters', 'out: cluster labels, plots,', '     run record', 'needs: declared environment,', '     execution limits']):
        ax.text(68.5, 33.6 - i * 2.6, line, fontsize=9.3, va='center')
    box(ax, 102, 26, 14.5, 10, 'Admission', 'independent\ngate', GREEN, '#d6efe6', size=11.5)
    arrow(ax, (26, 31), (33, 31)); arrow(ax, (60, 31), (67, 31)); arrow(ax, (95, 31), (102, 31))
    label(ax, 29.5, 38.4, 'pinned source', 9); label(ax, 63.5, 42, 'adapted to the capsule contract', 9)
    ax.text(109, 22.5, 'then an authorized\nagent may invoke it', ha='center', va='center', fontsize=9.3, color='#333333')
    for x0, x1, head, body, cx in [(2, 58, 'Factory call', 'Prepare a candidate clustering capability from this authorized source snapshot.', 46.5),
                                   (62, 116, 'Product call', 'Run the admitted clustering capability on this dataset.', 81)]:
        ax.add_patch(FancyBboxPatch((x0, 4), x1 - x0, 11, boxstyle='round,pad=0,rounding_size=1', fc='#f6f6f6', ec=GREY, lw=1.2))
        ax.text(x0 + 2, 12.2, head, fontsize=11.5, fontweight='bold', va='center')
        ax.text(x0 + 2, 8.2, '\n'.join(textwrap.wrap(body, 62)), fontsize=10.5, va='center', color='#222222', linespacing=1.3)
    ax.plot([46.5, 46.5], [15, 26], color=GREY, lw=1.2, ls=':')
    ax.plot([81, 81], [15, 20], color=GREY, lw=1.2, ls=':')
    ax.text(116.5, 1.4, 'Illustrative mapping, not an implemented integration', ha='right', va='center', fontsize=9.5, color=GREY, style='italic')
    save(fig, 'example')


if __name__ == '__main__':
    workflow(); leakage(); fit(); capsules(); example()
