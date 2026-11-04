"""Offline design validation. No registry access, execution, source edits or authority granted."""
import json
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from jsonschema import Draft202012Validator, ValidationError
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_bytes())
schema=read(ROOT/"contracts/cc.schema.json")
moe=read(ROOT/"contracts/moe.profile.schema.json")
for v in [schema,moe]:Draft202012Validator.check_schema(v)
validator=Draft202012Validator(schema)
known={moe["$id"]:moe}
def require(ok,msg):
    if not ok:raise ValueError(msg)
def unique(items,key):
    vals=[r[key] for r in items];require(len(vals)==len(set(vals)),"Duplicate "+key);return set(vals)
def check(d,tools=("moe.inspect-native-index",)):
    validator.validate(d)
    ids=unique(d["profiles"],"id")
    for p in d["profiles"]:
        if p["id"] not in known:
            require(not p["required"],"Unsupported required profile");continue
        path=ROOT/"contracts/moe.profile.schema.json"
        require(p["schema"]["sha256"]==sha256(path.read_bytes()).hexdigest(),"Profile schema bytes changed")
        Draft202012Validator(known[p["id"]]).validate(p["data"])
        if p["required"]:require(set(p["requires_tools"])<=set(tools),"Missing required profile reader")
    p=d["payload"]
    for g in p.get("acceptance",p.get("gates",[])):
        if g["operator"]!="equals":
            require(type(g["threshold"]) in (int,float),"Numeric gate requires numeric threshold")
        if g["operator"].startswith("ratio-"):
            require(g["threshold"]>=0,"Ratio threshold cannot be negative")
    if d["form"]=="change-request":
        gate_ids=unique(p["acceptance"],"id");unique(p["goals"],"id")
        unique(p["constraints"],"id");unique(p["change_intents"],"id");unique(p["open_questions"],"id")
        for g in p["goals"]:require(set(g["acceptance"])<=gate_ids,"Goal refers to absent gate")
        for c in p["change_intents"]:
            require(c["profile_id"] in ids,"Change refers to absent profile")
            profile=next(x for x in d["profiles"] if x["id"]==c["profile_id"])
            require(profile["required"],"Executable change depends on optional profile")
            if profile["id"]==moe["$id"]:require(profile["data"]["intent"]["mode"]==c["mode"],"Contradictory change mode")
    for rel in d["relations"]:
        target=rel["target"]
        if not target["uri"].startswith("fixture:"):
            path=(ROOT/"examples"/target["uri"]).resolve()
            require(path.parent== (ROOT/"examples").resolve(),"Nonlocal example ref")
            require(path.exists() and sha256(path.read_bytes()).hexdigest()==target["sha256"],"Relation digest mismatch")
    if d["form"]=="implementation":
        require(any(r["predicate"]=="implements" for r in d["relations"]),"Implementation missing request link")
        for delivery in p["deliveries"]:
            if delivery["format"]=="git-commit":require(delivery["source"]==p["source_snapshot"],"Commit identity mismatch")
            if delivery["format"]=="git-bundle":require(delivery["result_commit"]==p["source_snapshot"]["commit"],"Bundle commit mismatch")
    if d["form"]=="evaluation":
        unique(p["gates"],"id")
        target=ROOT/"examples"/p["request"]["uri"]
        require(sha256(target.read_bytes()).hexdigest()==p["request"]["sha256"],"Request changed")
        req=read(target)["payload"]
        require(p["gates"]==req["acceptance"] and p["evidence_policy"]==req["evidence_policy"],"Evaluation weakened request")
        require(p["target_profile"] in req["target_profiles"],"Unauthorized evaluation target")
def admission(d):
    check(d)
    def walk(v):
        if isinstance(v,dict):
            for k,x in v.items():
                if k in ("uri","image","builder_image") and isinstance(x,str):
                    require(not x.startswith("fixture:") and "fixture.invalid" not in x,"Synthetic artifact at admission")
                walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    walk(d)
def reject(name,d,func=check):
    try:func(d)
    except (ValidationError, ValueError):
        return
    raise AssertionError("Accepted invalid case: "+name)
if __name__=="__main__":
    docs={p.name:read(p) for p in (ROOT/"examples").glob("*.json")}
    for d in docs.values():check(d)
    r=docs["change-request.json"]; e=docs["evaluation.json"]; p=docs["implementation-patch.json"]
    cases=[]
    def case(name,base,mutate,fn=check):
        v=deepcopy(base);mutate(v);reject(name,v,fn);cases.append(name)
    case("request carries implementation",r,lambda d:d["payload"].update(deliveries=[]))
    case("missing objective",r,lambda d:d["payload"].pop("objective"))
    case("image is not mandatory",r,lambda d:d.update(images=[]))
    case("unknown goal gate",r,lambda d:d["payload"]["goals"][0].update(acceptance=["unknown"]))
    case("unknown required profile",r,lambda d:d["profiles"][0].update(id="urn:unknown"))
    case("changed profile schema",r,lambda d:d["profiles"][0]["schema"].update(sha256="0"*64))
    case("missing reader tool",r,lambda d:None,lambda d:check(d,tools=()))
    case("missing profile binding",r,lambda d:d.update(profiles=[]))
    case("optional behavior profile",r,lambda d:d["profiles"][0].update(required=False))
    case("malformed MoE profile",r,lambda d:d["profiles"][0]["data"].pop("target"))
    case("underspecified exact transform",r,lambda d:(d["payload"]["change_intents"][0].update(mode="specified-transformation"),d["profiles"][0]["data"]["intent"].update(mode="specified-transformation")))
    case("base branch name",p,lambda d:d["payload"]["deliveries"][0]["base"].update(commit="main"))
    case("no result tree",p,lambda d:d["payload"]["deliveries"][0].pop("result_tree"))
    case("missing request relation",p,lambda d:d.update(relations=[]))
    case("weakened evaluation",e,lambda d:d["payload"]["gates"][0].update(threshold=1.1))
    case("unresolved product accepted",e,lambda d:d["payload"]["execution_requirements"].update(requires_resolved_product_lock=False))
    case("changed relation digest",p,lambda d:d["relations"][0]["target"].update(sha256="0"*64))
    case("fixture dispatched",r,lambda d:None,admission)
    optional=deepcopy(r);optional["profiles"].append({"id":"urn:optional-display","schema":{"uri":"fixture:display","sha256":"0"*64,"media_type":"application/schema+json"},"required":False,"requires_tools":[],"data":{"label":"descriptive only"}});check(optional)
    print("PASS:",len(docs)+1,"valid examples including optional unknown metadata;",len(cases),"rejecting cases.")
    print("Shape and local semantic checks only. No patch application, build or GPU execution performed.")

