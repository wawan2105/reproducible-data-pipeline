WITH ordered AS (
 SELECT country_code, indicator_code, year, value,
        LAG(value) OVER (PARTITION BY country_code, indicator_code ORDER BY year) AS previous_value
 FROM portfolio_observation
)
SELECT country_code, indicator_code, year, value, previous_value,
 CASE WHEN previous_value IS NOT NULL AND previous_value <> 0
      THEN 100.0 * (value / previous_value - 1.0) END AS year_on_year_change_pct
FROM ordered
WHERE indicator_code IN ('NY.GDP.PCAP.CD', 'SP.POP.TOTL')
ORDER BY country_code, indicator_code, year;
