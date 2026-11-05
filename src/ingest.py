import json
import hashlib
import urllib.request
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from .common import ROOT,download,write_json
COUNTRIES=['IDN','MYS','THA','VNM','PHL','SGP']
INDICATORS={'NY.GDP.PCAP.CD':('GDP per capita','current US$'),'FP.CPI.TOTL.ZG':('Consumer price inflation','annual %'),'SP.POP.TOTL':('Population','persons')}
URL='https://api.worldbank.org/v2/country/'+ ';'.join(COUNTRIES)+'/indicator/'+';'.join(INDICATORS)+'?source=2&date=2010:2024&format=json&per_page=20000'

def ingest(refresh=False):
    name='worldbank_asean.json'
    if refresh:
        request=urllib.request.Request(URL,headers={'User-Agent':'WawanPortfolio/1.0'})
        with urllib.request.urlopen(request,timeout=120) as response:payload=response.read()
        decoded=json.loads(payload)
        if not isinstance(decoded,list) or len(decoded)!=2 or not isinstance(decoded[1],list):raise ValueError('Refresh did not return World Bank observations')
        # Validate refreshed data before replacing the local snapshot.
        records=parse(decoded)
        validate(records)
        path=ROOT/'data/raw'/name
        temp=path.with_suffix('.tmp');temp.write_bytes(payload);temp.replace(path)
        manifest=ROOT/'data/source_manifest.json'
        sources=json.loads(manifest.read_text()) if manifest.exists() else {}
        sources[name]={'url':URL,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload)}
        manifest.write_text(json.dumps(sources,indent=2))
    else:path=download(URL,name)
    decoded=json.loads(path.read_text())
    data=parse(decoded)
    validate(data)
    data.to_csv(ROOT/'data/processed/observations.csv',index=False)
    write_json('data_audit.json',{'rows':len(data),'countries':sorted(data.country_code.unique().tolist()),'indicators':sorted(data.indicator_code.unique().tolist()),'missing_values':int(data.value.isna().sum()),'duplicate_keys':int(data.duplicated(['country_code','indicator_code','year']).sum()),'api_metadata':decoded[0]})
    return data

def parse(decoded):
    if not isinstance(decoded,list) or len(decoded)!=2:raise ValueError('Unexpected API response')
    return pd.DataFrame([{'country_code':r['countryiso3code'],'country_name':r['country']['value'],'indicator_code':r['indicator']['id'],'year':int(r['date']),'value':r['value']} for r in decoded[1]])

def validate(data):
    required=['country_code','country_name','indicator_code','year','value']
    if not set(required)<=set(data):raise ValueError('Missing required columns')
    if data[required[:-1]].isna().any().any():raise ValueError('Missing key or label')
    if data.duplicated(['country_code','indicator_code','year']).any():raise ValueError('Duplicate observation keys')
    if set(data.country_code)!=set(COUNTRIES):raise ValueError('Unexpected country coverage')
    if set(data.indicator_code)!=set(INDICATORS):raise ValueError('Unexpected indicator coverage')
    if not data.year.between(2010,2024).all() or not (data.year%1==0).all():raise ValueError('Invalid year')
    if len(data)!=len(COUNTRIES)*len(INDICATORS)*15:raise ValueError('Incomplete country/indicator/year grid')
    valid=data.value.dropna()
    if not np.isfinite(valid).all():raise ValueError('Nonfinite value')
    if (data.loc[data.indicator_code.isin(['NY.GDP.PCAP.CD','SP.POP.TOTL']),'value'].dropna()<=0).any():raise ValueError('GDP/population must be positive')
    if (data.loc[data.indicator_code=='FP.CPI.TOTL.ZG','value'].dropna()<=-100).any():raise ValueError('Inflation below domain bound')
    return True
