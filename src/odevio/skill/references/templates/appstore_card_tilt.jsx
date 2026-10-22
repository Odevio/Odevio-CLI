// Tilt concept card. Asymmetric: a left-aligned headline at the top, and the phone pushed right of
// centre, turned a few degrees and cropped by the right and bottom edges. It reads as "picked up",
// not "displayed" — use it for an active, hands-on beat (adding, ticking off, logging) in the middle of
// a set, between calmer centred cards.
//
// Geometry is LOCKED; you fill words, colours and a font. Keep the headline to 1–3 short lines.
//
// Invariants: the frame box is sized by WIDTH only; screenshot and frame share that box, so the
// rotation turns them together and they cannot drift. The rotation is a transform on the box, which
// does not change its layout size. The phone band is `flex: 1 0 auto`:
// tall copy pushes the phone down, it never slides under the text.
//
// Space follows the text: the text block sits a fixed TEXT_GAP above the phone, and the phone is
// anchored to the bottom with a minimum bleed. Short copy -> the free space goes ABOVE the text (a top
// spacer absorbs it), never into a hole between text and phone; tall copy -> the spacer collapses and
// the phone is pushed down and cropped further. The headline size also follows the copy (tiers).
//
// SERVER-INJECTED (never set): _source_image, _frame_image, _frame_window.
// YOU AUTHOR: eyebrow, headline, subhead, background, headlineColor, accent, fontFamily.

export default function AppStoreCardTilt(props) {
  const {
    eyebrow = "",
    headline = "Your headline\nhere",
    subhead = "",
    background = "linear-gradient(165deg, #10233f 0%, #1d3f6e 100%)",
    headlineColor = "#ffffff",
    accent = "#9cc3ff",
    fontFamily = "Inter, system-ui, sans-serif",
    _source_image = "",
    _frame_image = "",
    _frame_window = { left: 0.05, top: 0.02, width: 0.9, height: 0.95 },
  } = props;

  // ---- LOCKED GRID ------------------------------------------------------------------------------
  const SIDE_PAD = "9cqw";
  const PHONE_W = 82; // % of the card
  const SCREEN_RADIUS = `${PHONE_W * 0.1256}cqw`;
  const TILT = "7deg"; // clockwise; the top-left corner rises ~PHONE_W/2 * sin(7deg) ≈ 5cqw
  const PHONE_SHIFT = "13cqw"; // the phone's centre sits this far right of the card's centre
  const PHONE_BLEED = "-12cqw"; // minimum run past the bottom edge (the tilt lifts one corner ~5cqw)
  const TEXT_GAP = "10cqw"; // covers the rising corner + breathing room under the text
  const SUBHEAD_SIZE = "4.3cqw";
  const EYEBROW_SIZE = "3.1cqw";
  const SUBHEAD_MEASURE = "66cqw";
  // -----------------------------------------------------------------------------------------------

  // Headline size follows the copy (computed once at render from props): 3 fixed tiers.
  const headlineLines = String(headline).split("\n");
  const longestLine = Math.max(1, ...headlineLines.map((l) => l.length));
  const tier = headlineLines.length >= 3 || longestLine > 26 ? 3 : headlineLines.length === 2 || longestLine > 14 ? 2 : 1;
  const HEADLINE_SIZE = tier === 1 ? "13cqw" : tier === 2 ? "11cqw" : "9.6cqw"; // 1 / 2 / 3 lines

  const spacer = { flex: "1 0 0", minHeight: 0 };

  const root = {
    position: "relative",
    width: "100%",
    height: "100%",
    overflow: "hidden",
    background,
    fontFamily,
    color: headlineColor,
    display: "flex",
    flexDirection: "column",
    containerType: "size",
  };

  const textBlock = {
    position: "relative",
    zIndex: 2,
    boxSizing: "border-box",
    width: "100%",
    padding: `11cqw ${SIDE_PAD} 0`,
    flex: "0 0 auto",
    textAlign: "left",
  };

  const eyebrowStyle = {
    margin: "0 0 3cqw",
    fontSize: EYEBROW_SIZE,
    fontWeight: 700,
    letterSpacing: "0.22em",
    textTransform: "uppercase",
    color: accent,
  };

  const headlineStyle = {
    margin: 0,
    fontSize: HEADLINE_SIZE,
    lineHeight: 1.02,
    fontWeight: 800,
    letterSpacing: "-0.025em",
    whiteSpace: "pre-line",
  };

  const subheadStyle = {
    margin: "3.6cqw 0 0",
    maxWidth: SUBHEAD_MEASURE,
    fontSize: SUBHEAD_SIZE,
    lineHeight: 1.3,
    fontWeight: 400,
    color: accent,
    textWrap: "pretty",
  };

  const phoneWrap = {
    position: "relative",
    zIndex: 1,
    flex: "0 0 auto",
    width: "100%",
    paddingTop: TEXT_GAP,
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-end",
  };

  const frameBox = {
    position: "relative",
    flex: "none",
    width: `${PHONE_W}%`,
    marginBottom: PHONE_BLEED,
    transform: `translateX(${PHONE_SHIFT}) rotate(${TILT})`,
    transformOrigin: "50% 0",
  };

  const win = _frame_window || {};
  const screenStyle = {
    position: "absolute",
    left: `${(win.left || 0) * 100}%`,
    top: `${(win.top || 0) * 100}%`,
    width: `${(win.width || 1) * 100}%`,
    height: `${(win.height || 1) * 100}%`,
    objectFit: "cover",
    borderRadius: SCREEN_RADIUS,
    background: "#000",
  };

  const frameImg = {
    position: "relative",
    display: "block",
    width: "100%",
    zIndex: 1,
    pointerEvents: "none",
  };

  return (
    <div style={root}>
      <div style={spacer} />
      <div style={textBlock}>
        {eyebrow ? <div style={eyebrowStyle}>{eyebrow}</div> : null}
        <h1 style={headlineStyle}>{headline}</h1>
        {subhead ? <p style={subheadStyle}>{subhead}</p> : null}
      </div>
      <div style={phoneWrap}>
        <div style={frameBox}>
          {_source_image ? <img src={_source_image} alt="" style={screenStyle} /> : null}
          {_frame_image ? <img src={_frame_image} alt="" style={frameImg} /> : null}
        </div>
      </div>
    </div>
  );
}
