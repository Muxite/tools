#!/usr/bin/env python3
"""Make a private, consistent local factory checkpoint. Never copy agent auth homes."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile


def checkpoint(factory_home, destination):
    factory_home = Path(factory_home).resolve(strict=True)
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(destination, 0o700)
    stage = Path(tempfile.mkdtemp(prefix='.checkpoint-', dir=destination))
    files = []
    try:
        # Deliberately exclude agent-data, environment files, tokens and sessions.
        for relative in ('factory.sqlite', 'ccstore/calls.sqlite'):
            source = (factory_home / relative).resolve(strict=True)
            if not source.is_relative_to(factory_home):
                raise ValueError('database escapes factory home: ' + relative)
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as src:
                with closing(sqlite3.connect(target)) as dst:
                    src.backup(dst)
                    if dst.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                        raise RuntimeError('SQLite integrity check failed: ' + relative)
            os.chmod(target, 0o600)
            with target.open('rb') as stream:
                os.fsync(stream.fileno())
                digest = hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(stream.read()).hexdigest()
            files.append(dict(path=relative, sha256=digest, bytes=target.stat().st_size))
        manifest = dict(format='satay-private-checkpoint/1', created_utc=datetime.now(timezone.utc).isoformat(),
                        source=str(factory_home), files=files,
                        note='Private databases may contain prompts and local paths. Not a portable workspace restore. Never publish in Git or presentation ZIP.')
        with (stage / 'manifest.json').open('w') as stream:
            json.dump(manifest, stream, indent=2)
            stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        # fsync containing directories before atomically publishing the snapshot.
        for directory in (stage / 'ccstore', stage):
            fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
            try: os.fsync(fd)
            finally: os.close(fd)
        final = destination / ('checkpoint-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + stage.name[-8:])
        stage.rename(final)
        fd = os.open(destination, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
        return final
    except BaseException:
        shutil.rmtree(stage)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--factory-home', type=Path, default=Path.home() / '.jiuwenswarm-factory')
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    print(checkpoint(args.factory_home, args.destination))
