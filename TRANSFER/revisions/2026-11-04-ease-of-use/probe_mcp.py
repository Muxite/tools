"""Actual pinned upstream-client check of result-first dispatch/session grants."""
import argparse
import asyncio
import inspect
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
REFERENCE = ROOT / 'AI4Research-Notebook/Designs/CC and Strata delivery/CC Protocols/reference'
sys.path.insert(0, str(REFERENCE))
from ccv2 import Host, file_sha
from mcp_server import invoke_tool
from openjiuwen.core.foundation.tool import McpServerConfig
from openjiuwen.core.foundation.tool.mcp.client.stdio_client import StdioClient


async def run(store):
    release = Host(store).seal(REFERENCE / 'examples/easy_results')
    config = McpServerConfig(server_name='cc_ease', server_path=str(REFERENCE / 'mcp_server.py'), client_type='stdio',
        params={'command': sys.executable, 'args': [str(REFERENCE / 'mcp_server.py'), '--store', str(store),
                                                   '--release', release, '--grant', 'workspace.write']})
    client = StdioClient(config)
    assert await client.connect(), getattr(client, '_last_connect_error', None)
    try:
        tools = await client.list_tools()
        assert {t.name for t in tools} == {'produce', 'review'}
        args = {'task': 'Save useful result', 'context': {'score': 0.25, 'additional': {'untyped': ['metadata']}}}
        value = await invoke_tool(client, 'produce', args, 'ease.produce')
        produced = json.loads(value) if isinstance(value, str) else value
        assert produced['state'] == 'succeeded' and produced['assessment']['verdict'] == 'not_requested'
        assert produced['effects']['granted'] == []
        repeated = await invoke_tool(client, 'produce', args, 'ease.produce')
        repeated = json.loads(repeated) if isinstance(repeated, str) else repeated
        assert repeated['call'] == produced['call']
        value = await invoke_tool(client, 'review', {'result': produced['outputs']['result'], 'policy': {'minimum_score': 0.8}}, 'ease.review')
        review = json.loads(value) if isinstance(value, str) else value
        assert review['state'] == 'succeeded' and review['outputs']['assessment']['accepted'] is False
        return {'scope': 'Real pinned upstream StdioClient, deterministic caller; no live model or GPU',
                'client_source_sha256': file_sha(inspect.getfile(StdioClient)), 'release': release,
                'produce': produced, 'review': review, 'stable_replay': True,
                'session_grant_not_forwarded_to_unrelated_capability': produced['effects']['granted'] == []}
    finally:
        await client.disconnect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--store', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = asyncio.run(run(args.store))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'state': result['produce']['state'], 'checks': result['produce']['assessment']['verdict'], 'stable_replay': True}))
