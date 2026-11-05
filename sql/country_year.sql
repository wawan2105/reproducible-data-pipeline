SELECT c.country_code, c.country_name, o.year,
       MAX(CASE WHEN o.indicator_code = 'NY.GDP.PCAP.CD' THEN o.value END) AS gdp_per_capita_usd,
       MAX(CASE WHEN o.indicator_code = 'FP.CPI.TOTL.ZG' THEN o.value END) AS inflation_pct,
       MAX(CASE WHEN o.indicator_code = 'SP.POP.TOTL' THEN o.value END) AS population
FROM portfolio_observation o
JOIN portfolio_country c ON c.country_code = o.country_code
GROUP BY c.country_code, c.country_name, o.year
ORDER BY c.country_code, o.year;
