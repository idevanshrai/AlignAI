import google.generativeai as genai
import os
import json
import re
from typing import Dict, Any
import logging

# Configure logging
logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('models/gemini-1.5-flash')

def get_gemini_insights(resume_text: str, jd_text: str, scores: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced AI-powered resume analysis with structured output"""
    # Validate and normalize scores
    normalized_scores = {
        'final_score': min(max(scores.get('final_score', 0), 0), 100),
        'skill_score': min(max(scores.get('skill_score', 0.0), 0.0), 1.0),
        'experience_score': min(max(scores.get('experience_score', 0.0), 0.0), 1.0),
        'atis_score': min(max(scores.get('atis_score', 0), 0), 100)
    }

    prompt = f"""
    **Resume Analysis Report**

    **Job Requirements Analysis:**
    {jd_text[:5000]}

    **Resume Content:**
    {resume_text[:10000]}

    **Current Assessment Scores:**
    - Overall Match: {normalized_scores['final_score']}/100
    - Skill Match: {normalized_scores['skill_score']}/1.0
    - Experience Match: {normalized_scores['experience_score']}/1.0
    - ATS Compliance: {normalized_scores['atis_score']}/100

    **Analysis Tasks:**
    1. Identify 3 specific improvements with actionable recommendations
    2. List missing qualifications with importance level
    3. Highlight 2 key strengths with evidence
    4. Identify 2 weaknesses with improvement suggestions
    5. Recommend 5-10 keywords to include
    6. Provide formatting optimization tips
    7. Generate personalized summary

    **Output Format (JSON):**
    {{
      "improvements": [
        {{
          "title": "Improvement area",
          "description": "Specific suggestion",
          "impact": "High/Medium/Low",
          "example": "Concrete example from resume"
        }}
      ],
      "missing_qualifications": [
        {{
          "skill": "Missing qualification",
          "importance": "Essential/Nice-to-have",
          "suggestion": "How to acquire"
        }}
      ],
      "strengths": [
        {{
          "title": "Strength name",
          "evidence": "Specific example",
          "relevance": "How it matches job"
        }}
      ],
      "weaknesses": [
        {{
          "title": "Weakness area",
          "description": "Specific issue",
          "suggestion": "Improvement strategy"
        }}
      ],
      "keywords": {{
        "missing": ["list", "of", "keywords"],
        "present": ["list", "of", "matched", "keywords"]
      }},
      "formatting": {{
        "issues": ["list", "of", "formatting", "issues"],
        "suggestions": ["specific", "formatting", "tips"]
      }},
      "summary": "2-3 paragraph personalized summary with overall fit assessment",
      "salary_estimate": {{
        "range": "Estimated salary range based on match",
        "confidence": "High/Medium/Low"
      }}
    }}
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 3000,
                "top_p": 0.9
            }
        )
        return parse_response(response.text)
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return get_fallback_response()

def parse_response(text: str) -> Dict[str, Any]:
    """Enhanced response parsing with validation"""
    try:
        # Clean response text
        text = text.replace("```json", "").replace("```", "").strip()

        # Parse JSON with basic validation
        result = json.loads(text)

        # Validate structure
        required_keys = ['improvements', 'missing_qualifications', 'strengths',
                       'weaknesses', 'keywords', 'formatting', 'summary']
        for key in required_keys:
            if key not in result:
                raise ValueError(f"Missing required key: {key}")

        return result
    except Exception as e:
        logger.error(f"Error parsing response: {str(e)}")
        return get_fallback_response()

def get_fallback_response() -> Dict[str, Any]:
    """Comprehensive fallback response"""
    return {
        "improvements": [{
            "title": "Keyword Optimization",
            "description": "Add more job-specific keywords from the description",
            "impact": "High",
            "example": None
        }],
        "missing_qualifications": [{
            "skill": "Job-specific skills",
            "importance": "Essential",
            "suggestion": "Review job description for required skills"
        }],
        "strengths": [{
            "title": "Relevant Experience",
            "evidence": "Matching work history found",
            "relevance": "High"
        }],
        "weaknesses": [{
            "title": "Formatting",
            "description": "Could improve resume structure",
            "suggestion": "Use standard sections (Experience, Education, Skills)"
        }],
        "keywords": {
            "missing": [],
            "present": []
        },
        "formatting": {
            "issues": ["Could improve readability"],
            "suggestions": ["Use bullet points for achievements"]
        },
        "summary": "Your resume shows potential but could be better optimized for this position. Focus on adding specific keywords and quantifiable achievements.",
        "salary_estimate": {
            "range": "Not available",
            "confidence": "Low"
        }
    }