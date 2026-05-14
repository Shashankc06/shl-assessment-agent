import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(CATALOG_URL, headers=headers)

if response.status_code != 200:
    print("Failed to fetch catalog page")
    exit()

soup = BeautifulSoup(response.text, "lxml")

assessment_links = []

# Find all product links
for link in soup.find_all("a", href=True):

    href = link["href"]

    if "/products/" in href and href not in assessment_links:

        if href.startswith("http"):
            full_url = href
        else:
            full_url = BASE_URL + href

        assessment_links.append(full_url)

assessment_links = list(set(assessment_links))

print(f"Found {len(assessment_links)} assessment links")

all_assessments = []

for idx, url in enumerate(assessment_links):

    try:
        print(f"Scraping {idx+1}/{len(assessment_links)}")

        page = requests.get(url, headers=headers, timeout=20)

        if page.status_code != 200:
            continue

        soup = BeautifulSoup(page.text, "lxml")

        title = soup.find("h1")

        name = title.text.strip() if title else "Unknown"

        paragraphs = soup.find_all("p")

        description = " ".join(
            [p.text.strip() for p in paragraphs[:5]]
        )

        assessment_data = {
            "name": name,
            "url": url,
            "description": description
        }

        all_assessments.append(assessment_data)

        time.sleep(1)

    except Exception as e:
        print("Error:", e)

with open("data/shl_catalog.json", "w", encoding="utf-8") as f:
    json.dump(all_assessments, f, indent=2, ensure_ascii=False)

df = pd.DataFrame(all_assessments)

df.to_csv("data/shl_catalog.csv", index=False)

print("Scraping completed!")
print(f"Saved {len(all_assessments)} assessments")