import fitz
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk
import re
from typing import List, Tuple

nltk.data.path.append('/Users/Maverick/nltk_data')

# Enhanced skill database with categories and levels
SKILL_DATABASE = {
    "Programming Languages": {
        "python": {"level": 3, "synonyms": ["python3", "py"]},
        "java": {"level": 3, "synonyms": ["java8", "java 11"]},
        "javascript": {"level": 2, "synonyms": ["js", "es6"]}
    },
    "Frameworks": {
        "react": {"level": 2, "synonyms": ["reactjs"]},
        "node.js": {"level": 2, "synonyms": ["node", "express"]}
    },
    "Cloud & DevOps": {
        "aws": {"level": 3, "synonyms": ["amazon web services"]},
        "docker": {"level": 2, "synonyms": ["containerization"]}
    }
}


def extract_text_from_pdf(file) -> str:
    """Enhanced PDF text extraction with section awareness"""
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            blocks = page.get_text("blocks")
            for block in sorted(blocks, key=lambda b: (b[1], b[0])):  # Sort by position
                if block[4].strip():
                    text += block[4] + "\n"
    return text


def extract_skills_from_text(text: str) -> List[str]:
    """Enhanced skill extraction with context awareness"""
    text = text.lower()
    found_skills = set()

    # Check for skills in each category
    for category, skills in SKILL_DATABASE.items():
        for skill, data in skills.items():
            # Check main skill name
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                found_skills.add(f"{skill}|{data['level']}|{category}")

            # Check synonyms
            for synonym in data.get('synonyms', []):
                if re.search(r'\b' + re.escape(synonym) + r'\b', text):
                    found_skills.add(f"{skill}|{data['level']}|{category}")

    # Extract education level
    education = extract_education(text)
    if education:
        found_skills.add(f"{education}|3|Education")

    return list(found_skills)


def extract_education(text: str) -> str:
    """Extract highest education level"""
    text = text.lower()
    if "phd" in text or "doctorate" in text:
        return "PhD"
    elif "master" in text or "ms" in text or "mba" in text:
        return "Master's"
    elif "bachelor" in text or "bs" in text or "ba" in text:
        return "Bachelor's"
    return ""