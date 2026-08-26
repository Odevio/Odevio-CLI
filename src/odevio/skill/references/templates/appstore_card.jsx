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
//   headline       the accroche. Keep it short — a few words. Long lines wrap; they do not shrink.
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
  const PHONE_WIDTH = "74%"; // leaves clear margin on both sides of the phone
  const SCREEN_RADIUS = "9.3cqw"; // matches the frame's screen corners at PHONE_WIDTH
  const HEADLINE_SIZE = "7.4cqw";
  const SUBHEAD_SIZE = "4.2cqw";
  const EYEBROW_SIZE = "3.1cqw";
  // ------------------------------------------------------------------------------------------------

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
  const textBlock = {
    width: "100%",
    boxSizing: "border-box",
    padding: headlineFirst ? `9cqw ${SIDE_PAD} 0` : `4cqw ${SIDE_PAD} 4cqw`,
    textAlign: "center",
    flex: headlineFirst ? "0 0 auto" : "1 1 auto",
    display: headlineFirst ? "block" : "flex",
    flexDirection: "column",
    justifyContent: "center",
  };

  const eyebrowStyle = {
    margin: `0 0 3cqw`,
    fontSize: EYEBROW_SIZE,
    fontWeight: 600,
    letterSpacing: "0.22em",
    textTransform: "uppercase",
    color: accent,
  };

  const headlineStyle = {
    margin: 0,
    fontSize: HEADLINE_SIZE,
    lineHeight: 1.1,
    fontWeight: 700,
    letterSpacing: "-0.01em",
    // Honour explicit line breaks in the headline (a "\n" in the prop) while still wrapping long lines.
    whiteSpace: "pre-line",
  };

  const subheadStyle = {
    margin: "3cqw 0 0",
    fontSize: SUBHEAD_SIZE,
    lineHeight: 1.25,
    fontWeight: 400,
    color: accent,
  };

  // The phone fills the remaining space and is centred, so its top and bottom slack are small, even
  // margins — it never touches the top or bottom edge.
  const phoneWrap = {
    position: "relative",
    flex: headlineFirst ? "1 1 auto" : "0 0 auto",
    width: "100%",
    minHeight: 0,
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: headlineFirst ? "2cqw 0" : "8cqw 0 0",
  };

  // Width alone drives the phone, so the box height always equals the frame image's height and the
  // screenshot, positioned with the window fractions, lands exactly in the screen. Never clamp this
  // box's height: the frame keeps its own size while the screenshot follows the box, and the two
  // come apart. Make room by giving the phone less width, never less height.
  const frameBox = {
    position: "relative",
    width: PHONE_WIDTH,
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
