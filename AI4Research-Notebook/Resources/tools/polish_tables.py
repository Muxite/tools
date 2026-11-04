"""Escape wiki-link aliases inside authored Obsidian tables; never touch archive bytes."""
from pathlib import Path
import re

VAULT=Path(__file__).resolve().parents[2]

def table_links(text):
    lines=[]
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith('|'):
            line=re.sub(r'\[\[[^\]]+\]\]',lambda m:re.sub(r'(?<!\\)\|',r'\\|',m.group(0)),line)
        lines.append(line)
    return ''.join(lines)

if __name__=='__main__':
    count=0
    for p in VAULT.rglob('*.md'):
        rel=p.relative_to(VAULT)
        if 'Imported' in rel.parts or '.git' in rel.parts:continue
        before=p.read_text(encoding='utf-8');after=table_links(before)
        if before!=after:
            p.write_text(after,encoding='utf-8');count+=1
    print('Authored table pages updated:',count)
