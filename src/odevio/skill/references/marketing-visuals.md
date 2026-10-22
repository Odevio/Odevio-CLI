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

Three vetted, internally title-safe templates ship with Odevio; the CLI takes them by name with
`--template classic|editorial|hero`. Read the one you pick in `references/templates/` — the comments
explain every prop — fill it through props, and keep its locked geometry (see below). Do not ask the
user for JSX; start from a template rather than inventing framing and screenshot placement from
scratch. `design-directions.md` covers *which* concept to choose.

| Template | Name | When to use |
|---|---|---|
| `appstore_card.jsx` | classic | the clean default — centred phone, headline above or below (`layout` prop) |
| `appstore_card_editorial.jsx` | editorial | oversized headline as the composition, phone bleeding off the bottom |
| `appstore_card_hero.jsx` | hero | one screen leads — phone bleeds off the top, headline centred below |

All three take the same server-injected assets; each has its own authored props (read its header).

**If the user names a template, use that one.** They browse the three in the editor's *Templates* panel
and ask for one by name — e.g. "use the editorial template for #149". A `#<n>` there is a **screenshot
id** (the number on each shot in the editor), so map it straight to step 3's flow, then compose with
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
| `layout` | you | **`appstore_card.jsx` only** — `"headline-top"` (default) or `"headline-bottom"`. The editorial and hero cards each have one fixed arrangement and ignore it |
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

**A genuinely new layout is welcome — build it as a new template, deliberately, keeping three
invariants.** If the user has an idea the three templates don't cover, make a new template file for it
rather than mangling an existing one mid-conversation — write it in the user's working folder and pass
it with `--jsx-file <path>`. These rules keep the frame and the screenshot from
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

You compose cards over raw screenshots the user captured on their own phone or simulator. **Odevio does
not take screenshots for them** — do not offer to start a device, run the app and photograph screens,
and never propose capturing screens on an Odevio machine. If a size has too few shots, ask the user to
capture more and carry on.

Raw captures come in the same way as finished pictures — `upload` — or through the editor's *Add
screenshots*. Each upload becomes a row with an id you compose on:

```bash
odevio screenshot listing upload <listing-key> --file <path> --file <path>
```

### Check every capture before composing

Look at each image yourself first — you can open them. A card amplifies whatever is in the shot, and
Apple wants the app as people use it. Before composing on a capture, check:

- **it is this app.** A capture of a web page, another app or the home screen does not belong in the
  set — leave it out and say which one and why.
- **nothing that should not be public**: names, messages, notifications, e-mail addresses, phone
  numbers, someone's photos.
- **nothing in the way**: a tutorial bubble or a dimmed overlay, a debug button, test data (a list
  called "Test", placeholder text).

When something is wrong, ask for a clean capture of that screen — it takes them seconds on their phone.
The only fix you make yourself is **cropping or reframing**; never repaint pixels or splice parts of the
screen together: the card would show an app that does not exist.

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

You read the cards already there with `odevio screenshot visuals <app-key> --json` (or
`odevio screenshot listing visuals <listing-key> --json`): each comes with its template, font and full
props. Start the next card's props file from the first card's, and change only the words. If the
existing cards already disagree with each other, say so and ask which one sets the system.

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
has a listing with screenshots; say so and ask which set they want to keep.

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

Turn that into a concrete proposed line and show it — do not open with "what should it say?".

> Your description pitches this as a weekly planner, so for the first shot I'd put "Plan your week in
> one tap" over a deep-violet background. Good, or say it your way?

**Derive the look too, not just the words.** Pull the card's colours from the app's own identity rather
than a generic default: the Flutter theme's seed colour in `lib/main.dart` (e.g. a `seedColor` of
`Colors.deepPurple` → a violet background), or the dominant colour of the app icon. A card that matches
the app's palette looks intentional; a stock blue does not.

Only ask an open question when there is genuinely nothing to go on — and even then, offer a default
built from the app's name rather than a blank prompt. Whatever you derive, the user still has the last
word: getting a nod before rendering saves a round.

**3. Author it.** Pick the template by name, write a props JSON for this card in the user's working
folder, and create the visual for that id:

```bash
odevio screenshot visual <app-key> 150 --template classic --props-file <file>
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

It writes `preview-<id>.png` — the exact image approval would produce — and approves nothing. Check the
words are whole and inside the margins, the contrast, the crop of the screenshot, and the typography;
fix what you see, then show them. The editor is their judging surface — the same compiled HTML the
final PNG is made from, so what they see is what Apple gets.

> Done — refresh the editor and it is under the 6.9-inch size. Tell me what to change.

**5. Iterate on props.** Every change is a **props** change — headline, subhead, colours, font,
`layout`. Re-run the `visual` command with the new props file, look at a fresh `preview`, then they
refresh. Do **not** approve just to look — `preview` is for looking, approval is for when it is right.

**Say what you will change before you render it.** When the user reacts or asks for something, put the
new line or the new look in words first and get a nod, then re-render — do not silently push a new
version and tell them to refresh. A change they can read in one sentence saves a wasted render and
keeps the words theirs. Most changes are a prop or a different template; if the ask is genuinely a new
layout, build it as a new template with the invariants above and verify it in the preview — never
tweak an existing template's geometry blindly to chase the look.

**6. Approve only on an explicit yes:**

```bash
odevio screenshot approve-visual <app-key> 150 151 152
```

Several ids go in one call. This renders the exact-pixel submission PNG and marks the visual as the image that replaces the raw
screenshot. **Nothing reaches Apple until `odevio screenshot push`** — approval is a local decision,
push is the Apple gate, and push still asks every time. Say both facts when you offer to approve, so
the boundary is clear.

The approved visual replaces the raw in what `push` sends; the raw stays in the database as the source
you can always re-skin later.

## Fonts

The card looks generic in the bundled font and distinctive in the right one, so it is worth asking
whether they have a font in mind. Name a Google Font and the weights you need:

```bash
odevio screenshot visual <app-key> 150 --template classic --props-file <file> --font 'Inter:600,800'
```

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
