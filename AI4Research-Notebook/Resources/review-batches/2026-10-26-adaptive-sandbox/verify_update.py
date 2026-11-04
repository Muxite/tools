from pathlib import Path
import hashlib
import json

B=Path(__file__).resolve().parent
V=B.parents[2]
def sha(x): return hashlib.sha256(x).hexdigest()

# Capture text with the documented LF encoding.
p=V/'Sources/Prompts/2026-10-26-adaptive-sandbox-replacement.txt'
p.write_bytes(p.read_text('utf-8').encode('utf-8'))
manifest=json.loads((V/'Sources/capture-manifest.json').read_text('utf-8'))
expected=next(r['sha256'] for r in manifest if r['path']==str(p.relative_to(V)).replace('\\','/'))
assert sha(p.read_bytes())==expected

# The same handoff index was edited twice. Restore the first exact before-state
# only when its bytes match the hash captured before either edit.
rp=B/'receipt.json'
receipt=json.loads(rp.read_text('utf-8'))
first={}
for row in receipt['before']:
    first.setdefault(row['path'],row)
for rel,row in first.items():
    target=V/row['snapshot']
    raw=target.read_bytes()
    if sha(raw)!=row['before_sha256']:
        assert rel=='Resources/Handoffs/m2-labs/README.md'
        t=raw.decode('utf-8').replace('status: historical-handoff-requires-reconciliation','status: ready-for-bounded-specification')
        candidates=[t.encode(),t.replace('\r\n','\n').replace('\n','\r\n').encode()]
        matches=[b for b in candidates if sha(b)==row['before_sha256']]
        assert matches, 'No exact matching original bytes; keep mismatch visible'
        target.write_bytes(matches[0])
    assert sha(target.read_bytes())==row['before_sha256']
receipt['before']=list(first.values())
rp.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')

dm=json.loads((V/'Designs/Sandbox Lab Diagrams/manifest.json').read_text('utf-8'))
for row in dm['diagrams']:
    for ext,key in [('mmd','source_sha256'),('svg','svg_sha256'),('png','png_sha256')]:
        assert sha((V/'Designs/Sandbox Lab Diagrams'/f"{row['stem']}.{ext}").read_bytes())==row[key]
print('Prompt bytes, exact before-state snapshots and all seven diagram projections verified.')
