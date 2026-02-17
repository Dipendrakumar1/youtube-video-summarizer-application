import re
import spacy
from heapq import nlargest
from string import punctuation
from transcript import get_transcript_of_yt_video
from translate import g_translate

# Load resources once
import nltk
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords

# Global NLP model loading to avoid reloading on every request
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load('en_core_web_sm')


def text_summarizer(text):
    """
    Summarizes the given text using frequency-based sentence scoring.
    """
    doc = nlp(text)
    stop_words = set(stopwords.words('english'))

    word_frequencies = {}
    for word in doc:
        text_lower = word.text.lower()
        if text_lower not in stop_words and text_lower not in punctuation:
            if word.text not in word_frequencies:
                word_frequencies[word.text] = 1
            else:
                word_frequencies[word.text] += 1

    if not word_frequencies:
        return text # Return original if no significant words found

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_frequency

    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}
    
    for sent in sentence_tokens:
        for word in sent:
            if word.text in word_frequencies:
                if sent not in sentence_scores:
                    sentence_scores[sent] = word_frequencies[word.text]
                else:
                    sentence_scores[sent] += word_frequencies[word.text]

    select_length = int(len(sentence_tokens) * 0.3)
    if select_length < 1:
        select_length = 1
        
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)

    # Reconstruct summary as a list of sentences
    final_summary = []
    for sent in summary:
        text = sent.text.replace("\n", " ").strip().capitalize()
        if text:
            # Ensure it ends with punctuation if missing
            if text and text[-1] not in punctuation:
                text += "."
            final_summary.append(text)
            
    return final_summary


def summarize_video(video_id):
    """
    Orchestrates the fetching, summarizing, and translating of a video's transcript.
    """
    transcript = get_transcript_of_yt_video(video_id)

    if not transcript:
        print(f"Transcript NOT fetched for {video_id}.")
        return None
    print(f"Transcript fetched successfully for {video_id}.")

    # Combine transcript text
    original_text = ' '.join([t['text'] for t in transcript])
    original_text_length = len(original_text)

    # Summarize in chunks to handle large texts better
    # Note: The original logic treated every 100 entries as a chunk. 
    # We will keep a similar logic but cleaned up.
    
    chunk_size = 10000 # Characters, roughly
    if len(original_text) > chunk_size:
        # Simple chunking by length for now, or use original logic relative to transcript segments
         # Original logic: every 100 segments.
        transcript_size = len(transcript)
        summarized_chunks = []
        current_chunk = ""
        
        for i, item in enumerate(transcript):
            current_chunk += item['text'] + " "
            if (i + 1) % 100 == 0 or i == transcript_size - 1:
                summarized_chunks.extend(text_summarizer(current_chunk))
                current_chunk = ""
        
        english_summary_list = summarized_chunks
    else:
        english_summary_list = text_summarizer(original_text)

    # Full text for length calculation and translation
    english_summary_text = ' '.join(english_summary_list)
    print(f"English summary generated. Length: {len(english_summary_text)}")
    final_summary_length = len(english_summary_text)

    # Translations - Join with newline to maintain sentence separation
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
