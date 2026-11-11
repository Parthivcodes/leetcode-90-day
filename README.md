# Daily C++ practice � ongoing

Prepared for **GandhiSmit06**. [Open the initial 90-question queue](ROADMAP.md).

| Queue positions | Topic | Questions |
|---|---|---:|
| 1–20 | Linked Lists | 20 |
| 21–40 | Hashing | 20 |
| 41–60 | Arrays | 20 |
| 61–75 | Strings | 15 |
| 76–90 | Stacks and Queues | 15 |

90 original C++ solutions, easy and medium only. The live runner also checks the current LeetCode difficulty and premium status before submitting. There are no AI calls, paid dependencies, Render services, or ChatGPT automations.

## Activation

**Live submissions are disabled until setup and authenticated checks pass.**

1. In this repository, open **Settings → Secrets and variables → Actions**.
2. Sign in to the intended LeetCode account in your own browser. In that browser's developer tools, under Application/Storage → Cookies → `https://leetcode.com`, find `LEETCODE_SESSION` and `csrftoken`. Add their values directly to GitHub repository secrets named `LEETCODE_SESSION` and `LEETCODE_CSRF_TOKEN`. Do not put these values in chat, source files, screenshots, issues, or logs. Treat them like passwords. No password is stored by this project.
3. Under **Variables**, set `START_DATE` to the intended first day in `YYYY-MM-DD` format. Choose a date whose 08:35 IST run has not passed. Keep this date fixed after starting.
4. Run **Daily C++ practice → Run workflow → preview**, then **preflight**. Preview is offline. Preflight verifies authentication, identity, current problem metadata, and submission history without submitting.
5. Only after preflight succeeds, set repository variable `ENABLE_SUBMISSIONS` to `true`. Remove it or set it to `false` to pause. Default-branch workflow write access must be allowed for the daily ledger. The workflow requests repository contents access for its ledger and issues access for acceptance notifications.

The primary daily run is **08:35 IST**, with backups at **12:35, 18:35, and 21:35 IST**. Live runs may operate from 08:35 IST until the end of the current UTC day (05:30 IST the next morning). A read-only audit at **06:35 IST** checks the previous UTC calendar day and fails if its record is missing or unconfirmed. Manual `live` runs use the current calendar day, never the preview day field. There is no end date or 90-day cutoff. The schedule continues until you disable it. The runner takes the first never-submitted problem from the ordered queue, skipping any previously attempted problem regardless of outcome.

## Submission limit and failure behavior

- The bot stops at the first Accepted verdict and tries at most three distinct questions per LeetCode UTC date. Only its own confirmed rejections are excluded from the same-day submission guard. A submission before 05:30 IST belongs to the previous LeetCode day.
- The runner reserves the day's slot in `state/YYYY-MM-DD.json (UTC date)` **before** contacting the submission endpoint. The GitHub file creation is atomic. Concurrency is also serialized by the workflow.
- Backup runs can resume after a confirmed rejection by trying a different question. Accepted or manually covered days exit successfully. Reserved or pending attempts stop for review.
- Out-of-window runs without a completed record fail instead of silently succeeding. The morning audit catches a day when no submission run started. Both use GitHub Actions failure emails; enable Email and Only notify for failed workflows in your GitHub notification settings. If GitHub never starts any job including the audit, GitHub alone cannot alert about its own total outage.
- If a request times out, the reservation stays. A rerun cannot submit again. This intentionally favors avoiding duplicates over guaranteeing daily success.
- Final wrong answers, compile errors, runtime errors, and resource-limit verdicts allow a different question. Expired sessions, HTTP failures, and unknown responses stop the run. Investigate failures in Actions; refresh expired credentials directly in GitHub secrets.
- No catch-up batches. Missing a day leaves the queue unchanged. Each available day uses the next unseen problem, not a calendar-indexed problem.
- Complete authenticated submission history and per-problem status are checked before selection. Historical bot reservations also exclude uncertain attempts. If history cannot be verified, no submission is sent.
- The initial queue contains 90 prepared solutions. Append new unique easy/medium problems and tested C++ solutions to `roadmap.json` in the desired topic order; `day` is a sequential queue position. The next topic sequence is awaiting your instructions. Repeating a topic must use new problems.
- If the prepared queue is exhausted, the run fails with a clear message so failure notifications can alert you. The schedule stays enabled, but cannot submit until new solutions are added.
- Do not delete or edit ledger records or change `START_DATE` during the run. Doing so can defeat the daily limit.
- The bot cannot prevent you from submitting manually after it runs, or eliminate a race with a simultaneous manual submission. Avoid submitting manually around the scheduled time if the account-wide limit must remain one.

## Free execution and reliability

The daily job refuses to execute if the repository is not public. No artifacts, caches, paid notification services, AI calls, or larger runners are added.

Use this **public repository** with standard `ubuntu-latest` hosted runners. Those runners are free for public repositories; larger runners and paid services are not used. Secrets remain in GitHub's secret storage. Do not change to private runners, paid services, or a private repository without reviewing the free allowance first.

GitHub schedules may be delayed or dropped. Public repository schedules can be disabled after 60 days without activity; successful daily ledger commits keep the repository active, but a prolonged failure needs manual attention. Enable GitHub Actions failure notifications for your account. Hosting does not guarantee daily streak credit.

LeetCode's submission endpoints are undocumented and can change or reject hosted runners. This is an experimental integration, not an official LeetCode API. It stops on access controls and does not bypass CAPTCHA or bot protection. Review [LeetCode's terms](https://leetcode.com/terms/), including its restrictions on automated processes, before activation.

## Verification

```sh
python3 -m unittest discover -s tests -v
python3 tests/check_cpp.py
python3 runner.py --mode preview --day 1
```

The C++ check compiles all 90 solution classes and runs sample/edge assertions for each. These tests are not equivalent to LeetCode's full hidden tests. An authenticated preflight and an actual accepted submission must be observed before declaring live automation verified.

References: [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [scheduled workflow limitations](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

The UTC calendar fix safely rechecks old IST skip records against authenticated UTC submission history. It never clears or retries an existing accepted, reserved, submitted, or rejected bot attempt. An explicitly dispatched manual live run may run earlier than 08:35 IST but still uses the current UTC date and the same daily reservation.
