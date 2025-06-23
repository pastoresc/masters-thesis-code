import requests
from bs4 import BeautifulSoup
import csv
import os
import re
import pandas as pd

# Input and output
URL_MAIN = "https://www.comp.nus.edu.sg/programmes/pg/mcomp-gen/"
URL_FEES = "https://www.comp.nus.edu.sg/programmes/pg/mcomp-gen/fees/"
URL_ADMISSIONS = "https://www.comp.nus.edu.sg/programmes/pg/mcomp-gen/admissions/"
OUTPUT_CSV = "nus_website_data.csv"
PDF_PATH = "nus_programs.pdf"

# Generate program ID
def get_existing_program_id(title, filepath, abbr="NUS"):
    if not os.path.exists(filepath):
        return None
    df = pd.read_csv(filepath)
    match = df[df["Program Title"].str.strip().str.lower() == title.strip().lower()]
    if not match.empty:
        return match.iloc[0]["Program ID"]
    return None

def get_next_program_id(abbr, filepath, format_type):
    existing_ids = []
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        for pid in df["Program ID"]:
            if isinstance(pid, str) and pid.startswith(abbr):
                number = pid.replace(abbr, "")
                if number.isdigit():
                    existing_ids.append(int(number))
    next_number = max(existing_ids, default=0) + 1
    return f"{abbr}{next_number:03d}{'P' if format_type == 'Part-time' else ''}"

# Extract plain text
def extract_text(soup, selector):
    el = soup.select_one(selector)
    return el.get_text(strip=True) if el else "Not Specified"

# Extract duration
def extract_durations_from_paragraph(soup):
    header = soup.find("h4", string=re.compile("Duration of Programme", re.IGNORECASE))
    if header:
        container = header.find_parent("div", class_="e-con-inner")
        if container:
            para = container.find("p")
            if para:
                text = para.get_text(separator=" ", strip=True)
                return {
                    "Full-time": "4 semesters" if "1.5 to 2" in text else "Not Specified",
                    "Part-time": "5 semesters" if "2.5" in text else "Not Specified"
                }
    return {"Full-time": "Not Specified", "Part-time": "Not Specified"}

# Extract language
def extract_language_from_text(text):
    keywords = ["language of instruction", "teaching language"]
    langs = ["English", "Chinese", "Mandarin", "German", "French", "Spanish"]
    if any(k in text.lower() for k in keywords):
        for lang in langs:
            if lang.lower() in text.lower():
                return lang
    return "Not Specified"

# Extract study format
def detect_study_formats(text):
    formats = []
    if "full-time" in text.lower():
        formats.append("Full-time")
    if "part-time" in text.lower():
        formats.append("Part-time")
    return formats if formats else ["Not Specified"]

# Extract specialization
def extract_specialization_from_title(title):
    if "general" in title.lower():
        return "Not Specified"
    return "Not Specified"

# Extract modality
def extract_modality(text):
    text = text.lower()
    if any(kw in text for kw in ["on campus", "in person", "face-to-face"]):
        return "On Campus"
    elif any(kw in text for kw in ["online", "remote learning"]):
        return "Online"
    elif any(kw in text for kw in ["hybrid", "blended"]):
        return "Hybrid"
    return "Not Specified"

# Extract tuition fee
def extract_tuition_fees():
    keywords = [
        "tuition fee", "tuition fees",
        "programme fee", "programme fees",
        "course fee", "course fees",
        "total cost", "total programme cost"
    ]
    try:
        response = requests.get(URL_FEES)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.find_all(["td", "p", "div", "span"]):
            content = tag.get_text(separator=" ", strip=True).lower()
            if any(k in content for k in keywords):
                match = re.search(r"s\$[\d,]+\.\d{2}", tag.decode_contents(), re.IGNORECASE)
                if match:
                    return match.group(0)
    except:
        pass
    return "Not Specified"

# Extract academic admission requirements
def extract_academic_admission_requirements():
    try:
        response = requests.get(URL_ADMISSIONS)
        soup = BeautifulSoup(response.text, "html.parser")
        heading = soup.find("h4", string=re.compile("Admission Criteria", re.IGNORECASE))
        if heading:
            container = heading.find_next("div", class_="elementor-widget-container")
            if container:
                paragraphs = container.find_all("p")
                combined = " ".join(p.get_text(strip=True) for p in paragraphs)
                return combined[:1000] + "..." if len(combined) > 1000 else combined
    except:
        pass
    return "Not Specified"

# Extract language admission requirements
def extract_language_admission_requirements():
    try:
        response = requests.get(URL_ADMISSIONS)
        soup = BeautifulSoup(response.text, "html.parser")
        keywords = ["proof of english proficiency", "toefl", "ielts", "english language requirement"]
        for p in soup.find_all("p"):
            text = p.get_text(strip=True).lower()
            if any(keyword in text for keyword in keywords):
                return text[:1000] + "..." if len(text) > 1000 else text
    except:
        pass
    return "Not Specified"

# Main process: Extract data and save to CSV
def main():
    response = requests.get(URL_MAIN)
    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text(separator=' ', strip=True)

    formats = detect_study_formats(page_text)
    durations = extract_durations_from_paragraph(soup)
    modality = extract_modality(page_text)
    tuition_fees = extract_tuition_fees()
    program_title = extract_text(soup, "h1.elementor-heading-title")
    specialization = extract_specialization_from_title(program_title)
    admission_requirements = extract_academic_admission_requirements()
    language_admission_requirements = extract_language_admission_requirements()

    program_rows = []
    for i, format_option in enumerate(formats):
        program_id = get_next_program_id("NUS", OUTPUT_CSV, format_option)
        data = {
            "Program ID": program_id,
            "Program Title": program_title,
            "Institution": "National University of Singapore",
            "Location": "Singapore",
            "Language": extract_language_from_text(page_text),
            "Study Format": format_option,
            "Duration": durations.get(format_option, "Not Specified"),
            "Total Credits": "Not Specified",
            "Degree Type": "Master of Science (MSc)",
            "Specialization": specialization,
            "Modality": modality,
            "Tuition Fees": tuition_fees,
            "Academic Admission Requirements": admission_requirements,
            "Language Admission Requirements": language_admission_requirements
        }
        program_rows.append(data)

    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        writer.writeheader()
        writer.writerows(program_rows)

    print(f"[OK] Website data saved to '{OUTPUT_CSV}'")

if __name__ == "__main__":
    main()