---
id: muse-cc-lab-diagrams
status: proposed-module-communication-views
source: CC schema and lab communication.md; Lab internals and telemetry.md; Tools.md
last_reviewed: 2026-11-05
next_action: Review module data paths and use only essential views in the short presentation
---

> **Post-presentation revision, November 9:** [[Post-presentation design revision]] is the current conceptual reference. Contract, CC and release image are distinct. Tool/skill CCs support agents; component CCs supply engine functionality. The lab agent now sits outside the experiment Incus instance in a separate management container. Earlier diagrams/specimens below remain historical where they disagree.

> Retained detailed context. Current November6 direction is [[Alignment and decisions]]: immutable submitted images, test-only lab, and Factory-owned knowledge/telemetry. Earlier local-workbench/native-first options are superseded, not implementation evidence.

**Current presentation revision (November 5):** [[Design rationale]] and [[Inference layers and profiling]] record the compatible Builder, optional ontology, scoped lab build/debug loop, nested Docker/Incus capture and current terminology. [[Build challenges]] and [[Data to collect]] distinguish proposed integrations from qualified evidence. The retained detail below predates that presentation revision where its scope differs.

# Five concrete views for the deep dive

These diagrams explain our CC/lab modules under a working unified coding-agent flow. They do not claim adoption of a complete system architecture or runtime validation. Use request/schema and sensor/dyno views in the main talk; keep broad context brief.

## 1. Full CC spectrum in one coding-agent flow

```mermaid
flowchart LR
  request["Request CC<br/>desired interface + materials + open choices"] --> builder["Unified coding agent<br/>inspect, code, build, package"]
  tools["Prebuilt CCs<br/>inspection / build / correctness / tuning"] --> builder
  builder --> engine["Implemented engine CC<br/>native product or image + interface"]
  builder --> supporting["Supporting CCs<br/>sensors / dyno / tools / knowledge"]
  engine --> lab["Existing lab boundary<br/>worker + engine + test tools"]
  supporting --> lab
  lab --> evidence["Memory + quality + speed evidence<br/>failures and coverage included"]
  evidence -->|"next candidate / tool / recipe"| builder
  supporting --> tools
```

[SVG](diagrams/01-system.svg) / [PNG](diagrams/01-system.png)

A separate CC implementation factory is not required by this working model. Architecture adoption remains with its responsible owner.

## 2. Lab calls and runtime communication

```mermaid
sequenceDiagram
  participant A as JiuwenSwarm / Codex agent
  participant M as CC MCP front door
  participant H as Local CC Host
  participant E as Native / Docker service
  participant D as Native client CC
  A->>M: cc_list / cc_describe / cc_material
  M->>H: Prepare and inspect selected packages
  M-->>A: Declarations, material and granted handles
  A->>M: cc_start(cc, api, inputs, key)
  M->>H: Host.start selected served capability
  H->>E: Start identified implementation
  E-->>H: Health response / provider observations
  H-->>M: Instance state, endpoint and identity
  M-->>A: Instance + environment handle
  A->>M: cc_call(client, benchmark, engine handle, key)
  M->>H: Bind inputs/resources and reserve key
  H->>D: Finite process packet
  D->>E: Native HTTP request
  E-->>D: Business response
  D-->>H: Metrics / artifact output
  H-->>M: Receipt and retained output references
  M-->>A: Result with receipt state to inspect
  A->>M: cc_stop(instance)
  M->>H: Stop session-owned instance
  H->>E: Stop and confirm cessation
  H-->>M: Confirmed stopped status
  M-->>A: Tool result with stopped state
```

[SVG](diagrams/02-deployment.svg) / [PNG](diagrams/02-deployment.png)

This is the implemented local tool/runner/service route. The retained demo uses synthetic HTTP compute, not inference streaming. A real inference engine can keep its native HTTP/SSE API; the remote Spark/Incus worker is a separate lab integration, not this local Host.

## 3. Sensors and dyno inside the lab

```mermaid
flowchart LR
  subgraph candidate["Measured engine scope"]
    engine["Native engine / image<br/>API + runtime state"]
    diag["Opt-in diagnostics<br/>routing / logits / stage events"]
    engine --> diag
  end
  proc["Host /proc<br/>memory, process, I/O, faults"] --> collector
  cg["Actual cgroup v2<br/>current, peak, stat, events, swap"] --> collector
  nvml["NVML where supported<br/>utilization, power, temperature"] --> collector
  collector["Protected host collector<br/>timestamp + units + coverage"] --> raw["Durable raw evidence<br/>attempt + generation + hashes"]
  diag --> decode["Versioned diagnostic decoder<br/>preserve original bytes"]
  decode --> raw
  dyno["Protected client dyno<br/>monotonic event timestamps"] -->|"fixed HTTP workload"| engine
  engine -->|"SSE events / usage"| dyno
  dyno --> raw
  raw --> compare["Memory + TTFT + token rate<br/>standardized benchmark result"]
  compare --> agent["Agent diagnosis / next candidate"]
```

[SVG](diagrams/03-evidence.svg) / [PNG](diagrams/03-evidence.png)

This is the proposed inference observation boundary, not a claim that the synthetic demo already provides these GPU/host sensors. The engine may provide diagnostics but cannot author protected host/client measurements. Missing coverage stays visible.

## 4. Dyno, memory budgets and feedback

```mermaid
flowchart TB
  candidate["Identified engine CC + native product"] --> identity["Start and verify loaded generation<br/>fixed workload/state/policy"]
  identity --> qualify{"Relevant memory paths<br/>accounted and constrained?"}
  qualify -->|"no"| gap["Report coverage gap<br/>no hard-budget claim"]
  qualify -->|"yes"| budget["Trial at explicit byte budget<br/>40 to 39 GB is an example"]
  budget --> runs["Repeated baseline/candidate runs<br/>diagnostics separate from timing"]
  runs --> results["Peak memory + client timings<br/>correctness + standard benchmark"]
  results --> judge{"Quality and speed gates met<br/>within tested budget?"}
  judge -->|"yes"| lower["Record passing point<br/>lower budget per run policy"]
  lower --> budget
  judge -->|"no / incomplete"| report["Keep failure class and raw evidence<br/>report tested boundary and uncertainty"]
  report --> agent["Same coding agent / RSI<br/>revise engine, tool or recipe"]
  agent --> candidate
```

[SVG](diagrams/04-budget-loop.svg) / [PNG](diagrams/04-budget-loop.png)

The inference-lab design requires this operation; the current synthetic client demo does not qualify GPU memory budgets. Exact experiment choice, repetitions and budget policy belong to project planning. A tested boundary is not a universal minimum.

## 5. Request ontology to implemented engine CC

```mermaid
flowchart LR
  subgraph request["Non-executable request CC"]
    desired["desired.capabilities + open<br/>engine interface and absent choices"]
    materials["desired.materials<br/>ontology / profile / source / image records"]
  end
  ontology["Assigned ontology contributor<br/>desired internal structure"] --> materials
  desired --> build["Coding agent<br/>read materials, implement, build"]
  materials --> build
  build --> product["Implemented engine CC<br/>bindings + serves + materials<br/>native product / realized description"]
  build --> tools["Supporting tool CCs"]
  product --> host["Current CC Host + agent tools<br/>prepare / start / call / stop"]
  tools --> host
  host --> future["Inference lab integration<br/>qualified model, memory and benchmark"]
  future --> evidence["Actual generation and measurement evidence<br/>not metadata alone"]
  evidence -->|"next candidate / tool / recipe"| build
```

[SVG](diagrams/05-ontology.svg) / [PNG](diagrams/05-ontology.png)

Current schema support is `desired.materials` and capability `serves`; no new root `system` field is needed. A synthetic request-built service and local lifecycle were demonstrated. The real inference ontology, backend and lab measurements remain future qualification.
