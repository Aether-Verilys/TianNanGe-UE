import unreal as u,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1];out={}
for name in ['BP_EasySnow','BP_EasySnowMask']:
    obj=u.get_default_object(u.load_class(None,f'/Game/EasySnow/Blueprints/{name}.{name}_C'))
    blob=(root/f'Content/EasySnow/Blueprints/{name}.uasset').read_bytes()
    strings=set(x.decode() for x in re.findall(rb'[\x20-\x7e]{3,90}\x00',blob) for x in [x[:-1]])
    fields={}
    for s in sorted(strings):
        try:
            v=obj.get_editor_property(s)
            fields[s]=v if isinstance(v,(str,int,bool,float)) or v is None else v.get_path_name() if isinstance(v,u.Object) else str(v)
        except Exception:pass
    out[name]=fields
f=u.load_asset('/Game/EasySnow/Materials/Functions/MF_WF_WorldSnow');io=[]
for e in u.MaterialEditingLibrary.get_material_function_expressions(f):
    if isinstance(e,(u.MaterialExpressionFunctionInput,u.MaterialExpressionFunctionOutput)):
        d={'class':e.get_class().get_name()}
        for n in ['input_name','input_type','output_name','preview_value','use_preview_value_as_default','sort_priority']:
            try:d[n]=str(e.get_editor_property(n))
            except Exception:pass
        io.append(d)
out['material_function_io']=io
out['niagara_api']=[x for x in dir(u.NiagaraComponent) if any(k in x for k in ['advance','seek','age','variable','tick','active','system','render'])]
out['actor_api']=[x for x in dir(u.Actor) if 'construction' in x or 'method' in x]
(root/'Saved/EasySnow/fields.json').write_text(json.dumps(out,indent=2))
