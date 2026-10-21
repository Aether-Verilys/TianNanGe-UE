import unreal as u,json
from pathlib import Path
d={name:hasattr(u,name) for name in ['AutomatedLevelSequenceCapture','SequencerTools','MovieSceneSequenceExtensions','LevelSequenceFactoryNew','ImageSequenceProtocol_PNG','OnRenderMovieStopped','MovieSceneObjectBindingID']}
if hasattr(u,'SequencerTools'):d['render_movie_doc']=u.SequencerTools.render_movie.__doc__
if hasattr(u,'MovieSceneSequenceExtensions'):d['sequence_methods']=[n for n in dir(u.MovieSceneSequenceExtensions) if 'track' in n or 'possess' in n]
(Path(__file__).resolve().parents[1]/'Saved/EasySnow/movie-api.json').write_text(json.dumps(d,indent=2))
