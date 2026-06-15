"""
modules/pipeline.py
Orchestrates all modules into a single end-to-end analysis pipeline.
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def run_analysis(
    file_bytes: bytes,
    file_type: str,
    job_role: str,
    jd_text: str,
    jd_skills: List[str] | None = None,
    use_semantic: bool = True,
    session_id: str = "anon",
) -> Dict:
    """
    Full SkillSync analysis pipeline.

    Args:
        file_bytes   : raw bytes of the uploaded resume
        file_type    : 'pdf' or 'docx'
        job_role     : target job role string
        jd_text      : full job description text
        jd_skills    : manually provided JD skills (optional)
        use_semantic : use BERT semantic matching in skill extractor
        session_id   : user session identifier

    Returns:
        {
          parsed        : resume parse result,
          resume_skills : list of skill dicts,
          ats           : ATS score dict,
          gap           : gap analysis dict,
          recommendations : list of course dicts,
          career        : list of career prediction dicts,
          explanations  : {ats_exp, skill_explanations},
          error         : str (only on failure)
        }
    """
    result: Dict = {}

    # ── 1. Parse Resume ───────────────────────────────────────────────────────
    try:
        from modules.resume_parser import parse_resume
        parsed = parse_resume(file_bytes, file_type)
        if "error" in parsed:
            return {"error": parsed["error"]}
        result["parsed"] = parsed
    except Exception as e:
        logger.exception(e)
        return {"error": f"Resume parsing failed: {e}"}

    resume_text = parsed["raw_text"]

    # ── 2. Extract Skills ─────────────────────────────────────────────────────
    try:
        from modules.skill_extractor import extract_skills, get_skills_list
        skill_dicts  = extract_skills(resume_text, use_semantic=use_semantic)
        resume_skills = [s["skill"] for s in skill_dicts]
        result["resume_skills"] = skill_dicts
    except Exception as e:
        logger.exception(e)
        resume_skills = []
        result["resume_skills"] = []

    # ── 3. Resolve JD skills ──────────────────────────────────────────────────
    if not jd_skills and jd_text:
        try:
            from modules.skill_extractor import get_skills_list
            jd_skills = get_skills_list(jd_text, use_semantic=False)
        except Exception:
            jd_skills = []
    jd_skills = jd_skills or []

    # ── 4. ATS Scoring ────────────────────────────────────────────────────────
    try:
        from modules.ats_scorer import compute_ats_score
        ats = compute_ats_score(resume_text, jd_text, resume_skills, jd_skills)
        result["ats"] = ats
    except Exception as e:
        logger.exception(e)
        result["ats"] = {"ats_score": 0, "grade": "N/A", "breakdown": {}}

    # ── 5. Gap Analysis ───────────────────────────────────────────────────────
    try:
        from modules.gap_analyzer import analyze_gap
        gap = analyze_gap(resume_skills, jd_skills, job_role)
        result["gap"] = gap
    except Exception as e:
        logger.exception(e)
        result["gap"] = {"missing": [], "matched": [], "match_percentage": 0}

    missing_skills = [m["skill"] for m in result["gap"].get("missing", [])]

    # ── 6. Recommendations ────────────────────────────────────────────────────
    try:
        from modules.recommender import get_recommendations
        recs = get_recommendations(missing_skills, student_skills=resume_skills)
        result["recommendations"] = recs
    except Exception as e:
        logger.exception(e)
        result["recommendations"] = []

    # ── 7. Career Prediction ──────────────────────────────────────────────────
    try:
        from modules.career_predictor import predict_career
        career = predict_career(resume_skills, top_n=5)
        result["career"] = career
    except Exception as e:
        logger.exception(e)
        result["career"] = []

    # ── 8. Explanations ───────────────────────────────────────────────────────
    try:
        from modules.llm_explainer import explain_ats, explain_skill_gap
        ats_exp = explain_ats(result["ats"].get("ats_score", 0))
        skill_exps = {}
        for m in result["gap"].get("missing", [])[:8]:
            skill_exps[m["skill"]] = explain_skill_gap(
                m["skill"], m.get("priority", "Medium"), job_role
            )
        result["explanations"] = {"ats": ats_exp, "skills": skill_exps}
    except Exception as e:
        logger.exception(e)
        result["explanations"] = {"ats": "", "skills": {}}

    # ── 9. Persist to DB ──────────────────────────────────────────────────────
    try:
        from database.init_db import save_analysis, save_recommendations, init_database
        import json
        init_database()
        aid = save_analysis(
            session_id, job_role, resume_text[:5000],
            result["ats"].get("ats_score", 0),
            result["gap"].get("match_percentage", 0),
            resume_skills,
            missing_skills,
            [c["role"] for c in result["career"]],
        )
        save_recommendations(aid, result["recommendations"])
    except Exception as e:
        logger.warning(f"DB persist failed (non-critical): {e}")

    return result
