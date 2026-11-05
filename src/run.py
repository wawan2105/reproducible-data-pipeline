import argparse
import logging
import json
import numpy as np
import pandas as pd
from sqlalchemy import select,func,text
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from .common import ROOT,write_json,table,figure,report,environment,plt
from .database import metadata,country,indicator,observation,engine_for,upsert
from .ingest import ingest,INDICATORS
LOG=logging.getLogger('portfolio.etl')

def load(engine,data):
    metadata.create_all(engine)
    countries=data[['country_code','country_name']].drop_duplicates().to_dict('records')
    indicators=[dict(indicator_code=k,indicator_name=v[0],unit=v[1]) for k,v in INDICATORS.items()]
    obs=data[['country_code','indicator_code','year','value']].astype(object).where(pd.notna(data[['country_code','indicator_code','year','value']]),None).to_dict('records')
    # All writes are atomic; validation happens before entering this transaction.
    with engine.begin() as con:
        upsert(con,country,countries,['country_code'])
        upsert(con,indicator,indicators,['indicator_code'])
        for start in range(0,len(obs),200):upsert(con,observation,obs[start:start+200],['country_code','indicator_code','year'])
    with engine.connect() as con:return int(con.scalar(select(func.count()).select_from(observation)))

def run(backend='postgresql',refresh=False):
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',handlers=[logging.FileHandler(ROOT/'outputs/pipeline.log',encoding='utf-8'),logging.StreamHandler()])
    data=ingest(refresh=refresh)
    LOG.info('Validated %d rows with %d missing observations',len(data),data.value.isna().sum())
    engine=engine_for(backend)
    try:
        count1=load(engine,data)
        count2=load(engine,data)
        if count1!=len(data) or count2!=count1:raise AssertionError('Idempotency row-count failure')
        with engine.connect() as con:
            sql=(ROOT/'sql/country_year.sql').read_text(encoding='utf-8-sig')
            dashboard=pd.read_sql(text(sql),con)
            changes=pd.read_sql(text((ROOT/'sql/year_on_year.sql').read_text(encoding='utf-8-sig')),con)
            saved=pd.read_sql(select(observation),con)
            dbversion=con.scalar(text('SELECT version()')) if engine.dialect.name=='postgresql' else con.scalar(text('SELECT sqlite_version()'))
        keys=['country_code','indicator_code','year']
        check=data[keys+['value']].merge(saved,on=keys,validate='one_to_one',suffixes=('_raw','_db'))
        if not np.array_equal(check.value_raw.to_numpy(dtype=float),check.value_db.to_numpy(dtype=float),equal_nan=True):raise AssertionError('Database value roundtrip differs')
        table('country_year.csv',dashboard);table('year_on_year.csv',changes)
        (ROOT/'sql/schema_postgresql.sql').write_text('\n\n'.join(str(CreateTable(t).compile(dialect=postgresql.dialect()))+';' for t in metadata.sorted_tables),encoding='utf-8')
        fig,axes=plt.subplots(1,2,figsize=(11,4))
        for name,g in dashboard.groupby('country_code'):
            axes[0].plot(g.year,g.gdp_per_capita_usd,label=name);axes[1].plot(g.year,g.inflation_pct,label=name)
        axes[0].set(title='GDP per capita | nominal current US$',xlabel='Year',ylabel='US$');axes[1].set(title='Consumer price inflation',xlabel='Year',ylabel='Annual %');axes[1].legend(ncol=2,fontsize=8)
        figure('dashboard_preview.png')
        result={'backend':engine.dialect.name,'database_version':dbversion,'source_rows':len(data),'loaded_rows':count1,'rows_after_repeat_load':count2,'idempotent':count1==count2,'database_values_match_source':True,'dashboard_rows':len(dashboard),'countries':data.country_code.nunique(),'indicators':data.indicator_code.nunique(),'years':[2010,2024],'missing_values':int(data.value.isna().sum())}
        write_json('metrics.json',result)
        report('Automated Analytics Pipeline: World Bank to PostgreSQL',{
            'Question and source':'Create reliable country-year analytical datasets for six Southeast Asian economies using World Bank GDP per capita, inflation and population, 2010–2024. Units remain explicit; nominal GDP per capita is not a purchasing-power or causal comparison.',
            'Architecture':'Cached public API JSON → explicit schema/domain validation → normalized country and indicator dimensions → observation facts with composite primary key and foreign keys → transactional upserts → analytical SQL pivot and LAG queries → dashboard-ready CSV and Streamlit app. PostgreSQL is the primary backend; SQLite is an explicit portable alternative.',
            'Actual execution':f'Backend {engine.dialect.name}; {len(data)} validated rows, {count1} stored rows, {count2} after repeat load, {len(dashboard)} analytical country-year rows. Database value roundtrip matched the source. Missing numeric values retained as SQL NULL: {data.value.isna().sum()}. Database: {dbversion}.',
            'Reliability':'Validation precedes writes. Transactions prevent partial dimension/fact loads. Primary keys prevent duplicates, foreign keys enforce dimensions, and repeated loads update existing keys. Refresh validates new API content before replacing the cached snapshot. Logs omit connection credentials. Re-run python -m src.run --refresh for an explicit refresh; no scheduler is installed.',
            'Limitations and Future Work':'Latest-vintage data can be revised; refresh changes snapshots and checksums. No claim of a historical-vintage warehouse or orchestration service. Fixed selected country/indicator/year coverage, no missing-value imputation, no currency or inflation adjustment of nominal GDP. Add migration tooling, freshness alerts, immutable source version history and automated database integration checks for production.'},[
            f'Built and executed a normalized {engine.dialect.name} analytics pipeline for {len(data)} public observations with foreign keys, transactional upserts and SQL window functions.',
            f'Verified repeat-load idempotency and exact source-to-database value roundtrip; exported {len(dashboard)} dashboard-ready country-year records.'])
        environment(['numpy','pandas','sqlalchemy','psycopg','psycopg-binary','matplotlib','streamlit','pyarrow','nbformat'])
        LOG.info('Completed backend=%s rows=%d idempotency=passed',engine.dialect.name,count2)
        print(json.dumps(result,indent=2))
        return result
    finally:engine.dispose()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--backend',choices=['postgresql','sqlite'],default='postgresql');p.add_argument('--refresh',action='store_true');args=p.parse_args()
    try:run(args.backend,args.refresh)
    except Exception:
        LOG.error('Pipeline failed. Check input validation, database availability and local configuration; transaction changes rolled back where applicable.')
        raise
