from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Create storage directory if it doesn't exist
STORAGE_DIR = "ad_data"
SS_DIR = "ss"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)
if not os.path.exists(SS_DIR):
    os.makedirs(SS_DIR)

def get_next_index(page_url):
    """Get the next available index for a given page URL"""
    base_filename = page_url.replace('/', '_').replace(':', '_')
    index = 0
    while True:
        filename = f"{STORAGE_DIR}/{base_filename}_{index}.json"
        if not os.path.exists(filename):
            return index
        index += 1

@app.route('/collect-ads', methods=['POST'])
def collect_ads():
    data = request.get_json()
    print("Received data:", data)
    
    # Extract required fields
    page_url = data.get('pageUrl', '')
    src = data.get('contentData', {}).get('src', '')
    target_url = data.get('targetUrl', '')
    
    if not page_url:
        return jsonify({"error": "Missing pageUrl"}), 400
    
    # Get next available index for this page
    index = get_next_index(page_url)
    
    # Create storage object
    storage_data = {
        "raw_data": data,
        "extracted_data": {
            "src": src,
            "targetUrl": target_url,
            "pageUrl": page_url
        },
        "index": index,
        "timestamp": datetime.now().isoformat()
    }
    
    # Save to file
    base_filename = page_url.replace('/', '_').replace(':', '_')
    filename = f"{STORAGE_DIR}/{base_filename}_{index}.json"
    
    with open(filename, 'w') as f:
        json.dump(storage_data, f, indent=2)
    
    return jsonify({
        "status": "success",
        "message": f"Data stored with index {index}",
        "filename": filename
    })

if __name__ == '__main__':
    app.run(port=5000) 
