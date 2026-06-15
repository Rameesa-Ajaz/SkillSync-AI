"""
app/main.py  —  SkillSync entry point
Run:  streamlit run app/main.py
"""
import sys
from pathlib import Path
# Make project root importable
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from app.components.theme import inject_theme, page_header, sidebar_brand

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkillSync | AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject premium theme ──────────────────────────────────────────────────────
inject_theme()

# ── Session state initialisation ──────────────────────────────────────────────
for key in ("analysis_result", "job_role", "jd_text"):
    if key not in st.session_state:
        st.session_state[key] = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_brand()
    st.markdown("---")

    st.markdown(
        '<p style="color:rgba(255,255,255,0.35);font-size:0.7rem;'
        'text-transform:uppercase;letter-spacing:0.12em;font-weight:600;'
        'margin-bottom:8px;">Navigation</p>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/01_resume_analysis.py",  label="📄 Resume Analysis",    icon="📄")
    st.page_link("pages/02_job_matching.py",      label="🎯 ATS Score",          icon="🎯")
    st.page_link("pages/03_skill_gap.py",         label="📊 Skill Gap",          icon="📊")
    st.page_link("pages/04_recommendations.py",   label="📚 Recommendations",    icon="📚")
    st.page_link("pages/05_career_prediction.py", label="🚀 Career Prediction",  icon="🚀")
    st.page_link("pages/06_ai_assistant.py",     label="💬 AI Assistant",       icon="💬")

    st.markdown("---")
    if st.session_state.get("analysis_result"):
        res = st.session_state["analysis_result"]
        ats = res.get("ats", {}).get("ats_score", 0)
        gap = res.get("gap", {}).get("match_percentage", 0)

        st.markdown(
            '<p style="color:rgba(255,255,255,0.35);font-size:0.7rem;'
            'text-transform:uppercase;letter-spacing:0.12em;font-weight:600;'
            'margin-bottom:8px;">Last Analysis</p>',
            unsafe_allow_html=True,
        )
        st.metric("ATS Score",    f"{ats:.1f}/100")
        st.metric("Skill Match",  f"{gap:.1f}%")
        st.metric("Role",         st.session_state.get("job_role","—"))

# ── Hero section ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:60px 20px 30px 20px;">
  <div style="font-size:3.2rem;margin-bottom:12px;">🎯</div>
  <h1 style="font-size:3rem;font-weight:800;letter-spacing:-0.03em;
             background:linear-gradient(135deg,#6C63FF 0%,#4ECDC4 50%,#00D4AA 100%);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
             margin:0 0 16px 0;line-height:1.1;">
    SkillSync AI
  </h1>
  <p style="color:rgba(255,255,255,0.5);font-size:1.1rem;max-width:550px;
            margin:0 auto 12px auto;line-height:1.7;">
    Upload your resume · Get your ATS score · Discover skill gaps ·
    Find free courses · Predict your ideal career path
  </p>
  <div style="width:60px;height:3px;background:linear-gradient(90deg,#6C63FF,#4ECDC4);
              margin:24px auto 0 auto;border-radius:2px;"></div>
</div>
""", unsafe_allow_html=True)

# ── Feature cards ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

cols = st.columns(5, gap="medium")
features = [
    ("📄", "Resume Parser",      "PDF & DOCX extraction with NLP",    "#6C63FF"),
    ("🎯", "ATS Scoring",        "Triple-engine ensemble AI",          "#4ECDC4"),
    ("📊", "Gap Analysis",        "Priority-ranked skill mapping",     "#00D4AA"),
    ("📚", "Recommendations",    "Curated free learning paths",       "#FFB547"),
    ("🚀", "Career Prediction",  "ML ensemble career matching",       "#FF6B6B"),
]
for col, (icon, title, sub, accent) in zip(cols, features):
    with col:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;min-height:180px;
                    display:flex;flex-direction:column;align-items:center;
                    justify-content:center;border-top:2px solid {accent};">
          <div style="font-size:2rem;margin-bottom:12px;
                      background:rgba(108,99,255,0.08);border-radius:14px;
                      width:52px;height:52px;display:flex;align-items:center;
                      justify-content:center;margin-left:auto;margin-right:auto;">
            {icon}
          </div>
          <p style="color:#FAFAFA;font-weight:700;margin:0 0 6px 0;
                    font-size:0.88rem;letter-spacing:-0.01em;">{title}</p>
          <p style="color:rgba(255,255,255,0.4);font-size:0.73rem;
                    margin:0;line-height:1.5;">{sub}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Getting started prompt ────────────────────────────────────────────────────
st.markdown("""
<div class="glass-card" style="text-align:center;padding:28px 32px;
            border:1px solid rgba(108,99,255,0.15);">
  <p style="color:rgba(255,255,255,0.7);font-size:0.95rem;margin:0;">
    👈 <strong>Get started:</strong> Use the sidebar or go directly to
    <strong>Resume Analysis</strong> to upload your resume.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:40px 0 20px 0;">
  <p style="color:rgba(255,255,255,0.2);font-size:0.72rem;margin:0;">
    SkillSync AI · Powered by BERT, SpaCy & Scikit-learn
  </p>
</div>
""", unsafe_allow_html=True)
