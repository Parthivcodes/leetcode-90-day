import base64
import json
import copy
import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner

class FakeLedger:
    def __init__(self):
        self.records = {}
        self.fail = False
    def read(self, key):
        record = self.records.get(key)
        return None if record is None else {'content': base64.b64encode(json.dumps(record).encode()).decode()}
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
        for hour, minute, expected in [(3,4,False),(3,5,True),(17,29,True),(18,29,True),(18,30,False)]:
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
        with self.assertRaises(runner.Stop):
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
        with self.assertRaises(runner.Stop):
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

    def test_late_run_without_record_fails_without_submission(self):
        lc = FakeLC()
        with self.assertRaises(runner.Stop):
            runner.run_live(self.config, self.plan, self.now.replace(hour=1), lc, self.ledger)
        self.assertEqual(lc.submitted, 0)

    def test_all_backup_runs_submit_only_once(self):
        lc = FakeLC()
        for hour in (3, 7, 13, 16, 18):
            runner.run_live(self.config, self.plan, self.now.replace(hour=hour, minute=5), lc, self.ledger)
        self.assertEqual(lc.submitted, 1)

    def test_audit_missing_day_fails_and_never_creates_record(self):
        from datetime import timedelta
        with self.assertRaises(runner.Stop):
            runner.audit_previous_day(self.config, self.plan, self.now + timedelta(days=1), self.ledger)
        self.assertEqual(self.ledger.records, {})

    def test_audit_accepted_day_passes(self):
        from datetime import timedelta
        lc = FakeLC()
        runner.run_live(self.config, self.plan, self.now, lc, self.ledger)
        runner.audit_previous_day(self.config, self.plan, self.now + timedelta(days=1), self.ledger)
        self.assertEqual(lc.submitted, 1)

    def test_audit_reserved_day_fails(self):
        from datetime import timedelta
        self.ledger.write('2026-10-27.json', {'date': '2026-10-27', 'status': 'reserved'})
        with self.assertRaises(runner.Stop):
            runner.audit_previous_day(self.config, self.plan, self.now + timedelta(days=1), self.ledger)

    def test_backup_recovers_preflight_failure(self):
        lc = FakeLC()
        with patch.object(lc, 'preflight', side_effect=runner.Stop('Temporary outage')):
            with self.assertRaises(runner.Stop):
                runner.run_live(self.config, self.plan, self.now, lc, self.ledger)
        runner.run_live(self.config, self.plan, self.now, lc, self.ledger)
        self.assertEqual(lc.submitted, 1)

    def preflight(self, question_changes=None, user_changes=None, history=None):
        client = runner.LeetCode('test-only-session', 'test-only-csrf')
        user = {'isSignedIn': True, 'username': 'GandhiSmit06', **(user_changes or {})}
        question = {'questionId': '206', 'questionFrontendId': '206',
                    'titleSlug': 'reverse-linked-list', 'difficulty': 'Easy',
                    'isPaidOnly': False, 'codeSnippets': [{'langSlug': 'cpp'}],
                    **(question_changes or {})}
        with patch.object(client,'graphql',side_effect=[{'userStatus':user},{'question':question}]):
            with patch.object(runner,'request_json',return_value=history if history is not None else {'submissions_dump': []}):
                return client.preflight('GandhiSmit06',self.plan[0],self.now)

    def test_preflight_rejects_hard(self):
        with self.assertRaises(runner.Stop):
            self.preflight({'difficulty':'Hard'})

    def test_preflight_rejects_premium_or_unknown(self):
        for paid in [True, None]:
            with self.assertRaises(runner.Stop):
                self.preflight({'isPaidOnly':paid})

    def test_preflight_rejects_wrong_user_or_expired_session(self):
        for change in [{'username':'someone-else'},{'isSignedIn':False}]:
            with self.assertRaises(runner.Stop):
                self.preflight(user_changes=change)

    def test_preflight_rejects_wrong_problem(self):
        with self.assertRaises(runner.Stop):
            self.preflight({'questionFrontendId':'1'})

    def test_preflight_rejects_missing_cpp(self):
        with self.assertRaises(runner.Stop):
            self.preflight({'codeSnippets':[]})

    def test_preflight_rejects_unknown_history(self):
        with self.assertRaises(runner.Stop):
            self.preflight(history={})

    def test_preflight_detects_any_submission_today(self):
        _, allowed = self.preflight(history={'submissions_dump':[{'timestamp':str(int(self.now.timestamp()))}]})
        self.assertFalse(allowed)

    def test_preflight_accepts_verified_free_problem(self):
        _, allowed = self.preflight()
        self.assertTrue(allowed)

if __name__ == '__main__':
    unittest.main()
