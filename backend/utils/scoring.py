from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize
import re

model = SentenceTransformer('all-mpnet-base-v2')  # More powerful model


def calculate_atis_score(text):
    """Calculate ATIS (Applicant Tracking System) score"""
    sentences = sent_tokenize(text)
    word_count = len(re.findall(r'\w+', text))

    # Score components
    length_score = min(word_count / 500, 1.0)  # Ideal ~500 words
    bullet_score = min(text.count('•') / 10, 1.0)  # At least 10 bullet points
    section_score = min((text.lower().count('experience') +
                         text.lower().count('education') +
                         text.lower().count('skills')) / 3, 1.0)

    return round((0.4 * length_score + 0.3 * bullet_score + 0.3 * section_score) * 100, 2)


def calculate_match_score(resume_text, jd_text, resume_skills, jd_skills):
    # Enhanced TF-IDF with n-grams
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    tfidf_score = (tfidf_matrix * tfidf_matrix.T).toarray()[0, 1]

    # Better BERT similarity
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)
    bert_score = util.pytorch_cos_sim(resume_embedding, jd_embedding).item()

    # Enhanced skill matching with skill levels
    matched_skills = list(set(resume_skills) & set(jd_skills))
    missing_skills = list(set(jd_skills) - set(resume_skills))

    # Skill score with weighting
    skill_score = len(matched_skills) / len(jd_skills) if jd_skills else 0

    # ATIS score
    atis_score = calculate_atis_score(resume_text)

    # Final weighted score
    final_score = (0.25 * tfidf_score +
                   0.35 * bert_score +
                   0.25 * skill_score +
                   0.15 * (atis_score / 100))

    return {
        'tfidf_score': round(tfidf_score, 2),
        'bert_score': round(bert_score, 2),
        'skill_score': round(skill_score, 2),
        'atis_score': atis_score,
        'final_score': round(final_score * 100, 2),
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'resume_length': len(re.findall(r'\w+', resume_text))
    }