"""
modules/gap_analyzer.py
Computes the skill gap between what a student has and what a job requires.
"""
import logging
from difflib import SequenceMatcher
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# ── Priority reference (manually curated) ────────────────────────────────────
PRIORITY_RULES: Dict[str, str] = {
    # High priority
    "python":"High","sql":"High","machine learning":"High","javascript":"High",
    "java":"High","react":"High","aws":"High","docker":"High","git":"High",
    "data analysis":"High","deep learning":"High","nlp":"High",
    # Medium priority
    "tensorflow":"Medium","pytorch":"Medium","kubernetes":"Medium","mongodb":"Medium",
    "postgresql":"Medium","typescript":"Medium","angular":"Medium","vue":"Medium",
    "django":"Medium","flask":"Medium","power bi":"Medium","tableau":"Medium",
    "api":"Medium","rest api":"Medium","agile":"Medium","scrum":"Medium",
    # Low priority
    "communication":"Low","teamwork":"Low","leadership":"Low",
    "microsoft office":"Low","excel":"Low","presentation":"Low",
}

LEARNING_TIME: Dict[str, str] = {
    "High":   "4–8 weeks",
    "Medium": "2–4 weeks",
    "Low":    "1–2 weeks",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    return s.lower().strip().replace("-", " ").replace("_", " ")


def _fuzzy_match(a: str, b: str, threshold: float = 0.80) -> bool:
    a, b = _norm(a), _norm(b)
    if a == b:
        return True
    return SequenceMatcher(None, a, b).ratio() >= threshold


def _find_in_list(skill: str, skill_list: List[str]) -> Tuple[bool, str]:
    for s in skill_list:
        if _fuzzy_match(skill, s):
            return True, s
    return False, ""


def get_priority(skill: str) -> str:
    low = skill.lower()
    for key, pri in PRIORITY_RULES.items():
        if key in low or low in key:
            return pri
    # Heuristic: looks technical → Medium, otherwise Low
    tech_hints = ["python","java","sql","ml","ai","cloud","aws","api","data","model","net","dev"]
    if any(h in low for h in tech_hints):
        return "Medium"
    return "Low"


# ── Main function ─────────────────────────────────────────────────────────────

def analyze_gap(
    student_skills: List[str],
    required_skills: List[str],
    job_role: str = "",
) -> Dict:
    """
    Compute skill gap.

    Args:
        student_skills  : skills extracted from resume
        required_skills : skills required for the target job role
        job_role        : job role name (for context)

    Returns:
        {matched, missing, extra, match_percentage, summary}
    """
    matched: List[Dict] = []
    missing: List[Dict] = []
    extra:   List[str]  = []

    # Find matched skills
    used_student = set()
    for req in required_skills:
        found, match = _find_in_list(req, student_skills)
        if found:
            matched.append({"required": req, "matched_as": match})
            used_student.add(_norm(match))
        else:
            pri = get_priority(req)
            missing.append({
                "skill":         req,
                "priority":      pri,
                "learning_time": LEARNING_TIME[pri],
            })

    # Skills in resume not required by job
    for s in student_skills:
        if _norm(s) not in used_student:
            extra.append(s)

    # Sort missing by priority
    order = {"High": 0, "Medium": 1, "Low": 2}
    missing.sort(key=lambda x: order.get(x["priority"], 2))

    total = len(required_skills)
    match_pct = round(len(matched) / total * 100, 1) if total else 0.0

    level = (
        "Excellent" if match_pct >= 80 else
        "Good"      if match_pct >= 60 else
        "Fair"      if match_pct >= 40 else
        "Needs Work"
    )

    return {
        "matched":          matched,
        "missing":          missing,
        "extra_skills":     extra,
        "match_percentage": match_pct,
        "level":            level,
        "total_required":   total,
        "total_matched":    len(matched),
        "total_missing":    len(missing),
        "job_role":         job_role,
    }


def get_missing_skills_list(gap_result: Dict) -> List[str]:
    """Extract plain list of missing skill names from gap result."""
    return [m["skill"] for m in gap_result.get("missing", [])]
