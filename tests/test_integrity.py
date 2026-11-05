import unittest
import json
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SourceIntegrity(unittest.TestCase):
    def test_snapshot_checksums(self):
        manifest=json.loads((ROOT/'data/source_manifest.json').read_text(encoding='utf-8'))
        self.assertTrue(manifest)
        for name,metadata in manifest.items():
            self.assertEqual(hashlib.sha256((ROOT/'data/raw'/name).read_bytes()).hexdigest(),metadata['sha256'])
    def test_actual_results_and_reports_exist(self):
        result=json.loads((ROOT/'outputs/metrics.json').read_text(encoding='utf-8'))
        self.assertTrue(result)
        text=(ROOT/'outputs/executive_summary.md').read_text(encoding='utf-8')
        self.assertIn('Limitations and Future Work',text)
        self.assertIn('CV-ready bullets',text)

import pandas as pd
from sqlalchemy import select,func
from sqlalchemy.exc import IntegrityError
from src.database import engine_for,observation
from src.ingest import validate
from src.run import load
class DatabaseIntegrity(unittest.TestCase):
    def setUp(self):
        self.data=pd.read_csv(ROOT/'data/processed/observations.csv')
    def test_duplicate_and_domain_rejection(self):
        with self.assertRaises(ValueError):validate(pd.concat([self.data,self.data.iloc[:1]],ignore_index=True))
        invalid=self.data.copy()
        invalid.loc[invalid.indicator_code=='SP.POP.TOTL','value']=-1
        with self.assertRaises(ValueError):validate(invalid)
    def test_transactional_load_idempotency_and_foreign_keys(self):
        engine=engine_for(url='sqlite:///:memory:')
        self.assertEqual(load(engine,self.data),270)
        self.assertEqual(load(engine,self.data),270)
        with self.assertRaises(IntegrityError):
            with engine.begin() as con:
                con.execute(observation.insert().values(country_code='XXX',indicator_code='SP.POP.TOTL',year=2024,value=1))
        with engine.connect() as con:
            self.assertEqual(con.scalar(select(func.count()).select_from(observation)),270)
        engine.dispose()

if __name__=='__main__': unittest.main()
