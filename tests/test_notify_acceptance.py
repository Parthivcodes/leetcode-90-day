import base64
import json
import unittest
from unittest.mock import Mock
from notify_acceptance import notify


class NotificationTests(unittest.TestCase):
    def record(self, status='accepted'):
        return {'content': base64.b64encode(json.dumps({
            'date': '2026-10-31', 'calendar_timezone': 'UTC', 'status': status,
            'slug': 'linked-list-cycle', 'submission_id': 123,
            'verdict': {'status_code': 10}}).encode()).decode()}

    def test_accepted_creates_one_mention_with_submission_link(self):
        request = Mock(side_effect=[self.record(), [], {'number': 1}])
        notify('Parthivcodes/leetcode-90-day', 'main', 'test-token', '2026-10-31', 'https://github.com/run', request)
        payload = request.call_args_list[-1].args[2]
        self.assertIn('@Parthivcodes', payload['body'])
        self.assertIn('/submissions/detail/123/', payload['body'])
        self.assertEqual(request.call_args_list[-1].args[3], 'POST')

    def test_backup_does_not_repeat_acceptance_mention(self):
        request = Mock(side_effect=[self.record(), [{'title': 'LeetCode Accepted 2026-10-31: linked-list-cycle'}]])
        notify('Parthivcodes/leetcode-90-day', 'main', 'test-token', '2026-10-31', 'https://github.com/run', request)
        self.assertEqual(request.call_count, 2)

    def test_unconfirmed_or_skipped_record_never_claims_acceptance(self):
        for status in ('reserved', 'submitted', 'needs-review', 'skipped-existing-submission'):
            request = Mock(return_value=self.record(status))
            notify('Parthivcodes/leetcode-90-day', 'main', 'test-token', '2026-10-31', 'https://github.com/run', request)
            self.assertEqual(request.call_count, 1)
