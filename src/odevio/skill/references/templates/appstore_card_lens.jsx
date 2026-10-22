// Lens concept card ("UI as object"). The phone is centred and bleeds off the bottom; a wide,
// frameless inset floats across its upper part and shows one zone of the SAME screenshot, enlarged —
// two rows of a list, a card, a total. Use it when the value is in a detail that is too small to read
// in a whole-phone shot.
//
// Authenticity: the inset is `_source_image` shown a second time, scaled and cropped in CSS. Nothing is
// redrawn, nothing is added.
//
// THE `focus` PROP — which zone of the screenshot the inset shows, as fractions of the screenshot's
// height, across its full width:   { "top": 0.148, "height": 0.175 }   (0 = top, 1 = bottom)
// How to fill it: look at the PNG, find the element(s) to feature, measure them in px and divide by the
// image height: top = y_top / H, height = (y_bottom − y_top) / H. Take whole elements (a row, a card)
// with a little margin; never cut through a line of text. Without `focus`, DEFAULT_FOCUS is used
// (the band under a standard iOS large title, where the first rows of a list usually sit).
//
// The inset's position and size on the card are LOCKED; only the zone shown changes. The screenshot is
// scaled to exactly the inset's width (MIN_ZOOM = MAX_ZOOM, computed for the 6.9" aspect 1320×2868), so
// the inset always shows the full width of the screen and never cuts a value off at its edges. It shows
// a band about 17% of the screen's height, centred on the middle of `focus`: a shorter zone gets some
// context above and below, a taller one is cut to that band.
//
// Invariants: the frame box is sized by WIDTH only; the phone screenshot is the FIRST <img>; the inset
// is absolutely positioned inside the frame box, so it never changes the box's size and always sits
// below the text. The phone band is `flex: 1 0 auto`: tall copy pushes the phone down.
//
// Space follows the text: the phone is anchored to the bottom with a minimum bleed, and the free space
// above it is shared between the top of the card and the gap under the text (TOP_SHARE : GAP_SHARE), so
// short copy sits balanced instead of leaving the top empty; tall copy -> both collapse to TEXT_GAP and
// the phone is pushed down and cropped further. The headline size also follows the copy (tiers).
//
// SERVER-INJECTED (never set): _source_image, _frame_image, _frame_window.
// YOU AUTHOR: eyebrow, headline, subhead, background, headlineColor, accent, fontFamily, focus.

export default function AppStoreCardLens(props) {
  const {
    eyebrow = "",
    headline = "Your headline\nhere",
    subhead = "",
    background = "#f1ece3",
    headlineColor = "#1d2a22",
    accent = "#3d6b52",
    fontFamily = "Inter, system-ui, sans-serif",
    focus = null,
    _source_image = "",
    _frame_image = "",
    _frame_window = { left: 0.05, top: 0.02, width: 0.9, height: 0.95 },
  } = props;

  // ---- LOCKED GRID ------------------------------------------------------------------------------
  const SIDE_PAD = "9cqw";
  const PHONE_W = 72; // % of the card
  const PHONE_BLEED = "-14cqw"; // minimum
  const SCREEN_RADIUS = `${PHONE_W * 0.1256}cqw`;
  const TEXT_GAP = "8cqw";
  const INSET_W = 80; // cqw — 10cqw from each card edge
  const INSET_H = 30; // cqw
  const INSET_LEFT = `${(100 - INSET_W) / 2 - (100 - PHONE_W) / 2}cqw`; // centred on the card
  const INSET_Y = "13%"; // of the phone box height, from the phone's top edge
  const INSET_RADIUS = "4cqw";
  const ASPECT = 1320 / 2868; // screenshot width / height (6.9")
  const MIN_ZOOM = (INSET_W / (ASPECT * INSET_H)) * 100; // image height %, below which sides show
  const MAX_ZOOM = MIN_ZOOM; // any further and the screen's left and right edges would be cropped
  const DEFAULT_FOCUS = { top: 0.148, height: 0.175 };
  const SUBHEAD_SIZE = "4.3cqw";
  const EYEBROW_SIZE = "3.1cqw";
  const SUBHEAD_MEASURE = "72cqw";
  // -----------------------------------------------------------------------------------------------

  const f = focus && focus.height > 0 ? focus : DEFAULT_FOCUS;
  const zoom = Math.min(Math.max(100 / f.height, MIN_ZOOM), MAX_ZOOM); // image height, % of the inset height
  const zoneCentre = f.top + f.height / 2;
  const imgTop = 50 - zoneCentre * zoom; // % of the inset height; equals -top/height when zoom = 100/height

  // Headline size follows the copy (computed once at render from props): 3 fixed tiers.
  const headlineLines = String(headline).split("\n");
  const longestLine = Math.max(1, ...headlineLines.map((l) => l.length));
  const tier = headlineLines.length >= 3 || longestLine > 26 ? 3 : headlineLines.length === 2 || longestLine > 14 ? 2 : 1;
  const HEADLINE_SIZE = tier === 1 ? "12cqw" : tier === 2 ? "10.4cqw" : "9.2cqw"; // 1 / 2 / 3 lines

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
    zIndex: 4,
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

  const inset = {
    position: "absolute",
    zIndex: 3,
    left: INSET_LEFT,
    top: INSET_Y,
    width: `${INSET_W}cqw`,
    height: `${INSET_H}cqw`,
    overflow: "hidden",
    borderRadius: INSET_RADIUS,
    background: "#fff",
    boxShadow: "0 0 0 0.35cqw rgba(0,0,0,0.06), 0 5cqw 11cqw -3cqw rgba(0,0,0,0.42)",
  };

  // Height drives the scale; width follows the image's own aspect. Centred horizontally.
  const insetImg = {
    position: "absolute",
    left: "50%",
    top: `${imgTop}%`,
    height: `${zoom}%`,
    width: "auto",
    maxWidth: "none",
    display: "block",
    transform: "translateX(-50%)",
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
          {_source_image ? (
            <div style={inset}>
              <img src={_source_image} alt="" style={insetImg} />
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
