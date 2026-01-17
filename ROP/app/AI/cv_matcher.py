import re
import os
import logging
import pdfplumber
from docx import Document

from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.pdfdocument import PDFTextExtractionNotAllowed
from pdfminer.psparser import PSEOF

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ================== LOGGING ==================
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s"
)
logger = logging.getLogger(__name__)


# ================== MODEL ==================
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# ================== CV EXTRACT ==================
def extract_text_from_pdf(file_path: str) -> str:
    if not os.path.exists(file_path):
        logger.error("❌ PDF không tồn tại: %s", file_path)
        return ""

    if os.path.getsize(file_path) == 0:
        logger.error("❌ PDF rỗng (0 bytes): %s", file_path)
        return ""

    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except (PDFSyntaxError, PDFTextExtractionNotAllowed, PSEOF) as e:
        logger.error("❌ PDF lỗi cấu trúc (%s): %s", file_path, e)
        return ""
    except Exception as e:
        logger.exception("❌ Lỗi đọc PDF (%s): %s", file_path, e)
        return ""

    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        logger.exception("❌ Lỗi đọc DOCX (%s): %s", file_path, e)
        return ""


def extract_cv_text(file_path: str) -> str:
    if not file_path:
        return ""

    file_path = file_path.lower()
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    if file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)

    logger.warning("⚠️ Định dạng CV không hỗ trợ: %s", file_path)
    return ""


# ================== TEXT PROCESSING ==================
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s\.\+\#]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> set:
    text = clean_text(text)
    return set(re.findall(r"\w+", text, flags=re.UNICODE))


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def text_to_vector(text: str):
    return model.encode(text)


def cosine_score(vec1, vec2) -> float:
    return float(cosine_similarity([vec1], [vec2])[0][0])

<<<<<<< HEAD

# ================== SPLIT CV & JD ==================
def split_cv_lines(cv_text: str) -> list:
    raw_parts = re.split(r"\n|•|-|–|—|;\s|\. ", cv_text)
    parts = []

    for p in raw_parts:
        p = clean_text(p)
        if not p:
            continue

        # bỏ nhiễu
        if re.search(r"\b\d{9,}\b", p):  # phone / id
            continue
        if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", p):
            continue
        if len(p.split()) < 3:
            continue

        parts.append(p)

    return parts


def split_jd_items(text: str) -> list:
    if not text:
        return []

    items = [
        clean_text(x)
        for x in re.split(r"\n|•|-|–|—|;\s|\. ", text)
        if clean_text(x)
    ]

    return [i for i in items if len(i.split()) >= 2]


# ================== MATCHING ==================
def match_list_score(cv_text, jd_text, section_name="Section", threshold=0.5) -> float:
    cv_lines = split_cv_lines(cv_text)
    jd_items = split_jd_items(jd_text)

    if not cv_lines or not jd_items:
        logger.info("[%s] Không có dữ liệu để so khớp", section_name)
        return 0.0

    # 🔥 TỐI ƯU: encode CV 1 lần
    cv_vectors = {line: text_to_vector(line) for line in cv_lines}

    kept_scores = []

    for item in jd_items:
        item_vec = text_to_vector(item)
        best_score = -1
        best_line = None

        for line in cv_lines:
            raw_cos = cosine_score(cv_vectors[line], item_vec)
            overlap = jaccard(tokenize(line), tokenize(item))
            combined = 0.7 * raw_cos + 0.3 * overlap

            if combined > best_score:
                best_score = combined
                best_line = line

        logger.debug(
            "[%s] JD: %s\n    CV: %s\n    Score: %.2f",
            section_name, item, best_line, best_score
        )

        if best_score >= threshold:
            kept_scores.append(best_score)

    return round((sum(kept_scores) / len(kept_scores)) * 100, 2) if kept_scores else 0.0


def match_cv_with_job_advanced(cv_text, job):
    if not cv_text:
        return 0, 0, 0, "Thấp"

    logger.info("===== CV CONTENT =====\n%s", cv_text)
    logger.info(
        "===== JOB =====\nTitle: %s\nDesc: %s\nReq: %s\nSkill: %s\nBenefit: %s",
        job.title,
        job.description or "",
        job.requirements or "",
        job.skills or "",
        job.benefit or ""
    )

    req_score = match_list_score(cv_text, job.requirements or "", "Requirement", 0.5)
    skill_score = match_list_score(cv_text, job.skills or "", "Skill", 0.5)
    desc_score = match_list_score(cv_text, job.description or "", "Description", 0.45)

    ai_score = round(0.6 * skill_score + 0.3 * req_score + 0.1 * desc_score, 2)

    if ai_score >= 80:
        level = "Rất phù hợp"
    elif ai_score >= 60:
        level = "Phù hợp"
    elif ai_score >= 40:
        level = "Trung bình"
    else:
        level = "Thấp"

    return percent, level
=======
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
        "requirements_score": round(score_req * 100, 2),
        "skills_score": round(score_skills * 100, 2),
        "location_score": round(score_location * 100, 2)
    }

>>>>>>> ed43d9ff39add11f2b9531724ec144fd60f73e10

    return skill_score, req_score, ai_score, level
