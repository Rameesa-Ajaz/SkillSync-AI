"""
app/pages/02_job_matching.py
Page 2 — ATS score gauge, breakdown charts, matched & missing keywords.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from app.components.theme import inject_theme, page_header

st.set_page_config(page_title="ATS Score | SkillSync", page_icon="🎯", layout="wide")
inject_theme()

page_header("ATS Score Dashboard", "How well does your resume match the target job?", icon="🎯")

res = st.session_state.get("analysis_result")
if not res:
    st.warning("⚠️ No analysis found. Please go to **Resume Analysis** and upload your resume first.")
    st.stop()

ats     = res.get("ats", {})
score   = ats.get("ats_score", 0)
grade   = ats.get("grade", "—")
breakdown = ats.get("breakdown", {})
matched_kws = ats.get("matched_keywords", [])
missing_skills = ats.get("missing_skills", [])
matched_skills = ats.get("matched_skills", [])
exp     = res.get("explanations",{}).get("ats","")

# ── Row 1: Gauge + breakdown ──────────────────────────────────────────────────
from app.components.charts import ats_gauge, ats_breakdown_bar
from app.components.cards  import metric_card, section_header

col_gauge, col_bar = st.columns([1, 1.3], gap="large")
with col_gauge:
    st.plotly_chart(ats_gauge(score, grade), use_container_width=True)
    if exp:
        st.markdown(f"""
        <div class="glass-card" style="margin-top:10px;padding:16px 20px;">
          <p style="color:rgba(255,255,255,0.65);font-size:.85rem;margin:0;line-height:1.6;">{exp}</p>
        </div>
        """, unsafe_allow_html=True)

with col_bar:
    st.plotly_chart(ats_breakdown_bar(breakdown), use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1: metric_card("BERT Semantic",  f"{breakdown.get('bert_semantic',0):.1f}%",  color="#6C63FF")
    with m2: metric_card("TF-IDF Match",   f"{breakdown.get('tfidf_keywords',0):.1f}%", color="#4ECDC4")
    with m3: metric_card("Direct Skills",  f"{breakdown.get('direct_match',0):.1f}%",   color="#FFB547")

st.markdown("---")

# ── Row 2: Keywords ───────────────────────────────────────────────────────────
col_match, col_miss = st.columns(2, gap="large")

with col_match:
    section_header("✅ Matched Keywords", f"{len(matched_kws)} keywords found in your resume")
    if matched_kws:
        badges = " ".join(
            f'<span style="background:rgba(0,212,170,.1);border:1px solid #00D4AA;'
            f'color:#00D4AA;border-radius:20px;padding:4px 14px;'
            f'font-size:.8rem;margin:3px;display:inline-block;font-weight:500;">{kw}</span>'
            for kw in matched_kws
        )
        st.markdown(badges, unsafe_allow_html=True)
    else:
        st.info("No matching keywords detected. Try pasting the job description on the Analysis page.")

with col_miss:
    section_header("❌ Missing Keywords", f"{len(missing_skills)} skills not found")
    if missing_skills:
        badges = " ".join(
            f'<span style="background:rgba(255,107,107,.1);border:1px solid #FF6B6B;'
            f'color:#FF6B6B;border-radius:20px;padding:4px 14px;'
            f'font-size:.8rem;margin:3px;display:inline-block;font-weight:500;">{s}</span>'
            for s in missing_skills[:20]
        )
        st.markdown(badges, unsafe_allow_html=True)
    else:
        st.success("No missing skills detected — great match!")

st.markdown("---")

# ── Row 3: Matched skills ──────────────────────────────────────────────────────
if matched_skills:
    section_header("🎯 Matched Skills", "Skills present in both your resume and the job description")
    badges = " ".join(
        f'<span style="background:rgba(78,205,196,.08);border:1px solid #4ECDC4;'
        f'color:#4ECDC4;border-radius:20px;padding:4px 14px;'
        f'font-size:.8rem;margin:3px;display:inline-block;font-weight:500;">{s.title()}</span>'
        for s in matched_skills
    )
    st.markdown(badges, unsafe_allow_html=True)

st.info("👉 **Next:** Check **Skill Gap** page for a priority-ranked view of what to learn.")
