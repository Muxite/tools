import hashlib,json,tarfile
from pathlib import Path
root=Path(__file__).resolve().parent;p=root/'spark-arm64-images.tar.gz'
expected={
'factory/agent:cc-dgx-spark-factory-loop-v1':'1823984018b3b9f744e604256fc2393afe1934359fdbb5e1bb55dad1ce633447',
'factory/builder:cc-dgx-spark-001':'d893d61a6f641fdeb6d20ce33870868d3ffd497746531a233d988427deff7f87',
'factory/cli:cc-dgx-spark-factory-loop-v1':'2fb559d3ad5b74e6eaa3c902b023cbb2caa508a9e501a2a4b96540cf7cd081d5',
'factory/strata:spark-strata-e2e-001':'c22e5406f9c81f5865a2318712c1f3247a86e2d1b1633a5ad19d1d3a09ffdfb4'}
hashes={};small={};blobs=0
with tarfile.open(p,'r|gz') as tar:
 for member in tar:
  if not member.isfile():continue
  stream=tar.extractfile(member);h=hashlib.sha256();parts=[]
  while chunk:=stream.read(2**20):
   h.update(chunk)
   if member.size<2**20:parts.append(chunk)
  digest=h.hexdigest();hashes[member.name]=digest
  if member.name.startswith('blobs/sha256/'):
   assert member.name.rsplit('/',1)[1]==digest,member.name
   blobs+=1
  if parts:small[member.name]=b''.join(parts)
manifest=json.loads(small['manifest.json']);actual={}
for entry in manifest:
 config=entry['Config'];assert config in hashes
 assert json.loads(small[config])['architecture']=='arm64'
 for layer in entry['Layers']:assert layer in hashes
 for tag in entry['RepoTags']:actual[tag]=hashes[config]
index=json.loads(small['index.json'])
archived={}
for entry in index['manifests']:
 tag=entry.get('annotations',{}).get('io.containerd.image.name') or entry.get('annotations',{}).get('org.opencontainers.image.ref.name')
 if tag and tag.startswith('docker.io/'):tag=tag.removeprefix('docker.io/')
 digest=entry['digest'].removeprefix('sha256:')
 assert hashes['blobs/sha256/'+digest]==digest
 if tag:archived[tag]=digest
assert archived==expected,(archived,expected)
assert set(actual)==set(expected)
# Verify every JSON descriptor link (including platform manifests/config/layers).
for name,data in small.items():
 if not name.startswith('blobs/sha256/'):continue
 try:obj=json.loads(data)
 except (ValueError,UnicodeDecodeError):continue
 if not isinstance(obj,dict):continue
 descriptors=list(obj.get('manifests',[]))+list(obj.get('layers',[]))
 if isinstance(obj.get('config'),dict) and 'digest' in obj['config']:descriptors.append(obj['config'])
 for descriptor in descriptors:
  digest=descriptor['digest'].removeprefix('sha256:')
  assert hashes.get('blobs/sha256/'+digest)==digest,descriptor['digest']

with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
(root/(p.name+'.sha256')).write_text(digest+'  '+p.name+'\n')
proof=dict(archive=p.name,size_bytes=p.stat().st_size,sha256=digest,image_index_sha256=archived,image_config_sha256=actual,architecture='arm64',archive_members_hashed=len(hashes),content_addressed_blobs_verified=blobs,scope='Streamed complete gzip/tar; checked blob digests, manifest/config identities and layer presence. Not a destination docker-load or GPU run.')
(root/'image-archive-verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
