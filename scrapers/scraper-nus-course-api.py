import requests
import pandas as pd
import csv
import re

# Input and output
INPUT_CSV = "nus_pdf_data.csv"
OUTPUT_CSV = "nus_course_details.csv"
API_BASE_URL = "https://api.nusmods.com/v2/2023-2024/modules/"

# Read course codes and titles
df_courses = pd.read_csv(INPUT_CSV)

# Prepare list for output
output_data = []

# Helper function to process workload
def process_workload(workload):
    if isinstance(workload, list):
        total_hours = sum(workload)
        units = round(total_hours / 2.5, 1)
        return f"{units} Units ({total_hours} hours)"
    elif isinstance(workload, int) or isinstance(workload, float):
        units = round(workload / 2.5, 1)
        return f"{units} Units ({workload} hours)"
    elif isinstance(workload, str):
        return workload
    else:
        return "Unknown"

# Scrape course details from API
for index, row in df_courses.iterrows():
    course_code = row["Course Code"]
    course_title = row["Course Title"]
    
    url = f"{API_BASE_URL}{course_code}.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        course_description = data.get("description", "Not Specified").strip()
        prerequisites = data.get("prerequisite", "Not Specified").strip()
        workload = data.get("workload", None)
        course_credits = process_workload(workload)

        output_data.append({
            "Course Code": course_code,
            "Course Title": course_title,
            "Course Credits": course_credits,
            "Course Description": course_description,
            "Prerequisites": prerequisites
        })

        print(f"[OK] Extracted data for {course_code}")
    else:
        print(f"[ERROR] Failed to retrieve data for {course_code}. Status Code: {response.status_code}")

# Save to CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Course Code", "Course Title", "Course Credits", "Course Description", "Prerequisites"])
    writer.writeheader()
    writer.writerows(output_data)

print(f"[OK] Saved {len(output_data)} courses to '{OUTPUT_CSV}'")