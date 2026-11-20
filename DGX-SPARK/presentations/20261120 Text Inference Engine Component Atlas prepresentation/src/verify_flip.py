"""Check the offline component flip against the source presentation in Chromium."""
import argparse
import json
import re
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


SOURCE = Path(__file__).resolve().parent
DESKTOP = Path.home() / "Desktop"
ORIGINAL = DESKTOP / "20261117 Text Inference Engine Atlas prepresentation.html"
EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
TABS = ["Engine", "Compare engines", "Software factory", "Factory integration",
        "From scratch", "All CCs", "Quantization", "Evidence"]
# 20261120 inventory: 46 components, 53 CCs (36 builder, 5 tool, 6 analysis, 6 factory), 101 actions, 65 handoffs.
EDITION = json.loads((SOURCE / "edition.json").read_text("utf-8"))
KIND_COUNTS = {"builder": 36, "tool": 5, "analysis": 6, "factory": 6}
N_CCS, N_COMPONENTS, N_ACTIONS, N_HANDOFFS, N_JOBS = sum(KIND_COUNTS.values()), 46, 101, 65, 20
# JiuwenSwarm capsule catalog (demo UI atlas-names.json, 63 directories) and the UI kind legend, word for word.
CAPSULE_COUNTS = {"builder": 19, "tool": 11, "analysis": 22, "factory": 11}
UI_LEGEND = {
    "builder": ("Builder", "Writes the source code for one engine component. The CC is the method that builds the code; it is not the component itself."),
    "tool": ("Tool", "Runs an existing tool, lab or runner and returns a verified receipt or artifact. It does not write product source."),
    "analysis": ("Analysis", "Reads evidence such as traces, counters and profiles and returns findings that a verifier can recompute. It does not write product source."),
    "factory": ("Factory worker", "Performs one step of the software factory and hands off its artifact."),
}
CAMPAIGN_COUNTS = {"73": "capped model launches", "28": "factory homes", "87": "planner decisions", "16": "native build attempts",
                   "538": "observations", "5": "starred builder CCs", "6": "analysis CCs created"}

# Include dimensions to catch wrapping and positioning regressions at both widths.
HEADER = """() => Array.from(document.querySelectorAll(
  'header, header .brand, header nav, header nav a, header button'
)).map(el => {
  const style=getComputedStyle(el), box=el.getBoundingClientRect();
  const properties=['display','alignItems','flexWrap','gap','padding','backgroundColor',
    'color','fontFamily','fontSize','fontWeight','lineHeight','borderBottom','minHeight'];
  return {tag:el.tagName,text:el.childElementCount?null:el.textContent.trim(),
    css:Object.fromEntries(properties.map(p=>[p,style[p]])),
    rect:[box.x,box.y,box.width,box.height].map(Math.round)};
})"""

GO = """async hash => {
  if(location.hash!==hash) await new Promise(done=>{
    addEventListener('hashchange',done,{once:true}); location.hash=hash;
  });
}"""

def check(condition, message):
    if not condition:
        raise AssertionError(message)


def visit(page, route):
    page.evaluate(GO, "#" + route)


def overview_and_paths(page, url):
    visit(page,"assemblies")
    homes=["weights","request","generation","decoder","state","backend"]
    cards=page.locator(".assembly-node[data-assembly]")
    check(set(cards.evaluate_all("els=>els.map(el=>el.dataset.assembly)"))==set(homes)
          and cards.count()==6, "Expected six distinct assembly cards")
    layout=cards.evaluate_all("""els=>els.map(el=>{
      const r=el.getBoundingClientRect();return [r.top,r.bottom,r.left,r.right];
    })""")
    for i,(top,bottom,left,right) in enumerate(layout):
        check(0<=top<bottom<=900 and 0<=left<right<=1440, f"Assembly {i+1} outside the presentation viewport")
        for other in layout[:i]:
            ot,ob,ol,orr=other
            check(min(bottom,ob)<=max(top,ot)+1 or min(right,orr)<=max(left,ol)+1,
                  "Home assembly cards overlap")
    check(page.locator('main svg [data-ax-id]').count()<=6,"Detailed execution graph on the home route")
    for name in homes:
        visit(page,"assemblies")
        page.locator(f'.assembly-node[data-assembly="{name}"]').click()
        expect(page).to_have_url(url+"#assembly/"+name)
        check(page.locator("main a").count()>0,"Assembly detail lacks a drilldown: "+name)
    visit(page,"assemblies")
    page.locator('.assembly-node[data-assembly="decoder"]').focus()
    page.keyboard.press("Enter")
    expect(page).to_have_url(url+"#assembly/decoder")
    for route in ["assembly/decoder/layer","assembly/decoder/layer/routed","component/engine.expert_weight_cache"]:
        page.locator(f'main a[href="#{route}"]').first.click()
        expect(page).to_have_url(url+"#"+route)
    for trace,n in [("token",18),("cold",8)]:
        visit(page,"assemblies")
        page.locator(f'main a[href="#trace/{trace}/0"]').first.click()
        for i in range(n):
            section=page.locator(f'[data-trace="{trace}"][data-step="{i}"]')
            expect(section).to_be_visible()
            expect(page).to_have_url(url+f"#trace/{trace}/{i}")
            check(section.locator("svg [data-ax-id]").count()==2,"Walkthrough traversal must display one component pair")
            check(section.locator('a[href^="#handoff/"]').count()>=1 and section.locator('a[href^="#action/"]').count()>=1,
                  f"Missing handoff or action link on {trace}/{i}")
            if trace=="token" and i==11:
                expect(section).to_contain_text("(5 × 4 + 2 × 11) / 7 = 6")
            if i+1<n:
                section.locator('[rel=next]').click()
        section.locator('[rel=prev]').click()
        expect(page).to_have_url(url+f"#trace/{trace}/{n-2}")
    visit(page,"assemblies")
    page.locator('main a[href="#connections"]').first.click()
    rows=page.locator("[data-engine-handoffs] [data-handoff-row]")
    check(rows.count()==N_HANDOFFS,"Full engine handoff inventory")
    inventory=rows.evaluate_all("""els=>els.map(el=>[
        el.querySelector('a[href^="#handoff/"]')?.getAttribute('href'),el.textContent
    ])""")
    edges=page.evaluate("engineHandoffs")
    check(len(edges)==N_HANDOFFS,f"Expected {N_HANDOFFS} canonical engine handoffs")
    added={
        ("weights.checkpoint_reader","model.decoder_stack"),("weights.checkpoint_reader","model.vocabulary_projection_head"),
        ("attention.dense_attention_operator","memory.sequence_kv_cache"),
        ("backend.kernel_dispatcher","engine.expert_weight_cache"),
        ("memory.workspace_allocator","backend.kernel_dispatcher"),("model.decoder_stack","backend.kernel_dispatcher"),
    }
    check(added<={(s,t) for s,t,*_ in edges},"Missing explicit pack, state, workspace or eager kernel handoff")
    by_href={href:body for href,body in inventory}
    for source,target,payload,*_ in edges:
        href="#handoff/"+source+"/"+target
        check(href in by_href and payload in by_href[href],"Inventory lost original payload for "+href)
    first_link=rows.first.locator('a[href^="#handoff/"]').first
    href=first_link.get_attribute("href")
    first_link.click()
    expect(page).to_have_url(url+href)

def factory_capabilities(page, data):
    caps={c["id"]:c for c in data["ccs"]}
    parts={c["id"]:c for c in data["components"]}
    build_pairs=data["builds"]
    operations=data["factoryCapabilities"]
    check(len(build_pairs)==KIND_COUNTS["builder"] and len(operations)==KIND_COUNTS["factory"],"Expected 36 build CCs and six factory capabilities")
    check({c for c,_ in operations}.isdisjoint({c for c,_ in build_pairs}),"Factory capabilities also marked as builders")
    check({part for _,part in operations}=={c["id"] for c in parts.values() if c["scope"]=="Factory"},
          "Every software factory component needs its corresponding capability")
    forbidden=re.compile(r"\bbuild (?:the |a |an )?(?:"+
                         "|".join(re.escape(parts[pid]["name"]) for _,pid in operations)+r")\b",re.I)
    capability_ids={cid for cid,_ in operations}
    def wording(body, route):
        match=forbidden.search(body)
        check(match is None,"Factory tool presented as a build assignment on "+route+
              (": "+match.group(0) if match else ""))
    visit(page,"library")
    selector=page.locator("#scope")
    factory_option=next((item for item in selector.locator("option").all_text_contents() if "factory" in item.lower()),None)
    check(factory_option,"Catalog needs a factory filter")
    selector.select_option(label=factory_option)
    actual=page.locator('#results a[href^="#cc/"]').evaluate_all("as=>as.map(a=>a.hash.slice(4))")
    check(set(actual)==capability_ids and len(actual)==6,"Factory catalog filter includes non-factory jobs")
    wording(page.locator("#results").text_content(),"filtered catalog")
    for cid,pid in operations:
        cc,component=caps[cid],parts[pid]
        check(cid==pid,"Factory CC and component routes should share the capability identity: "+pid)
        prefix,slug=pid.split(".",1)
        prior=prefix+".build_"+slug
        check(data["aliases"].get(prior)==cid,"Missing prior build ID "+prior)
        for route in ["cc/"+prior,"cc/"+cc["legacy"],"cc/"+cid]:
            visit(page,route)
            body=page.locator("main").text_content()
            wording(body,route)
            check(cc["summary"] in body and component["inputs"] in body and component["outputs"] in body,
                  "Factory operation must identify its inputs, receipt and remit on "+route)
            heads=page.locator("main h2").all_text_contents()
            check("Invocation" in heads and "Acceptance evidence" in heads,
                  "Factory invocation and acceptance headings missing on "+route)
            check("Components built" not in body,"Factory CC detail exposes an engine build section on "+route)
        for route in ["evidence/"+prior,"evidence/"+cc["legacy"]]:
            visit(page,route)
            check(page.locator('main a[href^="https://"]').count()>0,"Missing factory evidence for "+route)
        visit(page,"component/"+pid)
        main=page.locator("main")
        wording(main.text_content(),"component/"+pid)
        check("Factory capability" in main.locator("h2").all_text_contents() and "Built by" not in main.locator("h2").all_text_contents(),"Factory interface uses a build relationship")
        check(main.locator(f'a[href="#cc/{cid}"]').count()>0,"Factory component cannot open its capability")
        check(component["inputs"] in main.text_content() and component["outputs"] in main.text_content(),
              "Factory interface drops input or output receipt: "+pid)
    for j in data["jobs"]:
        assigned=[cid for cid,_ in j["assignments"] if cid in capability_ids]
        if assigned:
            visit(page,"construction/"+j["id"])
            work=page.locator("#work-order")
            wording(work.text_content(),"construction/"+j["id"])
            for cid in assigned:
                label=work.locator(f'article:has(a[href="#cc/{cid}"])').first
                check("Invoke factory capability" in label.text_content() and "Build CC" not in label.text_content(),j["id"]+" presents a factory capability as a build CC")
    for route in ["factory","integration","integration/coverage"]:
        visit(page,route)
        wording(page.locator("main").text_content(),route)
    visit(page,"assemblies")
    page.get_by_role("link",name="Engine implementation and acceptance").click()
    check(page.evaluate("location.hash")== "#readiness","Engine map must open readiness review")
    main=page.locator("main")
    check("readiness" in main.locator("h1").inner_text().lower(),"Readiness route needs a dedicated review")
    for title in ["Pack to next token","Library reuse and engine-owned code","Evidence still required"]:
        expect(main.get_by_role("heading",name=title,exact=True)).to_be_visible()
    gates=main.locator("details.insight")
    check(gates.count()>=4,"Engine review lost its component acceptance gates")
    for gate in gates.all():
        check(gate.locator('a[href^="#component/"]').count() and gate.locator('a[href^="#construction/"]').count()
              and "Acceptance evidence" in gate.text_content(),"Readiness gate is missing an owner, assigned order, or evidence")

def link_targets(locator):
    return set(locator.locator('a[href^="#"]').evaluate_all("as=>as.map(a=>a.hash)"))


def exact_fact(container, label, value, route):
    fact=container.locator(".fact").filter(has=container.page.get_by_text(label,exact=True))
    check(fact.count()==1,f"Expected one {label} field on {route}")
    expect(fact).to_have_text(label+value)


def semantic_records(page, data):
    main=page.locator("main")
    ccs={cc["id"]:cc for cc in data["ccs"]}
    parts={part["id"]:part for part in data["components"]}
    mappings=dict(data["builds"]+data["factoryCapabilities"])
    owners={pid:ccs[cid] for cid,pid in mappings.items()}
    sources={}
    for lane in ["memory","runtime","factory"]:
        sources.update(json.loads((SOURCE/(lane+".json")).read_text("utf-8-sig")))
    for key,record in EDITION["components"].items():
        sources[key]={**record["builder"]}
    operating={cid:cc for cid,cc in ccs.items() if cc["ccKind"] in ("tool","analysis")}
    check(len(sources)==len(ccs)-len(operating)==42 and len(ccs)==N_CCS and len(parts)==N_COMPONENTS,"Unexpected semantic record inventory")
    for cid,cc in ccs.items():
        if cid in operating:
            continue
        record=sources[cc["legacy"]]
        part=parts[mappings[cid]]
        check(cc["name"]==record["title"] and cc["summary"]==record["deliverable"] and
              cc["connection"]==record["integration"] and
              cc["evidence"]==record["evidence"],"CC source content changed in the build: "+cid)
        check(part["summary"]==record["behavior"] and part["consumer"]==record["consumer"],
              "Component source content changed in the build: "+part["id"])
        check(cc["summary"]!=part["summary"] and cc["summary"]!=cc["evidence"],
              "Code or artifact, operating behavior and evidence must be distinct: "+cid)
        for key in dict.fromkeys([cid,cc["legacy"]]):
            route="cc/"+key
            visit(page,route)
            factory=cc["kind"]=="factory"
            expect(main.locator("h1")).to_have_text(record["title"])
            if not factory:
                check(cc["name"]==part["name"]+" builder","Worker title must name the component it delivers")
                exact_fact(main,"What the component must do",record["requirement"],route)
                exact_fact(main,"Choices set by the contract",record["contractChoices"],route)
            exact_fact(main.locator("[data-delivery]"),
                       "Artifact delivered on invocation" if factory else "Code delivered",
                       record["deliverable"],route)
            exact_fact(main,"Where it runs" if factory else "Connect the implementation",record["integration"],route)
            exact_fact(main,"How the artifact is used" if factory else "What this code does",record["behavior"],route)
            exact_fact(main,"Consumer",record["consumer"],route)
            exact_fact(main,"Check",record["evidence"],route)
            check("#component/"+part["id"] in link_targets(main),"CC has no component link: "+route)
    for pid,part in parts.items():
        route="component/"+pid
        visit(page,route)
        expect(main.locator("h1")).to_have_text(part["name"])
        if part["scope"]=="Host":
            exact_fact(main,"Platform service",part["summary"],route)
            expect(main.get_by_role("heading",name="Platform acceptance evidence",exact=True)).to_be_visible()
            check(part["evidence"] in main.text_content(),"Missing platform evidence: "+pid)
            check(not any(h.startswith("#cc/") and ccs.get(h[4:],{}).get("ccKind") in ("builder","factory") for h in link_targets(main)),
                  "Platform service should have no builder or factory CC: "+pid)
            continue
        if part["scope"]=="Factory":
            exact_fact(main,"Artifact delivered on invocation",owners[pid]["summary"],route)
            exact_fact(main,"How it is used",part["summary"],route)
        else:
            exact_fact(main,"What this code does",part["summary"],route)
        check(part["consumer"] in main.text_content(),"Component consumer is missing: "+pid)
        exact_fact(main.locator("#inspector"),"Consumes",part["inputs"],route)
        exact_fact(main.locator("#inspector"),"Provides",part["outputs"],route)


def semantic_paths(page, data, url):
    main=page.locator("main")
    examples=[
        ("state","memory.sequence_kv","state/append"),
        ("storage","engine.expert_streaming","state/fill"),
        ("routing","model.expert_ffn","model/expert"),
        ("contract","compiler.engine_contract","f_spec/freeze"),
    ]
    ccs={cc["legacy"]:cc for cc in data["ccs"]}
    mappings=dict(data["builds"]+data["factoryCapabilities"])
    for job,legacy,action in examples:
        cc=ccs[legacy]
        cid=cc["id"]
        pid=mappings[cid]
        visit(page,"construction/"+job)
        assignment=main.locator(f'[data-cc="{cid}"]')
        assignment.locator(f'a[href="#cc/{cid}"]').click()
        expect(page).to_have_url(url+"#cc/"+cid)
        main.locator(f'a[href="#component/{pid}"]').first.click()
        expect(page).to_have_url(url+"#component/"+pid)
        main.locator(f'a[href="#action/{action}"]').first.click()
        expect(page).to_have_url(url+"#action/"+action)
        visit(page,"cc/"+legacy)
        expect(main.locator("h1")).to_have_text(cc["name"])
        visit(page,"evidence/"+legacy)
        check(main.locator('a[href^="https://"]').count()>0,"Original evidence alias fails: "+legacy)


def paired_views(page, data, url):
    factories={part:cc for cc,part in data["factoryCapabilities"]}
    targets={cc:part for cc,part in data["builds"]+data["factoryCapabilities"]}
    ccs={cc["id"]:cc for cc in data["ccs"]}
    parts={part["id"]:part for part in data["components"]}
    action_ids={act["id"] for act in data["actions"]}
    shells=["engine","factory"]
    for shell in shells:
        visit(page,"assemblies" if shell=="engine" else shell)
        page.locator(f'main a[href="#{shell}/actions"]').first.click()
        expect(page).to_have_url(url+"#"+shell+"/actions")
        expected={aid for aid in action_ids if aid.startswith("f_")==(shell=="factory")}
        rows=page.locator("[data-action-id]")
        observed=rows.evaluate_all("es=>es.map(e=>[e.dataset.actionId,Array.from(e.querySelectorAll('a'),a=>a.hash)])")
        check(len(observed)==len(expected) and {x[0] for x in observed}==expected,"Action coverage on "+shell)
        for aid,links in observed:
            performers={part for part,served in data["serves"] if served==aid}
            for part in performers:
                if shell=="factory":
                    check("#cc/"+factories[part] in links, f"Missing operating capability on {aid}")
                else:
                    check("#component/"+part in links, f"Missing {part} in action row {aid}")
            check("#action/"+aid in links, f"Missing deep link for {aid}")
        page.locator(f'main a[href="#{shell}"]').first.click()
        expect(page).to_have_url(url+"#"+shell)
    visit(page,"engine/actions")
    search=page.locator("#action-search")
    search.fill("diagnostics")
    matching=page.locator('[data-action-id="interface/diagnostics"]')
    expect(matching).to_be_visible()
    expect(page.locator('[data-action-id="model/route"]')).not_to_be_visible()
    matching.locator('a[href="#action/interface/diagnostics"]').click()
    page.locator("#page-back").click()
    expect(search).to_have_value("diagnostics")
    visit(page,"assemblies")
    panels=page.locator(".asm-card > details.expand-assembly")
    check(panels.count()==6,"Overview needs six inline disclosures")
    for level in ["components","actions","overview"]:
        page.locator(f'button[data-level="{level}"]').click()
        opened=page.locator("details[data-expand][open]").count()
        total=page.locator("details[data-expand]").count()
        check((level=="overview" and opened==0) or (level=="components" and 6<=opened<total) or
              (level=="actions" and opened==total),"Incorrect global detail level "+level)
    # Check all six in isolation, then open a CC and require Back to restore its parent.
    for panel in panels.all():
        panel.locator("summary").first.click()
        check(panel.get_attribute("open") is not None,"Assembly failed to expand")
        links=link_targets(panel)
        for prefix in ["#component/","#cc/","#action/"]:
            check(any(h.startswith(prefix) for h in links),"Inline disclosure lacks "+prefix)
        panel.locator("summary").first.click()
    members=page.locator("[data-member]").evaluate_all("es=>es.map(e=>[e.dataset.member,[...e.querySelectorAll('a')].map(a=>a.hash)])")
    for part,links in members:
        expected={"#component/"+part}
        expected.update("#cc/"+cc for cc,pid in data["builds"] if pid==part)
        expected.update("#action/"+act for pid,act in data["serves"] if pid==part)
        check(expected.issubset(links),"Incomplete inline assembly mapping for "+part)
    panel=panels.first
    panel.locator("summary").first.click()
    first_cc=panel.locator('a[href^="#cc/"]').first
    first_cc.evaluate("""el=>{let n=el.parentElement;const path=[];
      while(n){if(n.tagName==="DETAILS"&&!n.open)path.push(n);n=n.parentElement;}
      for(const p of path.reverse())p.querySelector("summary").click();}""")
    first_cc.click()
    page.locator("#page-back").click()
    expect(panels.first).to_have_attribute("open","")
    # Every work order stays reachable in both modes, with canonical assignments and receipts.
    quoted={
        "weights":("Checkpoint reader","Index the checkpoint"),
        "serving":("Engine image gateway and request pipeline","Build the image interface"),
        "reference":("Reference decoder block","Build a reference decoder block"),
        "routing":("Routed expert block","Implement the routed FFN"),
    }
    for variant in ["","/actions"]:
        base="construction"+variant
        visit(page,base)
        menu=link_targets(page.locator("main"))
        for j in data["jobs"]:
            path=base+"/"+j["id"]
            check("#"+path in menu,"Job unavailable from "+base+": "+j["id"])
            visit(page,path)
            detail=page.locator("#work-order")
            check(j["output"]!=j["evidence"],"Job artifact repeats acceptance evidence on "+path)
            for label,key in [("Engineering handoff","output"),("Acceptance evidence","evidence")]:
                heading=detail.get_by_role("heading",name=label,exact=True)
                expect(heading.locator("xpath=..").locator("p")).to_have_text(j[key])
            links=link_targets(detail)
            for cid,mode in j["assignments"]:
                check("#component/"+targets[cid] in links and "#cc/"+cid in links,
                      "Missing assignment on "+path+": "+cid)
                factory=cid in factories.values()
                assignment_mode="invoke" if factory else mode
                item=detail.locator(f'[data-cc="{cid}"][data-assignment-mode="{assignment_mode}"]')
                check(item.count()==1,"Wrong assignment mode on "+path+": "+cid)
                if mode=="use" and not factory:
                    exact_fact(item,"Existing interface used",parts[targets[cid]]["summary"],path)
                else:
                    label="Artifact delivered on invocation" if factory else "Code delivered"
                    exact_fact(item,label,ccs[cid]["summary"],path)
            counterpart="construction"+("" if variant else "/actions")+"/"+j["id"]
            check("#"+counterpart in link_targets(page.locator("main")),"Switch loses job identity on "+path)
            if j["id"] in quoted:
                label=quoted[j["id"]][bool(variant)]
                expect(detail.get_by_role("heading",level=1,name=label,exact=True)).to_be_visible()
        # Check an actual toggle without navigating by programmatic hash.
        sample="construction"+variant+"/routing"
        visit(page,sample)
        swap="construction"+("" if variant else "/actions")+"/routing"
        page.locator(f'main a[href="#{swap}"]').first.click()
        expect(page).to_have_url(url+"#"+swap)

def edition_checks(page, data, url, html):
    """Kinds, tool and analysis CCs, measured evidence, sources, capsule map and renamed worker (20261120)."""
    main=page.locator("main")
    ccs={c["id"]:c for c in data["ccs"]}
    parts={c["id"]:c for c in data["components"]}
    root=Path(html).resolve().parent
    # Naming rules for each kind.
    builder_targets=dict(data["builds"])
    for cid,cc in ccs.items():
        kind=cc["ccKind"]
        if kind=="builder":
            check(cc["name"]==parts[builder_targets[cid]]["name"]+" builder","Builder name rule: "+cid)
        else:
            check(not cc["name"].endswith(" builder"),"Only builder CCs may end in 'builder': "+cid)
        if kind=="analysis":
            check(cc["name"].endswith(" analysis"),"Analysis name rule: "+cid)
    # Catalog: legend, one filter per kind and a badge on every card.
    visit(page,"library")
    legend=page.locator(".kind-legend [data-kind-legend]")
    check(legend.count()==4,"Catalog needs a four-kind legend")
    for kind,n in KIND_COUNTS.items():
        expect(page.locator(f'.kind-legend [data-kind-legend="{kind}"]')).to_contain_text(f"{n} CCs")
    options=page.locator("#scope option").evaluate_all("os=>os.map(o=>[o.value,o.textContent])")
    check([v for v,_ in options]==["","builder","tool","analysis","factory"],"Catalog kind filter options changed")
    for value,label in options:
        page.locator("#scope").select_option(value=value)
        listed=page.locator('#results a[href^="#cc/"]').evaluate_all("as=>as.map(a=>[a.hash.slice(4),a.dataset.ccKind,a.querySelector('.kind-badge')?.textContent])")
        expected={cid for cid,cc in ccs.items() if not value or cc["ccKind"]==value}
        check({x[0] for x in listed}==expected,"Kind filter mismatch for "+label)
        for cid,kind,badge in listed:
            check(kind==ccs[cid]["ccKind"] and badge==data["kinds"][kind]["label"],"Card badge mismatch "+cid)
    page.locator("#scope").select_option(value="")
    page.locator("#search").fill("image builder")
    check(page.locator('#results a[href="#cc/factory.image_builder"]').count()==1,"Former name search fails")
    page.locator("#search").fill("expert_weight_cache")
    check(page.locator('#results a[href="#cc/engine.build_expert_weight_cache"]').count()==1,"Capsule directory search fails")
    page.locator("#search").fill("")
    table=page.locator("#capsule-map tr[data-capsule]")
    check(table.count()==len(data["capsuleMap"]),"Capsule map rows")
    dirs=set(table.evaluate_all("rs=>rs.map(r=>r.dataset.capsule)"))
    for d in ["expert_weight_cache","weight_placement_planner","expert_demand_predictor","batch_layout_mapper","observability_event_recorder"]:
        check(d in dirs,"Capsule map lacks "+d)
    # UI legend wording and the JiuwenSwarm capsule catalog.
    for kind,(label,plain) in UI_LEGEND.items():
        item=page.locator(f'.kind-legend [data-kind-legend="{kind}"]')
        check(item.locator(".kind-badge").inner_text()==label,"Legend label differs from UI: "+kind)
        check(item.locator("[data-kind-plain]").inner_text()==plain,"Legend wording differs from UI: "+kind)
        expect(item).to_contain_text(f"{CAPSULE_COUNTS[kind]} capsules")
    rows=page.locator("#capsule-catalog tr[data-catalog-dir]").evaluate_all(
        "rs=>rs.map(r=>({dir:r.dataset.catalogDir,kind:r.dataset.catalogKind,title:r.querySelector('[data-catalog-title]').textContent,"
        "cc:[...r.querySelectorAll('a[href^=\"#cc/\"]')].map(a=>a.hash.slice(4))}))")
    check(len(rows)==63 and len({r["dir"] for r in rows})==63,"Capsule catalog must list 63 directories")
    check({k:sum(r["kind"]==k for r in rows) for k in CAPSULE_COUNTS}==CAPSULE_COUNTS,"Capsule catalog kind counts")
    by_dir={r["dir"]:r for r in data["capsuleCatalog"]}
    linked=set()
    for r in rows:
        src=by_dir[r["dir"]]
        check(r["title"]==src["title"] and r["kind"]==src["kind"],"Catalog row differs from atlas-names: "+r["dir"])
        check(r["cc"]==([src["atlas"]] if src["atlas"] else []),"Catalog atlas link: "+r["dir"])
        for cid in r["cc"]:
            check(ccs[cid]["name"]==r["title"] and ccs[cid]["ccKind"]==r["kind"],"Atlas CC title or kind differs from capsule: "+cid)
            linked.add(cid)
    check(linked=={r["atlas"] for r in data["capsuleMap"]},"Capsule map and catalog disagree")
    expect(page.locator("#capsule-catalog [data-catalog-counts]")).to_contain_text(f"{N_CCS} atlas CCs · 63 capsule directories")
    # Spark campaign view.
    visit(page,"endpoint/campaign")
    counts=dict(page.locator("[data-campaign-counts] div").evaluate_all("ds=>ds.map(d=>[d.querySelector('strong').textContent,d.querySelector('span').textContent])"))
    check(counts==CAMPAIGN_COUNTS,"Campaign counts: "+str(counts))
    expect(main.locator("[data-campaign-contrast]")).to_contain_text("Satay (Jetson) demo applied one engine CC")
    for b in data["campaign"]["builders"]:
        row=main.locator(f'[data-campaign-builders] tr[data-campaign-cc="{b["cc"]}"]')
        check(row.count()==1,"Campaign lacks builder "+b["cc"])
        expect(row).to_contain_text(data["measured"]["components"][b["component"]]["status"])
        check(row.locator(f'a[href="{b["link"]}"]').count()==1 and (root/b["link"]).is_file(),"Campaign report link "+b["link"])
    check(main.locator("[data-campaign-builders] tr[data-campaign-cc]").count()==5,"Campaign lists five builder CCs")
    expect(main.locator("[data-campaign-combined]")).to_contain_text("Null · screening")
    for text in ["61,440 MiB","27.08 s at 512 tokens and 92.07 s at 2048 tokens","20/20 pairs","near parity","cold-start win",
                 "iteration 1: slower","1,360 of 1,360","96 unused prefetches","not the mapper"]:
        expect(main.locator("[data-campaign-builders]")).to_contain_text(text)
    check(main.locator("[data-campaign-operating] tr[data-campaign-cc]").count()==len(data["campaign"]["operating"]),"Campaign tool and analysis rows")
    for href in main.locator('a[href^="evidence/"]').evaluate_all("as=>as.map(a=>a.getAttribute('href'))"):
        check((root/href).is_file(),"Campaign evidence link broken: "+href)
    # Tool and analysis CC pages.
    for cid,cc in ccs.items():
        if cc["ccKind"] not in ("tool","analysis"):
            continue
        for key in [cid]+[k for k,v in data["aliases"].items() if v==cid]:
            visit(page,"cc/"+key)
            expect(main.locator("h1")).to_have_text(cc["name"])
            expect(main.locator(".tagline .kind-badge")).to_have_text(data["kinds"][cc["ccKind"]]["label"])
            exact_fact(main.locator("[data-delivery]"),"Receipt delivered" if cc["ccKind"]=="tool" else "Findings delivered",cc["summary"],key)
            exact_fact(main,"Verifier",cc["verifier"],key)
            links=link_targets(main)
            for part in cc["operates"]:
                check("#component/"+part in links,"Operating CC lacks component link: "+cid+" -> "+part)
            for f in cc["findings"]:
                check(main.locator(f'a[href="{f["link"]}"]').count()>0 and (root/f["link"]).is_file(),"Finding link broken: "+f["link"])
        for part in cc["operates"]:
            visit(page,"component/"+part)
            check(main.locator(f'[data-operators] a[href="#cc/{cid}"]').count()>0,"Component lacks operating CC "+cid)
    # Measured evidence on component, builder and endpoint pages, linked to local copies.
    measured=data["measured"]["components"]
    check(len(measured)==5,"Expected measured evidence for five components")
    for pid,record in measured.items():
        for route in ["component/"+pid]+["cc/"+c for c,p in data["builds"] if p==pid]:
            visit(page,route)
            block=main.locator(f'[data-measured="{pid}"]')
            check(block.count()==1,"Measured evidence missing on "+route)
            expect(block).to_contain_text(record["status"])
            for row in record["rows"]:
                check(block.locator(f'a[href="{row["link"]}"]').count()>0 and (root/row["link"]).is_file(),"Measured link broken: "+row["link"])
                expect(block).to_contain_text(row["result"])
    visit(page,"endpoint/measured")
    check(main.locator('article[data-measured]').count()==5,"Measured overview lists five components")
    expect(main).to_contain_text("27.08 s saved at 512 tokens and 92.07 s at 2048 tokens")
    # New components: endpoint subcomponent, Strata sources and builders.
    for pid in ["backend.quantized_matmul_kernel","backend.cpu_weight_repack","weights.engram_row_cache","engine.host_expert_store"]:
        visit(page,"component/"+pid)
        sources=main.locator("[data-sources]")
        check(sources.count()==1 and sources.locator('a[href*="github.com/ggml-org/llama.cpp/blob/9048bad8"]').count()>0,"Missing llama.cpp source on "+pid)
        check(sources.locator('a[href*="github.com/Muxite/Strata/blob/ffa80d73"]').count()>0,"Missing Strata source on "+pid)
    # Renamed factory worker keeps its IDs and shows its former name.
    for route in ["cc/factory.image_builder","cc/factory.builder","cc/factory.build_image_builder","component/factory.image_builder"]:
        visit(page,route)
        expect(main.locator("h1")).to_have_text("Image assembler")
        expect(main.locator("[data-former]")).to_contain_text("Image builder")
    for route in ["factory","integration","integration/coverage","construction/image"]:
        visit(page,route)
        check("Image builder" not in main.text_content(),"Old worker name still shown on "+route)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", nargs="?", type=Path,
                        default=SOURCE.parent / (SOURCE.parent.name + ".html"))
    parser.add_argument("--original", type=Path, default=ORIGINAL)
    parser.add_argument("--browser", type=Path, default=EDGE if EDGE.exists() else None)
    args = parser.parse_args()
    for path in [args.html, args.original]:
        check(path.is_file(), f"Missing atlas: {path}")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=str(args.browser) if args.browser else None)
        ctx = browser.new_context(viewport={"width":1440,"height":900}, offline=True,
                                  reduced_motion="reduce")
        old, page = ctx.new_page(), ctx.new_page()
        errors, requests = [], []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on("request", lambda req: requests.append(req.url) if req.url.startswith(("https:","http:")) else None)
        old.goto(args.original.resolve().as_uri()+"#engine")
        url = args.html.resolve().as_uri()
        page.goto(url+"#engine")
        page.set_default_timeout(6000)
        check(old.locator("header nav a").all_inner_texts()==TABS,"Original tab names differ")
        check(page.locator("header nav a").all_inner_texts()==TABS,"Eight original tabs must appear in order")
        for width,height in [(1440,900),(390,844)]:
            for tab in [old,page]:
                tab.set_viewport_size({"width":width,"height":height})
            actual, baseline=page.evaluate(HEADER),old.evaluate(HEADER)
            check(actual==baseline, f"Header style or geometry at {width}px: "+
                  str([(a,b) for a,b in zip(actual,baseline) if a!=b][:1]))
        old.close()
        page.set_viewport_size({"width":1440,"height":900})
        data=json.loads(page.locator("#records").text_content())
        ccs={c["id"]:c for c in data["ccs"]}
        comps={c["id"]:c for c in data["components"]}
        acts={a["id"]:a for a in data["actions"]}
        check(len(ccs)==N_CCS and len(acts)==N_ACTIONS and len(data["jobs"])==N_JOBS and len(comps)==N_COMPONENTS,"Unexpected inventory")
        check({k:sum(c["ccKind"]==k for c in ccs.values()) for k in KIND_COUNTS}==KIND_COUNTS,"Unexpected CC kind counts")
        urls=lambda loc: loc.evaluate_all("(as)=>as.map(a=>a.getAttribute('href'))")
        def node(id):
            return page.locator(f'svg [data-ax-id="{id}"]').first
        overview_and_paths(page,url)
        factory_capabilities(page,data)
        paired_views(page,data,url)
        semantic_records(page,data)
        semantic_paths(page,data,url)
        edition_checks(page,data,url,args.html)
        visit(page,"factory")
        target=node("factory.image_builder")
        expect(target).to_be_visible()
        target.click()
        expect(page).to_have_url(url+"#component/factory.image_builder")
        check(comps["factory.image_builder"]["summary"] in page.locator("main").text_content(),
              "Factory component drilldown")
        visit(page,"assembly/weights")
        reader_link=page.locator('main a[href="#component/weights.checkpoint_reader"]').first
        reader_link.focus()
        page.keyboard.press("Enter")
        expect(page).to_have_url(url+"#component/weights.checkpoint_reader")
        reader=next(c for c in data["ccs"] if c["legacy"]=="weights.load_checkpoint")
        page.locator(f'main a[href="#cc/{reader["id"]}"]').first.click()
        expect(page).to_have_url(url+"#cc/"+reader["id"])
        visit(page,"component/weights.checkpoint_reader")
        page.locator('main a[href="#action/state/weight"]').first.click()
        expect(page).to_have_url(url+"#action/state/weight")
        check(all(c in page.locator("main").text_content() for c in ["Checkpoint reader","Weight placement planner"]),
              "Shared action lost a component")
        visit(page,"library")
        listed=urls(page.locator('#results a[href^="#cc/"]'))
        check(set(listed)=={"#cc/"+k for k in ccs}, "Catalog list differs from CC inventory")
        for c in ccs.values():
            card=page.locator(f'#results a[href="#cc/{c["id"]}"]').first
            if c["kind"]=="engine":
                check(c["requirement"] in card.text_content(),"Missing worker responsibility on catalog card")
            check(c["summary"] in card.text_content(),f"Catalog summary {c['id']}")
        search=page.locator("#search")
        search.fill("checkpoint reader")
        entry=page.locator(f'#results a[href="#cc/{reader["id"]}"]').first
        expect(entry).to_be_visible()
        entry.click()
        expect(page).to_have_url(url+"#cc/"+reader["id"])
        page.locator('#page-back').click()
        expect(search).to_have_value("checkpoint reader")
        page.goto(url+"#action/model/route")
        page.reload()
        expect(page.locator("main")).to_contain_text(acts["model/route"]["detail"])
        visit(page,"integration/coverage")
        body=page.locator("main").text_content()
        for c in ccs.values():
            check(c["summary"] in body,"Coverage summary "+c["id"])
        for c in ccs.values():
            for id in [c["legacy"],c["id"]]:
                visit(page,"cc/"+id)
                check(c["summary"] in page.locator("main").text_content(),"CC route "+id)
            visit(page,"evidence/"+c["id"])
            check(page.locator('main a[href^="https://"]').count()>0,"Evidence route "+c["id"])
        for c in comps.values():
            visit(page,"component/"+c["id"])
            check(c["summary"] in page.locator("main").text_content(),"Component route "+c["id"])
        for a in acts.values():
            visit(page,"action/"+a["id"])
            txt=page.locator("main").text_content()
            check(a["title"] in txt and a["detail"] in txt,"Action route "+a["id"])
        for route,selector,count in [
            ("construction/designs",".comparison-group",4),("construction/trials",".spark-trial",8),
            ("quantization",".quant-steps article",5),("sources","table.matrix",1),
            ("integration",".integration-flow",1),("construction","#ready-jobs",1)
        ]:
            visit(page,route)
            check(page.locator(selector).count()==count,"Preserved view "+route)
        page.locator('#ready-jobs [data-accept="intent"]').click()
        expect(page.locator('#ready-jobs [data-accept="contract"]')).to_be_visible()
        visit(page,"integration")
        stage=page.locator('.integration-flow a[href="#integration/build"]')
        stage.click()
        expect(page.locator("#integration-detail")).to_contain_text("collected result")
        for width,height in [(390,844),(1440,900)]:
            page.set_viewport_size({"width":width,"height":height})
            for route in ["engine","factory","assembly/weights","assembly/decoder/layer/routed","connections",
                          "trace/token/0","trace/cold/0","readiness","component/model.expert_router","action/model/dispatch",
                          "cc/"+reader["id"],"library","integration/coverage","construction/serving",
                          "evidence/"+reader["id"],"construction/designs","construction/trials",
                          "integration","quantization","sources","engine/actions","factory/actions",
                          "construction/actions","construction/actions/routing","endpoint/campaign"]:
                visit(page,route)
                check(page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),
                      f"{width}px overflow on {route}")
        check(not errors,"Browser errors: "+str(errors))
        check(not requests,"Network requests while offline: "+str(requests))
        browser.close()
        kinds=", ".join(f"{n} {k}" for k,n in KIND_COUNTS.items())
        print(f"PASS: eight tabs, compact six-assembly overview, both traces, {N_HANDOFFS} handoffs, {len(comps)} components, "
              f"{len(ccs)} CCs ({kinds}), {len(acts)} actions, {len(data['jobs'])} work orders, "
              "CC kinds, measured evidence, capsule map, renamed worker, "
              "reference features, history, keyboard, mobile and offline rendering.")


if __name__ == "__main__":
    main()
