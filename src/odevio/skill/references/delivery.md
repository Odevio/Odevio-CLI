# Delivering the app

A green build is not a delivered app. What the user gets depends entirely on the build type, and getting
this wrong makes you promise something that does not work.

## What each type actually produces

| Type | Result | Installable on a phone? |
|---|---|---|
| `configuration` | a Mac desktop with their project, Xcode and the iOS simulator | no, but they **see the app running** |
| `distribution` | a signed IPA meant for uploading to Apple | **no** — it only proves the app compiles |
| `ad-hoc` | a signed IPA for registered devices | **yes**, straight away, by URL or QR code |
| `publication` | the build uploaded to Apple | **yes**, through TestFlight after processing |
| `validation` | the build checked against Apple's rules | no, it is a check |

**Never tell the user a `distribution` build gave them an installable file.** It did not. Say the app builds
and signs correctly, then ask what they want to do with it.

## Seeing it run without paying Apple anything

The only route that works with **no Apple developer account, no certificate and no app**: a `configuration`
build. The server tolerates the missing Apple credentials for this type alone, so it goes through where every
other type would fail.

It gives them a remote macOS desktop with their project already there, Xcode, and the **iOS simulator** — so
they watch their own app running, on the day they asked, without spending 99 €.

The build reaches the status `Configuration for remote desktop`, **not** `Succeeded` — that is its finish
line, and the signal to act. Run this straight away and hand the details over without waiting to be asked:

```sh
COLUMNS=200 odevio build connect <key> --yes
```

This returns the connection details and credentials. Four things to say, honestly, before they get their hopes
up:

- they need a **VNC client** on their machine to connect — that is a real obstacle for a beginner, so check
  they have one or help them get one first
- the machine stays available for **one hour**, then closes by itself
- it is a full macOS desktop, which is unfamiliar territory. Stay with them: tell them to open the simulator
  from Xcode rather than leaving them to explore
- what they see is a **simulator**, not their phone. Good enough to check the app looks and behaves right, not
  to feel it in the hand

Offer this first to anyone without a paid Apple account. It turns "come back in 24 hours" into something they
can do now, and it is the honest answer to "I just want to see it".

## Getting it onto their phone, right now

The fastest route, and the nicest: an `ad-hoc` build, then

```sh
COLUMNS=200 odevio build ipa <key>
```

which returns a URL. Opening it in Safari **on the iPhone** installs the app directly — no TestFlight, no
Apple review, no waiting.

The command also prints a QR code, but **do not tell the user to run the command themselves to see it.**
Output from a command you ran is not reliably visible to them, and asking them to repeat something you can do
is exactly the friction this skill exists to remove.

Instead, render the QR code **into your own message**, where it is certain to be seen. The `qrcode` package
ships with the CLI, so this always works:

```sh
python -c "
import qrcode
qr = qrcode.QRCode(border=1)
qr.add_data('<the url>')
qr.print_ascii(invert=True)
"
```

Put the result in a code block, and give the URL too. Then they either scan with the camera or open the link
on the phone — whichever suits them, with nothing to type.

If the blocks come out unreadable against their terminal background, drop `invert=True` and offer it again;
the URL remains the path that always works.

### The one prerequisite: the device must be registered with Apple

**There is no Odevio command that registers a device.** Do not go looking for one, and do not invent one —
`odevio device` does not exist. Only two things are possible:

- **registering** the iPhone happens on Apple's side, at https://developer.apple.com/account under
  **Devices**, and it needs the device's **UDID**
- **`odevio apple refresh-devices <account-key>`** then pulls Apple's current list into Odevio. It only reads;
  it never adds anything

Getting the UDID is the awkward part, and it depends on their computer: plugged into a Mac it shows in Finder,
on Windows in iTunes, and on Linux there is no comfortable route at all.

**So if they are not on macOS, steer them to TestFlight instead.** It needs no UDID and no device
registration — just an Apple ID e-mail — and for someone who has never done this, that is a far shorter path
than hunting for a device identifier. Offer the QR-code route only when it is genuinely the easier one for
them.

Whichever way, say that registering a device is done once per device, not per build.

## Getting it to TestFlight

For sharing with other people, or when they asked for TestFlight, a `publication` build uploads to Apple.
Then, in plain words:

- Apple processes the build first, usually five to thirty minutes. Nothing to do but wait
- as an **internal** tester — which the account holder already is — there is **no Apple review**. They open
  TestFlight from the App Store, sign in with the same Apple ID, and the app is there
- external testers, over a public link, do go through a light review, about a day for the first build

If the build never appears in TestFlight, the usual cause is Apple's encryption question left unanswered.
That is what the `ITSAppUsesNonExemptEncryption` entry in `references/first-time-setup.md` prevents; check it
before looking anywhere else.

## Putting it on the App Store

The upload is the same `publication` build. Everything after it is theirs to do in App Store Connect:
description, screenshots, age rating, privacy answers, then submitting for review.

Be honest about this rather than leaving them to discover it: Apple reviews the app, it takes from a few
hours to a few days, and it can be refused — most often for a missing privacy policy, or for an app judged
too slight. Say that up front. "The build works" and "the app is published" are far apart, and a beginner
who learns this late feels misled.

## Files they can retrieve

Always download them **into their project**, in a folder they can actually find, never into a temporary
directory. A path like `/private/tmp/claude-501/…/sources-21MQV.zip` is unusable: they will not find it, will
not think to look there, and it disappears.

Use `odevio-artifacts/` at the project root. Visible — not a dotted folder, which macOS hides in Finder — and
obviously yours.

| What | Command |
|---|---|
| the installable app, as a URL and QR code | `odevio build ipa <key>` |
| the sources as they were built, including anything Odevio changed | `odevio build download <key> -o odevio-artifacts/sources-<key>.zip` |
| only Odevio's own changes, as a patch | `odevio build patch <key> -o odevio-artifacts/odevio-<key>.patch` |
| the full build log | `odevio build logs <key> > odevio-artifacts/build-<key>.log` |

Include the build key in each filename, so several attempts do not overwrite each other.

### Two things to set up the first time you write there

**Keep it out of Git.** Add `odevio-artifacts/` to the project's `.gitignore` if it is not already there.
Nobody wants build logs and zip archives in their history.

**Keep it out of the upload.** This one bites later if forgotten: a new folder in the project **is uploaded
with every build**, so old logs and archives would travel to the Mac each time and count towards the 500 MB
limit. Add it to `.odevioignore`, with a trailing slash to mark a directory:

```
odevio-artifacts/
```

The trailing slash matters — without it the entry is treated as a file name and the folder is still uploaded.

Then tell them the path in plain words. "It's available in your Odevio space" leaves them to go hunting;
"I've put it in `odevio-artifacts/` in your project" does not.

## When they need to see the Mac itself

For a failure that survives the loop, or to open Xcode on the project:

```sh
COLUMNS=200 odevio build connect <key> --yes
```

This returns connection details and credentials for a **remote desktop** session on the Mac. Three things
to say when offering it: it needs a VNC client on their machine, the machine stays available for **one
hour**, and it is a real macOS desktop — which for a beginner is a last resort, not a suggestion.

## Finish warmly

The app reaching their phone is the moment they were waiting for. Say it as such, tell them exactly what to
do to see it, and list what changed in their project — files that are still uncommitted, so they know
something is waiting for them.
