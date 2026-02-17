"""
Project Name: YouTube Transcript Summarizer
YouTube Transcript Summarizer API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import urlparse, parse_qs
from video_summarizer import summarize_video_universal

app = Flask(__name__)
CORS(app)


def get_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    if not url:
        return None
        
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0] if 'v' in p else None
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
            
    return None


@app.route('/api/', methods=['GET'])
def respond():
    # Retrieve the video_url from url parameter
    video_url = request.args.get("video_url", None)

    video_id = get_video_id(video_url)

    if not video_id:
        return jsonify({
            "status": "Failed",
            "message": "Invalid or missing YouTube video URL."
        }), 400

    try:
        summary_data = summarize_video_universal(video_url, video_id)
        
        if not summary_data:
             return jsonify({
                "status": "Failed",
                "message": "Could not retrieve the transcript for this video."
            }), 404
            
        return jsonify({
            "data": {
                "message": "Success",
                "id": video_id,
                **summary_data
            }
        })

    except Exception as e:
        print(f"Error processing video: {e}")
        return jsonify({
            "status": "Failed",
            "message": "An internal error occurred."
        }), 500


@app.route('/')
def index():
    return jsonify({
        "message": "Success",
        "data": "Welcome to YTS API."
    })


if __name__ == '__main__':
    app.run(threaded=True, debug=True, port=5001)

