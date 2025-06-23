import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Input and output
COURSE_PAGE_URL = "https://studies.helsinki.fi/degree-structure/study-module/otm-eca7b5e8-26d8-41ab-88ca-47aa95c365cf?cpId=hy-lv-75"
OUTPUT_CSV = "uoh_course_details_data.csv"

# Handle cookies
def handle_cookies(driver):
    try:
        decline_button = driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonDecline")
        decline_button.click()
        print("[INFO] Clicked 'Use necessary cookies only'.")
        time.sleep(1)
    except:
        print("[INFO] No cookie consent banner detected or already handled.")

# Expand all collapsible sections on the page
def expand_all_elements(driver):
    try:
        expand_buttons = driver.find_elements(By.CSS_SELECTOR, "button.button--action.theme-transparent[aria-expanded='false']")
        print(f"[INFO] Found {len(expand_buttons)} sections to expand.")

        for idx, button in enumerate(expand_buttons):
            try:
                driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", button)
                driver.execute_script("arguments[0].click();", button)
                print(f"[INFO] Expanded section {idx + 1} of {len(expand_buttons)}.")
                time.sleep(0.5)
            except Exception as e:
                print(f"[WARNING] Could not expand section {idx + 1}: {e}")
                continue
    except Exception as e:
        print(f"[ERROR] Problem during expand_all_elements: {e}")

# Extract course description and prerequisites from course detail page
def extract_course_details(driver):
    course_description = ""
    prerequisites = ""

    try:
        headings = driver.find_elements(By.TAG_NAME, "h3")
        for heading in headings:
            heading_text = heading.text.strip().lower()
            if heading_text == "content":
                try:
                    next_element = heading.find_element(By.XPATH, "following-sibling::*[1]")
                    course_description = next_element.text.strip()
                except Exception as e:
                    print(f"[WARNING] Could not extract Content text: {e}")
            elif heading_text == "prerequisites":
                try:
                    next_element = heading.find_element(By.XPATH, "following-sibling::*[1]")
                    prerequisites = next_element.text.strip()
                except Exception as e:
                    print(f"[WARNING] Could not extract Prerequisites text: {e}")
    except Exception as e:
        print(f"[WARNING] Failed to extract details on course page: {e}")

    return course_description, prerequisites

# Main process
def main():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(COURSE_PAGE_URL)

    try:
        handle_cookies(driver)

        driver.refresh()
        print("[INFO] Page reloaded after cookie handling.")

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".rootModule__titleRow___3bf-C"))
        )
        print("[INFO] Basic page structure loaded after refresh.")

        first_section = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.rootModule__accordionName___1GiB5"))
        )
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", first_section)
        print("[INFO] Scrolled to first section to trigger lazy loading.")

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.button--action.theme-transparent[aria-expanded='false']"))
        )
        print("[INFO] Expandable sections detected, modules are loaded.")

        expand_all_elements(driver)
        print("[INFO] Expand actions completed.")

    except Exception as e:
        print(f"[ERROR] Problem during page loading or expansion: {e}")
        driver.quit()
        return

    # Collect all course entries from module overview
    course_links = []
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.rootModule__courseItem___8qM7s"))
        )
        course_items = driver.find_elements(By.CSS_SELECTOR, "li.rootModule__courseItem___8qM7s")
        print(f"[INFO] Found {len(course_items)} courses in list.")

        for item in course_items:
            try:
                link_element = item.find_element(By.CSS_SELECTOR, "a.rootModule__link___1BtmW")
                credits_element = item.find_element(By.CSS_SELECTOR, "span.rootModule__credits___nZOli")

                course_url = link_element.get_attribute("href")
                course_text = link_element.text.strip()
                course_credits = credits_element.text.strip().replace(" cr", "").replace(",", ".")

                parts = course_text.split(" ", 1)
                if len(parts) == 2:
                    course_code = parts[0].strip()
                    course_title = parts[1].strip()
                else:
                    course_code = ""
                    course_title = course_text.strip()

                course_links.append({
                    "Course URL": course_url,
                    "Course Code": course_code,
                    "Course Title": course_title,
                    "Course Credits": course_credits
                })
            except Exception as e:
                print(f"[WARNING] Could not extract a course entry: {e}")
                continue
    except Exception as e:
        print(f"[ERROR] Problem during course listing: {e}")
        driver.quit()
        return

    course_data = []

    # Visit each course page and extract details
    for idx, course in enumerate(course_links):
        try:
            driver.get(course["Course URL"])
            print(f"[INFO] ({idx + 1}/{len(course_links)}) Opened course: {course['Course Code']}")

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "h3"))
            )

            course_description, prerequisites = extract_course_details(driver)

            course_data.append({
                "Course Code": course["Course Code"],
                "Course Title": course["Course Title"],
                "Course Credits": course["Course Credits"],
                "Course Description": course_description,
                "Prerequisites": prerequisites
            })
        except Exception as e:
            print(f"[WARNING] Could not extract course details for {course['Course Code']}: {e}")
            continue

    driver.quit()

    df = pd.DataFrame(course_data)

    # Replace empty values with fallback
    for col in ["Course Description", "Prerequisites"]:
        df[col] = df[col].fillna("").replace("", "Not Specified")

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[OK] Detailed course data saved to '{OUTPUT_CSV}' with {len(course_data)} entries.")

# Run main process
if __name__ == "__main__":
    main()