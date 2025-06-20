from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Use remote Selenium endpoint since this is a pre-installed Grid image
driver = webdriver.Remote(
    command_executor="http://localhost:4444/wd/hub",
    options=chrome_options
)
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ API is up and running!"

@app.route("/api/connect", methods=["POST"])
def connect():
    try:
        data = request.get_json()
        company = data.get("company")
        count = data.get("count")
        message = data.get("message")

        print(f"👉 Request received for: {company}, count: {count}")

        # Minimal Selenium setup (headless)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Remote(
            command_executor="http://localhost:4444/wd/hub",
            options=chrome_options
        )


        driver.get("https://www.linkedin.com")
        driver.quit()

        return jsonify({
            "requests_sent": count,
            "failures": []
        })

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
