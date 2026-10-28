"""Run a project script in the active Unreal Editor Python session."""
import sys, time, json
from pathlib import Path

ENGINE = Path('D:/Program Files/Epic Games/UE_5.8/Engine')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE/'Plugins/Experimental/PythonScriptPlugin/Content/Python'))
import remote_execution

def run(script, options=None):
    remote = remote_execution.RemoteExecution()
    remote.start()
    try:
        for _ in range(20):
            nodes = [n for n in remote.remote_nodes if Path(n.get('project_root','')).resolve() == ROOT]
            if nodes: break
            time.sleep(.25)
        else: raise RuntimeError('TianNanGe editor not discovered')
        remote.open_command_connection(nodes[0]['node_id'])
        path = Path(script).resolve()
        assert path.is_relative_to(ROOT/'Tools')
        context = {'__name__':'__main__', '__file__':str(path), 'COMMAND': options or {}}
        code = f"exec(compile(open({str(path)!r},encoding='utf-8-sig').read(),{str(path)!r},'exec'),{context!r})"
        result = remote.run_command(code, exec_mode=remote_execution.MODE_EXEC_STATEMENT)
        print(json.dumps(result,ensure_ascii=False))
        if not result['success']: raise RuntimeError(result['result'])
        return result
    finally:
        remote.stop()

if __name__ == '__main__':
    run(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv)>2 else None)
