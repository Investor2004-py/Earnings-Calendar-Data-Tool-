from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Setup Chrome driver path and options
chromedriver_path = r"C:\Users\dhyey\OneDrive\chromedriver.exe"
service = Service(executable_path=chromedriver_path)

chrome_options = Options()
chrome_options.add_argument("--headless")  # comment to see browser
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=service, options=chrome_options)

base_url = "https://finance.yahoo.com/calendar/earnings?from=2025-06-30&to=2025-08-15&size=100&offset={}"

all_data = []
offset = 0
max_entries = 3789  # total approx entries (adjust if needed)

while offset < max_entries:
    url = base_url.format(offset)
    print(f"🔄 Loading page with offset {offset} ...")
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(("tag name", "table"))
        )
    except:
        print(f"⚠️ Timeout waiting for table at offset {offset}. Skipping this page.")
        offset += 100
        continue

    try:
        table = driver.find_element("tag name", "table")
        rows = table.find_elements("tag name", "tr")[1:]  # skip header

        if not rows:
            print("No more rows found, ending.")
            break

        for row in rows:
            cols = row.find_elements("tag name", "td")
            if len(cols) >= 6:
                all_data.append({
                    "Symbol": cols[0].text,
                    "Company": cols[1].text,
                    "Event Name": cols[2].text,
                    "Earnings Call Time": cols[3].text,
                    "EPS Estimate": cols[4].text,
                    "Reported EPS": cols[5].text,
                    "Surprise (%)": cols[6].text,
                    "Market Cap": cols[7].text
                })

    except Exception as e:
        print(f"❌ Error scraping page at offset {offset}: {e}")
        break

    offset += 100  # next page by offset increment

driver.quit()

# Save to CSV
df = pd.DataFrame(all_data)
df.to_csv("Yahoo_Earnings_Jun30_to_Aug15_2025.csv", index=False)
print(f"\n✅ Done! Scraped {len(df)} entries.")

