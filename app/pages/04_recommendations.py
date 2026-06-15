"""
app/pages/04_recommendations.py
Page 4 — Course and resource recommendations for missing skills.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from app.components.theme import inject_theme, page_header

st.set_page_config(page_title="Recommendations | SkillSync", page_icon="📚", layout="wide")
inject_theme()

page_header("Learning Recommendations", "Curated free and paid courses to close your skill gaps — sorted by relevance.", icon="📚")

res = st.session_state.get("analysis_result")
if not res:
    st.warning("⚠️ No analysis found. Go to **Resume Analysis** first.")
    st.stop()

recs    = res.get("recommendations", [])
missing = res.get("gap", {}).get("missing", [])
job_role = st.session_state.get("job_role", "your target role")
skill_exps = res.get("explanations", {}).get("skills", {})

from app.components.cards import course_card, section_header, metric_card

# ── Filters ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="glass-card" style="padding:16px 20px;margin-bottom:24px;">
  <p style="color:rgba(255,255,255,0.45);font-size:0.8rem;margin:0 0 10px 0;text-transform:uppercase;letter-spacing:0.05em;font-weight:600;">🔍 Filter Recommendations</p>
</div>
""", unsafe_allow_html=True)

# Place toggle and selectboxes
col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
with col_f1:
    free_only = st.toggle("🆓 Free courses only", value=False)
with col_f2:
    priority_filter = st.selectbox("Filter by Priority", ["All","High","Medium","Low"])
with col_f3:
    platform_options = ["All"] + sorted({r.get("platform","") for r in recs if r.get("platform")})
    platform_filter  = st.selectbox("Filter by Platform", platform_options)

# ── Apply filters ──────────────────────────────────────────────────────────────
filtered = recs
if free_only:
    filtered = [r for r in filtered if r.get("is_free")]
if platform_filter != "All":
    filtered = [r for r in filtered if r.get("platform") == platform_filter]

# Filter by priority of the skill
if priority_filter != "All":
    priority_skills = {m["skill"].lower() for m in missing if m.get("priority") == priority_filter}
    filtered = [r for r in filtered if r.get("skill","").lower() in priority_skills]

# ── Stats row ──────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
with m1: metric_card("Total Recs", str(len(recs)), color="#6C63FF")
with m2: metric_card("Free Courses", str(sum(1 for r in recs if r.get("is_free"))), color="#00D4AA")
with m3: metric_card("Skills Covered", str(len({r.get("skill") for r in recs})), color="#4ECDC4")
with m4: metric_card("Showing Now", str(len(filtered)), color="#FFB547")

st.markdown("---")

# ── No results ─────────────────────────────────────────────────────────────────
if not filtered:
    if not recs:
        # Regenerate on demand
        st.info("No recommendations found. Click below to generate them.")
        if st.button("🔄 Generate Recommendations"):
            with st.spinner("Fetching courses…"):
                try:
                    from modules.recommender import get_recommendations
                    missing_skills = [m["skill"] for m in missing]
                    resume_skills  = [s["skill"] for s in res.get("resume_skills", [])]
                    new_recs = get_recommendations(missing_skills, resume_skills)
                    res["recommendations"] = new_recs
                    st.session_state["analysis_result"] = res
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.warning("No results match the selected filters. Try adjusting the filters above.")
    st.stop()

# ── Group by missing skill priority ───────────────────────────────────────────
priority_order = {"High": 0, "Medium": 1, "Low": 2}
missing_by_skill = {m["skill"]: m for m in missing}

# Group recs by skill
from collections import defaultdict
recs_by_skill = defaultdict(list)
for r in filtered:
    recs_by_skill[r.get("skill","Other")].append(r)

# Sort skills by priority
sorted_skills = sorted(
    recs_by_skill.keys(),
    key=lambda s: priority_order.get(missing_by_skill.get(s, {}).get("priority","Medium"), 1)
)

for skill in sorted_skills:
    skill_recs = recs_by_skill[skill]
    skill_meta = missing_by_skill.get(skill, {})
    priority   = skill_meta.get("priority","Medium")
    ltime      = skill_meta.get("learning_time","")
    p_color    = {"High":"#FF6B6B","Medium":"#FFB547","Low":"#00D4AA"}.get(priority,"#6C63FF")

    st.markdown(
        f"""
        <div style="margin:24px 0 8px 0;display:flex;align-items:center;gap:12px;">
          <h3 style="color:#FAFAFA;font-size:1.1rem;font-weight:700;margin:0;">
            🎯 {skill.title()}
          </h3>
          <span style="background:rgba(0,0,0,.3);border:1px solid {p_color};
                       color:{p_color};border-radius:10px;padding:2px 10px;
                       font-size:.72rem;font-weight:600;letter-spacing:0.02em;">{priority.upper()}</span>
          {"" if not ltime else f'<span style="color:rgba(255,255,255,.4);font-size:.78rem;font-weight:500;">⏱ {ltime}</span>'}
        </div>
        """,
        unsafe_allow_html=True,
    )

    exp = skill_exps.get(skill, "")
    if exp:
        st.markdown(
            f'<p style="color:rgba(255,255,255,.55);font-size:.84rem;margin:0 0 12px 0;line-height:1.5;">{exp}</p>',
            unsafe_allow_html=True,
        )

    cols = st.columns(min(len(skill_recs), 2))
    for col, rec in zip(cols, skill_recs[:2]):
        with col:
            course_card(rec)

st.markdown("---")
st.info("👉 **Next:** Check **Career Prediction** to see which career paths suit your profile best.")
