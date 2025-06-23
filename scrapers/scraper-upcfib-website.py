import requests
import pandas as pd
import re
from bs4 import BeautifulSoup

# Input and output
PROGRAM_PAGE_URL = "https://www.fib.upc.edu/en/studies/masters/master-informatics-engineering"
FEES_PAGE_URL = "https://www.upc.edu/en/masters/informatics-engineering"
OUTPUT_CSV = "upcfib_website_data.csv"

print("[INFO] Sending request to program page...")
response = requests.get(PROGRAM_PAGE_URL)
soup = BeautifulSoup(response.text, 'html.parser')

print("[INFO] Sending request to fees page...")
fees_response = requests.get(FEES_PAGE_URL)
fees_soup = BeautifulSoup(fees_response.text, 'html.parser')

# Initialize fields
program_title = "Not Specified"
institution = "Universitat Politècnica de Catalunya"
location = "Not Specified"
language = "Not Specified"
duration = "Not Specified"
total_credits = "Not Specified"
degree_type = "MSc"
specialization = "Not Specified"
modality = "Not Specified"
tuition_fees = "Not Specified"

# Extract program title
try:
    print("[INFO] Extracting Program Title...")
    header = soup.find("h1", class_="page_title")
    if header:
        program_title = header.text.strip()
    print(f"[INFO] Program Title: {program_title}")
except Exception as e:
    print(f"[WARNING] Could not extract Program Title: {e}")

# Extract language, study format, duration, total credits, modality
full_time_available = False
part_time_available = False
try:
    print("[INFO] Extracting Language, Study Formats, Duration, Total Credits, and Modality...")
    fitxa_gris = soup.find("div", class_="fitxa-gris")
    if fitxa_gris:
        rows = fitxa_gris.find_all("div", class_="row")
        for row in rows:
            label = row.find("div", class_="field-label")
            value = row.find("div", class_="field-items")
            if label and value:
                label_text = label.get_text(strip=True).lower()
                value_text = value.get_text(separator=" ", strip=True)
                if "language" in label_text:
                    language = value_text
                if "workload" in label_text:
                    if "full-time" in value_text.lower():
                        full_time_available = True
                    if "part-time" in value_text.lower():
                        part_time_available = True
                if "duration" in label_text:
                    if "three semesters" in value_text.lower():
                        duration = "3 semesters"
                    credits_match = re.search(r"(\d+\s*ECTS)", value_text)
                    if credits_match:
                        total_credits = credits_match.group(1)
                    if "face-to-face" in value_text.lower():
                        modality = "On Campus"
    print(f"[INFO] Language: {language}")
    print(f"[INFO] Duration: {duration}")
    print(f"[INFO] Total Credits: {total_credits}")
    print(f"[INFO] Modality: {modality}")
except Exception as e:
    print(f"[WARNING] Could not extract detailed program information: {e}")

# Extract tuition fees from the fees page
try:
    print("[INFO] Extracting Tuition Fees...")
    fees_dt = fees_soup.find("dt", string=lambda t: t and "Fees and grants" in t)
    if fees_dt:
        fees_dd = fees_dt.find_next_sibling("dd")
        if fees_dd:
            fee_text = fees_dd.get_text(separator=" ", strip=True)
            fee_matches = re.findall(r"\u20ac\s?[\d.,]+", fee_text)
            if not fee_matches:
                fee_matches = re.findall(r"[\d.,]+\s?\u20ac", fee_text)
            if fee_matches and len(fee_matches) >= 2:
                eu_fee = fee_matches[0].replace("€", "").strip()
                non_eu_fee = fee_matches[1].replace("€", "").strip()
                tuition_fees = f"{eu_fee} EUR (EU students), {non_eu_fee} EUR (non-EU students)"
    print(f"[INFO] Tuition Fees: {tuition_fees}")
except Exception as e:
    print(f"[WARNING] Could not extract Tuition Fees: {e}")

# Extract location
try:
    print("[INFO] Extracting Location...")
    footer_region = soup.find("div", class_="region-footer-first")
    if footer_region:
        content_text = footer_region.get_text(separator=" ", strip=True)
        if "BARCELONA" in content_text.upper():
            location = "Barcelona, Spain"
    print(f"[INFO] Location: {location}")
except Exception as e:
    print(f"[WARNING] Could not extract Location: {e}")

# Save to CSV
print("[INFO] Saving extracted data...")

records = []

if full_time_available:
    records.append({
        "Program ID": "UPCFIB001",
        "Program Title": program_title,
        "Institution": institution,
        "Location": location,
        "Language": language,
        "Study Format": "Full-time",
        "Duration": duration,
        "Total Credits": total_credits,
        "Degree Type": degree_type,
        "Specialization": specialization,
        "Modality": modality,
        "Tuition Fees": tuition_fees
    })

if part_time_available:
    records.append({
        "Program ID": "UPCFIB002",
        "Program Title": program_title,
        "Institution": institution,
        "Location": location,
        "Language": language,
        "Study Format": "Part-time",
        "Duration": duration,
        "Total Credits": total_credits,
        "Degree Type": degree_type,
        "Specialization": specialization,
        "Modality": modality,
        "Tuition Fees": tuition_fees
    })

df = pd.DataFrame(records)
df.to_csv(OUTPUT_CSV, index=False)
print(f"[OK] Website data saved to '{OUTPUT_CSV}'")