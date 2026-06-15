"""
app/pages/03_skill_gap.py
Page 3 — Skill gap analysis: donut, priority bar, radar, skill table.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from app.components.theme import inject_theme, page_header

st.set_page_config(page_title="Skill Gap | SkillSync", page_icon="📊", layout="wide")
inject_theme()

page_header("Skill Gap Analysis", "See exactly which skills you have, which you're missing, and what to focus on.", icon="📊")

res = st.session_state.get("analysis_result")
if not res:
    st.warning("⚠️ No analysis found. Go to **Resume Analysis** first.")
    st.stop()

gap      = res.get("gap", {})
matched  = gap.get("matched", [])
missing  = gap.get("missing", [])
extra    = gap.get("extra_skills", [])
match_pct = gap.get("match_percentage", 0)
level    = gap.get("level", "")
job_role = res.get("gap",{}).get("job_role","") or st.session_state.get("job_role","")

resume_skills_raw = [s["skill"] for s in res.get("resume_skills", [])]
jd_skills_raw     = [m["required"] for m in matched] + [m["skill"] for m in missing]
skill_exps = res.get("explanations",{}).get("skills",{})

from app.components.charts import skill_match_donut, gap_priority_bar, skills_radar
from app.components.cards  import section_header, priority_badge, skill_badge, metric_card

# ── Row 1: Match summary ───────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
level_color = {"Excellent":"#00D4AA","Good":"#4ECDC4","Fair":"#FFB547","Needs Work":"#FF6B6B"}.get(level,"#6C63FF")
with c1: metric_card("Match %",        f"{match_pct:.1f}%", color="#6C63FF")
with c2: metric_card("Match Level",    level, color=level_color)
with c3: metric_card("Skills Matched", str(gap.get("total_matched", len(matched))), color="#00D4AA")
with c4: metric_card("Skills Missing", str(gap.get("total_missing", len(missing))), color="#FF6B6B")

st.markdown("---")

# ── Row 2: Donut + Radar ───────────────────────────────────────────────────────
col_donut, col_radar = st.columns(2, gap="large")
with col_donut:
    section_header("📈 Skill Coverage", "Matched vs Missing")
    st.plotly_chart(skill_match_donut(len(matched), len(missing)), use_container_width=True)

with col_radar:
    section_header("🕸️ Skill Profile Radar", "Your skills vs job requirements by category")
    st.plotly_chart(skills_radar(resume_skills_raw, jd_skills_raw), use_container_width=True)

st.markdown("---")

# ── Row 3: Priority bar + Missing table ───────────────────────────────────────
col_bar, col_table = st.columns([1, 1.4], gap="large")

with col_bar:
    section_header("🚦 Missing Skills by Priority")
    if missing:
        st.plotly_chart(gap_priority_bar(missing), use_container_width=True)
    else:
        st.success("🎉 No missing skills — perfect match!")

with col_table:
    section_header("📋 Skill Gap Details")
    if missing:
        for m in missing:
            skill    = m["skill"]
            priority = m.get("priority","Medium")
            ltime    = m.get("learning_time","2–4 weeks")
            exp_text = skill_exps.get(skill,"")

            p_color = {"High":"#FF6B6B","Medium":"#FFB547","Low":"#00D4AA"}.get(priority,"#6C63FF")
            st.markdown(
                f"""
                <div class="glass-card" style="border-left:3px solid {p_color};
                            padding:16px 20px;margin-bottom:12px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#FAFAFA;font-weight:600;font-size:0.95rem;">{skill.title()}</span>
                    <div>
                      <span style="background:rgba(0,0,0,.3);border:1px solid {p_color};
                                   color:{p_color};border-radius:10px;padding:2px 10px;
                                   font-size:.72rem;font-weight:600;letter-spacing:0.02em;">{priority.upper()}</span>
                      &nbsp;
                      <span style="color:rgba(255,255,255,.4);font-size:.78rem;font-weight:500;">⏱ {ltime}</span>
                    </div>
                  </div>
                  {"" if not exp_text else f'<p style="color:rgba(255,255,255,.55);font-size:.82rem;margin:8px 0 0 0;line-height:1.5;">{exp_text}</p>'}
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("---")

# ── Row 4: Your existing skills ───────────────────────────────────────────────
section_header("✅ Your Skills", f"{len(resume_skills_raw)} skills detected in your resume")
if resume_skills_raw:
    badges_html = " ".join(skill_badge(s, "matched") for s in resume_skills_raw[:40])
    st.markdown(badges_html, unsafe_allow_html=True)

st.info("👉 **Next:** Check **Recommendations** for free courses to fill your gaps.")
