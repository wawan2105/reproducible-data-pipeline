# Publication audit — 2026-11-06

Decision: **APPROVED FOR PUBLIC**

## Findings and action

Ready with indicator-level World Bank CC BY 4.0 attribution. Credential files and local databases remain ignored. Clean-copy runs pass on both SQLite and PostgreSQL, including 270-row repeat-load idempotency and exact value roundtrip.

## Verification

- Existing statistical/data-integrity suite: 4 tests passed.
- Git-history credential scan: 39 historical blobs checked; zero hits for the checked token/private-key patterns and the known local database password; no tracked `.env` file.
- Notebook files were checked for saved error outputs; no error outputs were found. This does not prove all methodological assumptions.
- README/source links were checked locally. Analysis limitations and provenance are retained.
- Scans are targeted checks, not a guarantee that every possible secret or identifier has been detected.

## Clean-copy reproduction

Analysis and tests passed in an independently installed Python 3.11 virtual environment, from copies containing only Git-trackable project files. Generated models, caches and local credential files were absent. Primary metrics matched the existing results. Direct dependencies were pinned; the fresh environment resolved transitive dependencies independently.

Both SQLite and PostgreSQL were tested. PostgreSQL 17.6 retained 270 rows across repeated loads; exact source/database values matched and analytical output had 90 country-year records. Local start/stop helpers were verified; no database password is included in this report.

## Source evidence reviewed

- [Source documentation](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD)
- [Source documentation](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG)
- [Source documentation](https://data.worldbank.org/indicator/SP.POP.TOTL)

The approval/defer decision is limited to this portfolio release and the evidence reviewed. It is not a certification of downstream deployment suitability or an assertion that deferred datasets prohibit redistribution.
