// Statement concept card. The words are the subject: the headline is set as large as its longest line
// allows (up to 24cqw), and a small phone sits low on the right, cropped by the right and bottom
// edges — one dominant contrast, enormous type against a small real screen. Use it for the first card
// of a set, or for a beat built on one word or one true number ("12 items", "€44 under budget").
//
// Size rule: 4 fixed tiers chosen from the LONGEST explicit line (split on "\n"), computed once at
// render from props — no DOM measurement. ≤6 chars 24cqw, ≤8 19cqw, ≤11 14.5cqw, ≤14 11.5cqw,
// longer 9.5cqw (and the line wraps). Put the line breaks yourself with \n; without them the whole headline
// counts as one line. The text itself is rendered untouched.
//
// Geometry is LOCKED; you fill words, colours and a font. The phone band is `flex: 1 0 auto`: long
// copy pushes the phone down, it never overlaps the type.
//
// Space follows the text: the phone is anchored to the bottom with a minimum bleed, and the free space
// above it is shared between the top of the card and the gap under the text (TOP_SHARE : GAP_SHARE), so
// short copy sits balanced instead of leaving the top empty; tall copy -> both collapse to TEXT_GAP and
// the phone is pushed down and cropped further. The headline size also follows the copy (tiers).
//
// SERVER-INJECTED (never set): _source_image, _frame_image, _frame_window.
// YOU AUTHOR: eyebrow, headline, subhead, background, headlineColor, accent, fontFamily.

export default function AppStoreCardStatement(props) {
  const {
    eyebrow = "",
    headline = "Say\nit big.",
    subhead = "",
    background = "#111014",
    headlineColor = "#ffffff",
    accent = "#c9b8ff",
    fontFamily = "Inter, system-ui, sans-serif",
    _source_image = "",
    _frame_image = "",
    _frame_window = { left: 0.05, top: 0.02, width: 0.9, height: 0.95 },
  } = props;

  // ---- LOCKED GRID ------------------------------------------------------------------------------
  const SIDE_PAD = "9cqw";
  // Tiers are sized for an 82cqw measure at ~0.52em per bold glyph (Inter / Fraunces 800). A line that
  // still runs long wraps (pre-line) rather than overflowing.
  const HEADLINE_TIERS = [[6, 24], [8, 19], [11, 14.5], [14, 11.5]]; // [max chars in longest line, cqw]
  const HEADLINE_FLOOR = 9.5; // cqw, for anything longer
  const PHONE_W = 66; // % of the card
  const PHONE_RIGHT = "-6cqw"; // the phone runs off the right edge by this much
  const PHONE_BLEED = "-12cqw"; // minimum
  const SCREEN_RADIUS = `${PHONE_W * 0.1256}cqw`;
  const TEXT_GAP = "6cqw";
  const SUBHEAD_SIZE = "4.4cqw";
  const EYEBROW_SIZE = "3.1cqw";
  const SUBHEAD_MEASURE = "64cqw";
  // -----------------------------------------------------------------------------------------------

  const lines = String(headline).split("\n");
  const longest = Math.max(1, ...lines.map((l) => l.length));
  const hit = HEADLINE_TIERS.find(([max]) => longest <= max);
  const headlineSize = `${hit ? hit[1] : HEADLINE_FLOOR}cqw`;

  const TOP_SHARE = 1;
  const GAP_SHARE = 0.6;
  const spacer = { flex: `${TOP_SHARE} 0 0`, minHeight: 0 };
  const gapSpacer = { flex: `${GAP_SHARE} 0 0`, minHeight: 0 };

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
    padding: `10cqw ${SIDE_PAD} 0`,
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
    fontSize: headlineSize,
    lineHeight: 0.94,
    fontWeight: 800,
    letterSpacing: "-0.035em",
    whiteSpace: "pre-line",
  };

  const subheadStyle = {
    margin: "4.4cqw 0 0",
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
    justifyContent: "flex-end",
    alignItems: "flex-end",
  };

  const frameBox = {
    position: "relative",
    flex: "none",
    width: `${PHONE_W}%`,
    marginRight: PHONE_RIGHT,
    marginBottom: PHONE_BLEED,
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
      <div style={gapSpacer} />
      <div style={phoneWrap}>
        <div style={frameBox}>
          {_source_image ? <img src={_source_image} alt="" style={screenStyle} /> : null}
          {_frame_image ? <img src={_frame_image} alt="" style={frameImg} /> : null}
        </div>
      </div>
    </div>
  );
}
