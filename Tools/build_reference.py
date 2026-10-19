"""Resume cached asset import, assemble the revision, light, align, and validate."""
import os,runpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['TIANNANGE_REBUILD']='1'
runpy.run_path(str(ROOT/'Tools/import_revision.py'),run_name='__main__')
result=json.loads((ROOT/'migration-fdf5e67-result.json').read_text())
assert not result['errors'],result['errors']
runpy.run_path(str(ROOT/'Tools/lookdev_reference.py'),run_name='__main__')
runpy.run_path(str(ROOT/'Tools/align_reference.py'),run_name='__main__')
runpy.run_path(str(ROOT/'Tools/validate_reference.py'),run_name='__main__')
