"""Real pinned OpenJiuwen StdioClient -> generated CC MCP -> native MAPIE."""
import argparse
import asyncio
import inspect
import json
from pathlib import Path
import sys

REFERENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REFERENCE))
from ccv2 import Host, file_sha
from mcp_server import invoke_tool
from mapie_demo import synthetic_data
from openjiuwen.core.foundation.tool import McpServerConfig
from openjiuwen.core.foundation.tool.mcp.client.stdio_client import StdioClient


def receipt(value):
    if isinstance(value, str):
        return json.loads(value)
    if isinstance(value, list):
        return json.loads(value[0]['text'] if isinstance(value[0], dict) else value[0].text)
    if isinstance(value, dict) and 'state' in value:
        return value
    raise ValueError('unexpected upstream MCP result: ' + repr(value))


async def run(store):
    release = Host(store).seal(REFERENCE / 'examples' / 'mapie')
    config = McpServerConfig(server_name='cc_mapie', server_path=str(REFERENCE / 'mcp_server.py'), client_type='stdio',
        params={'command': sys.executable, 'args': [str(REFERENCE / 'mcp_server.py'), '--store', str(store), '--release', release]})
    client = StdioClient(config)
    assert await client.connect(), getattr(client, '_last_connect_error', None)
    try:
        tools = await client.list_tools()
        assert {tool.name for tool in tools} == {'fit_calibrate', 'predict_intervals', 'evaluate'}
        schemas = {tool.name: tool.input_params for tool in tools}
        data, points, labels = synthetic_data()
        fit = receipt(await invoke_tool(client, 'fit_calibrate', {'data': data}, invocation_id='mcp-fit-20261104'))
        assert fit['state'] == 'succeeded', fit
        predict = receipt(await invoke_tool(client, 'predict_intervals', {'model': fit['outputs']['model'], 'data': points},
                                                                       invocation_id='mcp-predict-20261104'))
        assert predict['state'] == 'succeeded', predict
        evaluation = receipt(await invoke_tool(client, 'evaluate', {'intervals': predict['outputs']['intervals'], 'labels': labels},
                                                                 invocation_id='mcp-evaluate-20261104'))
        assert evaluation['state'] == 'succeeded', evaluation
        replay = receipt(await invoke_tool(client, 'evaluate', {'intervals': predict['outputs']['intervals'], 'labels': labels},
                                                             invocation_id='mcp-evaluate-20261104'))
        assert replay['call'] == evaluation['call']
        return {'mode': 'real upstream StdioClient stdio; deterministic client arguments; no LLM',
                'client_source': str(Path(inspect.getfile(StdioClient))), 'client_sha256': file_sha(inspect.getfile(StdioClient)),
                'release': release, 'schemas': schemas, 'fit': fit, 'predict': predict, 'evaluate': evaluation,
                'stable_key_replay_same_call': replay['call'] == evaluation['call']}
    finally:
        await client.disconnect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--store', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = asyncio.run(run(args.store))
    args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'state': 'passed', 'metrics': result['evaluate']['outputs']}))
