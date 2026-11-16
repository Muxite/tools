import hashlib,json,tarfile
from pathlib import Path
R=Path('/home/user2/software-factory-spark-20261113')
p=R/'incoming/factory-fe88a206.tar'
with p.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
assert digest=='422e437c37dc18fefe35c17dc77ce85459c0ba8ab836fcf7614447fb144d2a49'
dest=R/'sources/factory-fe88a206';dest.mkdir(exist_ok=False)
files={}
with tarfile.open(p) as t:
    t.extractall(dest,filter='data')
    for m in t.getmembers():
        if m.isfile():
            expected=hashlib.sha256(t.extractfile(m).read()).hexdigest()
            actual=hashlib.sha256((dest/m.name).read_bytes()).hexdigest()
            assert expected==actual,m.name
            files[m.name]=actual
receipt={'source_commit':'fe88a20682550603a5d32193403c74cc6e68e8b7','archive_sha256':digest,'files_verified':len(files),'files':files,'note':'Git archive includes repository-tracked artifacts and templates, not machine account state. Git reported an existing LFS non-pointer artifact; archive transfer hash and extracted regular files verified.'}
(R/'results/source-verification.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))
