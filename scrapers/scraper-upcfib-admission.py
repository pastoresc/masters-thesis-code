import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# Input and output
ADMISSION_PAGE_URL = "https://www.upc.edu/en/masters/access-admission-enrolment/academic-requirements"
LANGUAGE_PAGE_URL = "https://masters.fib.upc.edu/masters/master-informatics-engineering"
WEBSITE_DATA_CSV = "upcfib_website_data.csv"
OUTPUT_CSV = "upcfib_admission_data.csv"

# Load program ID
website_df = pd.read_csv(WEBSITE_DATA_CSV)
program_ids = website_df["Program ID"].tolist()

# Extract academic admission requirements
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
driver.get(ADMISSION_PAGE_URL)
time.sleep(2)

academic_admission_requirements = "Not Specified"
try:
    sections = []
    buttons = driver.find_elements(By.CSS_SELECTOR, "a[data-toggle='collapse'][data-parent='#collapse-base']")
    for btn in buttons:
        title = btn.text.strip()
        driver.execute_script("arguments[0].click();", btn)
        WebDriverWait(driver, 10).until(lambda d: btn.get_attribute("aria-expanded") == "true")
        time.sleep(0.3)
        panel = driver.find_element(By.ID, btn.get_attribute("href").split('#')[-1])
        text = panel.text.strip()
        if text:
            sections.append(f"{title}: {text}")
        # close panel
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.2)
    academic_admission_requirements = "\n\n".join(sections)
finally:
    driver.quit()

# Extract language admission requirements
resp = requests.get(LANGUAGE_PAGE_URL)
soup = BeautifulSoup(resp.text, 'html.parser')
lang_req = []
h4 = soup.find('h4', string=lambda s: s and 'Language' in s)
if h4:
    for sib in h4.find_next_siblings():
        if sib.name == 'h4':
            break
        lang_req.append(sib.get_text(separator=' ', strip=True))
language_admission_requirements = ' \n'.join(lang_req) if lang_req else 'Not Specified'

# Save to CSV
records = []
for pid in program_ids:
    records.append({
        'Program ID': pid,
        'Academic Admission Requirements': academic_admission_requirements,
        'Language Admission Requirements': language_admission_requirements
    })

df = pd.DataFrame(records)
df.to_csv(OUTPUT_CSV, index=False)
print(f"[OK] Admission data saved to '{OUTPUT_CSV}'")