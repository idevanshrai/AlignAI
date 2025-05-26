from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import re
from collections import defaultdict
import logging
import torch
import gc

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize models lazily
model = None
tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words='english', max_features=5000)

def get_model():
    global model
    if model is None:
        try:
            # Set device
            device = torch.device('cpu')
            # Load model with minimal memory usage
            model = SentenceTransformer('all-mpnet-base-v2', device=device)
            # Clear CUDA cache if using GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return None
    return model

def cleanup_memory():
    """Clean up memory after processing"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

def calculate_atis_score(text):
    """Enhanced ATIS (Applicant Tracking System) score calculation"""
    try:
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        word_count = len(words)

        # Score components with enhanced weights
        scores = {
            'length': min(word_count / 600, 1.0),
            'bullet_points': min(text.count('•') / 12, 1.0),
            'sections': min((text.lower().count('experience') +
                            text.lower().count('education') +
                            text.lower().count('skills') +
                            text.lower().count('project')) / 4, 1.0),
            'action_verbs': min(len(re.findall(r'\b(led|developed|implemented|managed|created)\b', text, re.I)) / 10, 1.0),
            'quantifiable': min(len(re.findall(r'\b(\d+%|\$?\d+[KM]?|increased|reduced|improved)\b', text)) / 5, 1.0)
        }

        # Weighted score calculation
        weights = {
            'length': 0.25,
            'bullet_points': 0.2,
            'sections': 0.25,
            'action_verbs': 0.15,
            'quantifiable': 0.15
        }

        atis_score = sum(scores[component] * weights[component] for component in scores)
        return round(atis_score * 100, 2)
    except Exception as e:
        logger.error(f"Error calculating ATIS score: {str(e)}")
        return 0

def calculate_skill_match(resume_skills, jd_skills):
    """Enhanced skill matching with level consideration"""
    try:
        if not jd_skills:
            return 0, [], []

        # Extract skill levels
        resume_skill_map = {skill.split('|')[0]: float(skill.split('|')[1]) for skill in resume_skills if '|' in skill}
        jd_skill_map = {skill.split('|')[0]: float(skill.split('|')[1]) for skill in jd_skills if '|' in skill}

        matched = []
        missing = []

        for skill, jd_level in jd_skill_map.items():
            if skill in resume_skill_map:
                resume_level = resume_skill_map[skill]
                level_match = min(resume_level / jd_level, 1.0)
                matched.append((skill, level_match))
            else:
                missing.append(skill)

        total_possible = sum(jd_skill_map.values())
        actual_score = sum(level for _, level in matched)
        skill_score = actual_score / total_possible if total_possible > 0 else 0

        return skill_score, [m[0] for m in matched], missing
    except Exception as e:
        logger.error(f"Error calculating skill match: {str(e)}")
        return 0, [], []

def calculate_experience_match(resume_text, jd_text):
    """Calculate experience alignment with normalization to 0-1 range"""
    try:
        # Extract years of experience patterns
        resume_exp = max([float(num) for num in re.findall(r'(\d+)\+? years?', resume_text, re.I)] or [0])
        jd_exp = max([float(num) for num in re.findall(r'(\d+)\+? years?', jd_text, re.I)] or [0])

        if jd_exp == 0:
            return 1.0  # No experience requirement

        exp_match = min(resume_exp / jd_exp, 1.5)  # Cap at 1.5x required experience
        return round(min(exp_match, 1.0), 2)  # Normalize to 0-1.0 range
    except Exception as e:
        logger.error(f"Error calculating experience match: {str(e)}")
        return 0

def calculate_match_score(resume_text, jd_text, resume_skills, jd_skills):
    """Enhanced scoring algorithm with multiple dimensions"""
    try:
        # Text Relevance (TF-IDF)
        tfidf_matrix = tfidf_vectorizer.fit_transform([resume_text, jd_text])
        tfidf_score = (tfidf_matrix * tfidf_matrix.T).toarray()[0, 1]

        # Semantic Match (BERT)
        model = get_model()
        if model is None:
            bert_score = 0
        else:
            with torch.no_grad():  # Disable gradient calculation
                try:
                    resume_embedding = model.encode(resume_text, convert_to_tensor=True, show_progress_bar=False)
                    jd_embedding = model.encode(jd_text, convert_to_tensor=True, show_progress_bar=False)
                    bert_score = float(util.pytorch_cos_sim(resume_embedding, jd_embedding).item())
                    # Clear memory
                    del resume_embedding
                    del jd_embedding
                except Exception as e:
                    logger.error(f"Error in BERT encoding: {str(e)}")
                    bert_score = 0
                finally:
                    cleanup_memory()

        # Skill Matching
        skill_score, matched_skills, missing_skills = calculate_skill_match(resume_skills, jd_skills)

        # Experience Matching
        experience_score = calculate_experience_match(resume_text, jd_text)

        # ATIS Compliance
        atis_score = calculate_atis_score(resume_text)

        # Education Matching
        education_match = 1.0 if any(edu in resume_text.lower() for edu in ['bachelor', 'master', 'phd']) else 0.5

        # Final weighted score
        weights = {
            'tfidf': 0.2,
            'bert': 0.3,
            'skills': 0.2,
            'experience': 0.15,
            'atis': 0.1,
            'education': 0.05
        }

        final_score = (
            weights['tfidf'] * tfidf_score +
            weights['bert'] * bert_score +
            weights['skills'] * skill_score +
            weights['experience'] * experience_score +
            weights['atis'] * (atis_score / 100) +  # Normalize to 0-1
            weights['education'] * education_match
        )

        return {
            'tfidf_score': round(tfidf_score, 2),
            'bert_score': round(bert_score, 2),
            'skill_score': round(skill_score, 2),
            'experience_score': round(experience_score, 2),
            'atis_score': round(atis_score, 2),
            'education_match': round(education_match, 2),
            'final_score': round(final_score * 100, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'resume_length': len(re.findall(r'\w+', resume_text)),
            'keywords': tfidf_vectorizer.get_feature_names_out().tolist()[:20]
        }
    except Exception as e:
        logger.error(f"Error calculating match score: {str(e)}")
        return {
            'tfidf_score': 0,
            'bert_score': 0,
            'skill_score': 0,
            'experience_score': 0,
            'atis_score': 0,
            'education_match': 0,
            'final_score': 0,
            'matched_skills': [],
            'missing_skills': [],
            'resume_length': 0,
            'keywords': []
        }