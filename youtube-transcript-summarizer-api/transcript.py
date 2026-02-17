from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript_of_yt_video(video_id):
    """
    Fetches the transcript for a given YouTube video ID.
    Prioritizes:
    1. Manually created English transcript.
    2. Generated English transcript.
    3. Any other transcript translated to English.
    """
    try:
        # Create an instance of the API
        api = YouTubeTranscriptApi()
        
        # list() is the method in this version (1.2.4)
        transcript_list = api.list(video_id)

        transcript = None
        try:
            # Try to find a manually created English transcript
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except Exception:
            try:
                # Fallback to generated English transcript
                transcript = transcript_list.find_generated_transcript(['en'])
            except Exception:
                try:
                    # Fallback to any transcript and translate to English
                    transcript = transcript_list.find_transcript(['en'])
                except Exception:
                    # Final fallback: just get the first available and try to translate
                    for t in transcript_list:
                        transcript = t.translate('en')
                        break

        if not transcript:
            return None

        # Fetch the actual transcript data
        data = transcript.fetch()
        
        # Convert objects to dictionaries for compatibility with model.py
        formatted_transcript = []
        for item in data:
            formatted_transcript.append({
                'text': item.text,
                'start': item.start,
                'duration': item.duration
            })
            
        return formatted_transcript

    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None
