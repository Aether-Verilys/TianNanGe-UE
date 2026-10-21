"""Encode the untouched UE-rendered PNG frames as a playable H.264 preview."""
from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'Tools/Live/encoding'))
import imageio_ffmpeg
tag=sys.argv[1] if len(sys.argv)>1 else 'EasySnowMotion'
frames=root/'Captures'/tag
files=sorted(frames.glob('EasySnow_*.png'));assert len(files)==72,len(files)
output=root/'Captures'/('EasySnow_Wind_Preview.mp4' if tag=='EasySnowMotion' else tag+'_Preview.mp4')
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ffmpeg,'-hide_banner','-loglevel','warning','-y','-framerate','24','-start_number','0','-i',str(frames/'EasySnow_%04d.png'),'-frames:v','72','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)
subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-i',str(output),'-f','null','-'],check=True)
(root/('Saved/EasySnow/'+tag+'-encoding.json')).write_text(json.dumps({'source':'Unreal native movie capture; no synthesized particles','frames':len(files),'fps':24,'duration_seconds':3,'output':str(output),'bytes':output.stat().st_size,'decode_success':True},indent=2))
print(output)
