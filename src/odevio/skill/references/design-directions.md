# Designing the marketing visuals, not just filling a template

The goal of the store images is a small advertising campaign for the app — distinctive, designed,
immediately telling someone what makes the app worth caring about. Technical compliance (exact size,
safe area) is the floor, never the creative ceiling.

The test to hold every concept to: **would this still look like a deliberate piece of product design
if the phone frame and the store logo were removed?** If not, it is leaning on the generic
screenshot-in-a-phone formula and should be pushed further.

## What this renderer can and cannot do

Visuals are React/HTML/CSS/SVG rendered to a PNG — no image generation, no 3D, no stock photography.

- **Reachable, and where the strength is:** typographic compositions, the UI as a graphic object,
  extreme crops, layered screens, floating cards, editorial layouts, oversized UI or a huge number,
  before/after and transformation built from real screens, window/portal framings, negative space,
  asymmetric and diagonal framing, contrast, motion implied by repetition or progression.
- **Not reachable here:** photorealistic environments, product photography, real reflections on glass,
  3D device renders. Do not attempt these or promise them — they need an image generator or supplied
  assets this pipeline does not have. Reach for a strong *graphic* direction instead.

## Do not default to phone-on-gradient

A centred phone on a gradient with a caption above is the **safe fallback**, not the default — the
`classic` template is exactly that, and it is fine when a clean, safe result is all that is
wanted. Before reaching for it, consider a real concept:

- **Typographic** — a large, deliberate headline *is* the composition; the UI is a supporting detail.
- **UI as object** — enlarge one meaningful element (a button, a card, a chart, a key number) until it
  becomes the graphic subject; no whole-phone mockup needed.
- **Extreme crop** — one instantly recognisable part of the UI, enlarged dramatically.
- **Transformation / before-after** — two real states contrasted, problem to result.
- **System / floating cards** — several real UI pieces arranged as a coherent modular layout.
- **Window / portal** — the screen as an opening into the product rather than a physical device.

The phone does not have to be the hero, or centred, or whole: it can be cropped by the edge, pushed to
one side, shown as a progression, or absent entirely with the UI floating.

## A concept per image, a campaign across them

Design the sequence, not each image alone. Hold one visual system across all of them — type, spacing,
colour, corner and shadow language, device treatment — then vary the composition so the set has rhythm:

1. **Hero** — what the app is, understood in a glance. Give the first image the most care; it carries
   recognition, differentiation and impact.
2. **Core feature** — the most important interaction.
3. **Transformation** — the result or benefit.
4. **Differentiator** — what competitors do not have.
5. onwards — secondary features, signals of quality.

Not every app needs six; the point is that the images tell a story rather than repeat one layout.

## Make the feature legible — with a metaphor when a screenshot won't carry it

When a capability is hard to read from a raw screen, build a visual metaphor from real UI: search as a
lens magnifying a result out of many; organisation as chaos resolving into an aligned system; speed as
compressed spatial progression; automation as several manual steps collapsing into one. The metaphor
must reinforce a real capability — never invent one.

## Words: concrete, never generic

Kill on sight: "Powerful and intuitive", "Everything you need", "Simple. Fast. Powerful.", "The
ultimate experience", "Take your productivity to the next level". They say nothing. Write a concrete
benefit and let the image back it up:

- "Find the right photo in seconds" — not "Powerful photo management".
- "See every treatment at a glance" — not "Your health, simplified".

Keep it short; a few words with impact beat a sentence shrunk to fit.

## Composition habits worth keeping

- **Typography as a primary element:** oversized type, extreme scale contrast, a single emphasised word,
  a dramatic number, text the composition is built around rather than a caption pasted on top.
- **One dominant contrast** makes an image recognisable: large vs small, dense vs empty, a tiny UI
  element against an enormous headline, detailed UI against a bare background.
- **Negative space is confident.** One phone, a short line, and a lot of intentional empty space reads
  more premium than a canvas stuffed with gradients and floating objects.
- **Unexpected framing:** off-centre, cropped by the edge, asymmetric, diagonal — as long as it is
  deliberate and stays within the technical safe area.

## Two lines that never bend

- **Authenticity (never fabricate).** Compose, crop, scale, reframe and typeset freely — but never
  invent UI, features, numbers, testimonials, notifications or data that the product does not have. The
  product experience shown must be true.
- **Technical floor.** Whatever the concept, the final asset meets the slot's exact pixel size and stays
  title-safe (see `marketing-visuals.md` for the locked grid and margins). Explore the concept first,
  then adapt it to the size — concept → composition → design → size adaptation, never size-first.

## How to work it with the user

Explore before refining — once, for the set as a whole: sketch two or three *genuinely different*
directions in words (e.g. a typographic set, a UI-as-object set, a calm classic set), one sentence each,
and let the user pick, rather than iterating one generic layout. Lead with the one you would choose and
put the rest of the first proposal in the same message (`marketing-visuals.md`, step 2), so picking a
direction is not a round of its own. Once a direction is chosen, the cards
follow it as one campaign, and each card gets one proposed line (`marketing-visuals.md`, step 2) — not a
new choice of directions. Then author it — a props file on one of the shipped templates — have them look
in the editor, and refine.

Reach the range first through the **shipped templates and the `layout` prop**: classic (centred, headline
top or bottom), editorial (oversized headline, phone off the bottom), hero (phone off the top),
statement (enormous type, small phone low on the right), tilt (phone tilted and off-centre), lens (an
enlarged zone of the screen over the phone — UI as object). Most directions are one of these plus the
right words, colour and font — try that before anything else.

For a direction none of them covers, you *can* build a new template — deliberately: keep the
invariants listed under "a genuinely new layout" in `marketing-visuals.md`, and check it in the editor
preview before relying on it.
What breaks things is the opposite: hand-tweaking an existing template's geometry round after round to
chase a look. That is what pulls the screenshot off its frame. New idea → a fresh, verified template;
never a blind geometry edit mid-conversation.
