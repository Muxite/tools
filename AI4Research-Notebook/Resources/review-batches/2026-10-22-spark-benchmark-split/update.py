from pathlib import Path
import hashlib, json

vault = Path(__file__).resolve().parents[3]
batch = Path(__file__).resolve().parent
capture = 'Sources/Prompts/2026-10-22-spark-benchmark-setup-approved-plan.txt'
def digest(data): return hashlib.sha256(data).hexdigest()
names = ['Resources/Coder Prompts/README.md', 'Resources/Coder Prompts/benchmark-runner.md', 'Workstreams/Lab Infrastructure.md', 'Designs/Agent Reading and Freshness.md', 'Designs/Design Library.md', 'Designs/Spark Shared Services and Storage.md', 'Designs/Lab Capsule and Factory Design Plan.md', 'Sources/Implementation Intent.md', 'Sources/Prompt Register.md', 'Activities/Activity Register.md', 'Sources/capture-manifest.json', 'Home.md']
receipts = []
for name in names:
    data = (vault/name).read_bytes()
    dst = batch/'before'/(name.replace('/', '__')+'.snapshot')
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open('xb') as f: f.write(data)
    assert digest(dst.read_bytes()) == digest(data)
    receipts.append({'path':name, 'snapshot':str(dst.relative_to(vault)), 'sha256':digest(data)})
(batch/'before-receipt.json').write_text(json.dumps(receipts, indent=2)+'\n', encoding='utf-8')

request = '''PLEASE IMPLEMENT THIS PLAN:
# Split out a practical Spark setup prompt

## Summary

Create **`spark-benchmark-setup.md`** alongside `benchmark-runner.md`. Its purpose is to get the existing system running on the DGX Spark quickly and reliably, making benchmark campaigns easier to run.

Keep the longer-term VM, capsule-container and factory architecture in the existing infrastructure designs. **Spark setup is an optional deployment path, not a requirement for benchmarking.**

## Prompt contents

Start with short **For human** bullets explaining what it sets up, what it provides and what requires human access. Follow with plain technical instructions for the coding agent:

- Inspect the actual Spark, available storage, architecture, Docker/Compose installation, existing services and current branch before changing anything. Preserve the working NVIDIA environment and unrelated workloads.
- Deploy directly on the host using the existing Docker/Compose structure. Do not introduce VMs, a registry, a capacity-controller service or a capsule factory for this delivery.
- Prepare isolated AI4R and baseline containers, independent writable state, correct host-resolved mounts and collision-free networking. Reuse immutable images and dependency layers where practical.
- Use the existing model connection first. Add shared local inference only when a selected benchmark requires it; keep model weights outside application images and avoid copies per target.
- Apply practical storage controls: inventory actual usage, retain 20% filesystem headroom for new growth, bound build caches and logs, and clean only resources owned by this deployment. Do not perform global pruning or delete existing models/results.
- Provide repeatable setup, readiness, start, stop and owned-resource cleanup commands. A second setup run must preserve state and avoid duplicate resources.
- Document the actual supported Codex authentication step. Complete independent setup work while waiting for human login or remote access.

## Boundaries and handoff

`benchmark-runner.md` continues to own case loading, parallel scheduling, branch comparison, results and exports. The new prompt owns host preparation and deployment integration.

The setup agent must reuse the runner’s configuration contract. Its handoff records target endpoints, image/commit identities, architecture, owned storage locations, credential references, resource limits and readiness results. Secrets stay outside reports.

If the runner is unfinished, deploy and verify the available app components, then report the remaining integration work. Do not build a second runner or claim benchmark readiness. Fix deployment-specific problems within this task; record broader application changes under the existing implementation workflow.

Update the prompt index and infrastructure reading routes to explain this split. Add a brief optional link from the benchmark prompt without making Spark setup a dependency.

## Validation and completion

The prompt will require evidence that:

- The app starts on the actual Spark and passes its supported readiness checks.
- Separate targets have working API connectivity and isolated writable state.
- Container input/output mounts work without changing sentinel user files.
- Stop/start and repeated setup preserve state and avoid collisions.
- Storage reporting and owned cleanup work without deleting retained evidence.
- When the runner and credentials are available, a small campaign produces real, exportable results. Otherwise, that final check remains explicitly incomplete.

During the document revision, preserve the previous notes, check for contradictory prerequisites, validate links and metadata, and keep source inspection distinct from actual Spark testing.
'''
with (vault/capture).open('xb') as f: f.write(request.encode('utf-8'))
manifest = json.loads((vault/'Sources/capture-manifest.json').read_text(encoding='utf-8-sig'))
manifest.append({'path':capture, 'sha256':digest(request.encode('utf-8')), 'capture_method':'exact visible approved-plan user message as UTF-8 LF; terminal newline included; not a transport export', 'captured_date':'2026-10-22'})
(vault/'Sources/capture-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def update(name, transform):
    p = vault/name
    s = p.read_text(encoding='utf-8')
    s = transform(s)
    s = s.replace('last_reviewed: 2026-10-20', 'last_reviewed: 2026-10-22', 1).replace('last_reviewed: 2026-10-21', 'last_reviewed: 2026-10-22', 1)
    p.write_text(s, encoding='utf-8')

update(names[0], lambda s: s.replace('next_action: Send benchmark-runner to its implementing agent; human reviews task results', 'next_action: Choose benchmark-runner for execution tooling or spark-benchmark-setup for optional Spark deployment').replace('\nSee [[Workstreams/M1', '\n| [[Resources/Coder Prompts/spark-benchmark-setup\\|spark-benchmark-setup]] | Optional direct-host Spark setup using existing containers, bounded storage and verified connectivity | Approved setup handoff; not a benchmark prerequisite or VM/factory implementation |\n\nSee [[Workstreams/M1', 1))
update(names[1], lambda s: s.replace('## For AI: implementation objective and existing design', 'Optional Spark deployment: [[Resources/Coder Prompts/spark-benchmark-setup|spark-benchmark-setup]] prepares the host and connects the existing containers. It is not a prerequisite; this runner must also work on another compatible Docker host.\n\n## For AI: implementation objective and existing design', 1))
update(names[2], lambda s: s.replace('next_action: Draft VM topology and container CC contracts, then complete the local factory design', 'next_action: Use the optional Spark setup prompt for immediate deployment; keep M2 VM/factory work separate') + '\n## Immediate Spark benchmark setup\n\n[[Resources/Coder Prompts/spark-benchmark-setup]] is the practical direct-host deployment handoff for the existing app and benchmark tooling. It uses Docker/Compose, isolated target state and bounded storage. It does not require VM qualification, a factory, a registry or the full M2 capacity controller. Benchmarking remains available on another compatible Docker host through [[Resources/Coder Prompts/benchmark-runner]]. The M2 sections above describe the longer-term architecture, not prerequisites for this setup.\n')
update(names[3], lambda s: s.replace('For the current M1 platform benchmark/CI coder request, use [[Resources/Coder Prompts/benchmark-runner]] and its named design owners. For M2 infrastructure, use [[Designs/Lab Capsule and Factory Design Plan]] then [[Designs/Spark Shared Services and Storage]]. Do not import M2 host/factory changes into the M1 sidecar handoff.', 'For benchmark execution tooling, use [[Resources/Coder Prompts/benchmark-runner]] and its named design owners. For optional immediate Spark deployment, use [[Resources/Coder Prompts/spark-benchmark-setup]]; it works directly on the host without VM/factory prerequisites. For the separate M2 architecture, use [[Designs/Lab Capsule and Factory Design Plan]] then [[Designs/Spark Shared Services and Storage]]. Do not require completion of M2 architecture to deploy the current app or run benchmarks.'))
update(names[4], lambda s: s.replace('## Your new design work', '## Optional Spark deployment prompt\n\n[[Resources/Coder Prompts/spark-benchmark-setup]] sets up the existing app and runner directly on the Spark using Compose. It owns host preparation, storage controls and deployment connectivity. Benchmark scheduling/results remain in [[Resources/Coder Prompts/benchmark-runner]], which can run on another host. M2 VM/factory architecture below remains separate.\n\n## Your new design work', 1))
for name in names[5:7]:
    update(name, lambda s: s.replace('\n## ', '\nFor immediate deployment of the existing app, use [[Resources/Coder Prompts/spark-benchmark-setup]]. That optional direct-host setup does not require the VM, registry, factory or full capacity-controller services in this M2 design. It applies basic storage controls now; the architecture below remains the longer-term work. Benchmarking can run independently on another compatible Docker host.\n\n## ', 1))
update(names[7], lambda s: s + '\n## Optional Spark deployment split\n\nThe [[Sources/Prompts/2026-10-22-spark-benchmark-setup-approved-plan.txt|approved plan]] creates [[Resources/Coder Prompts/spark-benchmark-setup]] for immediate direct-host Docker/Compose deployment. [[Resources/Coder Prompts/benchmark-runner]] retains case scheduling, comparisons and exports. Local inference is added only when needed. Practical storage headroom and owned cleanup apply now; M2 VMs, factories, registry and full capacity-controller services remain separate. This is a prompt/documentation delivery, not evidence that the Spark was accessed or qualified.\n')
update(names[8], lambda s: s + '\n- [[Sources/Prompts/2026-10-22-spark-benchmark-setup-approved-plan.txt|Approved Spark setup prompt split]] — immediate direct-host deployment is optional for benchmarking; local inference only when needed.\n')
update(names[9], lambda s: s + '\n- [[Activities/2026-10-22 Spark Benchmark Setup Prompt|Spark benchmark setup prompt]] — split immediate optional deployment from M2 architecture; updated coder and infrastructure routes; no Spark deployment performed.\n')
update('Home.md', lambda s: s.replace('Qualify Spark capacity and ARM64 CPU guests under the M2 resource policy', 'Use the optional Spark setup prompt now; keep M2 VM qualification separate') + '\n**Optional immediate Spark deployment:** [[Resources/Coder Prompts/spark-benchmark-setup]] prepares the current containers and bounded host storage. It does not gate [[Resources/Coder Prompts/benchmark-runner]] or require M2 VM/factory work.\n')
print('Captured approved plan; snapshotted 12 notes/manifests; aligned immediate and long-term reading routes.')
