"""Local, file-driven UE editor session for repeatable lighting/capture iterations."""
import unreal as u
import json,time,traceback,os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'Tools/Live'
LIVE.mkdir(exist_ok=True)
requested_map=os.environ.get('TIANNANGE_EDITOR_MAP','/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow')
if not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(requested_map+'.'):
    u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(requested_map)
state={'last':None,'running':False}

def tick(dt):
    job=LIVE/'command.json'
    if not job.exists() or state['running']:
        return
    try:
        command=json.loads(job.read_text(encoding='utf-8'))
        if command.get('pid',os.getpid())!=os.getpid():
            return
        if command['id']==state['last']:
            return
        state['last']=command['id'];state['running']=True
        path=Path(command['script']).resolve()
        assert path.is_relative_to(ROOT/'Tools'),path
        context={'__name__':'__main__','__file__':str(path),'COMMAND':command}
        exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),context)
        status={'id':command['id'],'executed':str(path),'success':True,'time':time.time()}
    except Exception:
        status={'id':state['last'],'success':False,'error':traceback.format_exc(),'time':time.time()}
        u.log_error(status['error'])
    finally:
        state['running']=False
    (LIVE/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')

handle=u.register_slate_post_tick_callback(tick)
(LIVE/'ready.json').write_text(json.dumps({'engine':u.SystemLibrary.get_engine_version(),'time':time.time(),'pid':os.getpid(),'map':requested_map}))
u.log('TIANNANGE_LIVE_READY')
