"""Send one GitHub mention notification per accepted UTC day; never submit code."""
import base64
from datetime import datetime, timedelta, timezone
import json
import os
import re
from runner import Stop, request_json


def notify(repo, branch, token, day, run_url, request=request_json):
    if repo != 'Parthivcodes/leetcode-90-day':
        raise Stop('Unexpected notification repository.')
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
               'User-Agent': 'leetcode-90-day'}
    base = f'https://api.github.com/repos/{repo}'
    saved = request(f'{base}/contents/state/{day}.json?ref={branch}', headers, allow_missing=True)
    if saved is None:
        print('No daily record; no acceptance notification.')
        return
    record = json.loads(base64.b64decode(saved['content']).decode())
    if record.get('status') != 'accepted':
        print('No confirmed acceptance; no acceptance notification.')
        return
    submission = record.get('submission_id')
    slug = record.get('slug', '')
    if (record.get('date') != day or record.get('calendar_timezone') != 'UTC'
            or record.get('verdict', {}).get('status_code') != 10
            or not isinstance(submission, int) or submission <= 0
            or not re.fullmatch(r'[a-z0-9-]+', slug)):
        raise Stop('Invalid acceptance record; notification blocked.')
    title = f'LeetCode Accepted {day}: {slug}'
    # A durable GitHub issue is both notification and deduplication record.
    # Workflow concurrency serializes backup runs; never retry a POST here.
    for page in range(1, 21):
        issues = request(f'{base}/issues?state=all&per_page=100&page={page}', headers)
        if not isinstance(issues, list):
            raise Stop('Notification history unavailable.')
        if any(issue.get('title') == title for issue in issues):
            print('Acceptance already announced; no duplicate email mention.')
            return
        if len(issues) < 100:
            break
    else:
        raise Stop('Notification history exceeds safe lookup limit.')
    body = (f'@Parthivcodes Your LeetCode submission was **Accepted** for **{day} UTC**.\n\n'
            f'Problem: **{slug}** (C++).\n\n'
            f'[View accepted submission](https://leetcode.com/submissions/detail/{submission}/)\n\n'
            f'[GitHub Actions run]({run_url})\n\n'
            'This notification runs on GitHub, even with your laptop off. '
            'Backups will not repeat this daily submission or acceptance mention.')
    result = request(f'{base}/issues', headers, {'title': title, 'body': body}, 'POST')
    print(f'Acceptance notification created: issue #{result["number"]}.')


if __name__ == '__main__':
    now = datetime.now(timezone.utc)
    day = now.date() - timedelta(days=1) if os.environ.get('MODE') == 'audit' else now.date()
    notify(os.environ['GITHUB_REPOSITORY'], os.environ['DEFAULT_BRANCH'],
           os.environ['GITHUB_TOKEN'], day.isoformat(),
           f'https://github.com/{os.environ["GITHUB_REPOSITORY"]}/actions/runs/{os.environ["GITHUB_RUN_ID"]}')
