import copy
import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner

class FakeLedger:
    def __init__(self):
        self.records = {}
        self.fail = False
    def read(self, key):
        return self.records.get(key)
    def write(self, key, record, previous=None):
        if self.fail:
            raise runner.Stop('Write failed')
        if key in self.records and previous is None:
            raise runner.Stop('Conflict')
        self.records[key] = copy.deepcopy(record)
        return {'sha': 'revision'}

class FakeLC:
    def __init__(self, allowed=True, crash=False, accepted=True):
        self.allowed, self.crash, self.accepted = allowed, crash, accepted
        self.submitted = 0
    def preflight(self, *args):
        return {'questionId': '206'}, self.allowed
    def submit_once(self, *args):
        self.submitted += 1
        if self.crash:
            raise runner.Stop('Network timeout after send')
        return 123
    def verdict(self, *args):
        return {'status_code': 10 if self.accepted else 11, 'status_msg': 'sample'}

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.plan = runner.load_plan()
        self.config = {'username': 'GandhiSmit06', 'start_date': '2026-10-27'}
        self.now = datetime(2026, 10, 27, 15, 5, tzinfo=timezone.utc)
        self.ledger = FakeLedger()

    def test_exact_90_unique_easy_medium(self):
        self.assertEqual(len(self.plan), 90)
        self.assertEqual(len({p['number'] for p in self.plan}), 90)
        self.assertNotIn('Hard', {p['difficulty'] for p in self.plan})

    def test_calendar_boundaries(self):
        for offset, expected in [(-1,None),(0,1),(89,90),(90,None),(200,None)]:
            from datetime import timedelta
            p = runner.select_problem(self.plan, self.config['start_date'], self.now+timedelta(days=offset))
            self.assertEqual(p['day'] if p else None, expected)

    def test_start_required(self):
        with self.assertRaises(runner.Stop):
            runner.select_problem(self.plan, None, self.now)

    def test_window_boundaries(self):
        for hour, minute, expected in [(15,4,False),(15,5,True),(17,29,True),(17,30,False),(19,0,False)]:
            self.assertEqual(runner.in_window(self.now.replace(hour=hour,minute=minute)), expected)

    def test_second_run_never_resubmits(self):
        lc = FakeLC()
        for _ in range(2):
            runner.run_live(self.config,self.plan,self.now,lc,self.ledger)
        self.assertEqual(lc.submitted,1)

    def test_ambiguous_submission_is_not_retried(self):
        lc = FakeLC(crash=True)
        with self.assertRaises(runner.Stop):
            runner.run_live(self.config,self.plan,self.now,lc,self.ledger)
        runner.run_live(self.config,self.plan,self.now,lc,self.ledger)
        self.assertEqual(lc.submitted,1)
        self.assertEqual(next(iter(self.ledger.records.values()))['status'],'reserved')

    def test_existing_manual_submission_skips_slot(self):
        lc = FakeLC(allowed=False)
        runner.run_live(self.config,self.plan,self.now,lc,self.ledger)
        self.assertEqual(lc.submitted,0)
        self.assertEqual(next(iter(self.ledger.records.values()))['status'],'skipped-existing-submission')

    def test_no_submission_when_reservation_fails(self):
        self.ledger.fail = True
        lc = FakeLC()
        with self.assertRaises(runner.Stop):
            runner.run_live(self.config,self.plan,self.now,lc,self.ledger)
        self.assertEqual(lc.submitted,0)

    def test_wrong_answer_not_retried(self):
        lc = FakeLC(accepted=False)
        with self.assertRaises(runner.Stop):
            runner.run_live(self.config,self.plan,self.now,lc,self.ledger)
        runner.run_live(self.config,self.plan,self.now,lc,self.ledger)
        self.assertEqual(lc.submitted,1)

    def test_expired_plan_does_not_submit(self):
        lc = FakeLC()
        runner.run_live(self.config,self.plan,self.now.replace(year=2027),lc,self.ledger)
        self.assertEqual(lc.submitted,0)

    def test_no_catch_up(self):
        from datetime import timedelta
        lc=FakeLC()
        runner.run_live(self.config,self.plan,self.now+timedelta(days=4),lc,self.ledger)
        self.assertEqual(next(iter(self.ledger.records.values()))['day'],5)
        self.assertEqual(lc.submitted,1)

if __name__ == '__main__':
    unittest.main()
