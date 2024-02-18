# Resume Matcher

A Python library for matching resumes with job description.

## Installation

You can install the required dependencies using pip:

<b>pip install resume-matcher</b>

## Usage

Here's how you can use the <b>resume_job_desc_match</b> function:

from resume_matcher.matching import resume_job_desc_match

<b>Path to the resume and job description files</b><br>
resume_path = "My_Resume.docx"
job_desc_path = "Job_desc.docx"

<b>Call the resume_job_desc_match function</b><br>
match_percentage = resume_job_desc_match(resume_path, job_desc_path)

<b>Print the match percentage</b><br>
print("Match percentage:", match_percentage)

<b>Overall Code:</b><br>

from resume_matcher.matching import resume_job_desc_match

resume_path = "My_Resume.docx"<br>
job_desc_path = "Job_desc.docx"

match_percentage = resume_job_desc_match(resume_path, job_desc_path)

print("Match percentage:", match_percentage)

<b>Note:</b> Please upload doc files of Job Description and Resume.




