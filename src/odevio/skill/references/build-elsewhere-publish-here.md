# Building somewhere else, publishing here

**Two conditions before any of this is said out loud.** They hold even if you arrived here by accident:

1. **The user is on a Mac**, or has a CI that already produces a signed `.ipa`. On Windows or Linux none of
   this exists — close this file, say nothing about local builds, and do not suggest finding a Mac. Not
   having one is the reason Odevio exists, and hinting at a better road they cannot take is the one way to
   make a working product feel like a compromise.
2. **They raised it, not you.** An `.ipa` they already have, a CI, Xcode or fastlane mentioned, or a direct
   question. Never offer this unprompted — a Mac owner may be here exactly to avoid Xcode, certificates and
   provisioning profiles, and talking them out of that serves nobody.

Once both hold: what they want from Odevio is the App Store side — the page, the pictures, the
questionnaire, the submission.

This is a supported route, not a downgrade. A local build takes about thirty seconds against roughly
fifteen minutes on a remote machine, so someone who already builds on their own Mac is right to keep doing
it. Nothing about the App Store half is lost that way.

## Why it works

The publishing half of Odevio never asks where the binary came from. `odevio app attach-build` reads the
list of builds Apple itself holds for the app and attaches one to the version being prepared. A build
uploaded from a developer's own Mac appears in that list exactly like one uploaded by an Odevio machine.

The same is true one level down: Odevio's own remote build finishes by running `xcrun altool
--upload-app`, authenticated with **the user's** App Store Connect API key — the one they registered when
they added their Apple account here. Apple only requires that the `.ipa` be signed by a certificate
belonging to the same Apple team as that key. It does not care which machine produced it.

So the only part that has to happen elsewhere is the upload itself.

## The route, end to end

**1. They build and sign, on their own machine.** Nothing to do here. Do not offer to build for them, and
do not treat this as a step that failed.

**2. They send it to Apple themselves.** This is one of the moments where you hand control back — the
command runs on their machine, against their own key, and you cannot run it for them:

```sh
xcrun altool --upload-app -f <path-to-ipa> -t ios --apiKey <key-id> --apiIssuer <issuer-id>
```

Both identifiers are theirs; `odevio apple detail <account-key>` shows what is registered if they cannot
find them. Say what the command does before giving it, and give it once.

**3. Apple processes the build before it can be used.** This takes minutes, sometimes longer, and there is
nothing to do but wait. A build that has not finished processing is not yet `VALID`, and attaching it
fails — which reads as an error when it is really "not yet". Warn them before it happens rather than
explaining it afterwards.

**4. Odevio takes over from there, unchanged.** Everything in `app-store-listing.md` applies as written:
read the page, create it if needed, write the metadata, put the pictures on, answer the privacy
questionnaire, attach the build, ask Apple whether it is ready, submit. None of it behaves differently
because the build arrived by another road.

## What changes in how you speak

Do not offer a build. The five outcomes in Step 0 of `SKILL.md` still frame what they want, but the build
itself is already theirs — asking "shall I build it?" of someone who just built it is the tell that you
have not understood their setup.

Do not treat the absence of an Odevio build as a problem to fix. `odevio build ls` will show nothing for
this app, and that is correct, not a broken state.

## Certificates, if they ask

They can sign with their own certificates — Xcode's automatic signing on their Mac is the simplest path —
or with the ones Odevio issued for them, which are stored and downloadable. Either satisfies Apple, as
long as the certificate and the App Store Connect API key belong to the same Apple team.

Do not volunteer this. It matters only to someone who already knows what they are asking.

## Be honest about what is given up

- **Odevio holds no record of that build.** No logs, no `.ipa` to retrieve from here, nothing in
  `build ls`. Bookkeeping lives on their machine now.
- **The automatic repair of failed builds does not apply.** `when-a-build-fails.md` exists for builds this
  skill launched and can read the error code of. A compile error on their own Mac is Xcode talking to them
  directly, and they are better placed to read it than you are.
- **The build number still has to line up.** `attach-build` finds a build by its number, so the number
  they built with is the number to attach. A mismatch here looks like a missing build.

None of that touches the App Store page, which is the part they came for.
