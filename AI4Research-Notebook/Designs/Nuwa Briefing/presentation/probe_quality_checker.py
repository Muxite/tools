"""Reproduce the limited structural-checker finding, without evaluating persona fidelity."""
import importlib.util
import json
from pathlib import Path

root = Path(__file__).parent
checker = root / 'references/scripts__quality_check.py'
spec = importlib.util.spec_from_file_location('nuwa_quality', checker)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
placeholder = '\n'.join([
    '## Mental Models', '### Model 1: Placeholder', '### Model 2: Placeholder',
    '### Model 3: Placeholder', '## Expression DNA', '句式 词汇 幽默',
    'limitation tension paradox', '## Honest Boundary', '- a', '- b', '- c',
])
checks = [module.check_mental_models, module.check_limitations,
          module.check_expression_dna, module.check_honest_boundary,
          module.check_tensions, module.check_primary_sources]
results = {check.__name__: check(placeholder)[0] for check in checks}
record = {'repository_commit': '7812110bf7e5a2b01b6aa5a738568044121bbfa2',
          'test_date': '2026-10-22', 'input': placeholder, 'results': results,
          'passed': sum(results.values()), 'total': len(checks),
          'scope': 'Structural-checker probe only; not a persona-quality or task-performance experiment.'}
(root / 'review/checker-probe.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(results))
