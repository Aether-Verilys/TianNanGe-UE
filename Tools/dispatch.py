import json,sys,time
from pathlib import Path
root=(Path(__file__).resolve().parents[1] / 'Tools')
job={'id':str(time.time_ns()),'script':str(root/sys.argv[1])}
if len(sys.argv)>2:job.update(json.loads(sys.argv[2]))
for attempt in range(50):
    try:(root/'Live/command.json').write_text(json.dumps(job),encoding='utf-8');break
    except PermissionError:time.sleep(.05)
else:raise RuntimeError('Live command locked')
for attempt in range(180):
    time.sleep(.5)
    try:status=json.loads((root/'Live/status.json').read_text(encoding='utf-8'))
    except (ValueError,FileNotFoundError):continue
    if status.get('id')==job['id']:
        print(json.dumps(status));sys.exit(0 if status.get('success') else 1)
raise RuntimeError('Live command timed out')
