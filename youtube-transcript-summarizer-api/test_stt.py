import os
import time
from video_summarizer import download_audio, transcribe_audio

def test_stt_fallback(video_url):
    print(f"\n--- Testing STT Fallback: {video_url} ---")
    try:
        start_time = time.time()
        print("Downloading audio...")
        audio_path, video_id = download_audio(video_url)
        print(f"Audio downloaded to: {audio_path}")
        
        print("Transcribing with Whisper...")
        text = transcribe_audio(audio_path)
        print(f"Transcription: {text[:200]}...")
        
        # Clean up
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print("Audio file cleaned up.")
            
        end_time = time.time()
        print(f"STT Fallback took {end_time - start_time:.2f} seconds.")
    except Exception as e:
        print(f"STT Fallback failed: {e}")

if __name__ == "__main__":
    # Me at the zoo (short, simple speech)
    test_stt_fallback("https://www.youtube.com/watch?v=jNQXAC9IVRw")
