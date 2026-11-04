import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch
import runner

class QueueTests(unittest.TestCase):
    def setUp(self):
        self.client = runner.LeetCode('test', 'test')
        self.plan = runner.load_plan()
        self.now = datetime(2026, 11, 4, 15, tzinfo=timezone.utc)

    def test_paginated_history_includes_failed_attempts_and_actual_page_size(self):
        replies = [{'userStatus': {'isSignedIn': True, 'username': 'GandhiSmit06'}},
                   {'submissionList': {'hasNext': True, 'submissions': [{'id':'1','titleSlug':self.plan[0]['slug'],'timestamp':'1','statusDisplay':'Wrong Answer'}]}},
                   {'submissionList': {'hasNext': False, 'submissions': [{'id':'2','titleSlug':self.plan[1]['slug'],'timestamp':'2','statusDisplay':'Accepted'}]}}]
        with patch.object(self.client, 'graphql', side_effect=replies) as query:
            used, today = self.client.submission_history('GandhiSmit06', self.now)
        self.assertEqual(used, {p['slug'] for p in self.plan[:2]})
        self.assertFalse(today)
        self.assertEqual(query.call_args_list[-1].args[1], {'offset': 1})

    def test_history_repeat_or_missing_slug_blocks(self):
        user = {'userStatus': {'isSignedIn': True, 'username': 'GandhiSmit06'}}
        row = {'id':'1','titleSlug':'used','timestamp':'1'}
        for rows in ([row, row], [{'id':'1','timestamp':'1'}]):
            with patch.object(self.client, 'graphql', side_effect=[user, {'submissionList':{'hasNext':False,'submissions':rows}}]):
                with self.assertRaises(runner.Stop):
                    self.client.submission_history('GandhiSmit06', self.now)

    def test_skip_history_reservations_and_attempted_status(self):
        with patch.object(self.client, 'submission_history', return_value=({self.plan[0]['slug']},False)), patch.object(self.client, 'question_details', side_effect=[{'status':'ac'}, {'status':'notac'}, {'status':None}]) as details:
            problem, _, allowed = self.client.next_problem('GandhiSmit06',self.plan,self.now,{self.plan[1]['slug']})
        self.assertEqual(problem,self.plan[4])
        self.assertTrue(allowed)
        self.assertEqual([call.args[0] for call in details.call_args_list],self.plan[2:5])

    def test_exhausted_queue_fails_without_repeats(self):
        with patch.object(self.client,'submission_history',return_value=({p['slug'] for p in self.plan},False)), patch.object(self.client,'submit_once') as submit:
            with self.assertRaisesRegex(runner.Stop,'No unsubmitted prepared problems'):
                self.client.next_problem('GandhiSmit06',self.plan,self.now,set())
            submit.assert_not_called()

    def test_any_submission_today_prevents_selection(self):
        with patch.object(self.client,'submission_history',return_value=(set(),True)), patch.object(self.client,'question_details') as details:
            self.assertEqual(self.client.next_problem('GandhiSmit06',self.plan,self.now,set()),(None,None,False))
            details.assert_not_called()

    def test_durable_attempts_excluded_but_skips_do_not_consume_problem(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'state').mkdir()
            for i,status in enumerate(['accepted','reserved','submitted','needs-review','skipped-existing-submission'],1):
                (root/'state'/f'2026-10-{i:02}.json').write_text(json.dumps({'status':status,'slug':str(i)}))
            with patch.object(runner,'ROOT',root):
                self.assertEqual(runner.previously_reserved(),{'1','2','3','4'})
                (root/'state'/'2026-10-06.json').write_text('{}')
                with self.assertRaises(runner.Stop): runner.previously_reserved()

    def test_queue_can_extend_beyond_90(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'solutions').mkdir()
            (root/'solutions'/'test.cpp').write_text('// fixture')
            plan=[dict(self.plan[0], day=i,slug=f'problem-{i}',solution='solutions/test.cpp') for i in range(1,92)]
            (root/'roadmap.json').write_text(json.dumps(plan))
            with patch.object(runner,'ROOT',root): self.assertEqual(len(runner.load_plan()),91)
