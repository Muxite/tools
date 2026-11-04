"""Validate the design package, not runtime correctness or scientific outcomes."""
from pathlib import Path
import argparse
import hashlib
import json
import re
from urllib.parse import unquote, urlparse
from jsonschema import Draft202012Validator, FormatChecker

EXPECTED_IDS={f'M2A-{i:02}' for i in range(1,15)}
EXPECTED_CATEGORIES={'calculation','reporting','intent','contract','literature','hypothesis','build','evaluation','planner','generalist'}
EXPECTED_MEMBERS={
    'calculation':{'calculate','normalize_table'},
    'reporting':{'markdown_report','packet_report','summary_to_packet','deliver','deliver_paper'},
    'intent':{'compile_intent'},'contract':{'compile_requirements'},
    'literature':{'search','screen','rank','summarize_paper'},
    'hypothesis':{'propose_hypothesis'},'build':{'build'},
    'evaluation':{'benchmark','evaluate'},'planner':{'plan','plan_paper'},
    'generalist':{'run_on_jiuwenswarm'}}
EXPECTED_SCHEMAS={'package','capability','call','receipt','artifact-manifest','research-contract','check-definition','quality-assessment'}

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def semantics(kind,value,examples):
    errors=[]
    if kind=='quality-assessment':
        if value['release_digest']!=examples['package']['release_digest']:errors.append('trust release mismatch')
        if value['trust_level']=='qualified_for_scope':
            if value['sample_count']<value['minimum_samples']:errors.append('insufficient trust evidence')
            if not value['thresholds_satisfied'] or not value['freshness_satisfied']:errors.append('quality or freshness not satisfied')
        if value['expires_at']<=value['assessed_at']:errors.append('invalid assessment validity interval')
    if kind=='receipt':
        call=examples['call']
        if value['call_id']!=call['id']:errors.append('call identity mismatch')
        if set(value['required_check_ids'])!=set(call['required_check_ids']):errors.append('prebound checks changed')
        ids=[c['id'] for c in value['checks']]
        if len(ids)!=len(set(ids)):errors.append('duplicate check identity')
        if value['status']=='accepted':
            if not value['terminal']:errors.append('accepted nonterminal result')
            if value['effect_state']=='unknown':errors.append('accepted unknown effect')
            if set(ids)!=set(call['required_check_ids']):errors.append('missing or substituted required check')
            if any(c['verdict']!='PASS' for c in value['checks']):errors.append('required check not PASS')
            if not value['output_refs']:errors.append('accepted without artifacts')
        if not set(value['observed_effects'])<=set(call['authorized_effects']):errors.append('effect outside bound authorization')
    elif kind=='artifact-manifest':
        required=set(value['required_obligations']);sat=set(value['satisfied_obligations']);unmet=set(value['unmet_obligations'])
        if sat & unmet or sat|unmet!=required:errors.append('invalid obligation partition')
        if required!={o['id'] for o in examples['research-contract']['acceptance_obligations']}:errors.append('contract obligation mismatch')
        if value['delivery_status']=='COMPLETE' and (sat!=required or unmet):errors.append('incomplete COMPLETE delivery')
        ids=[a['id'] for a in value['outputs']]
        if len(ids)!=len(set(ids)):errors.append('duplicate output identity')
        if not {value['report_artifact_id'],value['reproduce_artifact_id']}<=set(ids):errors.append('required artifact missing')
        if value['outputs']!=examples['receipt']['output_refs']:errors.append('outputs differ from fixture receipt')
    elif kind=='capability':
        package=examples['package']
        if value['package_id']!=package['id'] or value['id'] not in package['members']:errors.append('membership mismatch')
        if not set(value['effects'])<=set(package['effect_ceiling']):errors.append('effect ceiling exceeded')
    return errors

def validate(root):
    root=root.resolve();errors=[];counts={}
    def require(condition,message):
        if not condition:errors.append(message)
    def resolve(base,target):
        target=unquote(target)
        p=(base/target).resolve()
        if not p.is_relative_to(root):raise ValueError('required path escapes package: '+target)
        if not p.is_file():raise ValueError('missing required file: '+target)
        return p
    try:
        ref=root/'3-agent-reference'
        manifest=load(ref/'source-manifest.json')
        require(len(manifest.get('local_sources',[]))>=8,'missing source capture collection')
        for row in manifest['local_sources']:
            p=resolve(root,row['path']);require(sha(p)==row['sha256'],'source hash mismatch: '+row['path'])
        require(len(manifest.get('repository_pins',[]))>=4,'missing repository provenance')
        metadata_ids=[];link_count=0
        for p in root.rglob('*.md'):
            body=p.read_text(encoding='utf-8')
            for key in ('id','status','source','last_reviewed','next_action'):
                require(bool(re.search(r'^'+key+r':\s*\S',body,re.M)),f'{p.name}: missing metadata {key}')
            found=re.search(r'^id:\s*(.+)',body,re.M)
            if found:metadata_ids.append(found.group(1))
            # Inline and reference links, including images. Immutable snapshots are not .md.
            targets=re.findall(r'\]\((<[^>]+>|[^\s)]+)\)',body)
            targets+=re.findall(r'^\[[^\]]+\]:\s*(<[^>]+>|\S+)',body,re.M)
            for target in targets:
                target=target.strip('<>')
                if urlparse(target).scheme:continue
                filename,_,fragment=target.partition('#')
                dest=resolve(p.parent,filename) if filename else p
                if fragment and dest.suffix=='.md':
                    headings=re.findall(r'^#{1,6}\s+(.+)$',dest.read_text(encoding='utf-8'),re.M)
                    slugs={re.sub(r'[^\w\- ]','',h.lower()).replace(' ','-') for h in headings}
                    require(unquote(fragment) in slugs,'missing heading anchor: '+target)
                link_count+=1
        require(len(metadata_ids)==len(set(metadata_ids)),'duplicate note identity')
        counts.update(notes=len(metadata_ids),links=link_count,sources=len(manifest['local_sources']))
        matrix=load(ref/'acceptance-matrix.json')['obligations']
        require({r['id'] for r in matrix}==EXPECTED_IDS and len(matrix)==14,'missing or duplicate obligation coverage')
        for row in matrix:
            resolve(ref,row['design'])
            require(bool(row.get('owner')) and bool(row.get('acceptance')) and len(row.get('evidence_required',[]))>=2,'empty obligation mapping: '+row['id'])
        status=load(ref/'implementation-status.json')
        stage=load(ref/'stage-1.json')
        stage_ids={f'S1-{i:02}' for i in range(1,8)}
        require(stage.get('first_implementation_target') is True,'Stage 1 must be first build target')
        resolve(ref,stage['design'])
        require({r['id'] for r in stage['criteria']}==stage_ids and len(stage['criteria'])==7,'missing Stage 1 exit coverage')
        require(stage['required_members']=={'calculation':['calculate','normalize_table'],'reporting':['markdown_report']},'Stage 1 slice changed without reconciling its contract')
        require(len(stage.get('packaging_requirements',[]))>=4,'missing Stage 1 image/lifecycle/trust requirements')
        for row in stage['criteria']:
            require(bool(row['evidence_required']) and bool(row['parent_obligations']) and set(row['parent_obligations'])<=EXPECTED_IDS,'invalid Stage 1 parent/evidence mapping')
        require(status.get('current_build_target')=='stage-1','first coding target must be Stage 1')
        require({r['id'] for r in status['stage_1']['criteria']}==stage_ids,'missing Stage 1 runtime status')
        require(all(r['status']=='NOT_RUN' and not r['evidence'] for r in status['stage_1']['criteria']),'design-only Stage 1 must not claim runtime PASS')
        counts['stage_1_exits']=len(stage['criteria'])
        require({r['id'] for r in status['obligations']}==EXPECTED_IDS and len(status['obligations'])==14,'missing implementation status coverage')
        require(all(r['status']=='NOT_RUN' and r['evidence']==[] for r in status['obligations']),'design-only status must not claim runtime PASS')
        migration=load(ref/'migration-map.json')
        cats=migration['categories']
        require({c['id'] for c in cats}==EXPECTED_CATEGORIES and len(cats)==10,'missing/duplicate category coverage')
        for c in cats:
            require(bool(c.get('members')) and len(c['members'])==len(set(c['members'])) and bool(c.get('conversion')),'empty/duplicate member mapping: '+c['id'])
            require(EXPECTED_MEMBERS.get(c['id'],set())<=set(c['members']),'required member missing: '+c['id'])
        legacy={v for c in cats for v in c['legacy_ids']}
        release_rows=migration['inspected_release_manifests']
        require(len(release_rows)>=9,'missing inspected release inventory')
        require(all(r['legacy_id'] in legacy for r in release_rows),'public release missing conversion mapping')
        counts.update(obligations=len(matrix),categories=len(cats),members=sum(len(c['members']) for c in cats))
        schema_files={p.name.removesuffix('.schema.json'):p for p in (ref/'schemas').glob('*.schema.json')}
        require(set(schema_files)==EXPECTED_SCHEMAS,'missing schema collection')
        validators={}
        for name,p in schema_files.items():
            schema=load(p);Draft202012Validator.check_schema(schema)
            validators[name]=Draft202012Validator(schema,format_checker=FormatChecker())
        examples={name:load(ref/'examples'/f'{name}.json') for name in EXPECTED_SCHEMAS}
        fixtures=load(ref/'examples/fixtures.json')
        require(len(fixtures)>=14 and any(not f['valid'] for f in fixtures),'missing negative fixture coverage')
        for f in fixtures:
            value=load(resolve(ref/'examples',f['file']))
            failures=list(validators[f['schema']].iter_errors(value))
            if not failures:failures=semantics(f['schema'],value,examples)
            require((not failures)==f['valid'],'fixture outcome differs: '+f['file'])
        counts.update(schemas=len(validators),fixtures=len(fixtures))
        diagrams=load(root/'diagrams/manifest.json')
        require(len(diagrams)==6,'missing diagram coverage')
        for row in diagrams:
            for ext in ('mmd','svg','png'):
                p=resolve(root/'diagrams',row[ext]['path']);require(sha(p)==row[ext]['sha256'],'diagram hash mismatch: '+p.name)
        counts['rendered_diagrams']=len(diagrams)
        if (root/'package-files.json').exists():
            for row in load(root/'package-files.json')['files']:
                p=resolve(root,row['path']);require(sha(p)==row['sha256'],'package file hash mismatch: '+row['path'])
    except (OSError,ValueError,KeyError,TypeError) as exc:
        errors.append(str(exc))
    return dict(status='PASS' if not errors else 'FAIL',scope='Design-package integrity only; all runtime acceptance NOT_RUN.',counts=counts,errors=errors)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parents[2])
    args=parser.parse_args();result=validate(args.package)
    print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
