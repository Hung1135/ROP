# import logging
# def match_cv_with_job(cv_text, job_text):
#     if not cv_text or not job_text:
#         return 0, "Thấp"

#     cv_text = clean_text(cv_text)
#     job_text = clean_text(job_text)

#     cv_vec = text_to_vector(cv_text)
#     job_vec = text_to_vector(job_text)

    # logger = logging.getLogger(__name__)

    # logger.debug("CV Vector: %s", cv_vec)
    # logger.info("Job Vector: %s", job_vec)

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