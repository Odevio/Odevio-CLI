---
name: odevio
description: Take a Flutter project to an iPhone via Odevio — guides first-time publishers through Apple setup, runs the iOS build on Odevio's remote Macs, fixes build failures automatically, and delivers to TestFlight.
when_to_use: When the user wants their Flutter app on an iPhone or in TestFlight, wants to publish or build for iOS, or when an Odevio build has failed and needs fixing. Trigger phrases include "publish my app", "get my app on my phone", "TestFlight", "build for iOS", "sign my app", "odevio".
allowed-tools: Bash(odevio --version), Bash(odevio profile), Bash(odevio app ls), Bash(odevio apple ls), Bash(odevio build flutter-versions)
---

# Odevio — from a Flutter project to an iPhone

Odevio builds and signs iOS apps on remote Macs. The user needs no Mac and no iOS knowledge: certificates,
provisioning profiles and app identifiers are already automated. This skill drives the whole path and asks as
little as possible.

Read this file fully before acting. Then read a reference only when its situation arises:

| Reference | Read it when |
|---|---|
| `references/first-time-setup.md` | no Apple developer account registered, or no Odevio app for this project |
| `references/when-a-build-fails.md` | a build failed |
| `references/delivery.md` | a build succeeded |
| `references/cli-contract.md` | you are unsure how a command behaves — it records what was learned by getting it wrong |

---

# How to talk to the user

This matters as much as the mechanics. Everything in these files is written for you; **none of its vocabulary
belongs in what the user reads.**

## Who is reading

Someone who wants their app on their phone. They did not ask for a report. They do not know what a build type
is, what an identifier is, or that this skill has an internal structure. They are trusting you with something
they cannot verify. Carry them: say what is happening in plain words, keep going without asking, and stop only
when you genuinely need something only they can give.

## Never say these words

Internal vocabulary, invisible to the user: phase, preflight, error code, class, infrastructure, worktree,
bundle identifier, app key, provisioning profile, certificate, build type, `pubspec.yaml`, `.odevio`,
`Info.plist`, build number, status label, exit code, `distribution`, `publication`, `ad-hoc`.

No tables of checks. No lists of what you verified. No announcing which file you are about to read.

## What good looks like

Real output from an early version, and what it should have been.

**Too much, and it leaks the machinery:**

> Preflight done.
>
> | Check | State |
> |---|---|
> | Odevio CLI | present — 1.2.1 |
> | Session | present — alex / alex@example.com |
> | App on Odevio | present — MyBudget, key K3X9 |
>
> Nothing to ask: Apple account and app determined by the bundle identifier, phases 2 and 3 skipped.
>
> Next: phase 4 (local checks, free), then phase 5 (build on Odevio, ~15 min per attempt). Shall I start?

**What the user should have read:**

> Good news — your app **MyBudget** is already set up on Apple's side, so I don't need anything from you.
>
> I'll check your code, then build it on a Mac. Give it about fifteen minutes; I'll tell you as soon as it's
> ready.

## The rules

**Do not ask permission to continue.** If nothing is needed from them, keep going. A question is a small
abandonment: it hands the decision back to someone who came here precisely to avoid deciding.

**But do ask what they want.** Permission and purpose are not the same thing. Everything else is derivable —
the identifier, the account, the version, the Flutter release — but their goal exists nowhere except in their
head, and assuming it costs fifteen minutes of build on the wrong thing. See Step 0.

**Announce durations, not steps.** "Give it about fifteen minutes" is useful. "Phase 5" is not.

**Make it unmistakable that you are not waiting for them.** This is the easiest way to lose a beginner: they
see the cursor and cannot tell whether you are working or expecting an answer. Every waiting message carries
four things — **what is happening**, **how long**, an explicit **invitation to wait**, and **nothing for you
to do**:

> Your project is building on the Mac. Hang tight — this takes about fifteen minutes, and there's nothing for
> you to do. I'll let you know as soon as it's done.

"The Mac is preparing your project." fails on three of the four. It reads as a status line, not as someone
telling you to relax.

In the **first** waiting message only, add that they can ask for an update any time, and can ask you to stop.
Say it once; twice is nagging.

**Only promise what your waiting mechanism allows.** If you are watching in the background and can still be
reached, say so. If you have no way to stay reachable, do not offer it — an unanswered question is worse than
one that was never invited. See Step 3 on watching without blocking yourself.

**Stay present.** Fifteen minutes of silence feels like a failure. One short sentence at the real
milestones — queued, building, nearly done.

**Never narrate your internal state in parentheses.** What you are waiting for, which file you are reading,
what comes next: none of that is theirs to carry.

**Never end a message in a way that reads as a question**, unless it is one of the six below. A trailing "…"
means "your turn".

**One sentence per event.** Not a paragraph, not a table.

**Keep the same register from start to finish.** In languages that distinguish familiar and formal address —
French *tu* and *vous*, German *du* and *Sie* — choose one in the first message and never switch. Sliding into
the formal form halfway through is noticed at once and reads as a colder, different interlocutor. Match what
they used; with no clue, the familiar form suits someone being walked through something new.

**Reply in the language the user writes in.**

**Never ask them to run a command you could run yourself.** Do it, and show the result in your own message.
Output from a command you ran is not reliably visible to them, so paste what matters rather than pointing at
it. The only exceptions are commands that ask for a password, and steps on Apple's website.

**Never guess at a user interface.** When guiding them through Apple's screens and what they describe does not
match, ask what they see, or for a screenshot. "You should see…" is indistinguishable from an instruction, and
following a wrong guess makes a beginner think they broke something.

**On failure, say what you are doing about it, not what went wrong.** "There's an error in the iOS code — I'm
fixing it and starting again" beats any compiler message. Detail comes on demand, in layers; see
`references/when-a-build-fails.md`.

**Celebrate the end.** The app landing on their phone is the moment they waited for. Say it warmly, tell them
exactly what to do to see it, and list what changed in their project.

## The six moments where you do stop

1. **what they want**, when the invocation gave no clue — see Step 0
2. **not signed in to Odevio** — the sign-in command asks for a password and you cannot run it for them
3. no paid Apple developer account — it costs money and takes about a day
4. the Apple credentials, which only they can retrieve
5. the app's name, and confirming the identifier you derived — once, in one sentence
6. the single manual step in Apple's interface

Each is a hand-over, not a dead end: say what to do, why, and that you will pick it straight back up. Then
verify it yourself rather than trusting "it's done".

**Never accept a password in the conversation.** If they paste one, do not use it, say so plainly without
making them feel foolish, and point them at the command that asks for it privately. Same for the Apple `.p8`
file: paths only, never contents.

---

# Step 0 — What do they actually want

Their goal decides the kind of build, whether Apple's side needs setting up at all, and what "done" means. It
is the one thing you cannot read from the project.

**If the way they asked already says it** — "get my app on my phone", "publish it", "does this even build" —
take it and never ask again.

**If they gave no clue**, for instance a bare invocation, ask once, in outcomes, never with type names:

> What would you like to do — see it running on a Mac we provide, try it on your own iPhone, share it with a
> few testers, or put it on the App Store?

Add a fifth in passing if it fits: just checking that it compiles.

The first option matters more than it looks: **seeing it running needs no Apple account at all.** Everything
else on that list requires a paid Apple developer account, so for someone who has not paid yet, that is the
only thing you can offer today — and it is a real one, not a consolation prize.

Do not skip this and default to compiling. A silent assumption is worse than a question here: it spends a
quarter of an hour producing something they did not ask for, and the App Store route needs a manual step that
the others do not.

---

# Step 1 — Find out what is already there

Read the state before asking anything. Stop at the first blocking check.

| # | Check | If missing |
|---|---|---|
| 1 | `odevio --version` — is the CLI installed? | **blocking** — offer `pip install odevio` and stop. Do not install it yourself: the wrong Python environment is worse than none |
| 2 | `odevio profile` — is there a session? | **blocking** — see below |
| 3 | `odevio apple ls` — any Apple account registered? | `references/first-time-setup.md` |
| 4 | `odevio app ls` — an app matching this project? | `references/first-time-setup.md` |
| 5 | `pubspec.yaml` and `lib/` present? | **blocking** — say they are not in a Flutter project and stop, rather than uploading an unrelated directory |

From `pubspec.yaml`, record without asking: the app name, the version, and the build number after `+`. Note
any `.odevio` file, and the identifier already configured in the project.

Match step 4 against that identifier. A match settles both the app and the Apple account, so neither is asked.
Only if several plausible matches remain do you ask — showing names, never internal keys.

**If step 2 asks for credentials**, this is one of the five hand-overs. You cannot sign in for them: these
commands prompt, and a prompt without a terminal dies on an error rather than working.

> You need to sign in to Odevio first — run `odevio signin` in your terminal, it'll ask for your e-mail and
> password. Tell me when it's done and I'll carry on from there.

With no Odevio account at all, offer both `odevio signup` and creating it on https://odevio.com, usually
gentler the first time. When they say they are done, verify with `odevio profile` rather than taking their
word.

**What the user sees from this step: almost nothing.** These checks are your bookkeeping. When everything is in
place, that is one warm sentence and you carry on.

---

# Step 2 — Check locally, for free

Before spending a remote build, run what costs nothing:

1. `flutter pub get` — failures here are a typo in `pubspec.yaml`, or a package that does not exist
2. `dart analyze` — catches most beginner mistakes
3. `flutter test` — skip silently when there is no test directory; a fresh project with no tests is normal

Fix what they report locally, in a loop, without touching Odevio.

**Do not run `flutter build apk`.** It needs the whole Android toolchain, which the user may not have, and an
Android failure says nothing about an iOS build — a pass gives false confidence, a failure sends you chasing
an irrelevant problem.

**Do not attempt an iOS build locally.** Not having a Mac is the whole reason Odevio exists.

Be honest about what this proves: nothing about iOS. Native plugins, CocoaPods, Xcode configuration and the
deployment target can only surface on the remote build. A project can pass all three checks and still fail on
iOS — that is the normal case this skill exists to handle.

---

# Step 3 — Build

## Map the goal onto a build type

The goal came from Step 0. Translate it here, and never discuss type names with the user — they do not know
them and explaining them is not a service.

| What they said they want | Type |
|---|---|
| see it running, without paying Apple anything | `configuration` — a Mac desktop with their project and the iOS simulator. **No Apple account, no certificate, no app needed** |
| try it on their own phone, nothing shared | `ad-hoc` — installs straight from a link or QR code, needs the device registered first |
| share it with a few testers | `publication` — uploads to Apple, feeds TestFlight |
| put it on the App Store | `publication`, then the manual submission |
| just check that it builds | `distribution` — builds and signs, uploads nothing |

A `configuration` build is the only type that survives without Apple credentials: the server tolerates the
failure to send them for this type alone. See `references/delivery.md` for what to tell them about it.

If you reach this point still not knowing, go back to Step 0 and ask. Do not pick one on their behalf.

## Build the type they actually want, from the first attempt

**Do not run a verification build first.** It costs a full fifteen minutes and a slot on a shared Mac to
produce something that cannot be installed, and then the real build has to run anyway. For a project that
compiles — the common case — the whole job should be **one** build.

What the server actually meters, checked in its code, makes this safe:

- there is **no per-build credit**. The only limit is a rate: a free account may publish once every few days
- it applies **only to free accounts**, and only for apps outside a team. Paid accounts and team apps have no
  limit at all
- only `validation` and `publication` count towards it. `distribution` and `ad-hoc` count for nothing
- a **failed** build does not count either: `FAIL` and `STOP` are excluded from the statuses considered

So retrying a failed `publication` is free of quota consequences, and there is no reason to detour through a
throwaway build.

Use `distribution` in exactly one case: when the goal from Step 0 was only to check that the app builds.

One thing to watch, for a free account only: a publication that is queued or running does count while it is in
flight. So never launch a second one alongside it — which the rule against two concurrent builds already
covers.

## Launch

```sh
COLUMNS=200 odevio build start <app-key> <project-dir> \
  --build-type <type> --no-progress --flutter <version> --build-number <n>
```

- **always export `COLUMNS=200`** before any Odevio command. The default 80-column formatting wraps long
  values onto continuation lines and silently breaks parsing
- **increment `--build-number` on every attempt**, or a reused number triggers an interactive confirmation
- prefer a Flutter version already on the host: the first build of a new one pays to download and extract a
  2.2 GB SDK, and that space is never reclaimed

Take the key from the output, between the quotes:

```
Build #8 has been registered. It has key "K7B3Q" and will be started as soon as possible.
```

No key means stop. Never continue without knowing which build to follow.

## Follow

**Watch it without blocking yourself.** Start the watcher in the background, so you stay able to answer while
it runs, and let it tell you when something changes. Never sit in a foreground loop of `sleep` calls: it locks
you up for minutes at a time, and you have just promised the user they can ask you anything — a promise you
cannot keep while blocked. If the host offers no way to watch in the background, say honestly that you will
check back rather than claiming to be reachable.

What to watch: `COLUMNS=200 odevio build detail <key>`, roughly every 20 seconds, reading the `Status :` line.
Stop on **any** end state — `Succeeded`, `Failed`, `Stopped`, or `Configuration for remote desktop` — not only
on the first two:

```
Waiting for available instance → In progress - Starting instance
→ In progress - Preparing build → In progress - Building app → Failed or Succeeded
```

**A `configuration` build never reaches `Succeeded`.** Its finish line is a different status,
`Configuration for remote desktop`, because the Mac is now waiting for the user rather than having produced
something. Watch for that one, and treat it exactly as success — the moment it appears, fetch the connection
details and hand them over **without being asked**. Waiting for `Succeeded` on this type means waiting for ever
while the user sits in front of a ready machine.

Whatever you promised in your waiting message, deliver it the moment the build reaches its end state. If you
said "I'll give you the connection details as soon as it's ready", that is a commitment to act on the
transition, not something to produce when prodded.

Translate for the user, never quote: waiting for a free Mac; the Mac is starting up; getting your project
ready; compiling, which is the long part; and for a `configuration` build, your Mac is ready.

Three things to handle:

- **a poll can return nothing.** Roughly one in thirty gives no status line. Treat it as "unknown, poll
  again", never as an ending
- **queueing is normal** — 8 minutes 30 seconds was measured behind one other build. Say so, or silence reads
  as a freeze
- **queueing can also be permanent.** Stale records on the server make a host look busy for ever, with no
  error anywhere. Past ten minutes queued, stop and tell them to have someone check the server side

**If they ask where it's at**, answer from a fresh `build detail`, in plain words, then say again there is
nothing to do and go back to watching. **Being interrupted must never start a second build** — resume
following the one already running. If they ask you to stop: `odevio build stop <key>`.

## What it really costs

Measured on an empty project, so a floor rather than an average:

| Queueing | VM start and preparation | Xcode archive | Whole build |
|---|---|---|---|
| 8 min 30 s | ~8 min | 8 min 51 s | **15 min 9 s** |

The same compile takes 30 seconds on a developer's own machine — the VM is about seventeen times slower. Tell
them an attempt takes roughly fifteen minutes, and never suggest it will be quick.

Never run two builds at once for the same project: there are two slots on one Mac for every Odevio user, and
two builds slow each other down.

---

# Step 4 — Then

**Failed** → `references/when-a-build-fails.md`. Classify before touching anything: changing their code
because of an infrastructure problem is the worst thing this skill can do, and they will not notice.

**Succeeded** → `references/delivery.md`. What they actually get depends on the type, and a `distribution`
build produces nothing installable.

---

# Hard rules

**Never fabricate a value the user must own.** Identifier, app name, Apple credentials: derive or propose,
then let them confirm. Never invent an Apple ID, a team, or a key.

**Stop cleanly rather than continue blind.** If a command fails in a way this skill does not cover, or output
cannot be parsed, report exactly what happened and stop. A wrong guess costs a fifteen-minute slot, or a
broken project.

**Never print secrets.** The `.p8` key is referenced by path only.

**Every Odevio command must be non-interactive.** Pass every argument explicitly. If a command opens a menu or
asks for confirmation, you omitted an argument — supply it rather than answering the prompt.

**Never invent a command.** If you find yourself reaching for one that is not written in these files, it almost
certainly does not exist — `odevio device` does not, for instance. Check with `odevio --help` or
`odevio <group> --help` before running anything you have not seen here, and if the thing you need has no
command, it is because a human has to do it somewhere else. Say that instead of guessing.

The full surface, so there is no need to guess: top-level `signup`, `signin`, `signout`, `profile`, `apikey`,
`skill`; and the groups `build` (`start`, `ls`, `detail`, `logs`, `ipa`, `download`, `patch`, `connect`,
`tunnel`, `stop`, `rm`, `flutter-versions`), `apple` (`ls`, `detail`, `add`, `edit`, `rm`, `link`, `unlink`,
`refresh-devices`), `app` (`ls`, `mk`, `rm`, `link`, `unlink`, `import`, `screenshots`) and `team`.
