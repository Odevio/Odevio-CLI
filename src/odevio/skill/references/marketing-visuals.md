# Marketing visuals for the App Store

Raw screenshots ship perfectly well. This is the optional step above them: turning a bare screenshot
into a composed card — a headline, a styled background, the shot inside a phone frame — the kind of
picture that sells an app rather than merely showing it. Offer it when someone wants their page to
look finished, never as a hurdle in front of shipping.

The whole point is that **you compose the visual and they judge it**. They never write code, never see
a command, never touch a design tool. You author, they look at the editor and react in words, you
adjust. Keep that shape and the step feels like collaborating with a designer, not operating software.

For the *creative* side — how to make a visual distinctive instead of a generic phone-on-gradient, and
how to design a whole store page as one campaign — read `references/design-directions.md`. This file
covers the mechanics: the template, the props, the flow, and the safe grid.

## The templates

Vetted, internally title-safe templates ship with Odevio; the CLI takes them by name with
`--template NAME`. They live on the server: `odevio screenshot templates`
lists them, and `odevio screenshot templates NAME` prints the one you pick — read it, its comments explain every prop — fill it through props, and keep its locked geometry (see below). Do not ask the
user for JSX; start from a template rather than inventing framing and screenshot placement from
scratch. `design-directions.md` covers *which* concept to choose.

| Name | When to use |
|---|---|
| classic | the clean default — centred phone, headline above or below (`layout` prop) |
| editorial | oversized headline as the composition, phone bleeding off the bottom |
| hero | one screen leads — phone bleeds off the top, headline centred below |
| statement | the words are the subject — enormous headline, small phone low on the right; put the line breaks yourself |
| tilt | asymmetric — phone tilted and pushed right, cropped by the edges; for a screen whose point is top-left |
| lens | UI as object — an inset enlarges one zone of the same screenshot over the phone (`focus` prop) |
| panorama | **two App Store positions wide** — one picture across two slots, a tilted phone crossing the seam; a second headline (`headline2`) on the right card (see "A panorama" below) |

In every template the headline size steps down with its number of lines, and the phone follows the text,
so a short title leaves no hole. Put the line breaks yourself with `\n`.

All of them take the same server-injected assets and the same authored props below; `layout`, `focus`,
`inset` and `headline2` are the only ones a single template adds (read its header).

**If the user names a template, use that one.** They browse them in the editor's *Templates* panel
and ask for one by name — e.g. "use the editorial template for #149". A `#<n>` there is a **screenshot
id** (the number on each shot in the editor) — never the listing key, a separate short code even when it
happens to be all digits (`751`) — so map it straight to step 3's flow, then compose with
`odevio screenshot visual <app-key> <n> --template <name> --props-file <file>`
(or `odevio screenshot listing visual <listing-key> <n> …` when they work in a store listing).
If you don't know the app or which screenshots exist, list them first with `odevio screenshot ls
<app-key>` (`odevio screenshot listing screenshots <listing-key>` for a listing); don't stall asking the
user what `#<n>` means. Without a named template, pick the concept
yourself per `design-directions.md` — an explicit request always wins over the automatic pick.

**Props split in two.** Some are yours to write; some the server injects and you must never set:

| Prop | Who sets it | What it is |
|---|---|---|
| `headline`, `subhead`, `eyebrow`, `background`, `headlineColor`, `accent`, `fontFamily` | you | the words and the styling |
| `layout` | you | **classic only** — `"headline-top"` (default) or `"headline-bottom"`. The other cards each have one fixed arrangement and ignore it |
| `focus` | you | **lens only** — the zone of the screenshot the inset enlarges: `{"top": 0.23, "height": 0.09}`, fractions of the screenshot's height (see below) |
| `inset` | you | **lens only** — `"top"` (default) or `"bottom"`: where the inset sits. Put it where the zone is, so it covers the rows it enlarges instead of showing them twice. Always write it, even `"top"`: the editor offers the switch only when the prop is there |
| `_source_image` | the server | the user's raw screenshot, as a data URI |
| `_frame_image` | the server | the phone frame PNG for that size |
| `_frame_window` | the server | where the screen shows through the frame, as fractions |

A props file is flat JSON — only your own props, never the `_`-prefixed ones:

```json
{
  "eyebrow": "PLAN YOUR WEEK",
  "headline": "Plan your week\nin one tap",
  "subhead": "Every task, one screen.",
  "layout": "headline-bottom",
  "background": "linear-gradient(160deg, #2b1055 0%, #7b2ff7 100%)",
  "headlineColor": "#ffffff",
  "accent": "rgba(255, 255, 255, 0.82)",
  "fontFamily": "Inter"
}
```

**Placing `focus`.** The inset always spans the full width of the screen and shows a band about **17% of
its height**, centred on the middle of `focus`: only that centre really counts. Open the capture you
uploaded, find the one or two rows to feature, take the middle of them in pixels and divide by the image's
height; then write `{"top": centre − 0.085, "height": 0.17}`. Check the band's top and bottom edges
(`centre ± 0.085`) fall between rows, never through a line of text, and move the centre if they do. A
band holds about two ordinary list rows: it cannot isolate a single one, so feature a pair, or shift the
centre off the row so the band ends on whole rows. Rows just past the inset's edge are half hidden by it
on the phone: check them in the preview. The
inset shows the screenshot as framed in the editor, so after a zoom or a move the fractions shift: always
`preview`, look at the inset, and adjust.

`headline` honours `\n` — the templates render it with `white-space: pre-line`, so that is how you control
where the line breaks instead of leaving it to the box width.

The `_`-prefixed props arrive after your props, tied to the raw screenshot you targeted. Leaving them
out of your props JSON is correct — writing them yourself is not.

**Default to a props file on an existing template — and don't rebuild what a prop already does.** Pass
`--template <name>` and vary the `--props-file` from card to card. The
spacing, type sizes, phone size and the arrangements are already solved; on the classic card the
`layout` prop switches between `"headline-top"` and `"headline-bottom"`, and **headline-bottom already
centres the text in the space under the phone.** So "centre the text below the phone" is a prop value —
reach for the prop, not a geometry edit. Most requests are a prop or a different template; try that
first, every time.

**Never edit a shipped template, and do not offer a new one on your own.** When a card does not work
with one template, try its props (`layout`, `inset`, `focus`), another shipped template or another
screenshot, and say what the template cannot do. A new layout is for when the user asks for one
outright: then build it as a new template, deliberately, keeping three invariants — a new file in the
user's working folder (start from `odevio screenshot templates NAME > my_card.jsx`), passed with
`--jsx-file <path>`; a shipped template is never changed. These rules keep the frame and the screenshot from
drifting apart — break one and the picture comes visibly undone, which is what went wrong when a card
was hand-edited on the fly:

1. **Never clamp the frame box's height** (no `maxHeight`, no fixed height). The screenshot is placed as
   percentages of that box while the frame image keeps its own intrinsic height; clamp the box and the
   two slide apart — screenshot in one place, frame in another. To make the phone smaller, give it less
   **width**; the height follows.
2. **Size the frame and the screenshot off the same box**, and let the phone's band hug the phone so the
   text centres in the real space beside it.
3. **Set `containerType: "size"` on the root and express every size in `cqw`**, never in `px`. The card
   is rendered at the slot's exact pixel size, which differs from one device size to the next; container
   units make the whole locked grid scale with the card's own box, so one template serves every size.
   A `px` value is right at one size and wrong at all the others.

Build the new layout, check it in the editor preview, and only rely on it once it holds — do not tweak
geometry blindly round after round to chase a look.

Colours come in pairs: a template's default `background` and its default `headlineColor`/`accent` have to
be readable together. The hero card is the light-ground one, so its type defaults are dark; the other two
are dark-ground with white type. Change one and change the other.

## The screenshots are the user's own

You compose cards over raw screenshots of the user's own app: captured on their phone, or — **on a Mac —
on their own simulator, by you** (below). Never propose capturing screens on an Odevio machine. If a size
has too few shots, ask for more captures and carry on.

Raw captures come in the same way as finished pictures — `upload` — or through the editor's *Add
screenshots*. Each upload becomes a row with an id you compose on:

```bash
odevio screenshot listing upload <listing-key> --file <path> --file <path>
```

**When there are none yet, offer both ways in the same question** — never only one — and, on a Mac, the
third:

> Two ways to get your captures in: tell me the folder they are in and I upload them, or drop them
> yourself into the editor (*Add screenshots*, <editor link>) and tell me when it's done.
> *(On a Mac)* Or I take them myself: I start your app in the iPhone simulator and capture the screens.

Create the store listing first when there is none, so the link exists, and give it with the question
(`listing open <listing-key>` or `app screenshots <app-key>` prints it; they sign in there with the same
account). After they say they dropped them, list the screenshots to get
the ids — do not ask them for the ids.

### On a Mac, capture them yourself in the simulator

The user's own Mac is the fastest source of clean, exact-size captures, and you can drive it. Check
first — this is never proposed elsewhere: `uname -s` prints `Darwin` **and** `xcrun simctl list devices
available` answers. Then offer it once, in the question above; on a yes:

1. **A 6.9-inch iPhone**, so the captures are 1320 × 2868 as Apple wants them: pick an available
   *iPhone … Pro Max* from `xcrun simctl list devices available`, `xcrun simctl boot <udid>`, and
   `open -a Simulator`.
2. **A clean status bar**: `xcrun simctl status_bar <udid> override --time 9:41 --dataNetwork wifi
   --wifiBars 3 --cellularBars 4 --batteryState discharging --batteryLevel 100`.
3. **Their app on it**, from the project folder: `flutter run -d <udid>` in the background (a debug run
   shows the debug banner — `flutter run --profile` does not; use it when the project builds that way).
4. **The screens**: agree on the 3 to 5 screens that tell the story (the same beats as the cards).
   Drive the simulator yourself when you have a tool for it (tapping, typing, screenshots of the
   simulator); otherwise ask the user to open each screen in the Simulator window and tell you, one at a
   time. Prefer demo content: an empty list or a login form sells nothing — ask whether the app has a
   demo account or sample data before capturing.
5. **Capture**: `xcrun simctl io <udid> screenshot <folder>/<screen>.png` into the user's working folder
   (not a temporary one: the files are theirs). Look at each image, check it as below, then
   `upload` the ones that pass.
6. **Leave it as you found it**: `xcrun simctl status_bar <udid> clear`, stop the `flutter run`, and
   shut the simulator down if you booted it (`xcrun simctl shutdown <udid>`).

This costs them nothing and takes a few minutes; say so once. If the project does not build on their
Mac (no Xcode command line tools, a signing or pod error), do not debug their local setup for the sake of
screenshots — fall back to the two other ways.

### Check every capture before composing

Look at each image yourself first — you can open them. From a folder, look **before** uploading, and
upload only the ones that pass. A card amplifies whatever is in the shot, and
Apple wants the app as people use it. Before composing on a capture, check:

- **it is this app.** A capture of a web page, another app or the home screen does not belong in the
  set — leave it out and say which one and why.
- **nothing that should not be public**: names, messages, notifications, e-mail addresses, phone
  numbers, someone's photos. Demo data is fine — a first name the user confirms is invented can stay.
- **nothing in the way**: a tutorial bubble or a dimmed overlay, a debug button, test data (a list
  called "Test", placeholder text).

When something is wrong, ask for a clean capture of that screen — it takes them seconds on their phone.
The only fix you make yourself is **cropping or reframing**; never repaint pixels or splice parts of the
screen together: the card would show an app that does not exist.

To crop, `odevio screenshot listing crop <listing-key> <id> --top 0.06 --bottom 0.04` (or
`screenshot crop <app-key> <id>`) cuts shares of the height and as much off each side, half the total;
`--top 0 --bottom 0` restores the whole capture. Keep it small: the sides go too, and a title or a tab at
the edge is cut first — check the preview. Cropping a shot puts its visual back to draft.

**One usable capture is enough.** Apple needs at least one screenshot. Make that one strong card, ship
it, and offer more beats when they capture more screens — do not stretch one screen across several
cards.

### Sizes

Apple asks for exact pixel sizes per slot; **6.9-inch is the one that matters** — Apple scales it down
for every smaller iPhone.

| Slot | Exact size | Captures that go there |
|---|---|---|
| `6.9` | 1320 × 2868 | iPhone 16/17 Pro Max as is; any other recent iPhone — 1170 × 2532 (12–14), 1179 × 2556 (14 Pro, 15, 16), 1206 × 2622 (16/17 Pro) — with `--size 6.9` |
| `6.7` | 1290 × 2796 | iPhone 14 Plus / 15 Plus / Pro Max, as is |
| `6.5` | 1242 × 2688 | older Max phones, as is |
| `ipad` | 2048 × 2732 | 12.9-inch iPad |

A capture that is not an exact size is refused without `--size`, with a message saying so. Scaling a
recent iPhone capture to 6.9 changes its proportions by under 1% — invisible.

## When they already made the picture themselves

Some users arrive with finished artwork — made in Figma, by a designer, or with another tool — and want it
on the store as it is. That is not a failure of this step; it is a shorter route through it. Add their
files directly, and compose nothing:

```bash
odevio screenshot upload <app-key> --file <path> --size 6.9
```

`--file` repeats for several images. `--size` is one of `6.9`, `6.7`, `6.5`, `ipad`, and can be left out
when the image already matches a slot exactly — it is read from the image itself. The picture is fitted to
the slot's exact pixels; it is never put inside a phone frame, because a finished visual already is the
whole picture.

So ask before composing anything: a card built over artwork someone already paid for is wasted work.

The phone frame matches a current Dynamic Island iPhone, so a capture from that kind of device sits in
it perfectly. A screenshot from an older phone (a notch, a different status bar) still ships — the
editor resizes it to the slot — but its top furniture will not line up with the frame's Dynamic Island.
That is a device mismatch, not something to correct in the template; on a real app screen (the app's own
top bar or full-bleed content) it is invisible anyway. If it shows, ask for a shot from a newer phone
rather than distorting the fit.

## Good design is a floor, not a preference

The card has to look professional on the App Store, so the grid holds even when a request would break
it. When someone asks to "make the title bigger" or "reduce the margins", read the intent — they want
more impact — and deliver it **within** the grid rather than by crowding the edges:

- **more impact** → a bolder or shorter headline, a stronger background, the `headline-bottom` layout,
  a heavier weight — not a larger font that hits the sides;
- **tighter / less empty space** → switch layout or shorten the copy, not shrink the safe margin;
- if they insist on something that will look cramped, say plainly that you keep a safe margin so it
  reads well on the store and at thumbnail size, and offer the version that achieves what they're after.

Never let text run to the edge, and never let the phone touch the top or bottom edge. A short headline
(a few words) always beats a long one shrunk to fit — steer the copy that way.

## The whole set is one campaign

The screenshots for an app are read left to right as a set, so design them as one campaign, not one
card at a time. Before you make the second or third, look at the ones already there and **keep the
system**: the same background family, the same font, the same kind of layout. A violet card followed
by a red one reads as two different apps — so reuse the first card's palette and font unless the user
asks for contrast, and if you do change a colour, say so and confirm rather than just switching.

**Hold the system in a series, not by copying props.** A listing can carry a *series*: one theme
(font, eyebrow, a main and an optional alternate palette) and a sequence of layouts, one step per
card, repeating past the end. A card on a series brings only its words; its colours, font, eyebrow
and layout come from the series by its rank — its place among the shots of its size, the order they
were uploaded in, which the user can change by dragging in the editor. So upload in story order, set the
series once, then write words per card:

```bash
odevio screenshot series <app-key>                       # what is set, and each card's step
odevio screenshot templates --presets                    # editorial, calm, bold: layouts + one line each
odevio screenshot series <app-key> --theme-file theme.json --preset editorial
odevio screenshot visual <app-key> 150 --props-file words.json    # no --template: the step decides
```

`theme.json` holds `palette` (`background`, `headlineColor`, `accent`), optionally `alternate_palette`,
`eyebrow`, and `font` — a font the listing already has, by name. On a new listing, give the font with
`--font 'Family:600,800'` next to `--theme-file`: it wins over the file's, and no card needs a
`fontFamily` prop. Use `--sequence statement,tilt:alternate,lens` for steps of your own. A preset
alternates the main and the alternate palette from one step to the next when the theme has both — leave
`alternate_palette` out for one colour throughout. A card's own settings — `focus`, `inset`, `layout` —
are not exceptions; they stay the card's. (For a store listing, the same commands
live under `odevio screenshot listing … <listing-key>`.)

When cards already exist, read them first (`odevio screenshot visuals <app-key> --json`: template,
font, full props and their `series` step), then turn the series on **from the card that sets the
look**: `odevio screenshot series <app-key> --from-card 150 --dry-run` shows what it would derive and
how many values stay the cards' own; without `--dry-run` it creates it, and nothing re-renders. If the
existing cards disagree with each other, say so and ask which one sets the system.

A value a card sets for itself is an **exception** — a colour, the eyebrow, or a `--template` of its
own (`--follow-series` gives the card its step's layout back). Keep exceptions rare and deliberate.

**Changing the series un-approves exactly the cards whose image changes**; until they are approved
again, Apple gets the plain screenshots for them. After a change, re-approve them in one go with
`odevio screenshot approve-visual <app-key> --all`, after looking at a `preview`.

**A panorama** is one card that takes two App Store positions: the server renders it once at double
width and cuts it at the seam into two images, approved together. It reads as one picture across the
store page, so propose it **inside the series proposal, at most once per set**, as a step of the
sequence (`--sequence hero,panorama,classic`) or with `--template panorama` on one card. Rules:

- **Never across positions 3-4.** Search results show the first three images, and half a panorama there
  looks cut off. Put it on positions 1-2 or 2-3 (both halves in search results), or from 4 on.
  `odevio screenshot series <app-key>` and `visuals` show each card's positions (`2-3`) — for a store
  listing, `odevio screenshot listing series <listing-key>` and `listing visuals`. A panorama step shifts
  the cards after it by one position, and their layouts do not change (the sequence follows the cards,
  not the positions).
- **Always write a `headline2`** — the right card's line — so each half reads on its own. The tables do
  not print it; `visuals --json` does. Give the left half an eyebrow or a subhead too: with a short
  headline alone it reads half empty.
- **One screenshot**, the card's own, in one phone: it needs no second capture.
- **Check once the cards have their words.** Positions show only for shots that have a card, so run the
  check after writing them. A sequence repeats past its end, so a panorama step can come round twice:
  `series` must show exactly one two-position range, and not `3-4`. Give any other card on a panorama
  step its own `--template`.
- `preview` saves the full image and its two halves (`…-1.png`, `…-2.png`): look at both halves before
  asking the user to approve. Until it is approved, Apple gets the card's plain screenshot once.
- A first approval names the cards (`approve-visual <key> 150 151 …`); `--all` only re-approves cards a
  series change un-approved.
- Apple takes 10 images per display slot (all its pixel sizes together); an approved panorama counts
  for two, and a push over 10 is refused.

Each card is a different **beat**, never the same idea reworded: the first says who the app is, the
next shows a feature, the next the payoff. Two cards with the same words rearranged are not a story.

One honest limit: if every card is built on the **same screenshot**, only the words can differ — that
is a set of captions, not a campaign. A real story needs a second screen, a different moment in the
app. When you hit that wall, say it, and ask the user to capture another screen on their phone or
simulator and drop it in the editor; then build the next beat on it.

## No build yet — a store listing

When they only want App Store screenshots — no Odevio app for this project, no Apple account, or no wish
to build — do not walk them through Apple or app setup. A **store listing** needs neither:

```bash
odevio screenshot listing create "<app name>"
```

It prints the listing key. The flow below then runs unchanged through the `listing` sub-group, with the
same screenshot ids and the same templates:

| For an app | For a store listing |
|---|---|
| `odevio screenshot ls <app-key>` | `odevio screenshot listing screenshots <listing-key>` |
| `odevio screenshot visuals <app-key> --json` | `odevio screenshot listing visuals <listing-key> --json` |
| `odevio screenshot upload <app-key> --file …` | `odevio screenshot listing upload <listing-key> --file …` |
| `odevio screenshot visual <app-key> <id> …` | `odevio screenshot listing visual <listing-key> <id> …` |
| `odevio screenshot preview <app-key> <id> …` | `odevio screenshot listing preview <listing-key> <id> …` |
| `odevio screenshot approve-visual <app-key> <id> …` | `odevio screenshot listing approve-visual <listing-key> <id> …` |
| `odevio app screenshots <app-key>` (editor link) | `odevio screenshot listing open <listing-key>` |

App keys and listing keys are separate and can be the same string, so a listing key only ever goes to a
`listing` command. `odevio screenshot listing ls` shows the ones they already have — check it before
creating a second. `listing share <listing-key> <team-key>` lets a teammate pick the work up.

When they start building later, attach it once the app exists on Odevio:
`odevio screenshot listing link <listing-key> <app-key>`. Nothing moves — the screenshots and visuals
become the app's, and `odevio screenshot push <app-key>` sends them. It is refused when the app already
has a listing with screenshots; say so and ask which set they want to keep. Linked to the wrong app:
`odevio screenshot listing unlink <listing-key>` detaches it, everything kept, then link the right one.

## The flow, start to finish

**1. See what there is.** The raw screenshots and whether each already carries a visual:

```bash
odevio screenshot ls <app-key>
```

Each row has an id — `#150` — its size, and its visual state: `—`, `draft`, or `approved`. The id is
how everything below targets one shot. This is a read; run it freely. When some shots already carry a
visual, read them too with `odevio screenshot visuals <app-key> --json` before composing anything new.

**2. Propose the accroche — derived, not asked cold.** The headline is the app's own voice, so work it
out from what already describes the app before putting a blank question to the user. Look, in order, at:

- **the listing copy already on Apple.** `odevio app store-status <app-key>` reads the live listing and
  prints a *Current copy* block — the description, subtitle, keywords and promotional text. That is the
  app's pitch in its own words, and the best source for a headline. (A listing with no editable version
  yet shows no copy — then fall to the next source.)
- the App Store text you have written earlier **this session**, if you have not published it yet;
- the project itself: `pubspec.yaml`'s `description` and name, the `README`, the app's own on-screen
  strings. These say what the app does even when nothing has reached Apple yet.
- **the captures themselves**, when there is no project and no listing — often the case with a store
  listing. Screen titles, on-screen subtitles and real numbers ("€44 under your budget") are the app's
  own words: a headline built on them is true by construction.

Turn that into a concrete proposed line and show it — do not open with "what should it say?".

> Your description pitches this as a weekly planner, so for the first shot I'd put "Plan your week in
> one tap" over a deep-violet background. Good, or say it your way?

**Derive the look too, not just the words.** Pull the card's colours from the app's own identity rather
than a generic default: the Flutter theme's seed colour in `lib/main.dart` (e.g. a `seedColor` of
`Colors.deepPurple` → a violet background), the dominant colour of the app icon, or the colours of the
captures when that is all there is. A card that matches
the app's palette looks intentional; a stock blue does not.

Only ask an open question when there is genuinely nothing to go on — and even then, offer a default
built from the app's name rather than a blank prompt. Whatever you derive, the user still has the last
word: getting a nod before rendering saves a round.

**One nod before the first render, not one per choice.** Put the whole proposal in a single message — the
direction, the template and headline of each card, the colours, the font and the language — and ask
once. They see a first set within minutes and react to images, which is faster than answering five
questions in a row. Ask separately only what you cannot derive at all.

**The language** is their store page's when there is one; otherwise the language of the app's own
screens in the captures; otherwise the language they write to you in. Say which in the proposal.

**3. Author it.** On a set of cards, set the series first (above), then write each card's words. For a
single card, pick the template by name. Write the props JSON for this card in the user's working
folder — with your file-writing tool, not a shell heredoc, so it costs them no permission prompt — and
create the visual for that id:

```bash
odevio screenshot visual <app-key> 150 --props-file <file>                     # on a series
odevio screenshot visual <app-key> 150 --template classic --props-file <file>  # a card on its own
```

For most cards you write only the props file; a genuinely new layout is a new template (keeping the
invariants above). This is their product content, made on their behalf — so make it, but **do not paste
the command or the props at them**. One visual per screenshot: running it again on the same id updates
in place and resets approval, so a stale image never ships. The command dry-compiles through the
preview, so a broken component is caught here, not at approval.

**4. Look at it yourself, then send them to the editor.** Render a draft and open the PNG before saying
anything:

```bash
odevio screenshot preview <app-key> 150 151 --out-dir <folder>
```

It writes `preview-<id>.png` — the exact image approval would produce — and approves nothing. A preview
takes about thirty seconds a card and an approval about twenty-five; for a set, say so once before you
start rather than going quiet. Check the
words are whole and inside the margins, the contrast, the crop of the screenshot, and the typography;
fix what you see, then show them. The editor is their judging surface — the same compiled HTML the
final PNG is made from, so what they see is what Apple gets.

> Done — refresh the editor and it is under the 6.9-inch size. Tell me what to change, or retouch the
> words, colours, font or framing yourself there with **Retouch**.

Give them the editor link the first time (`odevio app screenshots <app-key>`, or
`odevio screenshot listing open <listing-key>`, which prints it), and say it opens on the web: they sign
in there with the same Odevio account. Tell them once that they can retouch a card themselves — they
will not find it otherwise.

**5. Iterate on props.** Every change is a **props** change — headline, subhead, colours, font,
`layout`. Re-run the `visual` command with the new props file, look at a fresh `preview`, then they
refresh. Do **not** approve just to look — `preview` is for looking, approval is for when it is right.

**The user can retouch a card themselves.** The editor lets them change exactly the props in the table
above — the words, the colours, the background, a font already used in the listing, `layout` — and
re-approve. Keep those names in every template you write, so a card of yours stays retouchable. A card
they touched shows `last_edited_by: "editor"` in `visuals --json` (and "editor" in the table). Before
you change such a card, read it there and start from its current props: their edits are the brief, not
something to overwrite. `visual` refuses to replace it — pass `--force` only when the user asks you to
redo that card over their changes.

**Say what you will change before you render it.** When the user reacts or asks for something, put the
new line or the new look in words first and get a nod, then re-render — do not silently push a new
version and tell them to refresh. A change they can read in one sentence saves a wasted render and
keeps the words theirs. Most changes are a prop or a different template; only when the user asks for a
new layout outright, build it as a new template with the invariants above and verify it in the preview
— never tweak a template's geometry to chase the look.

**6. Approve only on an explicit yes** — and a new one after every change: updating an approved card
puts it back to draft, so the earlier yes no longer covers it.

```bash
odevio screenshot approve-visual <app-key> 150 151 152
```

Several ids go in one call. This renders the exact-pixel submission PNG and marks the visual as the image that replaces the raw
screenshot. **Nothing reaches Apple until `odevio screenshot push`** — approval is a local decision,
push is the Apple gate, and push still asks every time. Say it in terms of where they are:

- **a store listing not linked to an app** (no app column in `listing ls`): the images stay in
  Odevio, ready. Do not talk about sending to Apple — there is nothing to send them with yet. Say once
  that they are ready for when the app exists: `listing link` attaches them, and the push sends them.
- **an app, or a listing linked to one**: say both facts when you offer to approve — approval
  chooses the image, the push sends it, and only on their word.

The approved visual replaces the raw in what `push` sends; the raw stays in the database as the source
you can always re-skin later.

## Fonts

The card looks generic in the bundled font and distinctive in the right one, so it is worth asking
whether they have a font in mind. Name a Google Font with the weights the templates use — 400 for the
subhead, 700 for the eyebrow, 800 for the headline:

```bash
odevio screenshot visual <app-key> 150 --template classic --props-file <file> --font 'Inter:400,700,800'
```

Pass `--font` when you create a card; it stays with the card when you update it later without the flag.
The font is fetched once and cached locally, embedded into the render so the editor and the final PNG
show it identically. Set the template's `fontFamily` prop to the same family name so the card actually
uses it. One honest limit: **only Google Fonts resolve this way** — a font from anywhere else will not
embed, and the card falls back to Inter. If they want a specific non-Google face, say so rather than
letting it silently fall back.

## Words in another language

Write the card in the language of their store page, with that language's typography:

- **typographic apostrophes and quotes** — `’`, `“ ”` — never the straight `'` and `"` of a keyboard;
- **French**: a narrow no-break space (U+202F) before `;` `:` `!` `?` and inside `« »`; keep the user's
  *tu* or *vous*;
- **accents**: the embedded font carries the Latin alphabet with Western European accents (é, ñ, ü, ç).
  Letters beyond it (ł, ő, ș…) and non-Latin scripts fall back to another font — check the preview, and
  pick a family that suits the language when it shows.

## Coming back later

Everything is kept — the JSX and the props, per visual — so weeks later you can change one headline
without starting over. Target the same id, edit, and it reloads what was stored.
