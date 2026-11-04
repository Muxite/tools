"""CC v2 feasibility host. Trusted-local execution is not a security boundary."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import importlib.metadata
import inspect
import json
import marshal
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time
import uuid

import yaml
from jsonschema import Draft202012Validator


class CCError(ValueError):
    def __init__(self, code, message, path=''):
        self.code, self.path = code, path
        super().__init__(message)

    def record(self):
        return {'code': self.code, 'path': self.path, 'message': str(self)}


def require(condition, code, message, path=''):
    if not condition:
        raise CCError(code, message, path)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def callable_identity(callback):
    """Identify host adapter code without serializing closures or secret config."""
    code = getattr(callback, '__code__', None)
    if code is None:
        code = getattr(getattr(callback, '__call__', None), '__code__', None)
    result = {'module': getattr(callback, '__module__', type(callback).__module__),
              'name': getattr(callback, '__qualname__', type(callback).__qualname__),
              'code_sha256': sha(marshal.dumps(code)) if code is not None else None}
    try:
        source = inspect.getsourcefile(callback if inspect.isfunction(callback) else type(callback))
        if source and Path(source).is_file():
            result['source_sha256'] = file_sha(source)
    except (TypeError, OSError):
        pass
    result['limits'] = 'Adapter code identity; closure state and remote model/provider configuration require host-specific binding evidence'
    return result


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for k, v in node.value:
        key = loader.construct_object(k)
        require(isinstance(key, str), 'INVALID_DECLARATION', 'Mapping keys must be strings')
        require(key not in result, 'DUPLICATE_ID', f'Duplicate key: {key}')
        result[key] = loader.construct_object(v)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
ID = re.compile(r'^[a-z][a-z0-9._-]*$')
NEEDS = {'workspace', 'python', 'process', 'gpu', 'environment'}
EFFECTS = {'workspace.read', 'workspace.write', 'process.exec', 'process.attach', 'process.control', 'gpu.use', 'dependency.install', 'network.request', 'model.invoke', 'git.publish', 'deploy'}
STATES = {'running', 'succeeded', 'failed', 'blocked', 'cancelled', 'unknown'}
IGNORED = {'.git', '.venv', '__pycache__', '.pytest_cache', '.cc-state', '.mypy_cache', '.ruff_cache'}


def fields(value, allowed, required=(), path=''):
    require(isinstance(value, dict), 'INVALID_DECLARATION', 'Expected an object', path)
    require(set(value) <= set(allowed), 'UNKNOWN_FIELD', f'Unknown fields: {sorted(set(value)-set(allowed))}', path)
    require(set(required) <= set(value), 'MISSING_FIELD', f'Missing fields: {sorted(set(required)-set(value))}', path)


def port(value, defs):
    if isinstance(value, str) and value.startswith('$'):
        require(value[1:] in defs, 'UNRESOLVED_REFERENCE', value)
        return port(defs[value[1:]], {})
    result = {'kind': value} if isinstance(value, str) else deepcopy(value)
    fields(result, {'kind', 'optional', 'schema', 'description', 'media_type'}, {'kind'})
    require(result['kind'] in {'json', 'text', 'artifact', 'handle'}, 'UNSUPPORTED_TYPE', str(result['kind']))
    result.setdefault('optional', False)
    require(type(result['optional']) is bool, 'INVALID_DECLARATION', 'optional must be boolean')
    if 'schema' in result:
        require(result['kind'] in {'json', 'text'}, 'INVALID_DECLARATION', 'Schema applies to JSON/text ports')
        Draft202012Validator.check_schema(result['schema'])
        require(not re.search(r'"\$(?:ref|dynamicRef)"\s*:\s*"(?!#)', json.dumps(result['schema'])),
                'UNRESOLVED_REFERENCE', 'External JSON Schema references must be bundled into the schema')
    if 'media_type' in result:
        require(result['kind'] == 'artifact' and isinstance(result['media_type'], str), 'INVALID_DECLARATION', 'media_type requires an artifact')
    return result


def normalize(raw):
    fields(raw, {'cc', 'id', 'version', 'bindings', 'capabilities', 'defs'}, {'cc', 'id', 'version', 'bindings', 'capabilities'})
    require(raw['cc'] == '2', 'UNSUPPORTED_VERSION', 'Explicit v2 declaration required; migrate v1 first')
    require(isinstance(raw['id'], str) and ID.fullmatch(raw['id']), 'INVALID_ID', 'Invalid capsule ID')
    require(isinstance(raw['version'], str) and re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', raw['version']), 'INVALID_VERSION', 'Use major.minor.patch')
    result = deepcopy(raw)
    result.setdefault('defs', {})
    require(isinstance(result['defs'], dict), 'INVALID_DECLARATION', 'defs must be a mapping')
    for name, definition in result['defs'].items():
        require(ID.fullmatch(name), 'INVALID_ID', name)
        port(definition, {})
    require(isinstance(result['bindings'], dict) and 'default' in result['bindings'], 'MISSING_BINDING', 'bindings.default is required')
    for name, binding in result['bindings'].items():
        require(ID.fullmatch(name), 'INVALID_ID', name)
        require(isinstance(binding, dict), 'INVALID_DECLARATION', 'Binding must be an object')
        kind = binding.get('kind')
        if kind in {'native', 'image'}:
            fields(binding, {'kind', 'command', 'image', 'lock'}, {'kind', 'command'} | ({'image'} if kind == 'image' else set()))
            require(isinstance(binding['command'], list) and bool(binding['command']) and all(isinstance(x, str) and x for x in binding['command']), 'INVALID_BINDING', 'command must be a nonempty argument vector')
            require(kind == 'image' or 'image' not in binding, 'INVALID_BINDING', 'Native binding cannot have image')
            if kind == 'image':
                require(isinstance(binding['image'], str) and re.fullmatch(r'(?:[^\s]+@)?sha256:[0-9a-f]{64}', binding['image']), 'MUTABLE_BINDING', 'Resolve image to immutable digest or local image ID')
            if 'lock' in binding:
                require(isinstance(binding['lock'], str) and bool(binding['lock']), 'INVALID_BINDING', 'lock is a bundle-relative path')
        elif kind == 'jiuwenswarm':
            fields(binding, {'kind', 'agent'}, {'kind', 'agent'})
            require(isinstance(binding['agent'], str) and bool(binding['agent']), 'INVALID_BINDING', 'agent must name a host-registered delegate')
        else:
            raise CCError('UNSUPPORTED_BINDING', str(kind))
    require(isinstance(result['capabilities'], dict) and bool(result['capabilities']), 'INVALID_DECLARATION', 'Provide at least one capability')
    for name, cap in result['capabilities'].items():
        require(ID.fullmatch(name), 'INVALID_ID', name)
        fields(cap, {'does', 'takes', 'gives', 'needs', 'changes', 'guarantees', 'using'}, {'does'})
        require(isinstance(cap['does'], str) and bool(cap['does'].strip()), 'INVALID_DECLARATION', f'{name}.does must explain the action')
        cap.setdefault('using', 'default')
        require(cap['using'] in result['bindings'], 'UNRESOLVED_REFERENCE', f'{name}.using')
        for side in ('takes', 'gives'):
            cap.setdefault(side, {})
            require(isinstance(cap[side], dict), 'INVALID_DECLARATION', f'{name}.{side} must be a port mapping')
            for pname, definition in cap[side].items():
                require(ID.fullmatch(pname), 'INVALID_ID', pname)
                port(definition, result['defs'])
        for field in ('needs', 'changes', 'guarantees'):
            cap.setdefault(field, [])
            require(isinstance(cap[field], list) and all(isinstance(x, str) for x in cap[field]) and len(cap[field]) == len(set(cap[field])), 'INVALID_DECLARATION', f'{name}.{field} must be unique strings')
        require(set(cap['needs']) <= NEEDS, 'UNSUPPORTED_PREREQUISITE', str(set(cap['needs']) - NEEDS))
        require(set(cap['changes']) <= EFFECTS, 'UNSUPPORTED_EFFECT', str(set(cap['changes']) - EFFECTS))
        # Guarantee IDs are obligations. An unavailable checker blocks rather than passes.
    encoded(result)
    return result


def load(path):
    text = Path(path).read_text(encoding='utf-8-sig')
    require(not any(isinstance(t, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken, yaml.tokens.TagToken)) for t in yaml.scan(text)), 'INVALID_DECLARATION', 'Aliases, anchors and tags are unsupported')
    try:
        return normalize(yaml.load(text, Loader=UniqueLoader))
    except (yaml.YAMLError, TypeError) as e:
        raise CCError('INVALID_DECLARATION', str(e)) from e


def contained(root, relative):
    root = Path(root).resolve()
    require(isinstance(relative, str) and bool(relative) and not Path(relative).is_absolute(), 'INVALID_PATH', str(relative))
    target = root / relative
    require(root in target.resolve().parents, 'INVALID_PATH', relative)
    require(not any(p.is_symlink() for p in [target, *list(target.parents)[:len(target.parts)-len(root.parts)]]), 'INVALID_PATH', 'Links are unsupported')
    return target


def tree_files(root):
    rows = []
    for path in sorted(Path(root).rglob('*')):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts):
            continue
        require(not path.is_symlink(), 'INVALID_PATH', f'Source links unsupported: {relative}')
        if path.is_file():
            rows.append({'path': relative.as_posix(), 'sha256': file_sha(path), 'size': path.stat().st_size, 'mode': stat.S_IMODE(path.stat().st_mode)})
    return rows


def snapshot(root):
    rows = tree_files(root)
    git = {}
    for key, arguments in [('head', ['rev-parse', 'HEAD']), ('index_path', ['rev-parse', '--git-path', 'index'])]:
        proc = subprocess.run(['git', '-C', str(root), *arguments], capture_output=True, text=True)
        if proc.returncode == 0:
            git[key] = proc.stdout.strip()
    if 'index_path' in git:
        index = Path(git.pop('index_path'))
        if not index.is_absolute():
            index = Path(root) / index
        git['index_sha256'] = file_sha(index) if index.is_file() else None
    result = {'files': rows, 'git': git}
    return dict(result, digest=sha(encoded(result)))


def differences(before, after):
    a = {r['path']: r for r in before['files']}
    b = {r['path']: r for r in after['files']}
    changed = [{'path': p, 'before': a.get(p), 'after': b.get(p)} for p in sorted(set(a) | set(b)) if a.get(p) != b.get(p)]
    if before.get('git') != after.get('git'):
        changed.append({'path': '<git-state>', 'before': before.get('git'), 'after': after.get('git')})
    return changed


class Host:
    def __init__(self, store, resources=None, delegates=None, checkers=None, python=None):
        self.store = Path(store).resolve()
        self.store.mkdir(parents=True, exist_ok=True)
        self.resources = resources or {}
        self.delegates = delegates or {}
        self.checkers = checkers or {}
        self.python = python or sys.executable
        with self.db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS calls (key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, receipt TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS leases (resource TEXT PRIMARY KEY, call_id TEXT NOT NULL)')

    @contextmanager
    def db(self):
        db = sqlite3.connect(self.store / 'calls.sqlite', timeout=30)
        try:
            yield db
            db.commit()
        finally:
            db.close()

    def seal(self, bundle):
        bundle = Path(bundle).resolve()
        decl = load(bundle / 'cc.yaml')
        rows = tree_files(bundle)
        for binding in decl['bindings'].values():
            if 'lock' in binding:
                require(contained(bundle, binding['lock']).is_file(), 'MISSING_MATERIAL', binding['lock'])
        executables = {}
        for name, binding in decl['bindings'].items():
            if binding['kind'] in {'native', 'image'}:
                for arg in binding['command']:
                    if arg.startswith('{bundle}/') or arg.startswith('{bundle}\\'):
                        path = contained(bundle, arg[len('{bundle}')+1:])
                        require(path.is_file(), 'MISSING_IMPLEMENTATION', 'Missing bundled command material: ' + arg)
            if binding['kind'] != 'native':
                continue
            for arg in binding['command'][1:]:
                require(not Path(arg).is_absolute(), 'UNSEALED_IMPLEMENTATION', 'Put implementation files in the bundle and use {bundle}; absolute external arguments are unsupported')
            command = binding['command'][0].replace('{python}', self.python).replace('{bundle}', str(bundle))
            executable = shutil.which(command) or (str(Path(command).resolve()) if Path(command).is_file() else None)
            require(executable, 'MISSING_IMPLEMENTATION', command)
            executables[name] = {'path': str(Path(executable).resolve()), 'sha256': file_sha(executable)}
        manifest = {'cc': '2', 'declaration': decl, 'files': rows, 'executables': executables}
        release = sha(encoded(manifest))
        destination = self.store / 'releases' / release
        if not destination.exists():
            destination.parent.mkdir(exist_ok=True)
            stage = Path(tempfile.mkdtemp(prefix='.seal-', dir=destination.parent))
            try:
                for row in rows:
                    out = stage / 'bundle' / row['path']
                    out.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(bundle / row['path'], out)
                    require(file_sha(out) == row['sha256'], 'SOURCE_CHANGED', row['path'])
                (stage / 'manifest.json').write_bytes(encoded(manifest))
                try:
                    stage.rename(destination)
                except FileExistsError:
                    shutil.rmtree(stage)
            except Exception:
                shutil.rmtree(stage, ignore_errors=True)
                raise
        return release

    def release(self, release):
        require(isinstance(release, str) and re.fullmatch('[0-9a-f]{64}', release), 'INVALID_RELEASE', str(release))
        root = self.store / 'releases' / release
        require((root / 'manifest.json').is_file(), 'MISSING_RELEASE', release)
        data = (root / 'manifest.json').read_bytes()
        require(sha(data) == release, 'DIGEST_MISMATCH', 'Release manifest changed')
        manifest = json.loads(data)
        for row in manifest['files']:
            path = contained(root / 'bundle', row['path'])
            require(path.is_file() and file_sha(path) == row['sha256'], 'DIGEST_MISMATCH', row['path'])
        for name, executable in manifest.get('executables', {}).items():
            binding = manifest['declaration']['bindings'][name]
            if '{bundle}' in binding['command'][0]:
                continue
            path = Path(executable['path'])
            require(path.is_file() and file_sha(path) == executable['sha256'], 'ENVIRONMENT_CHANGED', 'Native executable changed; seal a new release')
        return manifest['declaration'], root / 'bundle'

    def put_artifact(self, path):
        path = Path(path)
        digest = file_sha(path)
        destination = self.store / 'artifacts' / digest
        destination.parent.mkdir(exist_ok=True)
        if not destination.exists():
            shutil.copyfile(path, destination)
        require(file_sha(destination) == digest, 'DIGEST_MISMATCH', 'Stored artifact differs')
        return {'uri': destination.as_uri(), 'sha256': digest}

    def artifact_path(self, ref):
        fields(ref, {'uri', 'sha256'}, {'uri', 'sha256'})
        require(isinstance(ref['sha256'], str) and re.fullmatch('[0-9a-f]{64}', ref['sha256']), 'INVALID_INPUT', 'Invalid artifact digest')
        # Local experiment host accepts local files only; no hidden network downloads.
        from urllib.parse import urlparse, unquote
        parsed = urlparse(ref['uri'])
        require(parsed.scheme in {'file', ''} and not parsed.netloc, 'UNSUPPORTED_LOCATOR', 'Stage remote artifacts explicitly before calling')
        name = unquote(parsed.path) if parsed.scheme == 'file' else ref['uri']
        if os.name == 'nt' and re.match(r'^/[A-Za-z]:', name):
            name = name[1:]
        path = Path(name).resolve()
        require(path.is_file() and not path.is_symlink(), 'MISSING_ARTIFACT', str(path))
        require(file_sha(path) == ref['sha256'], 'DIGEST_MISMATCH', str(path))
        return path

    def validate_value(self, spec, value, output=False, outdir=None):
        kind = spec['kind']
        if kind == 'text':
            require(isinstance(value, str), 'INVALID_OUTPUT' if output else 'INVALID_INPUT', 'Expected text')
        elif kind == 'json':
            try:
                encoded(value)
            except (TypeError, ValueError) as e:
                raise CCError('INVALID_INPUT', str(e)) from e
        elif kind == 'handle':
            require(isinstance(value, str) and value in self.resources, 'MISSING_RESOURCE', 'Host-issued handle required')
        elif kind == 'artifact':
            if output:
                fields(value, {'path'}, {'path'})
                path = contained(outdir, value['path'])
                require(path.is_file() and not path.is_symlink(), 'INVALID_OUTPUT', 'Artifact must be an ordinary output file')
                return self.put_artifact(path)
            self.artifact_path(value)
        if 'schema' in spec:
            errors = list(Draft202012Validator(spec['schema']).iter_errors(value))
            require(not errors, 'INVALID_OUTPUT' if output else 'INVALID_INPUT', errors[0].message if errors else '')
        return value

    def status(self, key):
        with self.db() as db:
            row = db.execute('SELECT receipt FROM calls WHERE key=?', (key,)).fetchone()
        require(row is not None, 'UNKNOWN_CALL', key)
        return json.loads(row[0])

    def reconcile(self, key, *, stopped, note):
        """Single-user operator attestation; never converts uncertain results to success."""
        require(stopped is True and isinstance(note, str) and bool(note.strip()), 'RECONCILIATION_REQUIRED', 'Confirm execution stopped and describe actual effects')
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT receipt FROM calls WHERE key=?', (key,)).fetchone()
            require(row is not None, 'UNKNOWN_CALL', key)
            receipt = json.loads(row[0])
            require(receipt['state'] in {'running', 'unknown'}, 'INVALID_STATE', 'Only uncertain/nonterminal calls require reconciliation')
            event = {'previous_state': receipt['state'], 'previous_reason': receipt['reason'], 'stopped': True, 'operator_note': note, 'recorded': time.time()}
            receipt.setdefault('reconciliations', []).append(event)
            receipt.update(state='failed', reason='RECONCILED_STOP')
            db.execute('UPDATE calls SET receipt=? WHERE key=?', (json.dumps(receipt), key))
            db.execute('DELETE FROM leases WHERE call_id=?', (receipt['call'],))
        path = self.store / 'attempts' / receipt['call'] / ('reconciliation-' + str(len(receipt['reconciliations'])) + '.json')
        path.write_bytes(encoded(receipt))
        return receipt

    def call(self, release, capability, inputs, key=None, grants=(), timeout=60):
        key = key or str(uuid.uuid4())
        require(isinstance(key, str) and bool(key) and len(key) <= 256, 'INVALID_KEY', 'Nonempty bounded invocation key required')
        require(isinstance(inputs, dict), 'INVALID_INPUT', 'inputs must be an object')
        require(isinstance(timeout, (int, float)) and not isinstance(timeout, bool) and 0 < timeout <= 86400, 'INVALID_LIMIT', 'timeout must be between 0 and 86400 seconds')
        bound_resources = deepcopy(self.resources)
        request = {'release': release, 'capability': capability, 'inputs': inputs, 'grants': sorted(set(grants)), 'resources': bound_resources, 'timeout': timeout}
        try:
            fingerprint = sha(encoded(request))
        except (TypeError, ValueError) as e:
            raise CCError('INVALID_INPUT', 'Call must contain finite JSON values: ' + str(e)) from e
        receipt = {'cc': '2', 'call': str(uuid.uuid4()), 'key': key, 'release': release, 'capability': capability, 'attempt': 1,
                   'state': 'running', 'completeness': 'none', 'reason': 'STARTED', 'outputs': {},
                   'assessment': {'verdict': 'not_requested', 'checks': []}, 'provenance': {},
                   'effects': {'declared': [], 'granted': sorted(set(grants)), 'observed': [], 'assurance': 'trusted_local',
                               'enforced': ['selected_capability', 'grant_admission', 'artifact_integrity', 'workspace_lease'],
                               'observation_limits': ['No OS-wide effect monitoring in trusted-local mode', 'Dependency directories/caches excluded from file snapshots; host-interpreter package versions recorded; child runtimes need their own evidence', 'Workspace Git HEAD/index and ordinary file modes recorded; no implied publication authorization']}, 'diagnostics': []}
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            existing = db.execute('SELECT fingerprint,receipt FROM calls WHERE key=?', (key,)).fetchone()
            if existing:
                require(existing[0] == fingerprint, 'KEY_CONFLICT', 'Same key cannot change the bound request')
                return json.loads(existing[1])
            db.execute('INSERT INTO calls VALUES (?,?,?)', (key, fingerprint, json.dumps(receipt)))
        workspace_before = {}
        dispatched = False
        attempt = self.store / 'attempts' / receipt['call']
        attempt.mkdir(parents=True)
        try:
            decl, bundle = self.release(release)
            require(capability in decl['capabilities'], 'UNKNOWN_CAPABILITY', capability)
            cap = decl['capabilities'][capability]
            binding = decl['bindings'][cap['using']]
            receipt['effects']['declared'] = cap['changes']
            require(set(grants) <= set(cap['changes']), 'UNDECLARED_EFFECT', 'Grant exceeds selected capability effects')
            require(set(cap['changes']) <= set(grants), 'DENIED', 'Explicit grants required for declared effects')
            require(not set(cap['guarantees']) - set(self.checkers), 'CHECKER_UNAVAILABLE', str(set(cap['guarantees'])-set(self.checkers)))
            require(set(inputs) <= set(cap['takes']), 'INVALID_INPUT', 'Unknown input ports')
            missing = [p for p, t in cap['takes'].items() if not port(t, decl['defs'])['optional'] and p not in inputs]
            require(not missing, 'INVALID_INPUT', f'Missing input ports: {missing}')
            staged = deepcopy(inputs)
            outdir, indir = attempt / 'out', attempt / 'in'
            outdir.mkdir()
            indir.mkdir()
            resources = {}
            for pname, value in inputs.items():
                spec = port(cap['takes'][pname], decl['defs'])
                self.validate_value(spec, value)
                if spec['kind'] == 'artifact':
                    source = self.artifact_path(value)
                    target = indir / pname
                    shutil.copyfile(source, target)
                    require(file_sha(target) == value['sha256'], 'DIGEST_MISMATCH', 'Artifact changed during staging')
                    staged[pname] = dict(value, path=str(target))
                elif spec['kind'] == 'handle':
                    resource = deepcopy(bound_resources[value])
                    require(resource.get('kind') in {'workspace', 'process', 'gpu', 'environment', 'service'}, 'UNSUPPORTED_RESOURCE', str(resource.get('kind')))
                    if resource['kind'] == 'workspace':
                        require(set(cap['changes']) & {'workspace.read', 'workspace.write'}, 'DENIED', 'Workspace handle requires workspace access declaration')
                        path = Path(resource['path']).resolve()
                        require(path.is_dir(), 'MISSING_RESOURCE', str(path))
                        resource['path'] = str(path)
                        with self.db() as db:
                            db.execute('BEGIN IMMEDIATE')
                            current = os.path.normcase(str(path))
                            for other, owner in db.execute('SELECT resource,call_id FROM leases'):
                                if owner == receipt['call']:
                                    continue
                                other = os.path.normcase(other)
                                overlap = os.path.commonpath([current, other]) in {current, other} if Path(current).drive == Path(other).drive else False
                                require(not overlap, 'RESOURCE_BUSY', 'Overlapping workspace has an active or unreconciled call')
                            db.execute('INSERT OR IGNORE INTO leases VALUES (?,?)', (str(path), receipt['call']))
                        workspace_before[value] = snapshot(path)
                    resources[value] = resource
            for need in set(cap['needs']) - {'python'}:
                require(any(r['kind'] == need for r in resources.values()), 'MISSING_RESOURCE', f'{need} prerequisite requires a host-bound handle input')
            packet = {'call': receipt['call'], 'attempt': 1, 'capability': capability, 'inputs': staged, 'output_dir': str(outdir), 'resources': resources}
            receipt['provenance'] = {'binding': binding, 'started': time.time(), 'inputs': deepcopy(inputs),
                                     'source_release': release, 'python': {'path': self.python, 'sha256': file_sha(self.python)},
                                     'workspace_before': workspace_before,
                                     'packages': sorted([d.metadata['Name'], d.version] for d in importlib.metadata.distributions() if d.metadata['Name'])}
            (attempt / 'request.json').write_bytes(encoded(request))
            if binding['kind'] == 'jiuwenswarm':
                require(binding['agent'] in self.delegates, 'MISSING_DELEGATE', 'Host must register native agent dispatch')
                receipt['provenance']['delegate'] = callable_identity(self.delegates[binding['agent']])
                dispatched = True
                result = self.delegates[binding['agent']](packet, {'grants': list(grants), 'timeout': timeout, 'release': release, 'attempt_dir': str(attempt)})
                require(time.time() - receipt['provenance']['started'] <= timeout, 'EXECUTION_UNKNOWN', 'Delegate exceeded deadline; reconcile native session')
                receipt['effects']['assurance'] = 'native_host_policy'
            else:
                command = [arg.replace('{python}', self.python).replace('{bundle}', str(bundle)) for arg in binding['command']]
                if binding['kind'] == 'native':
                    manifest = json.loads((bundle.parent / 'manifest.json').read_bytes())
                    executable = manifest.get('executables', {}).get(cap['using'])
                    require(executable is not None, 'UNSEALED_IMPLEMENTATION', 'Reseal legacy reference-host releases to pin native executable')
                    if '{bundle}' not in binding['command'][0]:
                        command[0] = executable['path']
                    receipt['provenance']['resolved_executable'] = {'path': command[0], 'sha256': file_sha(command[0])}
                env = dict(os.environ, CC_OUTPUT_DIR=str(outdir), CC_BUNDLE_DIR=str(bundle), PYTHONUTF8='1')
                cwd = str(attempt)
                if binding['kind'] == 'image':
                    receipt['effects']['assurance'] = 'container'
                    receipt['effects']['enforced'] += ['container_filesystem_mounts', 'container_capability_drop']
                    receipt['effects']['observation_limits'][0] = 'No process-level syscall audit; filesystem and network restrictions enforced by Docker'
                    packet['output_dir'] = '/cc/out'
                    for pname, value in staged.items():
                        if port(cap['takes'][pname], decl['defs'])['kind'] == 'artifact':
                            value['path'] = '/cc/in/' + pname
                    command = ['docker', 'run', '--rm', '--name', 'cc-' + receipt['call'], '--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges',
                               '--tmpfs', '/tmp', '--mount', f'type=bind,src={bundle},dst=/cc/bundle,readonly',
                               '--mount', f'type=bind,src={indir},dst=/cc/in,readonly', '--mount', f'type=bind,src={outdir},dst=/cc/out',
                               '-e', 'CC_OUTPUT_DIR=/cc/out', '-e', 'PYTHONDONTWRITEBYTECODE=1']
                    if 'network.request' not in grants:
                        command += ['--network', 'none']
                        receipt['effects']['enforced'].append('network_disabled')
                    for index, (handle, resource) in enumerate(resources.items()):
                        require(resource['kind'] == 'workspace', 'UNSUPPORTED_RESOURCE', 'Container process/device resources require a qualified provider; no implicit host attachment')
                        mount = f'/cc/resources/{index}'
                        command += ['--mount', f'type=bind,src={resource["path"]},dst={mount}' + ('' if 'workspace.write' in grants else ',readonly')]
                        packet['resources'][handle]['path'] = mount
                    image_command = [a.replace('{bundle}', '/cc/bundle').replace('{python}', 'python') for a in binding['command']]
                    command += ['-i', binding['image'], *image_command]
                receipt['provenance']['command'] = command
                dispatched = True
                try:
                    process = subprocess.run(command, input=encoded(packet), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=env, timeout=timeout)
                except subprocess.TimeoutExpired as e:
                    (attempt / 'stderr.log').write_bytes(e.stderr or b'')
                    if binding['kind'] == 'image':
                        stopped = subprocess.run(['docker', 'rm', '-f', 'cc-' + receipt['call']], capture_output=True, timeout=20)
                        require(stopped.returncode == 0, 'EXECUTION_UNKNOWN', 'Container stop could not be confirmed')
                    # Native grandchildren may survive direct-process termination.
                    raise CCError('EXECUTION_UNKNOWN' if binding['kind'] == 'native' else 'DEADLINE', 'Deadline reached; no automatic replay') from e
                (attempt / 'stdout.log').write_bytes(process.stdout)
                (attempt / 'stderr.log').write_bytes(process.stderr)
                try:
                    result = json.loads(process.stdout)
                except (ValueError, UnicodeDecodeError) as e:
                    raise CCError('INVALID_OUTPUT' if process.returncode == 0 else 'PROCESS_FAILED', 'Expected one JSON result; inspect attempt logs') from e
                require((process.returncode == 0) == (result.get('outcome') in {'ok', 'partial'}), 'PROCESS_FAILED', 'Exit status contradicts reported outcome')
            fields(result, {'outcome', 'outputs', 'reason', 'error'}, {'outcome'})
            require(result['outcome'] in {'ok', 'partial', 'error'}, 'INVALID_OUTPUT', 'Unknown process outcome')
            if result['outcome'] == 'error':
                raise CCError(result.get('error', {}).get('code', 'TOOL_ERROR'), result.get('error', {}).get('message', 'Tool reported failure'))
            require(isinstance(result.get('outputs'), dict), 'INVALID_OUTPUT', 'outputs must be an object')
            require(set(result['outputs']) <= set(cap['gives']), 'INVALID_OUTPUT', 'Undeclared output ports')
            if result['outcome'] == 'ok':
                require(all(p in result['outputs'] or port(t, decl['defs'])['optional'] for p, t in cap['gives'].items()), 'INVALID_OUTPUT', 'Missing required output')
            else:
                require(isinstance(result.get('reason'), str) and bool(result['reason']), 'INVALID_OUTPUT', 'Partial result needs a reason')
            for pname, value in result['outputs'].items():
                receipt['outputs'][pname] = self.validate_value(port(cap['gives'][pname], decl['defs']), value, output=True, outdir=outdir)
            receipt.update(state='succeeded', completeness='complete' if result['outcome'] == 'ok' else 'partial', reason='COMPLETED' if result['outcome'] == 'ok' else 'PARTIAL_OUTPUT')
            if result['outcome'] == 'partial':
                receipt['diagnostics'].append({'code': 'PARTIAL_OUTPUT', 'message': result['reason']})
            for check in cap['guarantees']:
                observed = self.checkers[check](receipt, packet)
                require(observed in {'PASS', 'FAIL', 'INCONCLUSIVE'}, 'INVALID_ASSESSMENT', check)
                receipt['assessment']['checks'].append({'id': check, 'verdict': observed, 'checker': callable_identity(self.checkers[check])})
            if cap['guarantees']:
                verdicts = [c['verdict'] for c in receipt['assessment']['checks']]
                receipt['assessment']['verdict'] = 'failed' if 'FAIL' in verdicts else 'inconclusive' if 'INCONCLUSIVE' in verdicts else 'passed'
        except CCError as e:
            receipt.update(state='unknown' if e.code in {'EXECUTION_UNKNOWN', 'EFFECT_UNKNOWN'} else 'failed' if dispatched else 'blocked', reason=e.code)
            receipt['completeness'] = 'partial' if receipt['outputs'] else 'none'
            receipt['diagnostics'].append(e.record())
        except Exception as e:
            receipt.update(state='unknown' if dispatched else 'blocked', reason='HOST_ERROR')
            receipt['diagnostics'].append({'code': 'HOST_ERROR', 'message': str(e)})
        finally:
            for handle, before in workspace_before.items():
                try:
                    after = snapshot(bound_resources[handle]['path'])
                    changes = differences(before, after)
                    receipt['effects']['observed'].append({'resource': handle, 'kind': 'workspace.snapshot', 'before': before['digest'], 'after': after['digest'], 'changes': changes})
                    if changes and 'workspace.write' not in grants:
                        receipt.update(state='failed', reason='UNDECLARED_EFFECT')
                except Exception as e:
                    receipt.update(state='unknown' if dispatched else 'blocked', reason='EFFECT_UNKNOWN' if dispatched else 'OBSERVATION_FAILED')
                    receipt['diagnostics'].append({'code': receipt['reason'], 'message': str(e)})
            receipt['provenance']['finished'] = time.time()
            receipt['provenance']['attempt_dir'] = str(attempt)
            with self.db() as db:
                db.execute('BEGIN IMMEDIATE')
                current = json.loads(db.execute('SELECT receipt FROM calls WHERE key=?', (key,)).fetchone()[0])
                if current.get('reconciliations'):
                    # Operator reconciliation remains authoritative even if a buffered
                    # adapter response arrives afterwards. Preserve it as evidence.
                    late_path = attempt / ('late-result-' + uuid.uuid4().hex + '.json')
                    late_path.write_bytes(encoded(receipt))
                    current.setdefault('late_observations', []).append({'path': str(late_path), 'sha256': file_sha(late_path), 'recorded': time.time()})
                    receipt = current
                (attempt / 'receipt.json').write_bytes(encoded(receipt))
                db.execute('UPDATE calls SET receipt=? WHERE key=?', (json.dumps(receipt), key))
                if receipt['state'] != 'unknown':
                    db.execute('DELETE FROM leases WHERE call_id=?', (receipt['call'],))
        return receipt


def resolve_request(request, answers):
    fields(request, {'format', 'kind', 'id', 'desired', 'open'}, {'format', 'kind', 'id', 'desired', 'open'})
    require(request['format'] == 'cc-request/2' and request['kind'] in {'request', 'template'}, 'UNSUPPORTED_VERSION', 'Expected v2 request/template')
    require(isinstance(request['id'], str) and bool(request['id'].strip()), 'INVALID_REQUEST', 'Nonempty request ID required')
    require(request['kind'] == 'request', 'INVALID_REQUEST', 'Instantiate template before resolution')
    require(isinstance(request['open'], dict) and isinstance(answers, dict) and set(answers) == set(request['open']), 'INVALID_REQUEST', 'Answer exactly the open choices')
    result = deepcopy(request['desired'])
    pointers = sorted(request['open'])
    for i, pointer in enumerate(pointers):
        require(isinstance(pointer, str) and pointer.startswith('/') and not re.search(r'~(?![01])', pointer) and not any(p.startswith(pointer + '/') for p in pointers[i+1:]), 'INVALID_REQUEST', 'Overlapping or invalid pointers')
        descriptor = request['open'][pointer]
        fields(descriptor, {'owner', 'question'}, {'owner', 'question'})
        require(descriptor['owner'] in {'requester', 'implementer'} and isinstance(descriptor['question'], str) and descriptor['question'].strip(), 'INVALID_REQUEST', 'Invalid decision descriptor')
        parts = [p.replace('~1', '/').replace('~0', '~') for p in pointer[1:].split('/')]
        target = result
        for part in parts[:-1]:
            require(isinstance(target, dict) and part in target, 'INVALID_REQUEST', 'Open choice parent must exist')
            target = target[part]
        require(isinstance(target, dict) and parts[-1] not in target and answers[pointer] is not None, 'FIXED_FIELD_CHANGE', pointer)
        target[parts[-1]] = deepcopy(answers[pointer])
    return normalize(result)


def migrate_v1(raw):
    require(raw.get('cc') == '1', 'UNSUPPORTED_VERSION', 'Migration accepts v1 only')
    issues = []
    binding = raw.get('carrier')
    if not isinstance(binding, str):
        issues.append('Build recipe needs explicit materialization; no image fabricated')
    oldops = raw.get('operations') or {'run': {k: v for k, v in raw.items() if k in {'does', 'takes', 'gives', 'run', 'needs', 'changes', 'guarantees'}}}
    result = {'cc': '2', 'id': raw['id'], 'version': raw['version'], 'bindings': {}, 'capabilities': {}}
    for name, op in oldops.items():
        cap = {'does': op['does'], 'takes': {}, 'gives': {}}
        for side in ('takes', 'gives'):
            for pname, spec in op.get(side, {}).items():
                if isinstance(spec, str) and spec.startswith('$'):
                    spec = raw.get('defs', {}).get(spec[1:], {})
                if spec == 'string':
                    cap[side][pname] = 'text'
                elif isinstance(spec, dict) and 'artifact' in spec:
                    cap[side][pname] = {'kind': 'artifact', 'media_type': spec['artifact']}
                elif isinstance(spec, dict) and 'schema_ref' in spec:
                    issues.append(f'{name}.{side}.{pname}: external schema must be bundled; unresolved')
                else:
                    cap[side][pname] = {'kind': 'json', 'schema': {'type': spec} if isinstance(spec, str) else spec}
        for field in ('needs', 'changes', 'guarantees'):
            if op.get(field):
                issues.append(f'{name}.{field}: translate original rule definitions without weakening: {op[field]}')
        if isinstance(op.get('run'), str) and isinstance(op.get('carrier', binding), str):
            bname = 'default' if not result['bindings'] else 'op.' + name
            result['bindings'][bname] = {'kind': 'image', 'image': op.get('carrier', binding), 'command': [op['run']]}
            if bname != 'default':
                cap['using'] = bname
        else:
            issues.append(f'{name}: implementation binding needs manual translation')
        result['capabilities'][name] = cap
    if raw.get('profiles'):
        issues.append('Required profiles need explicit translation; no semantics discarded')
    if not issues:
        try:
            normalize(result)
        except Exception as e:
            issues.append('Translated candidate fails v2 validation: ' + str(e))
    return {'status': 'needs_review' if issues else 'translated', 'issues': issues, 'declaration': result if not issues else None, 'candidate': result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('validate'); p.add_argument('declaration')
    p = sub.add_parser('seal'); p.add_argument('bundle'); p.add_argument('--store', required=True)
    p = sub.add_parser('call'); p.add_argument('release'); p.add_argument('capability'); p.add_argument('--inputs', required=True); p.add_argument('--store', required=True); p.add_argument('--key'); p.add_argument('--grant', action='append', default=[]); p.add_argument('--resources'); p.add_argument('--timeout', type=float, default=60); p.add_argument('--trusted-local', action='store_true')
    p = sub.add_parser('status'); p.add_argument('key'); p.add_argument('--store', required=True)
    p = sub.add_parser('reconcile'); p.add_argument('key'); p.add_argument('--store', required=True); p.add_argument('--stopped', action='store_true'); p.add_argument('--note', required=True)
    p = sub.add_parser('resolve'); p.add_argument('request'); p.add_argument('answers')
    p = sub.add_parser('migrate'); p.add_argument('declaration')
    args = parser.parse_args()
    try:
        if args.action == 'validate':
            result = load(args.declaration)
        elif args.action == 'resolve':
            result = resolve_request(yaml.load(Path(args.request).read_text(encoding='utf-8'), Loader=UniqueLoader), json.loads(Path(args.answers).read_text()))
        elif args.action == 'migrate':
            result = migrate_v1(yaml.load(Path(args.declaration).read_text(encoding='utf-8'), Loader=UniqueLoader))
        else:
            host = Host(args.store, resources=json.loads(Path(args.resources).read_text()) if getattr(args, 'resources', None) else None)
            if args.action == 'seal':
                result = {'release': host.seal(args.bundle)}
            elif args.action == 'status':
                result = host.status(args.key)
            elif args.action == 'reconcile':
                result = host.reconcile(args.key, stopped=args.stopped, note=args.note)
            else:
                decl, _ = host.release(args.release)
                kind = decl['bindings'][decl['capabilities'][args.capability]['using']]['kind']
                require(kind != 'native' or args.trusted_local, 'TRUST_REQUIRED', 'Use --trusted-local for team-trusted native code')
                result = host.call(args.release, args.capability, json.loads(Path(args.inputs).read_text()), key=args.key, grants=args.grant, timeout=args.timeout)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except CCError as e:
        print(json.dumps({'error': e.record()}))
        raise SystemExit(2)


if __name__ == '__main__':
    main()
