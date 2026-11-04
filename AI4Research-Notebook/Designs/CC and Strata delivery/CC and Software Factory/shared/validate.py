"""Offline design fixtures. Requires Python 3.10+, jsonschema 4.x and referencing."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path


from jsonschema import Draft202012Validator as Validator, ValidationError
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent
EX = ROOT / "examples"
SCHEMAS = {}
registry = Registry()
for path in (ROOT / "contracts").rglob("*.schema.json"):
    schema = json.loads(path.read_bytes())
    Validator.check_schema(schema)
    registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    SCHEMAS[path.name] = schema


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def shape(name, obj):
    Validator(SCHEMAS[name + ".schema.json"], registry=registry).validate(obj)


def read(name):
    return json.loads((EX / name).read_bytes())


def linked(ref):
    """Resolve mandatory bundled links only. fixture: identities represent external prerequisites."""
    path = (EX / ref["uri"]).resolve()
    require(path.is_relative_to(ROOT) and path.is_file(), "Missing local record")
    require(sha256(path.read_bytes()).hexdigest() == ref["sha256"], "Link digest mismatch")
    return json.loads(path.read_bytes())


def profiles(obj, readers):
    for profile in obj.get("profiles", []):
        key = (profile["namespace"], profile["version"])
        if key not in readers:
            require(not profile["must_understand"], "Required profile reader unavailable")
            continue
        require(linked(profile["schema"]) == SCHEMAS["moe.schema.json"], "Unexpected profile schema")
        shape("moe", profile["data"])


def check_cc(cc):
    shape("cc", cc)
    profiles(cc, READERS)
    if cc["state"] != "qualified":
        return
    fields = {}
    for k, field in (("takes","name"),("gives","name"),("guarantees","id"),("needs","provider"),("changes","scope")):
        fields[k] = {item[field] for item in cc[k]["items"]}
        require(len(fields[k]) == len(cc[k]["items"]), "Duplicate named contract")
    ids = set()
    for op in cc["operations"]:
        require(op["id"] not in ids, "Duplicate operation")
        ids.add(op["id"])
        require(op["carrier_index"] < len(cc["carriers"]), "No bound carrier")
        for key, local in (("takes","takes"),("gives","gives"),("checks","guarantees"),("needs","needs"),("changes","changes")):
            require(set(op[key]) <= fields[local], "Unknown operation binding")


READERS = {("urn:ai4r:profile:moe", 1)}


def brief_chain(brief, readers=READERS):
    shape("factory-brief", brief)
    profiles(brief, readers)
    linked(brief["evaluation_policy"])
    for field, state in [("available_ccs","qualified"),("requested_ccs","draft")]:
        for ref in brief[field]:
            cc = linked(ref)
            check_cc(cc)
            require(cc["state"] == state, "Availability and desired capability mixed")


def check_chain(evaluation):
    shape("evaluation", evaluation)
    product = linked(evaluation["product"])
    shape("product", product)
    require(evaluation["brief"] == product["brief"], "Product built for different brief")
    brief = linked(product["brief"])
    brief_chain(brief)
    require(brief["evaluation_policy"] == evaluation["evaluation_policy"], "Evaluator has different policy")
    if "reviewable-source" in brief["output_expectations"]:
        require(any(d["format"] in {"git-commit","git-bundle","git-patch"} for d in product["deliveries"]),
                "Reviewable source missing")
    for ref in product["delivered_ccs"]:
        cc = linked(ref)
        check_cc(cc)
        require(cc["state"] == "qualified", "Delivered CC must qualify independently")


class FixturePool:
    """Single-process reference behavior; the caller supplies previously approved release digests."""
    def __init__(self, approved):
        self.approved = approved
        self.active = {}
        self.retained = {}

    def install(self, ref):
        cc = linked(ref)
        check_cc(cc)
        require(cc["state"] == "qualified" and self.approved.get(ref["sha256"]) == cc["qualification"]["sha256"], "Release is not admitted")
        self.retained[ref["sha256"]] = cc
        self.active[cc["id"]] = ref["sha256"]

    def search(self, tag, inventory, allowed_effects):
        matches = []
        for digest in self.active.values():
            cc = self.retained[digest]
            if tag not in cc["tags"] or self.approved.get(digest) != cc["qualification"]["sha256"]:
                continue
            needs = {row["provider"]: row for row in cc["needs"]["items"]}
            for operation in cc["operations"]:
                carrier = cc["carriers"][operation["carrier_index"]]
                platform = carrier["platform"] if carrier["format"] == "oci-image" else carrier["base_image"]["platform"]
                if platform != inventory["platform"] or not set(operation["changes"]) <= allowed_effects:
                    continue
                compatible = True
                for name in operation["needs"]:
                    requirement = needs[name]
                    if (name not in inventory["providers"]
                            or requirement.get("min_memory_mib", 0) > inventory["memory_mib"]
                            or ("reader_abi" in requirement and requirement["reader_abi"] not in inventory["reader_abis"])
                            or ("device_class" in requirement and requirement["device_class"] != inventory["device_class"])):
                        compatible = False
                        break
                if compatible:
                    matches.append((digest, operation["id"]))
        return matches

    def withdraw(self, capability_id):
        self.active.pop(capability_id, None)


def rejected(fn, *args):
    try:
        fn(*args)
    except (ValueError, ValidationError):
        return
    raise AssertionError(f"Should reject: {fn.__name__}")


def changed(doc, path, val):
    clone = deepcopy(doc)
    node = clone
    for k in path[:-1]:
        node = node[k]
    node[path[-1]] = val
    return clone


def run():
    brief = read("brief.json")
    evaluation = read("evaluation.json")
    qualified = read("cc-qualified.json")
    draft = read("cc-draft.json")
    for cc in [draft, qualified]:
        check_cc(cc)
    check_chain(evaluation)
    # Qualified capsules also support reproducible source-only carriers.
    check_cc(changed(qualified, ["carriers"], [read("product.json")["build"]]))
    # A generic software brief needs no domain extension.
    brief_chain(changed(brief, ["profiles"], []))
    # A qualified capsule may furnish multiple operations from different carriers.
    multi = deepcopy(qualified)
    multi["carriers"].append(read("product.json")["build"])
    multi["operations"].append(dict(multi["operations"][0], id="measure-source",carrier_index=1))
    check_cc(multi)
    cases = [
        (check_cc, changed(qualified, ["takes","status"], "suggested")),
        (check_cc, changed(draft, ["state"], "qualified")),
        (check_cc, changed(qualified, ["carriers",0,"image"], "registry.local/tool:latest")),
        (check_cc, changed(qualified, ["operations",0,"carrier_index"], 2)),
        (check_cc, changed(qualified, ["operations",0,"checks"], ["absent"])),
        (check_cc, changed(qualified, ["operations",1,"needs"], ["unknown-provider"])),
        (check_cc, changed(qualified, ["operations",0,"changes"], ["host.write"])),
        (check_cc, changed(qualified, ["carriers"], [{k:v for k,v in read("product.json")["build"].items() if k != "build_context"}])),
        (check_cc, changed(qualified, ["carriers"], [{k:v for k,v in read("product.json")["build"].items() if k != "base_image"}])),
        (check_cc, changed(qualified, ["run_id"], "accidental-runtime-state")),
        (brief_chain, changed(brief, ["requested_ccs"], brief["available_ccs"])),
        (brief_chain, changed(brief, ["available_ccs"], brief["requested_ccs"])),
        (brief_chain, changed(brief, ["available_ccs",0,"sha256"], "0"*64)),
        (brief_chain, brief, set()),
        (check_chain, changed(evaluation, ["evaluation_policy","sha256"], "0"*64)),
        (check_chain, changed(evaluation, ["brief"], brief["available_ccs"][0])),
        (check_chain, changed(evaluation, ["on_missing_evidence"], "pass")),
    ]
    for case in cases:
        rejected(*case)
    release_ref = brief["available_ccs"][0]
    digest = release_ref["sha256"]
    approved = {digest: qualified["qualification"]["sha256"]}
    pool = FixturePool(approved)
    host = {"providers": {"native-index","strata-api"}, "reader_abis":{"strata-native-index-v3"},
            "device_class":"gb10", "platform":"linux/arm64", "memory_mib":8192}
    effects = {"attempt.artifacts"}
    def operations(inventory=host, grants=effects):
        return {name for _, name in pool.search("strata", inventory, grants)}
    require(not operations(), "Unexpected preinstallation")
    pool.install(release_ref)
    require(operations() == {"inspect","measure"}, "Qualified operations absent")
    require(operations(dict(host,reader_abis=set())) == {"measure"}, "Inspector needs exact reader ABI")
    require(operations(dict(host,memory_mib=256)) == {"inspect"}, "Sparse host cannot serve benchmark")
    require(operations(dict(host,device_class="cpu")) == {"inspect"}, "Wrong device selected")
    require(operations(dict(host,platform="darwin/arm64")) == set(), "Wrong carrier OS selected")
    require(operations(grants=set()) == {"inspect"}, "Insufficient effect grant")
    approved.clear()
    require(not operations(), "Stale qualification still discoverable")
    approved[digest] = qualified["qualification"]["sha256"]
    rejected(pool.install, brief["requested_ccs"][0])
    rejected(FixturePool({}).install, release_ref)
    pool.withdraw(qualified["id"])
    require(not operations() and pool.retained[digest] == qualified, "Withdrawal lost trace or visibility")
    print(f"PASS: linked draft, qualified CC, brief, product and evaluation; recipe and multi-carrier variants; "
          f"{len(cases)+2} rejecting cases; inspector/benchmark filtered by reader ABI, resources, platform, grants and qualification; hot install/withdraw/retain.")


if __name__ == "__main__":
    run()


