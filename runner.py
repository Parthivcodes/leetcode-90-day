"""An extendable queue, one accepted submission per UTC day, no repeated problems."""
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

MAX_DAILY_ATTEMPTS = 3
REJECTION_VERDICTS = {
    'Wrong Answer', 'Compile Error', 'Runtime Error', 'Time Limit Exceeded',
    'Memory Limit Exceeded', 'Output Limit Exceeded',
}

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
    seen = set()
    if not plan:
        raise Stop('The problem queue is empty; add prepared solutions.')
    for day, p in enumerate(plan, 1):
        if p['day'] != day or p['slug'] in seen or p['difficulty'] not in ('Easy', 'Medium'):
            raise Stop('Invalid day, duplicate problem, or disallowed difficulty.')
        seen.add(p['slug'])
        if not isinstance(p.get('topic'), str) or not p['topic'].strip():
            raise Stop('Every problem needs a topic.')
        path = (ROOT / p['solution']).resolve()
        if not path.is_relative_to((ROOT / 'solutions').resolve()) or path.suffix != '.cpp' or not path.is_file():
            raise Stop('Missing or invalid C++ solution file.')
    return plan

def select_problem(plan, start, now, submitted=()):
    if not start:
        raise Stop('Set START_DATE (YYYY-MM-DD) before activating the schedule.')
    index = (now.astimezone(timezone.utc).date() - date.fromisoformat(start)).days
    if index < 0:
        return None
    return next((p for p in plan if p['slug'] not in submitted), None)


def previously_reserved():
    """Keep ambiguous attempts excluded even if LeetCode history omits them."""
    used = set()
    for path in (ROOT / 'state').glob('????-??-??.json'):
        try:
            record = json.loads(path.read_text())
            status = record['status']
            if status in ('reserved', 'submitted', 'accepted', 'needs-review', 'rejected'):
                slug = record['slug']
                if not isinstance(slug, str) or not slug:
                    raise ValueError()
                used.add(slug)
            used.update(attempt['slug'] for attempt in record.get('rejected_attempts', []))
            if status not in ('reserved', 'submitted', 'accepted', 'needs-review', 'rejected', 'skipped-existing-submission'):
                raise ValueError()
        except (KeyError, ValueError, TypeError):
            raise Stop(f'Invalid historical record {path.name}; selection blocked.') from None
    return used

def in_window(now):
    utc = now.astimezone(timezone.utc)
    return (3, 5) <= (utc.hour, utc.minute)

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

    def submission_history(self, username, now, rejected_ids=()):
        status = self.graphql('{ userStatus { isSignedIn username } }')['userStatus']
        if not status or status.get('isSignedIn') is not True or status.get('username', '').lower() != username.lower():
            raise Stop('LeetCode session is expired or belongs to a different username.')
        used, ids = set(), set()
        today = False
        # Exhaust all pages, not only recent/accepted submissions. Fail closed
        # if history is unavailable, malformed, repeats, or exceeds the bound.
        offset = 0
        for _ in range(500):
            history = self.graphql('query($offset:Int!){submissionList(offset:$offset,limit:100){hasNext submissions{id timestamp titleSlug statusDisplay}}}', {'offset': offset}).get('submissionList')
            if not isinstance(history, dict) or not isinstance(history.get('hasNext'), bool):
                raise Stop('Complete submission history could not be verified.')
            submissions = history.get('submissions')
            if not isinstance(submissions, list) or (not submissions and history['hasNext']):
                raise Stop('Complete submission history could not be verified.')
            for submission in submissions:
                try:
                    slug = submission['titleSlug']
                    ident = str(submission['id'])
                    stamp = datetime.fromtimestamp(int(submission['timestamp']), timezone.utc)
                    if not isinstance(slug, str) or not slug or not ident or ident in ids:
                        raise ValueError()
                except (KeyError, ValueError, TypeError, OverflowError):
                    raise Stop('Submission history is incomplete or repeated; selection blocked.') from None
                ids.add(ident)
                used.add(slug)
                today |= (stamp.date() == now.astimezone(timezone.utc).date()
                          and (ident not in rejected_ids or submission.get('statusDisplay') not in REJECTION_VERDICTS))
            if not history['hasNext']:
                return used, today
            offset += len(submissions)
        raise Stop('Submission history exceeds 500 pages; selection blocked rather than risking a repeat.')

    def question_details(self, problem):
        question = self.graphql('query($slug:String!){question(titleSlug:$slug){questionId questionFrontendId titleSlug status difficulty isPaidOnly codeSnippets{langSlug code}}}', {'slug': problem['slug']})['question']
        if not question or question.get('titleSlug') != problem['slug'] or str(question.get('questionFrontendId')) != str(problem['number']):
            raise Stop('Problem identity could not be verified.')
        if question.get('difficulty') not in ('Easy', 'Medium') or question.get('isPaidOnly') is not False:
            raise Stop('Hard, premium, or unverified problem: submission blocked.')
        if not any(x.get('langSlug') == 'cpp' for x in question.get('codeSnippets', [])):
            raise Stop('C++ is not available for this problem.')
        if 'status' not in question or question['status'] not in (None, 'ac', 'notac'):
            raise Stop('Problem submission status could not be verified.')
        return question

    def next_problem(self, username, plan, now, used, rejected_ids=()):
        history, today = (self.submission_history(username, now, rejected_ids) if rejected_ids
                          else self.submission_history(username, now))
        if today:
            return None, None, False
        used = set(used) | history
        for problem in plan:
            if problem['slug'] in used:
                continue
            question = self.question_details(problem)
            # Status also catches solved/attempted problems omitted from history.
            if question['status'] is not None:
                continue
            return problem, question, True
        raise Stop('No unsubmitted prepared problems remain. Add new easy/medium solutions to roadmap.json; the schedule remains enabled.')

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


def read_daily_record(saved, key):
    try:
        record = json.loads(base64.b64decode(saved['content']).decode())
    except (KeyError, ValueError, TypeError):
        raise Stop(f'Unreadable daily record {key}; no retry.') from None
    if not isinstance(record, dict) or record.get('date') != key[:-5]:
        raise Stop(f'Invalid daily record {key}; no retry.')
    return record


def require_completed(saved, key):
    record = read_daily_record(saved, key)
    if record.get('status') not in ('accepted', 'skipped-existing-submission'):
        raise Stop(f'Unconfirmed daily record {key}; inspect Actions and LeetCode. No retry.')
    return record

def audit_previous_day(config, plan, now, ledger):
    # Audit a completed LeetCode (UTC) date only; never submit here.
    yesterday = now.astimezone(timezone.utc).date() - timedelta(days=1)
    probe = datetime.combine(yesterday, datetime.min.time(), tzinfo=timezone.utc)
    if select_problem(plan, config['start_date'], probe) is None:
        print('Previous day outside the plan; no audit needed.')
        return
    key = yesterday.isoformat() + '.json'
    saved = ledger.read(key)
    if saved is None:
        raise Stop(f'Missed daily submission for {yesterday}; no record exists. No catch-up submission.')
    require_completed(saved, key)
    print(f'Daily audit passed for {yesterday}.')

def run_live(config, plan, now, lc, ledger, manual=False):
    started = time.monotonic()
    if select_problem(plan, config['start_date'], now) is None:
        print('Before start date; no submission.')
        return
    key = now.astimezone(timezone.utc).date().isoformat() + '.json'
    saved = ledger.read(key)
    rejected = []
    if saved is not None:
        previous = read_daily_record(saved, key)
        if previous.get('status') == 'rejected':
            rejected = previous.get('rejected_attempts', []) + [
                {k: previous[k] for k in ('slug', 'submission_id', 'verdict')}
            ]
            if any(type(attempt['submission_id']) is not int or attempt['submission_id'] <= 0
                   or attempt['verdict'].get('status_msg') not in REJECTION_VERDICTS
                   or attempt['verdict'].get('status_code') in (None, 10)
                   for attempt in rejected):
                raise Stop('Unverified rejection in the daily record; no retry.')
        else:
            require_completed(saved, key)
            if previous['status'] == 'accepted' or previous.get('calendar_timezone') == 'UTC':
                print('Today already completed; no submission.')
                return
            print('Rechecking legacy IST skip against LeetCode UTC history.')
    if not in_window(now) and not manual:
        raise Stop('Outside submission window (03:05 to midnight UTC); no submission.')

    used = previously_reserved()
    while len(rejected) < MAX_DAILY_ATTEMPTS:
        excluded = used | {attempt['slug'] for attempt in rejected}
        if rejected:
            ids = {str(attempt['submission_id']) for attempt in rejected}
            problem, question, allowed = lc.next_problem(config['username'], plan, now, excluded, ids)
        else:
            problem, question, allowed = lc.next_problem(config['username'], plan, now, excluded)
        record = {'date': key[:-5], 'at': now.isoformat(), 'calendar_timezone': 'UTC',
                  'status': 'reserved' if allowed else 'skipped-existing-submission',
                  'rejected_attempts': rejected.copy()}
        if allowed:
            code = (ROOT / problem['solution']).read_text()
            record.update(day=problem['day'], slug=problem['slug'],
                          code_sha256=hashlib.sha256(code.encode()).hexdigest())
        elapsed = timedelta(seconds=time.monotonic() - started)
        if allowed and (now.astimezone(timezone.utc) + elapsed).date().isoformat() != key[:-5]:
            raise Stop('UTC day ended before the question could submit.')
        # GitHub's file SHA prevents competing workers from reserving the same slot.
        saved = ledger.write(key, record, saved)
        if not allowed:
            print('Existing submission today; queue is unchanged.')
            return
        submission_id = lc.submit_once(question, problem, code)
        record.update(status='submitted', submission_id=submission_id)
        saved = ledger.write(key, record, saved)
        verdict = lc.verdict(submission_id)
        if verdict['status_code'] == 10:
            status = 'accepted'
        elif verdict['status_code'] is not None and verdict['status_msg'] in REJECTION_VERDICTS:
            status = 'rejected'
        else:
            status = 'needs-review'
        record.update(status=status, verdict=verdict)
        saved = ledger.write(key, record, saved)
        print(f"{problem['slug']}: {verdict['status_msg']}")
        if status == 'accepted':
            return
        if status == 'needs-review':
            raise Stop('Submission outcome is unconfirmed. No fallback will be sent.')
        rejected.append({'slug': problem['slug'], 'submission_id': submission_id, 'verdict': verdict})

    raise Stop(f'All {MAX_DAILY_ATTEMPTS} daily attempts were rejected; no acceptance today.')


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
    if not 1 <= args.day <= len(plan):
        raise Stop(f'Preview queue position must be between 1 and {len(plan)}.')
    if args.mode == 'preview':
        p = plan[args.day-1]
        print(json.dumps({'username': config['username'], **p, 'submitted': False}, indent=2))
        return
    now = datetime.now(timezone.utc)
    if args.mode == 'preflight':
        lc = LeetCode(os.environ.get('LEETCODE_SESSION'), os.environ.get('LEETCODE_CSRF_TOKEN'))
        diagnose_session(os.environ.get('LEETCODE_SESSION'), now)
        diagnose_public_access()
        problem, _, allowed = lc.next_problem(config['username'], plan, now, previously_reserved())
        print(f'Complete history and queue checks passed. Daily slot available: {allowed}. Nothing submitted.')
        if problem:
            print(f"Next unsubmitted problem: {problem['slug']} (queue position {problem['day']}).")
        return
    if os.environ.get('ENABLE_SUBMISSIONS') != 'true':
        raise Stop('Live submissions are disabled.')
    ledger = Ledger(os.environ.get('GITHUB_REPOSITORY'), os.environ.get('DEFAULT_BRANCH'), os.environ.get('GITHUB_TOKEN'))
    if args.mode == 'audit':
        audit_previous_day(config, plan, now, ledger)
        return
    lc = LeetCode(os.environ.get('LEETCODE_SESSION'), os.environ.get('LEETCODE_CSRF_TOKEN'))
    run_live(config, plan, now, lc, ledger, manual=os.environ.get('GITHUB_EVENT_NAME') == 'workflow_dispatch')

if __name__ == '__main__':
    try:
        main()
    except (Stop, ValueError) as exc:
        print(f'Stopped: {exc}', file=sys.stderr)
        sys.exit(1)
