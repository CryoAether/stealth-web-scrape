from bs4 import BeautifulSoup
import pandas as pd
import json


with open("motorcycles_CL.html", encoding='utf-8') as fp:
    soup = BeautifulSoup(fp,"lxml")
try:
    STORED_DATA = pd.read_csv("listings.csv")
except FileNotFoundError:
# This creates an empty table with specific Headers
    STORED_DATA = pd.DataFrame(columns=["Listing", "Price", "Location", "Link", "Image"])    
image_lookup = {}

script_tag = soup.find("script", {"id": "ld_searchpage_results"})

if script_tag:
    try:
        data = json.loads(script_tag.string)
        # Loop through the JSON data to fill our lookup dictionary
        for entry in data.get('itemListElement', []):
            item = entry.get('item', {})
            name = item.get('name')
            images = item.get('image', [])
            
            # If we have a name and at least one image, save it
            if name and images:
                # We only take the first image [0] for the CSV
                image_lookup[name] = images[0] 
    except json.JSONDecodeError:
        print("Could not parse JSON data")
              
rows = []
listings = soup.select('a[href*="/d/"]')
for a in listings:
    link = a["href"]
    title_tag = a.select_one("div.title")
    price_tag = a.select_one("div.price")
    loc_tag = a.select_one("div.location")

    title = title_tag.get_text(strip=True) if title_tag else None
    price = price_tag.get_text(strip=True) if price_tag else None
    loc = loc_tag.get_text(strip=True) if loc_tag else None

    img_url = image_lookup.get(title)
    rows.append({"Listing": title, 
                 "Price": price, 
                 "Location": loc,
                 "Link": link,
                 "Image": img_url
                })

new_data = pd.DataFrame(rows)

combined = pd.concat([STORED_DATA, new_data], ignore_index=True)
STORED_DATA = combined.drop_duplicates(subset="Listing", keep="last")
STORED_DATA.to_csv("listings.csv", index=False)
