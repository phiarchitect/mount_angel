import json
import re

def parse_markdown(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Split the markdown on '### ' to separate drawing entries
    # The first split will be intro text/empty, so we skip it
    entries = content.split('### ')[1:]
    
    drawings_data = []
    
    for entry in entries:
        # Each entry looks like:
        # 01-a1_gm-1142x700.jpg
        # - **Type**: Site Plan
        # - **Title Block**: ...
        # - **Contents**: ...
        
        lines = entry.strip().split('\n')
        
        # Line 1 is the filename
        filename = lines[0].strip()
        
        # Regex to extract the leading number ID (e.g., "01" from "01-a1_gm...")
        id_match = re.search(r'^(\d+)-', filename)
        drawing_id = int(id_match.group(1)) if id_match else 0
        
        drawing_obj = {
            "id": drawing_id,
            "filename": filename,
            "type": "Unknown",
            "title_block": "Unknown",
            "contents": "Unknown"
        }
        
        for line in lines[1:]:
            if line.startswith('- **Type**:'):
                drawing_obj["type"] = line.split('- **Type**:')[1].strip()
            elif line.startswith('- **Title Block**:'):
                drawing_obj["title_block"] = line.split('- **Title Block**:')[1].strip()
            elif line.startswith('- **Contents**:'):
                drawing_obj["contents"] = line.split('- **Contents**:')[1].strip()
        
        drawings_data.append(drawing_obj)
        
    return drawings_data

if __name__ == "__main__":
    md_path = "/home/phi/PROJECTS/phiarchitect/mountangel/references/drawings_index.md"
    json_path = "/home/phi/PROJECTS/phiarchitect/mountangel/docs/data.json"
    
    data = parse_markdown(md_path)
    
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)
        print(f"Successfully processed {len(data)} drawings into {json_path}")
