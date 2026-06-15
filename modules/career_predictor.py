"""
modules/career_predictor.py
Predicts top career paths from a student's skill profile using an
ensemble of Random Forest + Gradient Boosting (sklearn, free).

Train: python modules/career_predictor.py
Predict: predict_career(skills_list)
"""
import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

MODEL_PATH  = Path(__file__).parent.parent / "data" / "models" / "career_predictor.pkl"
DATA_DIR    = Path(__file__).parent.parent / "data" / "raw"

# ── Canonical career roles + their key skills ────────────────────────────────
CAREER_ROLES: Dict[str, List[str]] = {
    "Data Scientist": [
        "python","machine learning","deep learning","statistics","pandas",
        "numpy","scikit-learn","tensorflow","pytorch","sql","data analysis",
        "nlp","computer vision","matplotlib","seaborn","jupyter",
    ],
    "Software Engineer": [
        "python","java","javascript","c++","git","rest api","sql",
        "docker","linux","agile","data structures","algorithms",
        "object oriented programming","unit testing",
    ],
    "Data Analyst": [
        "sql","excel","python","tableau","power bi","data analysis",
        "statistics","pandas","data visualization","reporting",
        "google analytics","a/b testing",
    ],
    "ML Engineer": [
        "python","machine learning","tensorflow","pytorch","docker",
        "kubernetes","mlops","ci/cd","aws","scikit-learn",
        "model deployment","api","git","linux",
    ],
    "Web Developer": [
        "html","css","javascript","react","angular","vue",
        "node.js","rest api","git","sql","typescript","figma",
    ],
    "DevOps Engineer": [
        "docker","kubernetes","linux","ci/cd","terraform","ansible",
        "jenkins","aws","azure","git","bash","monitoring","networking",
    ],
    "NLP Engineer": [
        "python","nlp","transformers","pytorch","tensorflow",
        "machine learning","spacy","nltk","bert","regex","sql",
    ],
    "Business Analyst": [
        "sql","excel","tableau","power bi","communication",
        "project management","agile","statistics","requirements gathering",
        "jira","presentation","stakeholder management",
    ],
    "Cybersecurity Analyst": [
        "cybersecurity","networking","linux","python","firewalls",
        "penetration testing","cryptography","siem","incident response",
    ],
    "Cloud Architect": [
        "aws","azure","gcp","terraform","docker","kubernetes",
        "networking","linux","ci/cd","security","microservices","devops",
    ],
}

# Flat master skill list (union of all role skills)
ALL_SKILLS: List[str] = sorted({s for skills in CAREER_ROLES.values() for s in skills})


# ── Feature engineering ───────────────────────────────────────────────────────

def skills_to_vector(skills: List[str]) -> np.ndarray:
    """Convert a list of skill strings to a binary feature vector."""
    s_lower = {s.lower() for s in skills}
    return np.array([1.0 if sk in s_lower else 0.0 for sk in ALL_SKILLS])


def build_training_data():
    """
    Build synthetic training data from CAREER_ROLES.
    Each role generates positive examples (with required skills)
    and negative examples (with randomly removed skills).
    """
    X, y = [], []
    rng = np.random.default_rng(42)

    for role, role_skills in CAREER_ROLES.items():
        # 40 positive samples per role
        for _ in range(40):
            # Randomly pick 60-100% of the role's skills
            n = max(3, int(len(role_skills) * rng.uniform(0.6, 1.0)))
            chosen = rng.choice(role_skills, size=n, replace=False).tolist()
            # Add a few random noise skills from other roles
            noise_pool = [s for s in ALL_SKILLS if s not in role_skills]
            if noise_pool:
                noise = rng.choice(noise_pool,
                                   size=min(3, len(noise_pool)),
                                   replace=False).tolist()
                chosen += noise
            X.append(skills_to_vector(chosen))
            y.append(role)

    return np.array(X), np.array(y)


# ── Training ──────────────────────────────────────────────────────────────────

def train_model():
    """Train the ensemble classifier and save to disk."""
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import cross_val_score

    logger.info("Building training data …")
    X, y = build_training_data()

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    rf  = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
    gb  = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
    ens = VotingClassifier(estimators=[("rf", rf), ("gb", gb)], voting="soft")

    logger.info("Training ensemble (RF + GBM) …")
    ens.fit(X, y_enc)

    cv = cross_val_score(ens, X, y_enc, cv=5, scoring="accuracy")
    logger.info(f"5-fold CV accuracy: {cv.mean():.3f} ± {cv.std():.3f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": ens, "encoder": le, "skills": ALL_SKILLS}, f)
    logger.info(f"Model saved → {MODEL_PATH}")
    return ens, le


def _load_model():
    if not MODEL_PATH.exists():
        logger.info("No trained model found — training now (takes ~10 s) …")
        return train_model()
    with open(MODEL_PATH, "rb") as f:
        obj = pickle.load(f)
    return obj["model"], obj["encoder"]


# ── Prediction ────────────────────────────────────────────────────────────────

def predict_career(skills: List[str], top_n: int = 5) -> List[Dict]:
    """
    Predict top career paths for a given skill set.

    Returns:
        List of {"role": str, "confidence": float, "key_matching_skills": List[str]}
        sorted by confidence descending.
    """
    try:
        model, le = _load_model()
        vec = skills_to_vector(skills).reshape(1, -1)
        proba = model.predict_proba(vec)[0]
        top_idx = np.argsort(proba)[::-1][:top_n]

        results = []
        s_lower = {s.lower() for s in skills}
        for idx in top_idx:
            role = le.inverse_transform([idx])[0]
            conf = float(proba[idx]) * 100
            matching = [s for s in CAREER_ROLES.get(role, []) if s in s_lower]
            results.append({
                "role":                role,
                "confidence":          round(conf, 1),
                "key_matching_skills": matching,
            })
        return results

    except Exception as e:
        logger.error(f"Career prediction failed: {e}")
        # Rule-based fallback
        return _rule_based_predict(skills, top_n)


def _rule_based_predict(skills: List[str], top_n: int = 5) -> List[Dict]:
    """Simple overlap-based fallback (no sklearn needed)."""
    s_lower = {s.lower() for s in skills}
    scores = []
    for role, role_skills in CAREER_ROLES.items():
        match = [s for s in role_skills if s in s_lower]
        score = len(match) / len(role_skills) * 100 if role_skills else 0
        scores.append({"role": role, "confidence": round(score, 1),
                       "key_matching_skills": match})
    return sorted(scores, key=lambda x: x["confidence"], reverse=True)[:top_n]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_model()
    print("✅ Career predictor trained and saved.")
