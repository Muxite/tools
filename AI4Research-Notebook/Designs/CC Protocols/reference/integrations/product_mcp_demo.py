"""Pinned upstream MCP discovery keeps applications separate from callable tools."""
import argparse
import asyncio
import inspect
import json
from pathlib import Path
import shutil
import sys
import yaml

REFERENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFERENCE))
from ccv2 import Host, file_sha
from mcp_server import invoke_tool
from openjiuwen.core.foundation.tool import McpServerConfig
from openjiuwen.core.foundation.tool.mcp.client.stdio_client import StdioClient


async def run(directory):
    directory = Path(directory); directory.mkdir(parents=True)
    host = Host(directory/'store')
    observed = []
    for product_only in (False, True):
        bundle = directory/('product-only' if product_only else 'hybrid')
        shutil.copytree(REFERENCE/'examples/http_product', bundle)
        if product_only:
            declaration = yaml.safe_load((bundle/'cc.yaml').read_text())
            declaration['capabilities'].pop('inspect')
            (bundle/'cc.yaml').write_text(yaml.safe_dump(declaration), encoding='utf-8')
        release = host.prepare(bundle)
        config = McpServerConfig(server_name='cc_products', server_path=str(REFERENCE/'mcp_server.py'), client_type='stdio',
            params={'command': sys.executable, 'args': [str(REFERENCE/'mcp_server.py'), '--store', str(host.store), '--release', release]})
        client = StdioClient(config)
        assert await client.connect(), getattr(client, '_last_connect_error', None)
        try:
            tools = await client.list_tools()
            names = {tool.name for tool in tools}
            assert names == (set() if product_only else {'inspect'}), names
            record = {'product_only': product_only, 'release': release, 'tools': sorted(names), 'served_capabilities': ['api']}
            if not product_only:
                value = await invoke_tool(client, 'inspect', {}, invocation_id='product-inspection')
                if isinstance(value, str): value = json.loads(value)
                elif isinstance(value, list): value = json.loads(value[0]['text'] if isinstance(value[0], dict) else value[0].text)
                assert value['state'] == 'succeeded' and value['assessment']['verdict'] == 'not_requested', value
                record['receipt'] = value
            observed.append(record)
        finally:
            await client.disconnect()
    return {'evidence_level': 'Actual pinned OpenJiuwen StdioClient discovery and native inspection call; deterministic driver, no live LLM',
            'client_sha256': file_sha(inspect.getfile(StdioClient)), 'cases': observed}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True); args = parser.parse_args()
    result = asyncio.run(run(args.directory))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'status': 'passed', 'tool_lists': [c['tools'] for c in result['cases']]}))
