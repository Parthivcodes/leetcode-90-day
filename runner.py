"""One calendar slot, one durable attempt, no automatic submission retries."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from datetime import date, datetime, timedelta, timezone
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPRedirectHandler

ROOT = Path(__file__).resolve().parent
IST = timezone(timedelta(hours=5, minutes=30))
EXPECTED = {'Linked Lists': 20, 'Hashing': 20, 'Arrays': 20, 'Strings': 15, 'Stacks and Queues': 15}

class Stop(RuntimeError):
    pass

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def request_json(url, headers, payload=None, method=None, allow_missing=False):
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(url, data=data, headers={**headers, 'Content-Type': 'application/json'}, method=method)
    try:
        with build_opener(NoRedirect()).open(req, timeout=30) as response:
            return json.load(response)
    except HTTPError as exc:
        if allow_missing and exc.code == 404:
            return None
        # Report only allowlisted diagnostics, never bodies, cookies, or signed URLs.
        from urllib.parse import urlsplit
        endpoint = urlsplit(url).hostname + urlsplit(url).path
        challenge = exc.headers.get('cf-mitigated') == 'challenge'
        detail = ' Cloudflare challenge detected.' if challenge else ''
        raise Stop(f'Request to {endpoint} failed with HTTP {exc.code}.{detail} No submission retry.') from None
    except Exception:
        raise Stop('Remote response unavailable or invalid; no submission retry.') from None

def load_plan():
    plan = json.loads((ROOT / 'roadmap.json').read_text())
    counts = {key: 0 for key in EXPECTED}
    seen = set()
    if len(plan) != 90:
        raise Stop('The roadmap must contain exactly 90 entries.')
    for day, p in enumerate(plan, 1):
        if p['day'] != day or p['slug'] in seen or p['difficulty'] not in ('Easy', 'Medium'):
            raise Stop('Invalid day, duplicate problem, or disallowed difficulty.')
        seen.add(p['slug'])
        if p['topic'] not in counts:
            raise Stop('Unknown topic.')
        counts[p['topic']] += 1
        path = (ROOT / p['solution']).resolve()
        if not path.is_relative_to((ROOT / 'solutions').resolve()) or path.suffix != '.cpp' or not path.is_file():
            raise Stop('Missing or invalid C++ solution file.')
    if counts != EXPECTED:
        raise Stop('Topic allocation differs from the approved 90-day plan.')
    return plan

def select_problem(plan, start, now):
    if not start:
        raise Stop('Set START_DATE (YYYY-MM-DD) before activating the schedule.')
    index = (now.astimezone(IST).date() - date.fromisoformat(start)).days
    return plan[index] if 0 <= index < 90 else None

def in_window(now):
    local = now.astimezone(IST)
    # A delayed run cannot spill into the next day or consume tomorrow's slot.
    return (8, 35) <= (local.hour, local.minute)

class Ledger:
    def __init__(self, repo, branch, token):
        if not repo or not branch or not token:
            raise Stop('GitHub repository, default branch, and token are required.')
        self.base = f'https://api.github.com/repos/{repo}/contents/state/'
        self.branch = branch
        self.headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json', 'User-Agent': 'leetcode-90-day'}

    def read(self, key):
        from urllib.parse import quote
        return request_json(self.base + key + '?ref=' + quote(self.branch, safe=''), self.headers, allow_missing=True)

    def write(self, key, record, previous=None):
        payload = {'message': f'Record daily slot {key}', 'branch': self.branch,
                   'content': base64.b64encode((json.dumps(record, indent=2)+'\n').encode()).decode()}
        if previous:
            payload['sha'] = previous['sha']
        return request_json(self.base + key, self.headers, payload, 'PUT')['content']

class LeetCode:
    def __init__(self, session, csrf):
        if not session or not csrf:
            raise Stop('Add LEETCODE_SESSION and LEETCODE_CSRF_TOKEN to GitHub Actions secrets.')
        self.headers = {'Cookie': f'LEETCODE_SESSION={session}; csrftoken={csrf}',
                        'x-csrftoken': csrf, 'Origin': 'https://leetcode.com',
                        'Referer': 'https://leetcode.com/', 'User-Agent': 'leetcode-90-day/1.0'}

    def graphql(self, query, variables=None):
        result = request_json('https://leetcode.com/graphql/', self.headers, {'query': query, 'variables': variables or {}})
        if result.get('errors') or not isinstance(result.get('data'), dict):
            raise Stop('LeetCode metadata or authentication check failed.')
        return result['data']

    def preflight(self, username, problem, now):
        status = self.graphql('{ userStatus { isSignedIn username } }')['userStatus']
        if not status or status.get('isSignedIn') is not True or status.get('username', '').lower() != username.lower():
            raise Stop('LeetCode session is expired or belongs to a different username.')
        question = self.graphql('query($slug:String!){question(titleSlug:$slug){questionId questionFrontendId titleSlug difficulty isPaidOnly codeSnippets{langSlug code}}}', {'slug': problem['slug']})['question']
        if not question or question.get('titleSlug') != problem['slug'] or str(question.get('questionFrontendId')) != str(problem['number']):
            raise Stop('Problem identity could not be verified.')
        if question.get('difficulty') not in ('Easy', 'Medium') or question.get('isPaidOnly') is not False:
            raise Stop('Hard, premium, or unverified problem: submission blocked.')
        if not any(x.get('langSlug') == 'cpp' for x in question.get('codeSnippets', [])):
            raise Stop('C++ is not available for this problem.')
        history = request_json('https://leetcode.com/api/submissions/?offset=0&limit=20', self.headers)
        submissions = history.get('submissions_dump')
        if not isinstance(submissions, list) or (not submissions and history.get('has_next')):
            raise Stop('Submission history could not be verified.')
        for submission in submissions:
            try:
                stamp = datetime.fromtimestamp(int(submission['timestamp']), timezone.utc)
            except (KeyError, ValueError, TypeError):
                raise Stop('Submission history has an invalid timestamp.') from None
            if stamp.astimezone(IST).date() == now.astimezone(IST).date() or stamp.date() == now.astimezone(timezone.utc).date():
                return question, False
        return question, True

    def submit_once(self, question, problem, code):
        headers = {**self.headers, 'Referer': f"https://leetcode.com/problems/{problem['slug']}/"}
        result = request_json(f"https://leetcode.com/problems/{problem['slug']}/submit/", headers,
                              {'lang': 'cpp', 'question_id': str(question['questionId']), 'typed_code': code})
        submission_id = result.get('submission_id')
        if not isinstance(submission_id, int):
            raise Stop('Submission outcome unknown. The slot remains reserved; do not resubmit.')
        return submission_id

    def verdict(self, submission_id):
        for _ in range(12):
            result = request_json(f'https://leetcode.com/submissions/detail/{submission_id}/check/', self.headers)
            if result.get('state') == 'SUCCESS':
                return {'status_code': result.get('status_code'), 'status_msg': result.get('status_msg', 'Unknown')}
            time.sleep(3)
        return {'status_code': None, 'status_msg': 'Pending; inspect LeetCode manually'}


def require_completed(saved, key):
    try:
        record = json.loads(base64.b64decode(saved['content']).decode())
    except (KeyError, ValueError, TypeError):
        raise Stop(f'Unreadable daily record {key}; no retry.') from None
    if record.get('date') != key[:-5] or record.get('status') not in ('accepted', 'skipped-existing-submission'):
        raise Stop(f'Unconfirmed daily record {key}; inspect Actions and LeetCode. No retry.')
    return record

def audit_previous_day(config, plan, now, ledger):
    # Audit a completed IST date only; this operation never submits.
    yesterday = now.astimezone(IST).date() - timedelta(days=1)
    probe = datetime.combine(yesterday, datetime.min.time(), tzinfo=IST)
    if select_problem(plan, config['start_date'], probe) is None:
        print('Previous day outside the plan; no audit needed.')
        return
    key = yesterday.isoformat() + '.json'
    saved = ledger.read(key)
    if saved is None:
        raise Stop(f'Missed daily submission for {yesterday}; no record exists. No catch-up submission.')
    require_completed(saved, key)
    print(f'Daily audit passed for {yesterday}.')

def run_live(config, plan, now, lc, ledger):
    problem = select_problem(plan, config['start_date'], now)
    if problem is None:
        print('Outside the 90-day period; no submission.')
        return
    key = now.astimezone(IST).date().isoformat() + '.json'
    existing = ledger.read(key)
    if existing is not None:
        require_completed(existing, key)
        print('Today already completed; no submission.')
        return
    if not in_window(now):
        raise Stop('Missed submission window (08:35 to midnight IST); no submission.')
    question, allowed = lc.preflight(config['username'], problem, now)
    record = {'date': key[:-5], 'day': problem['day'], 'slug': problem['slug'],
              'at': now.isoformat(), 'status': 'reserved' if allowed else 'skipped-existing-submission'}
    code = (ROOT / problem['solution']).read_text()
    record['code_sha256'] = hashlib.sha256(code.encode()).hexdigest()
    # Create without a SHA: GitHub rejects an existing file atomically.
    # If this write times out, never submit. The reservation may already exist.
    saved = ledger.write(key, record)
    if not allowed:
        print('Existing submission today; the scheduled problem is skipped.')
        return
    try:
        submission_id = lc.submit_once(question, problem, code)
        record.update(status='submitted', submission_id=submission_id)
        saved = ledger.write(key, record, saved)
        verdict = lc.verdict(submission_id)
        record.update(status='accepted' if verdict['status_code'] == 10 else 'needs-review', verdict=verdict)
        ledger.write(key, record, saved)
        print(f"Day {problem['day']}: {problem['slug']}: {record['status']}")
        if record['status'] != 'accepted':
            raise Stop('Submission was not confirmed accepted. No retry will be made.')
    except Exception as exc:
        # Reservation must remain even after a crash, HTTP timeout, or reporting failure.
        if isinstance(exc, Stop):
            raise
        raise Stop('Attempt stopped after reservation; inspect the saved record. No retry.') from None

def diagnose_session(session, now):
    # Decode expiry only; this is not signature verification or proof of validity.
    try:
        encoded = session.split('.')[1]
        claims = json.loads(base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4)))
        expiry = datetime.fromtimestamp(int(claims['exp']), timezone.utc)
    except (IndexError, KeyError, ValueError, TypeError, AttributeError):
        print('Saved session expiry is not readable; authenticated check is required.')
        return
    print(f'Saved session declared expiry: {expiry.isoformat()}; expired: {now >= expiry}. Signature not verified.')

def diagnose_public_access():
    headers = {'User-Agent': 'leetcode-90-day/1.0', 'Origin': 'https://leetcode.com', 'Referer': 'https://leetcode.com/'}
    try:
        result = request_json('https://leetcode.com/graphql/', headers, {'query': '{ userStatus { isSignedIn } }'})
        print(f'Anonymous GraphQL reachable: {isinstance(result.get("data"), dict)}')
    except Stop as exc:
        print(f'Anonymous connectivity check: {exc}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['preview', 'preflight', 'live', 'audit'], default='preview')
    parser.add_argument('--day', type=int, default=1)
    args = parser.parse_args()
    config = json.loads((ROOT / 'config.json').read_text())
    config['start_date'] = os.environ.get('START_DATE') or config['start_date']
    plan = load_plan()
    if not 1 <= args.day <= 90:
        raise Stop('Preview day must be between 1 and 90.')
    if args.mode == 'preview':
        p = plan[args.day-1]
        print(json.dumps({'username': config['username'], **p, 'submitted': False}, indent=2))
        return
    now = datetime.now(timezone.utc)
    if args.mode == 'preflight':
        lc = LeetCode(os.environ.get('LEETCODE_SESSION'), os.environ.get('LEETCODE_CSRF_TOKEN'))
        diagnose_session(os.environ.get('LEETCODE_SESSION'), now)
        diagnose_public_access()
        _, allowed = lc.preflight(config['username'], plan[args.day-1], now)
        print(f'Authentication and problem checks passed. Daily slot available: {allowed}. Nothing submitted.')
        return
    if os.environ.get('ENABLE_SUBMISSIONS') != 'true':
        raise Stop('Live submissions are disabled.')
    ledger = Ledger(os.environ.get('GITHUB_REPOSITORY'), os.environ.get('DEFAULT_BRANCH'), os.environ.get('GITHUB_TOKEN'))
    if args.mode == 'audit':
        audit_previous_day(config, plan, now, ledger)
        return
    lc = LeetCode(os.environ.get('LEETCODE_SESSION'), os.environ.get('LEETCODE_CSRF_TOKEN'))
    run_live(config, plan, now, lc, ledger)

if __name__ == '__main__':
    try:
        main()
    except (Stop, ValueError) as exc:
        print(f'Stopped: {exc}', file=sys.stderr)
        sys.exit(1)
