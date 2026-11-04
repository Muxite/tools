from pathlib import Path
import concurrent.futures, hashlib, json, re, subprocess

v = Path(__file__).resolve().parents[3]
b = Path(__file__).resolve().parent
cli = Path('C:/Users/m50066326/AppData/Local/npm-cache/_npx/fa58c8ce4c502b5d/node_modules/@mermaid-js/mermaid-cli/src/cli.js')
policy = json.loads((b / 'capacity-policy.example.json').read_text())
assert abs(sum(policy['disk_pool_fraction'].values()) - 1) < 1e-9
assert sum(policy['memory_pool_fraction'].values()) == 1
assert policy['active_cpu_labs'] * policy['per_lab_virtual_disk_fraction'] < policy['disk_pool_fraction']['all_vm_state']
receipts = json.loads((b / 'pre-edit-receipts.json').read_text())
for r in receipts:
    assert hashlib.sha256((v / r['snapshot']).read_bytes()).hexdigest() == r['sha256']
items = []
for name, slug in [('Spark Shared Services and Storage.md', 'spark-shared-services'), ('Lab Capsule and Factory Design Plan.md', 'spark-m2-overview'), ('VM Lab Infrastructure Design.md', 'spark-vm-runtime')]:
    p = v / 'Designs' / name
    t = p.read_text(encoding='utf-8')
    assert t.count('```') % 2 == 0, name
    blocks = re.findall(r'```mermaid\n(.*?)```', t, re.S)
    assert len(blocks) == 1, name
    src = b / (slug + '.mmd')
    src.write_text(blocks[0], encoding='utf-8')
    items.append(dict(source=p.relative_to(v).as_posix(), source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(), mermaid_sha256=hashlib.sha256(blocks[0].encode()).hexdigest(), mmd=str(src), png=str(b / (slug + '.png'))))

def render(item):
    r = subprocess.run(['node', str(cli), '-i', item['mmd'], '-o', item['png'], '-b', 'white', '--size', '1800'], capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise RuntimeError(r.stdout + r.stderr)
    item['png_sha256'] = hashlib.sha256(Path(item['png']).read_bytes()).hexdigest()
    return item

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    rendered = list(pool.map(render, items))
(b / 'diagram-manifest.json').write_text(json.dumps(rendered, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(policy_arithmetic='PASS', snapshot_hashes_verified=len(receipts), diagrams_rendered=len(rendered), runtime='NOT_RUN')))
