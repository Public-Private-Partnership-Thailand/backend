import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_summary(params, label):
    try:
        url = f"{BASE_URL}/summary"
        print(f"Testing {label}: {url} params={params}")
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            total = data.get('summary', {}).get('totalProjects')
            print(f"  -> Status: 200, Total Projects: {total}")
        else:
            print(f"  -> Status: {resp.status_code}, Error: {resp.text}")
    except Exception as e:
        print(f"  -> Error: {e}")

if __name__ == "__main__":
    # Test 1: No filter
    test_summary({}, "No Filter")

    # Test 2: Contract Type ID 1
    test_summary({'contractType': '1'}, "Contract Type = 1")

    # Test 3: Contract Type Name "Road transport (CS)"
    test_summary({'contractType': 'Road transport (CS)'}, "Contract Type = Name")

    # Test 4: Sector ID 1
    test_summary({'sector': '1'}, "Sector = 1")
    
    # Test 5: Business Group (Sector) ID 1
    test_summary({'businessGroup': '1'}, "BusinessGroup = 1")
