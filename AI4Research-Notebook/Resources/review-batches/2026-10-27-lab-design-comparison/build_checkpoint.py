"""Checkpoint 1 only: comparison note, two matched vector/raster diagrams and navigation."""
from pathlib import Path
import hashlib
import html
import json
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

V=Path(__file__).resolve().parents[3]
B=Path(__file__).resolve().parent
OUT=V/'Designs/Lab Design Comparison'
OUT.mkdir(parents=True,exist_ok=True)
receipts=[]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(rel,text):
    p=V/rel
    if p.exists():
        dst=B/'before'/(rel.replace('/','__')+'.snapshot')
        dst.parent.mkdir(parents=True,exist_ok=True)
        assert not dst.exists(),f'Already captured: {rel}'
        dst.write_bytes(p.read_bytes());assert sha(dst)==sha(p)
        receipts.append({'path':rel,'before_sha256':sha(dst),'snapshot':dst.relative_to(V).as_posix()})
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes((text.strip()+'\n').encode('utf-8'))

# One geometry and vocabulary for both alternatives, so detail does not favor one.
W,H=1640,1200
colors={'ink':'#1F2A44','muted':'#59677A','bg':'#FAF8F4','work':'#E8EDF9','workline':'#3D4FB0','control':'#FFF0D8','controlline':'#A56815','data':'#E4F3EC','dataline':'#2C7A59','external':'#EEF1F5','rule':'#CAD0DA'}
fontroot=Path('C:/Windows/Fonts')
fonts={}
def font(sz,bold=False):
    key=(sz,bold)
    if key not in fonts:fonts[key]=ImageFont.truetype(str(fontroot/('segoeuib.ttf' if bold else 'segoeui.ttf')),sz)
    return fonts[key]

def diagram(vm):
    stem='02-vm-per-lab' if vm else '01-shared-host-containers'
    im=Image.new('RGB',(W,H),colors['bg']);d=ImageDraw.Draw(im)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="{colors["bg"]}"/>']
    graph={'title':'B: VM per lab' if vm else 'A: Shared-host container labs','nodes':[],'edges':[]}
    def text(x,y,lines,size=23,color=None,bold=False,anchor='left'):
        col=color or colors['ink']
        if isinstance(lines,str):lines=lines.split('\n')
        for i,t in enumerate(lines):
            yy=y+i*(size+7)
            width=d.textlength(t,font=font(size,bold))
            assert width<W-40,('oversize',t)
            xx=x-width/2 if anchor=='center' else x
            d.text((xx,yy),t,font=font(size,bold),fill=col)
            svg.append(f'<text x="{x}" y="{yy+size}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{col}" text-anchor="{"middle" if anchor=="center" else "start"}">{html.escape(t)}</text>')
    def box(n,x,y,w,h,lines,kind='work',size=23):
        fill=colors.get(kind,colors['external']);stroke=colors.get(kind+'line',colors['rule'])
        d.rectangle((x,y,x+w,y+h),fill=fill,outline=stroke,width=2)
        svg.append(f'<g id="{n}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        ls=lines.split('\n');lineh=size+7;top=y+(h-lineh*len(ls))/2
        for t in ls:assert d.textlength(t,font=font(size,True))<=w-24,(n,t)
        text(x+w/2,top,ls,size,bold=True,anchor='center')
        svg.append('</g>');graph['nodes'].append({'id':n,'position':[x,y,w,h],'text':lines,'kind':kind})
    def region(n,x,y,w,h,title,color):
        d.rectangle((x,y,x+w,y+h),outline=color,width=3)
        svg.append(f'<g id="{n}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{color}" stroke-width="3"/></g>')
        text(x+16,y+12,title,23,colors['muted'] if n=='host' else color,True)
    def arrow(n,pts,label='',lx=0,ly=0,color=None,dashed=False):
        col=color or colors['muted']
        for a,b in zip(pts,pts[1:]):
            if dashed:
                length=abs(b[0]-a[0])+abs(b[1]-a[1]);steps=max(1,int(length/10))
                for i in range(0,steps,2):
                    t0=i/steps;t1=min((i+1)/steps,1)
                    d.line((a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0,a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1),fill=col,width=2)
            else:d.line([a,b],fill=col,width=2)
        a,b=pts[-2:];dx=b[0]-a[0];dy=b[1]-a[1]
        if dx:
            sign=1 if dx>0 else -1;tri=[b,(b[0]-sign*10,b[1]-5),(b[0]-sign*10,b[1]+5)]
        else:
            sign=1 if dy>0 else -1;tri=[b,(b[0]-5,b[1]-sign*10),(b[0]+5,b[1]-sign*10)]
        d.polygon(tri,fill=col)
        svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="{col}" stroke-width="2"'+(' stroke-dasharray="8 6"' if dashed else '')+'/>')
        svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in tri)}" fill="{col}"/>')
        if label:text(lx,ly,label,18,col)
        graph['edges'].append({'id':n,'points':pts,'label':label,'dashed':dashed})

    text(40,25,graph['title'],36,bold=True)
    text(40,77,'Same research capability and controls; different lab and administrative boundaries',22,colors['muted'])
    box('people',40,130,310,84,'People\nLab UI / shell / editor','external',24)
    box('operator',400,130,860,84,'Infrastructure operator control\nWorks independently of a responsive research agent','control',24)
    region('host',40,265,1220,670,'Qualified VM host / provider' if vm else 'Shared host kernel and Docker Engine',colors['rule'])
    region('lab',70,325,1160,480,'Lab A VM: own guest kernel and Engine' if vm else 'Lab A: logical workload / data scope, not a VM',colors['workline'])
    box('ui',100,385,260,70,'Lab interface','work',25)
    box('shell',390,385,200,70,'Lab VM shell' if vm else 'Scoped shell','external',22)
    box('runtime',100,500,490,180,'Complete lab AI4R, version A\nIntent / planning / research / checking\nKnowledge / capability library\nCC factory / RSI','work',23)
    box('supervisor',650,385,540,70,'VM supervisor + own Docker Engine' if vm else 'Host supervisor + shared Docker Engine','control',23)
    text(650,462,'Only the controller holds Engine authority',18,colors['controlline'])
    box('cc',650,510,245,130,'Containerized CCs\nVendored tool parts\nand dependencies','work',23)
    box('apps',945,510,245,130,'Domain applications\nLibrary, batch or\nstateful service','work',22)
    box('data',100,720,1090,62,'Persistent lab data: knowledge, accepted artifacts, jobs and application state','data',22)
    box('peers',70,840,1160,66,'Other lab VMs: their own guest kernels, Engines, AI4R versions and data' if vm else 'Other lab containers: separate AI4R versions and data, same host kernel / Engine','external',22)
    text(1310,270,'Shared services',26,bold=True)
    text(1310,309,'Same or different machine',19,colors['muted'])
    box('inference',1310,385,290,90,'Shared inference\nAuthenticated endpoint','external',22)
    box('images',1310,530,290,90,'Image / artifact source\nSelected pinned packages','external',21)
    box('backup',1310,720,290,90,'Independent backup\nVerified restore input','data',22)

    arrow('people-ui',[(195,214),(195,242),(25,242),(25,420),(100,420)],'primary connection',40,220)
    arrow('people-shell',[(350,172),(370,172),(370,238),(610,238),(610,420),(590,420)],'direct access',400,217,dashed=True)
    arrow('ui-runtime',[(230,455),(230,500)])
    arrow('runtime-supervisor',[(590,550),(620,550),(620,420),(650,420)],color=colors['workline'])
    arrow('supervisor-cc',[(772,455),(772,510)],color=colors['controlline'])
    arrow('cc-app',[(895,575),(945,575)])
    arrow('runtime-data',[(345,680),(345,720)],color=colors['dataline'])
    arrow('app-data',[(1065,640),(1065,720)],color=colors['dataline'])
    arrow('inference-api',[(1190,420),(1310,420)],'model API',1200,391,dashed=True)
    arrow('package-import',[(1310,575),(1278,575),(1278,440),(1190,440)],color=colors['muted'],dashed=True)
    arrow('backup-data',[(1190,751),(1310,751)],color=colors['dataline'],dashed=True)
    arrow('operator-control',[(830,214),(830,250),(1220,250),(1220,348)],color=colors['controlline'])
    text(1030,224,'start / stop lab',18,colors['controlline'])
    text(650,663,'Cancel experiment / normal lab stop:',18,colors['controlline'],True)
    text(650,689,'stop owned work, observe status, retain data',18,colors['controlline'])
    text(40,955,'Operator-controlled lifecycle paths',25,bold=True)
    box('restart',40,1002,385,94,'Stopped → restart\nReconcile before dispatch','control',23)
    box('delete',455,1002,385,94,'Separate delete request\nExplicit data disposition','control',23)
    box('emergency',870,1002,390,94,'Emergency: stop the VM\nHost / provider confirms state' if vm else 'Emergency: stop containers\nOwned lab resources only\nRequires responsive Engine','control',22)
    box('shared-stays',1310,1002,290,94,'Other labs and shared\nservices stay running*','external',21)
    text(40,1122,'*Designed scoped stop. Host failure can affect co-located labs; remote effects may need cancellation/reconciliation.',19,colors['muted'])
    text(40,1158,'Design comparison only. No shutdown, isolation, restore or performance trial was run.',19,colors['muted'])
    svg.append('</svg>')
    (OUT/f'{stem}.svg').write_text('\n'.join(svg),encoding='utf-8')
    im.save(OUT/f'{stem}.png')
    (OUT/f'{stem}.graph.json').write_text(json.dumps(graph,indent=2)+'\n',encoding='utf-8')
    return {'stem':stem,'svg_sha256':sha(OUT/f'{stem}.svg'),'png_sha256':sha(OUT/f'{stem}.png'),'nodes':len(graph['nodes']),'edges':len(graph['edges'])}

diagrams=[diagram(False),diagram(True)]
assert diagrams[0]['nodes']==diagrams[1]['nodes'] and diagrams[0]['edges']==diagrams[1]['edges']
(OUT/'manifest.json').write_text(json.dumps({'purpose':'Checkpoint 1 comparison, not implementation or runtime evidence','diagrams':diagrams},indent=2)+'\n',encoding='utf-8')
if '--diagrams-only' in sys.argv:
    print('Rendered two matched diagrams; note and notebook routes preserved.')
    raise SystemExit(0)

note='''---
id: lab-design-comparison-checkpoint-1
status: comparison-for-discussion-not-selected
source: Sources/Prompts/2026-10-27-implement-lab-comparison.txt; Resources/review-batches/2026-10-27-lab-design-comparison/source-review.json
last_reviewed: 2026-10-27
next_action: Discuss the lab boundary and reuse choice before changing the current architecture or deck
---
# Lab designs: which boundary fits our work?

**Working recommendation: one VM per lab, containerized CCs inside it, and selective OpenJiuwen reuse.** This best fits people administering independently evolving research environments. Shared-host containers remain a credible lower-overhead option when lab owners do not need unrestricted guest administration. The recommendation is a fit assessment, not a measured performance or isolation result.

This is checkpoint 1 only: compare the choices before selecting the architecture. The existing [[Designs/Sandbox Lab Design|sandbox proposal]] and presentation are unchanged. No platform, hypervisor or sandbox was installed or tested.

## Same research system, different lab boundary

Both diagrams show one expanded lab and representative peers, not a fixed number of labs or people. Each lab contains a complete independently versioned AI4R: intent/requirements, planning, research stages, checking, knowledge, capability library, CC factory and RSI. People primarily use their lab interface and may use a terminal/editor. Shared inference and package services are network endpoints that can live on another machine.

CC images vendor tool implementations, adapters and software dependencies. Model weights, credentials, large datasets and attached services are separately declared resources. Containers provide the packaging/execution unit; they do not themselves supply all scientific checks or a new research orchestrator. Inference access is shown schematically: its relay or direct client must receive scoped authority rather than the Engine socket.

### A. Shared-host container labs

![Option A: complete AI4R labs sharing a host kernel and Engine](Lab%20Design%20Comparison/01-shared-host-containers.png)

[Scalable SVG](Lab%20Design%20Comparison/01-shared-host-containers.svg)

### B. VM per lab, with containerized capabilities

![Option B: complete AI4R inside independently managed lab VMs](Lab%20Design%20Comparison/02-vm-per-lab.png)

[Scalable SVG](Lab%20Design%20Comparison/02-vm-per-lab.svg)

| Decision criterion | A: shared host containers | B: VM per lab |
|---|---|---|
| Advantages | Fewer guest systems to maintain; normally lower idle overhead; one Engine can share image layers | Own guest kernel, packages and Engine; direct human guest administration; VM stop works independently of guest AI4R |
| Costs | Shared host/Engine administration needs tighter scoping; host/kernel failures can affect several labs | Guest memory/disk and updates; image/cache copies across VMs; device access needs qualification |
| Independent AI4R and RSI | Supported with separate containers, source and data; host-level changes remain infrastructure-owned | Supported inside each guest; local changes still need recovery and qualification controls |
| People editing the environment | Scoped container shell/editor. Giving access to the shared host Engine would expand authority beyond one lab | Guest shell/admin access can be lab-local. Hypervisor/provider authority stays outside the guest |
| Stop when AI4R hangs | Outside operator/supervisor stops that lab's owned containers; Engine failure requires a broader host recovery path | Outside operator requests guest shutdown, then forced VM power-off if needed; guest supervisor need not respond |
| Shared hardware | More direct host-device access, but scheduling and measurement interference still need controls | CPU guests are straightforward only on a qualified provider; GPU/device availability must be demonstrated |

The baseline tradeoffs follow Docker's namespace/cgroup and daemon-authority model and libvirt's guest shutdown/power-off controls. Overhead and fault-containment outcomes are deployment-dependent. Containers with separate daemons or stronger isolation profiles are possible but outside this two-option comparison. [Docker security](https://docs.docker.com/engine/security/), [libvirt lifecycle controls](https://libvirt.org/manpages/virsh.html).

## Management and execution reuse are separate decisions

These approaches can combine. In particular, a small VM supervisor can reuse OpenJiuwen interfaces without adopting a complete workspace platform.

| Approach | Pros | Cons / limits | Reuse, adapter and remaining AI4R work |
|---|---|---|---|
| Existing VM tooling + small stable supervisor | Small dependency set; preserves our lab lifecycle and packaging choices | We supply operator integration, job ownership/reconciliation and an accessible control surface | Reuse provider/Engine lifecycle; adapt typed lab/job requests; retain AI4R checking, artifact transfer and state recovery |
| Selective OpenJiuwen / JiuwenBox reuse | Source contains goals, replay, RSI and tool-sandbox lifecycle/job controls | JiuwenBox uses bubblewrap; it is not our OCI package carrier or outer VM. API presence does not establish backend termination | Reuse compatible capabilities/interfaces; adapt scoped resource and package bindings; verify real stop and restart behavior |
| Coder Workspaces | Existing access, provisioning and workspace-agent services; useful for multiple people | Additional control plane/database/templates; unattended work must integrate with scheduling; provider/edition constraints need checking | Evaluate workspace access/lifecycle integration. Keep the entire AI4R research loop and local data in the lab |

**OpenJiuwen evidence:** installed SDK `9e339019` contains `harness/goal`, workflow journal replay and `rsi`. Its sandbox gateway exposes release policies, but base `pause/resume/delete` methods are no-ops; default `on_stop` is `delete`, and idle eviction is described as deletion. Do not map durable-lab stop to that default. At inspected upstream JiuwenSwarm `02b37f47`, JiuwenBox implements start/stop/restart/delete and background-job kill; its manager calls `runtime.stop` before recording STOPPED. These are source observations, not our host test results. [SDK lifecycle contract](https://github.com/openJiuwen-ai/agent-core/blob/develop/openjiuwen/core/sys_operation/sandbox/launchers/base.py), [JiuwenBox](https://github.com/openJiuwen-ai/jiuwenswarm/tree/develop/jiuwenbox).

**Coder evidence:** its documented control plane connects users, provisioners and workspaces; workspace agents provide SSH, port forwarding and liveness. Scheduling detects specified session/activity types, so a disconnected human must not cause an active research job to be treated as idle. Coder is an evaluated option, not the default winner. [Architecture](https://coder.com/docs/install/plan/architecture), [scheduling](https://coder.com/docs/user-guides/workspace-scheduling).

## Shutdown must mean an observed outcome

| Operation | Designed behavior in both choices |
|---|---|
| Pause research | Block new dispatch; retain and account for active work. This alone does not release compute. |
| Cancel experiment | Supervisor requests termination, escalates within a configured bound, then observes job/process status. An unconfirmed outcome stays unknown. |
| Normal lab stop | Stop new work, drain/cancel owned jobs and stop lab services. Keep persistent data. |
| Emergency stop | Outside control stops the owned container set in A or the whole VM in B. Host failure still needs infrastructure recovery. |
| Restart | Reconcile jobs, ownership, accepted artifacts and application state before dispatch; inspect uncertain external effects before retry. |
| Delete | Separate explicit operation with a data-disposition decision. Normal stop and idle expiry do not delete unique project state. |

Stopping one lab must not stop a shared inference service or another lab. Cancel or reconcile its outstanding remote jobs/requests where supported; a VM power-off cannot undo an external effect. People may administer their guest, while agents have narrower access. Internal controls cannot promise protection against a human administrator deliberately overriding them.

## What would change the recommendation?

Choose B if direct guest administration, independent system evolution and an outside whole-VM stop are important enough to justify its cost. Choose A if workloads fit a controlled container profile and measured density/operational simplicity matters more. Both need bounded storage, verified external backups, restore and interference controls.

Before calling either choice demonstrated: measure idle/run resource cost; stop a runaway job; stop an unresponsive lab from outside; restart without duplicate effects; restore retained findings; and confirm another lab and shared inference remain available. No result for these checks is claimed here. Provider support, especially accelerator access, can change the decision.

The discussion now needs only two decisions: which lab boundary fits our operating model, and whether a workspace platform removes enough work to justify itself. Next, checkpoint 2 can replace the architecture explanation and stack around the selected boundary. Checkpoint 3 can expand the evidence appendix. The current deck has not been expanded.
'''
write('Designs/Lab Design Comparison.md',note)

sources=[]
pins=[('installed SDK','AI4Research-Development/openjiuwen-builder-sdk-9e339','9e3390195a9ea15235b2b5f7412cb2aa440622cc',[
 'openjiuwen/core/sys_operation/sandbox/launchers/base.py','openjiuwen/core/sys_operation/sandbox/launchers/pre_deployment_launcher.py','openjiuwen/core/sys_operation/sandbox/gateway/gateway.py','openjiuwen/core/sys_operation/config.py','openjiuwen/harness/goal/schema.py','openjiuwen/agent_teams/workflow/engine/journal.py','openjiuwen/rsi/__init__.py']),
 ('upstream JiuwenSwarm','openjiuwen/jiuwenswarm','02b37f47fbefe80a58e4ed88606120818ca44ac3',[
 'jiuwenbox/README.md','jiuwenbox/src/jiuwenbox/server/sandbox_manager.py','jiuwenbox/src/jiuwenbox/server/runtime/process.py','jiuwenbox/src/jiuwenbox/supervisor/cgroup.py'])]
for role,root,pin,paths in pins:
    repo=V.parent/root
    actual=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip();assert actual==pin
    for rel in paths:
        p=repo/rel;original=subprocess.check_output(['git','-C',str(repo),'show',f'{pin}:{rel}'])
        actualbytes=p.read_bytes()
        # Checkout line endings may differ; record bytes and compare normalized source.
        assert original.replace(b'\r\n',b'\n')==actualbytes.replace(b'\r\n',b'\n'),str(p)
        sources.append({'role':role,'repository':root,'revision':pin,'path':rel,'sha256':sha(p)})
(B/'source-review.json').write_text(json.dumps({'date':'2026-10-27','scope':'source review only; not runtime evidence','sources':sources,'external_sources':['https://docs.docker.com/engine/security/','https://libvirt.org/manpages/virsh.html','https://coder.com/docs/install/plan/architecture','https://coder.com/docs/user-guides/workspace-scheduling'],'mutable_link_note':'Online develop/doc links are navigation; local hashes and exact revisions above bound code observations.'},indent=2)+'\n',encoding='utf-8')

for rel,old,new in [
 ('Home.md','## Open directly','## Open directly\n\n- [[Designs/Lab Design Comparison|Lab design comparison: checkpoint 1]] — matched diagrams, pros/cons, OpenJiuwen reuse and shutdown paths; boundary selection remains open.'),
 ('Designs/Design Library.md','# Design library','# Design library\n\n[[Designs/Lab Design Comparison|Checkpoint 1: compare the lab designs]] precedes the next architecture selection. It does not replace the current proposal or expand the deck.'),
 ('Sources/Implementation Intent.md','# Current intent and working requirements','# Current intent and working requirements\n\n**October 27 bounded checkpoint:** [[Designs/Lab Design Comparison]] compares complete independently versioned labs, human access, network-shared services, containerized CCs and shutdown. Discuss boundary and software reuse first; architecture replacement and deck expansion are later checkpoints. Earlier container-first/VM-first wording is proposal history, not a newly selected deployment.'),
]:
    t=(V/rel).read_text('utf-8');assert old in t;write(rel,t.replace(old,new,1))

(B/'before-state.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
print('Saved comparison note, two matched diagrams (SVG/PNG), source review and notebook routes.')
