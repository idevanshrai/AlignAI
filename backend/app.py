from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.parser import extract_text_from_pdf, extract_skills_from_text
from utils.scoring import calculate_match_score
from utils.gemini_analysis import get_gemini_insights
import nltk
import ssl
import os


# SSL Bypass for local development
ssl._create_default_https_context = ssl._create_unverified_context

# NLTK Setup
nltk_data_path = os.path.expanduser('~/nltk_data')
nltk.data.path.append(nltk_data_path)

required_nltk_data = ['punkt', 'stopwords', 'punkt_tab', 'averaged_perceptron_tagger']
for package in required_nltk_data:
    try:
        nltk.data.find(
            f'tokenizers/{package}' if 'punkt' in package else f'taggers/{package}' if 'perceptron' in package else f'corpora/{package}')
    except LookupError:
        nltk.download(package, download_dir=nltk_data_path)

app = Flask(__name__)
CORS(app)


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'Missing resume file'}), 400
    if 'jobdesc' not in request.form:
        return jsonify({'error': 'Missing job description'}), 400

    try:
        resume_file = request.files['resume']
        jobdesc_text = request.form['jobdesc']

        resume_text = extract_text_from_pdf(resume_file)
        resume_skills = extract_skills_from_text(resume_text)
        jd_skills = extract_skills_from_text(jobdesc_text)

        # Calculate scores
        result = calculate_match_score(resume_text, jobdesc_text, resume_skills, jd_skills)

        # Get Gemini insights
        gemini_analysis = get_gemini_insights(resume_text, jobdesc_text, result)
        result.update(gemini_analysis)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)