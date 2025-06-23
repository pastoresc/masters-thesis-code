import pdfplumber
import pandas as pd
import re
import os
import requests
from io import BytesIO

# Input and output
PDF_URL = "https://science.ku.dk/studerende/studieordninger/erhvervskandidat/msc_computer_science_sto_erhvervska.pdf"
WEBSITE_CSV = "ucph_website_data.csv"
OUTPUT_CSV = "ucph_pdf_data.csv"

# Load program ID from website scraper output
def load_program_id(csv_file):
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Website CSV not found: {csv_file}")
    df = pd.read_csv(csv_file)
    return df.iloc[0]["Program ID"]

# Extract degree type, language and modality
def extract_structured_fields(text):
    text = text.lower()
    degree_type = "MSc" if "master of science" in text or "msc" in text else "Not specified"

    language = []
    if "english" in text:
        language.append("English")
    if "danish" in text:
        language.append("Danish")
    language = ", ".join(sorted(set(language))) if language else "Not specified"

    if "online" in text or "remote" in text or "distance" in text:
        modality = "Online"
    elif "blended" in text or "hybrid" in text:
        modality = "Hybrid"
    else:
        modality = "On Campus"

    return degree_type, language, modality

# Return academic requirements if expected section is found
def extract_academic_requirements_block(text):
    match = re.search(r"4\.2 Other Bachelor’s degrees(.+?)4\.3 Other applicants", text, re.DOTALL | re.IGNORECASE)
    if match:
        return (
            "Bachelor’s degree with 45 ECTS in Computer Science:\n"
            "- 7.5 ECTS in programming (2 paradigms)\n"
            "- 10 ECTS in computer systems (e.g., architecture, OS, networks)\n"
            "- 10 ECTS in theory (e.g., algorithms, complexity)\n"
            "- 7.5 ECTS in mathematics (discrete math, linear algebra, modelling)"
        )
    return "No structured academic requirements section found."

# Identify and normalize language requirement
def extract_language_requirement_normalized(text):
    for line in text.split("\n"):
        if any(kw in line.lower() for kw in ["english", "language requirement", "ielts", "toefl", "proficiency"]):
            return "Proof of English proficiency is required (see English language requirements)."
    return "Not available"

# Extract total credits
def extract_total_credits(text):
    match = re.search(r"(\d{2,3})\s*ECTS", text, re.IGNORECASE)
    if match:
        return f"{match.group(1)} ECTS"
    return "Not available"

# Main process: Download PDF, extract metadata and course modules and save to CSV
def main():
    response = requests.get(PDF_URL)
    if response.status_code != 200:
        print("[ERROR] Could not download PDF.")
        return

    program_id = load_program_id(WEBSITE_CSV)
    pdf_file = BytesIO(response.content)
    modules = []
    institution = "University of Copenhagen"

    with pdfplumber.open(pdf_file) as pdf:
        all_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        degree_type, language, modality = extract_structured_fields(all_text)
        academic_requirements = extract_academic_requirements_block(all_text)
        language_requirements = extract_language_requirement_normalized(all_text)
        total_credits = extract_total_credits(all_text)

        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 2:
                        continue
                    row = [cell.strip() if cell else "" for cell in row]
                    course_code = None
                    course_title = None
                    course_credits = None

                    for idx, cell in enumerate(row):
                        ects_match = re.search(r"(\d{1,2}(?:[.,]\d{1})?)\s*ECTS", cell, re.IGNORECASE)
                        if ects_match:
                            course_credits = ects_match.group(1).replace(",", ".").strip()
                            code_match = re.search(r"[A-Z]{2,}[0-9]{4,}[A-Z]?", " ".join(row[:idx]))
                            if code_match:
                                course_code = code_match.group(0).strip()
                            title_parts = [t for t in row[:idx] if len(t.strip()) > 2]
                            title_candidate = " ".join(title_parts).strip()
                            if course_code and course_code in title_candidate:
                                title_candidate = title_candidate.replace(course_code, "").strip()
                            course_title = re.sub(r"\(PDF\)", "", title_candidate).strip()
                            break

                    if course_title and course_credits:
                        modules.append({
                            "Program ID": program_id,
                            "Course Code": course_code,
                            "Course Title": course_title,
                            "Course Credits": course_credits,
                            "Institution": institution,
                            "Language": language,
                            "Modality": modality,
                            "Degree Type": degree_type,
                            "Specialization": None,
                            "Academic Admission Requirements": academic_requirements,
                            "Language Admission Requirements": language_requirements,
                            "Total Credits": total_credits
                        })

    df = pd.DataFrame(modules)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[OK] Saved {len(modules)} courses to '{OUTPUT_CSV}'")

if __name__ == "__main__":
    main()