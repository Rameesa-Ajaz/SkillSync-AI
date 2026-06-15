"""
modules/recommender.py
Multi-method course & resource recommender:
  1. Content-based (TF-IDF match against courses.csv)     30 %
  2. Skill-adjacency graph (networkx)                     40 %
  3. YouTube video fetch (free API quota)                  30 %
"""
import logging
import os
from pathlib import Path
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)
DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

# ── Load course dataset ───────────────────────────────────────────────────────

def _load_courses() -> pd.DataFrame:
    path = DATA_DIR / "courses.csv"
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception as e:
            logger.warning(f"courses.csv load failed: {e}")
    # Built-in fallback courses
    rows = [
        {"skill":"python","course_name":"Python for Everybody","platform":"Coursera","url":"https://www.coursera.org/specializations/python","is_free":True},
        {"skill":"machine learning","course_name":"Machine Learning Specialization","platform":"Coursera","url":"https://www.coursera.org/specializations/machine-learning-introduction","is_free":True},
        {"skill":"sql","course_name":"SQL for Data Science","platform":"Coursera","url":"https://www.coursera.org/learn/sql-for-data-science","is_free":True},
        {"skill":"deep learning","course_name":"Deep Learning Specialization","platform":"Coursera","url":"https://www.coursera.org/specializations/deep-learning","is_free":True},
        {"skill":"data science","course_name":"IBM Data Science Professional","platform":"Coursera","url":"https://www.coursera.org/professional-certificates/ibm-data-science","is_free":True},
        {"skill":"javascript","course_name":"The Complete JavaScript Course","platform":"Udemy","url":"https://www.udemy.com/course/the-complete-javascript-course/","is_free":False},
        {"skill":"react","course_name":"React - The Complete Guide","platform":"Udemy","url":"https://www.udemy.com/course/react-the-complete-guide-incl-redux/","is_free":False},
        {"skill":"docker","course_name":"Docker & Kubernetes: The Practical Guide","platform":"Udemy","url":"https://www.udemy.com/course/docker-kubernetes-the-practical-guide/","is_free":False},
        {"skill":"aws","course_name":"AWS Certified Cloud Practitioner","platform":"FreeCodeCamp","url":"https://www.youtube.com/watch?v=SOTamWNgDKc","is_free":True},
        {"skill":"nlp","course_name":"NLP with Python","platform":"YouTube","url":"https://www.youtube.com/watch?v=X2vAabgKiuM","is_free":True},
        {"skill":"tensorflow","course_name":"TensorFlow Developer Certificate","platform":"Coursera","url":"https://www.coursera.org/professional-certificates/tensorflow-in-practice","is_free":True},
        {"skill":"pytorch","course_name":"PyTorch for Deep Learning","platform":"YouTube","url":"https://www.youtube.com/watch?v=Z_ikDlimN6A","is_free":True},
        {"skill":"power bi","course_name":"Power BI Full Course","platform":"YouTube","url":"https://www.youtube.com/watch?v=NNSHu0rkew8","is_free":True},
        {"skill":"tableau","course_name":"Tableau Tutorial for Beginners","platform":"YouTube","url":"https://www.youtube.com/watch?v=TPMlZxRRaBQ","is_free":True},
        {"skill":"git","course_name":"Git and GitHub for Beginners","platform":"FreeCodeCamp","url":"https://www.youtube.com/watch?v=RGOj5yH7evk","is_free":True},
        {"skill":"kubernetes","course_name":"Kubernetes Tutorial for Beginners","platform":"TechWorld","url":"https://www.youtube.com/watch?v=X48VuDVv0do","is_free":True},
        {"skill":"mongodb","course_name":"MongoDB Crash Course","platform":"YouTube","url":"https://www.youtube.com/watch?v=-56x56UppqQ","is_free":True},
        {"skill":"django","course_name":"Django Full Course","platform":"YouTube","url":"https://www.youtube.com/watch?v=PtQiiknWUcI","is_free":True},
        {"skill":"flask","course_name":"Flask Web Framework","platform":"YouTube","url":"https://www.youtube.com/watch?v=Z1RJmh_OqeA","is_free":True},
        {"skill":"data analysis","course_name":"Data Analysis with Python","platform":"FreeCodeCamp","url":"https://www.freecodecamp.org/learn/data-analysis-with-python/","is_free":True},
    ]
    return pd.DataFrame(rows)


# ── Method 1: Content-based (TF-IDF) ─────────────────────────────────────────

def content_based(skill: str, courses_df: pd.DataFrame, top_n: int = 2) -> List[Dict]:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        texts = courses_df["skill"].fillna("") + " " + courses_df["course_name"].fillna("")
        vec = TfidfVectorizer(stop_words="english")
        mat = vec.fit_transform(texts.tolist() + [skill])
        sims = cosine_similarity(mat[-1], mat[:-1])[0]
        top_idx = np.argsort(sims)[::-1][:top_n]
        results = []
        for i in top_idx:
            row = courses_df.iloc[i]
            results.append({
                "skill":       skill,
                "course_name": row.get("course_name", ""),
                "platform":    row.get("platform", ""),
                "url":         row.get("url", ""),
                "is_free":     bool(row.get("is_free", True)),
                "relevance":   round(float(sims[i]), 3),
                "source":      "content-based",
            })
        return results
    except Exception as e:
        logger.error(f"Content-based error: {e}")
        return []


# ── Method 2: Skill adjacency graph ──────────────────────────────────────────

SKILL_GRAPH: Dict[str, List[str]] = {
    "machine learning": ["python","statistics","numpy","pandas","scikit-learn"],
    "deep learning":    ["machine learning","tensorflow","pytorch","python"],
    "nlp":              ["deep learning","python","transformers","regex"],
    "data science":     ["python","sql","statistics","data analysis","machine learning"],
    "web development":  ["html","css","javascript","react","node.js"],
    "devops":           ["docker","kubernetes","linux","ci/cd","git"],
    "cloud computing":  ["aws","azure","gcp","docker","terraform"],
    "data analysis":    ["python","sql","excel","tableau","power bi","pandas"],
}


def adjacency_recommend(skill: str, student_skills: List[str]) -> List[str]:
    """Return adjacent skills not yet in student profile."""
    skill_lower = skill.lower()
    for key, adjacents in SKILL_GRAPH.items():
        if skill_lower in key or key in skill_lower:
            return [a for a in adjacents if a.lower() not in {s.lower() for s in student_skills}]
    return []


# ── Method 3: YouTube API ─────────────────────────────────────────────────────

def youtube_search(skill: str, max_results: int = 2) -> List[Dict]:
    api_key = os.getenv("YOUTUBE_API_KEY", "")
    if not api_key:
        return []
    try:
        import requests
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet", "q": f"{skill} tutorial",
                "type": "video", "maxResults": max_results,
                "key": api_key, "relevanceLanguage": "en",
                "videoDuration": "medium",
            },
            timeout=5,
        )
        items = resp.json().get("items", [])
        return [
            {
                "skill":       skill,
                "course_name": it["snippet"]["title"],
                "platform":    "YouTube",
                "url":         f"https://www.youtube.com/watch?v={it['id']['videoId']}",
                "is_free":     True,
                "relevance":   0.8,
                "source":      "youtube",
            }
            for it in items if it.get("id", {}).get("videoId")
        ]
    except Exception as e:
        logger.warning(f"YouTube API error: {e}")
        return []


# ── Main entry point ──────────────────────────────────────────────────────────

def get_recommendations(
    missing_skills: List[str],
    student_skills: List[str] | None = None,
    free_only: bool = False,
    top_per_skill: int = 3,
) -> List[Dict]:
    """
    Get course/resource recommendations for a list of missing skills.

    Returns:
        Flat list of recommendation dicts, sorted by relevance.
    """
    if student_skills is None:
        student_skills = []

    courses_df = _load_courses()
    all_recs: List[Dict] = []

    for skill in missing_skills[:15]:   # cap to avoid slow loops
        recs = []

        # Method 1: content-based
        recs += content_based(skill, courses_df, top_n=2)

        # Method 2: adjacency → look up adjacent skills in course DB
        for adj in adjacency_recommend(skill, student_skills)[:2]:
            recs += content_based(adj, courses_df, top_n=1)

        # Method 3: YouTube
        recs += youtube_search(skill, max_results=1)

        # Filter and deduplicate
        seen_urls = set()
        for r in recs:
            if free_only and not r.get("is_free"):
                continue
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_recs.append(r)

    # Sort by relevance descending
    all_recs.sort(key=lambda x: x.get("relevance", 0), reverse=True)
    return all_recs[:top_per_skill * len(missing_skills)]
