"""
app/pages/01_resume_analysis.py
Page 1 — Upload resume, pick job role, run full pipeline.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import uuid
import pandas as pd
import streamlit as st
from app.components.theme import inject_theme, page_header

st.set_page_config(page_title="Resume Analysis | SkillSync", page_icon="📄", layout="wide")
inject_theme()

# ── Init session state ─────────────────────────────────────────────────────────
for key in ("analysis_result","job_role","jd_text","session_id"):
    if key not in st.session_state:
        st.session_state[key] = None
if not st.session_state["session_id"]:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]

# ── Load job roles list ────────────────────────────────────────────────────────
@st.cache_data
def load_job_roles():
    p = Path(__file__).parent.parent.parent / "data" / "raw" / "job_roles.csv"
    if p.exists():
        df = pd.read_csv(p)
        return df["job_role"].tolist()
    return ["Data Scientist","Software Engineer","Data Analyst","ML Engineer",
            "Web Developer","DevOps Engineer","NLP Engineer","Business Analyst"]

@st.cache_data
def get_jd_skills(role: str):
    p = Path(__file__).parent.parent.parent / "data" / "raw" / "job_roles.csv"
    if p.exists():
        df = pd.read_csv(p)
        row = df[df["job_role"] == role]
        if not row.empty:
            return [s.strip() for s in row.iloc[0]["required_skills"].split(",")]
    return []

# ── Header ─────────────────────────────────────────────────────────────────────
page_header("Resume Analysis", "Upload your resume and select a target job role to start the AI-powered analysis.", icon="📄")

# ── Layout: Upload + Config ────────────────────────────────────────────────────
col_left, col_right = st.columns([1.1, 1], gap="large")

with col_left:
    st.markdown("""
    <div class="glass-card" style="padding:28px 24px;text-align:center;
                min-height:220px;display:flex;flex-direction:column;
                align-items:center;justify-content:center;
                border:2px dashed rgba(108,99,255,0.25);">
      <div style="font-size:2.5rem;margin-bottom:12px;">📎</div>
      <p style="color:#FAFAFA;font-weight:600;margin:0 0 6px 0;">Upload Resume</p>
      <p style="color:rgba(255,255,255,0.35);font-size:0.8rem;margin:0;">
        Supports PDF, DOCX, and DOC formats
      </p>
    </div>
    """, unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Drag & drop or click to upload",
        type=["pdf","docx","doc"],
        label_visibility="collapsed",
    )
    if uploaded:
        ftype = uploaded.name.rsplit(".",1)[-1]
        st.success(f"✅ **{uploaded.name}** ({uploaded.size/1024:.1f} KB) — ready for analysis")

with col_right:
    st.markdown("""
    <div style="margin-bottom:20px;">
      <p style="color:#FAFAFA;font-weight:600;font-size:0.95rem;margin:0 0 8px 0;">
        🎯 Target Job Role
      </p>
    </div>
    """, unsafe_allow_html=True)
    roles = load_job_roles()
    job_role = st.selectbox("Select role", roles, label_visibility="collapsed")
    st.session_state["job_role"] = job_role

    st.markdown("""
    <div style="margin:20px 0 8px 0;">
      <p style="color:#FAFAFA;font-weight:600;font-size:0.95rem;margin:0 0 4px 0;">
        📝 Job Description
      </p>
      <p style="color:rgba(255,255,255,0.35);font-size:0.78rem;margin:0;">
        Optional but recommended for better ATS accuracy
      </p>
    </div>
    """, unsafe_allow_html=True)
    jd_text = st.text_area(
        "Paste the job description here",
        height=160,
        placeholder="Paste the full job description for better ATS accuracy…",
        label_visibility="collapsed",
    )
    st.session_state["jd_text"] = jd_text

# ── Advanced settings ──────────────────────────────────────────────────────────
with st.expander("⚙️ Advanced Settings"):
    use_semantic = st.toggle("Use BERT semantic matching (slower, more accurate)", value=True)
    st.caption("Disable for faster results on low-RAM devices.")

# ── Analyse button ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([2,1,2])
with btn_col:
    analyse_clicked = st.button("🚀 Analyse Resume", use_container_width=True)

if analyse_clicked:
    if not uploaded:
        st.error("⚠️ Please upload a resume file first.")
    else:
        jd_skills = get_jd_skills(job_role)
        if not jd_text.strip():
            jd_text = " ".join(jd_skills)   # fallback JD text from role data

        progress = st.progress(0, text="Parsing resume…")
        status   = st.empty()

        try:
            from modules.pipeline import run_analysis

            progress.progress(10, text="📄 Parsing resume…")
            file_bytes = uploaded.getvalue()
            file_type  = uploaded.name.rsplit(".",1)[-1]

            progress.progress(30, text="🔍 Extracting skills…")
            progress.progress(55, text="🎯 Computing ATS score…")
            progress.progress(75, text="📊 Analysing skill gap…")
            progress.progress(88, text="📚 Fetching recommendations…")

            result = run_analysis(
                file_bytes, file_type, job_role, jd_text,
                jd_skills=jd_skills,
                use_semantic=use_semantic,
                session_id=st.session_state["session_id"],
            )

            progress.progress(100, text="✅ Analysis complete!")

            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.session_state["analysis_result"] = result
                status.success("✅ Analysis complete! Navigate to the other pages to explore your results.")

        except Exception as e:
            progress.empty()
            st.exception(e)

# ── Show quick summary if result exists ───────────────────────────────────────
if st.session_state.get("analysis_result"):
    res = st.session_state["analysis_result"]
    st.markdown("---")

    st.markdown("""
    <div style="margin:16px 0 20px 0;">
      <h2 style="color:#FAFAFA;font-size:1.4rem;font-weight:700;margin:0;
                 letter-spacing:-0.02em;">✨ Quick Summary</h2>
    </div>
    """, unsafe_allow_html=True)

    from app.components.cards import metric_card
    m1, m2, m3, m4 = st.columns(4)
    with m1: metric_card("ATS Score",      f"{res['ats'].get('ats_score',0):.1f}/100", color="#6C63FF")
    with m2: metric_card("Skill Match",    f"{res['gap'].get('match_percentage',0):.1f}%", color="#4ECDC4")
    with m3: metric_card("Skills Found",   str(len(res.get("resume_skills",[]))), color="#00D4AA")
    with m4: metric_card("Missing Skills", str(res["gap"].get("total_missing",0)), color="#FF6B6B")

    parsed = res.get("parsed",{})
    contact = parsed.get("contact_info",{})
    if contact:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Detected Contact Info:**")
        info_cols = st.columns(len(contact))
        for col, (k,v) in zip(info_cols, contact.items()):
            col.markdown(f"**{k.title()}:** {v}")

    st.markdown("**Detected Sections:**")
    secs = parsed.get("sections",{})
    sec_cols = st.columns(4)
    for i,(sec,content) in enumerate(secs.items()):
        if content.strip():
            sec_cols[i%4].success(f"✅ {sec.title()}")

    st.info("👉 **Next:** Go to **ATS Score** in the sidebar to see your full score breakdown.")
