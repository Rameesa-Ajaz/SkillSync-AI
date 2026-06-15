"""
modules/llm_explainer.py
Generates natural language explanations for skill gaps and recommendations.
Uses template-based generation (instant, no model) with optional
HuggingFace Inference API upgrade (free tier).
"""
import hashlib
import logging
import os
from typing import Dict, List

logger = logging.getLogger(__name__)


# ── Template-based explanations (default — zero setup) ────────────────────────

TEMPLATES = {
    "gap_high": (
        "⚠️ **{skill}** is a **critical requirement** for {job_role} roles. "
        "Over 70% of job postings list this skill. We strongly recommend completing "
        "a structured course within the next 4–8 weeks to significantly boost your match score."
    ),
    "gap_medium": (
        "📌 **{skill}** appears in approximately 50% of {job_role} listings. "
        "Adding this skill will make your profile more competitive and open up "
        "a broader range of opportunities."
    ),
    "gap_low": (
        "💡 **{skill}** is a nice-to-have for {job_role} roles. "
        "Consider adding it after you've covered the high-priority skills — "
        "it will give your profile an extra edge."
    ),
    "course_rec": (
        "📚 We recommend **{course_name}** on {platform} to learn {skill}. "
        "{free_tag}This course aligns well with the requirements for {job_role} positions."
    ),
    "career_pred": (
        "🎯 Based on your skill profile, **{role}** is a strong career fit with "
        "{confidence:.0f}% confidence. Your existing skills in {top_skills} directly "
        "support this path. Closing the remaining skill gaps would make you highly competitive."
    ),
    "ats_high": (
        "✅ Your resume scores **{score}/100** on the ATS check — excellent match! "
        "Your profile closely aligns with the job requirements."
    ),
    "ats_medium": (
        "🔶 Your ATS score is **{score}/100** — a decent match with room to improve. "
        "Strengthening the missing skills below should push you into the top candidate bracket."
    ),
    "ats_low": (
        "🔴 Your ATS score is **{score}/100** — the profile needs more work to match this role. "
        "Focus on the High-priority skills first and tailor your resume keywords to the job description."
    ),
}


def _template_explain(template_key: str, **kwargs) -> str:
    tpl = TEMPLATES.get(template_key, "")
    try:
        return tpl.format(**kwargs)
    except KeyError as e:
        logger.warning(f"Template key missing: {e}")
        return tpl


# ── HuggingFace Inference API (optional upgrade) ──────────────────────────────

def _hf_generate(prompt: str) -> str | None:
    api_key = os.getenv("HUGGINGFACE_API_KEY", "")
    if not api_key:
        return None
    try:
        import requests
        url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 120}}
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json()[0].get("generated_text", "").strip()
    except Exception as e:
        logger.warning(f"HuggingFace API error: {e}")
    return None


def _get_cached(key: str) -> str | None:
    try:
        from database.init_db import get_cached_llm
        return get_cached_llm(key)
    except Exception:
        return None


def _set_cached(key: str, value: str):
    try:
        from database.init_db import set_cached_llm
        set_cached_llm(key, value)
    except Exception:
        pass


def _cache_key(*parts) -> str:
    return hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest()


# ── Public API ────────────────────────────────────────────────────────────────

def explain_skill_gap(skill: str, priority: str, job_role: str, use_llm: bool = True) -> str:
    """Generate explanation for a missing skill."""
    tpl_key = f"gap_{priority.lower()}"

    if use_llm:
        ck = _cache_key("gap", skill, priority, job_role)
        cached = _get_cached(ck)
        if cached:
            return cached
        
        try:
            from modules.llm_integration import GeminiIntegration
            gemini = GeminiIntegration()
            result = gemini.get_skill_explanation(skill, job_role)
            if result:
                # Add priority context if not present
                if priority.lower() == "high":
                    result = "⚠️ **High Priority**: " + result
                _set_cached(ck, result)
                return result
        except Exception as e:
            logger.warning(f"Gemini generation failed: {e}")

    return _template_explain(tpl_key, skill=skill, job_role=job_role)


def explain_course(course: Dict, skill: str, job_role: str) -> str:
    """Generate explanation for a course recommendation."""
    free_tag = "🆓 **Free course.** " if course.get("is_free") else ""
    return _template_explain(
        "course_rec",
        course_name=course.get("course_name", ""),
        platform=course.get("platform", ""),
        skill=skill,
        job_role=job_role,
        free_tag=free_tag,
    )


def explain_career(role: str, confidence: float, top_skills: List[str]) -> str:
    """Generate explanation for a career prediction."""
    skills_str = ", ".join(top_skills[:4]) if top_skills else "your existing skills"
    return _template_explain("career_pred", role=role, confidence=confidence, top_skills=skills_str)


def explain_ats(score: float) -> str:
    """Generate explanation for an ATS score."""
    if score >= 75:
        return _template_explain("ats_high", score=score)
    elif score >= 50:
        return _template_explain("ats_medium", score=score)
    else:
        return _template_explain("ats_low", score=score)
