import requests
import pdfplumber
import csv
import pandas as pd
import os
from io import BytesIO
import re

# Input and output
PDF_URL = "https://www.comp.nus.edu.sg/wp-content/uploads/2024/04/MComp-Gen-Track-Annex-A_April2024.pdf"
WEBSITE_CSV = "nus_website_data.csv"
OUTPUT_CSV = "nus_pdf_data.csv"

# Get program ID
def get_program_id(csv_file):
    """Fetches Program ID from the CSV file"""
    if not os.path.exists(csv_file):
        raise FileNotFoundError("Website CSV not found.")
    df = pd.read_csv(csv_file)
    if "Program ID" not in df.columns:
        raise ValueError("Missing 'Program ID' column.")
    return df.iloc[0]["Program ID"]

# Download the PDF and extract course data
def download_pdf(url):
    """Downloads the PDF from a URL and returns it as a BytesIO object"""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to download PDF.")
    return BytesIO(response.content)

def extract_courses_and_total_credits(pdf_file):
    """Extracts course data (Code, Title, Credits with Units) and Total Credits from the PDF"""
    course_list = []
    total_credits = 0

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split("\n")
            
            # Extract total credits
            essential_courses_match = re.search(r"Essential Courses.*?(\d+)\s*Units", text)
            capstone_project_match = re.search(r"Capstone Project.*?(\d+)\s*Units", text)
            elective_courses_match = re.search(r"Elective Courses.*?(\d+)\s*Units", text)
            
            if essential_courses_match:
                total_credits += int(essential_courses_match.group(1))
            if capstone_project_match:
                total_credits += int(capstone_project_match.group(1))
            if elective_courses_match:
                total_credits += int(elective_courses_match.group(1))

            # Extract course details
            for line in lines:
                match = re.match(r"^([A-Z]{2,}[0-9]{3,}[A-Z]?)\s+(.+)", line.strip())
                if match:
                    course_code = match.group(1).strip()
                    course_title = match.group(2).strip()
                    course_credits = "4 Units"
                    
                    unit_match = re.search(r"(\d{1,3})\s*Units", course_title)
                    if unit_match:
                        course_credits = f"{unit_match.group(1)} Units"
                    course_list.append([course_code, course_title, course_credits])

    return course_list, total_credits

def save_to_csv(program_id, courses, total_credits, output_file):
    """Saves extracted course data to a CSV file with predefined attributes"""
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Program ID", "Course Code", "Course Title", "Course Credits", "Total Credits"])
        for course in courses:
            writer.writerow([program_id] + course + [total_credits])  # Add program ID and total credits to each course entry
    print(f"[OK] Saved {len(courses)} courses to '{output_file}' with Total Credits: {total_credits}")

def run_pdf_scraper():
    """Downloads the PDF, extracts courses, and saves them to CSV"""
    pdf_data = download_pdf(PDF_URL)
    courses, total_credits = extract_courses_and_total_credits(pdf_data)
    program_id = get_program_id(WEBSITE_CSV)
    
    # Save to CSV
    save_to_csv(program_id, courses, total_credits, OUTPUT_CSV)

# Run main process
if __name__ == "__main__":
    run_pdf_scraper()