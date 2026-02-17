import os

# Fix for OpenMP duplicate library error - MUST BE SET BEFORE OTHER IMPORTS
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import re
import yt_dlp
import whisper
import imageio_ffmpeg
from transcript import get_transcript_of_yt_video
from model import text_summarizer
from translate import g_translate

# Ensure ffmpeg from imageio-ffmpeg is in PATH
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg_dir = os.path.dirname(ffmpeg_exe)
# Prefer a file named ffmpeg.exe in the same directory for compatibility
ffmpeg_alias = os.path.join(ffmpeg_dir, "ffmpeg.exe")
current_ffmpeg = ffmpeg_alias if os.path.exists(ffmpeg_alias) else ffmpeg_exe

if ffmpeg_dir not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + ffmpeg_dir

def download_audio(video_url, output_path="downloads"):
    """
    Downloads the audio of a YouTube video using yt-dlp.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
        'ffmpeg_location': current_ffmpeg,
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        video_id = info['id']
        audio_file = os.path.join(output_path, f"{video_id}.mp3")
        return audio_file, video_id

def transcribe_audio(audio_path):
    """
    Transcribes audio file using OpenAI Whisper.
    """
    print(f"Transcribing {audio_path}...")
    # Load model (base is a good compromise between speed and accuracy)
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']

def summarize_video_universal(video_url, video_id):
    """
    Summarizes a YouTube video by picking the best available method:
    1. Direct Transcript (fastest)
    2. Audio Download + STT Transcription (universal fallback)
    """
    # 1. Try fetching transcript first
    transcript_data = get_transcript_of_yt_video(video_id)
    
    if transcript_data:
        print(f"Transcript found for {video_id}. Proceeding with transcript.")
        original_text = ' '.join([t['text'] for t in transcript_data])
        original_text_length = len(original_text)
    else:
        # 2. Fallback to STT
        print(f"No transcript for {video_id}. Falling back to Audio Download + STT...")
        try:
            audio_path, _ = download_audio(video_url)
            original_text = transcribe_audio(audio_path)
            original_text_length = len(original_text)
            
            # Clean up audio file after transcription
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"Deleted temporary audio file: {audio_path}")
        except Exception as e:
            print(f"Universal fallback failed for {video_id}: {e}")
            return None

    if not original_text:
        return None

    # 3. Summarize the text
    # We reuse the text_summarizer from model.py for consistency
    english_summary_list = text_summarizer(original_text)
    english_summary_text = ' '.join(english_summary_list)
    final_summary_length = len(english_summary_text)

    # 4. Translations
    translation_input = '\n'.join(english_summary_list)
    
    try:
        hindi_translation = g_translate(translation_input, 'hi')
        hindi_summary_list = [s.strip() for s in hindi_translation.split('\n') if s.strip()]
    except Exception as e:
        print(f"Hindi translation failed: {e}")
        hindi_summary_list = ["Translation unavailable."]

    try:
        gujarati_translation = g_translate(translation_input, 'gu')
        gujarati_summary_list = [s.strip() for s in gujarati_translation.split('\n') if s.strip()]
    except Exception as e:
        print(f"Gujarati translation failed: {e}")
        gujarati_summary_list = ["Translation unavailable."]

    return {
        "original_txt_length": original_text_length,
        "final_summ_length": final_summary_length,
        "eng_summary": english_summary_list,
        "hind_summary": hindi_summary_list,
        "guj_summary": gujarati_summary_list
    }
