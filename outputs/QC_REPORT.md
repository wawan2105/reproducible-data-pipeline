# Quality-control report — Project 6

Author: Wawan Saputra

- Unit/integrity tests: 4 passed (`test_results.txt`).
- Notebooks: all three executed successfully; outputs embedded in notebook files.
- Public raw snapshots: SHA-256 verified against `data/source_manifest.json`.
- Statistics: reported quantities come from executable analysis; assumptions and limitations are explicit.
- Figures: the main output was visually inspected for readability.
- Reproducibility: Python and direct package versions recorded; no invented metrics or conclusions.
- CV bullets: generated from actual results in the executive summary.

## Method-specific review

Direct PostgreSQL 17.6 execution: 270 validated rows, 270 after repeated upserts, 90 analytical records, exact floating-point value roundtrip. SQLite unit tests exercise invalid data rejection, foreign-key failure and transaction rollback. Credentials are excluded from archives.

## Dashboard checks

AppTest passed interactive filters/selectors. Chromium rendered the live dashboard without page errors; screenshots saved in `outputs/figures/dashboard_screenshot.png`.
