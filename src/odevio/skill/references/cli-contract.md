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

## Always widen the output before parsing

```sh
export COLUMNS=200
```

The CLI formats output for an 80-column terminal. Long values are wrapped onto continuation lines, which
silently breaks any parsing of a value near the wrap point. With `COLUMNS=200` the same command emits
single-line rows. Set it for every invocation.

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
- Without one, it dies on an unhandled traceback. It does **not** silently pick something: no build is
  ever started on the wrong app. That failure is safe, just ugly.

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
