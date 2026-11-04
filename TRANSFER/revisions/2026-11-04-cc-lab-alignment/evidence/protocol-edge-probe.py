"""Independent unified-model probes. All capsules/stores are temporary."""
from copy import deepcopy
import json,pathlib,sys,tempfile
ROOT=pathlib.Path(__file__).parents[4]
REF=ROOT/'AI4Research-Notebook/Designs/CC and Strata delivery/CC Protocols/reference'
sys.path.insert(0,str(REF))
from ccv2 import CCError,Host,normalize,service_entries,callable_entries

result={}
with tempfile.TemporaryDirectory() as temp:
    root=pathlib.Path(temp);bundle=root/'passive';bundle.mkdir()
    declaration={'cc':'2','id':'review.passive','version':'1.0.0','materials':{'guide':{'path':'SKILL.md','media_type':'text/markdown'}}}
    (bundle/'cc.yaml').write_text(json.dumps(declaration));(bundle/'SKILL.md').write_text('Original sealed guide')
    host=Host(root/'store');release=host.prepare(bundle)
    (bundle/'SKILL.md').write_text('Changed author workspace')
    material=host.material(release,'guide')
    result['passive_no_binding']={'capabilities':host.describe(release)['capabilities'],'callable_entries':callable_entries(host.release(release)[0]),'content':host.artifact_path(material['artifact']).read_text()}
    hybrid={'cc':'2','id':'review.hybrid','version':'1.0.0','bindings':{'default':{'kind':'native','command':['{python}','{bundle}/tool.py']}},'capabilities':{'echo':{'does':'Echo JSON','takes':{'value':'json'},'gives':{'value':'json'}},'engine':{'does':'Serve engine API','changes':['process.exec'],'serves':{}}}}
    canonical=normalize(hybrid)
    result['canonical_service_partition']={'capabilities':sorted(canonical['capabilities']),'callable_entries':sorted(callable_entries(canonical)),'service_entries':sorted(service_entries(canonical)),'idempotent':normalize(canonical)==canonical}
    legacy=deepcopy(hybrid);legacy['capabilities'].pop('engine');legacy['applications']={'engine':{'does':'Serve engine API','changes':['process.exec']}}
    migrated=normalize(legacy)
    result['legacy_import']={'matches_canonical':migrated==canonical,'legacy_field_remaining':'applications' in migrated}
    collision=deepcopy(legacy);collision['applications']['echo']={'does':'Conflicting legacy action'}
    try:normalize(collision);result['legacy_collision']={'unexpected':'accepted'}
    except CCError as error:result['legacy_collision']={'code':error.code}
    reserved=root/'reserved';reserved.mkdir();(reserved/'.cc-state').mkdir();(reserved/'.cc-state'/'notes.md').write_text('Declared reference material')
    d={'cc':'2','id':'review.reserved','version':'1.0.0','materials':{'notes':{'path':'.cc-state/notes.md'}}}
    (reserved/'cc.yaml').write_text(json.dumps(d))
    try:
        r=host.prepare(reserved)
        try:host.material(r,'notes');result['explicit_ignored_material']={'sealed':True,'retrieved':True}
        except Exception as error:result['explicit_ignored_material']={'sealed':True,'retrieved':False,'exception':type(error).__name__,'message':str(error)}
    except CCError as error:result['explicit_ignored_material']={'sealed':False,'structured_rejection':error.record()}
print(json.dumps(result,indent=2))
