import google.generativeai as genai
import os
import json
import re

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('models/gemini-1.5-flash')


def get_gemini_insights(resume_text, jd_text, scores):
    """Get AI-powered resume analysis from Gemini"""
    prompt = f"""
    **Resume Analysis Task**

    **Resume Text** (first 10,000 characters):
    {resume_text[:10000]}

    **Job Description** (first 5,000 characters):
    {jd_text[:5000]}

    **Current Assessment Scores**:
    - Text Relevance (TF-IDF): {scores['tfidf_score']}/1.0
    - Semantic Match (BERT): {scores['bert_score']}/1.0  
    - Skill Match: {scores['skill_score']}/1.0
    - ATS Compliance: {scores['atis_score']}/100

    **Required Output Format** (STRICTLY FOLLOW THIS JSON STRUCTURE):
    {{
      "improvements": [
        "Specific actionable improvement 1",
        "Specific actionable improvement 2",
        "Specific actionable improvement 3"
      ],
      "missing_qualifications": [
        "Missing qualification 1 with explanation",
        "Missing qualification 2 with explanation"
      ],
      "strengths": [
        "Key strength 1 with evidence",
        "Key strength 2 with evidence"
      ],
      "weaknesses": [
        "Key weakness 1 with suggestions",
        "Key weakness 2 with suggestions"
      ],
      "suggested_keywords": ["keyword1", "keyword2", "keyword3"],
      "formatting_suggestions": "Specific formatting recommendations",
      "overall_feedback": "2-3 sentence summary of fit for position"
    }}

    **Analysis Guidelines**:
    1. Be specific and actionable in all suggestions
    2. Reference exact phrases from resume/JD when possible
    3. Prioritize suggestions that will most improve scores
    4. Consider both content and formatting aspects
    5. Provide concrete examples for improvements
    """

    try:
        # Use more controlled generation configuration
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,  # More deterministic output
                "max_output_tokens": 2000,
                "top_p": 0.95
            }
        )

        # Improved parsing
        return extract_structured_response(response.text)
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return {
            "error": "AI analysis unavailable",
            "improvements": ["Ensure your resume matches keywords from the job description"],
            "missing_qualifications": ["Check the job description for required qualifications"],
            "strengths": [],
            "weaknesses": [],
            "suggested_keywords": [],
            "formatting_suggestions": "Use standard resume formatting with clear sections",
            "overall_feedback": "Basic analysis complete. For detailed feedback, check the scores."
        }


def extract_structured_response(text):
    """More robust response parsing"""
    try:
        # First try to find JSON markdown
        json_match = re.search(r'```json\n({.*?})\n```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # Fallback to finding raw JSON
        json_str = text[text.find('{'):text.rfind('}') + 1]
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Fallback to manual parsing if JSON is malformed
        return parse_unstructured_response(text)


def parse_unstructured_response(text):
    """Parse unstructured Gemini response"""
    result = {
        "improvements": [],
        "missing_qualifications": [],
        "strengths": [],
        "weaknesses": [],
        "suggested_keywords": [],
        "formatting_suggestions": "",
        "overall_feedback": ""
    }

    # Extract improvements
    improvements = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\n\n|$)', text)
    if improvements and len(improvements) >= 3:
        result["improvements"] = improvements[:3]

    # Extract other sections similarly...
    # (Implementation would continue with more regex patterns)

    return result