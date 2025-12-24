import pandas as pd
import requests
import os
import time

# 1. Setup folders
if not os.path.exists("static/images"):
    os.makedirs("static/images")

df = pd.read_csv("listings.csv")
local_paths = []

print(f"Downloading images for {len(df)} listings...")

for index, row in df.iterrows():
    url = row['Image']
    # Create a safe filename (e.g., image_0.jpg, image_1.jpg)
    filename = f"image_{index}.jpg"
    filepath = os.path.join("static/images", filename)
    
    # Only download if we haven't already
    if not os.path.exists(filepath):
        try:
            # Fake a browser visit to avoid getting blocked
            headers = {'User-Agent': 'Mozilla/5.0'}
            img_data = requests.get(url, headers=headers, timeout=5).content
            with open(filepath, 'wb') as handler:
                handler.write(img_data)
            print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Failed {filename}: {e}")
            filename = "placeholder.jpg" # You might want a default 'no image' file
    
    # Store the RELATIVE path for Flask
    local_paths.append(f"images/{filename}")
    
    # Be nice to the server
    time.sleep(0.5)

df['LocalImage'] = local_paths
df.to_csv("listings_cached.csv", index=False)
print("Done! Created listings_cached.csv")