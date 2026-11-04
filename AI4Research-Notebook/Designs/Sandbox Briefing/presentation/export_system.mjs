import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const runtime='C:/Users/m50066326/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const skill='C:/Users/m50066326/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11618/skills/presentations';
const root='C:/Users/m50066326/huawei/AI4Research-Notebook/Designs/Sandbox Briefing/presentation';
process.env.RUNTIME_NODE_MODULES=runtime+'/node/node_modules';
const {Presentation,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const p=Presentation.load(JSON.parse(await fs.readFile(root+'/.build-system/final-live-deck.json','utf8')));
// External live snapshots omit image bytes. Materialize the same source asset.
const refSlide=p.slides.getItem(11);
const original=refSlide.images.items[0];
const asset=await fs.readFile(root+'/references/openjiuwen-figure-2.png');
if(original){const found=await p.inspect({select:'$.slides[11].elements[*]',include:['id','kind']});p.delete(found.records.filter(x=>x.kind==='image').map(x=>x.id));}
refSlide.images.add({blob:asset.buffer.slice(asset.byteOffset,asset.byteOffset+asset.byteLength),contentType:'image/png',position:{left:48,top:150,width:790,height:494},fit:'contain',alt:'Original OpenJiuwen Figure 2: shared execution, composability and runtime adaptation'});
await fs.mkdir(root+'/output',{recursive:true});
const candidate=root+'/.build-system/candidate.pptx';
await (await PresentationFile.exportPptx(p)).save(candidate);
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const owners=[10,11,14,15,16];
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:root+'/output/AI4Research Sandbox Design rev2.pptx',pythonExecutable:runtime+'/python/python.exe',integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',explicitTotalSlideCount:16,requiredNativeTableOwnerSlides:owners,requiredNativeChartOwnerSlides:[],layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...owners.flatMap(n=>['--require-native-table-slide',String(n)])],fontPolicy:{basis:'design',families:['Segoe UI']},verifyArtifactToolImport:true,receiptPath:root+'/.build-system/embedded-assets.validation.json'});
console.log(JSON.stringify(result));
