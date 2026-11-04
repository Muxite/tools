"""Render only the seven M2 sandbox diagrams; never prune unrelated artifacts."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import subprocess

VAULT = Path(__file__).resolve().parents[3]
OUT = VAULT / 'Designs/Sandbox Lab Diagrams'
CLI = Path('C:/Users/m50066326/AppData/Local/npm-cache/_npx/fa58c8ce4c502b5d/node_modules/@mermaid-js/mermaid-cli/src/cli.js')

DIAGRAMS = [
('01-lab-context', 'Lab context and ownership', '''flowchart TB
    HUMAN["Human direction<br/>Brief and budgets"]
    MASTER["Tested master AI4R<br/>and shared CC library"]
    subgraph LABS["Independent persistent projects"]
        A["Workload lab<br/>AI4R, CCs, profiler and state"]
        B["Robotics lab<br/>AI4R, CCs, application and state"]
        C["Other research labs<br/>Own goals, resources and state"]
    end
    INFRA["Lab infrastructure<br/>Isolation, resources and recovery"]
    CENTRAL["Separate central qualification<br/>Selected packages, data and findings"]
    HUMAN --> A
    HUMAN --> B
    MASTER -->|"seed selected versions"| A
    MASTER --> B
    MASTER --> C
    INFRA -->|"manage and preserve"| LABS
    A -.->|"candidate exports"| CENTRAL
    B -.-> CENTRAL
    C -.-> CENTRAL
    CENTRAL -->|"explicit adoption"| NEXT["Next tested master release"]
    class HUMAN,INFRA control
    class MASTER,CENTRAL,NEXT qualify
    class A,B,C work
'''),
('02-runtime-boundary', 'Runtime and infrastructure boundary', '''flowchart TB
    subgraph HOST["Permitted Linux environment or provisioned lab VM"]
        POLICY["Controller policy and ledger<br/>Outside mutable research source"]
        CTRL["Lab controller and broker<br/>Typed API, limits and reconciliation"]
        ENGINE["Docker Engine<br/>Controller access only"]
        subgraph LAB["Lab runtime scope"]
            APP["Persistent AI4R runtime<br/>Planner and CC factory module"]
            JOB["Bounded CC operation jobs<br/>Scoped inputs, outputs and deadline"]
            SERVICE["Managed application service<br/>Optional persistent lifetime"]
        end
        STORE["Persistent lab storage<br/>Separate project and service data"]
        POLICY --> CTRL
        APP -->|"authorized requests"| CTRL
        CTRL --> ENGINE
        ENGINE -->|"run persistent app"| APP
        ENGINE -->|"start and supervise"| JOB
        ENGINE --> SERVICE
        JOB -->|"scoped application API"| SERVICE
        APP --> STORE
        SERVICE --> STORE
        JOB -->|"validated output import"| CTRL
        CTRL --> STORE
    end
    BUILD["Optional workstation or CI builder"] -.->|"verified artifacts"| CTRL
    class POLICY,CTRL,ENGINE control
    class APP,JOB,SERVICE work
    class STORE data
    class BUILD external
'''),
('03-cc-package', 'CC package and operation bindings', '''flowchart TB
    subgraph PKG["Immutable CC package version"]
        DECL["Package manifest<br/>Lineage and compatibility set"]
        OPS["Named operations<br/>Purpose, ports, effects and preconditions"]
        BODY["Implementation artifacts<br/>Adapters, images or member packages"]
        PROFILE["Application profile<br/>Embedded, managed or attached"]
        CHECKS["Independent check association<br/>Operation and package journeys"]
        DECL --> OPS
        DECL --> BODY
        DECL --> PROFILE
        DECL --> CHECKS
    end
    BIND["Bind one invocation<br/>Exact package and selected operation"]
    RESOURCE["Lab application binding<br/>Instance, session, lease and state schema"]
    CALL["Execute bounded attempt<br/>Retain identity and observations"]
    OPS --> BIND
    BODY --> BIND
    CHECKS --> BIND
    PROFILE --> RESOURCE
    RESOURCE --> BIND
    BIND --> CALL
    class DECL,BIND control
    class OPS,BODY,PROFILE,CALL work
    class CHECKS qualify
    class RESOURCE data
'''),
('04-adaptive-work', 'Adaptive research and invocation acceptance', '''flowchart TB
    BRIEF["Approved brief and limits"]
    EVENT["Results, new CCs, failures<br/>or human direction"]
    PLAN["Revise future agenda<br/>Planner owner"]
    BIND["Validate and bind next work<br/>Pins, grants and checks"]
    RUN["Execute operation or observe job<br/>Fixed invocation record"]
    IMPORT["Capture outputs and observations<br/>Separate host custody"]
    CHECK["Host checks and<br/>output-only review"]
    GATE["Protected acceptance decision"]
    RESULT["Accepted result<br/>Retain stated uncertainty"]
    FAILURE["Failed attempt<br/>Retain observations"]
    BRIEF --> PLAN
    EVENT --> PLAN
    PLAN --> BIND
    BIND -->|"valid"| RUN
    BIND -->|"invalid or unavailable"| FAILURE
    RUN --> IMPORT
    IMPORT --> CHECK
    CHECK --> GATE
    GATE -->|"accepted"| RESULT
    GATE -->|"rejected or infrastructure failure"| FAILURE
    RESULT --> EVENT
    FAILURE --> EVENT
    class BRIEF,BIND,GATE control
    class PLAN,RUN work
    class CHECK qualify
    class EVENT,IMPORT,RESULT,FAILURE data
'''),
('05-storage-recovery', 'Persistent state and recovery', '''flowchart TB
    subgraph LAB["Stable lab identity"]
        INSTANCE["Replaceable deployment<br/>AI4R and application processes"]
        META["Transactional records<br/>Goals, jobs, catalog and bindings"]
        FILES["Durable project data<br/>Sources, resources and service volumes"]
        EVIDENCE["Retained evidence<br/>Artifacts, assessments and provenance"]
        INSTANCE --> META
        INSTANCE --> FILES
        INSTANCE --> EVIDENCE
    end
    CHECKPOINT["Consistent checkpoint<br/>Manifest and required bytes"]
    BACKUP["Verified independent backup<br/>Different device or service"]
    FENCE["Fence old writer<br/>Block if ownership is uncertain"]
    RESTORE["New deployment, same lab ID<br/>Verify compatibility and reconcile jobs"]
    READY["Readiness verified<br/>Accept new work"]
    META --> CHECKPOINT
    FILES --> CHECKPOINT
    EVIDENCE --> CHECKPOINT
    CHECKPOINT --> BACKUP
    BACKUP --> FENCE
    FENCE --> RESTORE
    RESTORE --> READY
    class INSTANCE work
    class META,FILES,EVIDENCE,CHECKPOINT,BACKUP data
    class FENCE,RESTORE,READY control
'''),
('06-factory-adoption', 'Factory qualification and automatic local adoption', '''flowchart TB
    REQUEST["Lab or RSI capability request<br/>Behavior, sources and budget"]
    FACTORY["CC factory<br/>Capture, adapt and build candidate"]
    QUAL["Independent qualification<br/>Frozen criteria and package journeys"]
    ELIGIBLE["Eligible exact package version"]
    ACTIVATE["Activation controller<br/>Compatibility and service readiness"]
    SELECT["Automatically active locally<br/>New work selects exact version"]
    ACTIVE["Existing sessions and jobs<br/>Retain compatible old bindings"]
    WAIT["Activation pending or rollback<br/>Capacity, state or readiness blocker"]
    FAILED["Rejected or blocked candidate<br/>Retain evidence"]
    CENTRAL["Optional central submission<br/>Separate qualification and adoption"]
    REQUEST --> FACTORY
    FACTORY --> QUAL
    QUAL -->|"pass"| ELIGIBLE
    QUAL -->|"fail or unavailable evidence"| FAILED
    ELIGIBLE --> ACTIVATE
    ACTIVATE -->|"ready"| SELECT
    ACTIVATE -->|"not ready"| WAIT
    SELECT -.->|"does not rewrite"| ACTIVE
    ELIGIBLE -.->|"selected export"| CENTRAL
    class REQUEST,ACTIVE,FAILED data
    class FACTORY work
    class QUAL,ELIGIBLE,CENTRAL qualify
    class ACTIVATE,SELECT,WAIT control
'''),
('07-domain-profiles', 'Shared contracts across domain applications', '''flowchart TB
    CORE["Shared lab and CC contracts<br/>Operations, bindings, state and checks"]
    subgraph W["First validation case: workload profiling"]
        WCC["Workload CC package<br/>Profile, extract, predict and evaluate"]
        WAPP["Batch profiler or telemetry service<br/>Declared measurement access"]
        WDATA["Traces and machine records<br/>Held-out cases and result artifacts"]
        WCC --> WAPP
        WAPP --> WDATA
    end
    subgraph R["Non-blocking example: robotics"]
        RCC["Robotics CC package<br/>Configure, run, observe and compare"]
        RAPP["Library, batch or simulator service<br/>Native interface selected later"]
        RDATA["Scenes and controller versions<br/>Episodes and checkpoints"]
        RCC --> RAPP
        RAPP --> RDATA
    end
    CORE --> WCC
    CORE --> RCC
    FIXTURE["Small stateful fixture<br/>Tests lifecycle before simulator exists"]
    CORE --> FIXTURE
    class CORE control
    class WCC,WAPP,RCC,RAPP,FIXTURE work
    class WDATA,RDATA data
'''),
]

STYLE = '''
    classDef work fill:#e8f1ff,stroke:#3568a8,color:#142d4e,stroke-width:1.5px
    classDef control fill:#fff1d7,stroke:#a66d16,color:#513406,stroke-width:1.5px
    classDef qualify fill:#eee8fa,stroke:#7854a0,color:#35204d,stroke-width:1.5px
    classDef data fill:#e5f3eb,stroke:#3c8160,color:#163e2a,stroke-width:1.5px
    classDef external fill:#f0f2f5,stroke:#65758a,color:#273547,stroke-width:1.5px
'''

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def render(item):
    stem, title, source = item
    inp = OUT / (stem + '.mmd')
    inp.write_text(source + STYLE, encoding='utf-8')
    for ext in ['svg', 'png']:
        dest = OUT / (stem + '.' + ext)
        cmd = ['node', str(CLI), '-i', str(inp), '-o', str(dest), '-c', str(OUT / 'render-config.json'), '-b', 'white', '--size', '1600', '-s', '1.5']
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=100)
        if r.returncode:
            raise RuntimeError(stem + '\n' + r.stdout + r.stderr)
    print('Rendered ' + stem, flush=True)
    return {'stem': stem, 'title': title, 'source_sha256': digest(inp), 'svg_sha256': digest(OUT / (stem+'.svg')), 'png_sha256': digest(OUT / (stem+'.png'))}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    config = {'theme':'base', 'themeVariables': {'fontFamily':'Arial, sans-serif', 'fontSize':'17px', 'primaryColor':'#e8f1ff', 'primaryTextColor':'#142d4e', 'lineColor':'#536579', 'clusterBkg':'#f8fafc', 'clusterBorder':'#bac6d5', 'edgeLabelBackground':'#ffffff'}, 'flowchart': {'htmlLabels':False, 'wrappingWidth':260, 'curve':'linear', 'nodeSpacing':35, 'rankSpacing':45, 'padding':16}}
    (OUT/'render-config.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(render, DIAGRAMS))
    (OUT/'manifest.json').write_text(json.dumps({'purpose':'M2 sandbox proposal, not runtime evidence','renderer':'Existing local Mermaid CLI; source files are canonical diagram definitions','diagrams':rows},indent=2)+'\n',encoding='utf-8')
    print('Complete: seven source diagrams, PNGs and SVGs')

if __name__ == '__main__':
    main()
