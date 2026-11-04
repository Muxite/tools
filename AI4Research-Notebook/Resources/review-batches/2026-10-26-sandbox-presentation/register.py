from pathlib import Path
import hashlib
import json

B=Path(__file__).resolve().parent
V=B.parents[2]

def change(rel,old,new):
    p=V/rel
    raw=p.read_bytes()
    backup=B/'before'/(rel.replace('/','__')+'.snapshot')
    backup.parent.mkdir(parents=True,exist_ok=True)
    if not backup.exists():
        backup.write_bytes(raw)
        assert hashlib.sha256(backup.read_bytes()).digest()==hashlib.sha256(raw).digest()
    t=raw.decode('utf-8')
    assert old in t
    p.write_bytes(t.replace(old,new,1).encode('utf-8'))

change('Presentation Library/Deck Catalog.md','## Quick open','## Quick open\n\n- [Sandbox design: live editable deck](page://page_7a233186a3548191869c85106fc552b4) · [six-slide story, sources and remaining decisions](../Designs/Sandbox%20Briefing/presentation/README.md). Six main slides and two hidden backups, reviewed as a design proposal on October 26.')
change('Home.md','## Open directly','## Open directly\n\n- [[Designs/Sandbox Briefing/presentation/README|Sandbox design presentation]] — six main slides, two hidden backups, a workload example, source evidence and explicit implementation decisions.')

prompt='''is this enough to present it. a presentation doesnt need to be long, we just show the design and make it well. imagine what makes a good presentation that is straight to the point and communicates a lot of info. perhaps check the general idea of hwat we did for nuwaskill and agent2agent. then apply it here. make sure there arent gaps.'''
rel='Sources/Prompts/2026-10-26-sandbox-short-presentation.txt'
(V/rel).write_bytes((prompt+'\n').encode('utf-8'))
mp=V/'Sources/capture-manifest.json'
raw=mp.read_bytes()
backup=B/'before'/'capture-manifest.json.snapshot'
backup.write_bytes(raw)
manifest=json.loads(raw)
manifest.append({'path':rel,'sha256':hashlib.sha256((V/rel).read_bytes()).hexdigest(),'capture_method':'exact visible user message, UTF-8 LF','captured_date':'2026-10-26'})
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

review=V/'Designs/Sandbox Briefing/presentation/review'
layouts=[json.loads(p.read_text('utf-8')) for p in sorted(review.glob('slide-*.layout.json'))]
assert len(layouts)==8
outside=[]
for l in layouts:
    for e in l['elements']:
        pos=e.get('position',{})
        if any(k not in pos for k in ['left','top','width','height']):continue
        if pos['left'] < -1 or pos['top'] < -1 or pos['left']+pos['width']>1281 or pos['top']+pos['height']>721:
            outside.append({'slide':l['slide']['index']+1,'element':e['id'],'position':pos})
assert not outside,outside
report={'artifactRef':'artifact_external_42591fe5-db24-45f7-82e2-e82d5a83fbbc','page_id':'page_7a233186a3548191869c85106fc552b4','state_version':6,'main_slides':6,'hidden_backups':2,'speaker_notes':'present on all 8 slides, checked in session','editable_tables':3,'visual_review':'All 8 rendered slides inspected individually; slide 3 repaired and rerendered','geometry':'all element bounds inside slide canvas','runtime_tests':'NOT_RUN; design proposal only','remaining_decisions':['First investigation boundary and acceptance rubric','Protected cross-batch accepted-result transfer','Quality/cost tradeoff before evaluation','Concurrent live patches only if first slice shows need']}
(B/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Registered the deck; eight-slide canvas bounds checked.')
