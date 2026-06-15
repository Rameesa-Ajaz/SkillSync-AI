"""
app/pages/05_career_prediction.py
Page 5 — ML-based career path predictions with confidence bars and gap comparison.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from app.components.theme import inject_theme, page_header

st.set_page_config(page_title="Career Prediction | SkillSync", page_icon="🚀", layout="wide")
inject_theme()

page_header("Career Prediction", "AI-powered career path recommendations based on your unique skill profile.", icon="🚀")

res = st.session_state.get("analysis_result")
if not res:
    st.warning("⚠️ No analysis found. Go to **Resume Analysis** first.")
    st.stop()

career_preds  = res.get("career", [])
resume_skills = [s["skill"] for s in res.get("resume_skills", [])]

from app.components.charts import career_confidence_bar
from app.components.cards  import career_card, section_header, metric_card
from modules.llm_explainer import explain_career

# ── Confidence chart ───────────────────────────────────────────────────────────
if career_preds:
    col_chart, col_top = st.columns([1.4, 1], gap="large")

    with col_chart:
        section_header("📊 Career Match Confidence", "Top 5 predicted career paths")
        st.plotly_chart(career_confidence_bar(career_preds), use_container_width=True)

    with col_top:
        section_header("🏆 Your Top Match")
        top = career_preds[0]
        conf  = top.get("confidence", 0)
        role  = top.get("role","")
        color = "#00D4AA" if conf >= 60 else "#FFB547" if conf >= 35 else "#FF6B6B"
        st.markdown(
            f"""
            <div class="glass-card" style="border-left:4px solid #6C63FF;padding:24px;text-align:center;">
              <p style="font-size:2.5rem;margin:0 0 10px 0;">🎯</p>
              <h2 style="color:#FAFAFA;font-size:1.4rem;font-weight:700;margin:0 0 6px 0;letter-spacing:-0.02em;">{role}</h2>
              <p style="color:{color};font-size:2.2rem;font-weight:800;margin:0;letter-spacing:-0.03em;">{conf:.1f}%</p>
              <p style="color:rgba(255,255,255,.35);font-size:.78rem;margin:4px 0 0 0;text-transform:uppercase;letter-spacing:0.05em;font-weight:600;">Match Confidence</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        exp = explain_career(role, conf, top.get("key_matching_skills",[]))
        st.markdown(
            f"""
            <div class="glass-card" style="margin-top:16px;padding:16px 20px;">
              <p style="color:rgba(255,255,255,.6);font-size:.85rem;margin:0;line-height:1.6;">{exp}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── All career cards ────────────────────────────────────────────────────────
    section_header("🗺️ All Predicted Career Paths")
    cols = st.columns(2)
    for i, pred in enumerate(career_preds):
        with cols[i % 2]:
            career_card(pred, rank=i+1)

    st.markdown("---")

    # ── Career gap drill-down ──────────────────────────────────────────────────
    section_header("🔍 Career Gap Drill-Down",
                   "Pick a career path to see the exact skills you need for it")

    selected_role = st.selectbox(
        "Select a career to analyse",
        [p["role"] for p in career_preds],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if selected_role:
        import pandas as pd
        roles_path = Path(__file__).parent.parent.parent / "data" / "raw" / "job_roles.csv"
        if roles_path.exists():
            df = pd.read_csv(roles_path)
            row = df[df["job_role"] == selected_role]
            if not row.empty:
                needed = [s.strip() for s in row.iloc[0]["required_skills"].split(",")]
                have   = {s.lower() for s in resume_skills}
                matched_s = [s for s in needed if s.lower() in have]
                missing_s = [s for s in needed if s.lower() not in have]

                c1, c2 = st.columns(2, gap="large")
                with c1:
                    st.markdown(
                        f"""
                        <div class="glass-card" style="border-left:3px solid #00D4AA;padding:20px;">
                          <h4 style="color:#00D4AA;margin:0 0 12px 0;font-size:1rem;font-weight:600;">✅ Skills You Have ({len(matched_s)})</h4>
                        """,
                        unsafe_allow_html=True,
                    )
                    for s in matched_s:
                        st.markdown(f'<p style="color:rgba(255,255,255,0.75);margin:4px 0;font-size:0.88rem;"><span style="color:#00D4AA;font-weight:bold;">✓</span> {s.title()}</p>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with c2:
                    st.markdown(
                        f"""
                        <div class="glass-card" style="border-left:3px solid #FF6B6B;padding:20px;">
                          <h4 style="color:#FF6B6B;margin:0 0 12px 0;font-size:1rem;font-weight:600;">❌ Skills to Learn ({len(missing_s)})</h4>
                        """,
                        unsafe_allow_html=True,
                    )
                    for s in missing_s:
                        st.markdown(f'<p style="color:rgba(255,255,255,0.75);margin:4px 0;font-size:0.88rem;"><span style="color:#FF6B6B;font-weight:bold;">✗</span> {s.title()}</p>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("No career predictions available. Please run the analysis from the Resume Analysis page.")
    if st.button("🔄 Generate Predictions"):
        with st.spinner("Running career predictor…"):
            try:
                from modules.career_predictor import predict_career
                preds = predict_career(resume_skills)
                res["career"] = preds
                st.session_state["analysis_result"] = res
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.success("✅ **Analysis complete!** Use the sidebar to revisit any section.")
