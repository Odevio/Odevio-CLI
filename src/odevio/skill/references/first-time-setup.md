# First-time setup

Read this when there is no Apple developer account registered on Odevio, or no Odevio app for this project.
Everything here happens once, then never again.

This is where a beginner is most likely to give up, so be slow and precise. Several of the moments where you
stop and hand control back to the user live here — `voice.md` holds the canonical list.

---

# Part 1 — The Apple account

Needed: a paid Apple Developer Program membership, and an App Store Connect API key letting Odevio act on
their behalf. Odevio has illustrated guides for both — link them rather than retyping steps, because Apple's
interface changes and screenshots help more than prose.

## Question 1 — do they have a paid Apple developer account?

Ask plainly. If they do, go to the key.

If not, this is a **stopping point**, said kindly and clearly:

- the Apple Developer Program costs **99 € per year**. There is no free path to a device or to TestFlight
- Apple reviews the enrolment, so access typically arrives about **24 hours** later
- the guide: https://odevio-cli.readthedocs.io/en/latest/apple/index.html

Then say exactly how to resume: come back and run `/odevio` again once Apple's welcome e-mail arrives.

**But do not leave them with nothing.** One thing works without any Apple account: a `configuration` build,
which gives them a Mac desktop with their project and the iOS simulator, so they can watch their own app
running today. Offer it — see `references/delivery.md`. It is the difference between someone who comes back and
someone who does not.

Beyond that, do not start any other kind of build "in the meantime", and do not keep asking about the account.

## Question 2 — the credentials

**First, the API may not be switched on for their account at all.** Opening *Integrations* can show, instead
of a list of keys, a message that permission is required and that **only the Account Holder can request
access**. Nobody else can lift this — not an Admin, not a Developer, not the person you are talking to unless
they happen to hold the account. It is the one prerequisite that no amount of clicking gets around.

So ask early, before walking anyone through screens: are they the Account Holder on this Apple account? If
not, say plainly that the Account Holder has to turn the API on first, and stop there rather than narrating
a page they cannot use. This is the common case for an agency handling a client's account — the client holds
it, so the request goes to them.

Once the API is on, four values. Three come from App Store Connect — start at **Users and Access**, look for
**Integrations**, and inside it the **App Store Connect API** keys — and the fourth from the developer portal.

| What | What it looks like | Where |
|---|---|---|
| Issuer ID | one identifier for the whole account, above the list of keys | App Store Connect |
| Key ID | on the row of the key just created | App Store Connect |
| Private key, a `.p8` file | offered for download when the key is created | App Store Connect |
| **Team ID** | **ten characters, letters and digits, like `A1B2C3D4E5`** | https://developer.apple.com/account, under *Membership details* — also top right of the portal |

The guide, with screenshots:
https://odevio-cli.readthedocs.io/en/latest/apple/index.html

**The Team ID is not an e-mail address.** The CLI option is called `--apple-id` and its help says "ID of your
developer account on Apple", which reads like an Apple ID. It is not: the value is stored as the Team ID and
shown as *Team ID* by `odevio apple ls`. Asking for their e-mail wastes a round trip and looks incompetent.

**Apple renames and reorganises these screens regularly.** What used to be a *Keys* tab now sits under
*Integrations*, possibly split between team and individual keys. Describe **what to look for**, never a fixed
sequence of clicks, and never insist a label exists. If what they see does not match, ask what is on their
screen, or for a screenshot, and work from that — the guide's screenshots may themselves be out of date.

Three warnings worth saying out loud, each costing real time if missed:

- **the `.p8` file downloads only once.** Tell them to keep it somewhere safe before continuing
- a **Developer** role on the key is enough
- Odevio stores the private key and **cannot give it back**. It must not be their only copy

## Register it

```sh
COLUMNS=200 odevio apple add \
  --apple-id <team id> \
  --name "<friendly name>" \
  --key-id <key id> \
  --issuer-id <issuer id> \
  --private-key <path to the .p8 file>
```

All of these prompt if omitted, so pass them all. `--private-key` must point at an existing file. `--team` is
optional and only matters when the Odevio account belongs to several teams.

**Check the Team ID before sending.** Odevio cannot verify it, and a wrong value makes builds fail much later,
with an error that does not point back here. Confirm it is ten alphanumeric characters, read it back to them,
and if a build later fails on signing, question this value first.

If Apple rejects the key, show **Apple's own message**. The usual causes are a `.p8` that does not match the
Key ID, an Issuer ID from the wrong account, or a revoked key. Say which you suspect and let them check.

Never copy the `.p8` into the project, never print its contents, and never continue if `odevio apple ls` still
shows no account — whatever the command printed, the registration did not take.

## Adding another Apple account

Read this when someone already has an Apple account here and wants a second one. It is an ordinary thing to
want — a freelancer taking on a client, an agency publishing for several of them, someone keeping their own
apps apart from a company's — and it is supported: `apple add` again, nothing to undo first, and
`odevio apple ls` lists them all. An app then belongs to exactly one of those accounts.

### Check they are allowed, before running anything

Whether a second account is permitted is already on screen: `odevio profile`, which you ran in Step 1, prints
**Account type** and the teams they belong to. The rule:

- **Business** — no limit. Add as many as they like.
- **Free or Hobbyist** — a second account is refused, *unless* it is attached to a team with `--team`. An
  account that already sits in a team does not count towards the limit, so this is a real way through and not
  a workaround.

If they are not allowed, say so before the command fails, and put both ways forward in front of them: attach
the new account to one of their teams — `profile` has just listed them — or move to a paid plan. Do not run
`apple add` to find out; a refusal you could have predicted, delivered as a server error, reads as the tool
breaking.

If it is refused anyway, relay Odevio's own message rather than paraphrasing it. It names their current plan
and, when they belong to a team, points at the `--team` option itself.

### One limit that only shows up later

Attaching the account to a team clears the way to *create* it, but a **second app** on that Apple account
additionally requires the team's manager to be on a Business plan. `profile` shows each team's admin, not
their plan, so this cannot be checked in advance — you find out when creating the second app. If that
happens, the message says so plainly; the way out is the team manager's plan, not anything about the app.

### Once there is more than one

- **Always pass `--account-key` explicitly.** With a single account the CLI selects it silently; the moment a
  second one exists that stops, and outside a terminal the command fails instead of choosing. Naming the
  account every time is also the only thing standing between a client's app and the wrong Apple team.
- **The account is fixed when the app is created.** `app mk` and `app import` take it, and it cannot be moved
  afterwards — a wrong choice here is undone by deleting the app and creating it again. Read the account name
  back to the user before creating, exactly as you would an identifier.
- **Name the account in words they recognise** — the client's name, never the key — whenever you say which one
  you are about to use.

---

# Part 2 — The app

## Question 3 — the app name

Ask for the name they want to see on their phone. Nothing else about it needs discussing.

## Question 4 — confirm the identifier

Every iOS app needs a globally unique identifier in reverse-domain form. They almost certainly do not know
what that means, so **derive one and ask them to confirm it, once**.

Derive `com.<user>.<app>`, where `<user>` comes from their Odevio username and `<app>` from the app name, both
lowercased with everything that is not a letter or digit removed. "My Budget" for user `alex` gives
`com.alex.mybudget`.

- only letters, digits, hyphens and periods are allowed — no underscores, no spaces
- **never keep `com.example.*`**, what `flutter create` leaves behind. It is a placeholder and likely already
  taken on Apple's side

One sentence — "your app will be identified as `com.alex.mybudget`, is that fine?" — and accept a correction
without arguing. Do not explain reverse-DNS notation unless asked.

## Create it on Odevio

```sh
COLUMNS=200 odevio app mk --name "<app name>" --bundle-id <bundle id> --account-key <account key>
```

Pass `--account-key` explicitly. Omitting it opens a menu whenever the account holds more than one developer
account.

This one command also registers the identifier on the Apple Developer account, so there is nothing to do by
hand on Apple's developer portal.

## Leave the Xcode project alone

The project may still carry `com.example.<name>` locally. Leave it: Odevio rewrites the identifier on its side
from the app record, during every build. Editing the Xcode project locally is unnecessary and risks corrupting
it.

**This holds even when the identifier plainly disagrees with the app they are publishing to.** Discovering
that the project says one thing and the Odevio app another is not a reason to edit
`PRODUCT_BUNDLE_IDENTIFIER` — it is a reason to say so and ask which they meant:

> Your project is set up as `odevio.deuse.demo`, but you have pointed it at an app registered as
> `be.deuse.probe`. Which of the two are you publishing? I will not change your project either way — Odevio
> uses whichever app you name, and the setting inside the project makes no difference to the build.

Editing it silently changes the identity of their application. On an app already on the App Store that is
unrecoverable: the identifier is what Apple uses to know it is the same app, and a different one is a
different product. Never touch it, in any file, for any reason.

## Answer Apple's encryption question, without asking

Apple asks about encryption for every uploaded build. Until it is answered the build sits waiting and **never
reaches the testers** — a silent failure that looks like Odevio lost the build.

Check `ios/Runner/Info.plist` for `ITSAppUsesNonExemptEncryption`. A project from `flutter create` does not
have it. When missing, add inside the top-level `<dict>`:

```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

Not a question. Tell them in one sentence what you added and why: Apple asks whether the app uses encryption,
and an app using only standard HTTPS answers no. The one case where `<false/>` is wrong is an app implementing
its own encryption beyond the system's HTTPS — if the project pulls in a cryptography package, say so and let
them decide.

## iPhone only, or iPad too — ask, because they do not know they chose

`flutter create` writes `TARGETED_DEVICE_FAMILY = "1,2"` into the Xcode project, so **every Flutter app
declares itself for iPhone and iPad** without its author ever deciding that. Two consequences neither of them
expects:

- Apple then wants iPad pictures as well as iPhone ones
- the app is reviewed **on an iPad**, where a layout built for a phone stretches and looks broken. It is a
  common reason for a first submission to be refused

Unlike the two above, this one is theirs to decide, so ask — once, in a sentence:

> Your app is currently set up for iPhone **and** iPad. Publishing for iPhone alone saves you preparing iPad
> pictures, and avoids a refusal if the layout does not suit a tablet. You can add iPad later. iPhone only?

If they say yes, set `TARGETED_DEVICE_FAMILY = 1` in all three configurations of
`ios/Runner.xcodeproj/project.pbxproj`. Odevio rewrites the identifier, the minimum iOS version and the
signing settings during a build, but never this — so what is in the project is what ships.

Only ask when the App Store is the goal. For putting the app on their own phone it changes nothing, and it is
one question too many.

## The App Store Connect record — the first of two manual steps

Before a build can be delivered, the app must exist in App Store Connect. **This cannot be automated:**
Apple's public API does not expose app creation, and neither does Odevio. Even `fastlane produce` cannot do it
with an API key.

So guide them, precisely, and stay with them:

1. open https://appstoreconnect.apple.com and go to **Apps**
2. click **+**, then **New App**
3. tick **iOS**, put the app name from question 3, pick a language
4. in **Bundle ID**, select the identifier just created — it appears because `odevio app mk` registered it
5. for **SKU**, the identifier itself is a fine answer
6. leave the rest as proposed and create

Confirm it is done before going further: a build uploaded without this record fails in a way that is hard to
read.

Say plainly how much of this there is in total, and be accurate about it. For getting the app onto a phone or
into TestFlight, this is the **only** thing they do themselves — two minutes, once per app. For the App Store
there is exactly one more, later: answering Apple's questions about data. Nothing else.

Promising "the only one" and producing a second later costs more trust than naming both now.

## Write the `.odevio` file

At the project root, holding only what never changes between builds:

```
app-key=<odevio app key>
flutter=<version>
```

Not `build-type`: it depends on what the user wants each time, so it belongs on the command line where the
intent for that run is explicit. Not `no-progress` or `no-flutter-warning` either — those are dead keys, see `references/cli-contract.md`.

## Nothing else is asked

The Flutter version, app version, build number, build mode, Apple team and minimum iOS version are all derived
from the project or from Odevio. If you are about to ask about any of them, you are doing it wrong.
