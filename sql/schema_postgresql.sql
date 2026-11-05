
CREATE TABLE portfolio_country (
	country_code VARCHAR(3) NOT NULL, 
	country_name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (country_code)
)

;


CREATE TABLE portfolio_indicator (
	indicator_code VARCHAR(40) NOT NULL, 
	indicator_name VARCHAR(150) NOT NULL, 
	unit VARCHAR(80) NOT NULL, 
	PRIMARY KEY (indicator_code)
)

;


CREATE TABLE portfolio_observation (
	country_code VARCHAR(3) NOT NULL, 
	indicator_code VARCHAR(40) NOT NULL, 
	year INTEGER NOT NULL, 
	value FLOAT, 
	PRIMARY KEY (country_code, indicator_code, year), 
	CONSTRAINT observation_year_range CHECK (year >= 2010 AND year <= 2024), 
	FOREIGN KEY(country_code) REFERENCES portfolio_country (country_code), 
	FOREIGN KEY(indicator_code) REFERENCES portfolio_indicator (indicator_code)
)

;