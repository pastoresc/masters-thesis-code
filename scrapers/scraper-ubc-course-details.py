import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Input
URL = "https://vancouver.calendar.ubc.ca/course-descriptions/subject/cpscv"

response = requests.get(URL)
if response.status_code != 200:
    print(f"[ERROR] Failed to fetch the page: Status code {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")
courses = []

# Match entries
for article in soup.find_all("article", class_="node--type-course"):
    header = article.find("h3")
    paragraph = article.find("p", class_="mt-0")

    if header and paragraph:
        header_text = header.get_text(strip=True)

        match = re.match(r"^(CPSC_V\s\d+[A-Z]?)\s*\(([\d\-–]+)\)\s*(.*)", header_text)
        if not match:
            continue

        course_code = match.group(1).strip()
        course_credits = match.group(2).strip()
        course_title = match.group(3).strip() or "Not Specified"

        full_text = paragraph.get_text(strip=True)
        if "Prerequisite:" in full_text:
            desc_part, prereq_part = full_text.split("Prerequisite:", 1)
            course_description = desc_part.strip()
            prerequisites = prereq_part.strip()
        else:
            course_description = full_text
            prerequisites = "Not Specified"

        courses.append({
            "Course Code": course_code,
            "Course Title": course_title,
            "Course Credits": course_credits,
            "Course Description": course_description,
            "Prerequisites": prerequisites
        })

# Save to CSV
output_file = "ubc_course-details_data.csv"
df = pd.DataFrame(courses)
df.to_csv(output_file, index=False)

print(f"[OK] Extracted {len(df)} courses to '{output_file}'")