# Scheduled setup in this fork

This fork tracks the upstream chat application (upstream commit `c74028c` at
the October 2026 migration). The task now opens `https://www.douyin.com/chat`
and uses the upstream login checks, conversation scanner and delivery receipts.

The existing `user-data` GitHub environment, `TASKS`, `COOKIES_*`, message
template and daily `0 1 * * *` UTC schedule remain in use.

## Configuration migration

- Replace `BROWSER_TIMEOUT` in milliseconds with `BROWSER_ACTION_TIMEOUT` in
  seconds: `120000` becomes `120`.
- `FRIEND_LIST_WAIT_TIME` now uses seconds: the old `2000` becomes `2`.
- `MATCH_MODE` is no longer consumed. Upstream matches supported account
  identifiers and display names automatically.
- Existing cookies may be expired or unsuitable for the new chat endpoint.
  Sign in using the upstream configuration app and refresh the matching
  `COOKIES_<unique_id>` secret when login checks fail.

## Diagnostics

The workflow enables `DOUYIN_CAPTURE_PAGES=1`. The `run-logs` artifact contains
screenshots and small metadata files for failed login checks, the ready friends
list before scanning, missing targets, and unexpected task errors.
Artifacts are retained for seven days; they can contain visible account/chat
information. Cookie values and browser storage are not exported by the capture
helper.

Unit tests run before account secrets are exported. Docker publishing is manual
in this fork, so updating the scheduled application does not publish a container.

Upstream considers GitHub Actions a legacy deployment option. A fresh hosted
runner does not preserve browser sessions or a stable network address between
runs. For persistent sessions, use the upstream local app or Docker deployment.
