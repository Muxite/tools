"""Build the offline component atlas from the audited inference atlas and editorial records."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TITLE = HERE.parent.name
BASE = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent.parent / "20261117 Text Inference Engine Atlas prepresentation" / "src"
spec = importlib.util.spec_from_file_location("baseline", BASE / "build.py")
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)
atlas = baseline.assemble()

def read_json(name):
    return json.loads((HERE / name).read_text("utf-8-sig"))

def embedded(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")

groups = {
    "Weights and residency": "weights placement engine routing",
    "Request and generation": "serving tokenizer scheduler batch decode sampling",
    "Decoder and experts": "attention model dense merge sequence",
    "Execution and state": "backend graph memory parallel observability",
    "Factory": "compiler factory",
}
roles = {r["id"]: r for r in atlas["roles"]}
interfaces = {}
build_text = {}
for filename in ["memory.json", "runtime.json", "factory.json"]:
    lane = read_json(filename)
    assert not build_text.keys() & lane.keys()
    build_text.update(lane)
    entries = read_json(filename.replace(".json","_interfaces.json"))
    assert entries.keys() == lane.keys()
    interfaces.update(entries)
assert roles.keys() == build_text.keys()
ccs, components, builds, serves, actions = [], [], [], [], []
component_ids, cc_ids = {}, {}
factory_capabilities, previous_factory_ids = [], {}
for line in (HERE / "components.txt").read_text("utf-8-sig").splitlines():
    old, slug, name = line.split("|")
    record = build_text[old]
    r = roles[old]
    family = old.split(".")[0]
    component = f"{family}.{slug}"
    factory = r.get("kind") == "factory"
    fields = {"title","deliverable","integration","behavior","consumer","evidence"}
    if not factory:
        fields.update({"contractChoices","requirement"})
        assert record["title"] == name + " builder", old
    assert set(record) == fields and all(isinstance(v,str) and v.strip() for v in record.values()), old
    cc = component if factory else f"{family}.build_{slug}"
    if factory:
        previous_factory_ids[f"{family}.build_{slug}"] = cc
    component_ids[old], cc_ids[old] = component, cc
    group = next(k for k, v in groups.items() if family in v.split())
    scope = "Factory" if r.get("kind") == "factory" else "Engine" if r["target"] else "Extension"
    components.append(dict(id=component,name=name,summary=record["behavior"],consumer=record["consumer"],
                           group=group,scope=scope,primary=r["review"]["site"],inputs=interfaces[old]["inputs"],
                           outputs=interfaces[old]["outputs"],when=r["when"],boundary=r["review"]["boundary"]))
    ccs.append(dict(id=cc,name=record["title"],kind="factory" if factory else "engine",summary=record["deliverable"],legacy=old,
                    requirement=record.get("requirement"),contractChoices=record.get("contractChoices"),connection=record["integration"],evidence=record["evidence"],
                    **{k:r[k] for k in ("contents","check","decisions","integration","greenfield","handoff","examples","essential")}))
    (factory_capabilities if factory else builds).append([cc,component])
assert len(roles) == len(set(component_ids.values())) == len(set(cc_ids.values())) == 38
for cc in ccs:
    cc["ccKind"] = "factory" if cc["kind"] == "factory" else "builder"
edition = read_json("edition.json")
host_providers = {
    "hostcpu": ("Host CPU and OS scheduler","The CPU and operating system schedule host threads and execute CPU work."),
    "device": ("Accelerator","The accelerator executes the kernels submitted by the engine."),
    "dram": ("Memory subsystem","The memory subsystem carries data between physical memory and compute units."),
    "ssd": ("Storage subsystem","The storage subsystem supplies checkpoint byte ranges on demand."),
}
host_interfaces = read_json("host_interfaces.json")
assert set(host_interfaces) == {"host."+k for k in host_providers}
connections = list(atlas["cross"])
for layer in atlas["engine"] + atlas["factory"]:
    connections.extend([f"{layer['id']}/{s}",f"{layer['id']}/{t}",label] for s,t,label,*_ in layer["edges"])
    for op in layer["ops"]:
        action = f"{layer['id']}/{op['id']}"
        actions.append(dict(id=action,layer=layer["title"],**{k:op[k] for k in ["title","detail","check","metric","target"]}))
        if not op["cc"]:
            assert layer["id"] == "host"
            name, summary = host_providers[op["id"]]
            host = "host." + op["id"]
            components.append(dict(id=host,name=name,summary=summary,group="Host platform",scope="Host",
                                   **host_interfaces[host], primary=action,when="Supplied by the deployment platform.",boundary=op["detail"]))
            serves.append([host,action])
        serves.extend([component_ids[key],action] for key in op["cc"])
assert len({a["id"] for a in actions}) == len(actions) == 101
action_ids = {a["id"] for a in actions}
endpoint_source = (HERE / "endpoint-data.js").read_text("utf-8")
endpoint = json.loads(endpoint_source[endpoint_source.index("{"):endpoint_source.rindex("}") + 1])
endpoint_children = {legacy: child for parent in endpoint["parents"] for child in parent["children"] for legacy in child["legacyIds"]}
pins = edition["pins"]
EDITION_ROOT = HERE.parent

def source_url(repo, ref):
    if repo == "evidence":
        assert (EDITION_ROOT / ref["path"]).is_file(), ref
        return ref["path"]
    pin = pins[repo]
    return f"{pin['repo']}/blob/{pin['commit']}/{ref['path']}#L{ref['line']}"

def source_examples(child):
    rows = [("llama.cpp", ref) for ref in [child.get("source"), *child.get("additionalSources", [])] if ref]
    rows += [("Strata", ref) for ref in child.get("strataSources", [])]
    examples = [dict(engine=repo, title=ref["path"] + " · " + ref["symbol"], url=source_url(repo, ref),
                     detail=ref.get("note") or child.get("llamaStatus") or child["action"]) for repo, ref in rows]
    examples += [dict(engine="Evidence copy", title=ref["label"], url=source_url("evidence", ref), detail=ref["note"])
                 for ref in child.get("localSources", [])]
    return examples

# Components added in the 20261120 edition. Each has a builder CC named "<Component> builder".
for old, rec in edition["components"].items():
    family = old.split(".")[0]
    component, cc = f"{family}.{rec['slug']}", f"{family}.build_{rec['slug']}"
    b, role = rec["builder"], rec["role"]
    assert b["title"] == rec["name"] + " builder" and old not in roles and rec["serves"][0] in action_ids, old
    assert set(rec["serves"]) <= action_ids and rec["scope"] in {"Engine", "Extension"}
    group = next(k for k, v in groups.items() if family in v.split())
    components.append(dict(id=component, name=rec["name"], summary=b["behavior"], consumer=b["consumer"], group=group,
                           scope=rec["scope"], primary=rec["serves"][0], inputs=rec["inputs"], outputs=rec["outputs"],
                           when=rec["when"], boundary=rec["boundary"], added="20261120"))
    child = endpoint_children[component]
    assert cc in child["builderIds"], component
    ccs.append(dict(id=cc, name=b["title"], kind="engine", ccKind="builder", summary=b["deliverable"], legacy=old,
                    requirement=b["requirement"], contractChoices=b["contractChoices"], connection=b["integration"],
                    evidence=b["evidence"], contents=role["contents"], check=role["check"], decisions=role["decisions"],
                    integration=role["existing"], greenfield=role["greenfield"], handoff=role["handoff"],
                    examples=source_examples(child), essential=role["essential"], added="20261120"))
    builds.append([cc, component])
    serves.extend([component, action] for action in rec["serves"])
    component_ids[old], cc_ids[old] = component, cc
# Strata and local evidence for existing endpoint subcomponents become source examples of their builders.
by_cc = {cc["id"]: cc for cc in ccs}
added_components = {c["id"] for c in components if c.get("added")}
for legacy, child in endpoint_children.items():
    if legacy in added_components or not (child.get("strataSources") or child.get("localSources")):
        continue
    for builder in child["builderIds"]:
        known = {x["url"] for x in by_cc[builder]["examples"]}
        for example in source_examples(child):
            if example["engine"] != "llama.cpp" and example["url"] not in known:
                by_cc[builder]["examples"].append(example)
                known.add(example["url"])
# Tool and analysis CCs operate on components; they deliver receipts or findings, not component code.
operates = []
component_index = {c["id"] for c in components}
for oc in edition["operatingCCs"]:
    assert oc["kind"] in {"tool", "analysis"} and oc["id"] not in by_cc
    assert (oc["kind"] == "analysis") == oc["name"].endswith(" analysis") and not oc["name"].endswith(" builder"), oc["name"]
    assert set(oc["operates"]) <= component_index, oc["id"]
    for finding in oc["findings"]:
        assert (EDITION_ROOT / finding["link"]).is_file(), finding
    examples = [dict(engine=ref["repo"] if ref["repo"] != "evidence" else "Evidence copy", title=ref["path"] + " · " + ref["symbol"],
                     url=source_url(ref["repo"], ref), detail=ref.get("note") or oc["method"]) for ref in oc["sources"]]
    examples += [dict(engine="Measured run", title=f["link"].rsplit("/", 1)[-1], url=f["link"], detail=f["text"]) for f in oc["findings"]]
    ccs.append(dict(oc, ccKind=oc["kind"], legacy=oc["id"], evidence=oc["verifier"], examples=examples, added="20261120"))
    operates.extend([oc["id"], part] for part in oc["operates"])
def renamed(value):
    """Apply edition renames to display text inherited from the original atlas."""
    if isinstance(value, str):
        for r in edition["renames"]:
            value = value.replace(r["from"], r["to"]).replace(r["from"].lower(), r["to"].lower())
        return value
    if isinstance(value, list):
        return [renamed(v) for v in value]
    if isinstance(value, dict):
        return {k: renamed(v) for k, v in value.items()}
    return value
ccs[:], components[:], actions[:] = renamed(ccs), renamed(components), renamed(actions)
for rename in edition["renames"]:
    for row in [next(c for c in ccs if c["id"] == rename["id"]), next(c for c in components if c["id"] == rename["id"])]:
        assert row["name"] == rename["to"], rename
        row["formerNames"] = [rename["from"]]
measured = edition["measured"]
for pid, record in measured["components"].items():
    assert pid in component_index and record["rows"], pid
    for row in record["rows"]:
        assert (EDITION_ROOT / row["link"]).is_file(), row["link"]
headlines = json.loads((EDITION_ROOT / "evidence" / "final-headlines.json").read_text("utf-8"))
assert {c["id"] for c in components} == {c for c,_ in serves}
assert {a["id"] for a in actions} == {a for _,a in serves}
assert len(builds) == 36 and len(factory_capabilities) == 6 and len(components) == 46
assert sum(cc["ccKind"] == "tool" for cc in ccs) == 5 and sum(cc["ccKind"] == "analysis" for cc in ccs) == 6
assets = [dict(a,assigned=cc_ids[a["assigned"]]) for a in atlas["assets"]]
script = (BASE/"construction_options.js").read_text("utf-8") + (BASE/"construction.js").read_text("utf-8").split("const jobIndex")[0]
script += "\nconsole.log(JSON.stringify({jobs:constructionJobs,gates:conditionalGates}))"
integration = (BASE / "integration.js").read_text("utf-8").split("function factoryCodeLink")[0]
integration += "\nconsole.log(JSON.stringify({pins:factoryPins,connections:factoryConnections}))"
references = json.loads(subprocess.check_output(["node","-"], input=integration.encode("utf-8")))
for cc in ccs:
    if cc["legacy"].startswith("compiler."):
        stage = next(row for row in references["connections"] if cc["legacy"] in row["cc"])
        for key,label,path in stage["refs"]:
            cc["examples"].append(dict(engine="Jiuwenswarm factory",title=label,detail=stage["existing"],
                                       url=f"https://github.com/Stellven/jiuwenswarm/blob/{references['pins'][key]}/{path}"))
orders = json.loads(subprocess.check_output(["node","-"],input=script.encode("utf-8")))
assignments = read_json("orders.json")
assert set(assignments) == {j["id"] for j in orders["jobs"]}
for job in orders["jobs"]:
    if job["id"] in {"intent","contract","plan"}:
        job["agent"] = {"intent":"Intent compiler","contract":"Contract compiler","plan":"Workflow orchestrator"}[job["id"]]
    mapping = assignments[job["id"]]
    assert mapping.keys() == set(job["cc"]) and set(mapping.values()) <= {"build","change","use"}
    job["assignments"] = [[cc_ids[k],mapping[k]] for k in job.pop("cc")]
from engine_orders import complete_engine_orders
complete_engine_orders(orders)
orders = renamed(orders)
handoffs = read_json("order_handoffs.json")
assert set(handoffs) == {j["id"] for j in orders["jobs"]}
for j in orders["jobs"]:
    receipt = handoffs[j["id"]]
    assert set(receipt) == {"deliverable","evidence"} and all(receipt.values())
    j.update(output=receipt["deliverable"],evidence=receipt["evidence"])
aliases = {**{k:cc_ids[v] for k,v in atlas["aliases"].items() if v in cc_ids},**cc_ids,**previous_factory_ids}
cc_index = {cc["id"] for cc in ccs}
for row in edition["capsuleMap"]:
    assert row["atlas"] in cc_index, row
    if row["capsuleId"] not in cc_index and row["capsuleId"] not in aliases:
        aliases[row["capsuleId"]] = row["atlas"]
# The JiuwenSwarm capsule catalog (demo UI atlas-names.json): same titles and kinds wherever a capsule carries an atlas CC.
catalog = edition["capsuleCatalog"]
by_cc = {cc["id"]: cc for cc in ccs}
assert len({r["dir"] for r in catalog}) == len(catalog) == 63
assert {k: sum(r["kind"] == k for r in catalog) for k in edition["kinds"]} == {"builder": 19, "tool": 11, "analysis": 22, "factory": 11}
for r in catalog:
    assert r["kind"] in edition["kinds"] and r["relates"] in component_index | {None}, r["dir"]
    assert (r["kind"] == "analysis") == r["title"].endswith(" analysis") and (r["kind"] == "builder") == r["title"].endswith(" builder"), r["title"]
    if r["atlas"]:
        cc = by_cc[r["atlas"]]
        assert cc["name"] == r["title"] and cc["ccKind"] == r["kind"], r["dir"]
mapped = {r["dir"]: r["atlas"] for r in catalog if r["atlas"]}
assert mapped == {r["dir"]: r["atlas"] for r in edition["capsuleMap"]}, "capsuleMap must match the catalog"
for cc in ccs:
    cap = cc.get("capsule") or {}
    assert not cap.get("dir") or mapped.get(cap["dir"]) == cc["id"], cc["id"]
campaign = edition["campaign"]
for row in campaign["builders"] + [campaign["combined"]]:
    assert (EDITION_ROOT / row["link"]).is_file(), row["link"]
for row in campaign["builders"]:
    assert [row["cc"], row["component"]] in builds and row["component"] in measured["components"], row
assert set(campaign["operating"]) <= {cc["id"] for cc in ccs if cc["ccKind"] in ("tool", "analysis")}
data = dict(capsuleCatalog=catalog,capsuleCatalogNote=edition["capsuleCatalogNote"],campaign=campaign,factoryCapabilities=factory_capabilities,components=components,ccs=ccs,builds=builds,serves=serves,actions=actions,cross=connections,assets=assets,**orders,
            aliases=aliases,operates=operates,kinds=edition["kinds"],kindNote=edition["common"],renames=edition["renames"],
            capsuleMap=edition["capsuleMap"],capsuleMapNote=edition["capsuleMapNote"],measured=measured,headlines=headlines,pins=pins,
            localReports=[f"evidence/reports/{p.name}" for p in sorted((EDITION_ROOT / "evidence" / "reports").glob("*.md"))])
from publish_layout import render_copy
page = render_copy(BASE,HERE,TITLE,data)
(HERE.parent / (TITLE+".html")).write_bytes(page.encode("utf-8"))
