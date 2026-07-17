import time
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🛠️ Setup
chromedriver_path = r"C:\Users\dhyey\OneDrive\chromedriver.exe"
service = Service(executable_path=chromedriver_path)

chrome_options = Options()
chrome_options.add_argument("--headless")  # comment this line to see browser
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=service, options=chrome_options)

# 📅 Date range
start_date = datetime(2025, 6, 30)
end_date = datetime(2025, 8, 15)

# 📁 Excel writer
excel_writer = pd.ExcelWriter("Yahoo_Earnings_Daily_Jun30_Aug15.xlsx", engine='xlsxwriter')

# 📅 Loop through each day
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    print(f"📅 Scraping earnings for {date_str}...")

    all_day_data = []
    offset = 0
    while True:
        url = f"https://finance.yahoo.com/calendar/earnings?from=2025-06-30&to=2025-08-15&day={date_str}&offset={offset}&size=25"
        print(f"   ↪️ Loading offset {offset}...")
        driver.get(url)
        time.sleep(5)  # Avoid rate limiting

        try:
            table = driver.find_element("tag name", "table")
            rows = table.find_elements("tag name", "tr")[1:]  # skip header

            if not rows:
                break  # no more rows

            for row in rows:
                cols = row.find_elements("tag name", "td")
                if len(cols) >= 6:
                    all_day_data.append({
                        "Symbol": cols[0].text,
                        "Company": cols[1].text,
                        "Event Name": cols[2].text,
                        "Earnings Call Time": cols[3].text,
                        "EPS Estimate": cols[4].text,
                        "Reported EPS": cols[5].text,
                        "Surprise (%)": cols[6].text if len(cols) > 6 else "",
                        "Market Cap": cols[7].text if len(cols) > 7 else ""
                    })

            offset += 25  # next page
        except Exception as e:
            print(f"   ⚠️ No table or error at offset {offset}")
            break  # assume no more pages or no data

    # 📄 Save to sheet
    if all_day_data:
        df_day = pd.DataFrame(all_day_data)
    else:
        df_day = pd.DataFrame([{"Message": "No earnings data on this day"}])

    # Clean sheet name (max 31 chars for Excel sheet names)
    sheet_name = date_str.replace("-", "_")
    excel_writer.sheets[sheet_name] = excel_writer.book.add_worksheet(sheet_name)
    df_day.to_excel(excel_writer, sheet_name=sheet_name, index=False)

    current_date += timedelta(days=1)

driver.quit()
excel_writer.close()
print("\n✅ Done! Earnings saved to: Yahoo_Earnings_Daily_Jun30_Aug15.xlsx")
