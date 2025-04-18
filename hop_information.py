from multiprocessing import Pool, Manager
import requests
import os 
import json
from tqdm import tqdm
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}


STORAGE_DIR = 'ad_data'

def fix_json_file(filepath):
    """Check if JSON is valid, fix if needed, or reject if unfixable."""
    try:
        with open(filepath, 'r') as f:
            content = f.read().strip()
        
        # First try to parse as-is
        try:
            content = json.loads(content)
            return "accept", content  # Valid JSON, accept as-is
        except json.JSONDecodeError:
            pass  # Continue to fixing logic
        
        # Find the first occurrence of "timestamp"
        timestamp_pos = content.find('"timestamp"')
        if timestamp_pos == -1:
            return "reject", None  # No timestamp field, reject
        
        # Find the first } after timestamp
        closing_brace_pos = content.find('}', timestamp_pos)
        if closing_brace_pos == -1:
            return "reject", None  # No closing brace found
        
        # Extract content up to the closing brace
        fixed_content = content[:closing_brace_pos + 1]
        
        # Validate the fixed content
        try:
            fixed_content_json = json.loads(fixed_content)
            # Save the fixed content
            with open(filepath, 'w') as f:
                f.write(fixed_content)
            return "fix", fixed_content_json
        except json.JSONDecodeError:
            return "reject", None
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return "reject", None

def process_file(filename):
    filepath = os.path.join(STORAGE_DIR, filename)
    
    # First try to read the file normally
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        # Only fix files that have the "Extra data" error
        if "Extra data" in str(e):
            print(f"Fixing {filename} due to extra data error")
            action, data = fix_json_file(filepath)
            if action == "reject":
                print(f"Failed to fix {filename}")
                return filename, None
        else:
            print(f"Error reading {filename}: {e}")
            return filename, None
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return filename, None
    
    # Extract the URL (assuming it's stored under 'extracted_data' -> 'targetUrl')
    url = data.get('extracted_data', {}).get('targetUrl', '')
    if not url:
        return filename, None
    
    # Get the redirect trail and count
    try:
        response = requests.get(url, allow_redirects=True, timeout=30, verify=False)
        hop_count = len(response.history)  # Number of redirects
        # Create a list of all URLs in the redirect chain
        redirect_trail = [url]  # Start with original URL
        for resp in response.history:
            redirect_trail.append(resp.url)
        redirect_trail.append(response.url)  # Add final URL
        
        return filename, {
            'hop_count': hop_count,
            'redirect_trail': redirect_trail,
            'final_url': response.url
        }
    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")
        # Instead of returning None, return the URL with error information
        return filename, {
            'error': str(e),
            'url': url,
            'hop_count': 0,
            'redirect_trail': [url],
            'final_url': url
        }

def main():
    batch_size = 500
    
    # Get the list of files in the storage directory
    file_list = os.listdir(STORAGE_DIR)
    total_files = len(file_list)
    
    # Create a shared dictionary for storing results
    manager = Manager()
    shared_hop_info = manager.dict()
    
    # Process files in batches of 500
    for i in range(0, total_files, batch_size):
        batch = file_list[i:i+batch_size]
        
        # Use a multiprocessing Pool to process files in parallel
        with Pool(processes=10) as pool:
            results = list(tqdm(pool.imap(process_file, batch), total=len(batch)))
        
        # Update the shared dictionary with results
        for filename, hop_info in results:
            if hop_info is not None:  # Still check for None from JSON parsing errors
                shared_hop_info[filename] = hop_info
        
        # Save progress after each batch
        with open('hop_information.json', 'w') as f:
            json.dump(dict(shared_hop_info), f)
        
        print(f"Processed {min(i+batch_size, total_files)}/{total_files} files")

if __name__ == '__main__':
    main()

