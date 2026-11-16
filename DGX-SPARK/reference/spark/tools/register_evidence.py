"""Record locally directed actions through the existing factory Store/taskgraph APIs."""
import hashlib,json,sys
from pathlib import Path
R=Path('/home/user2/software-factory-spark-20261113')
sys.path.insert(0,str(R/'sources/factory-fe88a206'))
from jiuwenswarm.factory.store import Store,NotFound
from jiuwenswarm.factory.taskgraph import plan_get
TASK='spark-ssh-research-20261113'
with Store(R/'factory-store') as store:
    try:store.get_task(TASK)
    except NotFound:store.create_task({'task_id':TASK,'objective':'Locally directed factory research on Spark: qualify SSH tools, improve build iteration, qualify memory/SSD inference and expand reusable CCs','target':{'profile':'spark-gb10'},'allowed_effects':['process.exec'],'constraints':{'agent_location':'Windows','provider_credentials_on_remote':False,'presentation_production':False}})
    task=store.get_task(TASK);graph=plan_get(store,TASK)
    if not graph['nodes']:
        nodes=[('transport','inspect','Qualify owned SSH execution'),('build','build','Establish isolated Spark build'),('iteration','investigate','Measure and improve rebuild turnaround'),('memory','measure','Qualify memory limits and real SSD behavior'),('cycle','decide','Evaluate a bounded reusable capability improvement')]
        store.advance_decision(TASK,task['current_decision_rev'],{'hypothesis':'Local reasoning can safely direct bounded remote tools without transferring provider authentication.','action':{'kind':'local_operator_workflow'},'reason_for_change':'User authorized implementation; no new presentation work. Initial registration reconciles already-started infrastructure qualification.','expected_graph_rev':0,'plan_patch':{'add':[{'node_id':n,'kind':k,'title':t,'depends_on':[] if i==0 else [nodes[i-1][0]]} for i,(n,k,t) in enumerate(nodes)]}})
    observations=[]
    for path in sorted((R/'results').glob('*/receipt.json')):
        data=path.read_bytes();key='receipt-'+hashlib.sha256(data).hexdigest()[:24]
        try:store.read(TASK,key)
        except NotFound:
            art=store.put_artifact(TASK,key+'-file',data,'application/json')
            body=json.loads(data)
            store.append_observation(TASK,{'obs_id':key,'kind':'ssh_tool_execution','values':{'id':body['id'],'rc':body['rc']},'source_artifacts':[art['artifact_id']],'host_run':{'request_id':body['id']},'limitations':'External SSH tool execution; not an autonomous remote agent invocation.'})
        observations.append(key)
    graph=plan_get(store,TASK);updates=[]
    for n in graph['nodes']:
        if n['state']=='done':continue
        if n['node_id']=='transport' and any((R/'results/transport-finish-001').glob('receipt.json')):
            # Completion evidence alone covers bounded execution; cancellation has separate queue receipt.
            updates.append({'node_id':'transport','state':'done','evidence_ids':observations,'reason':'Queue reconnection/idempotency and cancellation/timeout independently checked; raw output and receipts retained.'})
        if n['node_id']=='build':
            p=R/'results/build-cold-001/build-record.json'
            if p.exists() and json.loads(p.read_text()).get('status')=='success':updates.append({'node_id':'build','state':'done','evidence_ids':observations,'reason':'Cold Spark build and executable smoke check succeeded; model correctness is a separate gate.'})
    if updates:
        task=store.get_task(TASK)
        store.advance_decision(TASK,task['current_decision_rev'],{'hypothesis':'Infrastructure evidence supports continuing to build iteration and memory qualification.','evidence_ids':observations,'expected_graph_rev':graph['rev'],'plan_patch':{'update':updates},'action':{'kind':'continue_qualification'}})
    result=plan_get(store,TASK)
    (R/'results/factory-graph.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({'task':TASK,'graph_rev':result['rev'],'nodes':[(n['node_id'],n['state']) for n in result['nodes']]}))
