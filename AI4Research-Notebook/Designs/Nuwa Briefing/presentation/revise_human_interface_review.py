from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json
R=Path(__file__).parent
replacements={
'Deep reconstruction can conflict with speed':'Construction is a narrow test of understanding',
'Checks: 3 known positions, 1 unfamiliar case and voice. Target: over 50% primary sources.':'Prescribed fidelity test: 3 known positions, 1 unfamiliar case and voice; over 50% primary sources.',
"The earlier claim that an existing AI4R agent simply applies an extracted procedure skipped evidence and qualification and overstated Nuwa's role.":'An extracted procedure is only a candidate input; AI4R must attach evidence and qualify task behavior.',
}
with ZipFile(R/'.build-orange/Nuwa Human Interface draft.pptx') as src:
    files={i.filename:src.read(i.filename) for i in src.infolist()}
for name,data in files.items():
    if name.endswith('.xml'):
        content=data.decode('utf-8')
        for old,new in replacements.items():content=content.replace(old,new)
        files[name]=content.encode('utf-8')
with ZipFile(R/'.build-orange/Nuwa Human Interface reviewed draft.pptx','w',ZIP_DEFLATED) as dst:
    for name,data in files.items():dst.writestr(name,data)
for name in ['build_pptx.py','revise_human_interface.py']:
    p=R/name;t=p.read_text(encoding='utf-8')
    for old,new in replacements.items():t=t.replace(old,new)
    p.write_text(t,encoding='utf-8')
p=R/'finalize.mjs';t=p.read_text().replace('Nuwa Human Interface draft.pptx','Nuwa Human Interface reviewed draft.pptx').replace('rev3 human-interface','rev3 human-interface-reviewed');p.write_text(t)
p=R/'record_human_interface.py';t=p.read_text(encoding='utf-8').replace('rev3 human-interface','rev3 human-interface-reviewed');p.write_text(t,encoding='utf-8')
p=R/'README.md';t=p.read_text(encoding='utf-8').replace('rev3%20human-interface.validation.json','rev3%20human-interface-reviewed.validation.json');p.write_text(t,encoding='utf-8')
report='Luna follow-up (gpt-6-luna): narrow-interface framing holds. Corrected unsupported construction-vs-speed example to source-grounded limitation, removed revision history from slide2 notes, labeled prescribed fidelity test explicitly. No additional blockers reported.\n'
(R/'review-orange/luna-human-interface-review.txt').write_text(report,encoding='utf-8')
print(report)
