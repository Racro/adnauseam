import json

def fix_json(content):
    """Check if JSON is valid, fix if needed, or reject if unfixable."""
    # First try to parse as-is
    try:
        json.loads(content)
        return "accept", content  # Valid JSON, accept as-is
    except json.JSONDecodeError:
        pass  # Continue to fixing logic
    
    # Find the last occurrence of "timestamp"
    timestamp_pos = content.rfind('"timestamp"')
    if timestamp_pos == -1:
        return "reject", None  # No timestamp field, reject
    
    # Find the end of the timestamp value
    end_quote = content.find('"', timestamp_pos + len('"timestamp": "') + 1)
    if end_quote == -1:
        return "reject", None  # Invalid timestamp format, reject
    
    # Now look for the second } after the timestamp
    brace_count = 0
    for i in range(end_quote, len(content)):
        if content[i] == '}':
            brace_count += 1
            if brace_count == 2:
                # Found our stopping point
                fixed_content = content[:i+1]
                try:
                    json.loads(fixed_content)
                    return "fix", fixed_content  # Successfully fixed
                except json.JSONDecodeError:
                    return "reject", None  # Couldn't fix, reject
                break
    
    return "reject", None  # Didn't find second brace, reject

# Test cases
test_cases = [
    # Valid case (should accept)
    '''{
  "raw_data": {
    "id": null
  },
  "extracted_data": {
    "src": ""
  },
  "timestamp": "2025-04-07T00:56:35.318947"
}''',
    
    # Case with extra data (should fix)
    '''{
  "raw_data": {
    "id": null
  },
  "extracted_data": {
    "src": ""
  },
  "timestamp": "2025-04-07T00:56:35.318947"
} 44782"}''',
    
    # Case with multiple closing braces (should fix)
    '''{
  "raw_data": {
    "id": null
  },
  "extracted_data": {
    "src": ""
  },
  "timestamp": "2025-04-07T00:56:35.318947"
}}}}''',
    
    # Invalid case (should reject)
    '''{
  "raw_data": {
    "id": null
  },
  "extracted_data": {
    "src": ""
  },
  "timestamp": "2025-04-07T00:56:35.318947"
  missing closing brace''',
]

# Run tests
for i, test_case in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    print("Original:")
    print(test_case)
    
    action, result = fix_json(test_case)
    print(f"\nAction: {action.upper()}")
    if action == "accept":
        print("✅ Accepted as valid JSON")
    elif action == "fix":
        print("🛠️ Fixed JSON:")
        print(result)
    else:  # reject
        print("❌ Rejected - could not fix")
    print("-"*50) 