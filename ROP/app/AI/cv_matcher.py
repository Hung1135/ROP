import re
import pdfplumber
from docx import Document
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs).strip()


def extract_cv_text(file_path):
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    if file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)
    return ""

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9\s\+\#\.]', ' ', text)
    return text.strip()

def text_to_vector(text):
    return model.encode(text)

def cosine_score(vec1, vec2):
    return float(cosine_similarity([vec1], [vec2])[0][0])

# def match_cv_with_job(cv_text, job_text):
#     if not cv_text or not job_text:
#         return 0, "Thấp"

#     cv_text = clean_text(cv_text)
#     job_text = clean_text(job_text)

#     cv_vec = text_to_vector(cv_text)
#     job_vec = text_to_vector(job_text)

#     score = cosine_score(cv_vec, job_vec)
#     percent = round(score * 100, 2)

#     if percent >= 80:
#         level = "Rất phù hợp"
#     elif percent >= 60:
#         level = "Phù hợp"
#     elif percent >= 40:
#         level = "Trung bình"
#     else:
#         level = "Thấp"

#     return percent, level
# cv_matcher.py
def match_cv_fields(cv_data, job):
    """
    cv_data: dict với các field như description, skills, address
    job: object Job
    Trả về điểm % tổng hợp, mức độ và chi tiết từng field
    Trọng số: requirements 50%, skills 40%, location 10%
    """
    weights = {
        "requirements": 0.5,
        "skills": 0.4,
        "location": 0.1
    }

    # 1. Description ↔ Requirements
    cv_desc = clean_text(cv_data.get("description", ""))
    job_req = clean_text(job.requirements or "")
    score_req = cosine_score(text_to_vector(cv_desc), text_to_vector(job_req))

    # 2. Skills ↔ Skills
    cv_skills = clean_text(cv_data.get("skills", ""))
    job_skills = clean_text(job.skills or "")
    score_skills = cosine_score(text_to_vector(cv_skills), text_to_vector(job_skills))

    # 3. Address ↔ Location
    cv_address = clean_text(cv_data.get("address", ""))
    job_location = clean_text(job.location or "")
    score_location = cosine_score(text_to_vector(cv_address), text_to_vector(job_location))

    # Tổng weighted score
    total_score = score_req * weights["requirements"] + \
                  score_skills * weights["skills"] + \
                  score_location * weights["location"]

    percent = round(total_score * 100, 2)

    if percent >= 80:
        level = "Rất phù hợp"
    elif percent >= 60:
        level = "Phù hợp"
    elif percent >= 40:
        level = "Trung bình"
    else:
        level = "Thấp"

    return percent, level, {
        "requirements_score": round(score_req * 100 *0.5, 2),
        "skills_score": round(score_skills * 100*0.4, 2),
        "location_score": round(score_location * 100*0.1, 2)
    }


