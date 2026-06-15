"""
app/components/charts.py
Reusable Plotly chart builders for SkillSync UI.
Premium dark theme with transparent backgrounds to blend with glassmorphism.
"""
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List


COLORS = {
    "primary":  "#6C63FF",
    "success":  "#00D4AA",
    "warning":  "#FFB547",
    "danger":   "#FF6B6B",
    "info":     "#4ECDC4",
    "bg":       "rgba(0,0,0,0)",       # Transparent to blend with glassmorphism
    "surface":  "rgba(255,255,255,0.03)", # Glassmorphism surface
    "text":     "#FAFAFA",
    "muted":    "rgba(255,255,255,0.45)",
}

PRIORITY_COLOR = {"High": "#FF6B6B", "Medium": "#FFB547", "Low": "#00D4AA"}


def ats_gauge(score: float, grade: str) -> go.Figure:
    """Animated gauge chart for ATS score."""
    color = (
        COLORS["success"] if score >= 75 else
        COLORS["warning"] if score >= 50 else
        COLORS["danger"]
    )
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={"text": f"ATS Score  |  Grade {grade}", "font": {"color": COLORS["text"], "size": 18, "family": "Inter"}},
        delta={"reference": 70, "suffix": " vs target", "font": {"family": "Inter"}},
        gauge={
            "axis":  {"range": [0, 100], "tickcolor": COLORS["muted"], "tickfont": {"family": "Inter"}},
            "bar":   {"color": color, "thickness": 0.25},
            "bgcolor": "rgba(255,255,255,0.02)",
            "bordercolor": "rgba(255,255,255,0.08)",
            "steps": [
                {"range": [0,  50], "color": "rgba(255,255,255,0.01)"},
                {"range": [50, 75], "color": "rgba(255,255,255,0.03)"},
                {"range": [75,100], "color": "rgba(255,255,255,0.05)"},
            ],
            "threshold": {"line": {"color": COLORS["primary"], "width": 3}, "value": 70},
        },
        number={"suffix": "/100", "font": {"color": color, "size": 42, "weight": "bold", "family": "Inter"}},
    ))
    fig.update_layout(
        paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["bg"],
        height=280, margin=dict(t=60, b=10, l=20, r=20),
        font={"color": COLORS["text"], "family": "Inter"},
    )
    return fig


def ats_breakdown_bar(breakdown: Dict[str, float]) -> go.Figure:
    """Horizontal bar showing BERT / TF-IDF / Direct match contributions."""
    labels = ["BERT Semantic", "TF-IDF Keywords", "Direct Skill Match"]
    keys   = ["bert_semantic", "tfidf_keywords", "direct_match"]
    values = [breakdown.get(k, 0) for k in keys]
    bar_colors = [COLORS["primary"], COLORS["info"], COLORS["success"]]

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(
            color=bar_colors,
            line=dict(color="rgba(255,255,255,0.1)", width=1)
        ),
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        textfont={"color": COLORS["text"], "family": "Inter", "weight": "bold"},
    ))
    fig.update_layout(
        title={"text": "Score Breakdown", "font": {"color": COLORS["text"], "size": 16, "family": "Inter"}},
        paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["bg"],
        xaxis={
            "range": [0, 115],
            "gridcolor": "rgba(255,255,255,0.05)",
            "color": COLORS["muted"],
            "tickfont": {"family": "Inter"}
        },
        yaxis={
            "color": COLORS["text"],
            "tickfont": {"family": "Inter"}
        },
        height=220, margin=dict(t=40, b=10, l=10, r=20),
        font={"color": COLORS["text"], "family": "Inter"},
    )
    return fig


def skill_match_donut(matched: int, missing: int) -> go.Figure:
    """Donut chart showing matched vs missing skills."""
    fig = go.Figure(go.Pie(
        labels=["Matched", "Missing"],
        values=[matched, missing],
        hole=0.65,
        marker=dict(
            colors=[COLORS["success"], COLORS["danger"]],
            line=dict(color="rgba(11,13,20,1)", width=2)
        ),
        textinfo="percent",
        textfont={"color": COLORS["text"], "size": 13, "family": "Inter", "weight": "bold"},
    ))
    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        annotations=[{"text": f"{matched}/{matched+missing}<br><span style='font-size:0.75rem;color:rgba(255,255,255,0.4)'>skills</span>", "x": 0.5, "y": 0.5,
                      "font": {"size": 22, "color": COLORS["text"], "family": "Inter", "weight": "bold"}, "showarrow": False}],
        showlegend=True,
        legend={"font": {"color": COLORS["muted"], "family": "Inter"}},
        height=300, margin=dict(t=20, b=20, l=20, r=20),
    )
    return fig


def gap_priority_bar(missing: List[Dict]) -> go.Figure:
    """Horizontal bar of missing skills coloured by priority."""
    if not missing:
        return go.Figure()
    # Sort so high priority is at the top of the horizontal bar chart
    sorted_missing = sorted(missing, key=lambda x: {"High": 3, "Medium": 2, "Low": 1}.get(x.get("priority", "Medium"), 2))
    skills   = [m["skill"].title() for m in sorted_missing[:15]]
    priority = [m.get("priority", "Medium") for m in sorted_missing[:15]]
    colors   = [PRIORITY_COLOR.get(p, COLORS["info"]) for p in priority]

    fig = go.Figure(go.Bar(
        x=[1] * len(skills), y=skills, orientation="h",
        marker=dict(
            color=colors,
            line=dict(color="rgba(255,255,255,0.1)", width=1)
        ),
        text=priority, textposition="inside",
        textfont={"color": "#111111", "size": 11, "family": "Inter", "weight": "bold"},
    ))
    fig.update_layout(
        title={"text": "Missing Skills by Priority", "font": {"color": COLORS["text"], "size": 16, "family": "Inter"}},
        paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["bg"],
        xaxis={
            "showticklabels": False,
            "gridcolor": "rgba(255,255,255,0.05)",
            "visible": False
        },
        yaxis={
            "color": COLORS["text"],
            "tickfont": {"family": "Inter", "size": 11}
        },
        height=max(300, len(skills) * 32 + 60),
        margin=dict(t=40, b=10, l=10, r=10),
        font={"color": COLORS["text"], "family": "Inter"},
    )
    return fig


def career_confidence_bar(predictions: List[Dict]) -> go.Figure:
    """Horizontal bar of career predictions with confidence."""
    if not predictions:
        return go.Figure()
    # reverse order so highest is on top
    sorted_preds = sorted(predictions, key=lambda x: x.get("confidence", 0))
    roles = [p["role"] for p in sorted_preds]
    confs = [p["confidence"] for p in sorted_preds]

    fig = go.Figure(go.Bar(
        x=confs, y=roles, orientation="h",
        marker=dict(
            color=confs,
            colorscale=[[0, COLORS["danger"]], [0.5, COLORS["warning"]], [1, COLORS["success"]]],
            showscale=False,
            line=dict(color="rgba(255,255,255,0.1)", width=1)
        ),
        text=[f"{c:.1f}%" for c in confs],
        textposition="outside",
        textfont={"color": COLORS["text"], "family": "Inter", "weight": "bold"},
    ))
    fig.update_layout(
        title={"text": "Career Path Predictions", "font": {"color": COLORS["text"], "size": 16, "family": "Inter"}},
        paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["bg"],
        xaxis={
            "range": [0, 115],
            "gridcolor": "rgba(255,255,255,0.05)",
            "color": COLORS["muted"],
            "tickfont": {"family": "Inter"}
        },
        yaxis={
            "color": COLORS["text"],
            "tickfont": {"family": "Inter"}
        },
        height=300, margin=dict(t=40, b=10, l=10, r=20),
        font={"color": COLORS["text"], "family": "Inter"},
    )
    return fig


def skills_radar(student_skills: List[str], required_skills: List[str], top_n: int = 8) -> go.Figure:
    """Radar chart comparing student vs required skill coverage by category."""
    categories = {
        "ML/AI":       ["machine learning","deep learning","tensorflow","pytorch","nlp"],
        "Programming": ["python","java","javascript","typescript","c++"],
        "Data":        ["sql","pandas","data analysis","data visualization","statistics"],
        "DevOps":      ["docker","kubernetes","ci/cd","git","linux"],
        "Cloud":       ["aws","azure","gcp","cloud computing"],
        "Web":         ["react","angular","html","css","node.js"],
    }
    student_set  = {s.lower() for s in student_skills}
    required_set = {s.lower() for s in required_skills}

    cat_names, student_scores, required_scores = [], [], []
    for cat, cat_skills in categories.items():
        cat_names.append(cat)
        student_scores.append(sum(1 for s in cat_skills if s in student_set) / len(cat_skills) * 100)
        required_scores.append(sum(1 for s in cat_skills if s in required_set) / len(cat_skills) * 100)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=student_scores,  theta=cat_names, fill="toself",
                                  name="Your Skills",    line_color=COLORS["primary"], opacity=0.7))
    fig.add_trace(go.Scatterpolar(r=required_scores, theta=cat_names, fill="toself",
                                  name="Required Skills", line_color=COLORS["warning"], opacity=0.5))
    fig.update_layout(
        polar={"bgcolor": "rgba(255,255,255,0.02)",
               "radialaxis": {"visible": True, "range": [0, 100], "gridcolor": "rgba(255,255,255,0.05)", "tickfont": {"family": "Inter", "color": COLORS["muted"]}},
               "angularaxis": {"gridcolor": "rgba(255,255,255,0.05)", "tickfont": {"family": "Inter", "color": COLORS["text"]}}},
        paper_bgcolor=COLORS["bg"],
        legend={"font": {"color": COLORS["muted"], "family": "Inter"}},
        font={"color": COLORS["text"], "family": "Inter"},
        height=380, margin=dict(t=30, b=30, l=30, r=30),
    )
    return fig
