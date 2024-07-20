from playwright.sync_api import sync_playwright
import json

def get_leetcode_contest_data():
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
        
        url = "https://leetcode.com/contest/api/ranking/biweekly-contest-127/?pagination=1&region=global"
        
        page.goto(url, wait_until='networkidle')
        
        content = page.content()
        
        start_index = content.find('{')
        end_index = content.rfind('}') + 1
        json_data = content[start_index:end_index]
        
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            data = None
        
        browser.close()
        return data

# Run the function and print the result
result = get_leetcode_contest_data()
if result:
    print(json.dumps(result, indent=2))
else:
    print("Failed to retrieve data")
