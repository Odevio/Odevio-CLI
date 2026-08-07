# The Odevio CLI contract

Everything in this file was observed by running the CLI, not inferred. Follow it exactly — each rule
exists because assuming otherwise produced a wrong result.

## Authentication is the one thing that can still block

The CLI authenticates with a JWT token cached in its config file. It refreshes the token by itself while
it is refreshable. **When there is no usable token, the CLI asks for an e-mail and a password — and that
prompt lives in the shared authorization code, so any command can trigger it, not just `signin`.**

Before running anything else, confirm a usable session:

```sh
COLUMNS=200 odevio profile
```

If that returns the account details, a valid token is cached and every later command runs unattended. If
it asks for credentials, stop immediately and tell the user to run `odevio signin` themselves. Never type
a password on their behalf, and never pass one on a command line — it lands in shell history and in the
process list.

If `ODEVIO_API_KEY` support has been added to the CLI, prefer it: it removes the config-file dependency
and makes a mid-loop prompt impossible. Until then, treat the cached token as a prerequisite verified in
preflight, not as something that can be fixed mid-run.

## Why commands ask for approval, and what to do about it

The `allowed-tools` list in `SKILL.md` covers **only the turn that invokes the skill**. The grant clears the
moment the user sends their next message, so every reply — answering a question, confirming a build, saying
"go on" — takes it away again. A conversation this long therefore spends almost all of its time without it.
Adding entries to that list cannot fix this; the field is not the mechanism.

The mechanism is `permissions.allow` in the user's `settings.json`, which `odevio skill install` writes.
If the user is being asked to approve every command, they are missing those rules:

> Your assistant is asking permission before everything it does, because Odevio's setup never got as far
> as granting it. It is one command in your terminal and it stops for good — say the word and I will give
> you it.

That is one of the two things they have to type themselves, so give it once they say yes and not before.

Three commands ask every time by design and always should — starting a build, sending screenshots to Apple,
and opening a submission. Never suggest a way around those. When one is coming, say so first, in the same
message as whatever else you are telling them, so the prompt is expected rather than alarming.

## What this skill assumes about the machine

Almost nothing. Everything it runs is `odevio`, `flutter`, `dart` and read-only `git` — all of which work the
same on macOS, Linux and Windows. No `sed`, no `awk`, no Apple-only tooling: the Mac is Odevio's, not the
user's, which is the whole point of the product.

The one shell-specific habit is the `COLUMNS=200 …` prefix below. It is POSIX syntax and a shell that rejects
it will say so on the first command. **It is an optimisation, not a requirement** — drop it and pass the
argument the command offers, or accept wrapped output and parse more carefully. Both forms are granted, so
neither asks for approval.

Never name a shell — `zsh`, `bash`, `cmd` — in a command you build. Use whatever the host already runs.

## Always widen the output before parsing

```sh
COLUMNS=200 odevio build ls
```

The CLI formats output for an 80-column terminal. Long values are wrapped onto continuation lines, which
silently breaks any parsing of a value near the wrap point. With `COLUMNS=200` the same command emits
single-line rows. Put it in front of every invocation.

Write it as a prefix, never as `export COLUMNS=200` on a line of its own followed by the command. Two
commands joined together are no longer recognised as the pre-approved ones this skill was granted, so the
user is interrupted to approve a shell line they cannot judge.

## `build ls` cannot be filtered

It takes `--all` and nothing else. There is no way to ask for the builds of one app: no `--app-key`, no
`--app`, no positional argument. Passing one fails outright with `No such option`.

List them and read the App column yourself. The same goes for anything else that looks like it should
accept a filter — check `--help` before believing in an option, because a flag that sounds obvious is
exactly the kind this CLI tends not to have.

Never parse a value shown with a trailing ellipsis — `build ls` truncates dates as
`2026-08-03T09:57:36.34…`. Read those from `build detail` instead.

## Never trust the exit code

Observed, on the same command family:

| Situation | Exit code |
|---|---|
| Success | 0 |
| Build key does not exist | **0**, with `This build does not exist or you cannot access it.` |
| Required argument missing, no TTY | 1, with a raw Python traceback (`OSError: [Errno 22]`) |

Decide on the **content** of the output. Treat a non-zero exit as "something went wrong", never a zero
exit as "it worked".

## Always pass every argument

Omitting an argument makes the CLI open an interactive menu. Two consequences:

- With a real terminal, it waits for a human — the loop stalls.
- Without one, it prints the items it would have offered and exits 1. It does **not** silently pick
  something: no build is ever started on the wrong app.

The listing it prints on that failure is usable — read the key out of it and run the command again rather
than showing the user an error.

## Reading the project's history

`git diff`, `git log`, `git status` and `git show` are granted; nothing else about git is. Recent history is
the best clue for why a build that used to work has stopped, so look before asking.

**Run them from the project directory, never with `-C <path>`.** Only those four forms were granted, and
`git -C … diff` does not begin with `git diff`, so it is stopped for approval instead. Granting `git -C`
would have allowed every git subcommand including the destructive ones, which is why it was not.

This tells you what changed, not whether the user meant it. A commit after the last build is a reason to ask
whether they want a fresh one — never a reason to decide for them.

## Never put a line break inside a command

A newline ends a command, so a multi-line value is read as a second command that was never allowed, and the
run stops for approval showing the user shell quoting instead of their own words. This bites on the App Store
description, which has paragraphs: write it to a file and pass `--description-file`. Same reflex for any long
value — a file beats quoting.

One nuance from the implementation: when only **one** item exists — one Apple account, one app — the CLI
selects it without asking. A first-time user therefore never sees a menu. Pass the arguments anyway, so
behaviour does not depend on how many items the account happens to hold.

## Command names — verify, never guess

The Python function names do not match the command names. Check with `odevio <group> --help` before
writing any command into a skill file.

| Correct | Wrong, and why it is tempting |
|---|---|
| `odevio profile`, `signin`, `signup`, `signout`, `apikey` | there is **no** `user` group |
| `odevio apple ls` | the function is `developer_account_ls`, but the command is `ls` |

Groups: `build`, `team`, `app`, `apple`. Everything else is top-level.

## Parsing a build key

```
Build #7 has been registered. It has key "K7B3Q" and will be started as soon as possible.
```

Take the value between the double quotes.

Pass `--no-progress` and `--no-flutter-warning` **as command-line options**. Both are dead keys in `.odevio`:
they are declared `is_flag=True` without `default=None`, so Click always supplies `False` and the `.odevio`
reader's `if ... is None` test can never apply. Writing them into the file looks like it works and does nothing.

## The `.odevio` file

Read from the **current directory**, not from the project directory given on the command line. One `KEY=VALUE`
per line, `#` starts a comment, unknown keys warn. Useful keys: `app-key`, `build-type`, `flutter`,
`minimal-ios-version`, `app-version`, `build-number`, `mode`, `target`, `flavor`, `post-build-command`.

A value in the file applies only when the option was not given on the command line.

## Logs

```sh
COLUMNS=200 odevio build logs <key>
```

Available **during** the build: steps that have finished are already visible, so logs are usable for
progress, not only post-mortem. A step's own output only appears once that step ends.

Logs contain non-fatal noise. A real example from a healthy build:

```
Failed to delete directory at: /Volumes/My Shared Files/flutter/.pub-preload-cache
```

Never classify a failure by searching for words like `failed` or `error` in the logs. Classify on the
error code, and use the logs only to decide *what* to fix once the failure is known to be a code failure.
