# Bug List (re-review of main @ ad9e14e, 2026-10-13)

Replaces the Week 0 list. Every "confirmed" item was reproduced by sending real requests to the app against a throwaway test database, not only by reading the code.

IDs are permanent: closed items keep their number, and new items continue from B12.

Workflow for each fix (Week 1 step 4): write the test, watch it fail, fix, watch it pass, then commit the test and the fix separately.

## Corrections to the Week 0 list

The Week 0 list was written from the database dump without reading the route code, so three items were wrong when they were written.

| # | Week 0 claim | Status now | Why |
|---|---|---|---|
| B1 | `parent_id` validated against `Post` | **Not applicable** | Already fixed in 6cfd8e4 (`Comment.get_or_404(parent_id)`). |
| B2 | Reply can point at a comment on another post | **Fixed in code** | `create_comment` compares `post_id` with `parent.post_id`. Needs a test. The comparison has a type bug, see B19. |
| B3 | Score updated read-modify-write in Python | **Open (Week 7)** | Confirmed by reading: `post.score += value`. Loses votes under concurrency. |
| B4 | Vote change math (+1 → −1 must move the score by 2) | **No bug found** | `diff = value - vote.value` is correct. Keep it as a test in step 3e. |
| B5 | Deleting a post with children fails on the FK | **Not applicable** | `delete_cascade()` helpers delete the children first (1daef9c, 5519b60). New problems in those helpers: B21. |
| B6 | Soft delete has no column | **Answered** | Soft delete overwrites `content` with `"[Comment Deleted]"`. New problem with that design: B22. |
| B7 | Vote `value` has no CHECK | **Partly covered** | The route checks the value, but the check leaks, see B16. |
| B8 | `communities.name` not unique | **Open, confirmed** | Duplicate names return 201. The `except IntegrityError → 409` branch in `create_community` is dead code because no constraint can raise it. |
| B9 | Case-sensitive username/email | **Open (decision)** | Unchanged. |
| B10 | Timestamps and `utcnow()` | **Open** | Merged with W1. Also: `SavedPost`/`HiddenPost` use `datetime.now` (local time), the rest use `utcnow`. |
| B11 | Whitespace-only registration | **Fixed** | 3f7fb04 (test) + ad9e14e (fix). |

## New bugs

### Server errors (500) — should be 4xx

| # | Where | Bug | Evidence |
|---|---|---|---|
| B12 | `posts.py` `delete_post` | Non-author delete returns **500**: `jsonify({"error", "..."})` uses a comma, so it builds a **set**, which is not JSON-serializable. | confirmed |
| B15 | `posts.py` `create_post`, `comments.py` `create_comment` | No type checks: `community_id="abc"` / `post_id="abc"` → 500 (`DataError` from Postgres); `title` or `content` as a dict → 500 (`can't adapt type 'dict'`). | confirmed |
| B16 | `posts.py` `post_vote`, `comments.py` `comment_vote` | Vote value check leaks. Post: `1.0` is accepted (`1.0 in [1, 0, -1]` is `True`), `true` → 500. Comment: `"1"` passes `int(value)` then `score += "1"` → 500; `"abc"` → `int()` raises → 500. Note `True == 1` in Python, so `isinstance(value, int)` alone still lets booleans through. | confirmed |
| B20b | `auth.py` `login` (main) | `password` as an int → 500 (`int.encode`). | confirmed on main; likely fixed in your unpushed 3b/3c work, verify |

### Wrong acceptance

| # | Where | Bug | Evidence |
|---|---|---|---|
| B17 | both vote routes | A **first** vote with `value: 0` inserts a vote row with value 0. Value 0 means "no vote", so nothing should be stored. | confirmed |
| B18 | communities, posts, comments | Blank or whitespace-only `name` / `title` / comment `content` is accepted (201/200). Same bug as B11 in other routes. | confirmed |
| B19 | `comments.py` `create_comment` | Reply with `post_id` sent as the string `"1"` gets a false 400: `"1" != 1`. Disappears once B15 enforces int. | confirmed |

### HTTP semantics

| # | Where | Bug | Evidence |
|---|---|---|---|
| B13 | delete post / comment / community | "Not your resource" returns **400**. 400 means a malformed request; this should be **403 Forbidden**. | confirmed |
| B14 | create post, create comment | Return **200**; creating a resource should return **201** (create community already does). | confirmed |
| B23 | posts, communities vs `/auth/me` | A valid token for a deleted user gives three different answers: `/auth/me` → 401 "the account doesn't exist", create post → 404 "not found", create community → 400 "account not found". One rule, one place: Flask-JWT-Extended's `user_lookup_loader` + `user_lookup_error_loader`. | confirmed |

### Security

| # | Where | Bug | Evidence |
|---|---|---|---|
| B20a | `auth.py` `login` (main) | User enumeration: unknown email → "the account doesn't exist", wrong password → "invalid password". | confirmed on main; **fixed locally, not pushed** |
| B20c | `auth.py` `login` | Register stores the stripped email, but login looks up the raw value, so `"alice@example.com "` cannot log in. | confirmed on main; verify your local version |
| B24 | `config.py` `TestingConfig` | Test JWT key is 24 bytes; PyJWT warns (`InsecureKeyLengthWarning`) on every test because HS256 wants ≥ 32 bytes. | confirmed (pytest warning) |
| B26 | `frontend/src/api/client.ts` | `apiFetch` logs the request options, including the `Authorization` header (the JWT), to the browser console. | read |

### Data integrity (later weeks)

| # | Where | Bug | Evidence |
|---|---|---|---|
| B21 | `delete_cascade()` in `Post`, `Comment`, votes | (a) Helpers call `commit()` per child, so a failure halfway leaves a half-deleted tree: not atomic. (b) `Post.delete_cascade` loops over **all** comments of the post, including replies already deleted by their parent's recursion → SQLAlchemy warns "expected to delete 1 row(s); 0 were matched". All rows do end up gone. | confirmed (warnings) |
| B22 | comments soft delete | The deleted marker is the content itself. A live comment whose text is literally `[Comment Deleted]` is treated as deleted: voting on it returns 400. Fix: an `is_deleted` column (migration). | confirmed |
| B25 | `get_or_404` helpers, `User.query.get_or_404` | `Query.get()` is legacy in SQLAlchemy 2.0 (`LegacyAPIWarning`). Rewrite with `db.session.get()` / `select()`. | confirmed (warning) |

### Frontend

| # | Where | Bug | Evidence |
|---|---|---|---|
| B27 | `frontend/src/api/client.ts` | `apiFetch` always calls `response.json()`; a `204 No Content` (every DELETE) has no body, so it throws. | read |

## Repo hygiene

| # | Issue | Why it matters |
|---|---|---|
| H1 | `.claude/settings.json`, `.vscode/settings.json` and `frontend/.env` are **still tracked on main**. This is not a regression: `git log --diff-filter=D` shows they were never removed on main; the `git rm --cached` commits did not make it into PR #1. `.gitignore` only affects untracked files. | `.claude/settings.json` publishes your local tool allow-list; `frontend/.env` holds only a URL today, but the next secret put there would be pushed. |
| H2 | `backend/requirements.txt` is a full `pip freeze` (72 lines: Jupyter, IPython, pipreqs, …). | CI (step 5) installs all of it on every run. Keep direct runtime dependencies only. |
| H3 | `backend/.env.example` on main still has `FLASK_ENV` (C15 was marked fixed — probably only locally). | Someone cloning the repo copies an obsolete key. |
| H4 | `CORS(app)` allows every origin. | Restrict to the frontend origin at deployment (Week 2 / 8). |

## Triage

| When | Items |
|---|---|
| **Week 1 step 4** (test-first) | B12, B15 + B19, B16, B17, B18, B13, B14, B20 (push + verify), B24, B10/W1 |
| **Before step 5 CI** | H1, H2, H3 |
| **Week 1 if time, else Week 6** | B8 (needs a migration and a check for existing duplicates), B23 |
| **Week 6** (SQLAlchemy depth) | B21, B22, B25 |
| **Week 7** | B3 |
| **Weeks 3–5** (frontend) | B26, B27 |
| **Deployment** | H4 |
| **Decision pending** | B9 |

## Performance (Week 7, not bugs yet)

- The global feed (latest 25 posts) sorts by `created_at`, which has no standalone index. Measure at 100k rows.
- No index on `post_votes(post_id)` / `comment_votes(comment_id)`: lookups by target scan the table, and `delete_cascade` does exactly those lookups.