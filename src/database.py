import os
from pathlib import Path
from sqlalchemy import MetaData,Table,Column,String,Integer,Float,ForeignKey,CheckConstraint,create_engine,event
ROOT=Path(__file__).resolve().parents[1]
metadata=MetaData()
country=Table('portfolio_country',metadata,Column('country_code',String(3),primary_key=True),Column('country_name',String(100),nullable=False))
indicator=Table('portfolio_indicator',metadata,Column('indicator_code',String(40),primary_key=True),Column('indicator_name',String(150),nullable=False),Column('unit',String(80),nullable=False))
observation=Table('portfolio_observation',metadata,Column('country_code',String(3),ForeignKey(country.c.country_code),primary_key=True),Column('indicator_code',String(40),ForeignKey(indicator.c.indicator_code),primary_key=True),Column('year',Integer,primary_key=True),Column('value',Float,nullable=True),CheckConstraint('year >= 2010 AND year <= 2024',name='observation_year_range'))

def settings():
    values={}
    path=ROOT/'.env'
    if path.exists():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            if line and not line.lstrip().startswith('#') and '=' in line:
                k,v=line.split('=',1);values[k.strip()]=v.strip()
    values.update(os.environ)
    return values

def engine_for(backend='postgresql',url=None):
    if url is None:
        if backend=='sqlite':url='sqlite:///'+str(ROOT/'outputs/analytics.db')
        else:
            url=settings().get('DATABASE_URL')
            if not url:raise ValueError('Set DATABASE_URL in .env or environment; use --backend sqlite for a portable local run.')
    engine=create_engine(url,future=True)
    if engine.dialect.name=='sqlite':
        @event.listens_for(engine,'connect')
        def enable_foreign_keys(connection,record):connection.execute('PRAGMA foreign_keys=ON')
    if engine.dialect.name not in ('postgresql','sqlite'):raise ValueError('Only PostgreSQL and SQLite are supported')
    return engine

def upsert(connection,table,records,keys):
    if connection.dialect.name=='postgresql':
        from sqlalchemy.dialects.postgresql import insert
    else:
        from sqlalchemy.dialects.sqlite import insert
    statement=insert(table).values(records)
    updates={c.name:statement.excluded[c.name] for c in table.columns if c.name not in keys}
    if updates:statement=statement.on_conflict_do_update(index_elements=keys,set_=updates)
    else:statement=statement.on_conflict_do_nothing(index_elements=keys)
    connection.execute(statement)
