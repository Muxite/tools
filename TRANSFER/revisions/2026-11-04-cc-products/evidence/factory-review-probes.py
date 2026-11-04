from pathlib import Path
import sys,json,subprocess,time,uuid
from copy import deepcopy
root=Path.cwd();ref=root/'AI4Research-Notebook/Designs/CC and Strata delivery/CC Protocols/reference';sys.path.insert(0,str(ref))
from ccv2 import Host,CCError
from source_build import materialize
from integrations.product_demo import fixture
batch=root/'TRANSFER/revisions/2026-11-04-cc-products/evidence';probe=batch/('factory-probes-'+uuid.uuid4().hex[:8]);probe.mkdir(parents=True)
h=Host(probe/'store');out={'probe_directory':str(probe),'attempts':{}}
def attempt(name,template,change,**kw):
 dest=probe/(name+'-product');before={str(p.relative_to(h.store)) for p in h.store.rglob('*') if p.is_file()}
 try: result={'state':'materialized','result':materialize(h,template,change,dest,trusted_build=True,**kw)}
 except Exception as e:result={'state':'error','type':type(e).__name__,'code':getattr(e,'code',None),'message':str(e)}
 after={str(p.relative_to(h.store)) for p in h.store.rglob('*') if p.is_file()};result.update(change=change,package_visible=dest.exists(),new_store_files=sorted(after-before));out['attempts'][name]=result;return result
# Build failure loses both phase history and separate stderr/stdout.
t,c=fixture(probe/'failed-input',h);bad=deepcopy(c);bad['build']['command']=['{python}','-c',"import sys; print('build diagnosis stdout'); print('separate stderr',file=sys.stderr); sys.exit(7)"]
attempt('failed-build',t,bad)
# An empty patch identifies a legitimate unchanged exact tree.
t,c=fixture(probe/'empty-input',h);repo=Path(c['repository']);empty=probe/'empty.patch';empty.write_bytes(b'');c['patch']=h.put_artifact(empty);c['tree']=subprocess.check_output(['git','rev-parse',c['base']+'^{tree}'],cwd=repo,text=True).strip();attempt('unchanged-source',t,c)
# Track an actual LFS pointer and copy it into a nominally complete payload.
t,c=fixture(probe/'lfs-input',h);repo=Path(c['repository']);(repo/'.gitattributes').write_text('weights.bin filter=lfs diff=lfs merge=lfs -text\n');pointer='version https://git-lfs.github.com/spec/v1\noid sha256:'+'1'*64+'\nsize 123456\n';(repo/'weights.bin').write_text(pointer)
subprocess.run(['git','-c','filter.lfs.clean=cat','-c','filter.lfs.required=false','add','.gitattributes','weights.bin'],cwd=repo,check=True,capture_output=True)
p=probe/'lfs.patch';p.write_bytes(subprocess.check_output(['git','diff','--cached','--binary','--full-index',c['base']],cwd=repo));c['patch']=h.put_artifact(p);c['tree']=subprocess.check_output(['git','write-tree'],cwd=repo,text=True).strip();c['build']['command']=['{python}','-c',"import subprocess,sys,shutil; subprocess.run([sys.executable,'build.py'],check=True); shutil.copyfile('weights.bin','dist/weights.bin')"]
r=attempt('unresolved-lfs',t,c)
if r['package_visible']:r['payload_weight_bytes']=(probe/'unresolved-lfs-product/payload/weights.bin').read_text()
# Timeout must not imply all code stopped. Child writes only this probe's marker.
t,c=fixture(probe/'timeout-input',h);marker=probe/'late-build-child.txt';child="import time; from pathlib import Path; time.sleep(1.5); Path("+repr(str(marker))+").write_text('child continued after timeout')";parent="import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',"+repr(child)+"],cwd="+repr(str(probe))+",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); print('spawned child',flush=True); time.sleep(8)";c['build']['command']=['{python}','-c',parent]
start=time.time();r=attempt('timed-out-build',t,c,timeout=1);r['elapsed_to_error']=time.time()-start;r['marker_at_error']=marker.exists();time.sleep(2);r['late_child_effect']=marker.exists();r['marker_text']=marker.read_text() if marker.exists() else None
(batch/'factory-review-probe-evidence.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:{a:v for a,v in v.items() if a not in ['change','result']} for k,v in out['attempts'].items()},indent=2))
