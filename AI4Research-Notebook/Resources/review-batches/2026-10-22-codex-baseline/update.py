from pathlib import Path
import hashlib, json
v=Path(__file__).resolve().parents[3]
b=Path(__file__).resolve().parent
capture='Sources/Prompts/2026-10-22-codex-packaged-baseline.txt'
names=['Resources/Coder Prompts/benchmark-runner.md','Resources/Coder Prompts/spark-benchmark-setup.md','Sources/capture-manifest.json','Sources/Implementation Intent.md','Sources/Prompt Register.md','Activities/Activity Register.md']
sha=lambda data:hashlib.sha256(data).hexdigest()
receipt=[]
for name in names:
    data=(v/name).read_bytes()
    p=b/'before'/(name.replace('/','__')+'.snapshot')
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(data)
    assert sha(p.read_bytes())==sha(data)
    receipt.append({'path':name,'snapshot':str(p.relative_to(v)),'sha256':sha(data)})
(b/'before-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
request='can we make the benchmark allowed to run against codex, with codex in a package to run the benchmarker. we want to know the diff between ai4research with cpasules and this planning workflow, vs the similar setup but no workflow and just raw openjiuwen but with the codex model replacement, is this possible?\n'
with (v/capture).open('xb') as f:f.write(request.encode())
manifest=json.loads((v/names[2]).read_text(encoding='utf-8'))
manifest.append({'path':capture,'sha256':sha(request.encode()),'capture_method':'exact visible user message as UTF-8 LF; terminal newline included; not a transport export','captured_date':'2026-10-22'})
(v/names[2]).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=v/names[0]
s=p.read_text(encoding='utf-8')
s=s.replace('- **Compares:** Runs AI4R branch A versus branch B, or AI4R versus JiuwenSwarm/OpenJiuwen.', '- **Compares:** Runs AI4R branch A versus branch B, or AI4R with capsules/workflow versus plain JiuwenSwarm/OpenJiuwen using the same Codex backend. Direct Codex is an optional additional target.')
addition='''### Codex-backed baseline and optional direct Codex target

Support the following comparison as a first-class campaign configuration:

| Target | Behavior |
|---|---|
| AI4Research + Codex | Our capsule execution, planning workflow and verification gates, using the selected Codex backend |
| Plain JiuwenSwarm/OpenJiuwen + Codex | The selected native agent runtime with a minimal Codex provider/bridge integration, without AI4Research capsules, static research DAG or AI4Research verification pipeline |
| Direct Codex, optional | A packaged Codex CLI/app-server agent in its own container, without either application's orchestration |

The required comparison is the first two targets. Allow a separately selected direct-Codex adapter; do not make it a prerequisite for that comparison. Native agent reasoning, planning and ordinary tool use remain allowed in the plain baseline. "No workflow" means no imposed AI4Research workflow, not disabling the baseline's normal agent capabilities.

Package the Codex client/runtime and adapter with pinned dependencies in the appropriate target image or an explicitly scoped bridge service. Codex model execution is provided by its authenticated backend; bundling the client does not package model weights or make inference local. The benchmark runner remains the coordinator and collector, not a Codex agent performing or judging the cases. Keep target containers, case sessions, writable state and credentials isolated, while reusing the same pinned bridge implementation where practical. Use a documented headless integration; OpenAI documents CLI, SDK and app-server options in [Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform). Verify the interface supported by the actual pinned version.

Use upstream JiuwenSwarm/OpenJiuwen plus the minimum versioned Codex integration needed to execute the same tasks. If upstream lacks that provider, build the adapter in our branch and record the upstream commit, patch/harness hash and effective settings separately. Label it **upstream with Codex integration**, not unmodified upstream. Do not copy AI4Research's capsules, planner, research instructions or gate policy into this baseline. Do not substitute direct Codex and label it OpenJiuwen.

The inspected `ai4r_M1` source at `7cc7c2d843bc4ac22a7e9e731dc0efb2e09439e3` includes `interface_codex.py` and `codex_subscription/transport.py`, but that ordinary-chat slice rejects tools/attachments/team requests and rejects server requests for host tools/approvals. It is a reuse lead, not proof of a tool-capable baseline. Reinspect the current implementation and implement the missing native tool/result/approval integration needed by selected cases. An agentic task must not silently fall back to a text-only response. Keep the existing chat profile intact where other callers rely on it.

Give each target the same case brief, permitted source snapshots, external tool capabilities and effect permissions, with matched model identifier, reasoning effort where supported, time/resource/token budgets and repeats. Record actual Codex/runtime/provider versions, effective model identity, target instructions and any unmatched settings, including unavailable usage metrics. Keep AI4Research's real verification cost in its budget. Start with fresh case sessions and do not share solution history or warm-start one target with another's output. Parallel requests may share account limits; record rate-limit waits/contention and do not claim their wall times measure isolated speed.

This primary comparison measures the whole AI4Research system against the native agent setup. It does not isolate the individual contribution of capsules versus planning versus verification; that requires separately specified ablations. Export observed outputs, tool traces where exposed, time and usage for human review, with no automatic correctness scores or winner. Verify both required targets can complete a representative tool-backed task, export its real artifacts, cancel and reconcile without cross-target effects before claiming the comparison works.

'''
assert '### 5. Codex readiness' in s
s=s.replace('### 5. Codex readiness',addition+'### 5. Codex readiness',1)
p.write_text(s,encoding='utf-8')
p=v/names[1]
s=p.read_text(encoding='utf-8')
needle='## 3. Keep storage and model use bounded'
add='''For Codex-backed campaigns, follow the companion prompt's target definitions: AI4Research with capsules/workflow versus plain JiuwenSwarm/OpenJiuwen with the same Codex backend. Package the pinned client/bridge in isolated target images or a supported scoped bridge; model weights are not part of that package. Include the minimal baseline provider integration without importing AI4Research's pipeline. Record its patch/harness identity and verify actual tool execution, not just text chat. A direct Codex container is an optional extra target, not a replacement for the OpenJiuwen baseline or a setup prerequisite.

'''
assert needle in s
p.write_text(s.replace(needle,add+needle,1),encoding='utf-8')
extras={
names[3]:'\n## Codex-backed comparison\n\nThe [[Sources/Prompts/2026-10-22-codex-packaged-baseline.txt|latest request]] asks to compare AI4Research capsules/planning against plain JiuwenSwarm/OpenJiuwen with Codex replacing its model backend. [[Resources/Coder Prompts/benchmark-runner]] now makes that pair explicit and permits direct Codex as an optional third target. Packaging covers the client/harness, not local model weights. The existing inspected chat adapter is text-only, so real tool integration needs implementation and validation. A minimally patched upstream baseline must be labeled with its integration identity. This is a whole-system comparison, not a separate attribution of capsule and planning gains. [[Resources/Coder Prompts/spark-benchmark-setup]] follows the same definitions. No runtime comparison was performed.\n',
names[4]:'\n- [[Sources/Prompts/2026-10-22-codex-packaged-baseline.txt|Codex-backed native agent baseline and packaged Codex target]] — same backend for AI4Research and the plain baseline; direct Codex is optional.\n',
names[5]:'\n- 2026-10-22: Updated [[Resources/Coder Prompts/benchmark-runner]] and [[Resources/Coder Prompts/spark-benchmark-setup]] for matched Codex-backed targets, versioned baseline integration and optional direct Codex; inspected existing text-only adapter and official headless integration guidance. No software implementation or benchmark execution.\n'
}
for name,extra in extras.items():
    p=v/name
    p.write_text(p.read_text(encoding='utf-8')+extra,encoding='utf-8')
print('Updated benchmark and deployment prompts; preserved exact request and pre-edit bytes.')
