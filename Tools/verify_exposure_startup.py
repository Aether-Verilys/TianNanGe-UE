"""Read the cache setting in a fresh UE commandlet, independently of the live console override."""
import unreal as u,json
from pathlib import Path
value=u.SystemLibrary.get_console_variable_float_value('r.EyeAdaptation.CachedLightingPreExposure')
assert value==8.,value
(Path(__file__).resolve().parents[1]/'Saved/Exposure/startup-verified.json').write_text(json.dumps({'cache_exposure':value,'safe_range_ev':[value-12,value+8],'fresh_process':True,'passed':True},indent=2))
