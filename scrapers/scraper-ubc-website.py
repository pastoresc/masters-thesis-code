import requests
from bs4 import BeautifulSoup
import csv
import re

# Input and output
PROGRAM_URL = "https://www.grad.ubc.ca/prospective-students/graduate-degree-programs/master-of-science-computer-science"
SECONDARY_URL = "https://www.cs.ubc.ca/students/grad/prospective-grads/grad-programs/full-time-masters-programs"
OUTPUT_CSV = "ubc_website_data.csv"
PROGRAM_ID = "UBC001"

# Load pages
main_res = requests.get(PROGRAM_URL)
main_soup = BeautifulSoup(main_res.content, "html.parser")

secondary_res = requests.get(SECONDARY_URL)
secondary_text = secondary_res.text.lower()

# Helper
def get_text_safe(selector):
    el = main_soup.select_one(selector)
    return el.get_text(strip=True) if el else "Not Specified"

# Static fields
program_title = get_text_safe("h1")
institution = "University of British Columbia"
location = "Vancouver, Canada"
language = "English"
study_format = "Full-time"
degree_type = "MSc"
specialization = "Not Specified"
modality = "On Campus"

# Duration
duration = "Not Specified"
if re.search(r"\btwo[-\s]year\b", secondary_text):
    duration = "4 semesters"

# Total Credits
total_credits = "Not Specified"
patterns = [
    r"12[-\s]credit.*?thesis.*?18[-\s]credits",
    r"6[-\s]credit.*?thesis.*?24[-\s]credits",
    r"3[-\s]credit.*?essay.*?27[-\s]credits"
]
matches = [bool(re.search(p, secondary_text)) for p in patterns]
if sum(matches) >= 2:
    total_credits = "30 credits"

# Language Admission Requirements
language_admission = "Not Specified"
main_text = main_soup.get_text(separator=" ").replace("\n", " ")
toefl_match = re.search(r"\bTOEFL\b.*?\b100\b", main_text, re.IGNORECASE)
ielts_match = re.search(r"\bIELTS\b.*?\b7\.0\b", main_text, re.IGNORECASE)
if toefl_match and ielts_match:
    language_admission = "TOEFL iBT: 100 overall, IELTS Academic: 7.0 overall"

# Tuition Fees
tuition_fees = "Not Specified"
tuition_div = main_soup.find("div", class_="pane-node-field-prog-tuition")
if tuition_div:
    table = tuition_div.find("table")
    if table:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 3 and "tuition" in cells[0].text.lower() and "per year" in cells[0].text.lower():
                domestic_fee = cells[1].get_text(strip=True)
                international_fee = cells[2].get_text(strip=True)
                tuition_fees = f"{domestic_fee} CAD (Domestic) / {international_fee} CAD (International)"
                break

# Academic Admission Requirements
academic_admission = "Not Specified"
min_req_header = main_soup.find(lambda tag: tag.name in ["h3", "h4"] and "Minimum Academic Requirements" in tag.text)
if min_req_header:
    para = min_req_header.find_next_sibling("p")
    if para:
        text = para.get_text(strip=True)
        if "minimum admission requirements" in text.lower() and "b+" in text.lower():
            academic_admission = text

# Save to CSV
header = [
    "Program ID", "Program Title", "Institution", "Location", "Language", "Study Format",
    "Duration", "Total Credits", "Degree Type", "Specialization", "Modality", "Tuition Fees",
    "Academic Admission Requirements", "Language Admission Requirements"
]

row = [
    PROGRAM_ID, program_title, institution, location, language, study_format,
    duration, total_credits, degree_type, specialization, modality, tuition_fees,
    academic_admission, language_admission
]

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerow(row)

print(f"[OK] Website data saved to '{OUTPUT_CSV}'")