"""Run inside the UE editor on the revision map after rebuilding source geometry."""
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for script in ['lookdev_reference.py','align_reference.py','tune_reference_v02.py','tune_reference_v03.py','tune_reference_v04.py','tune_reference_v05.py','finish_reference.py','prepare_render.py']:
    runpy.run_path(str(ROOT/'Tools'/script),run_name='__main__')
