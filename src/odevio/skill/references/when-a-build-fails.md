# When a build fails

Two things happen here, in this order: decide **what kind** of failure it is, then, only if it belongs to the
application, fix it in a loop.

Getting the first part wrong is the worst thing this skill can do. The user does not read the patches you
write. Change their code in reaction to an infrastructure problem and you break a working project, with no way
for them to tell.

---

# Part 1 — Classify

**Decide from the error code. Never from words in the log.**

`odevio build detail <key>` prints, on failure:

```
Error message: Flutter build - Error building ipa - Error code 84
```

The number at the end is authoritative, and the status line reads `Failed`.

Codes follow `xy`, where `x` is the step and `y` the kind of failure.

| Code | Meaning | Class | What to do |
|---|---|---|---|
| `y=2`, e.g. `32`, `82` | the host did not respond | infrastructure | retry, **do not touch the code** |
| `y=3`, e.g. `83` | request to the host returned a non-200 | infrastructure | retry, do not touch the code |
| `26` | timed out waiting for the VM | infrastructure | retry |
| `30`, `80` | unexpected error | unknown | retry once, then hand over |
| **`84`** | **build failed** — confirmed on a real Swift compile error | **application** | read the log, fix the code |
| `55`, `56` | version unreadable in `pubspec.yaml` | application | fix the file |
| `95`, `105` | IPA not found | application | consequence of a failed compile, look one step earlier |
| `106`–`109` | keychain, private key, signing | Apple setup | **never touch the application code.** Suspect the Team ID given during setup, then hand over |

An unlisted code is **unknown**, never application. Retry once, then stop and explain.

## Two traps in the log

**The network trap.** Seen on an otherwise healthy build, during the Flutter step:

```
Command exited with code 128: fetch --tags
Standard error: fatal: unable to access 'https://github.com/flutter/flutter.git/': The requested URL returned error: 503
```

Flutter reaches GitHub from inside the VM. Here it failed fast and the build carried on. When GitHub is slow
rather than down, the same call hangs and the build freezes — which is what left two builds sitting for forty
minutes without moving. So a failure during the Flutter step with a network error is **infrastructure**. A
`code 128` alone says nothing; read the line after it. Never conclude "broken repository" and start editing.

**The "archive done" trap.** The log prints this *before* failing:

```
Xcode archive done.                    530.7s
Failed to build iOS app
Swift Compiler Error (Xcode): Cannot assign value of type 'String' to type '(any UNUserNotificationCenterDelegate)?'
ios/Runner/AppDelegate.swift:9:50
```

`Xcode archive done` does **not** mean success. The verdict is the status and the error code, never a line in
the log.

## Reading the log to find the fix

Only once the code says the failure is in the application:

- read the **end** of the log. It also holds a full keychain dump — dozens of lines of hexadecimal
  attributes — which is normal output and means nothing
- the useful part is the compiler error and its `file:line:column`. That path is inside the VM
  (`/Users/odevio/Documents/app/…`); map it by keeping everything after `app/`
- the message is identical to what a local compiler prints, so treat it as an ordinary compile error

## When the user wants the details

Three levels, each offered only if asked.

**Default — one sentence about what you are doing**, not about what broke:

> There's an error in your app's iOS code — I'm fixing it and starting another build.

**On request — the decisive excerpt, never the whole log.** A few lines in a code block so they can be copied,
then an explanation in plain words and what you changed.

**To keep or share it — write the whole log to a file**, do not print it:

```sh
COLUMNS=200 odevio build logs <key> > odevio-artifacts/build-<key>.log
```

Write it **into their project**, in `odevio-artifacts/`, never into a temporary directory they will never find.
Set that folder up as described in `references/delivery.md` — it needs an entry in `.gitignore` and one in
`.odevioignore`, or it travels to the Mac with every later build.

Then tell them the path. The full log runs to hundreds of lines; pasted into a conversation it is unusable, in
a file it is exactly what they need to attach to a message or an issue.

**Do not send them off to search for the error.** If a message is unfamiliar, look it up yourself and come back
with an answer. Avoiding that search is why they are using this.

---

# Part 2 — The fix loop

Only for a failure classified as coming from the application.

## What it costs

One attempt costs about **fifteen minutes** of build time, plus up to eight queued. This is a loop of two or
three attempts, not twenty, and every attempt must be a considered fix rather than a guess — the cheap fast
retry that makes loops work elsewhere does not exist here.

## Isolation: one worktree per attempt

```sh
git worktree add ../<project>-attempt-1 -b odevio-attempt-1
```

The user's working tree stays untouched until a fix is proven; a failed attempt is thrown away with its
worktree, and each attempt stays readable as its own branch. Isolation here buys cleanliness, not parallelism —
builds are serialised anyway.

### Two traps that break the build if ignored

**In a worktree, `.git` is a file, not a directory.** The upload excludes `.git` from directory names only; file
names go through a separate list that does not include it. So the `.git` file gets uploaded, defeats the
`if [ -d .git ]` cleanup inside the VM, then makes `git init` fail on a gitfile pointing nowhere. The build dies
at the source-import step, with an error that looks like infrastructure rather than anything you did.

Before the first build from a worktree, create a `.odevioignore` there containing:

```
.git
odevio-artifacts/
```

`.git` without a trailing slash, because in a worktree it is a **file**. `odevio-artifacts/` with one, because
that one is a directory. The slash is what tells the two apart, and getting it wrong means the entry is
silently ignored.

**`.odevio` and `.odevioignore` are read from the current directory**, not from the project directory given on
the command line. So `cd` into the worktree and launch from there. Running from the main project while pointing
at a worktree silently applies the wrong configuration.

## The loop

For each attempt, at most three:

1. locate the compiler error and its `file:line:column` at the end of the log
2. map the path: everything after `app/`
3. create the worktree, add `.odevioignore` with `.git`
4. make **one** considered fix, and explain it in a sentence before building
5. run the local checks from `SKILL.md` — free, and they catch a bad fix in seconds
6. `cd` into the worktree and launch **with the same build type as the original attempt**, and an
   **incremented** `--build-number`. Do not downgrade to a verification build: a failed `publication` does not
   count against a free account's publication rate — `FAIL` is excluded from the statuses the server
   counts — so retrying the real thing costs nothing extra and saves a fifteen-minute round trip
7. follow it as described in `SKILL.md`
8. on success, stop the loop. On failure, classify again before deciding anything

## When to stop

- **build succeeds** — apply the fix to their branch, remove the worktrees, say what changed
- **two identical failures in a row** — stop. The same error twice means the diagnosis is wrong, and a third
  attempt will not find it
- **three attempts** — stop, whatever happened
- **the class changes to infrastructure, Apple or unknown** — leave the loop and follow Part 1
- **the local checks fail on your own fix** — that fix was wrong; correct it without spending a build

On stopping without success, give a short account: what the error was, what you tried, why each attempt failed,
and what you would look at next. They have waited half an hour; they deserve better than "it did not work".

## Cleaning up

```sh
git worktree remove ../<project>-attempt-1
git branch -D odevio-attempt-1
```

Remove every worktree you created, including after an interruption — `git worktree list` shows what is left
behind. Otherwise the next run meets stale branches and the user finds directories they did not create.

## Never

- never modify the user's working tree before a fix has passed a build
- never make several unrelated changes in one attempt: if it fails, you learn nothing about which one was wrong
- never continue past the stopping rules because the next attempt "should" work — that is fifteen minutes of
  someone else's build capacity each time
