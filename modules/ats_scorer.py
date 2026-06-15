"""
modules/ats_scorer.py
Ensemble ATS scoring:
  - BERT semantic similarity  (40 %)
  - TF-IDF keyword similarity (30 %)
  - Direct skill set match    (30 %)
"""
import re
import logging
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── Method 1: BERT semantic ───────────────────────────────────────────────────

def bert_similarity(t1: str, t2: str) -> float:
    try:
        from modules.skill_extractor import _get_model
        from sklearn.metrics.pairwise import cosine_similarity
        model = _get_model()
        if model is None:
            return 0.5
        e1 = model.encode([t1[:512]], show_progress_bar=False)
        e2 = model.encode([t2[:512]], show_progress_bar=False)
        return float(np.clip(cosine_similarity(e1, e2)[0][0], 0, 1))
    except Exception as e:
        logger.error(f"BERT similarity error: {e}")
        return 0.5


# ── Method 2: TF-IDF ─────────────────────────────────────────────────────────

def tfidf_similarity(t1: str, t2: str) -> float:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=5000)
        tfidf = vec.fit_transform([t1, t2])
        return float(np.clip(cosine_similarity(tfidf[0], tfidf[1])[0][0], 0, 1))
    except Exception as e:
        logger.error(f"TF-IDF similarity error: {e}")
        return 0.0


# ── Method 3: Direct skill match ─────────────────────────────────────────────

def direct_skill_match(
    resume_skills: List[str], jd_skills: List[str]
) -> Tuple[float, List[str], List[str]]:
    if not jd_skills:
        return 0.0, [], []
    r_set = {s.lower() for s in resume_skills}
    j_set = {s.lower() for s in jd_skills}
    matched = sorted(r_set & j_set)
    missing = sorted(j_set - r_set)
    score = len(matched) / len(j_set)
    return float(score), matched, missing


# ── Keyword extraction (for explainability) ───────────────────────────────────

def get_matched_keywords(resume_text: str, jd_text: str, top_n: int = 25) -> List[str]:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=80)
        vec.fit([jd_text])
        jd_kws = list(vec.vocabulary_.keys())
        r_lower = resume_text.lower()
        return [kw for kw in jd_kws if kw in r_lower][:top_n]
    except Exception:
        return []


# ── Main scoring function ─────────────────────────────────────────────────────

def compute_ats_score(
    resume_text: str,
    jd_text: str,
    resume_skills: List[str],
    jd_skills: List[str],
    weights: Dict[str, float] | None = None,
) -> Dict:
    """
    Ensemble ATS score (0–100).

    Returns:
        {ats_score, grade, breakdown, matched_skills, missing_skills, matched_keywords}
    """
    if weights is None:
        weights = {"bert": 0.40, "tfidf": 0.30, "direct": 0.30}

    bert   = bert_similarity(_preprocess(resume_text[:1000]), _preprocess(jd_text[:1000]))
    tfidf  = tfidf_similarity(_preprocess(resume_text), _preprocess(jd_text))
    direct, matched, missing = direct_skill_match(resume_skills, jd_skills)

    raw = weights["bert"] * bert + weights["tfidf"] * tfidf + weights["direct"] * direct
    ats_score = round(min(100.0, raw * 120), 1)   # scale factor

    # Letter grade
    grade = (
        "A" if ats_score >= 85 else
        "B" if ats_score >= 70 else
        "C" if ats_score >= 55 else
        "D"
    )

    return {
        "ats_score":       ats_score,
        "grade":           grade,
        "breakdown": {
            "bert_semantic":  round(bert  * 100, 1),
            "tfidf_keywords": round(tfidf * 100, 1),
            "direct_match":   round(direct * 100, 1),
        },
        "matched_skills":   matched,
        "missing_skills":   missing,
        "matched_keywords": get_matched_keywords(resume_text, jd_text),
        "weights":          weights,
    }
