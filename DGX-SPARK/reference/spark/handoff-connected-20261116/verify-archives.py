"""Verify handoff tar content and saved image config/layer digests without loading."""
import gzip,hashlib,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
source=ROOT/'connected-development.tar.gz'
found={};expected=None
with tarfile.open(source,'r|gz') as tar:
 for entry in tar:
  if entry.issym() or entry.islnk():raise ValueError('Unexpected link in review archive')
  if not entry.isfile():continue
  name=Path(entry.name).relative_to('connected-development').as_posix()
  stream=tar.extractfile(entry)
  if name=='MANIFEST.json':expected=json.load(stream)
  else:found[name]=hashlib.file_digest(stream,'sha256').hexdigest()
if found!=expected:raise ValueError('Review archive file set/digest mismatch')
images=ROOT/'agent-arm64.tar'
hashes={};json_files={};members=0
with tarfile.open(images,'r|') as tar:
 for entry in tar:
  if entry.issym() or entry.islnk():raise ValueError('Unexpected image archive link')
  if not entry.isfile():continue
  members+=1;stream=tar.extractfile(entry)
  if entry.size<=4*2**20:
   raw=stream.read();hashes[entry.name]=hashlib.sha256(raw).hexdigest()
   try:json_files[entry.name]=json.loads(raw)
   except (ValueError,UnicodeDecodeError):pass
  else:hashes[entry.name]=hashlib.file_digest(stream,'sha256').hexdigest()
manifest=json_files['manifest.json'];identities=[]
expected_ids={'sha256:39677167fffa99d8c43ee050b26c0d7951b9fbd6e775db1b544631056ecf6085'}
index=json_files['index.json']
if {d['digest'] for d in index['manifests']} != expected_ids:raise ValueError('Unexpected saved image index identities')
config_roots={}
def descriptor(desc,root_id):
 name='blobs/sha256/'+desc['digest'].split(':',1)[1]
 if hashes.get(name)!=desc['digest'].split(':',1)[1]:raise ValueError('Missing/corrupt OCI descriptor')
 value=json_files.get(name,{})
 if 'manifests' in value:
  for child in value['manifests']:descriptor(child,root_id)
 elif 'config' in value and 'digest' in value['config']:
  config_roots[value['config']['digest']]=root_id
  descriptor(value['config'],root_id)
  for layer in value.get('layers',[]):descriptor(layer,root_id)
for desc in index['manifests']:descriptor(desc,desc['digest'])
with tarfile.open(images,'r:') as tar:
 for image in manifest:
  config=image['Config'];config_id='sha256:'+hashes[config]
  identity=config_roots[config_id]
  details=json_files[config];diff_ids=details['rootfs']['diff_ids']
  if len(diff_ids)!=len(image['Layers']):raise ValueError('Layer count mismatch')
  for layer,want in zip(image['Layers'],diff_ids):
   stream=tar.extractfile(layer);magic=stream.read(2);stream.seek(0)
   if magic==b'\x1f\x8b':stream=gzip.GzipFile(fileobj=stream)
   if 'sha256:'+hashlib.file_digest(stream,'sha256').hexdigest()!=want:raise ValueError('Uncompressed layer digest mismatch: '+layer)
  identities.append(dict(image_id=identity,config_digest=config_id,tags=image.get('RepoTags'),layers=len(diff_ids)))
if {i['image_id'] for i in identities}!=expected_ids:raise ValueError('Missing saved image')
for name,want in hashes.items():
 if name.startswith('blobs/sha256/') and Path(name).name!=want:raise ValueError('Blob digest mismatch')
result=dict(review=dict(archive=source.name,files=len(found),sha256=hashlib.file_digest(source.open('rb'),'sha256').hexdigest()),
 images=dict(archive=images.name,size_bytes=images.stat().st_size,sha256=hashlib.file_digest(images.open('rb'),'sha256').hexdigest(),
             verified_file_members=members,images=identities,loaded=False),
 verification='Streaming archive file/config/layer/blob SHA256 verification; Docker load not performed.',
 exclusions=['Model weights, mounted credentials and live databases are not part of these archives.'])
(ROOT/'IMAGE-ARCHIVE-VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/(images.name+'.sha256')).write_text(result['images']['sha256']+'  '+images.name+'\n')
print(json.dumps(result,indent=2))
