import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

# Input and output
PROGRAM_URL = "https://www.ku.dk/studies/masters/part-time-computer-science"
TUITION_URL = "https://www.ku.dk/studies/masters/application-and-admission/tuition-fees-and-scholarships"
OUTPUT_CSV = "ucph_website_data.csv"

# Load page content
def fetch_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# Extract study format
def extract_study_format(html):
    text = BeautifulSoup(html, "html.parser").get_text().lower()
    if "part-time" in text:
        return "Part-time"
    elif "full-time" in text:
        return "Full-time"
    return "Not specified"

# Extract location
def extract_location(soup):
    try:
        location_header = soup.find("h3", string=re.compile(r"Location", re.IGNORECASE))
        if location_header:
            location_list = location_header.find_next("ul").get_text(separator=" ", strip=True)
            if "København" in location_list or "Copenhagen" in location_list:
                return "Copenhagen, Denmark"
            return location_list
        return "Not available"
    except:
        return "Not available"

# Extract language
def extract_language(soup):
    try:
        content_div = soup.find("div", class_="regular-text")
        if "English" in content_div.text:
            return "English"
        elif "Danish" in content_div.text:
            return "Danish"
        return "Not specified"
    except:
        return "Not available"

# Extract tuition fee
def extract_tuition_fees():
    try:
        html = fetch_page(TUITION_URL)
        soup = BeautifulSoup(html, "html.parser")
        content = soup.get_text(separator="\n")

        for line in content.split("\n"):
            if "EUR" in line or "DKK" in line:
                match = re.search(r"(EUR|DKK)[^\.]+?year", line)
                if match:
                    return match.group(0).strip()
        return "Not specified"
    except:
        return "Not available"

# Main process: Extract data and save to CSV
def main():
    html = fetch_page(PROGRAM_URL)
    soup = BeautifulSoup(html, "html.parser")

    data = {
        "Program ID": "UCPH001",
        "Program Title": "Master of Science (MSc) in Computer Science",
        "Institution": "University of Copenhagen",
        "Location": extract_location(soup),
        "Language": extract_language(soup),
        "Study Format": extract_study_format(html),
        "Duration": "4 semesters",
        "Total Credits": "Not specified",
        "Degree Type": "MSc",
        "Specialization": "Not specified",
        "Modality": "Not specified",
        "Tuition Fees": extract_tuition_fees(),
        "Academic Admission Requirements": "",
        "Language Admission Requirements": ""
    }

    column_order = [
        "Program ID", "Program Title", "Institution", "Location", "Language", "Study Format",
        "Duration", "Total Credits", "Degree Type", "Specialization", "Modality", "Tuition Fees",
        "Academic Admission Requirements", "Language Admission Requirements"
    ]

    pd.DataFrame([data])[column_order].to_csv(OUTPUT_CSV, index=False)
    print(f"[OK] Website data saved to '{OUTPUT_CSV}'")

# Run main process
if __name__ == "__main__":
    main()