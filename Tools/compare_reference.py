"""Numeric render diagnostics; never modifies the rendered/reference image files."""
from PIL import Image
import numpy as np
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REFERENCE=Path('D:/Dev/TianNanGe/4TianNan1_4k_fb78c.jpg')
(ROOT/'Captures/ReferenceLook').mkdir(parents=True,exist_ok=True)
def stats(image):
    rgb=np.asarray(image.convert('RGB'),dtype=np.float32)/255
    y=rgb@np.array([.2126,.7152,.0722])
    saturation=rgb.max(axis=2)-rgb.min(axis=2)
    low=rgb[y<np.quantile(y,.25)].mean(axis=0)
    high=rgb[y>np.quantile(y,.9)].mean(axis=0)
    return {'width':image.width,'height':image.height,'mean_rgb':rgb.mean(axis=(0,1)).tolist(),'luminance_p10_p50_p90':np.quantile(y,[.1,.5,.9]).tolist(),'mean_saturation':float(saturation.mean()),'shadow_mean_rgb':low.tolist(),'highlight_mean_rgb':high.tolist()}
reference=Image.open(REFERENCE)
results={'reference':str(REFERENCE),'reference_stats':stats(reference),'renders':{}}
for name in sys.argv[1:]:
    path=Path(name)
    image=Image.open(path)
    resized=reference.resize(image.size,Image.Resampling.LANCZOS).convert('RGB')
    rgb=np.asarray(image.convert('RGB'),dtype=np.float32)/255
    target=np.asarray(resized,dtype=np.float32)/255
    entry=stats(image)
    entry['normalized_rgb_pixel_mae']=float(np.abs(rgb-target).mean())
    entry['metric_limit']='Pixel MAE includes geometry/pose differences and is not a perceptual similarity percentage.'
    results['renders'][path.name]=entry
(ROOT/'Captures/ReferenceLook/comparison-metrics.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
