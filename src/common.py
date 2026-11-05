from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone
from importlib.metadata import version, PackageNotFoundError
import urllib.request
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
SEED = 42
plt.rcParams.update({'figure.dpi':150,'axes.spines.top':False,'axes.spines.right':False,'font.size':10,'axes.prop_cycle':plt.cycler(color=['#117d89','#e08a45','#735aa6','#389668'])})

def download(url,filename):
    path=ROOT/'data/raw'/filename
    if not path.exists():
        request=urllib.request.Request(url,headers={'User-Agent':'WawanPortfolio/1.0 public-data-analysis'})
        with urllib.request.urlopen(request,timeout=120) as response:
            data=response.read()
        temp=path.with_suffix(path.suffix+'.tmp')
        temp.write_bytes(data)
        temp.replace(path)
    manifest=ROOT/'data/source_manifest.json'
    sources=json.loads(manifest.read_text()) if manifest.exists() else {}
    if filename not in sources:
        sources[filename]={'url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
        manifest.write_text(json.dumps(sources,indent=2),encoding='utf-8')
    elif hashlib.sha256(path.read_bytes()).hexdigest()!=sources[filename]['sha256']:
        raise ValueError('Cached source checksum mismatch: '+filename)
    return path

def write_json(name,obj):
    def convert(x):
        if isinstance(x,np.generic):return x.item()
        if isinstance(x,np.ndarray):return x.tolist()
        if isinstance(x,Path):return str(x)
        raise TypeError(type(x).__name__)
    (ROOT/'outputs'/name).write_text(json.dumps(obj,indent=2,default=convert,allow_nan=False),encoding='utf-8')

def table(name,df):
    df.to_csv(ROOT/'outputs/tables'/name,index=False)

def figure(name):
    plt.tight_layout()
    plt.savefig(ROOT/'outputs/figures'/name,bbox_inches='tight')
    plt.close()

def report(title,sections,bullets):
    parts=['# '+title,'Wawan Saputra | Independent Portfolio Project | 2026']
    for heading,content in sections.items():parts += ['## '+heading,content]
    parts += ['## CV-ready bullets']+['- '+b for b in bullets]
    (ROOT/'outputs/executive_summary.md').write_text('\n\n'.join(parts)+'\n',encoding='utf-8')

def environment(packages):
    import platform
    result={'python':platform.python_version()}
    for p in packages:
        try:result[p]=version(p)
        except PackageNotFoundError:pass
    write_json('environment.json',result)
    (ROOT/'requirements-lock.txt').write_text('\n'.join(f'{k}=={v}' for k,v in result.items() if k!='python')+'\n',encoding='utf-8')
