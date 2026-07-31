# technology-skills-checks

check50-style checks for the "Technology Skills" course, used by both:

- Students, running for free/local/unlimited feedback via `check50 --local --offline`
  (see the `check` command inside each lab's Codespace).
- The official Classroom50 autograder, which runs the exact same checks server-side
  to produce the graded score.

This repo intentionally contains **only check code** — no solutions, no student data,
no scores. It's public and safe to be public, mirroring how CS50's own checks live in
[cs50/problems](https://github.com/cs50/problems).

## Layout

One folder per assignment slug, e.g. `hello/__init__.py`.

## Editing

Edit anytime — changes take effect immediately for local `check` runs, and on the
next submission for official grading. No student repo needs to change.
