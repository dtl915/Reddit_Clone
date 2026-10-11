# Bug List and Open Questions (Week 0 review)

Each item gets a pytest test in Week 1: write the test first, watch it fail (or pass, which closes the question), then fix.

Status: `confirmed` = seen in code or data · `suspected` = inferred, needs a test · `decision` = not a bug yet, needs a choice

## From the code review

| # | Area | Issue | Status | Test idea |
|---|---|---|---|---|
| 1 | `routes/comments.py` | `parent_id` validated against `Post` instead of `Comment`. A reply to comment 7 fails if no post 7 exists; a reply to a non-existent comment passes validation when a post with that id exists, then hits the FK and returns a 500. | confirmed (code) | Reply to an existing comment whose id ≠ any post id → expect 201. Reply to a non-existent comment id that equals an existing post id → expect 404, not 500. |
| 2 | `routes/comments.py` | No check that the parent comment belongs to the **same post**. The FK only checks that the parent exists somewhere, so a reply on post B can point at a comment on post A. | suspected | Create comment on post A; reply to it via post B → expect 400. |
| 3 | Voting | Is the score updated atomically (`score = score + :delta` in SQL), or read–modify–written in Python? The latter loses votes under concurrency. | suspected | Check the code first; concurrency test in Week 7. |
| 4 | Voting | Changing a vote (+1 → −1) must move the score by 2; removing a vote must undo it. Easy to get wrong. | suspected | Upvote, downvote, unvote → assert score after each step equals `SUM(value)` of the vote rows. |

## From the schema

| # | Area | Issue | Status | Test idea |
|---|---|---|---|---|
| 5 | Deletes | No foreign key has `ON DELETE` behavior (default `NO ACTION`). Hard-deleting a post with comments or votes fails with an IntegrityError unless the ORM deletes children first. | suspected | Delete a post that has comments and votes → expect 200/204, not 500. |
| 6 | Comments | The model was described as having **soft delete**, but `comments` has no `is_deleted` / `deleted_at` column, and `author_id` and `content` are `NOT NULL`. How is soft delete implemented (overwriting `content`)? Is the model ahead of the migrations? | suspected | Delete a comment that has replies → expect the replies to survive and the deleted one to show as "[deleted]". Also run `flask db check` / compare model to DB. |
| 7 | Votes | `value` has no `CHECK (value IN (-1, 1))`. Only the route stops `value = 100`. | suspected | POST a vote with value 5 → expect 400. Consider adding a CHECK constraint. |
| 8 | Communities | `communities.name` is **not unique**, so two communities can share a name. | confirmed (schema) | Create two communities with the same name → expect 409. Add a unique constraint via migration. |
| 9 | Users | `username` / `email` uniqueness is case-sensitive: `Harry` and `harry` can both register. | decision | Decide: normalize to lowercase on register, or a unique index on `lower(email)`. |
| 10 | Timestamps | `timestamp without time zone`: correct only if the app always writes UTC. `datetime.utcnow()` is deprecated in Python 3.12. | decision | Check how `created_at` defaults are set. |

## Performance (Week 7, not bugs yet)

- The global feed (latest 25 posts across all communities) sorts by `created_at`, which has no index on its own, so it does a full sort. Fine at 6 posts; measure at 100k.
- There's no index on `post_votes(post_id)` / `comment_votes(comment_id)`. Deleting a post must scan the vote tables to check the FK.
