export const C={bg:'#FAF8F4',ink:'#1F2A44',muted:'#667085',rule:'#D6D3CC',indigo:'#3D4FB0',il:'#E7E9F7',teal:'#0F8588',tl:'#DFF1F1',amber:'#A96512',al:'#FBF0DC',white:'#FFFFFF'};

function rect(s,n,x,y,w,h,fill=C.white,stroke='none',lw=1){return s.shapes.add({name:n,geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:lw,style:'solid'}});}
function tx(s,n,x,y,w,h,t,size=22,color=C.ink,bold=false,align='left'){
 const p=rect(s,n,x,y,w,h,'none');p.text=t;p.text.style={fontSize:size,typeface:'Segoe UI',color,bold,alignment:align,verticalAlignment:'middle',wrap:'square',autoFit:'none',insets:0};return p;
}
function box(s,n,x,y,w,h,t,fill=C.il,stroke=C.indigo,size=23,color=C.ink){const p=rect(s,n,x,y,w,h,fill,stroke,1.6);p.text=t;p.text.style={fontSize:size,typeface:'Segoe UI',color,bold:true,alignment:'center',verticalAlignment:'middle',wrap:'square',autoFit:'none',insets:12};return p;}
function edge(s,a,b,color=C.muted,from='right',to='left',dash=false){return s.shapes.connect(a,b,{fromSide:from,toSide:to,kind:'elbow',line:{fill:color,width:2,style:dash?'dashed':'solid'},tail:{type:'triangle',width:'sm',length:'sm'}});}
function line(s,x,y,w,color=C.rule){return rect(s,'rule',x,y,w,1.3,color);}
function base(p,i,title,sub,source,hidden=false){const s=i===0?p.slides.getItem(0):p.slides.add({width:1280,height:720});s.background.fill=C.bg;s.hidden=hidden;tx(s,'title',56,30,1168,62,title,37,C.ink,true);if(sub)tx(s,'subtitle',56,101,1168,42,sub,20,C.muted);line(s,56,664,1168);tx(s,'source',56,677,1115,25,source,13,C.muted);tx(s,'number',1190,677,34,25,String(i+1),14,C.muted,false,'right');return s;}
function bar(s,y,t,fill=C.tl,color=C.teal){rect(s,'takeaway',56,y,1168,62,fill);tx(s,'takeaway text',74,y+8,1132,46,t,24,color,true);}
function note(s,t){s.speakerNotes.text=t;}
export function architectureDrawing(s){
 const human=box(s,'human',56,166,240,94,'Human direction\nGoal, limits, permissions',C.white,C.indigo,21);
 const app=box(s,'ai4r',356,166,868,94,'AI4R research runtime\nObjective, knowledge, strategy and next batch',C.il,C.indigo,25);
 const bind=box(s,'binding',356,322,240,94,'Protected binding\nScope, grants, pins',C.white,C.ink,22);
 const ctrl=box(s,'controller',646,322,250,94,'Lab controller\nLimits and lifecycle',C.al,C.amber,22);
 const jobs=box(s,'jobs apps',946,322,278,94,'CC jobs and apps\nScoped execution',C.white,C.amber,23);
 const checks=box(s,'checks',946,474,278,82,'Independent checks\nProtected acceptance',C.white,C.ink,22);
 const store=box(s,'project state',356,474,530,82,'Durable lab state\nKnowledge, artifacts, jobs, checkpoints',C.tl,C.teal,22);
 edge(s,human,app,C.indigo);edge(s,app,bind,C.indigo,'bottom','top');
 edge(s,bind,ctrl,C.amber);edge(s,ctrl,jobs,C.amber);edge(s,jobs,checks,C.ink,'bottom','top');
 edge(s,checks,store,C.teal,'left','right');edge(s,ctrl,store,C.teal,'bottom','top');
 tx(s,'controller boundary',646,297,578,20,'Controller authority stays outside mutable research code',16,C.amber);
 tx(s,'factory heading',56,300,240,35,'Capability growth',22,C.teal,true);
 tx(s,'factory',56,348,240,180,'Factory produces candidates\n\nIndependent qualification makes compatible versions eligible for new work',21);
 bar(s,584,'Restart reconciles work. Selected contributions return to central AI4R through qualification.');
}
function table(s,x,y,width,height,headers,values,widths){
 const vals=[headers,...values];const tb=s.tables.add({rows:vals.length,columns:headers.length,left:x,top:y,width,height,columnWidths:widths,values:vals});
 tb.borders.assign({fill:C.rule,width:1,style:'solid'});
 for(let r=0;r<vals.length;r++)for(let c=0;c<headers.length;c++){
  const cell=tb.getCell(r,c);cell.fill=r===0?C.il:C.bg;cell.text.style={typeface:'Segoe UI',fontSize:r===0?20:19,bold:r===0||c===0,color:r===0?C.indigo:C.ink,verticalAlignment:'middle',insets:12};
 }
 return tb;
}

export async function cover({presentation:p}){
 const s=base(p,0,'AI4Research sandbox labs','A proposed design for research that changes with new evidence','M2 proposal, October 2026. Source review supports feasibility. Research benefit remains unmeasured.');
 tx(s,'value',56,190,515,126,'Keep useful work when new findings change the plan',37,C.teal,true);
 tx(s,'purpose',56,345,490,112,'One durable project holds its goals, knowledge, capabilities and experiment results across agent sessions.',25);
 tx(s,'scope',56,510,490,72,'First use: workload research\nRobotics can attach later',23,C.muted);
 const a=box(s,'persistent goal',646,174,558,84,'Persistent research goal',C.il,C.indigo,29);
 const b=box(s,'strategy',646,314,558,84,'Revisable research strategy',C.tl,C.teal,29);
 const c=box(s,'attempts',646,454,558,84,'Checked, fixed execution attempts',C.white,C.ink,26);
 edge(s,a,b,C.indigo,'bottom','top');edge(s,b,c,C.teal,'bottom','top');
 tx(s,'feedback',650,568,550,54,'Findings change the next investigation',23,C.teal,true,'center');
 note(s,`Planned time 0:40. The design is ready to discuss as a proposal. Long research projects should retain goals and knowledge while experiments change with discoveries. This is a replacement of the earlier infrastructure-first presentation emphasis. We retain useful deployment and CC contracts. We have not implemented or measured this adaptive loop. The talk is six main slides plus two hidden backups, about six minutes at a deliberate pace. The estimate is not a timed rehearsal.\n\nSource: AI4Research-Notebook/Designs/Sandbox Lab Design.md and Lab Capsule and Factory Design Plan.md, replaced October 26. User's shared discussion: https://chatgpt.com/share/6adf9a5b-2320-83e9-afeb-ff63c4f96671.\n\nPresentation structure borrows the value-first, mechanism, worked-example, AI4R-fit and bounded-trial pattern reviewed in Nuwa Talk rev3 and final Paper2Agent Talk rev8. Their research results are not evidence for this sandbox.`);
 return {slide:0};
}

export async function exampleAndArchitecture({presentation:p}){
 let s=base(p,1,'A discovery changes the next experiment','Illustrative workload study: predict memory demand on a held-out machine','Illustrative scenario and proposed behavior. No predictor accuracy or adaptive-run result is claimed.');
 const a=box(s,'inspect',56,179,280,110,'Inspect authorized\nworkload traces',C.il,C.indigo,25);
 const b=box(s,'planned fit',456,179,280,110,'Fit a cross-machine\npredictor',C.white,C.rule,25);
 const c=box(s,'planned score',856,179,368,110,'Evaluate on a\nheld-out machine',C.white,C.rule,25);
 edge(s,a,b);edge(s,b,c);
 rect(s,'discovery field',56,334,1168,72,C.al);
 tx(s,'discovery',76,343,1128,54,'Discovery: the two machines define the same counter differently',25,C.amber,true);
 const d=box(s,'comparability',456,450,280,110,'Test counter\ncomparability',C.tl,C.teal,25);
 const e=box(s,'narrow conclusion',856,450,368,110,'Fit only comparable features\nor narrow the claim',C.tl,C.teal,24);
 edge(s,a,d,C.teal,'bottom','left');edge(s,d,e,C.teal);
 tx(s,'withdraw',458,296,730,28,'Withdraw the dependent fitting and scoring work',18,C.muted);
 tx(s,'reuse',56,465,280,78,'Retain unrelated valid\nmeasurements',22,C.teal,true);
 bar(s,590,'Web permission stays authoritative. Missing evidence remains a visible gap.');
 note(s,`Planned time 0:55. This is the worked example, not a completed experiment. Initial clarification establishes the question, data, success measure, cost and web permission. Before the discovery, fitting is a provisional future step. The initial executable batch only inspects authorized traces. The discovery invalidates the comparability premise. The planner should now test semantics, select comparable features or narrow the conclusion. It should not continue a scientifically inappropriate fit just because the first DAG named one. An unrelated accepted measurement can remain useful if its scope and dependencies still match. A driver choosing these steps only proves mechanics. The value demonstration requires the actual Planner to choose a useful revision.\n\nSource: Sandbox Lab Design.md, The AI4R problem this solves and Evidence that would make this valuable. Counter mismatch is a deliberately constructed test case, not an observed dataset finding. No-web denial uses provided material and explicit evidence gaps. A valid scientific negative is acceptable.`);

 s=base(p,2,'The lab owns research state and bounds execution','Binding precedes launch. Independent checks assess the outputs.','Proposed M2 ownership. Logical responsibilities can share one codebase.');
 architectureDrawing(s);
 note(s,`Planned time 1:10. This diagram shows logical ownership rather than a new process per rectangle. The Planner selects research work. Existing protected binding and checks validate each invocation and decide acceptance. The lab controller owns execution authority, job lifecycle and actual resource controls, outside mutable research code. AI4R does not receive the Docker socket or controller policy writes. The controller may refuse missing resources or permissions. Accepted artifacts enter durable custody. Both the control/job record and project data survive app replacement; restart reconciles actual jobs before retry. Restore must fence the previous writer and verify backup bytes. Measurement work needs an exclusive slot or explicit co-running-load limitation.\n\nThe first profile uses one permitted Docker host, existing store, scoped jobs and a small application fixture. A VM is an optional outer profile; no VM-equivalent isolation claim follows from Compose. Each lab owns separate writable data, credentials and selected versions. Shared immutable artifacts can be explicit inputs. Application authors supply setup, ports and reset/checkpoint semantics. Stateful application commands need leases. Attached service access does not imply reset/upgrade authority. CC packages may expose several operations.\n\nThe factory authors candidates; protected qualification controls eligibility. Compatible local updates apply to future bindings, preserving running attempts and sessions. Whole-harness RSI belongs to the RSI owner. Central adoption is separate. Factory expansion, robotics, GPU and fleet automation are not prerequisites for testing the first adaptive loop.\n\nSource: Sandbox Lab Design.md, What the sandbox supplies and Revising work without corrupting results. M2 infrastructure is a proposal; synthetic Docker evidence and M1 software tests do not establish this deployment.`);
 return {slides:[1,2]};
}

export async function revisionAndEvidence({presentation:p}){
 let s=base(p,3,'Plan revisions preserve work with valid dependencies','A material event revisits future work. Every dispatched attempt keeps its original contract.','Proposed M2 behavior. Initial delivery revises between batches. Concurrent live patches are a later extension.');
 const trig=box(s,'trigger',56,169,335,94,'Discovery, user change,\nfailure or no progress',C.al,C.amber,23);
 const plan=box(s,'revision',471,169,323,94,'Planner proposes\nthe affected next work',C.il,C.indigo,23);
 const gate=box(s,'validate',874,169,350,94,'Runtime checks revision,\ninputs, grants and budget',C.tl,C.teal,22);
 edge(s,trig,plan,C.indigo);edge(s,plan,gate,C.teal);
 table(s,56,316,1168,255,['Work state','Designed response'],[
  ['Unstarted','Withdraw or replace, then bind against current state'],
  ['Running','Keep independent work. Cancel or quarantine affected work.'],
  ['Completed','Reuse accepted results only while their dependencies remain valid'],
  ['Failed or uncertain effect','Reconcile the real job before any new attempt']
 ],[278,890]);
 bar(s,591,'Accepted artifact transfer between batches needs an explicit M2 contract.');
 note(s,`Planned time 1:05. Replanning is selective, not after every observation. Initial rules trigger at a declared investigation boundary, changed user direction or permission, invalidated assumption, missing prerequisite, unrecoverable failure or idle work with unmet objectives. Routine findings update knowledge. A bounded periodic/no-progress review catches missed triggers, with all planning and checking cost inside the cumulative budget. A semantic detector is a possible later experiment. Specialists adapt locally within their assignment and escalate shared premise changes.\n\nFirst implement the simpler between-batch change. M1 Scheduler._committed_node checks a same-run frozen-plan proof. Importing an accepted result into another batch therefore needs a protected transfer that validates original artifact identity, check outcome, task scope, assumptions/dependency versions and authorized reads, without accepting arbitrary refs. Current declaration and qualified reviewer profile still own reviewer visibility.\n\nIf concurrency justifies live patches, propose against exact plan and knowledge revisions, validate atomically, reject stale proposals and cycles, and prevent stale dispatch. Permission revocation immediately blocks new prohibited dispatch and requests cancellation of affected work. Cancellation may not undo effects. An obsolete output remains historical evidence but cannot feed current descendants. Unknown dependency validity means conservative rerun or a visible block. Prompt cache identity alone is insufficient when datasets, policy or services changed.\n\nGoal completion requires the fixed accepted objective criteria, not the producer's success field. Negative/inconclusive science can be accepted. The project stops or waits on supported completion, budget exhaustion, no progress or required input. Source: Sandbox Lab Design.md, How the loop works and Revising work without corrupting results.`);

 s=base(p,4,'AI4R already has useful parts of this design','Reuse the governed path and test the upstream mechanisms before extending them','Evidence: M1 ab0d9c7, installed OpenJiuwen 9e339019. Source inspection is separate from runtime validation.');
 tx(s,'left heading',56,169,548,42,'Our AI4R baseline',28,C.indigo,true);
 tx(s,'right heading',676,169,548,42,'Reuse candidates',28,C.teal,true);
 line(s,56,222,548);line(s,676,222,548);
 tx(s,'m1 source',56,244,548,112,'Compiler Brief, Planner proposal,\nprotected freeze, checked execution\nand retained results',26);
 tx(s,'upstream',676,244,548,112,'OpenJiuwen persistent goals\nand workflow replay can retain state\nand reuse matching calls',26);
 tx(s,'m1 limit',56,389,548,90,'Our Planner adapter deliberately disables the broader task loop and SwarmFlow orchestration.',22,C.muted);
 tx(s,'reuse limit',676,389,548,90,'Replay signatures do not establish research validity or safe mutation of an active DAG.',22,C.muted);
 rect(s,'evidence basis',56,517,1168,54,C.white);
 tx(s,'references',74,523,1132,42,'Magentic-One: task/progress ledgers     SyncPlan: selective replanning hypothesis',21,C.ink);
 bar(s,591,'Integration work: next-batch control, accepted-result transfer and restart reconciliation.');
 note(s,`Planned time 0:55. These are source observations and references, not measured AI4R adaptation. Inspected our published M1 commit ab0d9c7fe8ceadf45c61d04e94e2dd9b44b867a7 through objects in the reviewed-integration checkout. Scheduler.run receives a Compiler Brief, chooses static/planned proposal, binder.freeze then execute_plan. _committed_node verifies same-run frozen-plan identity. planning.py contains bounded failure/continuation behavior, not scientific replanning. native.py disables tools/subagents, task loop/task planning and Planner Leader SwarmFlow. This is our adapter choice, not an upstream limitation.\n\nInstalled SDK source 9e3390195a9ea15235b2b5f7412cb2aa440622cc: harness/goal/schema.py, manager.py, store.py contain persistent goal state, progress and budgets. agent_teams/workflow/engine/journal.py uses structural call path, content signature and run_id in get_cached. primitives.py agent() reuses matching prior records. Source bytes inspected match this SDK revision for the cited paths. This is a different SDK pin from upstream JiuwenSwarm's declared dependency.\n\nMagentic-One https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html supports separate task/progress ledgers and stalled-progress replanning. It does not prove AI4R quality or cost benefit. SyncPlan https://arxiv.org/abs/2608.01652 motivates testing plan-staleness-triggered replanning in a different task setting. We do not transfer its performance results. Learning When to Plan https://arxiv.org/abs/2509.03581 is an additional cost-allocation reference.\n\nReuse spike: compare adapting pinned goal/replay paths with extending our current store/scheduler. Keep source/checking authority explicit. No framework replacement is selected. Upstream release descriptions https://github.com/openJiuwen-ai/jiuwenswarm/releases support goals and partial replay, but not arbitrary concurrent live graph mutation.`);
 return {slides:[3,4]};
}

export async function decisionAndBackups({presentation:p}){
 let s=base(p,5,'The first delivery tests useful adaptation','One workload lab, existing capabilities and one discovery that should change the next experiment','Proposed evaluation. Quality and acceptable cost limits must be agreed before the runs. No improvement is established.');
 const xs=[56,456,856], titles=['1  Connect','2  Demonstrate','3  Compare'];
 const bodies=[
  'Reuse the goal, scheduler and checks.\nDefine accepted-result transfer.\nKeep the next batch bounded.',
  'Revise after a late discovery.\nRetain unaffected work.\nResume after an interruption.',
  'Fixed initial plan\nReplan at every batch boundary\nSelective replanning'
 ];
 for(let i=0;i<3;i++){tx(s,'step '+i,xs[i],173,368,48,titles[i],29,i===2?C.teal:C.indigo,true);line(s,xs[i],235,368);tx(s,'step body '+i,xs[i],259,368,166,bodies[i],24);}
 rect(s,'measure area',56,465,1168,95,C.white);
 tx(s,'measure',76,477,1128,69,'Independent research quality, stale-result use, retained valid work,\nplanning and checking cost, elapsed time and recovery',24);
 bar(s,589,'Continue if changed-information tasks improve within the agreed cost limit.');
 note(s,`Planned time 0:55. This is the proposed next delivery and decision. It prioritizes the research loop rather than a fleet or automatically generated ecosystem. Before coding, register the bounded slice through the target repository's current instructions and task allocation. First determine whether pinned upstream goal/replay components reduce integration work without weakening our protected checks. Then implement one changing-information journey using an actual planner. Qualify real job limits, stop, restart and independent backup/restore on the chosen host.\n\nThe comparison uses the same capabilities, model settings, task inputs, authorized data, discovery schedule, permissions, total budget and independent scoring across three planning policies. Freeze the quality rubric and acceptable cost/quality tradeoff before runs, including static-task quality protection. Include no-change tasks, scope changes, misleading observations, failed prerequisites and interruption. Repeat paired trials on held-out discovery cases. All attempts, failures and rejected outputs remain in the results. The budget includes planning, execution, review, repair and authoring where applicable; report preparation separately.\n\nUseful selective adaptation should improve independently verified outcomes on changing-information tasks, preserve static-task quality and compare favorably with frequent replanning on cost at comparable quality. These are testable hypotheses, not outcomes. A single demonstration proves feasibility; an extended representative run is needed before a day-long reliability claim. Hardware transfer prediction quality and CC effectiveness have separate experimental controls.\n\nDiscussion decisions: first investigation boundary, completion rubric and cost limit, accepted-result transfer rule, and whether concurrency requires live patches after the first trial. Source: replacement Lab Capsule and Factory Design Plan.md and Sandbox Lab Design.md.`);

 s=base(p,6,'Backup: failure and recovery behavior','Owners and expected outcomes for the first implementation slice','Designed behavior only. Each row needs observed evidence on the selected runtime.',true);
 table(s,56,165,1168,444,['Case','Owner and expected behavior'],[
  ['Web forbidden or revoked','Dispatcher refuses new prohibited work and requests cancellation of affected jobs'],
  ['Stale plan or changed dataset','Runtime rejects stale revision or invalid reuse and rebinds dependent work'],
  ['App crash or unknown effect','Controller reconciles the job before retry and fences duplicate writers'],
  ['Bad output or valid negative','Checks reject missing/corrupt output. Supported negative science can pass.'],
  ['New CC version or service state','Qualification enables compatible future work. Active bindings stay pinned.'],
  ['Storage or budget exhausted','Controller/runtime stops growth or dispatch, retains evidence and explains the stop']
 ],[334,834]);
 note(s,`Backup. Coverage review includes user intent/permission authority, source of investigation inputs, proposed strategy, fixed execution identity, accepted output custody, reuse validity, interruption, stop and capability eligibility. Restore also needs independent verified backups, application-consistent checkpoints and old-writer fencing. A service volume does not imply a resumable simulator physics state. Credential loss or unavailable environment blocks only dependent work; never invent a success. Conflicting mutable sessions serialize through leases. Rejected candidate outputs and uncertain external effects cannot silently become accepted scientific evidence.\n\nSource: Sandbox Lab Design.md. Every designed outcome needs actual implementation and evidence. This slide is not a test report.`);

 s=base(p,7,'Backup: evidence and the remaining design decisions','The proposal has explicit integration questions rather than implied capabilities','Source checks dated October 26, 2026. No new runtime or scientific trial ran for this presentation.',true);
 table(s,56,165,1168,350,['Evidence or gap','What it establishes or requires'],[
  ['M1 scheduler and native adapter','Frozen-plan execution exists. Its adapter narrows upstream orchestration.'],
  ['Pinned SDK goal and journal code','Persistent goal records and signature/run-scoped replay are reuse candidates.'],
  ['Magentic-One and planning research','Support mechanisms and test hypotheses, not AI4R performance claims.'],
  ['Cross-batch accepted artifacts','Define identity, scope, dependencies, authorization and original acceptance proof.'],
  ['Concurrent live patches','Choose only if needed. Require atomic revision checks and invalidation closure.']
 ],[363,805]);
 tx(s,'remaining',56,544,1168,77,'Before implementation: settle transfer semantics and the first boundary.\nBefore benefit claims: freeze quality/cost criteria, then run the comparison.',25,C.teal,true);
 note(s,`Backup source map.\nM1 source ab0d9c7fe8ceadf45c61d04e94e2dd9b44b867a7: https://github.com/Stellven/jiuwenswarm/tree/ab0d9c7fe8ceadf45c61d04e94e2dd9b44b867a7/jiuwenswarm/research . Cited paths scheduler.py (run, _committed_node), planning.py (research_continuation), native.py (Planner Leader configuration).\nInstalled local OpenJiuwen 9e3390195a9ea15235b2b5f7412cb2aa440622cc: AI4Research-Development/openjiuwen-builder-sdk-9e339/openjiuwen/harness/goal/{schema,manager,store}.py and agent_teams/workflow/engine/{journal,primitives,runtime}.py.\nUpstream JiuwenSwarm locally inspected 02b37f47fbefe80a58e4ed88606120818ca44ac3; distinguish upstream source from our fork and SDK pins. Release notes: https://github.com/openJiuwen-ai/jiuwenswarm/releases .\nMagentic-One: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html\nSyncPlan: https://arxiv.org/abs/2608.01652\nLearning When to Plan: https://arxiv.org/abs/2509.03581\nTemporal durable event pattern, optional: https://docs.temporal.io/develop/python/workflows/message-passing\n\nCurrent notebook design: Sandbox Lab Design.md and Lab Capsule and Factory Design Plan.md. October 26 M1 Reliability and ML Readiness Checkpoint records 319 controlled software checks and separate pending live scientific acceptance; that number is deliberately absent from the main talk because it does not prove this adaptive design. Current qualified review modes include historical output-only and opt-in evidence-aware review; this change preserves each selected profile rather than changing review payload authority.\n\nThe design is presentation-ready as a proposal, not specification-ready for arbitrary concurrent mutation. Open implementation decisions are explicit. No numerical benefit, complete research correctness, multi-lab deployment, malicious-code containment or day-long autonomy is established.`);
 return {slides:[5,6,7],mainSlides:6,hiddenBackups:2};
}
