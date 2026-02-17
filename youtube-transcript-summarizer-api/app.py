import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import urlparse, parse_qs
from video_summarizer import summarize_video_universal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Production CORS setup
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
# Use a more flexible regex for resources
CORS(app, resources={r"/api*": {"origins": allowed_origins}})


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


@app.route('/api/', methods=['GET'], strict_slashes=False)
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
        logger.info(f"Processing video: {video_url}")
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
        logger.error(f"Error processing video {video_url}: {e}")
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
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    if debug:
        app.run(threaded=True, debug=True, port=port)
    else:
        # Production server
        from waitress import serve
        logger.info(f"Starting production server on port {port}")
        serve(app, host="0.0.0.0", port=port)

