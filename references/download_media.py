import json
import os
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

base_dir = "/home/phi/PROJECTS/phiarchitect/mountangel/references"
json_path = os.path.join(base_dir, "image_urls.json")

with open(json_path, "r") as f:
    items = json.load(f)

for d in ["photos", "drawings", "documents", "other"]:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

def determine_folder(item):
    url = item["url"].lower()
    title = item["title"].lower()
    if url.endswith(".pdf"):
        return "documents"
    if "slide" in title or "-a" in title or "-s" in title or "blueprint" in title or "aalto architecture" in title or "_gm" in url:
        return "drawings"
    if "img_" in url or "library" in title or "photo" in title or "crop" in url:
        return "photos"
    return "other"

md_lines = ["# Alvar Aalto Mount Angel Library References\n"]

def download_item(idx, item):
    url = item["url"]
    folder = determine_folder(item)
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename:
        filename = f"image_{idx}.jpg"
        
    out_path = os.path.join(base_dir, folder, filename)
    
    if not os.path.exists(out_path):
        print(f"Downloading {url} to {folder}/{filename}")
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    f.write(r.content)
            else:
                print(f"Failed to download {url}: Status {r.status_code}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            
    header_title = item['title'] or filename
    
    return {
        "idx": idx,
        "lines": [
            f"## {header_title}",
            f"- **Type:** {item['type']}",
            f"- **Original URL:** {url}",
            f"- **Local Path:** {folder}/{filename}",
            f"- **Alt Text:** {item['text']}" if item['text'] else "",
            f"\n![{header_title}](./{folder}/{filename})\n"
        ]
    }

results = []
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download_item, idx, item) for idx, item in enumerate(items)]
    for future in as_completed(futures):
        results.append(future.result())

results.sort(key=lambda x: x["idx"])

for res in results:
    md_lines.extend([line for line in res["lines"] if line])

with open(os.path.join(base_dir, "references.md"), "w") as f:
    f.write("\n".join(md_lines))
    
print("Finished downloading and organizing files.")
