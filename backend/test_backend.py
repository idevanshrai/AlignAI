import requests

# URL of your running backend
url = "http://127.0.0.1:5000/analyze"

# Corrected paths relative to 'backend' folder where script is run
resume_path = "../frontend/assets/RESUME.pdf"  # Resume
jd_path = "../frontend/assets/job_description.pdf"  # Job Description

with open(resume_path, "rb") as resume_file, open(jd_path, "rb") as jd_file:
    files = {
        "resume": ("resume.pdf", resume_file, "application/pdf"),
        "jd": ("job_description.pdf", jd_file, "application/pdf"),
    }

    response = requests.post(url, files=files)

print(response.status_code)
print(response.json())
