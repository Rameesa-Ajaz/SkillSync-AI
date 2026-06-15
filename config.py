# config.py
# Professional configuration management

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # App Configuration
    APP_NAME = "SkillSync"
    APP_VERSION = "1.0.0"
    DEBUG = False
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data", "raw") # Adjusting to my existing data folder
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    
    # API Keys (Free tier)
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "") # Using GOOGLE_API_KEY as per standard
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///skillsync.db")
    
    # Model Configuration
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384
    SKILL_THRESHOLD = 0.55
    
    # ATS Configuration
    ATS_WEIGHTS = {
        "bert": 0.4,
        "tfidf": 0.3,
        "keyword": 0.3
    }
    
    # Recommendation Configuration
    TOP_RECOMMENDATIONS = 10
    MIN_COURSE_RATING = 4.0
    
    # Cache Configuration
    CACHE_ENABLED = True
    CACHE_TTL = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "skillsync.log"

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "INFO"

# Get configuration based on environment
ENV = os.getenv("ENV", "development")
config = ProductionConfig() if ENV == "production" else DevelopmentConfig()
