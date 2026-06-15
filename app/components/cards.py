"""
app/components/cards.py
Reusable HTML/CSS card components rendered via st.markdown.
Premium glassmorphism design with micro-animations.
"""
import streamlit as st
from typing import Dict, List


def skill_badge(skill: str, style: str = "default") -> str:
    colors = {
        "matched": ("rgba(0,212,170,0.12)", "#00D4AA"),
        "missing": ("rgba(255,107,107,0.12)", "#FF6B6B"),
        "default": ("rgba(108,99,255,0.12)", "#6C63FF"),
    }
    bg, border = colors.get(style, colors["default"])
    return (
        f'<span style="background:{bg};border:1px solid {border};color:{border};'
        f'border-radius:20px;padding:4px 14px;font-size:0.78rem;font-weight:500;'
        f'margin:3px;display:inline-block;transition:all 0.2s ease;'
        f'letter-spacing:0.01em;">{skill}</span>'
    )


def priority_badge(priority: str) -> str:
    c = {"High": "#FF6B6B", "Medium": "#FFB547", "Low": "#00D4AA"}.get(priority, "#6C63FF")
    return (
        f'<span style="background:rgba(0,0,0,0.3);border:1px solid {c};color:{c};'
        f'border-radius:12px;padding:3px 12px;font-size:0.73rem;font-weight:600;'
        f'letter-spacing:0.02em;">'
        f'{priority}</span>'
    )


def metric_card(label: str, value: str, delta: str = "", color: str = "#6C63FF") -> None:
    st.markdown(
        f"""
        <div class="glass-card" style="border-left:3px solid {color};padding:20px 22px;">
          <p style="color:rgba(255,255,255,0.4);font-size:0.72rem;margin:0 0 6px 0;
                    text-transform:uppercase;letter-spacing:0.1em;font-weight:500;">{label}</p>
          <p style="color:#FAFAFA;font-size:1.7rem;font-weight:700;margin:0;
                    letter-spacing:-0.02em;">{value}</p>
          {"" if not delta else f'<p style="color:{color};font-size:0.8rem;margin:6px 0 0 0;font-weight:500;">{delta}</p>'}
        </div>
        """,
        unsafe_allow_html=True,
    )


def course_card(rec: Dict, explanation: str = "") -> None:
    free_tag = "🆓 Free" if rec.get("is_free") else "💳 Paid"
    free_color = "#00D4AA" if rec.get("is_free") else "#FFB547"
    platform_icons = {
        "YouTube":   "▶️", "Coursera": "🎓", "Udemy": "📘",
        "FreeCodeCamp": "💻", "Microsoft Learn": "🪟",
    }
    icon = platform_icons.get(rec.get("platform",""), "📚")
    url = rec.get("url", "#")

    st.markdown(
        f"""
        <div class="glass-card" style="padding:20px 24px;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div style="flex:1;">
              <p style="color:#FAFAFA;font-size:0.95rem;font-weight:600;margin:0 0 8px 0;
                        line-height:1.4;">
                {icon} {rec.get('course_name','')}
              </p>
              <p style="color:rgba(255,255,255,0.45);font-size:0.8rem;margin:0 0 10px 0;">
                {rec.get('platform','')} &nbsp;·&nbsp;
                <span style="color:{free_color};font-weight:500;">{free_tag}</span>
              </p>
              {"" if not explanation else f'<p style="color:rgba(255,255,255,0.55);font-size:0.82rem;margin:0 0 12px 0;line-height:1.5;">{explanation}</p>'}
            </div>
          </div>
          <a href="{url}" target="_blank"
             style="display:inline-block;background:rgba(108,99,255,0.12);
                    color:#6C63FF;border:1px solid rgba(108,99,255,0.3);
                    border-radius:10px;padding:8px 20px;font-size:0.82rem;
                    text-decoration:none;font-weight:600;
                    transition:all 0.25s ease;">
            Open Course →
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def career_card(pred: Dict, rank: int) -> None:
    conf = pred.get("confidence", 0)
    role = pred.get("role", "")
    matching = pred.get("key_matching_skills", [])
    color = "#00D4AA" if conf >= 60 else "#FFB547" if conf >= 35 else "#FF6B6B"
    bar_w = max(4, int(conf))

    medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")

    st.markdown(
        f"""
        <div class="glass-card" style="padding:20px 24px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <span style="color:#FAFAFA;font-size:1rem;font-weight:700;
                         letter-spacing:-0.01em;">
              {medal} {role}
            </span>
            <span style="color:{color};font-size:1.2rem;font-weight:800;">{conf:.1f}%</span>
          </div>
          <div style="background:rgba(255,255,255,0.06);border-radius:8px;height:6px;
                      margin-bottom:12px;overflow:hidden;">
            <div style="background:linear-gradient(90deg,{color},{color}88);width:{bar_w}%;
                        height:6px;border-radius:8px;transition:width 1s ease;"></div>
          </div>
          <p style="color:rgba(255,255,255,0.4);font-size:0.78rem;margin:0;">
            Matching: {', '.join(matching[:5]) if matching else '—'}
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div style="margin:24px 0 16px 0;">
          <h2 style="color:#FAFAFA;font-size:1.3rem;font-weight:700;margin:0 0 4px 0;
                     letter-spacing:-0.02em;">
            {title}
          </h2>
          {"" if not subtitle else f'<p style="color:rgba(255,255,255,0.4);font-size:0.88rem;margin:0;line-height:1.5;">{subtitle}</p>'}
        </div>
        """,
        unsafe_allow_html=True,
    )
