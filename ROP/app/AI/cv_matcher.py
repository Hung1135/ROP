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

def match_cv_with_job(cv_text, job_text):
    if not cv_text or not job_text:
        return 0, "Thấp"

    cv_text = clean_text(cv_text)
    job_text = clean_text(job_text)

    cv_vec = text_to_vector(cv_text)
    job_vec = text_to_vector(job_text)

    score = cosine_score(cv_vec, job_vec)
    percent = round(score * 100, 2)

    if percent >= 80:
        level = "Rất phù hợp"
    elif percent >= 60:
        level = "Phù hợp"
    elif percent >= 40:
        level = "Trung bình"
    else:
        level = "Thấp"

    return percent, level

