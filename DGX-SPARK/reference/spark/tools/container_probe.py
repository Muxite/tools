import json,os,signal,subprocess,time
from pathlib import Path
name='ssh-factory-'+os.environ['FACTORY_REQUEST_ID']
out=Path(os.environ['FACTORY_RESULT_DIR'])
def stop(*args):raise KeyboardInterrupt('cancelled by queue')
signal.signal(signal.SIGTERM,stop)
try:
    subprocess.run(['docker','create','--name',name,'--label','factory.owner=software-factory-spark-20261113','--network=none','--read-only','--memory=64m','--memory-swap=64m','--cpus=1','--entrypoint','/bin/sleep','sha256:695214dcb4d4062014335702caee98836bbf92c5974b78331c70e152176cbf08','60'],check=True)
    subprocess.run(['docker','start',name],check=True)
    print('owned container running',flush=True)
    time.sleep(60)
finally:
    subprocess.run(['docker','stop','-t','1',name],capture_output=True)
    removed=subprocess.run(['docker','rm',name],capture_output=True)
    (out/'cleanup.json').write_text(json.dumps({'name':name,'remove_rc':removed.returncode}))
