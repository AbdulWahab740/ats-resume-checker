import spacy as sp
import docx
from pyresparser import ResumeParser
import re
from script.score import get_score
from pypdf import PdfReader

nlp = sp.load("en_core_web_sm")

# Constants
Keyword = 0.65
Formatting = 0.05
skills = 0.30

def docs_to_words(path):
    doc = docx.Document(path)
    data = []
    for paragraph in doc.paragraphs:
        data.append(paragraph.text)
    return "\n".join(data)

def extract_skills_text(path):
    file_extension = path.split(".")[-1].lower()
    if file_extension not in ["pdf", "docx", "doc"]:
        raise ValueError("Unsupported file format")
    resume = path
    text = ""
    if file_extension == "pdf":
            text = pdf_reader(resume)
    elif file_extension in ["docx","doc"]: text = docs_to_words(resume)
    try:
        skills_text = text.split("skills", 1)[1].strip()
        skills = skills_text.split()
        return skills
    except IndexError:
        print("No skills section found.")
        return []
        
def pdf_reader(path):
    text = ""
    reader = PdfReader(path)
    for page in reader.pages:
        text += page.extract_text() or ""  # Avoid NoneType issues
    return text

def keyword_test(docdata, jobReq):
    responses = get_score(docdata, jobReq)
    score = [response.score for response in responses]
    # print(score[0] * 100)
    return score[0] * 100

def formating_check(text):
    table_check = bool(re.search(r'<table>', text, re.IGNORECASE))
    image_check = bool(re.search(r'<img', text, re.IGNORECASE))
    special_char_check = bool(re.search(r'[^\x00-\x7F]+', text))
    issues = {'tables_found': table_check, 'images_found': image_check, 'special_chars': special_char_check}
    print("Issues: ", sum(issues.values()))
    score_deduction = sum(issues.values()) * 10
    return max(30 - score_deduction, 0)

def skill_check(resume, skillsReq):
    skills_text = extract_skills_text(resume)
    count = [skill for skill in skillsReq if skill.lower() in skills_text]
    if len(skillsReq) == 0:
        return 0
    percentage = len(count) / len(skillsReq) * 100
    return percentage
