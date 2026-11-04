"""Render canonical .mmd definitions without restoring historical diagram text."""
from pathlib import Path
import argparse
import importlib.util
import json

V=Path(__file__).resolve().parents[3]
OUT=V/'Designs/Sandbox Lab Diagrams'
spec=importlib.util.spec_from_file_location('renderer',V/'Resources/review-batches/2026-10-26-sandbox-design-refresh/build_diagrams.py')
renderer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
manifest=json.loads((OUT/'manifest.json').read_text('utf-8'))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stem',choices=[r['stem'] for r in manifest['diagrams']])
args=parser.parse_args()
for i,row in enumerate(manifest['diagrams']):
    if args.stem and row['stem']!=args.stem:
        continue
    source=(OUT/f"{row['stem']}.mmd").read_text('utf-8')
    # Existing style is a projection detail, appended once by the renderer.
    source=source.split('    classDef work fill:')[0].rstrip()+'\n'
    manifest['diagrams'][i]=renderer.render((row['stem'],row['title'],source))
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
