import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

# Load Program ID from website scraper output
df = pd.read_csv("ubc_website_data.csv")
program_id = df.loc[0, "Program ID"]

# Input and output
URLS = [
    "https://www.cs.ubc.ca/students/grad/graduate-courses/courses-winter-term-1",
    "https://www.cs.ubc.ca/students/grad/graduate-courses/courses-winter-term-2"
]

OUTPUT_CSV = "ubc_course_data.csv"
courses = []

# Extract from each page
for url in URLS:
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")

    # Find all course tables
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 3:
                course_code = cells[0].get_text(strip=True).replace("CPSC_V", "CPSC").replace("\xa0", " ")
                course_title = cells[2].get_text(strip=True)
                if course_code.startswith("CPSC") and course_title:
                    courses.append({
                        "Program ID": program_id,
                        "Course Code": course_code,
                        "Course Title": course_title
                    })

# Save to CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Program ID", "Course Code", "Course Title"])
    writer.writeheader()
    writer.writerows(courses)

print(f"[OK] Extracted {len(courses)} courses to '{OUTPUT_CSV}'")