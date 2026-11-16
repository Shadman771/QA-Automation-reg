# Git Workflow

Copy-paste command reference for day-to-day Git usage on this project.
This is documentation only - it doesn't change how `run_tests.py` or any
automation behaves.

## Check your current state

```bash
git status                  # what's modified/staged/untracked right now
git branch                  # which branch you're on
git remote -v               # which remotes exist and where they point
```

This repo can have more than one remote configured (e.g. `origin`,
`upstream`, `newrepo` pointing at different GitHub accounts/repos). Run
`git remote -v` before pushing if you're ever unsure which one a plain
`git push` would target - a push can be rejected with "permission denied"
simply because your cached GitHub credential belongs to a different
account than the one a given remote's URL points at. That's a credentials
problem, not a code problem; switch accounts or push to the remote whose
account you're actually signed in as, rather than force-pushing or trying
every remote until one accepts it.

## Pulling the latest changes

```bash
git pull origin version-3        # merge the remote branch into your local one
git pull --rebase origin version-3   # same, but replays your local commits on top
                                       # instead of creating a merge commit
```

If you have uncommitted changes that `git pull` would overwrite, commit or
stash them first (see below) - never `git checkout .` / `git reset --hard`
to "make room" without checking what you'd lose.

## Branching

```bash
git checkout -b feature/my-change      # create and switch to a new branch
git checkout version-3                 # switch back to an existing branch
git branch -d feature/my-change        # delete a local branch once merged
```

## Staging and committing

```bash
git status                       # see what changed before staging anything
git add path/to/file.py          # stage specific files - prefer this over `git add -A`
                                  # so you don't accidentally stage an unrelated
                                  # change (e.g. a credentials file, or someone else's
                                  # in-progress edit to a test_data/*.xlsx you didn't touch)
git diff --staged                # review exactly what you're about to commit
git commit -m "Short, clear summary of the change"
```

Before committing, always re-run `git status` after a broad `git add` and
scan the file list - if anything there looks like it might contain a
credential or an unrelated pre-existing change you didn't make, unstage it
(`git restore --staged <file>`) and double-check before committing.

## Pushing

```bash
git push origin version-3              # push your branch to its remote
git push -u origin feature/my-change   # first push of a new branch - sets up tracking
```

**Never use `git push --force` / `git push --force-with-lease` on a shared
branch** (`main`, `version-3`, or any branch someone else might also be
working on) unless you specifically mean to overwrite its remote history
and have confirmed with everyone else using it. A rejected push almost
always means the remote has commits you don't have locally yet - `git pull`
(or `git pull --rebase`) first, resolve any conflicts, then push normally.

## Pull requests

```bash
# Using GitHub CLI (gh) - install from https://cli.github.com/
gh pr create --title "Short title" --body "What changed and why"
gh pr view --web              # open the PR in your browser
gh pr checks                  # check CI status on the PR
```

Without `gh`, open the compare URL GitHub prints after a `git push` of a
new branch, or go to the repo's "Pull requests" tab on GitHub directly.

## Merging

```bash
git checkout main
git pull origin main
git merge version-3           # merge version-3 into main locally
git push origin main
```

Prefer merging through the GitHub PR UI (or `gh pr merge`) for anything
reviewed by someone else - it keeps a record of the review and the exact
commits that went in, rather than a silent local merge.

## Handling conflicts

```bash
git pull origin version-3     # (or git merge/rebase) - this is what surfaces conflicts
git status                    # lists every file with a conflict, marked "both modified"
# open each conflicted file, resolve the <<<<<<< / ======= / >>>>>>> markers by hand
git add path/to/resolved_file.py
git commit                    # completes a merge; `git rebase --continue` completes a rebase
```

If a conflict is in an auto-generated file this project regenerates every
run (`test_data/**/*.xlsx`, `reports/*.html`, `reports/*.json`, anything
under `screenshots/` or `logs/`), the simplest fix is usually to take
either side and let the next `python run_tests.py` regenerate it correctly
- these files are never meant to be hand-merged.

## Keeping local and remote in sync

```bash
git fetch origin                                  # see what's on the remote without merging yet
git log origin/version-3..version-3 --oneline     # commits you have that the remote doesn't
git log version-3..origin/version-3 --oneline     # commits the remote has that you don't
git status -b --short                             # quick "ahead N / behind N" summary
```

Run the first two before any push you're unsure about, especially after a
long gap or after someone else may have pushed - don't assume "ahead by
N commits" always means N commits of *your own, reviewed* work; it can
include auto-generated commits (e.g. this project's own
`chore: publish latest QA report to GitHub Pages` commits made by
`utils/publish.py` after each run) mixed in with real feature work. If
you're about to publish a large backlog of commits to a remote for the
first time, skim `git log --oneline` over that range first so you know
what you're actually publishing.
