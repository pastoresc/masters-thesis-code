import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Input and output
PROGRAM_URL = "https://www.helsinki.fi/en/degree-programmes/computer-science-masters-programme"
STUDYING_URL = "https://www.helsinki.fi/en/degree-programmes/computer-science-masters-programme/studying"
OUTPUT_CSV = "uoh_website_data.csv"

# Load static HTML page
def fetch_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

# Load dynamic page
def fetch_page_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)
    return driver

# Generate a program ID
def generate_program_id(institution_name, number="001"):
    abbreviation = "".join(word[0] for word in institution_name.split()).upper()
    return f"{abbreviation}{number}"

# Extract program title
def extract_program_title(driver):
    try:
        title_element = driver.find_element(By.CSS_SELECTOR, "h2.hy-hero__title.hy-heading__hero")
        return title_element.text.strip()
    except:
        return "Not available"

# Extract institution name
def extract_institution(soup):
    try:
        address_tag = soup.find("address")
        if address_tag and "University of Helsinki" in address_tag.text:
            return "University of Helsinki"
    except:
        pass
    return "Not available"

# Extract location information
def extract_location(soup):
    try:
        address_tag = soup.find("address")
        if address_tag and "Helsinki" in address_tag.text:
            return "Helsinki, Finland"
    except:
        pass
    return "Not available"

# Extract language
def extract_language(driver):
    try:
        language_section = driver.find_element(By.CSS_SELECTOR, ".degree-programme__factbox--item.degree-programme__factbox--language .degree-programme__factbox--item__value")
        return language_section.text.strip().replace("\n", "").replace(",", ", ")
    except:
        return "Not available"

# Extract study format
def extract_study_format(driver):
    try:
        factbox_text = driver.find_element(By.CLASS_NAME, "degree-programme__factbox").text.lower()
        if "full-time" in factbox_text:
            return "Full-time"
        elif "part-time" in factbox_text:
            return "Part-time"
    except:
        pass
    return "Not specified"

# Parse duration and credit information
def extract_duration_and_credits(soup):
    duration = "Not specified"
    credits = "Not specified"
    try:
        text = soup.get_text(separator="\n").lower()
        if "2 years" in text:
            duration = "4 semesters"
        if "120 ects" in text or "120 credits" in text:
            credits = "120"
    except:
        pass
    return duration, credits

# Extract specialization
def extract_specialization_from_studying(soup):
    try:
        specialization_list = []
        uls = soup.find_all("ul")
        for ul in uls:
            items = ul.find_all("li")
            for item in items:
                text = item.get_text().strip()
                if text in ["Algorithms", "Networks", "Software"]:
                    specialization_list.append(text)
        if specialization_list:
            return "; ".join(specialization_list)
    except:
        pass
    return "Not specified"

# Extract degree type
def extract_degree_type(soup):
    try:
        paragraphs = soup.find_all("p")
        for para in paragraphs:
            text = para.get_text().lower()
            if "msc degree" in text:
                return "MSc"
            elif "ma degree" in text:
                return "MA"
            elif "llm degree" in text:
                return "LL.M."
            elif "meng degree" in text:
                return "MEng"
            elif "mphil degree" in text:
                return "MPhil"
    except:
        pass
    return "Not specified"

# Extract modality
def extract_modality(soup):
    try:
        text = soup.get_text(separator="\n").lower()

        on_campus_phrases = ["on campus", "studied on campus", "campus-based"]
        online_phrases = ["online programme", "online program", "online learning", "fully online", "studied online"]
        hybrid_phrases = ["blended learning", "hybrid model", "hybrid learning"]

        if any(phrase in text for phrase in on_campus_phrases):
            return "On Campus"
        elif any(phrase in text for phrase in online_phrases):
            return "Online"
        elif any(phrase in text for phrase in hybrid_phrases):
            return "Hybrid"
    except:
        pass
    return "Not specified"

# Extract tuition fees
def extract_tuition_fees(driver):
    try:
        tuition_section = driver.find_element(By.CSS_SELECTOR, ".degree-programme__factbox--item.degree-programme__factbox--fee .degree-programme__factbox--item__value")
        return tuition_section.text.strip()
    except:
        return "Not specified"

# Return academic admission requirements
def extract_academic_admission_requirements_opintopolku():
    return ("1. A first-cycle (Bachelor’s or equivalent) degree is required. "
            "3. If you have not yet graduated, you must provide proof of your eligibility by the time you accept your study place.")

# Return language admission requirements
def extract_language_admission_requirements_opintopolku():
    return ("2. Proof of sufficient English language skills is required. Accepted certificates are specified by the university.")

# Main process: Fetch pages, extract data and save to CSV
def main():
    main_page_soup = fetch_page(PROGRAM_URL)
    studying_page_soup = fetch_page(STUDYING_URL)

    driver = fetch_page_selenium(PROGRAM_URL)

    institution = extract_institution(main_page_soup)
    location = extract_location(main_page_soup)
    program_id = generate_program_id(institution, "001")

    program_title = extract_program_title(driver)
    language = extract_language(driver)
    study_format = extract_study_format(driver)
    duration, credits = extract_duration_and_credits(main_page_soup)
    specialization = extract_specialization_from_studying(studying_page_soup)
    degree_type = extract_degree_type(studying_page_soup)
    modality = extract_modality(main_page_soup)
    tuition_fees = extract_tuition_fees(driver)
    academic_admission = extract_academic_admission_requirements_opintopolku()
    language_admission = extract_language_admission_requirements_opintopolku()

    driver.quit()

    data = {
        "Program ID": program_id,
        "Program Title": program_title,
        "Institution": institution,
        "Location": location,
        "Language": language,
        "Study Format": study_format,
        "Duration": duration,
        "Total Credits": credits,
        "Degree Type": degree_type,
        "Specialization": specialization,
        "Modality": modality,
        "Tuition Fees": tuition_fees,
        "Academic Admission Requirements": academic_admission,
        "Language Admission Requirements": language_admission
    }

    column_order = [
        "Program ID", "Program Title", "Institution", "Location", "Language", "Study Format",
        "Duration", "Total Credits", "Degree Type", "Specialization", "Modality", "Tuition Fees",
        "Academic Admission Requirements", "Language Admission Requirements"
    ]

    df = pd.DataFrame([data])
    df[column_order].to_csv(OUTPUT_CSV, index=False)
    print(f"[OK] Website data saved to '{OUTPUT_CSV}'")

# Run main process
if __name__ == "__main__":
    main()