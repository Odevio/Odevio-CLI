// Hero concept card. A single screen leads: the phone bleeds off the TOP edge, and the headline is
// centred in the space beneath it. A distinct arrangement from the fallback (centred phone) and the
// editorial (oversized headline) — use it when one clean screenshot is the story and a short line
// sits under it.
//
// Geometry is LOCKED; you fill words, colours and a font. Keep the headline short.
//
// Carries the same two fixes as the base card:
//   1. Never clamp the frame box's height — the screenshot is placed as percentages of it while the
//      frame keeps its own height; clamp the box and the two slide apart. Make the phone smaller with
//      less WIDTH, never a height cap.
//   2. The phone's band hugs the phone (`flex: 0 0 auto`) so the text band below (`flex: 1 1 auto`,
//      centred) fills the real space under the frame instead of starting below an invisible gap.
//
// SERVER-INJECTED (never set): _source_image, _frame_image, _frame_window.
// YOU AUTHOR: eyebrow, headline, subhead, background, headlineColor, accent, fontFamily.

export default function AppStoreCardHero(props) {
  const {
    eyebrow = "",
    headline = "Your headline here",
    subhead = "",
    background = "linear-gradient(180deg, #efeaff 0%, #e6e0ff 100%)",
    headlineColor = "#ffffff",
    accent = "rgba(255, 255, 255, 0.82)",
    fontFamily = "Inter, system-ui, sans-serif",
    _source_image = "",
    _frame_image = "",
    _frame_window = { left: 0.05, top: 0.02, width: 0.9, height: 0.95 },
  } = props;

  // ---- LOCKED GRID ------------------------------------------------------------------------------
  const SIDE_PAD = "10cqw";
  const PHONE_WIDTH = "79%";
  const PHONE_BLEED = "12cqw"; // how far the phone runs off the top edge
  const SCREEN_RADIUS = "9.9cqw"; // matches the frame's screen corners at PHONE_WIDTH
  const HEADLINE_SIZE = "8.2cqw";
  const SUBHEAD_SIZE = "4.3cqw";
  const EYEBROW_SIZE = "3.1cqw";
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
    alignItems: "center",
    containerType: "size",
  };

  // The phone sits at the top and runs off the top edge; the card's overflow crops it. Its band hugs
  // it (fix #2) so the text below centres in the real remaining space.
  const phoneWrap = {
    position: "relative",
    flex: "0 0 auto",
    width: "100%",
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-start",
  };

  const frameBox = {
    position: "relative",
    width: PHONE_WIDTH,
    marginTop: `-${PHONE_BLEED}`,
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

  // Text fills the space under the phone and centres in it.
  const textBlock = {
    width: "100%",
    boxSizing: "border-box",
    padding: `4cqw ${SIDE_PAD}`,
    textAlign: "center",
    flex: "1 1 auto",
    minHeight: 0,
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  };

  const eyebrowStyle = {
    margin: "0 0 3cqw",
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
    whiteSpace: "pre-line",
  };

  const subheadStyle = {
    margin: "3cqw 0 0",
    fontSize: SUBHEAD_SIZE,
    lineHeight: 1.25,
    fontWeight: 400,
    color: accent,
  };

  return (
    <div style={root}>
      <div style={phoneWrap}>
        <div style={frameBox}>
          {_source_image ? <img src={_source_image} alt="" style={screenStyle} /> : null}
          {_frame_image ? <img src={_frame_image} alt="" style={frameImg} /> : null}
        </div>
      </div>
      <div style={textBlock}>
        {eyebrow ? <div style={eyebrowStyle}>{eyebrow}</div> : null}
        <h1 style={headlineStyle}>{headline}</h1>
        {subhead ? <p style={subheadStyle}>{subhead}</p> : null}
      </div>
    </div>
  );
}
