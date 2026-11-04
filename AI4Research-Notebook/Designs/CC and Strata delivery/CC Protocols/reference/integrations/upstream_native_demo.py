"""Pinned native TaskTool delegation with deterministic child/tool driver.

This tests the actual framework delegation/lifecycle and local filesystem/shell
operations. It is not an LLM coding-quality or full JiuwenSwarm UI test.
"""
import argparse
import asyncio
import inspect
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import uuid

REFERENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFERENCE))
from ccv2 import Host, file_sha
from openjiuwen.core.foundation.tool import ToolCard
from openjiuwen.core.session.agent import Session
from openjiuwen.core.single_agent.schema.agent_card import AgentCard
from openjiuwen.core.sys_operation import LocalWorkConfig, OperationMode, SysOperation, SysOperationCard
from openjiuwen.harness.tools.subagent.task_tool import TaskTool


def git(workspace, *args):
    return subprocess.run(['git', '-C', str(workspace), *args], text=True, capture_output=True, check=True).stdout


def fixture(root):
    origin, worktree = root / 'origin', root / 'worktree'
    origin.mkdir(parents=True)
    git(origin, 'init')
    (origin / 'calculator.py').write_text('def add(a, b):\n    return a - b\n', encoding='utf-8')
    (origin / 'USER_NOTES.md').write_text('User original notes.\n', encoding='utf-8')
    git(origin, 'add', '.')
    git(origin, '-c', 'user.name=CC Feasibility', '-c', 'user.email=cc@example.invalid', 'commit', '-m', 'isolated fixture')
    git(origin, 'worktree', 'add', '-b', 'demo-repair', str(worktree))
    (worktree / 'USER_NOTES.md').write_text('User original notes.\nPreexisting dirty user text.\n', encoding='utf-8')
    (worktree / 'user-scratch.txt').write_text('Preexisting untracked user text.\n', encoding='utf-8')
    return worktree


async def native_repair(packet, context, evidence):
    workspace = Path(packet['resources'][packet['inputs']['workspace']]['path'])
    operation = SysOperation(SysOperationCard(id='cc_native_demo', mode=OperationMode.LOCAL,
        work_config=LocalWorkConfig(sandbox_root=[str(workspace)], restrict_to_sandbox=True,
            shell_allowlist=[sys.executable, 'python'])))

    class DeterministicChild:
        card = AgentCard(name='code_agent', description='Deterministic feasibility tool driver', id='cc-child')

        async def prepare_task_resources(self):
            evidence['prepare_calls'] += 1

        async def cleanup_task_resources(self):
            evidence['cleanup_calls'] += 1

        async def invoke(self, inputs):
            evidence['child_inputs'] = inputs
            for name, content in {
                'calculator.py': 'def add(a, b):\n    return a + b\n',
                'test_calculator.py': 'from calculator import add\nassert add(2, 3) == 5\nassert add(-2, 2) == 0\nprint("2 regression assertions passed")\n',
            }.items():
                result = await operation.fs().write_file(str(workspace / name), content)
                evidence.setdefault('file_operations', []).append(result.model_dump(mode='json'))
                assert result.code == 0, result
            command = 'python -B test_calculator.py'
            result = await operation.shell().execute_cmd(command, cwd=str(workspace), timeout=20,
                shell_type='cmd' if sys.platform == 'win32' else 'sh', environment={'PYTHONDONTWRITEBYTECODE': '1'})
            evidence['test_operation'] = result.model_dump(mode='json')
            assert result.code == 0 and result.data.exit_code == 0, result
            return {'output': 'Repaired calculator addition and passed 2 regression assertions.'}

    child = DeterministicChild()
    def create_subagent(agent_type, subsession_id, **kwargs):
        evidence['dispatch'] = {'agent_type': agent_type, 'subsession_id': subsession_id}
        assert agent_type == 'code_agent'
        return child
    parent = SimpleNamespace(create_subagent=create_subagent)
    tool = TaskTool(card=ToolCard(id='cc_task_tool', name='task_tool', description='Native upstream delegation'), parent_agent=parent)
    result = await tool.invoke({'subagent_type': 'code_agent', 'task_description': packet['inputs']['task']},
                               session=Session(session_id=packet['call']))
    evidence['task_tool_result'] = result.model_dump(mode='json')
    assert result.success, result
    output = Path(packet['output_dir']) / 'native-evidence.json'
    output.write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    return {'outcome': 'ok', 'outputs': {'evidence': {'path': output.name}, 'test': {'passed': True, 'assertions': 2}}}


def run(root):
    workspace = fixture(root)
    protected = {name: file_sha(workspace / name) for name in ('USER_NOTES.md', 'user-scratch.txt')}
    before_status = git(workspace, 'status', '--porcelain=v1', '--untracked-files=all')
    evidence = {'mode': 'real upstream TaskTool and SysOperation; deterministic child driver; no LLM',
                'prepare_calls': 0, 'cleanup_calls': 0}
    def dispatch(packet, context):
        return asyncio.run(native_repair(packet, context, evidence))
    host = Host(root / 'store', resources={'coding-workspace': {'kind': 'workspace', 'path': str(workspace)}},
                delegates={'code_agent': dispatch})
    release = host.seal(REFERENCE / 'examples' / 'native_code')
    result = host.call(release, 'repair', {'workspace': 'coding-workspace', 'task': 'Fix add so 2 + 3 is 5; preserve user notes and scratch; add and execute a regression test.'},
                       grants=['workspace.read', 'workspace.write', 'process.exec'])
    assert result['state'] == 'succeeded', result
    assert evidence['prepare_calls'] == evidence['cleanup_calls'] == 1, evidence
    assert all(file_sha(workspace / name) == digest for name, digest in protected.items())
    after_status = git(workspace, 'status', '--porcelain=v1', '--untracked-files=all')
    assert ' M calculator.py' in after_status and '?? test_calculator.py' in after_status
    return {'receipt': result, 'native_evidence': evidence, 'workspace': str(workspace),
            'status_before': before_status, 'status_after': after_status, 'protected_files_unchanged': protected,
            'diff': git(workspace, 'diff', '--', 'calculator.py'),
            'upstream_modules': {str(Path(inspect.getfile(cls))): file_sha(inspect.getfile(cls)) for cls in (TaskTool, SysOperation)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root / ('native-' + uuid.uuid4().hex[:8]))
    args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'state': 'passed', 'test': result['receipt']['outputs']['test']}))
