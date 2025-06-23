import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Input and output
COURSE_PAGE_URL = "https://studies.helsinki.fi/degree-structure/study-module/otm-eca7b5e8-26d8-41ab-88ca-47aa95c365cf?cpId=hy-lv-75"
OUTPUT_CSV = "uoh_course_data.csv"

def handle_cookies(driver):
    try:
        decline_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button#CybotCookiebotDialogBodyButtonDecline"))
        )
        decline_button.click()
        print("[INFO] Clicked 'Use necessary cookies only'.")
        time.sleep(2)
    except:
        print("[INFO] No cookie consent banner detected or already handled.")

def expand_all_elements(driver):
    try:
        expand_buttons = driver.find_elements(By.CSS_SELECTOR, "button.button--action.theme-transparent[aria-expanded='false']")
        print(f"[INFO] Found {len(expand_buttons)} sections to expand.")

        for idx, button in enumerate(expand_buttons):
            try:
                driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", button)
                print(f"[INFO] Expanded section {idx + 1} of {len(expand_buttons)}.")
                time.sleep(1)
            except Exception as e:
                print(f"[WARNING] Could not expand section {idx + 1}: {e}")
                continue
    except Exception as e:
        print(f"[ERROR] Problem during expand_all_elements: {e}")

def extract_course_data(driver):
    course_data = []
    try:
        course_items = driver.find_elements(By.CSS_SELECTOR, "li.rootModule__courseItem___8qM7s")
        for item in course_items:
            try:
                link_element = item.find_element(By.CSS_SELECTOR, "a.rootModule__link___1BtmW")
                credits_element = item.find_element(By.CSS_SELECTOR, "span.rootModule__credits___nZOli")

                course_text = link_element.text.strip()
                course_url = link_element.get_attribute("href").strip()
                course_credits = credits_element.text.strip().replace(" cr", "").replace(",", ".")

                parts = course_text.split(" ", 1)
                if len(parts) == 2:
                    course_code = parts[0].strip()
                    course_title = parts[1].strip()
                else:
                    course_code = ""
                    course_title = course_text.strip()

                if course_title and course_credits:
                    course_data.append({
                        "Course Code": course_code,
                        "Course Title": course_title,
                        "Course Credits": course_credits
                    })
            except Exception as e:
                print(f"[WARNING] Skipped a course item due to extraction issue: {e}")
                continue
    except Exception as e:
        print(f"[ERROR] Problem during course data extraction: {e}")
    return course_data

def main():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(COURSE_PAGE_URL)

    try:
        # Handle cookies
        handle_cookies(driver)

        # Hard refresh page after cookie acceptance
        driver.refresh()
        print("[INFO] Page reloaded after cookie handling.")
        time.sleep(5)

        # Wait for page structure
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".rootModule__titleRow___3bf-C"))
        )
        print("[INFO] Basic page structure loaded after refresh.")

        time.sleep(2)

        # Scroll to first module section title
        first_section = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.rootModule__accordionName___1GiB5"))
        )
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", first_section)
        print("[INFO] Scrolled to first section to trigger lazy loading.")

        time.sleep(5)  # Allow modules to load after scroll

        # Wait for at least one expandable module button to appear
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.button--action.theme-transparent[aria-expanded='false']"))
        )
        print("[INFO] Expandable sections detected, modules are loaded.")

        time.sleep(2)

        # Expand all sections
        expand_all_elements(driver)
        print("[INFO] Expand actions completed.")

        time.sleep(5)  # Allow courses to load after expand

        # Wait for course list items
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.rootModule__courseItem___8qM7s"))
        )
        print("[INFO] Course list items are now visible.")

    except Exception as e:
        print(f"[ERROR] Problem during page loading or expansion: {e}")
        driver.quit()
        return

    # Extract course data and save to CSV
    course_data = extract_course_data(driver)
    driver.quit()

    if course_data:
        df = pd.DataFrame(course_data)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"[OK] Course data saved to '{OUTPUT_CSV}' with {len(course_data)} entries.")
    else:
        print("[WARNING] No course data found.")
        
# Run main process
if __name__ == "__main__":
    main()