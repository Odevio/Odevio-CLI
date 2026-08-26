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

`references/templates/` holds vetted, internally title-safe templates. Read the one you pick — the
comments explain every prop — fill it through props, and keep its locked geometry (see below). Do not
ask the user for JSX; start from a template rather than inventing framing and screenshot placement from
scratch. `design-directions.md` covers *which* concept to choose.

| Template | When to use |
|---|---|
| `appstore_card.jsx` | the clean fallback — centred phone, headline above or below (`layout` prop) |
| `appstore_card_editorial.jsx` | oversized headline as the composition, phone bleeding off the bottom |
| `appstore_card_hero.jsx` | one screen leads — phone bleeds off the top, headline centred below |

Both take the same server-injected assets; each has its own authored props (read its header).

**Props split in two.** Some are yours to write; some the server injects and you must never set:

| Prop | Who sets it | What it is |
|---|---|---|
| `headline`, `subhead`, `eyebrow`, `background`, `headlineColor`, `accent`, `fontFamily` | you | the words and the styling |
| `layout` | you | `"headline-top"` (default) or `"headline-bottom"` — the two vetted arrangements |
| `_source_image` | the server | the user's raw screenshot, as a data URI |
| `_frame_image` | the server | the phone frame PNG for that size |
| `_frame_window` | the server | where the screen shows through the frame, as fractions |

The `_`-prefixed props arrive after your props, tied to the raw screenshot you targeted. Leaving them
out of your props JSON is correct — writing them yourself is not.

**Default to a props file on an existing template — and don't rebuild what a prop already does.** Point
`--jsx-file` at one of `references/templates/*.jsx` and vary the `--props-file` from card to card. The
spacing, type sizes, phone size and the arrangements are already solved; the `layout` prop switches
between `"headline-top"` and `"headline-bottom"`, and **headline-bottom already centres the text in the
space under the phone.** So "centre the text below the phone" is a prop value — reach for the prop, not
a geometry edit. Most requests are a prop or a different template; try that first, every time.

**A genuinely new layout is welcome — build it as a new template, deliberately, keeping two
invariants.** If the user has an idea the three templates don't cover, make a new template file for it
rather than mangling an existing one mid-conversation. Two rules keep the frame and the screenshot from
drifting apart — break either and the picture comes visibly undone, which is what went wrong when a card
was hand-edited on the fly:

1. **Never clamp the frame box's height** (no `maxHeight`, no fixed height). The screenshot is placed as
   percentages of that box while the frame image keeps its own intrinsic height; clamp the box and the
   two slide apart — screenshot in one place, frame in another. To make the phone smaller, give it less
   **width**; the height follows.
2. **Size the frame and the screenshot off the same box**, and let the phone's band hug the phone so the
   text centres in the real space beside it.

Build the new layout, check it in the editor preview, and only rely on it once it holds — do not tweak
geometry blindly round after round to chase a look.

## The screenshots are the user's own

You compose cards from the screenshots the user has already put in the editor. **Odevio does not take
screenshots for them** — do not offer to start a device, run the app and photograph screens. If a size
has too few shots, ask the user to capture more on their own phone or simulator and drop them into the
editor, then carry on. Never propose capturing screens on an Odevio machine.

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

Each card is a different **beat**, never the same idea reworded: the first says who the app is, the
next shows a feature, the next the payoff. Two cards with the same words rearranged are not a story.

One honest limit: if every card is built on the **same screenshot**, only the words can differ — that
is a set of captions, not a campaign. A real story needs a second screen, a different moment in the
app. When you hit that wall, say it, and ask the user to capture another screen on their phone or
simulator and drop it in the editor; then build the next beat on it.

## The flow, start to finish

**1. See what there is.** The raw screenshots and whether each already carries a visual:

```bash
odevio screenshot ls <app-key>
```

Each row has an id — `#150` — its size, and its visual state: `—`, `draft`, or `approved`. The id is
how everything below targets one shot. This is a read; run it freely.

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

**3. Author it.** Point `--jsx-file` at the chosen template in `references/templates/` **as-is**, write
a props JSON for this card, and create the visual for that id:

```bash
odevio screenshot visual <app-key> 150 --jsx-file references/templates/appstore_card.jsx --props-file <file>
```

For most cards you write only the props file; a genuinely new layout is a new template (keeping the two
invariants above). This is their product content, made on their behalf — so make it, but **do not paste
the command or the props at them**. One visual per screenshot: running it again on the same id updates
in place and resets approval, so a stale image never ships. The command dry-compiles through the
preview, so a broken component is caught here, not at approval.

**4. Send them to the editor to look.** The editor is the judging surface — the same compiled HTML the
final PNG is made from, so what they see is what Apple gets.

> Done — refresh the editor and it is under the 6.9-inch size. Tell me what to change.

**5. Iterate on the preview, not on PNGs.** Every change is a **props** change — headline, subhead,
colours, font, `layout`. Re-run the `visual` command with the new props file; they refresh. Work
against the light HTML preview every round. Do **not** approve just to look — approval is for when it
is right, and rendering a PNG each iteration is slow and pointless when the preview already matches.

**Say what you will change before you render it.** When the user reacts or asks for something, put the
new line or the new look in words first and get a nod, then re-render — do not silently push a new
version and tell them to refresh. A change they can read in one sentence saves a wasted render and
keeps the words theirs. Most changes are a prop or a different template; if the ask is genuinely a new
layout, build it as a new template with the two invariants above and verify it in the preview — never
tweak an existing template's geometry blindly to chase the look.

**6. Approve only on an explicit yes:**

```bash
odevio screenshot approve-visual <app-key> 150
```

This renders the exact-pixel submission PNG and marks the visual as the image that replaces the raw
screenshot. **Nothing reaches Apple until `odevio screenshot push`** — approval is a local decision,
push is the Apple gate, and push still asks every time. Say both facts when you offer to approve, so
the boundary is clear.

The approved visual replaces the raw in what `push` sends; the raw stays in the database as the source
you can always re-skin later.

## Fonts

The card looks generic in the bundled font and distinctive in the right one, so it is worth asking
whether they have a font in mind. Name a Google Font and the weights you need:

```bash
odevio screenshot visual <app-key> 150 --jsx-file <file> --props-file <file> --font 'Inter:600,800'
```

The font is fetched once and cached locally, embedded into the render so the editor and the final PNG
show it identically. Set the template's `fontFamily` prop to the same family name so the card actually
uses it. One honest limit: **only Google Fonts resolve this way** — a font from anywhere else will not
embed, and the card falls back to Inter. If they want a specific non-Google face, say so rather than
letting it silently fall back.

## Coming back later

Everything is kept — the JSX and the props, per visual — so weeks later you can change one headline
without starting over. Target the same id, edit, and it reloads what was stored.
