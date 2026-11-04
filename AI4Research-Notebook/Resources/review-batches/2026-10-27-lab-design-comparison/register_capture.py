from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent
V=B.parents[2]
rel='Sources/Prompts/2026-10-27-implement-lab-comparison.txt'
p=V/rel
p.write_bytes(p.read_text('utf-8').encode('utf-8'))
manifest=V/'Sources/capture-manifest.json'
raw=manifest.read_bytes()
backup=B/'before'/'capture-manifest.json.snapshot'
backup.parent.mkdir(exist_ok=True)
assert not backup.exists()
backup.write_bytes(raw)
data=json.loads(raw)
assert not any(r['path']==rel for r in data)
data.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'capture_method':'exact visible user message, UTF-8 LF; not a transport export','captured_date':'2026-10-27'})
manifest.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
register=V/'Sources/Prompt Register.md'
raw=register.read_bytes()
(B/'before'/'Prompt Register.md.snapshot').write_bytes(raw)
register.write_bytes(raw+b'\n\n- [[Sources/Prompts/2026-10-27-implement-lab-comparison.txt]]: implement checkpoint 1 only; [[Designs/Lab Design Comparison]] contains the comparison, diagrams and source limits.\n')
print('Exact prompt registered. Checkpoint scope remains comparison only.')
