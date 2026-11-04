from pathlib import Path
import hashlib,json,subprocess
v=Path(__file__).resolve().parents[3];b=Path(__file__).resolve().parent
capture='Sources/Prompts/2026-10-22-jiuwenswarm-policy-reuse.txt'
names=['Resources/Coder Prompts/benchmark-runner.md','Sources/Implementation Intent.md','Sources/Prompt Register.md','Activities/Activity Register.md','Sources/capture-manifest.json']
sha=lambda d:hashlib.sha256(d).hexdigest()
rows=[]
for name in names:
    data=(v/name).read_bytes();dst=b/'before'/(name.replace('/','__')+'.snapshot')
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb') as f:f.write(data)
    assert sha(dst.read_bytes())==sha(data)
    rows.append({'path':name,'snapshot':str(dst.relative_to(v)),'sha256':sha(data)})
(b/'before-receipt.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
request='look how it links to jiuwenswarma nd if theres reusable polciies or nah\n'
with (v/capture).open('xb') as f:f.write(request.encode())
manifest=json.loads((v/names[-1]).read_text(encoding='utf-8'))
manifest.append({'path':capture,'sha256':sha(request.encode()),'capture_method':'exact visible user message as UTF-8 LF; terminal newline included; not a transport export','captured_date':'2026-10-22'})
(v/names[-1]).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=v/names[0];s=p.read_text(encoding='utf-8')
needle='### Required deployment: two images and two containers'
block='''### Reuse JiuwenSwarm/AI4R policies at their existing boundaries

AI4R extends the JiuwenSwarm application; the runner is a separate client of that app, not a second agent runtime. Reuse code from the actual branch and verify its dependencies before selecting image contents. The following modules were inspected at the commit above; they are reuse leads, not proof of the finished deployment:

| Existing module or configuration | Reuse and boundary |
|---|---|
| `research_sidecar/client.py` | Authenticated HTTP client and record validation. Extend the supported interface instead of importing app internals. |
| `research/contracts/types.py`, `research/shell_auth.py` | App-side principal, workspace, operation and audience enforcement. Issue only scoped client access to the runner. |
| `research_sidecar/ledger.py`, `reconcile.py` | Durable action identity and reconcile-before-resubmit behavior. Extend to worker leases/concurrency without claiming the existing ledger is a complete scheduler. |
| `research_sidecar/evidence.py` | Safe relative paths, write-once files, hashes and audience-checked archive extraction. Preserve those checks when adding streamed collection and durable acknowledgement. |
| `research_sidecar/cleanup.py` | Ownership/disposable-resource checks and retained data volumes. Update allowed project naming coherently; current code accepts specific QA/verification prefixes. |
| JiuwenSwarm permission rails, `runtime/permission_catalog.py`, `file_delivery_policy.py` | Keep tool/effect decisions and channel delivery policy in the app. The permission catalog is a read-only view, not an authorization grant; channel file delivery is not a replacement for authenticated artifact export. |
| Existing sidecar Dockerfile/Compose settings | Reuse minimal dependencies, non-root execution, read-only root filesystem, dropped capabilities, private networking and explicit bind sources. |

Do not copy the app's agent tools, approval machinery or complete dependency graph into `benchmark-runner`. Keep policy enforcement in the app and consume its authorized outputs. Record unresolved permissions as pending/blocked through the interface; neither an approved campaign nor a client token grants unrestricted agent tool access. Shared contract and file-integrity utilities may be packaged neutrally where required.

Two inspected defaults must change: the current app build packages the broad JiuwenSwarm wheel, which includes sidecar modules; exclude runner code from the app image/wheel and verify installed contents. The current sidecar Compose service is named `sidecar` and requires score/report mounts; expose the requested `benchmark-runner` service/image role and remove those mounts as requirements for this human-reviewed mode. Keep unrelated legacy modes intact. Existing archive helpers buffer bounded bundles, so large-file streaming, collection retry/confirmation and retention need real implementation rather than being claimed as already complete. Existing record-export split labeling does not define or generate the externally supplied campaign tests.

'''
assert needle in s;s=s.replace(needle,block+needle,1);p.write_text(s,encoding='utf-8')
for name,extra in {
names[1]:'\n## JiuwenSwarm reuse review\n\n[[Resources/Coder Prompts/benchmark-runner]] now identifies reusable app authentication/permission enforcement, sidecar client/ledger/evidence/cleanup and container settings. App policies stay in the app; the sidecar uses scoped client operations. Reviewed source is pinned in `Resources/review-batches/2026-10-22-runner-policy-reuse/source-receipt.json`. App-wheel inclusion of runner modules, required score mounts and bounded in-memory export helpers still need adaptation. These are source findings, not deployment results.\n',
names[2]:'\n- [[Sources/Prompts/2026-10-22-jiuwenswarm-policy-reuse.txt|Review JiuwenSwarm links and reusable policies]] — ownership and code reuse mapped in the runner prompt.\n',
names[3]:'\n- 2026-10-22: Reviewed pinned JiuwenSwarm/AI4R client, policies, evidence and image packaging; added boundary-specific reuse guidance to [[Resources/Coder Prompts/benchmark-runner]]. No runtime checks performed.\n'
}.items():
    p=v/name;p.write_text(p.read_text(encoding='utf-8')+extra,encoding='utf-8')
repo=v.parent/'AI4Research-Development/jiuwenswarm-m1-prompt-review-20261022.git'
paths=['pyproject.toml','deploy/m1/Dockerfile.app','deploy/m1/Dockerfile.app.dockerignore','deploy/m1/Dockerfile.sidecar','deploy/m1/compose.sidecar.yaml','jiuwenswarm/research_sidecar/client.py','jiuwenswarm/research_sidecar/ledger.py','jiuwenswarm/research_sidecar/reconcile.py','jiuwenswarm/research_sidecar/evidence.py','jiuwenswarm/research_sidecar/cleanup.py','jiuwenswarm/research/shell_auth.py','jiuwenswarm/research/contracts/types.py','jiuwenswarm/research_records/export.py','jiuwenswarm/agents/harness/common/tools/file_delivery_policy.py']
receipt={'repository':'https://github.com/Stellven/jiuwenswarm.git','branch':'ai4r_M1','commit':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),'review_date':'2026-10-22','scope':'bounded source review; no current remote-head check, upstream audit or runtime validation','files':[]}
for path in paths:
    d=subprocess.check_output(['git','-C',str(repo),'show','HEAD:'+path]);receipt['files'].append({'path':path,'sha256':sha(d)})
(b/'source-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('PASS: exact request and original snapshots preserved; policy reuse guidance added with pinned source hashes.')
