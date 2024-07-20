from playwright.sync_api import sync_playwright
import json
import random
import time
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def get_leetcode_contest_data(pagination):
    logging.info(f"Attempting to fetch data for pagination {pagination}")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True,
        )
        page = context.new_page()
        
        url = f"https://leetcode.com/contest/api/ranking/biweekly-contest-127/?pagination={pagination}&region=global&timestamp={int(time.time())}"
        
        logging.info("Navigating to LeetCode homepage")
        page.goto("https://leetcode.com")
        delay = random.uniform(2, 5)
        logging.info(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)
        
        logging.info(f"Navigating to contest API URL: {url}")
        page.goto(url, wait_until='networkidle')
        delay = random.uniform(1, 3)
        logging.info(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)
        
        logging.info("Extracting page content")
        content = page.content()
        
        start_index = content.find('{')
        end_index = content.rfind('}') + 1
        json_data = content[start_index:end_index]
        
        try:
            data = json.loads(json_data)
            logging.info("Successfully parsed JSON data")
        except json.JSONDecodeError as e:
            logging.error(f"JSON Decode Error for pagination {pagination}: {e}")
            logging.debug(f"Content snippet: {content[:500]}...")
            data = None
        
        browser.close()
        return data

def fetch_all_contest_data():
    logging.info("Starting to fetch all contest data")
    os.makedirs("contest_data", exist_ok=True)
    logging.info("Created 'contest_data' directory")
    
    pagination = 1
    while True:
        logging.info(f"Fetching data for pagination {pagination}")
        data = get_leetcode_contest_data(pagination)
        
        if data is None:
            logging.warning(f"Rate limited or error occurred. Waiting for 30 seconds before retrying pagination {pagination}")
            time.sleep(30)
            continue
        
        if 'time' not in data:
            logging.info(f"Reached end of data at pagination {pagination - 1}")
            break
        
        file_path = f"contest_data/pagination-{pagination}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Saved data to {file_path}")
        
        pagination += 1
        delay = 5
        logging.info(f"Waiting for {delay} seconds before next request")
        time.sleep(delay)

    logging.info("Finished fetching all contest data")

# Run the function to fetch all contest data
if __name__ == "__main__":
    logging.info("Script started")
    fetch_all_contest_data()
    logging.info("Script completed")
