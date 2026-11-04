import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';

const root = path.dirname(fileURLToPath(import.meta.url));
const skill = 'C:/Users/m50066326/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11618/skills/presentations';
const python = 'C:/Users/m50066326/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES = 'C:/Users/m50066326/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const reference = path.resolve(root, 'output/Nuwa Talk rev2.pptx');
const { finalizePresentation } = await import(pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const result = await finalizePresentation({
  workspaceDir: root,
  candidatePath: path.join(root, '.build-orange/Nuwa Human Interface reviewed draft.pptx'),
  finalPath: path.join(root, 'output/Nuwa Talk rev3 human-interface-reviewed.pptx'),
  pythonExecutable: python,
  integrityValidatorPath: path.join(skill, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(skill, 'container_tools/inspect_presentation_layout_geometry.py'),
  explicitTotalSlideCount: 11,
  requiredNativeTableOwnerSlides: [3, 4, 10, 11],
  requiredNativeChartOwnerSlides: [],
  layoutArgs: ['--expected-slide-size-emu', '12191695,6858000', '--validate-bullet-geometry', '--validate-heading-fit', '--require-native-table-slide', '3', '--require-native-table-slide', '4', '--require-native-table-slide', '10', '--require-native-table-slide', '11'],
  fontPolicy: { basis: 'reference', families: ['Segoe UI'], referencePath: reference, referenceSha256: createHash('sha256').update(await fs.readFile(reference)).digest('hex') },
  verifyArtifactToolImport: true,
  receiptPath: path.join(root, '.build-orange/Nuwa Talk rev3 human-interface-reviewed.validation.json'),
});
console.log(JSON.stringify(result));
