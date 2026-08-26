// Editorial / typographic concept card. The headline IS the composition — oversized, left-aligned,
// with generous negative space — and the phone is a supporting element that bleeds off the bottom edge
// (a deliberate editorial crop, not the centred-phone fallback). Use this when the pitch is carried by
// a short, strong line and one recognisable screen.
//
// Like the base card, the geometry is LOCKED: you fill words, colours and a font, not the spacing or
// type sizes. Keep the headline short (a few words) — the scale is the point, and long copy wrecks it.
//
// SERVER-INJECTED (never set): _source_image, _frame_image, _frame_window (see marketing-visuals.md).
// YOU AUTHOR: eyebrow, headline, subhead, background, headlineColor, accent, fontFamily.

export default function AppStoreCardEditorial(props) {
  const {
    eyebrow = "",
    headline = "Say more\nwith less.",
    subhead = "",
    background = "#0e0e12",
    headlineColor = "#ffffff",
    accent = "#8b7bff",
    fontFamily = "Inter, system-ui, sans-serif",
    _source_image = "",
    _frame_image = "",
    _frame_window = { left: 0.05, top: 0.02, width: 0.9, height: 0.95 },
  } = props;

  // ---- LOCKED GRID ------------------------------------------------------------------------------
  const SIDE_PAD = "9cqw"; // title-safe left/right margin for all text
  const PHONE_WIDTH = "79%"; // the phone bleeds off the bottom, cropped by the card
  const PHONE_BLEED = "-15cqw"; // how far the phone runs past the bottom edge
  const SCREEN_RADIUS = "9.9cqw"; // matches the frame's screen corners at PHONE_WIDTH
  const HEADLINE_SIZE = "12cqw"; // the hero: deliberately oversized
  const SUBHEAD_SIZE = "4.4cqw";
  const EYEBROW_SIZE = "3.2cqw";
  // -----------------------------------------------------------------------------------------------

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

  // Text pinned to the top-left, left-aligned — the magazine masthead treatment.
  const textBlock = {
    position: "relative",
    zIndex: 2,
    width: "100%",
    boxSizing: "border-box",
    padding: `10cqw ${SIDE_PAD} 0`,
    textAlign: "left",
    flex: "0 0 auto",
  };

  const eyebrowStyle = {
    margin: "0 0 3cqw",
    fontSize: EYEBROW_SIZE,
    fontWeight: 600,
    letterSpacing: "0.24em",
    textTransform: "uppercase",
    color: accent,
  };

  // whiteSpace pre-line lets the author place line breaks with \n for a controlled ragged setting.
  const headlineStyle = {
    margin: 0,
    fontSize: HEADLINE_SIZE,
    lineHeight: 1.02,
    fontWeight: 800,
    letterSpacing: "-0.02em",
    whiteSpace: "pre-line",
  };

  const subheadStyle = {
    margin: "4cqw 0 0",
    fontSize: SUBHEAD_SIZE,
    lineHeight: 1.3,
    fontWeight: 400,
    color: accent,
    maxWidth: "80%",
  };

  // The phone fills the lower area and runs off the bottom edge; the card's overflow crops it.
  const phoneWrap = {
    position: "relative",
    zIndex: 1,
    flex: "1 1 auto",
    width: "100%",
    minHeight: 0,
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-end",
  };

  const frameBox = {
    position: "relative",
    width: PHONE_WIDTH,
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
