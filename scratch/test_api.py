import requests
import json

def test_api():
    url = "http://localhost:8000/api/v1/projects"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for p in data.get("data", []):
                print(f"Title: {p['title']}")
                print(f"  Concession: {p['concession']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_api()
