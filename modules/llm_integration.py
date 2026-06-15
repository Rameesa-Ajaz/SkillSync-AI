# modules/llm_integration.py
"""Professional LLM integration with Google Gemini (FREE)"""

import google.generativeai as genai
import logging
from config import config
from functools import lru_cache

logger = logging.getLogger(__name__)

class GeminiIntegration:
    """Free Google Gemini AI integration"""
    
    def __init__(self):
        if config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini AI successfully configured.")
            except Exception as e:
                self.model = None
                logger.error(f"Error configuring Gemini: {str(e)}")
        else:
            self.model = None
            logger.warning("Gemini API key not configured")
    
    def get_skill_explanation(self, skill: str, job_role: str) -> str:
        """Get AI explanation for a skill"""
        if not self.model:
            return f"{skill} is essential for success in a {job_role} role, as it forms a core technical competency for solving complex problems."
        
        try:
            prompt = f"""
            Explain briefly (2-3 sentences) why {skill} is important for a {job_role}.
            Be concise and professional.
            """
            
            response = self.model.generate_content(prompt)
            logger.info(f"Generated explanation for {skill}")
            return response.text
        
        except Exception as e:
            logger.error(f"Error getting explanation: {str(e)}")
            return f"Proficiency in {skill} is critical for {job_role} to ensure high-quality delivery and technical excellence."
    
    def generate_cover_letter(self, name: str, job_role: str, skills: list) -> str:
        """Generate professional cover letter"""
        if not self.model:
            return "Cover letter generation unavailable (API Key missing)"
        
        try:
            skills_text = ", ".join(skills[:5])
            prompt = f"""
            Write a professional cover letter for {name} applying for a {job_role} position.
            Key skills: {skills_text}
            Keep it to 3-4 paragraphs.
            """
            
            response = self.model.generate_content(prompt)
            logger.info(f"Generated cover letter for {name}")
            return response.text
        
        except Exception as e:
            logger.error(f"Error generating cover letter: {str(e)}")
            return "Cover letter generation failed due to an API error."
    
    def get_career_advice(self, profile: dict) -> str:
        """Get personalized career advice"""
        if not self.model:
            return "Career advice unavailable (API Key missing)"
        
        try:
            prompt = f"""
            Provide brief career advice for a professional with:
            - GPA: {profile.get('gpa', 'Unknown')}
            - Skills: {', '.join(profile.get('skills', [])[:5])}
            - Experience: {profile.get('years_experience', 0)} years
            Keep response to 2-3 sentences.
            """
            
            response = self.model.generate_content(prompt)
            logger.info("Generated career advice")
            return response.text
        
        except Exception as e:
            logger.error(f"Error getting career advice: {str(e)}")
            return "Unable to generate personalized advice at this time."
    
    @lru_cache(maxsize=128)
    def answer_question(self, question: str) -> str:
        """Answer user questions using FREE Gemini"""
        if not self.model:
            return "AI assistance unavailable (API Key missing)"
        
        try:
            response = self.model.generate_content(question)
            logger.info("Answered user question")
            return response.text
        
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return "I am currently unable to answer that question. Please try again later."
