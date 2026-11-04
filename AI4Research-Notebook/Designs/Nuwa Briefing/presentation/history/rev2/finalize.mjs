import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';

const root = path.dirname(fileURLToPath(import.meta.url));
const skill = 'C:/Users/m50066326/.codex/plugins/cache/openai-primary-runtime/presentations/26.1017.22135/skills/presentations';
const python = 'C:/Users/m50066326/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES = 'C:/Users/m50066326/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const reference = path.resolve(root, '../../Paper2Agent Briefing/presentation/Paper2Agent Talk rev8.pptx');
const { finalizePresentation } = await import(pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const result = await finalizePresentation({
  workspaceDir: root,
  candidatePath: path.join(root, '.build/Nuwa Talk draft.pptx'),
  finalPath: path.join(root, 'output/Nuwa Talk rev2.pptx'),
  pythonExecutable: python,
  integrityValidatorPath: path.join(skill, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(skill, 'container_tools/inspect_presentation_layout_geometry.py'),
  explicitTotalSlideCount: 10,
  requiredNativeTableOwnerSlides: [9, 10],
  requiredNativeChartOwnerSlides: [],
  layoutArgs: ['--expected-slide-size-emu', '12191695,6858000', '--validate-bullet-geometry', '--validate-heading-fit', '--require-native-table-slide', '9', '--require-native-table-slide', '10'],
  fontPolicy: { basis: 'reference', families: ['Segoe UI'], referencePath: reference, referenceSha256: createHash('sha256').update(await fs.readFile(reference)).digest('hex') },
  verifyArtifactToolImport: true,
  receiptPath: path.join(root, '.build/Nuwa Talk rev2.validation.json'),
});
console.log(JSON.stringify(result));
