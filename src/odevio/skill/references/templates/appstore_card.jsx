// Base App Store marketing card. ONE template, with a LOCKED layout grid so every card stays
// title-safe and balanced no matter the content. You fill it with words, colours and a font, and pick
// a `layout` preset — you do NOT hand-tune the spacing, type sizes or phone size. Those are constants
// below, tuned so text never touches the edges and the phone never bleeds off the frame. If a request
// is "bigger title" or "tighter margins", keep the grid and answer it another way (see the reference).
//
// SERVER-INJECTED PROPS (never set these — injected after your props):
//   _source_image  data URI of the user's raw screenshot
//   _frame_image   data URI of the phone frame PNG (transparent screen window)
//   _frame_window  { left, top, width, height } fractions of the frame — where the screen shows through
//
// PROPS YOU AUTHOR:
//   headline       the accroche. Keep it short — a few words; its size steps down with each line (3 tiers).
//   subhead        optional second line, shorter than the headline
//   background      any CSS background (solid or gradient); derive it from the app's own palette
//   headlineColor   headline colour
//   accent         subhead / secondary colour
//   fontFamily      the family the server declared from --font; falls back to bundled Inter
//   eyebrow         optional tiny label above the headline (e.g. the app name), or ""
//   layout          "headline-top" (default) or "headline-bottom" — the two vetted arrangements

export default function AppStoreCard(props) {
  const {
    headline = "Your headline here",
    subhead = "",
    eyebrow = "",
    background = "linear-gradient(160deg, #1b1140 0%, #3a1d6e 55%, #5a2ea6 100%)",
    headlineColor = "#ffffff",
    accent = "rgba(255, 255, 255, 0.82)",
    fontFamily = "Inter, system-ui, sans-serif",
    layout = "headline-top",
    _source_image = "",
    _frame_image = "",
    _frame_window = { left: 0.05, top: 0.02, width: 0.9, height: 0.95 },
  } = props;

  // ---- LOCKED GRID. Do not expose these as props or edit them per card. -------------------------
  const SIDE_PAD = "10cqw"; // title-safe side margin: text never runs to the edge
  const PHONE_W = 72; // phone width, % of the card
  const SCREEN_RADIUS = `${PHONE_W * 0.1256}cqw`; // screen corners follow the phone width
  const SUBHEAD_SIZE = "4.2cqw";
  const EYEBROW_SIZE = "3.1cqw";
  const SUBHEAD_MEASURE = "78cqw"; // longest subhead line
  // ------------------------------------------------------------------------------------------------

  // Headline size follows the copy (computed once at render from props): 3 fixed tiers.
  const headlineLines = String(headline).split("\n");
  const longestLine = Math.max(1, ...headlineLines.map((l) => l.length));
  const tier = headlineLines.length >= 3 || longestLine > 26 ? 3 : headlineLines.length === 2 || longestLine > 14 ? 2 : 1;
  const HEADLINE_SIZE = tier === 1 ? "9.6cqw" : tier === 2 ? "8.4cqw" : "7.6cqw"; // 1 / 2 / 3 lines

  const headlineFirst = layout !== "headline-bottom";

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
    alignItems: "center",
    containerType: "size",
  };

  // The text block. Fixed side padding is the title-safe floor; it is never reduced.
  // headline-bottom: 4cqw above, 9cqw below, so the block sits on the optical centre of its band.
  const textBlock = {
    width: "100%",
    boxSizing: "border-box",
    padding: headlineFirst ? `11cqw ${SIDE_PAD} 0` : `4cqw ${SIDE_PAD} 9cqw`,
    textAlign: "center",
    flex: headlineFirst ? "0 0 auto" : "1 1 auto",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
  };

  const eyebrowStyle = {
    margin: "0 0 2.6cqw",
    fontSize: EYEBROW_SIZE,
    fontWeight: 700,
    letterSpacing: "0.2em",
    textTransform: "uppercase",
    color: accent,
  };

  const headlineStyle = {
    margin: 0,
    fontSize: HEADLINE_SIZE,
    lineHeight: 1.05,
    fontWeight: 700,
    letterSpacing: "-0.02em",
    // Honour explicit line breaks in the headline (a "\n" in the prop) while still wrapping long lines.
    whiteSpace: "pre-line",
    textWrap: "balance",
  };

  const subheadStyle = {
    margin: "3.2cqw 0 0",
    maxWidth: SUBHEAD_MEASURE,
    fontSize: SUBHEAD_SIZE,
    lineHeight: 1.3,
    fontWeight: 400,
    color: accent,
    textWrap: "balance",
  };

  // The phone fills the remaining space and is centred. `1 0 auto`: it may grow, never shrink below
  // the phone, so over-long copy pushes the phone down instead of overlapping it.
  const phoneWrap = {
    position: "relative",
    flex: headlineFirst ? "1 0 auto" : "0 0 auto",
    width: "100%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: headlineFirst ? "3cqw 0 2cqw" : "8cqw 0 0",
  };

  // Width alone drives the phone, so the box height always equals the frame image's height and the
  // screenshot, positioned with the window fractions, lands exactly in the screen. Never clamp this
  // box's height. Make room by giving the phone less width, never less height.
  const frameBox = {
    position: "relative",
    width: `${PHONE_W}%`,
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

  const textNode = (
    <div style={textBlock}>
      {eyebrow ? <div style={eyebrowStyle}>{eyebrow}</div> : null}
      <h1 style={headlineStyle}>{headline}</h1>
      {subhead ? <p style={subheadStyle}>{subhead}</p> : null}
    </div>
  );

  const phoneNode = (
    <div style={phoneWrap}>
      <div style={frameBox}>
        {_source_image ? <img src={_source_image} alt="" style={screenStyle} /> : null}
        {_frame_image ? <img src={_frame_image} alt="" style={frameImg} /> : null}
      </div>
    </div>
  );

  return (
    <div style={root}>
      {headlineFirst ? textNode : phoneNode}
      {headlineFirst ? phoneNode : textNode}
    </div>
  );
}
