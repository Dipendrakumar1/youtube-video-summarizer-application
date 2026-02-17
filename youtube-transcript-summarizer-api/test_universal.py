import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001/api/"

def test_summary(video_url, test_name):
    print(f"\n--- Testing: {test_name} ---")
    print(f"URL: {video_url}")
    start_time = time.time()
    try:
        response = requests.get(BASE_URL, params={"video_url": video_url}, timeout=300)
        end_time = time.time()
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            # print(f"Summary: {data['data']['eng_summary'][:2]}...")
        else:
            print(f"Failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 1. Video with transcript (should be fast)
    test_summary("https://www.youtube.com/watch?v=BNHR6IQJGZs", "Video with Transcript")
    
    # 2. Video likely without transcript (e.g., a music video or very short clip)
    # Using a short video to avoid long processing time during verification
    # test_summary("https://www.youtube.com/watch?v=vpL96b86_7Y", "Video without Transcript Fallback")
