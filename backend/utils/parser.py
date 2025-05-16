import fitz
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import re

nltk.data.path.append('/Users/Maverick/nltk_data')

SKILL_KEYWORDS = {
    # Programming Languages
    'python': {'level': 2, 'synonyms': ['python3', 'python 3']},
    'java': {'level': 2},
    'javascript': {'level': 2, 'synonyms': ['js', 'es6']},

    # Frameworks
    'react': {'level': 2},
    'node.js': {'level': 2, 'synonyms': ['node', 'nodejs']},

    # Cloud
    'aws': {'level': 3},
    'docker': {'level': 2},

    # Add more skills with levels (1=basic, 2=intermediate, 3=advanced)
}


def extract_text_from_pdf(file):
    """Extract text with formatting awareness"""
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            blocks = page.get_text("blocks")
            for block in blocks:
                if block[4].strip():  # The actual text
                    text += block[4] + "\n"
    return text


def extract_skills_from_text(text):
    """Enhanced skill extraction with levels"""
    text = text.lower()
    found_skills = set()

    # Check for exact matches and synonyms
    for skill, data in SKILL_KEYWORDS.items():
        # Check main skill name
        if skill in text:
            found_skills.add(f"{skill}|{data['level']}")

        # Check synonyms
        for synonym in data.get('synonyms', []):
            if synonym in text:
                found_skills.add(f"{skill}|{data['level']}")

    return list(found_skills)