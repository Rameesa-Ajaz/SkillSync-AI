"""
modules/skill_extractor.py
Extracts skills using 3 combined methods:
  1. Keyword matching against master skill list
  2. SpaCy NER entity detection
  3. BERT semantic similarity (sentence-transformers)
"""
import re
import logging
from pathlib import Path
from typing import Dict, List, Set

import numpy as np
import pandas as pd

from config import config

logger = logging.getLogger(__name__)
DATA_DIR = Path(config.DATA_DIR)

# ── Fallback built-in skill list ─────────────────────────────────────────────
FALLBACK_SKILLS: Set[str] = {
    "python","java","javascript","typescript","c++","c#","r","go","rust","kotlin","swift",
    "react","angular","vue","node.js","django","flask","fastapi","spring boot","express",
    "tensorflow","pytorch","keras","scikit-learn","pandas","numpy","matplotlib","seaborn",
    "sql","mysql","postgresql","mongodb","redis","elasticsearch","sqlite","oracle",
    "docker","kubernetes","aws","azure","gcp","terraform","ansible","jenkins","ci/cd",
    "git","github","gitlab","linux","bash","powershell",
    "machine learning","deep learning","nlp","natural language processing","computer vision",
    "data science","data analysis","data visualization","big data","spark","hadoop",
    "html","css","rest api","graphql","microservices","agile","scrum","devops",
    "excel","power bi","tableau","statistics","a/b testing",
    "communication","leadership","teamwork","problem solving","project management",
    "jira","confluence","figma","ui/ux","photoshop",
    "blockchain","cybersecurity","network","cloud computing",
}

# ── Model cache ───────────────────────────────────────────────────────────────
_model = None
_skill_embeddings = None
_cached_skill_list: List[str] = []


def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading sentence-transformer model {config.EMBEDDING_MODEL}...")
            _model = SentenceTransformer(config.EMBEDDING_MODEL)
            logger.info("Model loaded.")
        except Exception as e:
            logger.warning(f"sentence-transformers unavailable: {e}")
            _model = False   # sentinel so we don't retry
    return _model if _model is not False else None


def _get_skill_embeddings(skills: List[str]):
    global _skill_embeddings, _cached_skill_list
    model = _get_model()
    if model is None:
        return None
    if _cached_skill_list != skills:
        _skill_embeddings = model.encode(skills, show_progress_bar=False, batch_size=64)
        _cached_skill_list = skills
    return _skill_embeddings


# ── Data loading ──────────────────────────────────────────────────────────────

def load_master_skills() -> Set[str]:
    path = DATA_DIR / "skills_master.csv"
    if path.exists():
        try:
            df = pd.read_csv(path)
            return set(df["skill"].str.lower().tolist())
        except Exception as e:
            logger.warning(f"Could not load skills_master.csv: {e}")
    return FALLBACK_SKILLS


# ── Method 1: Keyword matching ────────────────────────────────────────────────

def keyword_match(text: str, master: Set[str]) -> List[Dict]:
    text_lower = text.lower()
    found = []
    for skill in master:
        pat = r"\b" + re.escape(skill) + r"\b" if len(skill) <= 4 else re.escape(skill)
        if re.search(pat, text_lower):
            found.append({"skill": skill, "confidence": 1.0, "method": "keyword"})
    return found


# ── Method 2: SpaCy NER ───────────────────────────────────────────────────────

def spacy_candidates(text: str) -> List[str]:
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text[:50_000])
        return [e.text.lower() for e in doc.ents if e.label_ in ("ORG","PRODUCT","LANGUAGE","WORK_OF_ART")]
    except Exception as e:
        logger.warning(f"SpaCy failed: {e}")
        return []


# ── Method 3: Semantic matching ───────────────────────────────────────────────

def semantic_match(text: str, master: Set[str], threshold: float | None = None) -> List[Dict]:
    if threshold is None:
        threshold = config.SKILL_THRESHOLD
    model = _get_model()
    if model is None:
        return []
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        # Build candidate n-grams (1-3 words)
        words = re.findall(r"\b[a-zA-Z][\w.#+]*\b", text)
        candidates = []
        for n in range(1, 4):
            for i in range(len(words) - n + 1):
                c = " ".join(words[i:i+n]).lower()
                if len(c) > 2:
                    candidates.append(c)
        candidates = list(dict.fromkeys(candidates))[:300]   # deduplicate, cap

        skills_list = sorted(master)
        skill_embs = _get_skill_embeddings(skills_list)
        if skill_embs is None:
            return []

        cand_embs = model.encode(candidates, show_progress_bar=False, batch_size=64)
        sims = cosine_similarity(cand_embs, skill_embs)

        found, seen = [], set()
        for i, cand in enumerate(candidates):
            best = int(np.argmax(sims[i]))
            score = float(sims[i][best])
            if score >= threshold:
                matched = skills_list[best]
                if matched not in seen:
                    seen.add(matched)
                    found.append({"skill": matched, "confidence": score, "method": "semantic"})
        return found
    except Exception as e:
        logger.error(f"Semantic match error: {e}")
        return []


# ── Main function ─────────────────────────────────────────────────────────────

def extract_skills(text: str, use_semantic: bool = True) -> List[Dict]:
    """
    Extract skills from text using all 3 methods combined.

    Returns:
        List of {"skill": str, "confidence": float, "method": str}
        sorted by confidence descending.
    """
    master = load_master_skills()
    all_found: Dict[str, Dict] = {}

    # 1. Keyword
    for r in keyword_match(text, master):
        all_found[r["skill"]] = r

    # 2. SpaCy NER candidates → verify against master list
    for cand in spacy_candidates(text):
        if cand in master and cand not in all_found:
            all_found[cand] = {"skill": cand, "confidence": 0.85, "method": "ner"}

    # 3. Semantic
    if use_semantic:
        for r in semantic_match(text, master):
            key = r["skill"]
            if key not in all_found:
                all_found[key] = r
            else:
                # Boost confidence for skills confirmed by multiple methods
                old = all_found[key]["confidence"]
                all_found[key]["confidence"] = min(1.0, (old + r["confidence"]) / 2 + 0.05)
                all_found[key]["method"] = "multi"

    return sorted(all_found.values(), key=lambda x: x["confidence"], reverse=True)


def get_skills_list(text: str, use_semantic: bool = True) -> List[str]:
    """Convenience wrapper — returns just skill names."""
    return [s["skill"] for s in extract_skills(text, use_semantic)]
