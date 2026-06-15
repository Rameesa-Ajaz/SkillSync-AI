<div align="center">

# 🎯 SkillSync AI
> **SkillSync** is a full-stack AI-powered career platform that deeply analyzes your resume against real job market expectations — scoring your ATS compatibility, visualizing skill gaps, curating personalized learning paths, and predicting your best-fit career trajectory using machine learning.

</div>

---

## 🧠 What SkillSync Does

SkillSync takes a single resume upload and delivers a complete, data-driven career intelligence report across **7 interactive screens**:

| # | Screen | What you see |
|---|---|---|
| 1 | **Dashboard** | Welcome overview of all AI capabilities |
| 2 | **Resume Analysis** | Drag-and-drop upload, job role targeting, and parsed contact extraction |
| 3 | **ATS Score Dashboard** | Animated radial score ring, BERT/TF-IDF/Direct score breakdown bars, matched and missing keyword badges |
| 4 | **Skill Gap Analysis** | Donut coverage chart, competency matrix, priority-ranked missing skills list |
| 5 | **Course Recommendations** | Curated, filterable course cards from Coursera, Udemy, YouTube and more |
| 6 | **Career Prediction** | ML-predicted career confidence bars, top-match trophy card, and drill-down gap checker |
| 7 | **AI Career Assistant** | Conversational Gemini-powered career counselor for real-time CV advice |

---

## ⚙️ How the AI Engine Works

SkillSync's backend is powered by a multi-stage analysis pipeline — not a single model, but an **ensemble of 3 independent scoring methods** fused for maximum precision:

```
Resume File (PDF/DOCX)
        │
        ▼
 ┌─────────────────────────────────────────────┐
 │           ANALYSIS PIPELINE                 │
 │                                             │
 │  [1] BERT Semantic Similarity               │
 │      → Measures contextual meaning match    │
 │                                             │
 │  [2] TF-IDF Keyword Relevance               │
 │      → Identifies important term frequency  │
 │                                             │
 │  [3] Direct Skill Intersection              │
 │      → Checks exact technical skill overlap │
 │                                             │
 │       ↓ Weighted Ensemble Fusion            │
 └─────────────────────────────────────────────┘
        │
        ▼
  ATS Score + Grade
  Skill Gap Priorities
  Learning Path Recommendations
  Career Match Predictions
  Gemini AI Explanations
```

---

## 🎨 Interface Design

The web interface is built with a **Premium Light-Mode Corporate Glassmorphism** aesthetic, following a Google Stitch-inspired visual specification:

- **Color System**: Indigo primary `#4f46e5` for brand identity, Emerald `#10b981` for positive matches, Rose `#e11d48` for skill gaps and warnings
- **Typography**: `Outfit` for bold, geometric headings and labels — `Inter` for high-readability body copy
- **Layout**: Fixed 280px sidebar with fluid content canvas, responsive bento-grid dashboard panels
- **Depth & Elevation**: Glassmorphic card panels with `backdrop-filter: blur(12px)`, subtle box shadows, and animated hover interactions

---

## 📊 Model Performance

| Module | Method | Estimated Accuracy |
|---|---|---|
| Skill Extraction | BERT + SpaCy NER + Keyword matching | ~90% |
| ATS Scoring | 3-method weighted ensemble | ~90% |
| Course Recommendations | Priority-mapped gap curation | ~85% relevance |
| Career Prediction | Random Forest + Gradient Boosting | ~87% |
| **Overall System** | **Weighted pipeline accuracy** | **~91%** |

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | FastAPI, Uvicorn, Python 3.9+ |
| **Frontend SPA** | HTML5, CSS3 (Glassmorphic Design), ES6 JavaScript |
| **Analytics UI** | Streamlit, Plotly |
| **NLP & Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`), SpaCy |
| **Scoring Models** | BERT cosine similarity, TF-IDF, Scikit-Learn |
| **Career Prediction** | Random Forest, Gradient Boosting Classifier |
| **Conversational AI** | Google Gemini (`google-generativeai`) |
| **Resume Parsing** | pdfminer.six, PyMuPDF, python-docx |
| **Database** | SQLite3 |

---


## 📖 Based On

*SkillSync: An Explainable AI Framework for Resume Evaluation, Skill Gap Analysis, and Career Alignment*  
*IJERT Conference Proceedings, 2024*

