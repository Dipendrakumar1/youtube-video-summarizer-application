import requests
import json

url = "http://127.0.0.1:5001/api/"
video_url = "https://www.youtube.com/watch?v=BNHR6IQJGZs"

print(f"Testing API with video: {video_url}")
try:
    response = requests.get(url, params={"video_url": video_url}, timeout=120)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Success!")
        print(f"Summary length: {data['data']['final_summ_length']}")
        print(f"English Summary: {data['data']['eng_summary'][:150]}...")
    else:
        print(f"Failed: {response.text}")
except Exception as e:
    print(f"Error calling API: {e}")
