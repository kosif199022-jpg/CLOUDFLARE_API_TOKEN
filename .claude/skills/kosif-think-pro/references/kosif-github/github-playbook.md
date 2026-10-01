# GitHub playbook

## Tool mapping (use whichever the host actually exposes)
| Need | GitHub MCP tool | gh CLI | git |
|---|---|---|---|
| read a file | `get_file_contents` | `gh api repos/O/R/contents/P` | `git show HEAD:P` |
| list/search PRs | `list_pull_requests`, `search_pull_requests` | `gh pr list` | — |
| PR diff / status / checks | `pull_request_read` | `gh pr view --json`, `gh pr checks` | `git diff base...head` |
| CI logs | `actions_list`, `get_job_logs` | `gh run view --log-failed` | — |
| open PR | `create_pull_request` | `gh pr create` | — |
| comment / review | `add_issue_comment`, `pull_request_review_write` | `gh pr comment`, `gh pr review` | — |
| push files without a clone | `push_files`, `create_or_update_file` | — | `git push` |

## Commit message
```
<type optional>: <imperative summary ≤ 72 chars>

Why the change is needed (the problem), what it does at a high level,
and any trade-off or follow-up. Wrap near 72–100 columns.

Refs: #123 (if the repo links issues)
```
Types when the repo uses Conventional Commits: feat, fix, docs, refactor, test, perf, build, ci, chore.

## Pull-request body (when no template exists)
```
## Summary
- what changed and why (2–4 bullets)

## Test plan
- [x] command run → result (paste the real output line)
- [ ] manual check still to do

## Risk / rollback
- blast radius, feature flag, how to revert
```

## GitHub Actions recipes
Python:
```yaml
name: ci
on: [push, pull_request]
permissions: {contents: read}
jobs:
  test:
    runs-on: ubuntu-latest
    strategy: {matrix: {python: ["3.10", "3.12"]}}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "${{ matrix.python }}", cache: pip}
      - run: pip install -r requirements.txt
      - run: python -m pytest -q
```
Node:
```yaml
      - uses: actions/setup-node@v4
        with: {node-version: 22, cache: npm}
      - run: npm ci && npm test
```
Cloudflare Worker deploy (secret in the repo's Actions secrets, never in the file):
```yaml
      - run: npx wrangler deploy
        env: {CLOUDFLARE_API_TOKEN: "${{ secrets.CLOUDFLARE_API_TOKEN }}"}
```
Least privilege: set `permissions:` explicitly; pin third-party actions to a tag or SHA; never echo secrets.

## CI triage
| Symptom | Likely class | Action |
|---|---|---|
| fails in code the PR touched | this PR | reproduce locally, fix root cause, push once |
| same check red on the base branch | base branch | port an existing fix (or say none exists) and comment once |
| died before tests ran (checkout, install, runner lost) | infrastructure | one re-run at most |
| passes locally, fails in CI | environment difference | compare versions, env vars, timezone, locale, file order |
| intermittent | real bug (race, time, order) | make the test deterministic; never skip/disable it |

## Merge conflicts
1. `git fetch origin <base>` → `git merge origin/<base>` (merge commit keeps others' checkouts valid).
2. Resolve by intent: keep both sides' behaviour; ask only when both changed the same logic in incompatible ways.
3. Lockfiles/generated files: regenerate with the tool (`npm install`, `poetry lock`, the repo's generator), never hand-edit.
4. Run the tests, then push.

## Repository hygiene
`.gitignore` for the stack · README with run/test commands · CODEOWNERS for critical paths · branch protection: required checks + reviews on the default branch · Dependabot or Renovate for updates · SECURITY.md with private reporting · secrets only in the platform secret store.

## Lessons from the user's repositories
- `kosif199022-jpg/cloude` keeps encrypted data in git and the password outside it; builds are reproducible (`python3 build.py`) — follow the same pattern: secrets and keys never in the repository.
- `kosif199022-jpg/moon` runs CI and GitHub Pages workflows from `.github/workflows/` — reuse its split (ci.yml for tests, pages.yml for deploy).
- The Cloudflare Workers in `cloude` (`wrangler.*.toml`) take secrets through the platform store; mirror that for any new Worker.
