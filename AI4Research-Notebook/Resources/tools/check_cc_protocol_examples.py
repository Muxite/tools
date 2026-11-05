from pathlib import Path
import runpy
ROOT=Path(__file__).resolve().parents[2]/'Designs/CC Protocols'
import sys
sys.path.insert(0,str(ROOT/'reference'))
runpy.run_path(str(ROOT/'reference/check_package.py'),run_name='__main__')
