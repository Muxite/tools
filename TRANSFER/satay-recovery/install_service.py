#!/usr/bin/env python3
"""Install Satay's user queue service only while the real queue is idle."""
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess


def main():
    root = Path.home() / 'projects/siminfeng'
    queue = root / 'lab/jobq'
    if not (root / 'bin/jobq').is_file():
        raise SystemExit('Expected existing ~/projects/siminfeng/bin/jobq')
    queue.mkdir(parents=True, exist_ok=True)
    with (queue / 'lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        active = [p.name for p in queue.glob('job-*.json')
                  if json.loads(p.read_text())['state'] in ('queued', 'running')]
        if active:
            raise SystemExit('Refusing service takeover with queued/running jobs: ' + ', '.join(active))
        # Retire only idle workers of this checkout, never arbitrary Python sessions.
        for proc in Path('/proc').glob('[0-9]*'):
            try:
                args = (proc / 'cmdline').read_bytes().split(b'\0')
                if len(args) < 3 or args[2] != b'worker':
                    continue
                cwd = (proc / 'cwd').resolve(strict=True)
                executable = Path(os.fsdecode(args[1]))
                if not executable.is_absolute(): executable = cwd / executable
                if executable.resolve() == (root / 'bin/jobq').resolve():
                    os.kill(int(proc.name), signal.SIGTERM)
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                pass
        destination = Path.home() / '.config/systemd/user/satay-jobq.service'
        destination.parent.mkdir(parents=True, exist_ok=True)
        tmp = destination.with_suffix('.tmp')
        tmp.write_bytes(Path(__file__).with_name('satay-jobq.service').read_bytes())
        tmp.replace(destination)
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', '--user', 'enable', '--now', 'satay-jobq.service'], check=True)
    subprocess.run(['systemctl', '--user', 'is-active', 'satay-jobq.service'], check=True)
    user = os.environ.get('USER', 'muk')
    def linger_status():
        return subprocess.check_output(['loginctl', 'show-user', user, '-p', 'Linger'], text=True).strip()
    if linger_status() != 'Linger=yes':
        # Own-user policy can permit this without sudo. Never prompt unattended.
        result = subprocess.run(['loginctl', '--no-ask-password', 'enable-linger', user],
                                capture_output=True, text=True)
        if result.returncode:
            print('Automatic linger enable failed: ' + result.stderr.strip())
    status = linger_status()
    print(status)
    if status != 'Linger=yes':
        print('Boot without login still requires administrator enable-linger.')
    else:
        print('Boot startup prerequisite configured; an actual reboot is not tested here.')


if __name__ == '__main__':
    main()
