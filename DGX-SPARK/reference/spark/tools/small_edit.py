import json,subprocess
from pathlib import Path
R=Path('/home/user2/software-factory-spark-20261113/sources/llama.cpp')
p=R/'tools/completion/completion.cpp'
text=p.read_text();needle='int llama_completion(int argc, char ** argv) {'
assert text.count(needle)==1
assert 'ssh-build-probe' not in text
p.write_text(text.replace(needle,needle+'\n    fprintf(stderr, "ssh-build-probe: incremental source executed\\n");',1))
subprocess.run(['git','-C',str(R),'add','tools/completion/completion.cpp'],check=True)
subprocess.run(['git','-C',str(R),'-c','user.name=Factory qualification','-c','user.email=factory-qualification@localhost','commit','-m','Add owned incremental-build execution marker'],check=True)
print(subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True))
