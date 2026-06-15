"""
app/components/theme.py
Centralized SkillSync premium theme — Dark Mode Glassmorphism.
Import and call inject_theme() at the top of every page.
"""
import streamlit as st

# ── Design Tokens ─────────────────────────────────────────────────────────────
COLORS = {
    "bg":        "#0B0D14",
    "sidebar":   "#0F1119",
    "surface":   "rgba(255,255,255,0.03)",
    "border":    "rgba(255,255,255,0.06)",
    "primary":   "#6C63FF",
    "secondary": "#4ECDC4",
    "text":      "#FAFAFA",
    "muted":     "rgba(255,255,255,0.45)",
    "success":   "#00D4AA",
    "warning":   "#FFB547",
    "danger":    "#FF6B6B",
}

GLOBAL_CSS = """
<style>
/* ═══════════════════════════════════════════════════════════════════════════
   SkillSync — Premium Dark Glassmorphism Theme
   ═══════════════════════════════════════════════════════════════════════════ */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base Reset ───────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: linear-gradient(165deg, #0B0D14 0%, #0E1019 40%, #0D0F18 100%);
}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F1119 0%, #0C0E16 100%) !important;
    border-right: 1px solid rgba(108,99,255,0.08) !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.55);
}

/* Sidebar nav links */
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
    border-radius: 10px !important;
    padding: 8px 14px !important;
    margin: 2px 0 !important;
    transition: all 0.25s cubic-bezier(.4,0,.2,1) !important;
}

section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
    background: rgba(108,99,255,0.1) !important;
    transform: translateX(4px);
}

section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: rgba(108,99,255,0.12) !important;
    border-left: 3px solid #6C63FF !important;
}

/* ── Main Content ─────────────────────────────────────────────────────────── */
.main .block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #6C63FF 0%, #4ECDC4 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.8rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em;
    box-shadow: 0 4px 15px rgba(108,99,255,0.25) !important;
    transition: all 0.3s cubic-bezier(.4,0,.2,1) !important;
}

.stButton > button:hover {
    opacity: 0.92 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(108,99,255,0.35) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── File Uploader ────────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(108,99,255,0.3) !important;
    border-radius: 16px !important;
    padding: 14px !important;
    transition: border-color 0.3s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(108,99,255,0.6) !important;
}

/* ── Progress Bar ─────────────────────────────────────────────────────────── */
.stProgress > div > div {
    background: linear-gradient(90deg, #6C63FF, #4ECDC4) !important;
    border-radius: 20px !important;
}

/* ── Metrics ──────────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    transition: all 0.3s ease !important;
}

[data-testid="metric-container"]:hover {
    background: rgba(108,99,255,0.06) !important;
    border-color: rgba(108,99,255,0.15) !important;
    transform: translateY(-2px);
}

[data-testid="metric-container"] label {
    color: rgba(255,255,255,0.45) !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #FAFAFA !important;
    font-weight: 700 !important;
}

/* ── Selectbox / Inputs ───────────────────────────────────────────────────── */
.stSelectbox > div > div,
.stTextArea textarea,
.stTextInput input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #FAFAFA !important;
    transition: border-color 0.25s ease !important;
}

.stSelectbox > div > div:focus-within,
.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: rgba(108,99,255,0.5) !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.1) !important;
}

/* ── Expander ─────────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    color: #FAFAFA !important;
    font-weight: 500 !important;
}

/* ── Tabs ──────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.02);
    border-radius: 12px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: rgba(255,255,255,0.5) !important;
    padding: 8px 20px !important;
    font-weight: 500 !important;
    transition: all 0.25s ease !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(108,99,255,0.15) !important;
    color: #6C63FF !important;
    font-weight: 600 !important;
}

/* ── Divider ──────────────────────────────────────────────────────────────── */
hr {
    border-color: rgba(255,255,255,0.05) !important;
    margin: 24px 0 !important;
}

/* ── Alert Boxes ──────────────────────────────────────────────────────────── */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
}

[data-testid="stNotificationMessage"][data-type="info"] {
    background: rgba(108,99,255,0.08) !important;
    border-left: 4px solid #6C63FF !important;
}

[data-testid="stNotificationMessage"][data-type="success"] {
    background: rgba(0,212,170,0.08) !important;
    border-left: 4px solid #00D4AA !important;
}

[data-testid="stNotificationMessage"][data-type="warning"] {
    background: rgba(255,181,71,0.08) !important;
    border-left: 4px solid #FFB547 !important;
}

[data-testid="stNotificationMessage"][data-type="error"] {
    background: rgba(255,107,107,0.08) !important;
    border-left: 4px solid #FF6B6B !important;
}

/* ── Chat Messages ────────────────────────────────────────────────────────── */
.stChatMessage {
    background: rgba(108,99,255,0.04) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(108,99,255,0.08) !important;
    margin-bottom: 10px !important;
}

[data-testid="stChatInput"] {
    border-color: rgba(108,99,255,0.2) !important;
    border-radius: 14px !important;
}

/* ── Scrollbar ────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(108,99,255,0.3);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(108,99,255,0.5); }

/* ── Custom Glassmorphism Classes ─────────────────────────────────────────── */
.glass-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    transition: all 0.35s cubic-bezier(.4,0,.2,1);
}

.glass-card:hover {
    background: rgba(108,99,255,0.05);
    border-color: rgba(108,99,255,0.15);
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(108,99,255,0.12);
}

.gradient-text {
    background: linear-gradient(135deg, #6C63FF 0%, #4ECDC4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.glow-primary {
    box-shadow: 0 0 20px rgba(108,99,255,0.15);
}

.page-header {
    margin-bottom: 32px;
}

.page-header h1 {
    color: #FAFAFA;
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0 0 6px 0;
    letter-spacing: -0.02em;
}

.page-header p {
    color: rgba(255,255,255,0.45);
    font-size: 1rem;
    margin: 0;
    line-height: 1.6;
}

/* ── Animated Particles Background (subtle) ───────────────────────────────── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(circle at 15% 25%, rgba(108,99,255,0.04) 0%, transparent 50%),
        radial-gradient(circle at 85% 75%, rgba(78,205,196,0.03) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

/* ── Toggle Switch ────────────────────────────────────────────────────────── */
[data-testid="stCheckbox"] label span[data-testid="stCheckbox-label"] {
    color: rgba(255,255,255,0.7) !important;
}

/* ── Plotly Chart Backgrounds ─────────────────────────────────────────────── */
.js-plotly-plot .plotly .main-svg {
    border-radius: 14px;
}

</style>
"""


def inject_theme():
    """Call once at the top of each page to inject the full premium theme."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a premium page header with gradient icon."""
    icon_html = f'<span style="font-size:1.8rem;margin-right:10px;">{icon}</span>' if icon else ""
    st.markdown(
        f"""
        <div class="page-header">
          <h1>{icon_html}{title}</h1>
          {"" if not subtitle else f'<p>{subtitle}</p>'}
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand():
    """Render the premium sidebar brand header."""
    st.markdown(
        """
        <div style="text-align:center;padding:12px 0 24px 0;">
          <div style="font-size:2.4rem;margin-bottom:4px;">🎯</div>
          <h1 class="gradient-text" style="font-size:1.6rem;font-weight:800;
              margin:0;letter-spacing:-0.03em;">SkillSync</h1>
          <p style="color:rgba(255,255,255,0.35);font-size:0.72rem;
              margin:4px 0 0 0;text-transform:uppercase;letter-spacing:0.15em;
              font-weight:500;">AI Resume Analyzer</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
