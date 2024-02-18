import docx2txt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def resume_job_desc_match(resume,job_desc):
    job_desc = docx2txt.process(job_desc)
    resume = docx2txt.process(resume)
    content = [resume,job_desc]
    cv = CountVectorizer()
    matrix = cv.fit_transform(content)
    similarity_matrix = cosine_similarity(matrix)
    match_percentage = similarity_matrix[0][1]*100
    return f"{round(match_percentage, 2)}%"

