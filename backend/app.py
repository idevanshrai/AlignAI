from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.parser import extract_text_from_pdf, extract_skills_from_text
from utils.scoring import calculate_match_score
from utils.gemini_analysis import get_gemini_insights
import nltk
import os
import logging
import numpy as np
import datetime
from typing import Dict, Any, List
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# NLTK Setup
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Memory optimization settings
if torch.cuda.is_available():
    torch.cuda.empty_cache()

app = Flask(__name__)
# Enable CORS with explicit configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# Configure app for better memory handling
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB
app.config['PROPAGATE_EXCEPTIONS'] = True

def convert_numpy_types(obj):
    """Convert numpy types to native Python types"""
    if isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    return obj

def format_gemini_analysis(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Format Gemini analysis to match frontend expectations"""
    return {
        'improvements': [item.get('description', '') for item in analysis.get('improvements', [])],
        'missing_qualifications': [item.get('skill', '') for item in analysis.get('missing_qualifications', [])],
        'suggested_keywords': analysis.get('keywords', {}).get('missing', []),
        'formatting_suggestions': ' '.join(analysis.get('formatting', {}).get('suggestions', []))
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'Missing resume file'}), 400
    if 'jobdesc' not in request.form:
        return jsonify({'error': 'Missing job description'}), 400

    try:
        # Process files
        resume_file = request.files['resume']
        jobdesc_text = request.form['jobdesc']

        # Extract text and skills
        resume_text = extract_text_from_pdf(resume_file)
        resume_skills = extract_skills_from_text(resume_text)
        jd_skills = extract_skills_from_text(jobdesc_text)

        # Calculate scores
        scores = calculate_match_score(resume_text, jobdesc_text, resume_skills, jd_skills)
        logger.info(f"Scores calculated: {scores}")

        # Convert numpy types to native Python types
        scores = convert_numpy_types(scores)

        # Get Gemini analysis
        required_scores = {
            'final_score': scores.get('final_score', 0),
            'skill_score': scores.get('skill_score', 0),
            'experience_score': min(scores.get('experience_score', 0), 1.0),
            'atis_score': scores.get('atis_score', 0)
        }
        gemini_analysis = get_gemini_insights(resume_text, jobdesc_text, required_scores)
        logger.info("Gemini analysis completed")

        response = {
            'final_score': round(float(scores.get('final_score', 0))),  # Fixed: Added missing parenthesis
            'tfidf_score': round(float(scores.get('tfidf_score', 0)), 2),
            'bert_score': round(float(scores.get('bert_score', 0)), 2),
            'skill_score': round(float(scores.get('skill_score', 0)), 2),
            'atis_score': round(float(scores.get('atis_score', 0))),
            'resume_length': int(scores.get('resume_length', 0)),
            'matched_skills': list(scores.get('matched_skills', [])),
            'missing_skills': list(scores.get('missing_skills', [])),
            **format_gemini_analysis(gemini_analysis)
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'final_score': 0,
            'tfidf_score': 0,
            'bert_score': 0,
            'skill_score': 0,
            'atis_score': 0,
            'resume_length': 0,
            'matched_skills': [],
            'missing_skills': [],
            'improvements': ['Analysis failed: ' + str(e)],
            'missing_qualifications': [],
            'suggested_keywords': [],
            'formatting_suggestions': ''
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)