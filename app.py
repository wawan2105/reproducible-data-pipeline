from pathlib import Path
import pandas as pd
import streamlit as st
ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='ASEAN Economic Indicators',layout='wide')
st.title('Southeast Asia Economic Indicators')
st.caption('World Bank | 2010–2024 | Wawan Saputra')
p=ROOT/'outputs/tables/country_year.csv'
if not p.exists():
    st.warning('Run the ETL pipeline to create the analytical dataset.');st.stop()
d=pd.read_csv(p)
country=st.selectbox('Country',sorted(d.country_name.unique()))
metrics={'GDP per capita (current US$)':'gdp_per_capita_usd','Consumer price inflation (annual %)':'inflation_pct','Population (persons)':'population'}
metric=st.selectbox('Indicator',list(metrics))
g=d[d.country_name==country].sort_values('year').set_index('year')
st.line_chart(g[[metrics[metric]]])
st.dataframe(g,hide_index=False)
st.download_button('Download all country-year indicators',d.to_csv(index=False),'country_year.csv','text/csv')
st.caption('Historical published indicators; nominal GDP per capita is not purchasing-power adjusted. Missing values remain missing.')
