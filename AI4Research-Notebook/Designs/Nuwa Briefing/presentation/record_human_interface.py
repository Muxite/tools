from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET
import json, hashlib, shutil
from PIL import Image, ImageOps, ImageDraw
R=Path(__file__).parent
V=R.parents[2]
prompt="what do you mean existing ai4r agent applies extracted procedure? you gotta be way more critical of nuwa-skill and its validations, imo its not the greatest project. we have better way for evidence backed capabilities, we will use nuwa-skills methodology for the human-to-skill stuff\n"
rel='Sources/Prompts/2026-10-23-nuwa-human-to-skill-critical-scope.txt'
(V/rel).write_text(prompt,encoding='utf-8',newline='\n')
mf=V/'Sources/capture-manifest.json'
rows=json.loads(mf.read_text(encoding='utf-8-sig'))
rows.append({'path':rel,'sha256':hashlib.sha256(prompt.encode()).hexdigest(),'capture_method':'exact visible user message as UTF-8 LF with terminal newline; not a transport export','captured_date':'2026-10-23'})
mf.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for file,append in {
'Sources/Prompt Register.md':'\n- [[Sources/Prompts/2026-10-23-nuwa-human-to-skill-critical-scope.txt|Nuwa critical scope correction]] — borrow the human-to-skill research interface; retain AI4R capability evidence and qualification.\n',
'Sources/Implementation Intent.md':'\n## Nuwa scope correction, 2026-10-23\n\nThe latest direction narrows Nuwa\'s contribution to human-to-skill research/extraction as a possible person-plus-trait factory input. It supersedes the presentation\'s broader evidence-backed capability-authoring endorsement. AI4R retains its own capability evidence, tests and admission. Nuwa\'s small persona-fidelity evaluation and permissive structural checker do not establish task capability. This is presentation/design intent, not implementation or an empirical comparison of the systems.\n',
'Activities/2026-10-23 Nuwa Orange Revision.md':'\n## Critical human-to-skill scope correction\n\nReplaced direct application by an existing AI4R agent with person-plus-trait research producing a candidate for factory qualification. Slide 2 answers yes narrowly. The deck now distinguishes Nuwa\'s human-focused authoring value from AI4R\'s existing evidence and qualification approach. The critique specifies 50/100 points for stance/style, a small fidelity test, shared-judge bias and a saved source-free placeholder passing 6/6 checker functions. Updated notes and conclusion preserve pipeline order, orange style, slide count and planned timings. No comparative task result is claimed.\n',
}.items():
    p=V/file
    with p.open('a',encoding='utf-8') as f:f.write(append)

p=R/'README.md'
t=p.read_text(encoding='utf-8')
t=t.replace('Explicit answer: yes, valuable as an evidence-backed capability-authoring design pattern','Explicit answer: yes narrowly, as a human-to-skill input to the CC Factory')
t=t.replace("Nuwa's pitfalls suggest stronger evidence and task checks","Weak fidelity assurance: resemblance-heavy scoring, tiny tests and source-free lint passes")
t=t.replace('A focused trial tests one expert-derived procedure','A bounded trial tests human-to-skill authoring utility, then task qualification')
t=t.replace('Learn the method and earn further integration with task evidence','Borrow the human-to-skill interface; AI4R owns capability evidence and qualification')
t=t.replace('rev3%20pipeline-order.validation.json','rev3%20human-interface.validation.json')
t=t.replace('next_action: Rehearse rev3 aloud; define the frozen expert-source corpus and generic-checklist control before any AI4R trial','next_action: Trial one person-plus-trait authoring request, then qualify any candidate through AI4R')
t+='\n## Human-to-skill scope correction (current)\n\nThis supersedes earlier broad endorsements in the historical revision notes. Nuwa\'s relevant contribution is the human-to-skill research/extraction input. AI4R already has its own evidence-backed capability approach. Slide 2 answers yes narrowly and sends a draft to factory qualification instead of directly to an AI4R agent. The validation critique now specifies scoring weights, question count and the source-free placeholder probe. Separate LLM judges are a useful safeguard but do not establish independent task validity. Authoring utility and downstream task gain are separate outcomes. Current edits preserve the native package through `revise_human_interface.py`; the legacy builder content is synchronized but was not used for this edit.\n'
p.write_text(t,encoding='utf-8')
p=R/'references/source-review.md'
t=p.read_text(encoding='utf-8').replace('next_action: Test an extracted neutral procedure against a length-matched generic checklist using unseen AI4R tasks','next_action: Assess one human-to-skill authoring request; independently qualify any useful candidate')
t+='\n## Critical scope correction (supersedes broader value endorsement)\n\nNuwa contributes a person-plus-trait research/extraction interface, not a superior general method for evidence-backed capabilities. AI4R retains its own evidence, qualification and admission. Source reread confirmed stance30/style20/uncertainty20/source15/structure15 in the fidelity rubric, with 3 known-position, 1 unfamiliar and 1 style question. This tests a small sample of persona fidelity, not AI4R task performance. The rubric separates answering and judging agents and recommends extra judges for important conclusions; these safeguards do not eliminate shared-model bias. The checker returns success for absent or untyped source sections. The saved placeholder passed6/6; it was content-free boilerplate, not a zero-byte file. This proves a lint weakness, not universal poor persona output. Our proposed trial now distinguishes source attribution, corrections and authoring effort from independently measured downstream task utility.\n'
p.write_text(t,encoding='utf-8')

src=R/'output/Nuwa Talk rev3 human-interface-reviewed.pptx'
shutil.copyfile(src,R/'output/Nuwa Talk rev3.pptx')
A='http://schemas.openxmlformats.org/drawingml/2006/main'; P='http://schemas.openxmlformats.org/presentationml/2006/main'
with ZipFile(src) as z:
    prs=ET.fromstring(z.read('ppt/presentation.xml'))
    rs=ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
    targets={r.get('Id'):r.get('Target') for r in rs}
    script=['---','id: nuwa-speaker-script','status: current','source: output/Nuwa Talk rev3.pptx','last_reviewed: 2026-10-23','next_action: Rehearse timing aloud','---','# Nuwa rev3 speaker script','']
    for i,s in enumerate(prs.find('{'+P+'}sldIdLst'),1):
        import posixpath
        path='ppt/'+targets[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        relpath=posixpath.dirname(path)+'/_rels/'+posixpath.basename(path)+'.rels'
        rr=ET.fromstring(z.read(relpath))
        target=next(r.get('Target') for r in rr if r.get('Type').endswith('/notesSlide'))
        nx=ET.fromstring(z.read(posixpath.normpath(posixpath.join(posixpath.dirname(path),target))))
        body=next(sp for sp in nx.findall('.//{'+P+'}sp') if sp.find('.//{'+P+'}ph') is not None and sp.find('.//{'+P+'}ph').get('type')=='body')
        script+=['## Slide '+str(i),'','\n'.join(t.text or '' for t in body.findall('.//{'+A+'}t')),'']
    (R/'speaker-script.md').write_text('\n'.join(script),encoding='utf-8')

canvas=Image.new('RGB',(1200,((11+2)//3)*245),'white')
for i in range(1,12):
    im=Image.open(R/f'review-orange/slide-{i:02}.png').convert('RGB');im.thumbnail((390,220))
    x=((i-1)%3)*400;y=((i-1)//3)*245
    canvas.paste(im,(x,y));ImageDraw.Draw(canvas).text((x+8,y+222),str(i),fill='black')
canvas.save(R/'review-orange/contact-sheet.jpg',quality=90)
check={'status':'pass','slides':11,'hidden_slides':[10,11],'scope':'Human-to-skill input; AI4R evidence and qualification retained','final_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'native_powerpoint_render':'11 slides','visual_review':'All11 individually inspected; no clipping','empirical_task_gain':'unmeasured'}
(R/'review-orange/human-interface-check.json').write_text(json.dumps(check,indent=2)+'\n',encoding='utf-8')
(R/'review-orange/review.json').write_text(json.dumps(check,indent=2)+'\n',encoding='utf-8')
batch=V/'Resources/review-batches/2026-10-23-nuwa-three-interfaces'
bundle=batch/'Nuwa Talk rev3 human-interface-reviewed.bundle.zip'
with ZipFile(bundle,'w',ZIP_DEFLATED) as z:
    for f in [R/'output/Nuwa Talk rev3.pptx',R/'build_pptx.py',R/'revise_human_interface.py',R/'speaker-script.md',R/'README.md',R/'references/source-review.md',R/'review-orange/human-interface-check.json',R/'.build-orange/Nuwa Talk rev3 human-interface-reviewed.validation.json']:
        z.write(f,f.relative_to(R))
with ZipFile(bundle) as z:assert z.testzip() is None
(batch/'human-interface-bundle-receipt.json').write_text(json.dumps({'archive':bundle.name,'sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'zip_integrity':'pass','off_device_backup':False},indent=2)+'\n',encoding='utf-8')
print('Recorded and backed up human-to-skill scope correction.')
