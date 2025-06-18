from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random

app = Flask(__name__)

# --- CONFIGURATION ---
# Target companies mapping (LinkedIn company IDs)
companies = {
    "Apple": "162479",
    "NVIDIA": "3608",
    "AMD": "1497",
    "ARM": "4472",
    "Broadcom": "3072",
    "Qualcomm": "2017"
}

# Selenium Chrome options:
# - Retain your Chrome login session via user-data-dir
# - Run in headless for server deployment
chrome_options = Options()
chrome_options.add_argument(
    "--user-data-dir=C:/Users/anuj/AppData/Local/Google/Chrome/User Data"
)
chrome_options.add_argument("--profile-directory=Default")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# If you need to specify chromedriver path explicitly:
# service = Service(executable_path="/path/to/chromedriver")


def send_requests(company_id: str, message: str, max_requests: int = 10) -> dict:
    """
    Automates LinkedIn connection requests to people at `company_id`.
    Returns a dict with 'requests_sent', 'connected' list, and 'failures'.
    """
    # Initialize a headless Chrome driver
    driver = webdriver.Chrome(options=chrome_options)
    results = {"requests_sent": 0, "connected": [], "failures": []}

    try:
        # Step 1: Navigate to feed to confirm login
        driver.get("https://www.linkedin.com/feed/")
        WebDriverWait(driver, 15).until(EC.url_contains("feed"))

        # Step 2: Build search URL for the target company
        search_url = (
            f"https://www.linkedin.com/search/results/people/?"
            f"currentCompany=%5B%22{company_id}%22%5D"
        )
        driver.get(search_url)
        time.sleep(3)  # brief pause for page load

        # Step 3: Iterate through connect buttons
        while results['requests_sent'] < max_requests:
            buttons = driver.find_elements(
                By.XPATH,
                "//button[contains(@class, 'artdeco-button') and .//span[text()='Connect']]"
            )
            if not buttons:
                break  # no more connect buttons on this page

            for btn in buttons:
                if results['requests_sent'] >= max_requests:
                    break

                try:
                    # Click 'Connect'
                    btn.click()

                    # Wait for dialog and enter message
                    dialog = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, "//div[@role='dialog']"))
                    )
                    textarea = WebDriverWait(dialog, 5).until(
                        EC.element_to_be_clickable((By.TAG_NAME, 'textarea'))
                    )
                    textarea.clear()
                    textarea.send_keys(message)

                    # Send invitation
                    send_btn = dialog.find_element(
                        By.XPATH,
                        "//button[contains(@class,'artdeco-button--primary') and .//span[contains(text(),'Send')]]"
                    )
                    send_btn.click()

                    # Record success
                    label = btn.get_attribute('aria-label') or 'unknown'
                    results['connected'].append(label)
                    results['requests_sent'] += 1

                    # polite wait
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    # capture any exception (popup failure, rate limit, etc.)
                    results['failures'].append(str(e))
                    # attempt to close dialog if stuck
                    try:
                        close_btn = driver.find_element(By.XPATH, "//button[@aria-label='Dismiss']")
                        close_btn.click()
                    except:
                        pass
                    continue

            # Attempt pagination
            try:
                next_btn = driver.find_element(By.XPATH, "//button[@aria-label='Next']")
                if 'disabled' in next_btn.get_attribute('class'):
                    break
                next_btn.click()
                time.sleep(random.uniform(4, 7))
            except Exception:
                break

        return results

    finally:
        driver.quit()


@app.route('/api/connect', methods=['POST'])
def api_connect():
    data = request.get_json(force=True)
    company = data.get('company')
    message = data.get('message', '')
    count = int(data.get('count', 5))

    if company not in companies:
        return jsonify({"error": "Unknown company key."}), 400

    try:
        result = send_requests(companies[company], message, count)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # debug=True can be turned off in production
    app.run(host='0.0.0.0', port=5000, debug=True)
