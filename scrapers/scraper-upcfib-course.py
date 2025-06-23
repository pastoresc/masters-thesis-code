import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Input and output
CURRICULUM_URL = "https://www.fib.upc.edu/en/studies/masters/master-informatics-engineering/curriculum"
BASE_URL = "https://www.fib.upc.edu"
OUTPUT_CSV = "upcfib_course_data.csv"

# Setup Selenium headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

print("[INFO] Requesting curriculum page...")
response = requests.get(CURRICULUM_URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the curriculum course blocks
print("[INFO] Extracting course entries...")
courses = []

course_blocks = soup.find_all("div", class_=lambda c: c and c.startswith("assig "))
for block in course_blocks:
    title_tag = block.find("a")
    text_after_link = block.get_text(separator=" ", strip=True)
    match = re.search(r"\(([^-]+)-([^\)]+)\)", text_after_link)

    if title_tag and match:
        title = title_tag.get_text(strip=True)
        code = match.group(1).strip()
        credits_raw = match.group(2).strip()
        credits = credits_raw.replace("'", ".")

        course_description = "Not Specified"
        prerequisites = "Not Specified"

        link = title_tag.get("href")
        if link and ("/curriculum/syllabus/" in link or "/assignatures/" in link):
            detail_url = BASE_URL + link
            try:
                driver.get(detail_url)

                # Check if the page loaded and description exists
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "descripcio"))
                )
                detail_soup = BeautifulSoup(driver.page_source, "html.parser")

                # Extract description
                desc_section = detail_soup.find("section", id="descripcio")
                if not desc_section:
                    desc_section = detail_soup.find("section", class_="descripcio")
                if desc_section:
                    course_description = " ".join(
                        p.get_text(strip=True) for p in desc_section.find_all(["p", "br"])
                    ).strip()
                    if not course_description:
                        course_description = desc_section.get_text(separator=" ", strip=True)

                # Extract prerequisites
                fitxa = detail_soup.find("div", class_="fitxa")
                if fitxa:
                    rows = fitxa.find_all("div", class_="row")
                    for r in rows:
                        label_div = r.find("div", class_="col-xs-3")
                        value_div = r.find("div", class_="col-xs-9")
                        if label_div and value_div:
                            label = label_div.get_text(strip=True)
                            if "Requirements" in label:
                                prerequisites = value_div.get_text(separator=" ", strip=True)
                                break

            except Exception as e:
                print(f"[INFO] No detail page for {code}: {e}")

        courses.append({
            "Course Code": code,
            "Course Title": title,
            "Course Credits": credits,
            "Course Description": course_description,
            "Prerequisites": prerequisites
        })

# Cleanup
driver.quit()

# Report and save to CSV
count = len(courses)
print(f"[OK] Extracted {count} courses.")

if courses:
    df = pd.DataFrame(courses)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[OK] Course data saved to '{OUTPUT_CSV}'")
else:
    df_empty = pd.DataFrame(columns=["Course Code", "Course Title", "Course Credits", "Course Description", "Prerequisites"])
    df_empty.to_csv(OUTPUT_CSV, index=False)
    print(f"[OK] Empty course data saved to '{OUTPUT_CSV}'")