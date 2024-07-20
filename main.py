import os
import requests
import json
from urllib.parse import urljoin
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL for the API
BASE_URL = "https://clist.by"
API_ENDPOINT = "/api/v4/contest/"

# Get the API key from environment variable
API_KEY = os.environ.get("CLIST_API_KEY")

if not API_KEY:
    logging.error("CLIST_API_KEY environment variable is not set")
    raise ValueError("CLIST_API_KEY environment variable is not set")

headers = {
    "Authorization": f"ApiKey {API_KEY}"
}

params = {
    "resource": "leetcode.com",
    "limit": 200,
    "with_problems": True,
    "upcoming": False,
    "order_by": "start"
}

all_problems = []

def fetch_data(url):
    logging.info(f"Fetching data from: {url}")
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    logging.info(f"Successfully fetched data from: {url}")
    return response.json()

def process_problems(data):
    contest_count = len(data["objects"])
    logging.info(f"Processing {contest_count} contests")
    for contest in data["objects"]:
        contest_name = contest['event']
        problem_count = len(contest["problems"])
        logging.info(f"Processing {problem_count} problems from contest: {contest_name}")
        for problem in contest["problems"]:
            all_problems.append({
                "title": problem["name"],
                "url": problem["url"],
                "rating": problem.get("rating", 0),  # Use 0 if rating is not available
                "contest": contest_name
            })
    logging.info(f"Total problems processed so far: {len(all_problems)}")

# Fetch initial data
url = urljoin(BASE_URL, API_ENDPOINT)
data = fetch_data(url)
process_problems(data)

# Fetch subsequent pages
page_count = 1
requests_made = 1
start_time = time.time()

while "next" in data["meta"] and data["meta"]["next"]:
    page_count += 1
    logging.info(f"Fetching page {page_count}")
    
    # Check rate limit
    if requests_made >= 10:
        elapsed_time = time.time() - start_time
        if elapsed_time < 60:
            sleep_time = 60 - elapsed_time
            logging.info(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        requests_made = 0
        start_time = time.time()
    
    next_url = urljoin(BASE_URL, data["meta"]["next"])
    data = fetch_data(next_url)
    process_problems(data)
    requests_made += 1
    
    # Check if we've reached the end
    if not data["objects"]:
        logging.info("No more objects found. This is the last page.")
        break

logging.info(f"Finished fetching data. Total pages processed: {page_count}")

# Sort problems by rating in descending order
logging.info("Sorting problems by rating...")
sorted_problems = sorted(all_problems, key=lambda x: x["rating"], reverse=True)

# Check if docs folder exists
docs_folder = "docs"
if not os.path.exists(docs_folder):
    logging.warning(f"'{docs_folder}' folder does not exist. Creating files in the current directory.")
    docs_folder = "."

# Generate Markdown file
md_file = os.path.join(docs_folder, "README.md")
logging.info(f"Generating Markdown file: {md_file}")
with open(md_file, "w") as f:
    f.write("# LeetCode Problems Sorted by Rating\n\n")
    for problem in sorted_problems:
        f.write(f"- [{problem['title']}]({problem['url']}) (Rating: {problem['rating']}, Contest: {problem['contest']})\n")

logging.info(f"Markdown file '{md_file}' has been generated.")

# Generate JSON file
json_file = os.path.join(docs_folder, "leetcode_problems.json")
logging.info(f"Generating JSON file: {json_file}")
json_data = {
    "problems": [
        {"title": p["title"], "url": p["url"], "rating": p["rating"]}
        for p in sorted_problems
    ]
}
with open(json_file, "w") as f:
    json.dump(json_data, f, indent=2)

logging.info(f"JSON file '{json_file}' has been generated.")
logging.info(f"Total problems written: {len(sorted_problems)}")
