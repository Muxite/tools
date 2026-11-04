"""Read-only text layout budget; creates no PDF and assumes frontmatter is hidden."""
from pathlib import Path
import hashlib
import html
import json
import re

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle

VAULT = Path(__file__).resolve().parents[3]
SOURCE = VAULT / 'Documents/AI4Research Role and Technical Contributions.md'
body = SOURCE.read_text(encoding='utf-8').split('---', 2)[2].strip()
sections = body.split('<div style="page-break-after: always;"></div>')
styles = {
    'body': ParagraphStyle('body', fontName='Helvetica', fontSize=11, leading=14),
    'h1': ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=17, leading=21),
    'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=14, leading=18),
    'h3': ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=11.5, leading=15),
}


def inline(text):
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html.escape(text))


def measure(part, width):
    lines = part.strip().splitlines()
    height = 0
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[: -]+', x) for x in cells):
                    rows.append([Paragraph(inline(x), styles['body']) for x in cells])
                i += 1
            table = Table(rows, colWidths=[105, width - 105])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            height += table.wrap(width, 10000)[1] + 8
            continue
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            style = styles['h' + str(min(level, 3))]
            height += Paragraph(inline(line.lstrip('# ').strip()), style).wrap(width, 10000)[1] + 12
            i += 1
            continue
        if line.startswith('- '):
            height += Paragraph(inline(line[2:]), styles['body']).wrap(width - 12, 10000)[1] + 5
            i += 1
            continue
        parts = [line.lstrip('> ')]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#', '- ', '|', '>')):
            parts.append(lines[i].strip())
            i += 1
        height += Paragraph(inline(' '.join(parts)), styles['body']).wrap(width, 10000)[1] + 8
    return height


results = []
for name, size in [('A4', A4), ('Letter', letter)]:
    width, available = size[0] - 36 * mm, size[1] - 36 * mm
    results.append({
        'paper': name,
        'sections': [
            {'section': n, 'height_points': round(measure(part, width), 1),
             'available_points': round(available, 1), 'fits': measure(part, width) <= available}
            for n, part in enumerate(sections, 1)
        ],
    })
result = {
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'words': len(re.findall(r'\S+', body)),
    'explicit_sections': len(sections),
    'assumptions': '11pt body, 14pt leading, 18mm margins, hidden YAML frontmatter; three explicit print breaks. Text/table height probe only, no PDF rendering; renderer settings can change pagination.',
    'results': results,
}
Path(__file__).with_name('layout-check.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
assert len(sections) == 4
assert all(s['fits'] for paper in results for s in paper['sections'])
