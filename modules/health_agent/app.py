/* =========================
   static/style.css
   Dashboard grid override
   ========================= */

:root {
  --tile-gap: 12px;
}

/* ensure container uses full width */
.block-container {
  max-width: 100% !important;
  padding-left: 1rem !important;
  padding-right: 1rem !important;
  box-sizing: border-box !important;
}

/* dashboard grid: 2 columns on phones, 4 on large desktops */
.dashboard-grid,
div.dashboard-grid,
section.dashboard-grid {
  display: grid !important;
  gap: var(--tile-gap) !important;
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  align-items: stretch !important;
}

/* tiny phones: switch to 1 column */
@media (max-width: 340px) {
  .dashboard-grid,
  div.dashboard-grid,
  section.dashboard-grid {
    grid-template-columns: 1fr !important;
  }
}

/* fallback: override Streamlit auto-fit grid */
*[style*="grid-template-columns: repeat(auto-fit"] {
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
}

/* force children not to set large min-widths */
[data-testid^="stColumn"] > *,
[data-testid="stHorizontalBlock"] > *,
.rmp-card, .stBlock {
  min-width: 0 !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
}

/* card/tile styling */
.rmp-card {
  border-radius: 12px !important;
  border: 1px solid rgba(0,0,0,0.08) !important;
  background: #fff !important;
  padding: 12px !important;
  min-height: 120px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  align-items: center !important;
}

/* metric text inside cards */
.rmp-card .metric {
  font-size: 1.6rem !important;
  margin-top: 6px !important;
  color: #222 !important;
}

/* avoid horizontal scrolling */
html, body, .block-container {
  overflow-x: hidden !important;
}
