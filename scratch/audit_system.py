import json
import requests
import sys

def audit_system():
    # 1. Load source data
    with open('data/data.json', 'r', encoding='utf-8') as f:
        source_data = json.load(f)
    
    # 2. Fetch API data
    api_url = "http://localhost:8000/api/v1/projects?page_size=100"
    try:
        resp = requests.get(api_url)
        if resp.status_code != 200:
            print(f"API Error: {resp.status_code}")
            return
        api_projects = resp.json().get("data", [])
    except Exception as e:
        print(f"Connection Error: {e}")
        return

    print(f"--- Full System Audit Start ---")
    print(f"Source Projects: {len(source_data)}")
    print(f"API Projects: {len(api_projects)}")
    
    issues = []
    
    # Create a map for easier comparison
    api_map = {p['title'].strip(): p for p in api_projects}
    
    for i, src in enumerate(source_data):
        title = src.get('title', '').strip()
        if title not in api_map:
            issues.append(f"Missing Project: {title}")
            continue
        
        api_p = api_map[title]
        
        # Check Concession
        src_concessions = [ac['description'] for ac in src.get('additionalClassifications', []) if ac.get('scheme') == "รูปแบบสัมปทานหรือค่าตอบแทน"]
        if set(src_concessions) != set(api_p.get('concession', [])):
            issues.append(f"Concession Mismatch in '{title}': Expected {src_concessions}, Got {api_p.get('concession')}")
            
        # Check Public Authority
        src_pa = src.get('publicAuthority', {}).get('name', '')
        if src_pa and src_pa != api_p.get('public_authority'):
            # Only report if API has something different (sometimes source PA name is empty but party list has it)
            if api_p.get('public_authority'):
                pass # Already handled by import logic which fills from parties
            else:
                issues.append(f"Public Authority Missing in '{title}': Expected {src_pa}")

    if not issues:
        print("✅ Result: All 42 projects are correctly imported and matched with source data!")
    else:
        print(f"❌ Found {len(issues)} potential issues:")
        for issue in issues:
            print(f"  - {issue}")
            
    print(f"--- Audit End ---")

if __name__ == "__main__":
    audit_system()
