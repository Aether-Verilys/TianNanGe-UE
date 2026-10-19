import unreal as u,json,time,traceback
from pathlib import Path
_preview_root=Path(__file__).resolve().parents[1]
_preview_last_poll=0
_preview_wait_handle=None
def _wait_for_migration(dt):
    global _preview_last_poll,_preview_wait_handle
    if time.time()-_preview_last_poll<3:return
    _preview_last_poll=time.time()
    path=_preview_root/'validation-result.json'
    if not path.exists():return
    try:
        result=json.loads(path.read_text())
        if not result.get('pass'):return
        u.unregister_slate_post_tick_callback(_preview_wait_handle)
        exec(compile((_preview_root/'Tools/capture_preview.py').read_text(),'capture_preview.py','exec'),globals())
    except Exception:(_preview_root/'preview-error.txt').write_text(traceback.format_exc())
_preview_wait_handle=u.register_slate_post_tick_callback(_wait_for_migration)
u.log('TIANNANGE_PREVIEW_WAITING_FOR_VALIDATION')
